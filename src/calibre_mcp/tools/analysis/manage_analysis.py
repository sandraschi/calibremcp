"""
Analysis management portmanteau tool for CalibreMCP.

Consolidates all analysis and statistics operations into a single unified interface.
"""

from typing import Dict, Any, Optional

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response

# Import helper functions (NOT registered as MCP tools)
from .analysis_helpers import (
    get_tag_statistics_helper,
    find_duplicate_books_helper,
    get_series_analysis_helper,
    analyze_library_health_helper,
    unread_priority_list_helper,
    reading_statistics_helper,
)

logger = get_logger("calibremcp.tools.analysis")


@mcp.tool()
async def manage_analysis(
    operation: str,
    limit: Optional[int] = None,
    threshold: Optional[float] = None,
    book_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Comprehensive analysis and statistics tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 6 analytics operations into a single interface to eliminate decision paralysis
    and provide deep insights into library composition and reading habits.
    Follows SOTA 2026 requirements for advanced knowledge base analytics.

    SUPPORTED OPERATIONS:
    - tag_statistics: Analyze tag usage patterns and identify redundancy or gaps
    - duplicate_books: Find potential content duplicates using fuzzy matching and metadata
    - series_analysis: Detect incomplete series and suggest missing volumes
    - library_health: High-level audit of metadata integrity and file consistency
    - unread_priority: Efficiently prioritize reading queue using satisfaction metrics
    - reading_stats: Detailed analytics on completion rates and genre trends

    Args:
        operation (str, required): The operation to perform. Must be one of:
            "tag_statistics", "duplicate_books", "series_analysis",
            "library_health", "unread_priority", "reading_stats".

    Returns:
        Dictionary containing operation-specific results:
        - For 'tag_statistics': usage frequency and consolidation suggestions
        - For 'duplicate_books': similarity groups for manual review
        - For 'series_analysis': missing sequence numbers and reading order
        - For 'library_health': metadata audit report and repair recommendations
        - For 'unread_priority': sorted list of books for maximum efficiency
        - For 'reading_stats': temporal trends and thematic distribution

    Usage:
        result = await manage_analysis(operation="tag_statistics")
        result = await manage_analysis(operation="series_analysis")
        result = await manage_analysis(operation="reading_stats")

    Errors:
        - INVALID_OPERATION: When the specified operation is not supported
        - CALIBRATION_REQUIRED: When library context is missing or invalid

    See Also:
        - manage_libraries(): For project switching
        - manage_tags(): For actual tag manipulation
        - manage_books(): For manual metadata correction
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
