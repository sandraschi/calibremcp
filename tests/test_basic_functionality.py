#!/usr/bin/env python3
"""
Quick test to verify basic Calibre MCP functionality works.
"""

import sys
from pathlib import Path

# Add repo src when tests are run without an editable install
_repo_root = Path(__file__).resolve().parent.parent
_src = _repo_root / "src"
if _src.is_dir():
    sys.path.insert(0, str(_src))


def test_basic_calibre_mcp_imports():
    """MCP instance lives in server to avoid circular imports in package __init__."""
    from calibre_mcp import CalibreConfig
    from calibre_mcp.server import mcp

    assert mcp is not None, "MCP instance is None"
    assert hasattr(mcp, "tool"), "MCP should have tool decorator"
    CalibreConfig()
