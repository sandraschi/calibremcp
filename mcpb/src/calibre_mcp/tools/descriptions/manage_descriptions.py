"""
Description management portmanteau for CalibreMCP.

Calibre's "comment" field = book description/synopsis. This tool provides
browse/query operations analogous to manage_authors.
For create/update/delete use manage_comments.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error
from .description_helpers import (
    get_description_helper,
    get_description_stats_helper,
    get_descriptions_by_letter_helper,
    list_descriptions_helper,
)

logger = get_logger("calibremcp.tools.descriptions")


@mcp.tool()
async def manage_descriptions(
    operation: str,
    query: str | None = None,
    has_description: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    book_id: int | None = None,
    letter: str | None = None,
) -> dict[str, Any]:
    """
    Browse and query book descriptions (Calibre comment field).

    Description = Comment in Calibre - the book synopsis. For editing
    (create/update/delete) use manage_comments.

    PORTMANTEAU PATTERN: Analogous to manage_authors for browse operations.

    SUPPORTED OPERATIONS:
    - list: List books with optional description filter/search
    - get: Get description for a book
    - stats: Description coverage statistics
    - by_letter: Books with descriptions whose title starts with letter

    Args:
        operation: One of "list", "get", "stats", "by_letter"
        query: Search in description text (list)
        has_description: If True, only books with descriptions; if False, only without (list)
        limit: Max results (default 50)
        offset: Pagination offset (default 0)
        book_id: Required for get
        letter: Required for by_letter (single character)

    Returns:
        Operation-specific result dict.
    """
    try:
        if operation == "list":
            return await list_descriptions_helper(
                query=query,
                has_description=has_description,
                limit=limit,
                offset=offset,
            )

        elif operation == "get":
            if book_id is None:
                return format_error_response(
                    error_msg="book_id is required for operation='get'.",
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide book_id parameter",
                        "Use query_books to find book IDs",
                    ],
                    related_tools=["query_books", "manage_comments"],
                )
            return await get_description_helper(book_id=book_id)

        elif operation == "stats":
            return await get_description_stats_helper()

        elif operation == "by_letter":
            if not letter:
                return format_error_response(
                    error_msg="letter is required for operation='by_letter'.",
                    error_code="MISSING_LETTER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide letter (e.g., 'A')"],
                    related_tools=["manage_descriptions"],
                )
            return await get_descriptions_by_letter_helper(letter=letter.strip())

        else:
            return format_error_response(
                error_msg=f"Invalid operation: '{operation}'. Use: list, get, stats, by_letter.",
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "list: List books with description filter/search",
                    "get: Get description for book",
                    "stats: Description coverage stats",
                    "by_letter: Books with descriptions by title letter",
                ],
                related_tools=["manage_descriptions", "manage_comments"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "query": query,
                "book_id": book_id,
                "letter": letter,
                "has_description": has_description,
                "limit": limit,
                "offset": offset,
            },
            tool_name="manage_descriptions",
            context="Browsing book descriptions (Calibre comment field)",
        )
