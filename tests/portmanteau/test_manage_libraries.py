#!/usr/bin/env python3
"""
Test Battery for manage_libraries Portmanteau Tool

Tests all operations: list, switch, stats, search
Run with: python tests/portmanteau/test_manage_libraries.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_libraries portmanteau."""

    print("MANAGE_LIBRARIES PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: list, switch, stats, search operations")
    print("=" * 60)

    test_results = []

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_libraries tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.library.manage_libraries import manage_libraries

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

        # Test 1: List Libraries
        print("\n[TEST1] LIST LIBRARIES")
        try:
            result = await manage_libraries(operation="list")
            if result.get("success") or "libraries" in result:
                lib_count = len(result.get("libraries", []))
                test_results.append(("List Libraries", True, f"Found {lib_count} libraries"))
                print(f"[OK] Found {lib_count} libraries")
                for lib in result.get("libraries", [])[:3]:
                    print(f"  - {lib.get('name', 'Unknown')}: {lib.get('book_count', 0)} books")
            else:
                test_results.append(("List Libraries", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("List Libraries", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Switch Library
        print("\n[TEST2] SWITCH LIBRARY")
        try:
            if len(libraries) > 1:
                second_lib_name = list(libraries.keys())[1]
                result = await manage_libraries(operation="switch", library_name=second_lib_name)
                if result.get("success"):
                    test_results.append(("Switch Library", True, f"Switched to {second_lib_name}"))
                    print(f"[OK] Switched to library: {second_lib_name}")

                    # Switch back
                    await manage_libraries(operation="switch", library_name=first_lib_name)
                else:
                    test_results.append(("Switch Library", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Switch Library", True, "Only one library available (skip)"))
                print("[SKIP] Only one library available")
        except Exception as e:
            test_results.append(("Switch Library", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Get Library Stats
        print("\n[TEST3] GET LIBRARY STATS")
        try:
            result = await manage_libraries(operation="stats", library_name=first_lib_name)
            if result.get("success") or "total_books" in result:
                total_books = result.get("total_books", 0)
                test_results.append(("Get Stats", True, f"Library has {total_books} books"))
                print(f"[OK] Library stats retrieved: {total_books} books")
                print(f"  - Authors: {result.get('total_authors', 0)}")
                print(f"  - Tags: {result.get('total_tags', 0)}")
            else:
                test_results.append(("Get Stats", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Get Stats", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Cross-Library Search
        print("\n[TEST4] CROSS-LIBRARY SEARCH")
        try:
            result = await manage_libraries(operation="search", query="book", limit=10)
            if result.get("success") or "results" in result:
                books_found = result.get("total_found", len(result.get("results", [])))
                test_results.append(("Cross-Library Search", True, f"Found {books_found} books"))
                print(f"[OK] Cross-library search found {books_found} books")
            else:
                test_results.append(("Cross-Library Search", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Cross-Library Search", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Search with Library Filter
        print("\n[TEST5] SEARCH WITH LIBRARY FILTER")
        try:
            result = await manage_libraries(operation="search", query="book", libraries=[first_lib_name], limit=5)
            if result.get("success") or "results" in result:
                books_found = result.get("total_found", len(result.get("results", [])))
                test_results.append(("Search with Filter", True, f"Found {books_found} books in filtered libraries"))
                print(f"[OK] Filtered search found {books_found} books")
            else:
                test_results.append(("Search with Filter", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search with Filter", False, str(e)))
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
