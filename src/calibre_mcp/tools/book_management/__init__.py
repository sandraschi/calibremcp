"""
Book Management Tools

This package contains tools for managing books in the Calibre library.
"""

# Import portmanteau tools (these auto-register with @mcp.tool() decorator)
# Import helpers (NOT registered as MCP tools - used internally)
from .add_book import add_book_helper  # noqa: F401 - Helper for manage_books
from .delete_book import delete_book_helper  # noqa: F401 - Helper for manage_books
from .get_book import get_book_helper  # noqa: F401 - Helper for manage_books
from .manage_books import manage_books  # Portmanteau tool for add/get/update/delete
from .query_books import query_books  # Portmanteau tool for search/list/by_author/by_series
from .update_book import update_book_helper  # noqa: F401 - Helper for manage_books

__all__ = [
    "manage_books",  # Portmanteau tool (visible to Claude)
    "query_books",  # Portmanteau tool (visible to Claude)
]

# Re-export models for convenience
from ...models import Book, BookFormat, BookStatus  # noqa: E402, F401
