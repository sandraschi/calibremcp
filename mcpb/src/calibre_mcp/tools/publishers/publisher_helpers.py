"""
Helper functions for publisher management operations.

Uses DatabaseService (same as books, authors, tags) for library context.
"""

from typing import Any

from ...db.database import db as database_singleton
from ...logging_config import get_logger
from ...services.publisher_service import get_publisher_service
from ..shared.error_handling import format_error_response

logger = get_logger("calibremcp.tools.publishers")


async def list_publishers_helper(
    query: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """List publishers with filtering and pagination. Uses DatabaseService (same as books/authors/tags)."""
    try:
        if not database_singleton._engine or not database_singleton._current_db_path:
            return {
                "error": "No library loaded",
                "message": "Database not initialized. Ensure a library is loaded at startup.",
                "items": [],
                "total": 0,
                "page": 1,
                "per_page": limit,
                "total_pages": 0,
            }
        svc = get_publisher_service()
        return svc.get_all(
            skip=offset,
            limit=limit,
            search=query,
            sort_by="name",
            sort_order="asc",
        )
    except Exception as e:
        logger.error(f"Error listing publishers: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to list publishers: {str(e)}",
            error_code="LIST_PUBLISHERS_ERROR",
            error_type=type(e).__name__,
            operation="list",
        )


async def get_publisher_helper(
    publisher_id: int | None = None,
    publisher_name: str | None = None,
) -> dict[str, Any]:
    """Get publisher details by ID or name."""
    try:
        svc = get_publisher_service()
        if publisher_id is not None:
            return svc.get_by_id(publisher_id)
        if publisher_name:
            return svc.get_by_name(publisher_name)
        return format_error_response(
            error_msg="publisher_id or publisher_name is required.",
            error_code="MISSING_PUBLISHER",
            error_type="ValueError",
            operation="get",
            suggestions=["Provide publisher_id or publisher_name"],
            related_tools=["manage_publishers"],
        )
    except Exception as e:
        logger.error(f"Error getting publisher: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Publisher not found: {str(e)}",
            error_code="PUBLISHER_NOT_FOUND",
            error_type=type(e).__name__,
            operation="get",
            suggestions=[
                "Verify publisher_id or publisher_name",
                "Use operation='list' to see available publishers",
            ],
        )


async def get_publisher_books_helper(
    publisher_id: int | None = None,
    publisher_name: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Get books by publisher."""
    try:
        svc = get_publisher_service()
        if publisher_id is None and not publisher_name:
            return format_error_response(
                error_msg="publisher_id or publisher_name is required.",
                error_code="MISSING_PUBLISHER",
                error_type="ValueError",
                operation="get_books",
                suggestions=["Provide publisher_id or publisher_name"],
                related_tools=["manage_publishers"],
            )
        return svc.get_books_by_publisher(
            publisher_id=publisher_id,
            publisher_name=publisher_name,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Error getting books for publisher: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get books: {str(e)}",
            error_code="GET_PUBLISHER_BOOKS_ERROR",
            error_type=type(e).__name__,
            operation="get_books",
            suggestions=["Verify publisher_id or publisher_name"],
            related_tools=["manage_publishers"],
        )


async def get_publisher_stats_helper() -> dict[str, Any]:
    """Get publisher statistics."""
    try:
        svc = get_publisher_service()
        return svc.get_stats()
    except Exception as e:
        logger.error(f"Error getting publisher stats: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get publisher statistics: {str(e)}",
            error_code="GET_PUBLISHER_STATS_ERROR",
            error_type=type(e).__name__,
            operation="stats",
        )


async def get_publishers_by_letter_helper(letter: str) -> dict[str, Any]:
    """Get publishers by first letter of name."""
    try:
        if len(letter) != 1 or not letter.isalpha():
            return format_error_response(
                error_msg=f"Invalid letter: '{letter}'. Must be a single alphabetic character.",
                error_code="INVALID_LETTER",
                error_type="ValueError",
                operation="by_letter",
                suggestions=["Provide a single letter (e.g., 'A')"],
            )

        svc = get_publisher_service()
        items = svc.get_by_letter(letter.upper())
        return {"publishers": items, "letter": letter.upper(), "count": len(items)}
    except Exception as e:
        logger.error(f"Error getting publishers by letter {letter}: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get publishers by letter: {str(e)}",
            error_code="GET_PUBLISHERS_BY_LETTER_ERROR",
            error_type=type(e).__name__,
            operation="by_letter",
        )
