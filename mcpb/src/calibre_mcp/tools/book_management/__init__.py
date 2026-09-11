"""
Book Management Tools

This package contains tools for managing books in the Calibre library.
"""

# Import portmanteau tools (these auto-register with @mcp.tool() decorator)
# Import helpers (NOT registered as MCP tools - used internally)
from ...models import Book, BookFormat, BookStatus
from .add_book import add_book_helper
from .delete_book import delete_book_helper
from .fulltext_search import search_fulltext
from .get_book import get_book_helper
from .manage_books import manage_books
from .query_books import query_books
from .update_book import update_book_helper

__all__ = [
    "add_book_helper",
    "Book",
    "BookFormat",
    "BookStatus",
    "delete_book_helper",
    "get_book_helper",
    "manage_books",
    "query_books",
    "search_fulltext",
    "update_book_helper",
]
