#!/usr/bin/env python3
"""
Test Battery for manage_system Portmanteau Tool

Tests all operations: help, status, tool_help, list_tools, hello_world, health_check
Run with: python tests/portmanteau/test_manage_system.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_system portmanteau."""

    print("MANAGE_SYSTEM PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: help, status, tool_help, list_tools, hello_world, health_check")
    print("=" * 60)

    test_results = []

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_system tool...")
        from calibre_mcp.tools.system.manage_system import manage_system

        print("[OK] Tool imported successfully")

        # Test 1: Hello World
        print("\n[TEST1] HELLO WORLD")
        try:
            result = await manage_system(operation="hello_world")
            if result or isinstance(result, str):
                test_results.append(("Hello World", True, "Hello world test passed"))
                print(f"[OK] Hello world: {result[:100] if isinstance(result, str) else 'OK'}")
            else:
                test_results.append(("Hello World", False, "No response"))
                print("[FAIL] No response")
        except Exception as e:
            test_results.append(("Hello World", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: List Tools
        print("\n[TEST2] LIST TOOLS")
        try:
            result = await manage_system(operation="list_tools")
            if result.get("success") or "tools" in result:
                tools_count = len(result.get("tools", []))
                test_results.append(("List Tools", True, f"Found {tools_count} tools"))
                print(f"[OK] Found {tools_count} tools")
            else:
                test_results.append(("List Tools", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("List Tools", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Get Help
        print("\n[TEST3] GET HELP")
        try:
            result = await manage_system(operation="help", level="basic")
            if result or isinstance(result, str):
                test_results.append(("Get Help", True, "Help retrieved"))
                print(f"[OK] Help retrieved ({len(result) if isinstance(result, str) else 'OK'} chars)")
            else:
                test_results.append(("Get Help", False, "No help content"))
                print("[FAIL] No help content")
        except Exception as e:
            test_results.append(("Get Help", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 4: Get Tool Help
        print("\n[TEST4] GET TOOL HELP")
        try:
            result = await manage_system(operation="tool_help", tool_name="manage_books", tool_help_level="basic")
            if result or isinstance(result, str):
                test_results.append(("Tool Help", True, "Tool help retrieved"))
                print(f"[OK] Tool help retrieved ({len(result) if isinstance(result, str) else 'OK'} chars)")
            else:
                test_results.append(("Tool Help", False, "No tool help"))
                print("[FAIL] No tool help")
        except Exception as e:
            test_results.append(("Tool Help", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 5: Health Check
        print("\n[TEST5] HEALTH CHECK")
        try:
            result = await manage_system(operation="health_check")
            if result.get("success") or "status" in result:
                status = result.get("status", "unknown")
                test_results.append(("Health Check", True, f"Health status: {status}"))
                print(f"[OK] Health check: {status}")
            else:
                test_results.append(("Health Check", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Health Check", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 6: Get Status
        print("\n[TEST6] GET STATUS")
        try:
            result = await manage_system(operation="status", status_level="basic")
            if result or isinstance(result, str):
                test_results.append(("Get Status", True, "Status retrieved"))
                print(f"[OK] Status retrieved ({len(result) if isinstance(result, str) else 'OK'} chars)")
            else:
                test_results.append(("Get Status", False, "No status"))
                print("[FAIL] No status")
        except Exception as e:
            test_results.append(("Get Status", False, str(e)))
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
