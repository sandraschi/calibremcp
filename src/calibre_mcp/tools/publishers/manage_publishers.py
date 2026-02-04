"""
Publisher management portmanteau tool for CalibreMCP.

Consolidates all publisher-related operations into a single unified interface,
analogous to manage_authors. Supports both Calibre publishers table and
identifiers (type='publisher') fallback.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error
from .publisher_helpers import (
    get_publisher_books_helper,
    get_publisher_helper,
    get_publisher_stats_helper,
    get_publishers_by_letter_helper,
    list_publishers_helper,
)

logger = get_logger("calibremcp.tools.publishers")


@mcp.tool()
async def manage_publishers(
    operation: str,
    query: str | None = None,
    limit: int = 50,
    offset: int = 0,
    publisher_id: int | None = None,
    publisher_name: str | None = None,
    letter: str | None = None,
) -> dict[str, Any]:
    """
    Comprehensive publisher management tool for CalibreMCP.

    PORTMANTEAU PATTERN: Consolidates publisher operations analogous to manage_authors.

    SUPPORTED OPERATIONS:
    - list: List publishers with filtering and pagination
    - get: Get publisher details by ID or name
    - get_books: Get all books from a publisher
    - stats: Library-wide publisher statistics
    - by_letter: Filter publishers by first letter of name

    Works with Calibre publishers table; falls back to identifiers (type='publisher')
    if publishers table does not exist.

    Args:
        operation: One of "list", "get", "get_books", "stats", "by_letter"
        query: Search term for list operation
        limit: Max results (default 50)
        offset: Pagination offset (default 0)
        publisher_id: Required for get/get_books when using table (optional with publisher_name)
        publisher_name: Alternative to publisher_id for get/get_books
        letter: Required for by_letter (single character)

    Returns:
        Operation-specific result dict.
    """
    try:
        if operation == "list":
            return await list_publishers_helper(query=query, limit=limit, offset=offset)

        elif operation == "get":
            if publisher_id is None and not publisher_name:
                return format_error_response(
                    error_msg="publisher_id or publisher_name is required for operation='get'.",
                    error_code="MISSING_PUBLISHER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide publisher_id or publisher_name",
                        "Use operation='list' to find publishers",
                    ],
                    related_tools=["manage_publishers"],
                )
            return await get_publisher_helper(
                publisher_id=publisher_id,
                publisher_name=publisher_name,
            )

        elif operation == "get_books":
            if publisher_id is None and not publisher_name:
                return format_error_response(
                    error_msg="publisher_id or publisher_name is required for operation='get_books'.",
                    error_code="MISSING_PUBLISHER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide publisher_id or publisher_name",
                        "Use operation='list' or query_books(publisher='...')",
                    ],
                    related_tools=["manage_publishers", "query_books"],
                )
            return await get_publisher_books_helper(
                publisher_id=publisher_id,
                publisher_name=publisher_name,
                limit=limit,
                offset=offset,
            )

        elif operation == "stats":
            return await get_publisher_stats_helper()

        elif operation == "by_letter":
            if not letter:
                return format_error_response(
                    error_msg="letter is required for operation='by_letter'.",
                    error_code="MISSING_LETTER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide letter (e.g., 'A')"],
                    related_tools=["manage_publishers"],
                )
            return await get_publishers_by_letter_helper(letter=letter.strip())

        else:
            return format_error_response(
                error_msg=f"Invalid operation: '{operation}'. Use: list, get, get_books, stats, by_letter.",
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "list: List publishers with optional search",
                    "get: Get publisher by ID or name",
                    "get_books: Get books from publisher",
                    "stats: Publisher statistics",
                    "by_letter: Publishers starting with letter",
                ],
                related_tools=["manage_publishers"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "query": query,
                "publisher_id": publisher_id,
                "publisher_name": publisher_name,
                "letter": letter,
                "limit": limit,
                "offset": offset,
            },
            tool_name="manage_publishers",
            context="Managing publishers in Calibre library",
        )
