"""
Author management portmanteau tool for CalibreMCP.

Consolidates all author-related operations into a single unified interface.
"""

from typing import Optional, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response

# Import helper functions (NOT registered as MCP tools)
from .author_helpers import (
    list_authors_helper,
    get_author_helper,
    get_author_books_helper,
    get_author_stats_helper,
    get_authors_by_letter_helper,
)

logger = get_logger("calibremcp.tools.authors")


@mcp.tool()
async def manage_authors(
    operation: str,
    # List operation parameters
    query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    # Get operation parameters
    author_id: Optional[int] = None,
    # Get books operation parameters
    # (uses author_id from above)
    # Stats operation parameters
    # (no parameters needed)
    # By letter operation parameters
    letter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Comprehensive author management tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 5 separate tools (one per operation), this tool consolidates related
    author operations into a single interface. This design:
    - Prevents tool explosion (5 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with author management tasks
    - Enables consistent author interface across all operations
    - Follows FastMCP 2.12+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - list: List authors with filtering and pagination
    - get: Get author details by ID
    - get_books: Get all books by a specific author
    - stats: Get statistics about authors in the library
    - by_letter: Get authors whose names start with a specific letter

    OPERATIONS DETAIL:

    list: List authors with filtering and pagination
    - Supports searching authors by name (case-insensitive partial match)
    - Pagination with limit and offset
    - Parameters: query (optional), limit (default: 50), offset (default: 0)

    get: Get author details by ID
    - Retrieve author information including book count
    - Returns author details or error if not found
    - Parameters: author_id (required)

    get_books: Get all books by a specific author
    - Results are paginated for efficient browsing of large collections
    - Returns author information and paginated list of books
    - Parameters: author_id (required), limit (default: 50), offset (default: 0)

    stats: Get author statistics
    - Comprehensive statistics about authors in the library
    - Includes total authors, top authors by book count, distribution by first letter
    - No parameters required

    by_letter: Get authors by first letter
    - Returns all authors whose names start with the specified letter
    - Case-insensitive (e.g., 'A' and 'a' are equivalent)
    - Parameters: letter (required, single alphabetic character)

    Prerequisites:
        - Library must be configured (use manage_libraries(operation='switch'))
        - For operations requiring author_id: Author must exist (use operation='list' to find IDs)

    Parameters:
        operation: The operation to perform. Must be one of:
            "list", "get", "get_books", "stats", "by_letter"

        # List operation parameters
        query: Search term to filter authors by name (case-insensitive partial match)
        limit: Maximum number of results (1-1000, default: 50)
        offset: Results offset for pagination (default: 0)

        # Get operation parameters
        author_id: Author ID (required for 'get' and 'get_books' operations)

        # Get books operation parameters
        limit: Maximum number of books to return (default: 50, for 'get_books')
        offset: Number of books to skip (for pagination, default: 0, for 'get_books')

        # By letter operation parameters
        letter: Single letter to filter authors by (required for 'by_letter')

    Returns:
        Dictionary containing operation-specific results:

        For operation="list":
            {
                "items": List[Dict] - Author objects with id, name, book_count
                "total": int - Total number of matching authors
                "page": int - Current page number
                "per_page": int - Items per page
                "total_pages": int - Total number of pages
            }

        For operation="get":
            {
                "id": int - Author ID
                "name": str - Author name
                "sort": str - Sortable version of author name
                "book_count": int - Number of books by this author
            }

        For operation="get_books":
            {
                "author": Dict - Author information
                "books": List[Dict] - Paginated list of books
                "total": int - Total number of books by this author
                "page": int - Current page number
                "per_page": int - Items per page
                "total_pages": int - Total number of pages
            }

        For operation="stats":
            {
                "total_authors": int - Total number of authors
                "top_authors": List[Dict] - Top authors by book count
                "authors_by_letter": List[Dict] - Author count by first letter
            }

        For operation="by_letter":
            {
                "authors": List[Dict] - List of author objects whose names start with the letter
                "letter": str - The letter searched
                "count": int - Number of authors found
            }

    Usage:
        # List all authors
        result = await manage_authors(operation="list")

        # Search for authors containing "martin"
        result = await manage_authors(operation="list", query="martin")

        # Get author details
        result = await manage_authors(operation="get", author_id=42)

        # Get books by author
        result = await manage_authors(operation="get_books", author_id=42, limit=10)

        # Get author statistics
        result = await manage_authors(operation="stats")

        # Get authors by letter
        result = await manage_authors(operation="by_letter", letter="A")

    Examples:
        # Search for authors with pagination
        page1 = await manage_authors(operation="list", query="smith", limit=20, offset=0)
        page2 = await manage_authors(operation="list", query="smith", limit=20, offset=20)

        # Get all books by an author with pagination
        books = await manage_authors(operation="get_books", author_id=42, limit=50, offset=0)

        # Get comprehensive statistics
        stats = await manage_authors(operation="stats")
        print(f"Total authors: {stats['total_authors']}")
        print(f"Top author: {stats['top_authors'][0]['name']}")

        # Browse authors by letter
        authors_a = await manage_authors(operation="by_letter", letter="A")

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of the supported operations listed above
        - Missing author_id (get/get_books): Provide author_id parameter
        - Missing letter (by_letter): Provide letter parameter (single character)
        - Author not found: Verify author_id is correct using operation='list'
        - Invalid letter: Letter must be a single alphabetic character
        - No library configured: Use manage_libraries(operation='switch') to configure library

    See Also:
        - manage_libraries(): For library management and switching
        - query_books(): For finding books by author
        - manage_books(): For book management operations
    """
    try:
        if operation == "list":
            try:
                return await list_authors_helper(query=query, limit=limit, offset=offset)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"query": query, "limit": limit, "offset": offset},
                    tool_name="manage_authors",
                    context="Listing authors",
                )

        elif operation == "get":
            if not author_id:
                return format_error_response(
                    error_msg=(
                        "author_id is required for operation='get'. "
                        "Use operation='list' to find available authors."
                    ),
                    error_code="MISSING_AUTHOR_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide author_id parameter (e.g., author_id=42)",
                        "Use operation='list' to see all available authors",
                    ],
                    related_tools=["manage_authors"],
                )
            try:
                return await get_author_helper(author_id=author_id)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"author_id": author_id},
                    tool_name="manage_authors",
                    context=f"Getting author details for author_id={author_id}",
                )

        elif operation == "get_books":
            if not author_id:
                return format_error_response(
                    error_msg=(
                        "author_id is required for operation='get_books'. "
                        "Use operation='list' to find available authors."
                    ),
                    error_code="MISSING_AUTHOR_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide author_id parameter (e.g., author_id=42)",
                        "Use operation='list' to see all available authors",
                    ],
                    related_tools=["manage_authors"],
                )
            try:
                return await get_author_books_helper(
                    author_id=author_id, limit=limit, offset=offset
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"author_id": author_id, "limit": limit, "offset": offset},
                    tool_name="manage_authors",
                    context=f"Getting books for author_id={author_id}",
                )

        elif operation == "stats":
            try:
                return await get_author_stats_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_authors",
                    context="Getting author statistics",
                )

        elif operation == "by_letter":
            if not letter:
                return format_error_response(
                    error_msg=(
                        "letter is required for operation='by_letter'. "
                        "Provide a single alphabetic character."
                    ),
                    error_code="MISSING_LETTER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide letter parameter (e.g., letter='A')",
                        "Letter must be a single alphabetic character",
                        "Letter is case-insensitive",
                    ],
                    related_tools=["manage_authors"],
                )
            try:
                return await get_authors_by_letter_helper(letter=letter)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"letter": letter},
                    tool_name="manage_authors",
                    context=f"Getting authors by letter '{letter}'",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'list', 'get', 'get_books', 'stats', 'by_letter'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='list' to list authors",
                    "Use operation='get' to get author details",
                    "Use operation='get_books' to get books by author",
                    "Use operation='stats' to get author statistics",
                    "Use operation='by_letter' to get authors by first letter",
                ],
                related_tools=["manage_authors"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "author_id": author_id,
                "query": query,
                "letter": letter,
            },
            tool_name="manage_authors",
            context="Author management operation",
        )

