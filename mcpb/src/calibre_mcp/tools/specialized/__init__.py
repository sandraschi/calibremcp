"""
Specialized tools for CalibreMCP.

NOTE: Only portmanteau tools are registered with @mcp.tool() and visible to Claude.
Helper functions are imported but NOT registered (they have no @mcp.tool() decorator).
"""

# Import portmanteau tool (this is registered with @mcp.tool() and visible to Claude)
from .manage_specialized import manage_specialized  # noqa: F401

# Helper functions are imported but NOT registered (they have no @mcp.tool() decorator)
from .specialized_tools import (
    japanese_book_organizer_helper,  # noqa: F401
    it_book_curator_helper,  # noqa: F401
    reading_recommendations_helper,  # noqa: F401
)

# List of tools to register (only @mcp.tool() decorated functions)
# Note: With FastMCP 2.13+, tools with @mcp.tool() auto-register on import
# This list is kept for backward compatibility and explicit registration if needed
tools = [
    manage_specialized,  # Portmanteau tool - registered with @mcp.tool()
    # Helper functions are NOT in this list (they have no @mcp.tool() decorator)
]

__all__ = [
    "manage_specialized",  # Portmanteau tool - registered with @mcp.tool()
    # Helper functions are NOT in this list (they have no @mcp.tool() decorator)
]
