"""
Book query portmanteau tool for CalibreMCP.

Consolidates search_books, list_books, get_books_by_author, get_books_by_series
into a single portmanteau tool with operation parameter.
"""

from typing import Optional, Dict, Any, List

from ...server import mcp
from ...logging_config import get_logger

# Import helper functions (NOT registered as MCP tools)
from ..book_tools import search_books_helper as _search_books_helper
from ..core.library_operations import list_books_helper as _list_books_helper
from ..book_tools import get_books_by_author_helper as _get_books_by_author_helper
from ..book_tools import get_books_by_series_helper as _get_books_by_series_helper

logger = get_logger("calibremcp.tools.book_management")


@mcp.tool()
async def query_books(
    operation: str,
    # Search parameters (all passed through to search_books_helper)
    author: Optional[str] = None,
    authors: Optional[List[str]] = None,
    exclude_authors: Optional[List[str]] = None,
    author_id: Optional[int] = None,
    series_id: Optional[int] = None,
    series: Optional[str] = None,
    exclude_series: Optional[List[str]] = None,
    text: Optional[str] = None,
    query: Optional[str] = None,
    tag: Optional[str] = None,
    tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    publisher: Optional[str] = None,
    publishers: Optional[List[str]] = None,
    has_publisher: Optional[bool] = None,
    rating: Optional[int] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    unrated: Optional[bool] = None,
    pubdate_start: Optional[str] = None,
    pubdate_end: Optional[str] = None,
    added_after: Optional[str] = None,
    added_before: Optional[str] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    formats: Optional[List[str]] = None,
    comment: Optional[str] = None,
    has_empty_comments: Optional[bool] = None,
    # Display/formatting
    format_table: bool = False,
    limit: int = 50,
    offset: int = 0,
    **kwargs,
) -> Dict[str, Any]:
    """
    Query and search books in the Calibre library with multiple operations in a single unified interface.

    This portmanteau tool consolidates all book query operations (searching, listing,
    filtering by author/series) into a single interface. Use the `operation` parameter
    to select which operation to perform.

    **IMPORTANT FOR CLAUDE:** When user says "list books by [author name]", use:
    - operation="search" with author="[author name]" parameter
    - Example: "list books by conan doyle" → query_books(operation="search", author="Conan Doyle")
    - This searches the currently loaded library (auto-loaded on startup)

    Operations:
    - search: Search books with flexible filters (author, tag, text, etc.)
              **Use this for "list books by [author]" queries - just set author parameter**
    - list: List all books in the library with optional filters
    - by_author: Get books by a specific author (requires author_id)
    - by_series: Get books in a specific series (requires series_id)

    Prerequisites:
        - **Default library is auto-loaded on server startup** - no manual library loading needed!
        - For 'search': At least one filter parameter recommended (author, text, tag, etc.)
        - For 'by_author': author_id required (integer)
        - For 'by_series': series_id required (integer)
        - Library must be accessible (automatically handled on startup)

    Parameters:
        operation: The operation to perform. Must be one of: "search", "list", "by_author", "by_series"
            - "search": Search books with flexible filters. Most parameters apply.
            - "list": List all books with basic filters. Supports author, tag, limit, offset.
            - "by_author": Get books by author_id. Requires author_id parameter.
            - "by_series": Get books by series_id. Requires series_id parameter.

        author: Filter by author name (for 'search' and 'list' operations)
            - Case-insensitive partial match
            - Example: "Conan Doyle" or "conan"

        author_id: Author ID for 'by_author' operation (required for 'by_author')
            - Must be an integer
            - Use search_books to find author IDs

        series_id: Series ID for 'by_series' operation (required for 'by_series')
            - Must be an integer
            - Use search_books to find series IDs

        text: Search text for 'search' operation
            - Searches in title, author, tags, series, comments
            - Example: "python programming"

        query: Alias for text parameter (backward compatibility)

        tag: Filter by tag name (for 'search' and 'list')
            - Example: "mystery"

        tags: Filter by multiple tags (for 'search')
            - Example: ["mystery", "crime"]

        series: Filter by series name (for 'search')
            - Example: "Sherlock Holmes"

        rating: Filter by exact rating (for 'search')
            - Integer 1-5

        min_rating: Filter by minimum rating (for 'search')
            - Integer 1-5

        format_table: Format results as table (for 'search')
            - Boolean, default: False

        limit: Maximum results to return (default: 50)

        offset: Results offset for pagination (default: 0)

    Returns:
        Dictionary containing operation-specific results with book list and pagination info.

    Usage:
        # Search for books by author (what Claude will use for "list books by conan doyle")
        # This works immediately - default library is auto-loaded on server startup
        result = await query_books(
            operation="search",
            author="Conan Doyle"
        )
        print(f"Found {result['total']} books")

        # No need to load/switch libraries first - default library is already loaded!

        # List all books
        result = await query_books(operation="list", limit=20)

        # Get books by author ID
        result = await query_books(
            operation="by_author",
            author_id=42
        )

    Examples:
        # Claude says: "list books by conan doyle"
        result = await query_books(
            operation="search",
            author="Conan Doyle",
            format_table=True
        )

        # Search by multiple authors
        result = await query_books(
            operation="search",
            authors=["Shakespeare", "Homer"]
        )

        # List recent books
        result = await query_books(
            operation="list",
            limit=10
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "search", "list", "by_author", "by_series"
        - Missing author_id: Provide author_id for 'by_author' operation
        - Missing series_id: Provide series_id for 'by_series' operation

    See Also:
        - manage_books(): For adding, updating, deleting books
        - Helper functions: search_books, list_books (NOT visible to Claude, used internally)
    """
    if operation == "search":
        # Use search_books helper - pass ALL search parameters
        return await _search_books_helper(
            # Text/search
            text=text or query,
            query=None,  # Already handled via text
            # Authors
            author=author,
            authors=authors,
            exclude_authors=exclude_authors,
            # Series
            series=series,
            exclude_series=exclude_series,
            # Tags
            tag=tag,
            tags=tags,
            exclude_tags=exclude_tags,
            # Publisher
            publisher=publisher,
            publishers=publishers,
            has_publisher=has_publisher,
            # Rating
            rating=rating,
            min_rating=min_rating,
            max_rating=max_rating,
            unrated=unrated,
            # Dates
            pubdate_start=pubdate_start,
            pubdate_end=pubdate_end,
            added_after=added_after,
            added_before=added_before,
            # Size
            min_size=min_size,
            max_size=max_size,
            # Formats
            formats=formats,
            # Comments
            comment=comment,
            has_empty_comments=has_empty_comments,
            # Display/pagination
            format_table=format_table,
            limit=limit,
            offset=offset,
            **kwargs,  # Any other parameters (fields, operator, fuzziness, etc.)
        )

    elif operation == "list":
        # Use list_books helper (simplified parameters)
        return await _list_books_helper(
            query=author or tag or text or query,
            limit=limit,
        )

    elif operation == "by_author":
        if author_id is None:
            return {
                "success": False,
                "error": "author_id is required for operation='by_author'.",
                "suggestions": [
                    "First use query_books(operation='search', author='Author Name') to find the author_id",
                    "Then use query_books(operation='by_author', author_id=<id>)",
                ],
            }
        return await _get_books_by_author_helper(
            author_id=author_id,
            limit=limit,
            offset=offset,
        )

    elif operation == "by_series":
        if series_id is None:
            return {
                "success": False,
                "error": "series_id is required for operation='by_series'.",
                "suggestions": [
                    "First use query_books(operation='search', series='Series Name') to find the series_id",
                    "Then use query_books(operation='by_series', series_id=<id>)",
                ],
            }
        return await _get_books_by_series_helper(series_id=series_id)

    else:
        return {
            "success": False,
            "error": f"Invalid operation: '{operation}'. Must be one of: 'search', 'list', 'by_author', 'by_series'",
            "suggestions": [
                "Use operation='search' to search books with filters (author, tag, text, etc.)",
                "Use operation='list' to list all books",
                "Use operation='by_author' to get books by author_id",
                "Use operation='by_series' to get books by series_id",
            ],
        }
