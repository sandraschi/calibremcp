#!/usr/bin/env python3
"""
Test Battery for query_books Portmanteau Tool

Tests all operations: search, list, recent, by_author, by_series
Run with: python tests/portmanteau/test_query_books.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for query_books portmanteau."""

    print("QUERY_BOOKS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: search, list, recent, by_author, by_series operations")
    print("=" * 60)

    test_results = []

    try:
        # Import tool
        print("\n[IMPORT] Importing query_books tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.book_management.query_books import query_books

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

        # Test 1: Search by Text
        print("\n[TEST1] SEARCH BY TEXT")
        try:
            result = await query_books(operation="search", text="book", limit=10)
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                total = result.get("total", books_found)
                test_results.append(("Search by Text", True, f"Found {books_found} books (total: {total})"))
                print(f"[OK] Found {books_found} books matching 'book'")
            else:
                test_results.append(("Search by Text", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search by Text", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Search by Author
        print("\n[TEST2] SEARCH BY AUTHOR")
        try:
            result = await query_books(operation="search", author="test", limit=5)
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                test_results.append(("Search by Author", True, f"Found {books_found} books"))
                print(f"[OK] Found {books_found} books by author 'test'")
            else:
                test_results.append(("Search by Author", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search by Author", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Search by Tag
        print("\n[TEST3] SEARCH BY TAG")
        try:
            result = await query_books(operation="search", tag="fiction", limit=5)
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                test_results.append(("Search by Tag", True, f"Found {books_found} books"))
                print(f"[OK] Found {books_found} books with tag 'fiction'")
            else:
                test_results.append(("Search by Tag", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search by Tag", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: List All Books
        print("\n[TEST4] LIST ALL BOOKS")
        try:
            result = await query_books(operation="list", limit=20)
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                test_results.append(("List Books", True, f"Retrieved {books_found} books"))
                print(f"[OK] Listed {books_found} books")
            else:
                test_results.append(("List Books", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("List Books", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Get Recent Books
        print("\n[TEST5] GET RECENT BOOKS")
        try:
            result = await query_books(operation="recent", limit=10)
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                test_results.append(("Recent Books", True, f"Found {books_found} recent books"))
                print(f"[OK] Found {books_found} recently added books")
            else:
                test_results.append(("Recent Books", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Recent Books", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Search by Multiple Tags
        print("\n[TEST6] SEARCH BY MULTIPLE TAGS")
        try:
            result = await query_books(operation="search", tags=["fiction", "mystery"], limit=5)
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                test_results.append(("Search Multiple Tags", True, f"Found {books_found} books"))
                print(f"[OK] Found {books_found} books with tags 'fiction' AND 'mystery'")
            else:
                test_results.append(("Search Multiple Tags", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search Multiple Tags", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 7: Search by Rating
        print("\n[TEST7] SEARCH BY RATING")
        try:
            result = await query_books(operation="search", min_rating=4, limit=5)
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                test_results.append(("Search by Rating", True, f"Found {books_found} books"))
                print(f"[OK] Found {books_found} books with rating >= 4")
            else:
                test_results.append(("Search by Rating", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search by Rating", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 8: Search by Publication Date Range
        print("\n[TEST8] SEARCH BY DATE RANGE")
        try:
            result = await query_books(
                operation="search", pubdate_start="2020-01-01", pubdate_end="2024-12-31", limit=5
            )
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                test_results.append(("Search by Date", True, f"Found {books_found} books"))
                print(f"[OK] Found {books_found} books published 2020-2024")
            else:
                test_results.append(("Search by Date", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search by Date", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 9: Search with Exclusions
        print("\n[TEST9] SEARCH WITH EXCLUSIONS")
        try:
            result = await query_books(operation="search", text="book", exclude_tags=["test"], limit=5)
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                test_results.append(("Search with Exclusions", True, f"Found {books_found} books"))
                print(f"[OK] Found {books_found} books excluding 'test' tag")
            else:
                test_results.append(("Search with Exclusions", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search with Exclusions", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 10: Complex Search
        print("\n[TEST10] COMPLEX SEARCH")
        try:
            result = await query_books(operation="search", author="test", min_rating=3, tags=["fiction"], limit=5)
            if result.get("success") or "items" in result:
                books_found = len(result.get("items", []))
                test_results.append(("Complex Search", True, f"Found {books_found} books"))
                print(f"[OK] Complex search found {books_found} books")
            else:
                test_results.append(("Complex Search", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Complex Search", False, str(e)))
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
