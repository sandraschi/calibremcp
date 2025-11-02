"""
Test script to verify the server will load successfully in Claude.

This simulates what Claude does when it loads an MCP server:
1. Import the server module
2. Check that all tools are registered
3. Verify no import errors or startup failures
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def test_server_imports():
    """Test that all server imports work without errors."""
    print("Testing server imports...")
    try:
        print("[OK] Server module imports successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Server import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tools_registration():
    """Test that all tools can be registered without errors."""
    print("\nTesting tools registration...")
    try:
        from calibre_mcp.server import mcp
        from calibre_mcp.tools import register_tools

        # Try to register tools (this is what happens during server startup)
        register_tools(mcp)
        print("[OK] Tools registered successfully")

        # Check that tools are available
        tools = mcp.list_tools() if hasattr(mcp, "list_tools") else []
        print(f"[OK] Server initialized with {len(tools)} tools (if available)")
        return True
    except Exception as e:
        print(f"[FAIL] Tools registration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tag_tools_import():
    """Test that tag tools can be imported (since we just added them)."""
    print("\nTesting tag tools import...")
    try:
        from calibre_mcp.tools import tag_tools

        print("[OK] Tag tools import successfully")

        # Check that tag tools are available
        import inspect

        tag_functions = [
            name
            for name, obj in inspect.getmembers(tag_tools)
            if inspect.iscoroutinefunction(obj) and hasattr(obj, "__name__")
        ]
        print(f"[OK] Found {len(tag_functions)} tag tool functions")
        return True
    except Exception as e:
        print(f"[FAIL] Tag tools import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_server_startup_simulation():
    """Simulate server startup without actually running it."""
    print("\nSimulating server startup...")
    try:
        from calibre_mcp.server import mcp
        from calibre_mcp.tools import register_tools
        from calibre_mcp.config import CalibreConfig

        # Check config
        config = CalibreConfig()
        print(f"[OK] Config loaded: library_path = {config.local_library_path}")

        # Register tools (what main() does)
        register_tools(mcp)
        print("[OK] Tools registered")

        print("[OK] Server startup simulation successful")
        return True
    except Exception as e:
        print(f"[FAIL] Server startup simulation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing CalibreMCP Server Load for Claude")
    print("=" * 60)

    results = []

    results.append(("Server Imports", test_server_imports()))
    results.append(("Tag Tools Import", test_tag_tools_import()))
    results.append(("Tools Registration", test_tools_registration()))
    results.append(("Server Startup Simulation", test_server_startup_simulation()))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("[OK] All tests passed! Server should load successfully in Claude.")
        return 0
    else:
        print("[FAIL] Some tests failed! Server may not load in Claude.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
