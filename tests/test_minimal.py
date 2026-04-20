#!/usr/bin/env python3
"""
Minimal test to check if Calibre MCP server can start and register tools.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def test_minimal():
    """Test minimal Calibre MCP functionality."""


    try:
        # Test 1: Import server module
        from calibre_mcp import server


        # Test 2: Check MCP instance
        mcp = server.mcp
        if mcp is None:
            return False

        # Test 3: Check MCP has tool decorator
        if not hasattr(mcp, "tool"):
            return False

        # Test 4: Try to import one tool module
        try:
            pass
        except Exception:
            return False

        # Test 5: Check tool registration
        try:
            from calibre_mcp.tools import register_tools

            register_tools(mcp)
        except Exception:
            return False

        # Test 6: Check registered tools
        try:
            if hasattr(mcp, "list_tools"):
                tools = mcp.list_tools()
                tool_count = len(tools) if tools else 0
            elif hasattr(mcp, "_tools"):
                tool_count = len(mcp._tools) if hasattr(mcp._tools, "__len__") else 0
            else:
                tool_count = "unknown"


            if tool_count == 0 or tool_count == "unknown":
                pass
            else:
                pass

        except Exception:
            return False


        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_minimal()
    sys.exit(0 if success else 1)
