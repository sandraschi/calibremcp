#!/usr/bin/env python3
"""
Simple test to check if Calibre MCP server can be imported and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("Testing Calibre MCP imports...")

try:
    # Test 1: Basic imports
    print("1. Testing basic imports...")
    from calibre_mcp import mcp
    from calibre_mcp.server import CalibreConfig
    from calibre_mcp.calibre_api import CalibreAPIClient
    print("   ✓ Basic imports successful")

    # Test 2: MCP instance
    print("2. Testing MCP instance...")
    assert mcp is not None, "MCP instance is None"
    assert hasattr(mcp, "tool"), "MCP missing tool decorator"
    print("   ✓ MCP instance valid")

    # Test 3: Config
    print("3. Testing config...")
    config = CalibreConfig()
    assert hasattr(config, "server_url"), "Config missing server_url"
    print(f"   ✓ Config loaded (library: {config.library_name})")

    # Test 4: Database imports
    print("4. Testing database imports...")
    from calibre_mcp.db.database import init_database, get_database
    print("   ✓ Database imports successful")

    # Test 5: Tool imports
    print("5. Testing tool imports...")
    from calibre_mcp.tools import register_tools
    print("   ✓ Tool imports successful")

    # Test 6: Service imports
    print("6. Testing service imports...")
    from calibre_mcp.services.book_service import BookService
    print("   ✓ Service imports successful")

    print("\n🎉 ALL TESTS PASSED!")
    print("Calibre MCP server basic functionality is working.")

except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    sys.exit(1)
except AssertionError as e:
    print(f"❌ ASSERTION ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)