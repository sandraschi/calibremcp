"""
Helper functions for description management (Calibre comment = description).

Read-only browse operations. For create/update/delete use manage_comments.
"""

from typing import Any

from ...logging_config import get_logger
from ...services.description_service import get_description_service
from ..shared.error_handling import format_error_response

logger = get_logger("calibremcp.tools.descriptions")


async def list_descriptions_helper(
    query: str | None = None,
    has_description: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """List books with description info. Optional search in description text."""
    try:
        svc = get_description_service()
        return svc.get_all(
            skip=offset,
            limit=limit,
            search=query,
            has_description=has_description,
        )
    except Exception as e:
        logger.error(f"Error listing descriptions: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to list descriptions: {str(e)}",
            error_code="LIST_DESCRIPTIONS_ERROR",
            error_type=type(e).__name__,
            operation="list",
        )


async def get_description_helper(book_id: int) -> dict[str, Any]:
    """Get description for a book."""
    try:
        svc = get_description_service()
        return svc.get_by_book_id(book_id)
    except Exception as e:
        logger.error(f"Error getting description for book {book_id}: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get description: {str(e)}",
            error_code="GET_DESCRIPTION_ERROR",
            error_type=type(e).__name__,
            operation="get",
            suggestions=["Verify book_id", "Use query_books to find book IDs"],
            related_tools=["query_books", "manage_comments"],
        )


async def get_description_stats_helper() -> dict[str, Any]:
    """Get description coverage statistics."""
    try:
        svc = get_description_service()
        return svc.get_stats()
    except Exception as e:
        logger.error(f"Error getting description stats: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get description statistics: {str(e)}",
            error_code="GET_DESCRIPTION_STATS_ERROR",
            error_type=type(e).__name__,
            operation="stats",
        )


async def get_descriptions_by_letter_helper(letter: str) -> dict[str, Any]:
    """Get books with descriptions whose title starts with letter."""
    try:
        if len(letter) != 1 or not letter.isalpha():
            return format_error_response(
                error_msg=f"Invalid letter: '{letter}'. Must be a single alphabetic character.",
                error_code="INVALID_LETTER",
                error_type="ValueError",
                operation="by_letter",
                suggestions=["Provide a single letter (e.g., 'A')"],
            )

        svc = get_description_service()
        items = svc.get_by_letter(letter.upper())
        return {"items": items, "letter": letter.upper(), "count": len(items)}
    except Exception as e:
        logger.error(f"Error getting descriptions by letter {letter}: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get descriptions by letter: {str(e)}",
            error_code="GET_DESCRIPTIONS_BY_LETTER_ERROR",
            error_type=type(e).__name__,
            operation="by_letter",
        )
