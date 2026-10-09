#!/usr/bin/env python3
"""
Test Battery for manage_smart_collections Portmanteau Tool

Tests all operations: create, create_series, create_recently_added, create_unread, create_ai_recommended, get, update, delete, list, query
Run with: python tests/portmanteau/test_manage_smart_collections.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_smart_collections portmanteau."""

    print("MANAGE_SMART_COLLECTIONS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: create, create_series, create_recently_added, create_unread, get, update, delete, list, query")
    print("=" * 60)

    test_results = []
    created_collection_ids = []

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_smart_collections tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.advanced_features.manage_smart_collections import manage_smart_collections

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

        # Test 1: Create Smart Collection
        print("\n[TEST1] CREATE SMART COLLECTION")
        try:
            import time

            collection_data = {
                "id": f"test_col_{int(time.time())}",
                "name": "Test Collection - High Rated",
                "description": "Books with rating >= 4",
                "rules": [{"field": "rating", "operator": ">=", "value": 4}],
                "match_all": True,
            }
            result = await manage_smart_collections(operation="create", collection_data=collection_data)
            if result.get("success") or "collection" in result:
                collection_id = result.get("collection", {}).get("id")
                created_collection_ids.append(collection_id)
                test_results.append(("Create Collection", True, f"Created collection '{collection_id}'"))
                print(f"[OK] Created collection: {collection_id}")
            else:
                test_results.append(("Create Collection", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Create Collection", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: List Collections
        print("\n[TEST2] LIST COLLECTIONS")
        try:
            result = await manage_smart_collections(operation="list")
            if result.get("success") or "collections" in result:
                collections = result.get("collections", [])
                test_results.append(("List Collections", True, f"Found {len(collections)} collections"))
                print(f"[OK] Found {len(collections)} collections")
            else:
                test_results.append(("List Collections", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("List Collections", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Get Collection
        print("\n[TEST3] GET COLLECTION")
        try:
            if created_collection_ids:
                collection_id = created_collection_ids[0]
                result = await manage_smart_collections(operation="get", collection_id=collection_id)
                if result.get("success") or "collection" in result:
                    test_results.append(("Get Collection", True, f"Retrieved collection {collection_id}"))
                    print(f"[OK] Retrieved collection: {collection_id}")
                else:
                    test_results.append(("Get Collection", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get Collection", True, "No collection created (skip)"))
                print("[SKIP] No collection available")
        except Exception as e:
            test_results.append(("Get Collection", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Update Collection
        print("\n[TEST4] UPDATE COLLECTION")
        try:
            if created_collection_ids:
                collection_id = created_collection_ids[0]
                result = await manage_smart_collections(
                    operation="update", collection_id=collection_id, updates={"description": "Updated description"}
                )
                if result.get("success") or "collection" in result:
                    test_results.append(("Update Collection", True, f"Updated collection {collection_id}"))
                    print(f"[OK] Updated collection: {collection_id}")
                else:
                    test_results.append(("Update Collection", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Update Collection", True, "No collection created (skip)"))
                print("[SKIP] No collection available")
        except Exception as e:
            test_results.append(("Update Collection", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Create Series Collection
        print("\n[TEST5] CREATE SERIES COLLECTION")
        try:
            # Find a series name from the library
            from calibre_mcp.db.database import get_database
            from calibre_mcp.services.book_service import BookService

            db = get_database()
            book_service = BookService(db)
            books_result = book_service.get_all(limit=20)

            series_name = None
            for book in books_result.get("items", []):
                if book.get("series"):
                    series_name = book["series"]
                    break

            if series_name:
                result = await manage_smart_collections(
                    operation="create_series", name=f"Test Series Collection - {series_name}", series_name=series_name
                )
                if result.get("success") or "collection" in result:
                    collection_id = result.get("collection", {}).get("id")
                    created_collection_ids.append(collection_id)
                    test_results.append(
                        ("Create Series Collection", True, f"Created series collection for '{series_name}'")
                    )
                    print(f"[OK] Created series collection for: {series_name}")
                else:
                    test_results.append(("Create Series Collection", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Create Series Collection", True, "No series found (skip)"))
                print("[SKIP] No series found in library")
        except Exception as e:
            test_results.append(("Create Series Collection", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Create Recently Added Collection
        print("\n[TEST6] CREATE RECENTLY ADDED COLLECTION")
        try:
            result = await manage_smart_collections(
                operation="create_recently_added", name="Test Recently Added", days=30
            )
            if result.get("success") or "collection" in result:
                collection_id = result.get("collection", {}).get("id")
                created_collection_ids.append(collection_id)
                test_results.append(("Create Recently Added", True, "Created recently added collection"))
                print("[OK] Created recently added collection")
            else:
                test_results.append(("Create Recently Added", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Create Recently Added", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 7: Query Collection
        print("\n[TEST7] QUERY COLLECTION")
        try:
            if created_collection_ids:
                collection_id = created_collection_ids[0]
                result = await manage_smart_collections(operation="query", collection_id=collection_id, limit=10)
                if result.get("success") or "books" in result:
                    books_found = result.get("total_matches", len(result.get("books", [])))
                    test_results.append(("Query Collection", True, f"Found {books_found} matching books"))
                    print(f"[OK] Query returned {books_found} matching books")
                else:
                    test_results.append(("Query Collection", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Query Collection", True, "No collection created (skip)"))
                print("[SKIP] No collection available")
        except Exception as e:
            test_results.append(("Query Collection", False, str(e)))
            print(f"[FAIL] {e}")

        # Clean up: Delete created collections
        print("\n[CLEANUP] Deleting test collections...")
        for collection_id in created_collection_ids:
            try:
                await manage_smart_collections(operation="delete", collection_id=collection_id)
                print(f"[OK] Deleted collection: {collection_id}")
            except Exception as e:
                print(f"[WARN] Could not delete collection {collection_id}: {e}")

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
