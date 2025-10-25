"""
Core tools initialization.

This module registers all core library operation tools with the MCP server.
"""

from .library_operations import (
    list_books,
    get_book_details,
    search_books,
    test_calibre_connection
)

# List of tools to register
tools = [
    list_books,
    get_book_details,
    search_books,
    test_calibre_connection
]
