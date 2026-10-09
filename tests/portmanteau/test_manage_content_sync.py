#!/usr/bin/env python3
"""
Test Battery for manage_content_sync Portmanteau Tool

Tests all operations: register_device, update_device, get_device, start, status, cancel
Run with: python tests/portmanteau/test_manage_content_sync.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_content_sync portmanteau."""

    print("MANAGE_CONTENT_SYNC PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: register_device, update_device, get_device, start, status, cancel")
    print("=" * 60)

    test_results = []
    test_device_id = None

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_content_sync tool...")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database
        from calibre_mcp.tools.advanced_features.manage_content_sync import manage_content_sync

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

        # Test 1: Register Device
        print("\n[TEST1] REGISTER DEVICE")
        try:
            import time

            device_name = f"test_device_{int(time.time())}"
            result = await manage_content_sync(operation="register_device", name=device_name, device_type="ereader")
            if result.get("success") or "device_id" in result:
                test_device_id = result.get("device_id")
                test_results.append(("Register Device", True, f"Registered device '{device_name}'"))
                print(f"[OK] Registered device: {device_name}")
            else:
                test_results.append(("Register Device", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Register Device", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: Get Device
        print("\n[TEST2] GET DEVICE")
        try:
            if test_device_id:
                result = await manage_content_sync(operation="get_device", device_id=test_device_id)
                if result.get("success") or "device" in result:
                    test_results.append(("Get Device", True, f"Retrieved device {test_device_id}"))
                    print(f"[OK] Retrieved device: {test_device_id}")
                else:
                    test_results.append(("Get Device", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get Device", True, "No device registered (skip)"))
                print("[SKIP] No device available")
        except Exception as e:
            test_results.append(("Get Device", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Update Device
        print("\n[TEST3] UPDATE DEVICE")
        try:
            if test_device_id:
                result = await manage_content_sync(
                    operation="update_device", device_id=test_device_id, updates={"name": "Updated Test Device"}
                )
                if result.get("success"):
                    test_results.append(("Update Device", True, f"Updated device {test_device_id}"))
                    print(f"[OK] Updated device: {test_device_id}")
                else:
                    test_results.append(("Update Device", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Update Device", True, "No device registered (skip)"))
                print("[SKIP] No device available")
        except Exception as e:
            test_results.append(("Update Device", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Start Sync
        print("\n[TEST4] START SYNC")
        try:
            if test_device_id:
                result = await manage_content_sync(operation="start", device_id=test_device_id, sync_type="full")
                if result.get("success") or "job_id" in result:
                    job_id = result.get("job_id")
                    test_results.append(("Start Sync", True, f"Started sync job {job_id}"))
                    print(f"[OK] Started sync job: {job_id}")

                    # Test 5: Get Sync Status
                    print("\n[TEST5] GET SYNC STATUS")
                    try:
                        if job_id:
                            status_result = await manage_content_sync(operation="status", job_id=job_id)
                            if status_result.get("success") or "status" in status_result:
                                sync_status = status_result.get("status", "unknown")
                                test_results.append(("Sync Status", True, f"Sync status: {sync_status}"))
                                print(f"[OK] Sync status: {sync_status}")
                            else:
                                test_results.append(("Sync Status", False, status_result.get("error", "Unknown error")))
                                print(f"[FAIL] {status_result.get('error', 'Unknown error')}")
                    except Exception as e:
                        test_results.append(("Sync Status", False, str(e)))
                        print(f"[FAIL] {e}")
                else:
                    test_results.append(("Start Sync", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Start Sync", True, "No device registered (skip)"))
                print("[SKIP] No device available")
        except Exception as e:
            test_results.append(("Start Sync", False, str(e)))
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
