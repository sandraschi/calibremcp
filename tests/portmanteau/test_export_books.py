#!/usr/bin/env python3
"""
Test Battery for export_books Portmanteau Tool

Tests all operations: csv, json, html, pandoc
Run with: python tests/portmanteau/test_export_books.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for export_books portmanteau."""

    print("EXPORT_BOOKS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: csv, json, html, pandoc export operations")
    print("=" * 60)

    test_results = []

    try:
        # Import tool
        print("\n[IMPORT] Importing export_books tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.import_export.export_books_portmanteau import export_books

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

        # Test 1: Export to CSV
        print("\n[TEST1] EXPORT TO CSV")
        try:
            import tempfile

            export_dir = Path(tempfile.gettempdir()) / "calibre_test_export"
            export_dir.mkdir(exist_ok=True)

            result = await export_books(operation="csv", book_ids=test_book_ids[:3], limit=3, open_file=False)
            if result.get("success") or "file_path" in result:
                file_path = result.get("file_path", "")
                test_results.append(("Export CSV", True, f"Exported to {file_path}"))
                print(f"[OK] Exported to CSV: {file_path}")
            else:
                test_results.append(("Export CSV", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Export CSV", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Export to JSON
        print("\n[TEST2] EXPORT TO JSON")
        try:
            result = await export_books(
                operation="json", book_ids=test_book_ids[:3], limit=3, pretty=True, open_file=False
            )
            if result.get("success") or "file_path" in result:
                file_path = result.get("file_path", "")
                test_results.append(("Export JSON", True, f"Exported to {file_path}"))
                print(f"[OK] Exported to JSON: {file_path}")
            else:
                test_results.append(("Export JSON", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Export JSON", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Export to HTML
        print("\n[TEST3] EXPORT TO HTML")
        try:
            result = await export_books(operation="html", book_ids=test_book_ids[:3], limit=3, open_file=False)
            if result.get("success") or "file_path" in result:
                file_path = result.get("file_path", "")
                test_results.append(("Export HTML", True, f"Exported to {file_path}"))
                print(f"[OK] Exported to HTML: {file_path}")
            else:
                test_results.append(("Export HTML", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Export HTML", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Export with Author Filter
        print("\n[TEST4] EXPORT WITH AUTHOR FILTER")
        try:
            result = await export_books(operation="csv", author="test", limit=5, open_file=False)
            if result.get("success") or "file_path" in result:
                books_exported = result.get("books_exported", 0)
                test_results.append(("Export with Filter", True, f"Exported {books_exported} books"))
                print(f"[OK] Exported {books_exported} books with author filter")
            else:
                test_results.append(("Export with Filter", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Export with Filter", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Export with Tag Filter
        print("\n[TEST5] EXPORT WITH TAG FILTER")
        try:
            result = await export_books(operation="json", tag="fiction", limit=5, open_file=False)
            if result.get("success") or "file_path" in result:
                books_exported = result.get("books_exported", 0)
                test_results.append(("Export with Tag", True, f"Exported {books_exported} books"))
                print(f"[OK] Exported {books_exported} books with tag filter")
            else:
                test_results.append(("Export with Tag", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Export with Tag", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Export to Pandoc (DOCX)
        print("\n[TEST6] EXPORT TO PANDOC (DOCX)")
        try:
            # Check if pandoc is available
            import shutil

            pandoc_available = shutil.which("pandoc") is not None

            if pandoc_available:
                result = await export_books(
                    operation="pandoc", format_type="docx", book_ids=test_book_ids[:2], limit=2, open_file=False
                )
                if result.get("success") or "file_path" in result:
                    file_path = result.get("file_path", "")
                    test_results.append(("Export Pandoc", True, f"Exported to {file_path}"))
                    print(f"[OK] Exported to DOCX: {file_path}")
                else:
                    test_results.append(("Export Pandoc", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Export Pandoc", True, "Pandoc not installed (skip)"))
                print("[SKIP] Pandoc not installed")
        except Exception as e:
            test_results.append(("Export Pandoc", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 7: Export with Custom Fields
        print("\n[TEST7] EXPORT WITH CUSTOM FIELDS (CSV)")
        try:
            result = await export_books(
                operation="csv",
                book_ids=test_book_ids[:3],
                include_fields=["title", "authors", "rating", "tags"],
                limit=3,
                open_file=False,
            )
            if result.get("success") or "file_path" in result:
                file_path = result.get("file_path", "")
                test_results.append(("Export Custom Fields", True, f"Exported with custom fields to {file_path}"))
                print(f"[OK] Exported with custom fields: {file_path}")
            else:
                test_results.append(("Export Custom Fields", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Export Custom Fields", False, str(e)))
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
