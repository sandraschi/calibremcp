"""
Analysis management portmanteau tool for CalibreMCP.

Consolidates all analysis and statistics operations into a single unified interface.
"""

from typing import Dict, Any

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
async def manage_analysis(operation: str) -> Dict[str, Any]:
    """
    Comprehensive analysis and statistics tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 6 separate tools (one per operation), this tool consolidates related
    analysis operations into a single interface. This design:
    - Prevents tool explosion (6 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with analysis tasks
    - Enables consistent analysis interface across all operations
    - Follows FastMCP 2.12+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - tag_statistics: Analyze tag usage and suggest cleanup operations
    - duplicate_books: Find potentially duplicate books for cleanup
    - series_analysis: Analyze book series completion and reading order
    - library_health: Perform comprehensive library health check
    - unread_priority: Get prioritized list of unread books
    - reading_stats: Generate personal reading analytics

    OPERATIONS DETAIL:

    tag_statistics: Analyze tag usage and suggest cleanup
    - Identifies duplicate tags (similar names), unused tags
    - Provides suggestions for tag consolidation and organization
    - Helps maintain a clean and organized tag structure
    - No parameters required

    duplicate_books: Find potentially duplicate books
    - Uses title similarity, author matching, and ISBN comparison
    - Identifies potential duplicates for cleanup and organization
    - No parameters required

    series_analysis: Analyze book series completion
    - Identifies incomplete series (missing volumes)
    - Calculates series statistics
    - Suggests optimal reading order based on series_index
    - Helps track series progress and plan reading
    - No parameters required

    library_health: Perform library health check
    - Checks for missing files, corrupted metadata, orphaned records
    - Provides recommendations for library maintenance and optimization
    - No parameters required

    unread_priority: Prioritize unread books
    - Austrian efficiency: Eliminate decision paralysis
    - Uses rating, series status, purchase date, and tags
    - Creates prioritized reading list that maximizes satisfaction
    - No parameters required

    reading_stats: Generate reading analytics
    - Analyzes reading patterns, completion rates, genre preferences
    - Provides insights into reading habits and preferences
    - No parameters required

    Prerequisites:
        - Library must be configured (use manage_libraries(operation='switch'))

    Parameters:
        operation: The operation to perform. Must be one of:
            "tag_statistics", "duplicate_books", "series_analysis",
            "library_health", "unread_priority", "reading_stats"

    Returns:
        Dictionary containing operation-specific results:

        For operation="tag_statistics":
            TagStatsResponse with:
            - total_tags: Total number of unique tags
            - duplicate_tags: Groups of potentially duplicate tags
            - unused_tags: Tags not assigned to any books
            - suggestions: Recommended tag consolidation actions

        For operation="duplicate_books":
            DuplicatesResponse with:
            - duplicate_groups: List of potential duplicate book groups

        For operation="series_analysis":
            SeriesAnalysisResponse with:
            - incomplete_series: Series with missing volumes or gaps
            - reading_order_suggestions: Recommended reading order for series
            - series_statistics: Overall statistics about all series

        For operation="library_health":
            LibraryHealthResponse with:
            - health_status: Overall health status
            - issues: List of identified issues
            - recommendations: Maintenance recommendations
            - statistics: Library statistics

        For operation="unread_priority":
            UnreadPriorityResponse with:
            - prioritized_books: Prioritized list of unread books
            - reasoning: Explanation of prioritization

        For operation="reading_stats":
            ReadingStats with:
            - total_books, read_books, unread_books: Book counts
            - reading_patterns: Analysis of reading patterns
            - genre_preferences: Genre distribution
            - insights: Reading insights and recommendations

    Usage:
        # Get tag statistics
        result = await manage_analysis(operation="tag_statistics")

        # Find duplicate books
        result = await manage_analysis(operation="duplicate_books")

        # Analyze series
        result = await manage_analysis(operation="series_analysis")

        # Check library health
        result = await manage_analysis(operation="library_health")

        # Get unread priority list
        result = await manage_analysis(operation="unread_priority")

        # Get reading statistics
        result = await manage_analysis(operation="reading_stats")

    Examples:
        # Tag weeding workflow
        tag_stats = await manage_analysis(operation="tag_statistics")
        for dup_group in tag_stats["duplicate_tags"]:
            print(f"Similar tags: {dup_group['tags']}")

        # Series completion check
        series_analysis = await manage_analysis(operation="series_analysis")
        for series in series_analysis["incomplete_series"]:
            print(f"{series['name']}: {series['missing_count']} missing volumes")

        # Library maintenance
        health = await manage_analysis(operation="library_health")
        for issue in health["issues"]:
            print(f"Issue: {issue['description']}")

        # Reading recommendations
        priority = await manage_analysis(operation="unread_priority")
        for book in priority["prioritized_books"][:5]:
            print(f"Read next: {book['title']}")

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of the supported operations listed above
        - No library configured: Use manage_libraries(operation='switch') to configure library

    See Also:
        - manage_libraries(): For library management and switching
        - manage_tags(): For tag management operations
        - query_books(): For finding books
        - manage_books(): For book management operations
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

