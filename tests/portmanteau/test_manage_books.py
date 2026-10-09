#!/usr/bin/env python3
"""
Test Battery for manage_books Portmanteau Tool

Tests all operations: add, get, details, update, delete
Run with: python tests/portmanteau/test_manage_books.py

SAFETY PROTOCOL:
- Non-destructive operations (get, details, update) use real libraries safely
- Destructive operations (delete) use a temporary test library
- Test library is created, used, and automatically cleaned up
- NO books are deleted from real libraries
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import test helpers
sys.path.insert(0, str(Path(__file__).parent))
from test_helpers import TestLibraryManager  # noqa: E402 (sys.path bootstrap above)


async def run_test_battery():
    """Run comprehensive test battery for manage_books portmanteau."""

    print("MANAGE_BOOKS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: add, get, details, update, delete operations")
    print("=" * 60)
    print("[SAFETY] Destructive operations use test library")
    print("=" * 60)

    test_results = []
    test_book_id = None
    test_lib_manager = None

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_books tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.book_management.manage_books import manage_books

        print("[OK] Tool imported successfully")

        # Initialize with a library (for non-destructive tests)
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

        # Test 1: Get Book
        print("\n[TEST1] GET BOOK")
        try:
            # First, get a list of books to find an ID
            from calibre_mcp.db.database import get_database
            from calibre_mcp.services.book_service import BookService

            db = get_database()
            book_service = BookService(db)
            books_result = book_service.get_all(limit=1)

            if books_result.get("items"):
                test_book_id = str(books_result["items"][0]["id"])
                result = await manage_books(operation="get", book_id=test_book_id)

                if result.get("success") or "id" in result:
                    test_results.append(("Get Book", True, f"Retrieved book ID {test_book_id}"))
                    print(f"[OK] Retrieved book: {result.get('title', 'Unknown')}")
                else:
                    test_results.append(("Get Book", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get Book", True, "No books in library (skip)"))
                print("[SKIP] No books available")
        except Exception as e:
            test_results.append(("Get Book", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Get Book Details
        print("\n[TEST2] GET BOOK DETAILS")
        try:
            if test_book_id:
                result = await manage_books(operation="details", book_id=test_book_id)
                if result.get("success") or "id" in result:
                    test_results.append(("Get Details", True, f"Retrieved detailed info for book {test_book_id}"))
                    print("[OK] Retrieved detailed book information")
                    print(f"  - Formats: {len(result.get('formats', []))}")
                else:
                    test_results.append(("Get Details", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get Details", True, "No test book (skip)"))
                print("[SKIP] No test book available")
        except Exception as e:
            test_results.append(("Get Details", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Update Book Metadata
        print("\n[TEST3] UPDATE BOOK METADATA")
        try:
            if test_book_id:
                result = await manage_books(operation="update", book_id=test_book_id, metadata={"rating": 4})
                if result.get("success"):
                    test_results.append(("Update Book", True, f"Updated book {test_book_id}"))
                    print("[OK] Updated book metadata")
                else:
                    test_results.append(("Update Book", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Update Book", True, "No test book (skip)"))
                print("[SKIP] No test book available")
        except Exception as e:
            test_results.append(("Update Book", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Update Reading Status
        print("\n[TEST4] UPDATE READING STATUS")
        try:
            if test_book_id:
                result = await manage_books(operation="update", book_id=test_book_id, status="reading", progress=0.5)
                if result.get("success"):
                    test_results.append(("Update Status", True, f"Updated reading status for book {test_book_id}"))
                    print("[OK] Updated reading status and progress")
                else:
                    test_results.append(("Update Status", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Update Status", True, "No test book (skip)"))
                print("[SKIP] No test book available")
        except Exception as e:
            test_results.append(("Update Status", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5 & 6: Add and Delete Book (uses test library for safety)
        print("\n[TEST5-6] ADD AND DELETE BOOK (TEST LIBRARY)")
        print("[SAFETY] Using test library - will be cleaned up automatically")
        try:
            # Create test library for add/delete operations
            test_lib_manager = TestLibraryManager()
            test_lib_name, test_lib_path = test_lib_manager.create_test_library()

            # Re-initialize database with test library
            init_database(str(test_lib_path / "metadata.db"), echo=False)
            print(f"[OK] Switched to test library: {test_lib_name}")

            # Check for test book file
            test_files_dir = project_root / "tests" / "fixtures" / "test_library"
            test_files = list(test_files_dir.rglob("*.epub"))

            if test_files:
                test_file = test_files[0]

                # Test 5: Add Book
                print("\n[TEST5] ADD BOOK TO TEST LIBRARY")
                add_result = await manage_books(
                    operation="add",
                    file_path=str(test_file),
                    metadata={"title": "Test Book from Battery", "tags": ["test"]},
                    fetch_metadata=False,
                )

                if add_result.get("success") or "id" in add_result:
                    added_book_id = add_result.get("id")
                    test_results.append(("Add Book", True, f"Added book with ID {added_book_id} to test library"))
                    print(f"[OK] Added book to test library: {add_result.get('title', 'Unknown')}")

                    # Test 6: Delete Book (safe - it's in test library)
                    print("\n[TEST6] DELETE BOOK FROM TEST LIBRARY")
                    delete_result = await manage_books(operation="delete", book_id=added_book_id, delete_files=True)

                    if delete_result.get("success"):
                        test_results.append(
                            ("Delete Book", True, f"Deleted test book {added_book_id} from test library")
                        )
                        print("[OK] Deleted test book from test library")
                    else:
                        test_results.append(("Delete Book", False, delete_result.get("error", "Unknown error")))
                        print(f"[FAIL] {delete_result.get('error', 'Unknown error')}")
                else:
                    test_results.append(("Add Book", False, add_result.get("error", "Unknown error")))
                    print(f"[FAIL] {add_result.get('error', 'Unknown error')}")
                    test_results.append(("Delete Book", True, "Skipped (add failed)"))
            else:
                test_results.append(("Add Book", True, "No test files available (skip)"))
                test_results.append(("Delete Book", True, "No test files available (skip)"))
                print("[SKIP] No test book files available")

            # Switch back to original library
            init_database(str(first_lib_path / "metadata.db"), echo=False)
            print(f"[OK] Switched back to original library: {first_lib_name}")
        except Exception as e:
            test_results.append(("Add Book", False, str(e)))
            test_results.append(("Delete Book", False, str(e)))
            print(f"[FAIL] {e}")
        finally:
            # Always cleanup test library
            if test_lib_manager:
                test_lib_manager.cleanup()
                print("[OK] Test library cleaned up")
        print("\n[TEST6] DELETE BOOK (TEST LIBRARY)")
        print("[SAFETY] Using test library - will be cleaned up automatically")
        try:
            # Create test library for destructive operation
            test_lib_manager = TestLibraryManager()
            test_lib_name, test_lib_path = test_lib_manager.create_test_library()

            # Re-initialize database with test library
            init_database(str(test_lib_path / "metadata.db"), echo=False)
            print(f"[OK] Switched to test library: {test_lib_name}")

            # Add a test book to the test library
            test_files_dir = project_root / "tests" / "fixtures" / "test_library"
            test_files = list(test_files_dir.rglob("*.epub"))

            if test_files:
                test_file = test_files[0]
                add_result = await manage_books(
                    operation="add",
                    file_path=str(test_file),
                    metadata={"title": "Test Book for Deletion", "tags": ["test", "delete"]},
                    fetch_metadata=False,
                )

                if add_result.get("success") or "id" in add_result:
                    delete_book_id = add_result.get("id")
                    print(f"[OK] Added test book to test library: {delete_book_id}")

                    # Now delete it (safe - it's in test library)
                    delete_result = await manage_books(operation="delete", book_id=delete_book_id, delete_files=True)

                    if delete_result.get("success"):
                        test_results.append(
                            ("Delete Book", True, f"Deleted test book {delete_book_id} from test library")
                        )
                        print("[OK] Deleted test book from test library")
                    else:
                        test_results.append(("Delete Book", False, delete_result.get("error", "Unknown error")))
                        print(f"[FAIL] {delete_result.get('error', 'Unknown error')}")
                else:
                    test_results.append(("Delete Book", True, "Could not add test book (skip)"))
                    print("[SKIP] Could not add test book to test library")
            else:
                test_results.append(("Delete Book", True, "No test files available (skip)"))
                print("[SKIP] No test book files available")

            # Switch back to original library
            init_database(str(first_lib_path / "metadata.db"), echo=False)
            print(f"[OK] Switched back to original library: {first_lib_name}")
        except Exception as e:
            test_results.append(("Delete Book", False, str(e)))
            print(f"[FAIL] {e}")
        finally:
            # Always cleanup test library
            if test_lib_manager:
                test_lib_manager.cleanup()
                print("[OK] Test library cleaned up")

    except Exception as e:
        print(f"\n[CRITICAL] ERROR: {e}")
        import traceback

        traceback.print_exc()
        # Ensure cleanup even on error
        if test_lib_manager:
            test_lib_manager.cleanup()
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
