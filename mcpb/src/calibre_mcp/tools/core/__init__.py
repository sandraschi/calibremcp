"""
Core tools initialization.

This module registers all core library operation tools with the MCP server.
"""

from .library_operations import (
    get_book_details_helper,  # noqa: F401 - Helper function (NOT registered)
    list_books_helper,  # noqa: F401
    test_calibre_connection,
)

# list_books_helper and get_book_details_helper are helper functions (NOT registered)
# get_book_details migrated to manage_books(operation="details")

# List of tools to register (only @mcp.tool() decorated functions)
tools = [
    test_calibre_connection,  # Registered with @mcp.tool() - diagnostic tool
    # get_book_details removed - use manage_books(operation="details") instead
]
