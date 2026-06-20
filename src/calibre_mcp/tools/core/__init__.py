"""
Core tools initialization.

This module registers all core library operation tools with the MCP server.
"""

from .library_operations import (
    get_book_details_helper,
    list_books_helper,
    test_calibre_connection_helper,
)

# test_connection merged into manage_libraries(operation="test_connection")
# Core module not loaded by default - manage_libraries provides consolidated interface

__all__ = [
    "get_book_details_helper",
    "list_books_helper",
    "test_calibre_connection_helper",
]

tools: list = []
