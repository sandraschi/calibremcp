#!/usr/bin/env python3
"""
Test Battery for manage_authors Portmanteau Tool

Tests all operations: list, get, get_books, stats, by_letter
Run with: python tests/portmanteau/test_manage_authors.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_authors portmanteau."""

    print("MANAGE_AUTHORS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: list, get, get_books, stats, by_letter operations")
    print("=" * 60)

    test_results = []
    test_author_id = None

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_authors tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.authors.manage_authors import manage_authors

        print("[OK] Tool imported successfully")

        # Initialize with a library
        print("\n[DB] Initializing database...")
        config = CalibreConfig()
        libraries = config.discover_libraries()

        if not libraries:
            print("[ERROR] No libraries found")
            return False

        first_lib_name = next(iter(libraries.keys()))
        first_lib_path = libraries[first_lib_name].path
        init_database(str(first_lib_path / "metadata.db"), echo=False)
        print(f"[OK] Database initialized with library: {first_lib_name}")

        # Test 1: List Authors
        print("\n[TEST1] LIST AUTHORS")
        try:
            result = await manage_authors(operation="list", limit=20)
            if result.get("success") or "items" in result:
                authors_found = len(result.get("items", []))
                total = result.get("total", authors_found)
                test_results.append(("List Authors", True, f"Found {authors_found} authors (total: {total})"))
                print(f"[OK] Found {authors_found} authors")
                if result.get("items"):
                    test_author_id = result["items"][0]["id"]
                    print(f"  - Sample: {result['items'][0]['name']} ({result['items'][0]['book_count']} books)")
            else:
                test_results.append(("List Authors", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("List Authors", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Search Authors
        print("\n[TEST2] SEARCH AUTHORS")
        try:
            result = await manage_authors(operation="list", query="test", limit=10)
            if result.get("success") or "items" in result:
                authors_found = len(result.get("items", []))
                test_results.append(("Search Authors", True, f"Found {authors_found} authors"))
                print(f"[OK] Found {authors_found} authors matching 'test'")
            else:
                test_results.append(("Search Authors", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search Authors", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Get Author Details
        print("\n[TEST3] GET AUTHOR DETAILS")
        try:
            if test_author_id:
                result = await manage_authors(operation="get", author_id=test_author_id)
                if result.get("success") or "id" in result:
                    test_results.append(("Get Author", True, f"Retrieved author ID {test_author_id}"))
                    print(f"[OK] Retrieved author: {result.get('name', 'Unknown')}")
                    print(f"  - Books: {result.get('book_count', 0)}")
                else:
                    test_results.append(("Get Author", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get Author", True, "No test author (skip)"))
                print("[SKIP] No test author available")
        except Exception as e:
            test_results.append(("Get Author", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Get Books by Author
        print("\n[TEST4] GET BOOKS BY AUTHOR")
        try:
            if test_author_id:
                result = await manage_authors(operation="get_books", author_id=test_author_id, limit=10)
                if result.get("success") or "books" in result:
                    books_found = len(result.get("books", []))
                    total = result.get("total", books_found)
                    test_results.append(("Get Books by Author", True, f"Found {books_found} books (total: {total})"))
                    print(f"[OK] Found {books_found} books by author")
                else:
                    test_results.append(("Get Books by Author", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get Books by Author", True, "No test author (skip)"))
                print("[SKIP] No test author available")
        except Exception as e:
            test_results.append(("Get Books by Author", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Get Author Statistics
        print("\n[TEST5] GET AUTHOR STATISTICS")
        try:
            result = await manage_authors(operation="stats")
            if result.get("success") or "total_authors" in result:
                total_authors = result.get("total_authors", 0)
                test_results.append(("Author Stats", True, f"Found {total_authors} total authors"))
                print("[OK] Author statistics retrieved")
                print(f"  - Total authors: {total_authors}")
                if result.get("top_authors"):
                    print(
                        f"  - Top author: {result['top_authors'][0]['name']} ({result['top_authors'][0]['book_count']} books)"
                    )
            else:
                test_results.append(("Author Stats", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Author Stats", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Get Authors by Letter
        print("\n[TEST6] GET AUTHORS BY LETTER")
        try:
            result = await manage_authors(operation="by_letter", letter="A")
            if result.get("success") or "authors" in result:
                authors_found = len(result.get("authors", []))
                test_results.append(("Authors by Letter", True, f"Found {authors_found} authors starting with 'A'"))
                print(f"[OK] Found {authors_found} authors starting with 'A'")
            else:
                test_results.append(("Authors by Letter", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Authors by Letter", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 7: Pagination Test
        print("\n[TEST7] PAGINATION TEST")
        try:
            page1 = await manage_authors(operation="list", limit=10, offset=0)
            page2 = await manage_authors(operation="list", limit=10, offset=10)

            if (page1.get("success") or "items" in page1) and (page2.get("success") or "items" in page2):
                page1_count = len(page1.get("items", []))
                page2_count = len(page2.get("items", []))
                test_results.append(("Pagination", True, f"Page 1: {page1_count}, Page 2: {page2_count}"))
                print(f"[OK] Pagination working: Page 1 ({page1_count}), Page 2 ({page2_count})")
            else:
                test_results.append(("Pagination", False, "Pagination failed"))
                print("[FAIL] Pagination failed")
        except Exception as e:
            test_results.append(("Pagination", False, str(e)))
            print(f"[FAIL] {e}")

    except Exception as e:
        print(f"\n[CRITICAL] ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Print results summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, success, details in test_results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}: {details}")
        if success:
            passed += 1

    print(f"\nOVERALL: {passed}/{total} tests passed")

    if passed == total:
        print("ALL TESTS PASSED!")
        return True
    else:
        print("SOME TESTS FAILED.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_test_battery())
    sys.exit(0 if success else 1)
