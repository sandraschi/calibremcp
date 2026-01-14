#!/usr/bin/env python3
"""
Minimal test to check if Calibre MCP server can start and register tools.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_minimal():
    """Test minimal Calibre MCP functionality."""

    print("🔧 MINIMAL CALIBRE MCP TEST")
    print("=" * 30)

    try:
        # Test 1: Import server module
        print("\n📦 TEST 1: Server Module Import")
        from calibre_mcp import server
        print("✓ Server module imported")

        # Test 2: Check MCP instance
        print("\n🔧 TEST 2: MCP Instance")
        mcp = server.mcp
        if mcp is None:
            print("❌ MCP instance is None")
            return False
        print(f"✓ MCP instance created: {type(mcp)}")

        # Test 3: Check MCP has tool decorator
        print("\n🛠️  TEST 3: Tool Decorator")
        if not hasattr(mcp, 'tool'):
            print("❌ MCP missing tool decorator")
            return False
        print("✓ MCP has tool decorator")

        # Test 4: Try to import one tool module
        print("\n📚 TEST 4: Tool Import")
        try:
            from calibre_mcp.tools.library.manage_libraries import manage_libraries
            print("✓ Tool module imported")
        except Exception as e:
            print(f"❌ Tool import failed: {e}")
            return False

        # Test 5: Check tool registration
        print("\n📋 TEST 5: Tool Registration")
        try:
            from calibre_mcp.tools import register_tools
            register_tools(mcp)
            print("✓ Tool registration completed")
        except Exception as e:
            print(f"❌ Tool registration failed: {e}")
            return False

        # Test 6: Check registered tools
        print("\n📊 TEST 6: Tool Count")
        try:
            if hasattr(mcp, 'list_tools'):
                tools = mcp.list_tools()
                tool_count = len(tools) if tools else 0
            elif hasattr(mcp, '_tools'):
                tool_count = len(mcp._tools) if hasattr(mcp._tools, '__len__') else 0
            else:
                tool_count = "unknown"

            print(f"✓ Tools registered: {tool_count}")

            if tool_count == 0 or tool_count == "unknown":
                print("⚠️  Warning: No tools detected")
            else:
                print("✅ Tools are registered!")

        except Exception as e:
            print(f"❌ Tool count check failed: {e}")
            return False

        print("\n" + "=" * 30)
        print("🎉 MINIMAL TEST PASSED!")
        print("Calibre MCP server should work.")
        print("=" * 30)

        return True

    except Exception as e:
        print(f"\n💥 CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal()
    sys.exit(0 if success else 1)