#!/usr/bin/env python3
"""
Test Battery for manage_analysis Portmanteau Tool

Tests all operations: tag_statistics, duplicate_books, series_analysis, library_health, unread_priority, reading_stats
Run with: python tests/portmanteau/test_manage_analysis.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_analysis portmanteau."""

    print("MANAGE_ANALYSIS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: tag_statistics, duplicate_books, series_analysis, library_health, unread_priority, reading_stats")
    print("=" * 60)

    test_results = []

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_analysis tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.analysis.manage_analysis import manage_analysis

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

        # Test 1: Tag Statistics
        print("\n[TEST1] TAG STATISTICS")
        try:
            result = await manage_analysis(operation="tag_statistics")
            if result.get("success") or "total_tags" in result or "duplicate_tags" in result:
                total_tags = result.get("total_tags", 0)
                test_results.append(("Tag Statistics", True, f"Analyzed {total_tags} tags"))
                print(f"[OK] Tag statistics retrieved: {total_tags} total tags")
                if result.get("duplicate_tags"):
                    print(f"  - Found {len(result['duplicate_tags'])} duplicate groups")
            else:
                test_results.append(("Tag Statistics", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Tag Statistics", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Find Duplicate Books
        print("\n[TEST2] FIND DUPLICATE BOOKS")
        try:
            result = await manage_analysis(operation="duplicate_books")
            if result.get("success") or "duplicate_groups" in result:
                dup_groups = len(result.get("duplicate_groups", []))
                test_results.append(("Duplicate Books", True, f"Found {dup_groups} duplicate groups"))
                print(f"[OK] Found {dup_groups} duplicate book groups")
            else:
                test_results.append(("Duplicate Books", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Duplicate Books", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Series Analysis
        print("\n[TEST3] SERIES ANALYSIS")
        try:
            result = await manage_analysis(operation="series_analysis")
            if result.get("success") or "incomplete_series" in result or "series_statistics" in result:
                incomplete = len(result.get("incomplete_series", []))
                test_results.append(("Series Analysis", True, f"Found {incomplete} incomplete series"))
                print(f"[OK] Series analysis completed: {incomplete} incomplete series")
            else:
                test_results.append(("Series Analysis", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Series Analysis", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Library Health Check
        print("\n[TEST4] LIBRARY HEALTH CHECK")
        try:
            result = await manage_analysis(operation="library_health")
            if result.get("success") or "health_score" in result or "issues_found" in result:
                health_score = result.get("health_score", 0)
                issues = len(result.get("issues_found", []))
                test_results.append(("Library Health", True, f"Health score: {health_score}, {issues} issues"))
                print(f"[OK] Library health check: score {health_score}, {issues} issues found")
            else:
                test_results.append(("Library Health", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Library Health", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Unread Priority
        print("\n[TEST5] UNREAD PRIORITY")
        try:
            result = await manage_analysis(operation="unread_priority")
            if result.get("success") or "prioritized_books" in result:
                prioritized = len(result.get("prioritized_books", []))
                test_results.append(("Unread Priority", True, f"Prioritized {prioritized} unread books"))
                print(f"[OK] Prioritized {prioritized} unread books")
            else:
                test_results.append(("Unread Priority", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Unread Priority", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Reading Statistics
        print("\n[TEST6] READING STATISTICS")
        try:
            result = await manage_analysis(operation="reading_stats")
            if result.get("success") or "total_books_read" in result or "reading_patterns" in result:
                books_read = result.get("total_books_read", 0)
                test_results.append(("Reading Stats", True, f"Found {books_read} books read"))
                print(f"[OK] Reading statistics: {books_read} books read")
            else:
                test_results.append(("Reading Stats", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Reading Stats", False, str(e)))
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
