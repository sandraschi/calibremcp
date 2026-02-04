"""
Specialized tools portmanteau for CalibreMCP.

Consolidates specialized library organization and recommendation operations.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Note: Response models (JapaneseBookOrganization, ITBookCuration, ReadingRecommendations)
# will be imported when operations are implemented

logger = get_logger("calibremcp.tools.specialized")


@mcp.tool()
async def manage_specialized(operation: str) -> dict[str, Any]:
    """
    Manage specialized library organization and recommendation operations in a single unified interface.

    This portmanteau tool consolidates specialized operations (Japanese book organization,
    IT book curation, and reading recommendations) into a single interface. Use the `operation`
    parameter to select which operation to perform.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 3 separate tools (one per specialized operation), this tool consolidates related
    specialized operations into a single interface. This design:
    - Prevents tool explosion (3 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with specialized tasks
    - Enables consistent interface across all specialized operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - japanese_organizer: Organize Japanese library for maximum cultural efficiency
    - it_curator: IT book curation for programming and technology collection
    - reading_recommendations: Austrian efficiency reading recommendations

    OPERATIONS DETAIL:

    japanese_organizer: Organize Japanese library
    - Categorizes manga series, light novels, language learning materials
    - Provides reading order recommendations for Japanese content
    - Returns: JapaneseBookOrganization with organized content and recommendations
    - Parameters: None (analyzes entire library)

    it_curator: IT book curation
    - Organizes by programming language
    - Identifies outdated books
    - Provides learning path recommendations for technology topics
    - Returns: ITBookCuration with organized content and learning recommendations
    - Parameters: None (analyzes entire library)

    reading_recommendations: Reading recommendations
    - Provides smart recommendations based on reading history, series progress, ratings
    - Eliminates decision paralysis with prioritized reading list
    - Optimizes reading satisfaction
    - Returns: ReadingRecommendations with personalized recommendations and reasoning
    - Parameters: None (analyzes entire library)

    Prerequisites:
        - Library must be accessible (auto-loaded on server startup)
        - Library must contain books for analysis

    Parameters:
        operation: The operation to perform. Must be one of:
            "japanese_organizer", "it_curator", "reading_recommendations"

    Returns:
        Dictionary containing operation-specific results:

        For operation="japanese_organizer":
            JapaneseBookOrganization: {
                "manga_series": List[Dict] - Organized manga series with reading order
                "light_novels": List[Dict] - Organized light novels
                "language_learning": List[Dict] - Language learning materials
                "recommendations": List[Dict] - Reading order recommendations
                ... (other organization fields)
            }

        For operation="it_curator":
            ITBookCuration: {
                "by_language": Dict[str, List[Dict]] - Books organized by programming language
                "outdated_books": List[Dict] - Books that may be outdated
                "learning_paths": List[Dict] - Recommended learning paths
                ... (other curation fields)
            }

        For operation="reading_recommendations":
            ReadingRecommendations: {
                "recommendations": List[Dict] - Prioritized reading recommendations
                "reasoning": str - Explanation of recommendations
                "factors_considered": List[str] - Factors used in recommendations
                ... (other recommendation fields)
            }

    Usage:
        # Organize Japanese library
        result = await manage_specialized(operation="japanese_organizer")

        # Get IT book curation
        result = await manage_specialized(operation="it_curator")

        # Get reading recommendations
        result = await manage_specialized(operation="reading_recommendations")

    Examples:
        # Get Japanese book organization
        japanese_org = await manage_specialized(operation="japanese_organizer")
        print(f"Found {len(japanese_org['manga_series'])} manga series")

        # Get IT book curation
        it_curation = await manage_specialized(operation="it_curator")
        print(f"Found {len(it_curation['by_language'])} programming languages")

        # Get reading recommendations
        recommendations = await manage_specialized(operation="reading_recommendations")
        print(f"Top recommendation: {recommendations['recommendations'][0]['title']}")

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "japanese_organizer", "it_curator", "reading_recommendations"
        - Library not accessible: Ensure library is loaded and accessible
        - No books found: Verify library contains books for analysis

    See Also:
        - query_books(): For finding books in the library
        - manage_libraries(): For library management operations
    """
    try:
        if operation == "japanese_organizer":
            try:
                # TODO: Implement Japanese book organization
                # This will be moved from server.py
                return {
                    "success": False,
                    "error": "Japanese book organizer not yet implemented",
                    "message": "Implementation will be moved from server.py",
                }
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_specialized",
                    context="Organizing Japanese library",
                )

        elif operation == "it_curator":
            try:
                # TODO: Implement IT book curation
                # This will be moved from server.py
                return {
                    "success": False,
                    "error": "IT book curator not yet implemented",
                    "message": "Implementation will be moved from server.py",
                }
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_specialized",
                    context="Curating IT books",
                )

        elif operation == "reading_recommendations":
            try:
                # TODO: Implement reading recommendations
                # This will be moved from server.py
                return {
                    "success": False,
                    "error": "Reading recommendations not yet implemented",
                    "message": "Implementation will be moved from server.py",
                }
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_specialized",
                    context="Generating reading recommendations",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'japanese_organizer', 'it_curator', 'reading_recommendations'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='japanese_organizer' to organize Japanese library",
                    "Use operation='it_curator' to curate IT books",
                    "Use operation='reading_recommendations' to get reading recommendations",
                ],
                related_tools=["manage_specialized"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={"operation": operation},
            tool_name="manage_specialized",
            context="Specialized operation",
        )
