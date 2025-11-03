"""
Library management tools initialization.

This module registers all library management tools with the MCP server.

NOTE: Only portmanteau tools are registered with @mcp.tool() and visible to Claude.
Legacy helper functions are available but NOT registered as MCP tools.
"""

# Import portmanteau tool (this is registered with @mcp.tool() and visible to Claude)
from .manage_libraries import manage_libraries

# Import helper functions (NOT registered - used internally by portmanteau tool)
# These are NOT visible to Claude, only used as helpers
from .library_management import (
    list_libraries_helper,  # noqa: F401
    switch_library_helper,  # noqa: F401
    get_library_stats_helper,  # noqa: F401
    cross_library_search_helper,  # noqa: F401
)

# List of tools to register - ONLY portmanteau tools are registered
# Helper functions are imported above but NOT in this list (they have no @mcp.tool() decorator)
tools = [
    manage_libraries,  # Portmanteau tool (ONLY ONE visible to Claude)
]
