"""
Analysis management portmanteau tool for CalibreMCP.

Consolidates all analysis and statistics operations into a single unified interface.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Import helper functions (NOT registered as MCP tools)
from .analysis_helpers import (
    analyze_library_health_helper,
    find_duplicate_books_helper,
    get_series_analysis_helper,
    get_tag_statistics_helper,
    reading_statistics_helper,
    unread_priority_list_helper,
)

logger = get_logger("calibremcp.tools.analysis")


@mcp.tool()
async def manage_analysis(
    operation: str,
    limit: int | None = None,
    threshold: float | None = None,
    book_id: int | None = None,
) -> dict[str, Any]:
    """
    Advanced library analytics and metadata auditing interface.

    Operations:
    - tag_statistics: Usage frequency and consolidation suggestions.
    - duplicate_books: Find potential content duplicates via fuzzy matching.
    - series_analysis: Detect missing volumes and sequence gaps.
    - library_health: Audit metadata integrity and file consistency.
    - unread_priority: Quantitative prioritization of the reading queue.
    - reading_stats: Temporal trends and genre distribution analytics.

    Example:
    - manage_analysis(operation="library_health")
    - manage_analysis(operation="duplicate_books")
    """
    try:
        if operation == "tag_statistics":
            try:
                return await get_tag_statistics_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_analysis",
                    context="Analyzing tag statistics",
                )

        elif operation == "duplicate_books":
            try:
                return await find_duplicate_books_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_analysis",
                    context="Finding duplicate books",
                )

        elif operation == "series_analysis":
            try:
                return await get_series_analysis_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_analysis",
                    context="Analyzing series completion",
                )

        elif operation == "library_health":
            try:
                return await analyze_library_health_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_analysis",
                    context="Analyzing library health",
                )

        elif operation == "unread_priority":
            try:
                return await unread_priority_list_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_analysis",
                    context="Getting prioritized unread books list",
                )

        elif operation == "reading_stats":
            try:
                return await reading_statistics_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_analysis",
                    context="Getting reading statistics",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'tag_statistics', 'duplicate_books', 'series_analysis', "
                    "'library_health', 'unread_priority', 'reading_stats'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='tag_statistics' to analyze tag usage",
                    "Use operation='duplicate_books' to find duplicate books",
                    "Use operation='series_analysis' to analyze series completion",
                    "Use operation='library_health' to check library health",
                    "Use operation='unread_priority' to get prioritized unread books",
                    "Use operation='reading_stats' to get reading analytics",
                ],
                related_tools=["manage_analysis"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={"operation": operation},
            tool_name="manage_analysis",
            context="Analysis operation",
        )
