"""
List Books Tool

This module provides functionality to list and search books in the Calibre library.
"""

import logging
from typing import Dict, Any, Optional

from fastmcp import MCPServerError
from ...models import BookFormat, BookStatus

# Import the tool decorator from the parent package
from .. import tool

logger = logging.getLogger("calibremcp.tools.library_operations")


@tool(
    name="list_books",
    description="List books in the library with optional filtering and pagination",
    parameters={
        "query": {"type": "string", "description": "Search query string", "default": ""},
        "author": {"type": "string", "description": "Filter by author", "default": ""},
        "tag": {"type": "string", "description": "Filter by tag", "default": ""},
        "format": {
            "type": "string",
            "description": "Filter by format",
            "enum": [fmt.value for fmt in BookFormat],
            "default": "",
        },
        "status": {
            "type": "string",
            "description": "Filter by reading status",
            "enum": [s.value for s in BookStatus],
            "default": "",
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of results to return",
            "minimum": 1,
            "maximum": 1000,
            "default": 50,
        },
        "offset": {
            "type": "integer",
            "description": "Offset for pagination",
            "minimum": 0,
            "default": 0,
        },
        "sort_by": {
            "type": "string",
            "description": "Field to sort by",
            "enum": ["title", "author", "date_added", "pubdate", "rating"],
            "default": "title",
        },
        "sort_order": {
            "type": "string",
            "description": "Sort order",
            "enum": ["asc", "desc"],
            "default": "asc",
        },
    },
)
async def list_books(
    query: str = "",
    author: str = "",
    tag: str = "",
    format: str = "",
    status: str = "",
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "title",
    sort_order: str = "asc",
    library_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List books in the library with optional filtering and pagination.

    Args:
        query: Search query string
        author: Filter by author
        tag: Filter by tag
        format: Filter by format
        status: Filter by reading status
        limit: Maximum number of results to return
        offset: Offset for pagination
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        library_path: Path to the Calibre library

    Returns:
        Dictionary containing the list of books and pagination info

    Raises:
        MCPServerError: If there's an error listing books
    """
    try:
        # In a real implementation, this would query a database
        # For now, we'll return a mock response

        # Mock data - in a real implementation, this would come from a database
        mock_books = [
            {
                "id": "a1b2c3d4",
                "title": "Example Book 1",
                "authors": ["Author One", "Author Two"],
                "formats": ["epub", "pdf"],
                "tags": ["fiction", "sci-fi"],
                "rating": 4.5,
                "publisher": "Example Publisher",
                "pubdate": "2023-01-01",
                "size": 1024000,
                "description": "This is an example book description.",
                "series": "Example Series",
                "series_index": 1,
                "languages": ["en"],
                "status": "unread",
                "progress": 0.0,
                "date_added": "2023-01-01T00:00:00",
                "cover_url": "/covers/a1b2c3d4",
            },
            # Add more mock books as needed
        ]

        # Apply filters (in a real implementation, this would be done in the database query)
        filtered_books = []
        for book in mock_books:
            # Apply query filter
            if query and query.lower() not in book["title"].lower():
                continue

            # Apply author filter
            if author and not any(author.lower() in a.lower() for a in book["authors"]):
                continue

            # Apply tag filter
            if tag and tag.lower() not in [t.lower() for t in book["tags"]]:
                continue

            # Apply format filter
            if format and format.lower() not in book["formats"]:
                continue

            # Apply status filter
            if status and status.lower() != book["status"].lower():
                continue

            filtered_books.append(book)

        # Apply sorting (in a real implementation, this would be done in the database query)
        reverse_sort = sort_order.lower() == "desc"

        def get_sort_key(book):
            if sort_by == "title":
                return book["title"].lower()
            elif sort_by == "author":
                return book["authors"][0].lower() if book["authors"] else ""
            elif sort_by == "date_added":
                return book.get("date_added", "")
            elif sort_by == "pubdate":
                return book.get("pubdate", "")
            elif sort_by == "rating":
                return book.get("rating", 0)
            return ""

        filtered_books.sort(key=get_sort_key, reverse=reverse_sort)

        # Apply pagination
        total_books = len(filtered_books)
        paginated_books = filtered_books[offset : offset + limit]

        return {
            "books": paginated_books,
            "total_count": total_books,
            "offset": offset,
            "limit": limit,
            "has_more": (offset + len(paginated_books)) < total_books,
        }

    except Exception as e:
        logger.error(f"Error listing books: {e}", exc_info=True)
        raise MCPServerError(f"Failed to list books: {str(e)}")
