"""
Help Tool

This module provides a help system for the Calibre MCP server,
offering documentation and usage examples for all available tools.
"""
import logging
from typing import Dict, Any, List, Optional, Union

from fastmcp import MCPServerError

# Import the tool decorator from the parent package
from .. import tool

logger = logging.getLogger("calibremcp.tools.help")

# Help documentation
HELP_DOCS = {
    "overview": {
        "title": "Calibre MCP Server Help",
        "description": (
            "The Calibre MCP Server provides a programmatic interface to manage your "
            "Calibre library. It allows you to add, search, and manage ebooks through "
            "a simple API."
        ),
        "sections": [
            {
                "title": "Getting Started",
                "content": (
                    "1. Use the `list_books` tool to see what's in your library.\n"
                    "2. Add new books with the `add_book` tool.\n"
                    "3. Search and filter books using the `list_books` parameters."
                )
            },
            {
                "title": "Available Tools",
                "content": (
                    "- `add_book`: Add a new book to the library\n"
                    "- `list_books`: Search and list books in the library\n"
                    "- `get_book`: Get details for a specific book\n"
                    "- `update_book`: Update book metadata\n"
                    "- `delete_book`: Remove a book from the library"
                )
            }
        ]
    },
    "add_book": {
        "title": "Add Book Tool",
        "description": "Add a new book to the Calibre library from a file or URL.",
        "usage": {
            "basic": "add_book(file_path=\"/path/to/book.epub\")",
            "with_metadata": """add_book(
    file_path="/path/to/book.epub",
    metadata={
        "title": "The Great Gatsby",
        "authors": ["F. Scott Fitzgerald"],
        "tags": ["classic", "fiction"]
    },
    fetch_metadata=True
)"""
        },
        "parameters": [
            {
                "name": "file_path",
                "type": "string",
                "required": True,
                "description": "Path to the book file to add"
            },
            {
                "name": "metadata",
                "type": "object",
                "required": False,
                "description": "Optional metadata to override extracted metadata"
            },
            {
                "name": "fetch_metadata",
                "type": "boolean",
                "default": True,
                "description": "Whether to fetch metadata from online sources"
            },
            {
                "name": "convert_to",
                "type": "string",
                "required": False,
                "description": "Convert the book to this format before adding"
            }
        ]
    },
    "list_books": {
        "title": "List Books Tool",
        "description": "Search and list books in the library with filtering and pagination.",
        "usage": {
            "basic": "list_books()",
            "with_filters": """list_books(
    query="science fiction",
    author="Asimov",
    tag="sci-fi",
    format="epub",
    limit=10,
    offset=0
)"""
        },
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "default": "",
                "description": "Search query string"
            },
            {
                "name": "author",
                "type": "string",
                "default": "",
                "description": "Filter by author"
            },
            {
                "name": "tag",
                "type": "string",
                "default": "",
                "description": "Filter by tag"
            },
            {
                "name": "format",
                "type": "string",
                "default": "",
                "description": "Filter by book format"
            },
            {
                "name": "status",
                "type": "string",
                "default": "",
                "description": "Filter by reading status"
            },
            {
                "name": "limit",
                "type": "integer",
                "default": 50,
                "description": "Maximum number of results to return"
            },
            {
                "name": "offset",
                "type": "integer",
                "default": 0,
                "description": "Offset for pagination"
            },
            {
                "name": "sort_by",
                "type": "string",
                "default": "title",
                "description": "Field to sort by (title, author, date_added, pubdate, rating)"
            },
            {
                "name": "sort_order",
                "type": "string",
                "default": "asc",
                "description": "Sort order (asc or desc)"
            }
        ]
    },
    "get_book": {
        "title": "Get Book Tool",
        "description": "Get detailed information about a specific book.",
        "usage": {
            "basic": "get_book(book_id=\"12345678\")",
            "with_format": "get_book(book_id=\"12345678\", format=\"epub\")"
        },
        "parameters": [
            {
                "name": "book_id",
                "type": "string",
                "required": True,
                "description": "ID of the book to retrieve"
            },
            {
                "name": "format",
                "type": "string",
                "required": False,
                "description": "Specific format to retrieve (if available)"
            }
        ]
    }
}
