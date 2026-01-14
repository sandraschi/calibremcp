#!/usr/bin/env python3
"""
Quick test to verify basic Calibre MCP functionality works.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    print("Testing imports...")

    # Test basic imports
    from calibre_mcp import mcp, CalibreConfig, CalibreAPIClient
    print("✓ Basic imports successful")

    # Test MCP instance
    assert mcp is not None, "MCP instance is None"
    assert hasattr(mcp, "tool"), "MCP should have tool decorator"
    print("✓ MCP instance valid")

    # Test config
    config = CalibreConfig()
    print(f"✓ Config loaded: {config.library_name}")

    # Test tool registration
    from calibre_mcp.tools import register_tools
    print("✓ Tool registration import successful")

    # Test database imports
    from calibre_mcp.db.database import init_database, get_database
    print("✓ Database imports successful")

    # Test service imports
    from calibre_mcp.services.book_service import BookService
    print("✓ Service imports successful")

    print("\n🎉 All basic functionality tests passed!")
    print("The Calibre MCP server appears to be working correctly.")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)