#!/usr/bin/env python3
"""
Quick test to verify basic Calibre MCP functionality works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:

    # Test basic imports
    from calibre_mcp import CalibreConfig, mcp


    # Test MCP instance
    assert mcp is not None, "MCP instance is None"
    assert hasattr(mcp, "tool"), "MCP should have tool decorator"

    # Test config
    config = CalibreConfig()

    # Test tool registration

    # Test database imports

    # Test service imports


except Exception:
    import traceback

    traceback.print_exc()
    sys.exit(1)
