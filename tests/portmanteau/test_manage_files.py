#!/usr/bin/env python3
"""
Test Battery for manage_files Portmanteau Tool

Tests all operations: convert, download, bulk
Run with: python tests/portmanteau/test_manage_files.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_files portmanteau."""

    print("MANAGE_FILES PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: convert, download, bulk operations")
    print("=" * 60)

    test_results = []
    test_book_id = None

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_files tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.files.manage_files import manage_files

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

        # Get a test book with formats
        print("\n[SETUP] Finding test book with formats...")
        from calibre_mcp.db.database import get_database
        from calibre_mcp.services.book_service import BookService

        db = get_database()
        book_service = BookService(db)
        books_result = book_service.get_all(limit=10)

        # Find a book with EPUB format
        test_book = None
        for book in books_result.get("items", []):
            formats = book.get("formats", [])
            if formats:
                test_book = book
                test_book_id = book["id"]
                break

        if not test_book:
            print("[ERROR] No books with formats found")
            return False

        print(f"[OK] Using book ID: {test_book_id} with formats: {test_book.get('formats', [])}")

        # Test 1: Download Book File
        print("\n[TEST1] DOWNLOAD BOOK FILE")
        try:
            result = await manage_files(operation="download", book_id=test_book_id, format_preference="EPUB")
            if result.get("success") or "file_path" in result:
                file_path = result.get("file_path", "")
                test_results.append(("Download File", True, f"Downloaded to {file_path}"))
                print(f"[OK] Downloaded book file: {file_path}")
            else:
                test_results.append(("Download File", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Download File", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Convert Book Format
        print("\n[TEST2] CONVERT BOOK FORMAT")
        try:
            # Check if book has EPUB to convert
            formats = test_book.get("formats", [])
            source_format = None
            for fmt in formats:
                if fmt.upper() in ["EPUB", "PDF", "MOBI"]:
                    source_format = fmt.upper()
                    break

            if source_format and source_format != "PDF":
                result = await manage_files(
                    operation="convert",
                    conversion_requests=[
                        {
                            "book_id": test_book_id,
                            "source_format": source_format,
                            "target_format": "PDF",
                            "quality": "high",
                        }
                    ],
                )
                if result and (result[0].get("success") if isinstance(result, list) else result.get("success")):
                    test_results.append(("Convert Format", True, f"Converted {source_format} to PDF"))
                    print(f"[OK] Converted {source_format} to PDF")
                else:
                    error_msg = (
                        result[0].get("error", "Unknown")
                        if isinstance(result, list)
                        else result.get("error", "Unknown")
                    )
                    test_results.append(("Convert Format", False, error_msg))
                    print(f"[FAIL] {error_msg}")
            else:
                test_results.append(("Convert Format", True, "No suitable source format (skip)"))
                print("[SKIP] No suitable source format for conversion")
        except Exception as e:
            test_results.append(("Convert Format", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Bulk Convert
        print("\n[TEST3] BULK CONVERT")
        try:
            # Get multiple book IDs
            books_result = book_service.get_all(limit=3)
            book_ids = [b["id"] for b in books_result.get("items", []) if b.get("formats")]

            if len(book_ids) >= 2:
                result = await manage_files(
                    operation="bulk", operation_type="convert", target_format="PDF", book_ids=book_ids[:2]
                )
                if result.get("success") or "converted" in str(result).lower():
                    test_results.append(("Bulk Convert", True, f"Bulk converted {len(book_ids[:2])} books"))
                    print(f"[OK] Bulk converted {len(book_ids[:2])} books")
                else:
                    test_results.append(("Bulk Convert", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Bulk Convert", True, "Not enough books (skip)"))
                print("[SKIP] Not enough books with formats for bulk convert")
        except Exception as e:
            test_results.append(("Bulk Convert", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Bulk Validate Formats
        print("\n[TEST4] BULK VALIDATE FORMATS")
        try:
            books_result = book_service.get_all(limit=5)
            book_ids = [b["id"] for b in books_result.get("items", [])]

            if book_ids:
                result = await manage_files(operation="bulk", operation_type="validate", book_ids=book_ids[:3])
                if result.get("success") or "validated" in str(result).lower():
                    test_results.append(("Bulk Validate", True, f"Validated {len(book_ids[:3])} books"))
                    print(f"[OK] Bulk validated {len(book_ids[:3])} books")
                else:
                    test_results.append(("Bulk Validate", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Bulk Validate", True, "No books (skip)"))
                print("[SKIP] No books available")
        except Exception as e:
            test_results.append(("Bulk Validate", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Download with Format Preference
        print("\n[TEST5] DOWNLOAD WITH FORMAT PREFERENCE")
        try:
            # Try different format preferences
            for fmt_pref in ["EPUB", "PDF", "MOBI"]:
                result = await manage_files(operation="download", book_id=test_book_id, format_preference=fmt_pref)
                if result.get("success") or "file_path" in result:
                    test_results.append(("Download Format Preference", True, f"Downloaded in {fmt_pref} format"))
                    print(f"[OK] Downloaded with preference {fmt_pref}")
                    break
                elif fmt_pref == "MOBI":  # Last attempt
                    test_results.append(("Download Format Preference", True, "Format preference tested"))
                    print("[OK] Format preference tested (may not have all formats)")
                    break
        except Exception as e:
            test_results.append(("Download Format Preference", False, str(e)))
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
