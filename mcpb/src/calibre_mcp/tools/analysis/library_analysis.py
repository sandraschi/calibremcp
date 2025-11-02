"""
Analysis and statistics tools for CalibreMCP.

These tools provide comprehensive analytics, health checks, and
statistical analysis of Calibre libraries and reading patterns.
"""

from typing import Dict, List, Any
from difflib import SequenceMatcher

# Import the MCP server instance
from ...server import mcp

# Import response models
from ...server import (
    TagStatsResponse,
    DuplicatesResponse,
    SeriesAnalysisResponse,
    LibraryHealthResponse,
    UnreadPriorityResponse,
    ReadingStats,
)

# Import services and models
from ...db.database import DatabaseService
from ...models.tag import Tag
from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.library_analysis")


@mcp.tool()
async def get_tag_statistics() -> TagStatsResponse:
    """
    Analyze tag usage and suggest cleanup operations.

    Identifies duplicate tags (similar names), unused tags,
    and provides suggestions for tag consolidation and organization.
    Helps maintain a clean and organized tag structure.

    Returns:
        TagStatsResponse containing:
        {
            "total_tags": int - Total number of unique tags
            "unique_tags": int - Number of distinct tags (same as total_tags)
            "duplicate_tags": List[Dict] - Groups of potentially duplicate tags with similarity scores
            "unused_tags": List[str] - Tags that are not assigned to any books
            "suggestions": List[Dict] - Recommended tag consolidation actions
        }

    Example:
        # Get tag statistics
        stats = get_tag_statistics()
        print(f"Total tags: {stats['total_tags']}")
        print(f"Unused tags: {len(stats['unused_tags'])}")

        # Review duplicate suggestions
        for dup_group in stats['duplicate_tags']:
            print(f"Similar tags: {dup_group['tags']}")
    """
    db = DatabaseService()

    try:
        with db.get_session() as session:
            # Get all tags with book counts
            tags = (
                session.query(Tag)
                .options(
                    # Load books relationship to count
                )
                .all()
            )

            total_tags = len(tags)
            unused_tags: List[str] = []
            tag_usage: Dict[str, int] = {}

            # Count usage for each tag
            for tag in tags:
                book_count = len(tag.books) if hasattr(tag, "books") else 0
                tag_usage[tag.name] = book_count
                if book_count == 0:
                    unused_tags.append(tag.name)

            # Find duplicate/similar tags using similarity matching
            duplicate_groups: List[Dict[str, Any]] = []
            processed = set()
            similarity_threshold = 0.85  # 85% similarity

            [tag.name for tag in tags]

            for i, tag1 in enumerate(tags):
                if tag1.name in processed:
                    continue

                similar_tags = [tag1.name]

                for j, tag2 in enumerate(tags[i + 1 :], start=i + 1):
                    if tag2.name in processed:
                        continue

                    # Calculate similarity (case-insensitive)
                    similarity = SequenceMatcher(None, tag1.name.lower(), tag2.name.lower()).ratio()

                    if similarity >= similarity_threshold:
                        similar_tags.append(tag2.name)
                        processed.add(tag2.name)

                if len(similar_tags) > 1:
                    # Sort by usage (most used first)
                    similar_tags.sort(key=lambda t: tag_usage.get(t, 0), reverse=True)
                    duplicate_groups.append(
                        {
                            "tags": similar_tags,
                            "similarity_score": similarity_threshold,
                            "recommended": similar_tags[0],  # Use most popular
                            "total_usage": sum(tag_usage.get(t, 0) for t in similar_tags),
                        }
                    )
                    processed.add(tag1.name)

            # Generate suggestions
            suggestions: List[Dict[str, Any]] = []

            # Suggest merging duplicate tags
            for dup_group in duplicate_groups:
                if len(dup_group["tags"]) > 1:
                    suggestions.append(
                        {
                            "type": "merge_tags",
                            "description": f"Merge {', '.join(dup_group['tags'][1:])} into '{dup_group['recommended']}'",
                            "tags_to_merge": dup_group["tags"][1:],
                            "target_tag": dup_group["recommended"],
                            "potential_books_affected": dup_group["total_usage"],
                        }
                    )

            # Suggest removing unused tags
            if unused_tags:
                suggestions.append(
                    {
                        "type": "remove_unused",
                        "description": f"Remove {len(unused_tags)} unused tags",
                        "tags": unused_tags[:10],  # Show first 10
                        "total_count": len(unused_tags),
                    }
                )

            return TagStatsResponse(
                total_tags=total_tags,
                unique_tags=total_tags,
                duplicate_tags=duplicate_groups,
                unused_tags=unused_tags,
                suggestions=suggestions,
            )

    except Exception as e:
        logger.error(f"Error getting tag statistics: {e}", exc_info=True)
        # Return empty result on error
        return TagStatsResponse(
            total_tags=0, unique_tags=0, duplicate_tags=[], unused_tags=[], suggestions=[]
        )


