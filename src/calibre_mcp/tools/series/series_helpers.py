"""
Helper functions for series management operations.

Uses DatabaseService (same as books, authors, tags, publishers).
"""

from typing import Optional, Dict, Any

from ...db.database import db as database_singleton
from ...services.series_service import get_series_service
from ...logging_config import get_logger
from ..shared.error_handling import format_error_response

logger = get_logger("calibremcp.tools.series")


async def list_series_helper(
    query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """List series with filtering and pagination. Uses DatabaseService (same as books/authors/tags)."""
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
        svc = get_series_service()
        return svc.get_all(
            skip=offset,
            limit=limit,
            search=query,
            sort_by="name",
            sort_order="asc",
        )
    except Exception as e:
        logger.error(f"Error listing series: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to list series: {str(e)}",
            error_code="LIST_SERIES_ERROR",
            error_type=type(e).__name__,
            operation="list",
        )


async def get_series_helper(series_id: int) -> Dict[str, Any]:
    """Get series details by ID."""
    try:
        svc = get_series_service()
        return svc.get_by_id(series_id)
    except Exception as e:
        logger.error(f"Error getting series {series_id}: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Series with ID {series_id} not found: {str(e)}",
            error_code="SERIES_NOT_FOUND",
            error_type=type(e).__name__,
            operation="get",
            suggestions=[
                f"Verify series_id={series_id} is correct",
                "Use operation='list' to see all available series",
            ],
        )


async def get_series_books_helper(
    series_id: int,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """Get books in a series."""
    try:
        svc = get_series_service()
        return svc.get_books_by_series(
            series_id=series_id,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Error getting books for series {series_id}: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get books for series {series_id}: {str(e)}",
            error_code="GET_SERIES_BOOKS_ERROR",
            error_type=type(e).__name__,
            operation="get_books",
            suggestions=[
                f"Verify series_id={series_id} is correct",
                "Use operation='list' to see all available series",
            ],
        )


async def get_series_stats_helper() -> Dict[str, Any]:
    """Get series statistics."""
    try:
        svc = get_series_service()
        return svc.get_series_stats()
    except Exception as e:
        logger.error(f"Error getting series statistics: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get series statistics: {str(e)}",
            error_code="GET_SERIES_STATS_ERROR",
            error_type=type(e).__name__,
            operation="stats",
        )


async def get_series_by_letter_helper(letter: str) -> Dict[str, Any]:
    """Get series by first letter of name."""
    try:
        if len(letter) != 1 or not letter.isalpha():
            return format_error_response(
                error_msg=f"Invalid letter: '{letter}'. Must be a single alphabetic character.",
                error_code="INVALID_LETTER",
                error_type="ValueError",
                operation="by_letter",
                suggestions=[
                    "Provide a single letter (e.g., 'A' or 'a')",
                    "Letter is case-insensitive",
                ],
            )

        svc = get_series_service()
        series_list = svc.get_series_by_letter(letter.upper())
        return {"series": series_list, "letter": letter.upper(), "count": len(series_list)}
    except Exception as e:
        logger.error(f"Error getting series by letter {letter}: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get series by letter {letter}: {str(e)}",
            error_code="GET_SERIES_BY_LETTER_ERROR",
            error_type=type(e).__name__,
            operation="by_letter",
        )
