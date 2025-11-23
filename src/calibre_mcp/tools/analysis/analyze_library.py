"""
Library analysis portmanteau tool for CalibreMCP.

Consolidates all library analysis operations into a single unified interface.
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
async def analyze_library(operation: str) -> Dict[str, Any]:
    """
    Comprehensive library analysis tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 6 separate tools (one per analysis type), this tool consolidates related
    analysis operations into a single interface. This design:
    - Prevents tool explosion (6 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with analysis tasks
    - Enables consistent analysis interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - tag_statistics: Analyze tag usage and suggest cleanup operations
    - duplicates: Find potentially duplicate books
    - series: Analyze book series completion and reading order
    - health: Perform comprehensive library health check
    - unread_priority: Prioritize unread books (Austrian efficiency)
    - reading_stats: Generate personal reading analytics

    OPERATIONS DETAIL:

    tag_statistics: Analyze tag usage and suggest cleanup
    - Identifies duplicate tags (similar names) with similarity scores
    - Finds unused tags (not assigned to any books)
    - Provides suggestions for tag consolidation and organization
    - Helps maintain clean and organized tag structure
    - Returns: TagStatsResponse with duplicate groups, unused tags, suggestions

    duplicates: Find duplicate books
    - Uses title similarity, author matching, and ISBN comparison
    - Identifies potential duplicates for cleanup and organization
    - Works within and across libraries
    - Returns: DuplicatesResponse with duplicate book groups

    series: Analyze book series
    - Identifies incomplete series (missing volumes)
    - Calculates series statistics
    - Suggests optimal reading order based on series_index
    - Helps track series progress and plan reading
    - Returns: SeriesAnalysisResponse with incomplete series and reading order

    health: Library health check
    - Checks for missing files, corrupted metadata, orphaned records
    - Provides recommendations for library maintenance and optimization
    - Database integrity analysis
    - Returns: LibraryHealthResponse with health score, issues, recommendations

    unread_priority: Prioritize unread books
    - Austrian efficiency: Eliminate decision paralysis
    - Uses rating, series status, purchase date, and tags
    - Creates prioritized reading list maximizing satisfaction
    - Returns: UnreadPriorityResponse with prioritized books and reasoning

    reading_stats: Reading analytics
    - Analyzes reading patterns and completion rates
    - Genre preferences and insights
    - Reading habits and preferences analysis
    - Returns: ReadingStats with comprehensive analytics

    Prerequisites:
        - Library must be accessible (auto-loaded on server startup)
        - Database must be initialized

    Parameters:
        operation: The analysis operation to perform. Must be one of:
            "tag_statistics", "duplicates", "series", "health", "unread_priority", "reading_stats"

    Returns:
        Dictionary containing operation-specific results:

        For operation="tag_statistics":
            {
                "total_tags": int - Total number of unique tags
                "unique_tags": int - Number of distinct tags
                "duplicate_tags": List[Dict] - Groups of potentially duplicate tags
                "unused_tags": List[str] - Tags not assigned to any books
                "suggestions": List[Dict] - Recommended tag consolidation actions
            }

        For operation="duplicates":
            {
                "duplicate_groups": List[Dict] - Groups of potentially duplicate books
                "total_duplicates": int - Total number of duplicate groups
                "confidence_scores": Dict - Confidence scores for duplicates
            }

        For operation="series":
            {
                "incomplete_series": List[Dict] - Series with missing volumes
                "reading_order_suggestions": List[Dict] - Recommended reading order
                "series_statistics": Dict - Overall series statistics
            }

        For operation="health":
            {
                "health_score": float - Overall health score (0.0-1.0)
                "issues_found": List[Dict] - Issues discovered
                "recommendations": List[str] - Maintenance recommendations
                "database_integrity": bool - Database integrity status
            }

        For operation="unread_priority":
            {
                "prioritized_books": List[Dict] - Prioritized unread books
                "priority_reasons": Dict - Reasoning for prioritization
                "total_unread": int - Total number of unread books
            }

        For operation="reading_stats":
            {
                "total_books_read": int - Total books read
                "average_rating": float - Average rating
                "favorite_genres": List[str] - Favorite genres
                "reading_patterns": Dict - Reading pattern analysis
            }

    Usage:
        # Analyze tag usage
        result = await analyze_library(operation="tag_statistics")

        # Find duplicate books
        result = await analyze_library(operation="duplicates")

        # Analyze series
        result = await analyze_library(operation="series")

        # Check library health
        result = await analyze_library(operation="health")

        # Get prioritized unread list
        result = await analyze_library(operation="unread_priority")

        # Get reading statistics
        result = await analyze_library(operation="reading_stats")

    Examples:
        # Tag weeding workflow
        tag_stats = await analyze_library(operation="tag_statistics")
        print(f"Found {len(tag_stats['duplicate_tags'])} duplicate tag groups")
        print(f"Found {len(tag_stats['unused_tags'])} unused tags")

        # Series analysis
        series_analysis = await analyze_library(operation="series")
        for series in series_analysis["incomplete_series"]:
            print(f"{series['name']}: Missing {series['missing_count']} volumes")

        # Library health check
        health = await analyze_library(operation="health")
        print(f"Library health score: {health['health_score']}")
        if health["issues_found"]:
            print(f"Issues found: {len(health['issues_found'])}")

        # Get prioritized reading list
        priority = await analyze_library(operation="unread_priority")
        print(f"Total unread: {priority['total_unread']}")
        for book in priority["prioritized_books"][:5]:
            print(f"- {book['title']}")

        # Reading analytics
        stats = await analyze_library(operation="reading_stats")
        print(f"Books read: {stats['total_books_read']}")
        print(f"Average rating: {stats['average_rating']}")

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of the supported operations listed above
        - Database error: Verify library is accessible using manage_libraries(operation='list')

    See Also:
        - manage_tags(): For tag management operations
        - manage_books(): For book management operations
        - manage_libraries(): For library management
    """
    try:
        if operation == "tag_statistics":
            try:
                result = await get_tag_statistics_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="analyze_library",
                    context="Analyzing tag statistics",
                )

        elif operation == "duplicates":
            try:
                result = await find_duplicate_books_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="analyze_library",
                    context="Finding duplicate books",
                )

        elif operation == "series":
            try:
                result = await get_series_analysis_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="analyze_library",
                    context="Analyzing series completion",
                )

        elif operation == "health":
            try:
                result = await analyze_library_health_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="analyze_library",
                    context="Analyzing library health",
                )

        elif operation == "unread_priority":
            try:
                result = await unread_priority_list_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="analyze_library",
                    context="Getting prioritized unread books list",
                )

        elif operation == "reading_stats":
            try:
                result = await reading_statistics_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="analyze_library",
                    context="Getting reading statistics",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'tag_statistics', 'duplicates', 'series', 'health', "
                    "'unread_priority', 'reading_stats'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='tag_statistics' to analyze tag usage",
                    "Use operation='duplicates' to find duplicate books",
                    "Use operation='series' to analyze book series",
                    "Use operation='health' to check library health",
                    "Use operation='unread_priority' to prioritize unread books",
                    "Use operation='reading_stats' to get reading analytics",
                ],
                related_tools=["analyze_library"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={"operation": operation},
            tool_name="analyze_library",
            context="Library analysis operation",
        )

