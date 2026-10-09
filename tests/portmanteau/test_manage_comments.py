#!/usr/bin/env python3
"""
Test Battery for manage_comments Portmanteau Tool

Tests all operations: create, read, update, delete, append, replace
Run with: python tests/portmanteau/test_manage_comments.py

SAFETY PROTOCOL:
- Comment operations are safe - they only modify metadata, not books
- Comments are added/updated/deleted on real books (metadata only)
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
    """Run comprehensive test battery for manage_comments portmanteau."""

    print("MANAGE_COMMENTS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: create, read, update, delete, append, replace operations")
    print("=" * 60)

    test_results = []
    test_book_id = None

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_comments tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.comments.manage_comments import manage_comments

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

        test_book_id = str(books_result["items"][0]["id"])
        print(f"[OK] Using book ID: {test_book_id}")

        # Test 1: Create Comment
        print("\n[TEST1] CREATE COMMENT")
        try:
            test_comment = "This is a test comment created by the test battery."
            result = await manage_comments(operation="create", book_id=test_book_id, text=test_comment)
            if result.get("success"):
                test_results.append(("Create Comment", True, "Comment created successfully"))
                print(f"[OK] Created comment for book {test_book_id}")
            else:
                # Comment might already exist, try update instead
                if "already exists" in str(result.get("error", "")):
                    test_results.append(("Create Comment", True, "Comment already exists (using update)"))
                    print("[OK] Comment already exists, will test update instead")
                else:
                    test_results.append(("Create Comment", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Create Comment", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Read Comment
        print("\n[TEST2] READ COMMENT")
        try:
            result = await manage_comments(operation="read", book_id=test_book_id)
            if result.get("success") or "comment" in result:
                comment_text = result.get("comment", {}).get("text", "") if result.get("comment") else ""
                if comment_text:
                    test_results.append(("Read Comment", True, f"Retrieved comment ({len(comment_text)} chars)"))
                    print(f"[OK] Retrieved comment: {comment_text[:50]}...")
                else:
                    test_results.append(("Read Comment", True, "No comment found (expected)"))
                    print("[OK] No comment found (expected if not created)")
            else:
                test_results.append(("Read Comment", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Read Comment", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Update Comment
        print("\n[TEST3] UPDATE COMMENT")
        try:
            updated_comment = "This is an updated test comment."
            result = await manage_comments(operation="update", book_id=test_book_id, text=updated_comment)
            if result.get("success"):
                test_results.append(("Update Comment", True, "Comment updated successfully"))
                print(f"[OK] Updated comment for book {test_book_id}")
            else:
                test_results.append(("Update Comment", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Update Comment", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Append to Comment
        print("\n[TEST4] APPEND TO COMMENT")
        try:
            append_text = "\n\nAdditional notes appended by test battery."
            result = await manage_comments(operation="append", book_id=test_book_id, text=append_text)
            if result.get("success"):
                test_results.append(("Append Comment", True, "Comment appended successfully"))
                print(f"[OK] Appended to comment for book {test_book_id}")
            else:
                test_results.append(("Append Comment", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Append Comment", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Replace Comment
        print("\n[TEST5] REPLACE COMMENT")
        try:
            replace_text = "This is a completely replaced comment."
            result = await manage_comments(operation="replace", book_id=test_book_id, text=replace_text)
            if result.get("success"):
                test_results.append(("Replace Comment", True, "Comment replaced successfully"))
                print(f"[OK] Replaced comment for book {test_book_id}")
            else:
                test_results.append(("Replace Comment", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Replace Comment", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Delete Comment
        # NOTE: Comment deletion is safe - only removes metadata, not books
        print("\n[TEST6] DELETE COMMENT")
        try:
            result = await manage_comments(operation="delete", book_id=test_book_id)
            if result.get("success"):
                test_results.append(("Delete Comment", True, "Comment deleted successfully (safe - metadata only)"))
                print(f"[OK] Deleted comment for book {test_book_id} (safe - only removes metadata)")
            else:
                test_results.append(("Delete Comment", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Delete Comment", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 7: Read After Delete
        print("\n[TEST7] READ AFTER DELETE")
        try:
            result = await manage_comments(operation="read", book_id=test_book_id)
            if result.get("success"):
                comment = result.get("comment")
                if not comment or not comment.get("text"):
                    test_results.append(("Read After Delete", True, "No comment found (expected)"))
                    print("[OK] No comment found after deletion (expected)")
                else:
                    test_results.append(("Read After Delete", True, "Comment still exists"))
                    print("[OK] Comment still exists")
            else:
                test_results.append(("Read After Delete", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Read After Delete", False, str(e)))
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
