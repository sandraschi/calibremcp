"""
Helper functions for analysis operations.

These functions are NOT registered as MCP tools - they are called by
the manage_analysis portmanteau tool.

NOTE: These helpers delegate to the functions in library_analysis.py which
are kept for backward compatibility but are no longer registered as tools.
"""


from ...server import (
    TagStatsResponse,
    DuplicatesResponse,
    SeriesAnalysisResponse,
    LibraryHealthResponse,
    UnreadPriorityResponse,
    ReadingStats,
)
from ...logging_config import get_logger

# Import the deprecated individual tools as helpers (they no longer have @mcp.tool())
from .library_analysis import (
    get_tag_statistics,
    find_duplicate_books,
    get_series_analysis,
    analyze_library_health,
    unread_priority_list,
    reading_statistics,
)

logger = get_logger("calibremcp.tools.analysis")


async def get_tag_statistics_helper() -> TagStatsResponse:
    """
    Helper function to get tag statistics.

    Returns:
        TagStatsResponse with tag usage analysis
    """
    # Delegate to the deprecated function (no longer registered as tool)
    return await get_tag_statistics()


async def find_duplicate_books_helper() -> DuplicatesResponse:
    """
    Helper function to find duplicate books.

    Returns:
        DuplicatesResponse with potential duplicate book groups
    """
    # Delegate to the deprecated function (no longer registered as tool)
    return await find_duplicate_books()


async def get_series_analysis_helper() -> SeriesAnalysisResponse:
    """
    Helper function to get series analysis.

    Returns:
        SeriesAnalysisResponse with series completion analysis
    """
    # Delegate to the deprecated function (no longer registered as tool)
    return await get_series_analysis()


async def analyze_library_health_helper() -> LibraryHealthResponse:
    """
    Helper function to analyze library health.

    Returns:
        LibraryHealthResponse with health check results
    """
    # Delegate to the deprecated function (no longer registered as tool)
    return await analyze_library_health()


async def unread_priority_list_helper() -> UnreadPriorityResponse:
    """
    Helper function to get unread priority list.

    Returns:
        UnreadPriorityResponse with prioritized unread books
    """
    # Delegate to the deprecated function (no longer registered as tool)
    return await unread_priority_list()


async def reading_statistics_helper() -> ReadingStats:
    """
    Helper function to get reading statistics.

    Returns:
        ReadingStats with reading analytics
    """
    # Delegate to the deprecated function (no longer registered as tool)
    return await reading_statistics()
