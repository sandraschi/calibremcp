"""
Date/time management portmanteau for CalibreMCP.

Query books by added date (timestamp) or publication date (pubdate).
Calibre's pubdate = edition date; use manage_extended_metadata for first_published.
"""

from typing import Optional, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response
from ...services.times_service import TimesService

logger = get_logger("calibremcp.tools.times")


def _get_times_service() -> TimesService:
    return TimesService()


@mcp.tool()
async def manage_times(
    operation: str,
    added_after: Optional[str] = None,
    added_before: Optional[str] = None,
    published_after: Optional[str] = None,
    published_before: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Query books by date: added (timestamp) or published (pubdate/edition).

    - timestamp = when book was added to Calibre library
    - pubdate = edition publication date (use manage_extended_metadata for first_published)

    SUPPORTED OPERATIONS:
    - added_in_range: Books added between added_after and added_before
    - published_in_range: Books with pubdate in range
    - recent_additions: Most recently added books
    - stats_by_month_added: Count per month (added)
    - stats_by_month_published: Count per month (pubdate)
    - date_stats: Summary (earliest/latest dates)

    Args:
        operation: One of "added_in_range", "published_in_range", "recent_additions",
                   "stats_by_month_added", "stats_by_month_published", "date_stats"
        added_after: Start date for added (YYYY-MM-DD)
        added_before: End date for added (YYYY-MM-DD)
        published_after: Start date for pubdate
        published_before: End date for pubdate
        year: Filter stats by year (optional)
        limit: Max results (default 50)
        offset: Pagination offset (default 0)

    Returns:
        Operation-specific result dict.
    """
    try:
        svc = _get_times_service()

        if operation == "added_in_range":
            if not added_after:
                return format_error_response(
                    error_msg="added_after is required for added_in_range (e.g. 2024-12-01).",
                    error_code="MISSING_ADDED_AFTER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide added_after in YYYY-MM-DD format"],
                    related_tools=["query_books", "manage_times"],
                )
            return svc.added_in_range(
                after=added_after,
                before=added_before,
                limit=limit,
                offset=offset,
            )

        elif operation == "published_in_range":
            if not published_after:
                return format_error_response(
                    error_msg="published_after is required for published_in_range.",
                    error_code="MISSING_PUBLISHED_AFTER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide published_after in YYYY-MM-DD format"],
                    related_tools=["query_books", "manage_times"],
                )
            return svc.published_in_range(
                after=published_after,
                before=published_before,
                limit=limit,
                offset=offset,
            )

        elif operation == "recent_additions":
            return svc.recent_additions(limit=limit)

        elif operation == "stats_by_month_added":
            return svc.stats_by_month_added(year=year)

        elif operation == "stats_by_month_published":
            return svc.stats_by_month_published(year=year)

        elif operation == "date_stats":
            return svc.date_stats()

        else:
            return format_error_response(
                error_msg=f"Invalid operation: '{operation}'. Use: added_in_range, published_in_range, recent_additions, stats_by_month_added, stats_by_month_published, date_stats.",
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "added_in_range: Books added between dates",
                    "published_in_range: Books by pubdate range",
                    "recent_additions: Recently added books",
                    "stats_by_month_added: Count by month (added)",
                    "stats_by_month_published: Count by month (pubdate)",
                    "date_stats: Date range summary",
                ],
                related_tools=["manage_times", "query_books"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "added_after": added_after,
                "added_before": added_before,
                "published_after": published_after,
                "published_before": published_before,
                "year": year,
            },
            tool_name="manage_times",
            context="Querying books by date",
        )
