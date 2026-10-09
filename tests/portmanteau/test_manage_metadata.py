#!/usr/bin/env python3
"""
Test Battery for manage_metadata Portmanteau Tool

Tests all operations: update, organize_tags, fix_issues
Run with: python tests/portmanteau/test_manage_metadata.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_metadata portmanteau."""

    print("MANAGE_METADATA PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: update, organize_tags, fix_issues operations")
    print("=" * 60)

    test_results = []
    test_book_id = None

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_metadata tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.metadata.manage_metadata import manage_metadata

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

        # Get a test book ID
        print("\n[SETUP] Finding test book...")
        from calibre_mcp.db.database import get_database
        from calibre_mcp.services.book_service import BookService

        db = get_database()
        book_service = BookService(db)
        books_result = book_service.get_all(limit=1)

        if not books_result.get("items"):
            print("[ERROR] No books in library")
            return False

        test_book_id = books_result["items"][0]["id"]
        print(f"[OK] Using book ID: {test_book_id}")

        # Test 1: Update Metadata
        print("\n[TEST1] UPDATE METADATA")
        try:
            result = await manage_metadata(
                operation="update", updates=[{"book_id": test_book_id, "field": "rating", "value": 4}]
            )
            if result.get("success") or "updated_books" in result:
                updated_count = len(result.get("updated_books", []))
                test_results.append(("Update Metadata", True, f"Updated {updated_count} book(s)"))
                print(f"[OK] Updated metadata for {updated_count} book(s)")
            else:
                test_results.append(("Update Metadata", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Update Metadata", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Bulk Update Metadata
        print("\n[TEST2] BULK UPDATE METADATA")
        try:
            # Get multiple book IDs
            books_result = book_service.get_all(limit=3)
            book_ids = [b["id"] for b in books_result.get("items", [])]

            if book_ids:
                updates = [{"book_id": bid, "field": "rating", "value": 3} for bid in book_ids]
                result = await manage_metadata(operation="update", updates=updates)
                if result.get("success") or "updated_books" in result:
                    updated_count = len(result.get("updated_books", []))
                    test_results.append(("Bulk Update", True, f"Updated {updated_count} books"))
                    print(f"[OK] Bulk updated {updated_count} books")
                else:
                    test_results.append(("Bulk Update", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Bulk Update", True, "Not enough books (skip)"))
                print("[SKIP] Not enough books for bulk update")
        except Exception as e:
            test_results.append(("Bulk Update", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Organize Tags
        print("\n[TEST3] ORGANIZE TAGS")
        try:
            result = await manage_metadata(operation="organize_tags")
            if result.get("success") or "duplicate_tags" in result or "suggestions" in result:
                test_results.append(("Organize Tags", True, "Tag organization completed"))
                print("[OK] Tag organization completed")
                if result.get("duplicate_tags"):
                    print(f"  - Found {len(result['duplicate_tags'])} duplicate tag groups")
            else:
                test_results.append(("Organize Tags", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Organize Tags", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Fix Metadata Issues
        print("\n[TEST4] FIX METADATA ISSUES")
        try:
            result = await manage_metadata(operation="fix_issues")
            if result.get("success") or "fixed_books" in result or "issues_found" in result:
                fixed_count = result.get("fixed_books", 0) or len(result.get("issues_found", []))
                test_results.append(("Fix Issues", True, f"Fixed {fixed_count} issue(s)"))
                print(f"[OK] Metadata fix completed: {fixed_count} issue(s) addressed")
            else:
                test_results.append(("Fix Issues", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Fix Issues", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Update Multiple Fields
        print("\n[TEST5] UPDATE MULTIPLE FIELDS")
        try:
            updates = [
                {"book_id": test_book_id, "field": "rating", "value": 5},
                {"book_id": test_book_id, "field": "pubdate", "value": "2024-01-01"},
            ]
            result = await manage_metadata(operation="update", updates=updates)
            if result.get("success") or "updated_books" in result:
                updated_count = len(result.get("updated_books", []))
                test_results.append(("Update Multiple Fields", True, f"Updated {updated_count} book(s)"))
                print(f"[OK] Updated multiple fields for {updated_count} book(s)")
            else:
                test_results.append(("Update Multiple Fields", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Update Multiple Fields", False, str(e)))
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
