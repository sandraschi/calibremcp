"""
Library management tools initialization.

This module registers all library management tools with the MCP server.

NOTE: Only portmanteau tools are registered with @mcp.tool() and visible to Claude.
Legacy helper functions are available but NOT registered as MCP tools.
"""

# Import portmanteau tools (these are registered with @mcp.tool() and visible to Claude)
# library_discovery merged into manage_libraries(operation="discover")
# Import helper functions (NOT registered - used internally by portmanteau tool)
from .library_management import (
    cross_library_search_helper,
    get_library_stats_helper,
    list_libraries_helper,
    switch_library_helper,
)
from .manage_libraries import manage_libraries

tools = [manage_libraries]

__all__ = [
    "cross_library_search_helper",
    "get_library_stats_helper",
    "list_libraries_helper",
    "manage_libraries",
    "switch_library_helper",
]
