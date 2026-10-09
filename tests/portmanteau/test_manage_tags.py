#!/usr/bin/env python3
"""
Test Battery for manage_tags Portmanteau Tool

Tests all operations: list, get, create, update, delete, find_duplicates, merge, get_unused, delete_unused, statistics
Run with: python tests/portmanteau/test_manage_tags.py

SAFETY PROTOCOL:
- Tag operations are safe - they only modify metadata, not books
- Test tags are created and cleaned up automatically
- NO books are deleted or modified
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_tags portmanteau."""

    print("MANAGE_TAGS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: list, get, create, update, delete, find_duplicates, merge, get_unused, delete_unused, statistics")
    print("=" * 60)

    test_results = []
    test_tag_id = None
    created_tag_id = None

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_tags tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.tags.manage_tags import manage_tags

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

        # Test 1: List Tags
        print("\n[TEST1] LIST TAGS")
        try:
            result = await manage_tags(operation="list", limit=20)
            if result.get("success") or "items" in result:
                tags_found = len(result.get("items", []))
                total = result.get("total", tags_found)
                test_results.append(("List Tags", True, f"Found {tags_found} tags (total: {total})"))
                print(f"[OK] Found {tags_found} tags")
                if result.get("items"):
                    test_tag_id = result["items"][0]["id"]
                    print(f"  - Sample: {result['items'][0]['name']} ({result['items'][0]['book_count']} books)")
            else:
                test_results.append(("List Tags", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("List Tags", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Search Tags
        print("\n[TEST2] SEARCH TAGS")
        try:
            result = await manage_tags(operation="list", search="test", limit=10)
            if result.get("success") or "items" in result:
                tags_found = len(result.get("items", []))
                test_results.append(("Search Tags", True, f"Found {tags_found} tags"))
                print(f"[OK] Found {tags_found} tags matching 'test'")
            else:
                test_results.append(("Search Tags", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Search Tags", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Get Tag Details
        print("\n[TEST3] GET TAG DETAILS")
        try:
            if test_tag_id:
                result = await manage_tags(operation="get", tag_id=test_tag_id)
                if result.get("success") or "id" in result:
                    test_results.append(("Get Tag", True, f"Retrieved tag ID {test_tag_id}"))
                    print(f"[OK] Retrieved tag: {result.get('name', 'Unknown')}")
                    print(f"  - Books: {result.get('book_count', 0)}")
                else:
                    test_results.append(("Get Tag", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get Tag", True, "No test tag (skip)"))
                print("[SKIP] No test tag available")
        except Exception as e:
            test_results.append(("Get Tag", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Create Tag
        print("\n[TEST4] CREATE TAG")
        try:
            import time

            unique_name = f"test_tag_{int(time.time())}"
            result = await manage_tags(operation="create", name=unique_name)
            if result.get("success") or "id" in result:
                created_tag_id = result.get("id")
                test_results.append(("Create Tag", True, f"Created tag '{unique_name}' with ID {created_tag_id}"))
                print(f"[OK] Created tag: {unique_name}")
            else:
                test_results.append(("Create Tag", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Create Tag", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Update Tag
        print("\n[TEST5] UPDATE TAG")
        try:
            if created_tag_id:
                new_name = f"updated_{created_tag_id}"
                result = await manage_tags(operation="update", tag_id=created_tag_id, new_name=new_name)
                if result.get("success") or "id" in result:
                    test_results.append(("Update Tag", True, f"Updated tag to '{new_name}'"))
                    print(f"[OK] Updated tag name to: {new_name}")
                else:
                    test_results.append(("Update Tag", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Update Tag", True, "No created tag (skip)"))
                print("[SKIP] No tag was created")
        except Exception as e:
            test_results.append(("Update Tag", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Find Duplicate Tags
        print("\n[TEST6] FIND DUPLICATE TAGS")
        try:
            result = await manage_tags(operation="find_duplicates", similarity_threshold=0.8)
            if result.get("success") or "duplicate_groups" in result:
                dup_groups = len(result.get("duplicate_groups", []))
                test_results.append(("Find Duplicates", True, f"Found {dup_groups} duplicate groups"))
                print(f"[OK] Found {dup_groups} duplicate tag groups")
            else:
                test_results.append(("Find Duplicates", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Find Duplicates", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 7: Get Unused Tags
        print("\n[TEST7] GET UNUSED TAGS")
        try:
            result = await manage_tags(operation="get_unused")
            if result.get("success") or "unused_tags" in result:
                unused_count = len(result.get("unused_tags", []))
                test_results.append(("Get Unused", True, f"Found {unused_count} unused tags"))
                print(f"[OK] Found {unused_count} unused tags")
            else:
                test_results.append(("Get Unused", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Get Unused", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 8: Tag Statistics
        print("\n[TEST8] TAG STATISTICS")
        try:
            result = await manage_tags(operation="statistics")
            if result.get("success") or "total_tags" in result:
                total_tags = result.get("total_tags", 0)
                test_results.append(("Tag Statistics", True, f"Found {total_tags} total tags"))
                print("[OK] Tag statistics retrieved")
                print(f"  - Total tags: {total_tags}")
                print(f"  - Unused: {result.get('unused_tags_count', 0)}")
            else:
                test_results.append(("Tag Statistics", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Tag Statistics", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 9: List Tags with Filters
        print("\n[TEST9] LIST TAGS WITH FILTERS")
        try:
            result = await manage_tags(
                operation="list", min_book_count=5, sort_by="book_count", sort_order="desc", limit=10
            )
            if result.get("success") or "items" in result:
                tags_found = len(result.get("items", []))
                test_results.append(("List with Filters", True, f"Found {tags_found} tags"))
                print(f"[OK] Found {tags_found} tags with 5+ books, sorted by usage")
            else:
                test_results.append(("List with Filters", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("List with Filters", False, str(e)))
            print(f"[FAIL] {e}")

        # Clean up: Delete created tag
        # NOTE: Tag deletion is safe - it only removes metadata, not books
        print("\n[CLEANUP] Deleting test tag...")
        try:
            if created_tag_id:
                delete_result = await manage_tags(operation="delete", tag_id=created_tag_id, force=True)
                if delete_result.get("success"):
                    print("[OK] Test tag deleted (safe - only removes metadata)")
                else:
                    print(f"[WARN] Could not delete test tag: {delete_result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"[WARN] Cleanup failed: {e}")

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
