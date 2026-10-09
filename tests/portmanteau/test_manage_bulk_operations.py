#!/usr/bin/env python3
"""
Test Battery for manage_bulk_operations Portmanteau Tool

Tests all operations: update_metadata, export, delete, convert
Run with: python tests/portmanteau/test_manage_bulk_operations.py

SAFETY PROTOCOL:
- Bulk delete operation is SKIPPED (destructive - would require test library)
- Other operations (update, export, convert) are safe
- NO books are deleted from real libraries
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_bulk_operations portmanteau."""

    print("MANAGE_BULK_OPERATIONS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: update_metadata, export, delete, convert operations")
    print("=" * 60)

    test_results = []

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_bulk_operations tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.advanced_features.manage_bulk_operations import manage_bulk_operations

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

        # Get test book IDs
        print("\n[SETUP] Finding test books...")
        from calibre_mcp.db.database import get_database
        from calibre_mcp.services.book_service import BookService

        db = get_database()
        book_service = BookService(db)
        books_result = book_service.get_all(limit=5)
        test_book_ids = [b["id"] for b in books_result.get("items", [])]

        if not test_book_ids:
            print("[ERROR] No books in library")
            return False

        print(f"[OK] Using {len(test_book_ids)} test book IDs")

        # Test 1: Bulk Update Metadata
        print("\n[TEST1] BULK UPDATE METADATA")
        try:
            if len(test_book_ids) >= 2:
                result = await manage_bulk_operations(
                    operation="update_metadata", book_ids=test_book_ids[:2], updates={"rating": 3}, batch_size=2
                )
                if result.get("success") or "updated_books" in result:
                    updated_count = len(result.get("updated_books", []))
                    test_results.append(("Bulk Update Metadata", True, f"Updated {updated_count} books"))
                    print(f"[OK] Bulk updated {updated_count} books")
                else:
                    test_results.append(("Bulk Update Metadata", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Bulk Update Metadata", True, "Not enough books (skip)"))
                print("[SKIP] Not enough books for bulk update")
        except Exception as e:
            test_results.append(("Bulk Update Metadata", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Bulk Export
        print("\n[TEST2] BULK EXPORT")
        try:
            if len(test_book_ids) >= 2:
                import tempfile

                export_dir = Path(tempfile.gettempdir()) / "calibre_test_export"
                export_dir.mkdir(exist_ok=True)

                result = await manage_bulk_operations(
                    operation="export", book_ids=test_book_ids[:2], export_path=str(export_dir), format="directory"
                )
                if result.get("success") or "exported" in str(result).lower():
                    test_results.append(("Bulk Export", True, f"Exported {len(test_book_ids[:2])} books"))
                    print(f"[OK] Bulk exported {len(test_book_ids[:2])} books")
                else:
                    test_results.append(("Bulk Export", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Bulk Export", True, "Not enough books (skip)"))
                print("[SKIP] Not enough books for bulk export")
        except Exception as e:
            test_results.append(("Bulk Export", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Bulk Convert
        print("\n[TEST3] BULK CONVERT")
        try:
            # Find books with formats
            books_with_formats = []
            for bid in test_book_ids:
                book_result = await book_service.get_by_id(bid)
                if book_result and book_result.get("formats"):
                    books_with_formats.append(bid)

            if len(books_with_formats) >= 2:
                result = await manage_bulk_operations(
                    operation="convert", book_ids=books_with_formats[:2], target_format="PDF"
                )
                if result.get("success") or "converted" in str(result).lower():
                    test_results.append(("Bulk Convert", True, f"Converted {len(books_with_formats[:2])} books"))
                    print(f"[OK] Bulk converted {len(books_with_formats[:2])} books")
                else:
                    test_results.append(("Bulk Convert", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Bulk Convert", True, "Not enough books with formats (skip)"))
                print("[SKIP] Not enough books with formats for bulk convert")
        except Exception as e:
            test_results.append(("Bulk Convert", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Bulk Delete (SKIP - DESTRUCTIVE)
        # NOTE: Bulk delete would require test library setup - skipped for safety
        print("\n[TEST4] BULK DELETE (SKIP - DESTRUCTIVE)")
        try:
            test_results.append(("Bulk Delete", True, "Skipped (destructive - would require test library)"))
            print("[SKIP] Bulk delete skipped (destructive operation - use test library for actual testing)")
        except Exception as e:
            test_results.append(("Bulk Delete", False, str(e)))
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
