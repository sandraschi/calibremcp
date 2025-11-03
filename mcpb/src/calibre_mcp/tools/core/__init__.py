"""
Core tools initialization.

This module registers all core library operation tools with the MCP server.
"""

from .library_operations import (
    list_books_helper,  # noqa: F401
    get_book_details,
    test_calibre_connection,
)
# list_books_helper is a helper function (NOT registered - used by query_books portmanteau)

# List of tools to register (only @mcp.tool() decorated functions)
tools = [
    get_book_details,  # Registered with @mcp.tool()
    test_calibre_connection,  # Registered with @mcp.tool()
    # list_books_helper is NOT registered (it's a helper)
]
