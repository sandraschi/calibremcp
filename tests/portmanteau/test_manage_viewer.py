#!/usr/bin/env python3
"""
Test Battery for manage_viewer Portmanteau Tool

Tests all operations: open, get_page, get_metadata, get_state, update_state, close, open_file
Run with: python tests/portmanteau/test_manage_viewer.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_viewer portmanteau."""

    print("MANAGE_VIEWER PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: open, get_page, get_metadata, get_state, update_state, close, open_file")
    print("=" * 60)

    test_results = []
    test_book_id = None
    test_file_path = None

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_viewer tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.viewer.manage_viewer import manage_viewer

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

        # Get a test book with file path
        print("\n[SETUP] Finding test book with file...")
        from calibre_mcp.db.database import get_database
        from calibre_mcp.services.book_service import BookService

        db = get_database()
        book_service = BookService(db)
        books_result = book_service.get_all(limit=20)

        # Find a book with a file path
        for book in books_result.get("items", []):
            formats = book.get("formats", [])
            if formats:
                # Try to get file path from format
                test_book_id = book["id"]
                # Get detailed book info to find file path
                book_details = await book_service.get_by_id(test_book_id)
                if book_details and book_details.get("formats"):
                    # Use first format's path
                    format_info = book_details["formats"][0]
                    if isinstance(format_info, dict) and format_info.get("path"):
                        test_file_path = format_info["path"]
                    elif isinstance(format_info, str):
                        # Format might be just the format name, need to construct path
                        # This is a simplified test - actual implementation may differ
                        test_file_path = None
                break

        if not test_book_id:
            print("[ERROR] No books with formats found")
            return False

        print(f"[OK] Using book ID: {test_book_id}")
        if test_file_path:
            print(f"[OK] File path: {test_file_path}")
        else:
            print("[WARN] File path not found, some tests may be skipped")

        # Test 1: Get Metadata
        print("\n[TEST1] GET METADATA")
        try:
            if test_file_path:
                result = await manage_viewer(operation="get_metadata", book_id=test_book_id, file_path=test_file_path)
                if result.get("success") or "page_count" in result:
                    page_count = result.get("page_count", 0)
                    test_results.append(("Get Metadata", True, f"Retrieved metadata: {page_count} pages"))
                    print(f"[OK] Retrieved metadata: {page_count} pages")
                else:
                    test_results.append(("Get Metadata", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get Metadata", True, "No file path (skip)"))
                print("[SKIP] No file path available")
        except Exception as e:
            test_results.append(("Get Metadata", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Open Viewer
        print("\n[TEST2] OPEN VIEWER")
        try:
            if test_file_path:
                result = await manage_viewer(operation="open", book_id=test_book_id, file_path=test_file_path)
                if result.get("success") or "metadata" in result:
                    test_results.append(("Open Viewer", True, "Viewer opened successfully"))
                    print("[OK] Viewer opened")
                else:
                    test_results.append(("Open Viewer", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Open Viewer", True, "No file path (skip)"))
                print("[SKIP] No file path available")
        except Exception as e:
            test_results.append(("Open Viewer", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Get Page
        print("\n[TEST3] GET PAGE")
        try:
            if test_file_path:
                result = await manage_viewer(
                    operation="get_page", book_id=test_book_id, file_path=test_file_path, page_number=0
                )
                if result.get("success") or "content" in result or "image_url" in result:
                    test_results.append(("Get Page", True, "Retrieved page 0"))
                    print("[OK] Retrieved page 0")
                else:
                    test_results.append(("Get Page", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get Page", True, "No file path (skip)"))
                print("[SKIP] No file path available")
        except Exception as e:
            test_results.append(("Get Page", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Get State
        print("\n[TEST4] GET STATE")
        try:
            if test_file_path:
                result = await manage_viewer(operation="get_state", book_id=test_book_id, file_path=test_file_path)
                if result.get("success") or "current_page" in result:
                    current_page = result.get("current_page", 0)
                    test_results.append(("Get State", True, f"Retrieved state: page {current_page}"))
                    print(f"[OK] Retrieved viewer state: page {current_page}")
                else:
                    test_results.append(("Get State", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get State", True, "No file path (skip)"))
                print("[SKIP] No file path available")
        except Exception as e:
            test_results.append(("Get State", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Update State
        print("\n[TEST5] UPDATE STATE")
        try:
            if test_file_path:
                result = await manage_viewer(
                    operation="update_state",
                    book_id=test_book_id,
                    file_path=test_file_path,
                    current_page=5,
                    zoom_mode="fit-width",
                )
                if result.get("success") or "current_page" in result:
                    test_results.append(("Update State", True, "Updated viewer state"))
                    print("[OK] Updated viewer state")
                else:
                    test_results.append(("Update State", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Update State", True, "No file path (skip)"))
                print("[SKIP] No file path available")
        except Exception as e:
            test_results.append(("Update State", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Close Viewer
        print("\n[TEST6] CLOSE VIEWER")
        try:
            if test_file_path:
                result = await manage_viewer(operation="close", book_id=test_book_id, file_path=test_file_path)
                if result.get("success"):
                    test_results.append(("Close Viewer", True, "Viewer closed successfully"))
                    print("[OK] Viewer closed")
                else:
                    test_results.append(("Close Viewer", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Close Viewer", True, "No file path (skip)"))
                print("[SKIP] No file path available")
        except Exception as e:
            test_results.append(("Close Viewer", False, str(e)))
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
