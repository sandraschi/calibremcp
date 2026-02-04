"""
Series management portmanteau tool for CalibreMCP.

Consolidates all series-related operations into a single unified interface,
analogous to manage_authors.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error
from .series_helpers import (
    get_series_books_helper,
    get_series_by_letter_helper,
    get_series_helper,
    get_series_stats_helper,
    list_series_helper,
)

logger = get_logger("calibremcp.tools.series")


@mcp.tool()
async def manage_series(
    operation: str,
    query: str | None = None,
    limit: int = 50,
    offset: int = 0,
    series_id: int | None = None,
    letter: str | None = None,
) -> dict[str, Any]:
    """
    Comprehensive series management tool for CalibreMCP.

    PORTMANTEAU PATTERN: Consolidates series operations analogous to manage_authors.

    SUPPORTED OPERATIONS:
    - list: List series with filtering and pagination
    - get: Get series details by ID
    - get_books: Get all books in a series
    - stats: Library-wide series statistics
    - by_letter: Filter series by first letter of name

    Args:
        operation: One of "list", "get", "get_books", "stats", "by_letter"
        query: Search term for list operation
        limit: Max results (default 50)
        offset: Pagination offset (default 0)
        series_id: Required for get and get_books
        letter: Required for by_letter (single character)

    Returns:
        Operation-specific result dict.
    """
    try:
        if operation == "list":
            return await list_series_helper(query=query, limit=limit, offset=offset)

        elif operation == "get":
            if series_id is None:
                return format_error_response(
                    error_msg="series_id is required for operation='get'.",
                    error_code="MISSING_SERIES_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide series_id parameter",
                        "Use operation='list' to find series IDs",
                    ],
                    related_tools=["manage_series"],
                )
            return await get_series_helper(series_id=series_id)

        elif operation == "get_books":
            if series_id is None:
                return format_error_response(
                    error_msg="series_id is required for operation='get_books'.",
                    error_code="MISSING_SERIES_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide series_id parameter",
                        "Use operation='list' or query_books(series='...') to find series",
                    ],
                    related_tools=["manage_series", "query_books"],
                )
            return await get_series_books_helper(series_id=series_id, limit=limit, offset=offset)

        elif operation == "stats":
            return await get_series_stats_helper()

        elif operation == "by_letter":
            if not letter:
                return format_error_response(
                    error_msg="letter is required for operation='by_letter'.",
                    error_code="MISSING_LETTER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide letter (e.g., 'A')"],
                    related_tools=["manage_series"],
                )
            return await get_series_by_letter_helper(letter=letter.strip())

        else:
            return format_error_response(
                error_msg=f"Invalid operation: '{operation}'. Use: list, get, get_books, stats, by_letter.",
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "list: List series with optional search",
                    "get: Get series by ID",
                    "get_books: Get books in series",
                    "stats: Series statistics",
                    "by_letter: Series starting with letter",
                ],
                related_tools=["manage_series"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "query": query,
                "series_id": series_id,
                "letter": letter,
                "limit": limit,
                "offset": offset,
            },
            tool_name="manage_series",
            context="Managing series in Calibre library",
        )
