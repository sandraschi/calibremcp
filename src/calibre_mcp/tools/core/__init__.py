"""
Core tools initialization.

This module registers all core library operation tools with the MCP server.
"""

from .library_operations import (
    list_books_helper,  # noqa: F401
    get_book_details_helper,  # noqa: F401
    test_calibre_connection_helper,  # noqa: F401
)
# test_connection merged into manage_libraries(operation="test_connection")
# Core module not loaded by default - manage_libraries provides consolidated interface

tools: list = []