@mcp.tool()
async def find_duplicate_books() -> DuplicatesResponse:
    """
    Find potentially duplicate books within and across libraries.

    Uses title similarity, author matching, and ISBN comparison
    to identify potential duplicates for cleanup and organization.

    Returns:
        DuplicatesResponse: List of potential duplicate book groups
    """
    # Implementation will be moved from server.py
    pass


@mcp.tool()
async def get_series_analysis() -> SeriesAnalysisResponse:
    """
    Analyze book series completion and provide reading order recommendations.

    Identifies incomplete series (missing volumes), calculates series statistics,
    and suggests optimal reading order based on series_index (volume numbers).
    Helps track series progress and plan reading.

    Returns:
        SeriesAnalysisResponse containing:
        {
            "incomplete_series": List[Dict] - Series with missing volumes or gaps
            "reading_order_suggestions": List[Dict] - Recommended reading order for series
            "series_statistics": Dict - Overall statistics about all series
        }

    Example:
        # Analyze series
        analysis = get_series_analysis()

        # Check incomplete series
        for series in analysis['incomplete_series']:
            print(f"{series['name']}: {series['missing_indices']} missing volumes")

        # Get reading suggestions
        for suggestion in analysis['reading_order_suggestions']:
            print(f"{suggestion['series_name']}: Start with {suggestion['first_book']}")
    """
    from ...models.series import Series
    from sqlalchemy.orm import joinedload

    db = DatabaseService()

    try:
        with db.get_session() as session:
            # Get all series with their books
            series_list = session.query(Series).options(joinedload(Series.books)).all()

            incomplete_series: List[Dict[str, Any]] = []
            reading_order_suggestions: List[Dict[str, Any]] = []

            total_series = len(series_list)
            total_books_in_series = 0
            series_with_gaps = 0

            for series in series_list:
                if not hasattr(series, "books") or not series.books:
                    continue

                books = series.books
                total_books_in_series += len(books)

                # Get series_index values
                indices = sorted(
                    [book.series_index for book in books if book.series_index is not None]
                )

                if not indices:
                    continue

                # Check for gaps in series
                min_index = indices[0]
                max_index = indices[-1]
                expected_count = int(max_index) - int(min_index) + 1
                actual_count = len(indices)

                missing_indices = []
                gap_ranges = []

                # Check for gaps (missing volumes)
                if actual_count < expected_count:
                    series_with_gaps += 1
                    complete_range = set(range(int(min_index), int(max_index) + 1))
                    present_indices = set(int(idx) for idx in indices)
                    missing_indices = sorted(complete_range - present_indices)

                    # Find gap ranges (consecutive missing indices)
                    if missing_indices:
                        gap_start = missing_indices[0]
                        gap_end = gap_start

                        for i in range(1, len(missing_indices)):
                            if missing_indices[i] == gap_end + 1:
                                gap_end = missing_indices[i]
                            else:
                                if gap_start == gap_end:
                                    gap_ranges.append(f"#{gap_start}")
                                else:
                                    gap_ranges.append(f"#{gap_start}-#{gap_end}")
                                gap_start = gap_end = missing_indices[i]

                        # Add final gap
                        if gap_start == gap_end:
                            gap_ranges.append(f"#{gap_start}")
                        else:
                            gap_ranges.append(f"#{gap_start}-#{gap_end}")

                # Add to incomplete if there are gaps
                if missing_indices:
                    incomplete_series.append(
                        {
                            "series_id": series.id,
                            "name": series.name,
                            "book_count": len(books),
                            "expected_count": expected_count,
                            "missing_count": len(missing_indices),
                            "missing_indices": [int(idx) for idx in missing_indices],
                            "gap_description": ", ".join(gap_ranges)
                            if gap_ranges
                            else f"Missing {len(missing_indices)} volumes",
                            "first_index": min_index,
                            "last_index": max_index,
                        }
                    )

                # Generate reading order suggestion
                # Sort books by series_index
                sorted_books = sorted(books, key=lambda b: b.series_index if b.series_index else 0)
                first_book = sorted_books[0] if sorted_books else None

                reading_order_suggestions.append(
                    {
                        "series_id": series.id,
                        "series_name": series.name,
                        "first_book": {
                            "id": first_book.id if first_book else None,
                            "title": first_book.title if first_book else "Unknown",
                            "series_index": first_book.series_index if first_book else None,
                        },
                        "total_books": len(books),
                        "reading_order": [
                            {"index": book.series_index, "title": book.title, "book_id": book.id}
                            for book in sorted_books
                        ],
                        "is_complete": len(missing_indices) == 0,
                        "completion_percentage": round(
                            (actual_count / expected_count * 100) if expected_count > 0 else 0, 1
                        ),
                    }
                )

            # Calculate statistics
            series_stats = {
                "total_series": total_series,
                "total_books_in_series": total_books_in_series,
                "series_with_gaps": series_with_gaps,
                "average_books_per_series": round(total_books_in_series / total_series, 2)
                if total_series > 0
                else 0,
                "complete_series_count": total_series - series_with_gaps,
                "incomplete_series_count": series_with_gaps,
            }

            return SeriesAnalysisResponse(
                incomplete_series=incomplete_series,
                reading_order_suggestions=reading_order_suggestions,
                series_statistics=series_stats,
            )

    except Exception as e:
        logger.error(f"Error getting series analysis: {e}", exc_info=True)
        # Return empty result on error
        return SeriesAnalysisResponse(
            incomplete_series=[],
            reading_order_suggestions=[],
            series_statistics={
                "total_series": 0,
                "total_books_in_series": 0,
                "series_with_gaps": 0,
                "average_books_per_series": 0,
                "complete_series_count": 0,
                "incomplete_series_count": 0,
            },
        )


@mcp.tool()
async def analyze_library_health() -> LibraryHealthResponse:
    """
    Perform comprehensive library health check and database integrity analysis.

    Checks for missing files, corrupted metadata, orphaned records,
    and provides recommendations for library maintenance and optimization.

    Returns:
        LibraryHealthResponse: Health check results and maintenance recommendations
    """
    # Implementation will be moved from server.py
    pass


@mcp.tool()
async def unread_priority_list() -> UnreadPriorityResponse:
    """
    Austrian efficiency: Prioritize unread books to eliminate decision paralysis.

    Uses rating, series status, purchase date, and tags to create
    a prioritized reading list that maximizes reading satisfaction.

    Returns:
        UnreadPriorityResponse: Prioritized list of unread books with reasoning
    """
    # Implementation will be moved from server.py
    pass


@mcp.tool()
async def reading_statistics() -> ReadingStats:
    """
    Generate personal reading analytics from library database.

    Analyzes reading patterns, completion rates, genre preferences,
    and provides insights into reading habits and preferences.

    Returns:
        ReadingStats: Comprehensive reading analytics and insights
    """
    # Implementation will be moved from server.py
    pass
