"""
Specialized tools for CalibreMCP.

DEPRECATED: This module is deprecated in favor of the manage_specialized portmanteau tool
(see tools/specialized/manage_specialized.py). Individual tools are kept for backward
compatibility but are no longer registered with FastMCP 2.13+.

Use manage_specialized(operation="...") instead of individual tools:
- japanese_book_organizer() → manage_specialized(operation="japanese_organizer")
- it_book_curator() → manage_specialized(operation="it_curator")
- reading_recommendations() → manage_specialized(operation="reading_recommendations")
"""

# NOTE: @mcp.tool() decorators removed - use manage_specialized portmanteau tool instead

# Import response models (for type hints)
from ...server import JapaneseBookOrganization, ITBookCuration, ReadingRecommendations

# NOTE: These functions are NOT registered as tools (no @mcp.tool() decorator)
# They are kept for reference but should not be used directly


async def japanese_book_organizer_helper() -> JapaneseBookOrganization:
    """
    Weeb optimization - Organize Japanese library for maximum cultural efficiency.

    Categorizes manga series, light novels, language learning materials,
    and provides reading order recommendations for Japanese content.

    Returns:
        JapaneseBookOrganization: Organized Japanese content with reading recommendations
    """
    # Implementation will be moved from server.py
    pass


async def it_book_curator_helper() -> ITBookCuration:
    """
    IT book curation for Sandra's programming and technology collection.

    Organizes by programming language, identifies outdated books,
    and provides learning path recommendations for technology topics.

    Returns:
        ITBookCuration: Organized IT content with learning recommendations
    """
    # Implementation will be moved from server.py
    pass


async def reading_recommendations_helper() -> ReadingRecommendations:
    """
    Austrian efficiency reading recommendations - eliminate decision paralysis.

    Provides smart recommendations based on reading history, series progress,
    ratings, and personal preferences to optimize reading satisfaction.

    Returns:
        ReadingRecommendations: Personalized reading recommendations with reasoning
    """
    # Implementation will be moved from server.py
    pass
