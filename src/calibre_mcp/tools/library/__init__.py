"""
Library management tools initialization.

This module registers all library management tools with the MCP server.
"""

from .library_management import (
    list_libraries,
    switch_library,
    get_library_stats,
    cross_library_search
)

# List of tools to register
tools = [
    list_libraries,
    switch_library,
    get_library_stats,
    cross_library_search
]
