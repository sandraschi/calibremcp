"""
Viewer tools for CalibreMCP.

NOTE: Only portmanteau tools are registered with @mcp.tool() and visible to Claude.
Helper functions are imported but NOT registered (they have no @mcp.tool() decorator).
"""

# Import portmanteau tool (this is registered with @mcp.tool() and visible to Claude)
from .manage_viewer import manage_viewer  # noqa: F401

# Helper functions are imported but NOT registered (they have no @mcp.tool() decorator)
# (No helpers yet - viewer operations are directly in manage_viewer)

# List of tools to register (only @mcp.tool() decorated functions)
__all__ = [
    "manage_viewer",  # Portmanteau tool - registered with @mcp.tool()
    # Helper functions are NOT in this list (they have no @mcp.tool() decorator)
]

