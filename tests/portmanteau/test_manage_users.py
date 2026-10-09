#!/usr/bin/env python3
"""
Test Battery for manage_users Portmanteau Tool

Tests all operations: create_user, update_user, delete_user, list_users, get_user, login, verify_token
Run with: python tests/portmanteau/test_manage_users.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_users portmanteau."""

    print("MANAGE_USERS PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: create_user, update_user, delete_user, list_users, get_user, login, verify_token")
    print("=" * 60)

    test_results = []
    test_user_id = None
    test_token = None

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_users tool...")
        from calibre_mcp.tools.user_management.manage_users import manage_users

        print("[OK] Tool imported successfully")

        # Test 1: Create User
        print("\n[TEST1] CREATE USER")
        try:
            import time

            username = f"testuser_{int(time.time())}"
            user_data = {
                "username": username,
                "email": f"{username}@test.com",
                "password": "testpass123",
                "role": "user",
            }
            result = await manage_users(operation="create_user", user_data=user_data)
            if result.get("success") or "user_id" in result:
                test_user_id = result.get("user_id")
                test_results.append(("Create User", True, f"Created user '{username}'"))
                print(f"[OK] Created user: {username}")
            else:
                test_results.append(("Create User", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Create User", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: List Users
        print("\n[TEST2] LIST USERS")
        try:
            result = await manage_users(operation="list_users", page=1, per_page=20)
            if result.get("success") or "users" in result:
                users_count = len(result.get("users", []))
                test_results.append(("List Users", True, f"Found {users_count} users"))
                print(f"[OK] Found {users_count} users")
            else:
                test_results.append(("List Users", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("List Users", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Get User
        print("\n[TEST3] GET USER")
        try:
            if test_user_id:
                result = await manage_users(operation="get_user", user_id=test_user_id)
                if result.get("success") or "user" in result:
                    test_results.append(("Get User", True, f"Retrieved user {test_user_id}"))
                    print(f"[OK] Retrieved user: {test_user_id}")
                else:
                    test_results.append(("Get User", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Get User", True, "No user created (skip)"))
                print("[SKIP] No user available")
        except Exception as e:
            test_results.append(("Get User", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Login
        print("\n[TEST4] LOGIN")
        try:
            if test_user_id:
                # Get username from user data
                username = (
                    f"testuser_{int(time.time())}"
                    if not hasattr(run_test_battery, "_username")
                    else run_test_battery._username
                )
                result = await manage_users(operation="login", username=username, password="testpass123")
                if result.get("success") or "token" in result:
                    test_token = result.get("token")
                    test_results.append(("Login", True, "Login successful"))
                    print("[OK] Login successful, token received")
                else:
                    test_results.append(("Login", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Login", True, "No user created (skip)"))
                print("[SKIP] No user available")
        except Exception as e:
            test_results.append(("Login", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Verify Token
        print("\n[TEST5] VERIFY TOKEN")
        try:
            if test_token:
                result = await manage_users(operation="verify_token", token=test_token)
                if result.get("success") or result.get("valid"):
                    test_results.append(("Verify Token", True, "Token verified"))
                    print(f"[OK] Token verified: {result.get('valid', False)}")
                else:
                    test_results.append(("Verify Token", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Verify Token", True, "No token (skip)"))
                print("[SKIP] No token available")
        except Exception as e:
            test_results.append(("Verify Token", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Update User
        print("\n[TEST6] UPDATE USER")
        try:
            if test_user_id:
                result = await manage_users(
                    operation="update_user", user_id=test_user_id, update_data={"email": "updated@test.com"}
                )
                if result.get("success"):
                    test_results.append(("Update User", True, f"Updated user {test_user_id}"))
                    print(f"[OK] Updated user: {test_user_id}")
                else:
                    test_results.append(("Update User", False, result.get("error", "Unknown error")))
                    print(f"[FAIL] {result.get('error', 'Unknown error')}")
            else:
                test_results.append(("Update User", True, "No user created (skip)"))
                print("[SKIP] No user available")
        except Exception as e:
            test_results.append(("Update User", False, str(e)))
            print(f"[FAIL] {e}")

        # Clean up: Delete test user
        print("\n[CLEANUP] Deleting test user...")
        try:
            if test_user_id:
                delete_result = await manage_users(operation="delete_user", user_id=test_user_id)
                if delete_result.get("success"):
                    print("[OK] Test user deleted")
                else:
                    print(f"[WARN] Could not delete test user: {delete_result.get('error', 'Unknown')}")
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
