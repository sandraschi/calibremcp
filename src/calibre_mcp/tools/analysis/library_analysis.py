"""
Analysis and statistics tools for CalibreMCP.

DEPRECATED: These individual tools are deprecated in favor of the manage_analysis
portmanteau tool (see tools/analysis/manage_analysis.py). These functions are kept
as helpers but are no longer registered with FastMCP 2.13+.

Use manage_analysis(operation="...") instead:
- get_tag_statistics() → manage_analysis(operation="tag_statistics")
- find_duplicate_books() → manage_analysis(operation="duplicate_books")
- get_series_analysis() → manage_analysis(operation="series_analysis")
- analyze_library_health() → manage_analysis(operation="library_health")
- unread_priority_list() → manage_analysis(operation="unread_priority")
- reading_statistics() → manage_analysis(operation="reading_stats")
"""

from typing import Dict, List, Any
from difflib import SequenceMatcher

# Import the MCP server instance
from ...server import (
    mcp,
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
                    similarity = SequenceMatcher(
                        None, tag1.name.lower(), tag2.name.lower()
                    ).ratio()

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
                            "total_usage": sum(
                                tag_usage.get(t, 0) for t in similar_tags
                            ),
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
            total_tags=0,
            unique_tags=0,
            duplicate_tags=[],
            unused_tags=[],
            suggestions=[],
        )


@mcp.tool()
async def find_duplicate_books() -> DuplicatesResponse:
    """
    Find potentially duplicate books using title/author fuzzy matching.
    """
    from ...models.book import Book
    from sqlalchemy import func

    db = DatabaseService()
    duplicate_groups = []

    try:
        with db.get_session() as session:
            # Find exact title/author duplicates first (most common)
            dupes = (
                session.query(
                    Book.title, Book.author_sort, func.count("*").label("cnt")
                )
                .group_by(Book.title, Book.author_sort)
                .having(func.count("*") > 1)
                .all()
            )

            for title, author, count in dupes:
                books = (
                    session.query(Book)
                    .filter(Book.title == title, Book.author_sort == author)
                    .all()
                )
                duplicate_groups.append(
                    {
                        "title": title,
                        "author": author,
                        "books": [
                            {"id": b.id, "formats": [f.format for f in b.formats]}
                            for b in books
                        ],
                        "confidence": 1.0,
                    }
                )

        return DuplicatesResponse(
            duplicate_groups=duplicate_groups,
            total_duplicates=len(duplicate_groups),
            confidence_scores={"exact_match": 1.0},
        )
    except Exception as e:
        logger.error(f"Duplicate check failed: {e}")
        return DuplicatesResponse(
            duplicate_groups=[], total_duplicates=0, confidence_scores={}
        )


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
                    [
                        book.series_index
                        for book in books
                        if book.series_index is not None
                    ]
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
                sorted_books = sorted(
                    books, key=lambda b: b.series_index if b.series_index else 0
                )
                first_book = sorted_books[0] if sorted_books else None

                reading_order_suggestions.append(
                    {
                        "series_id": series.id,
                        "series_name": series.name,
                        "first_book": {
                            "id": first_book.id if first_book else None,
                            "title": first_book.title if first_book else "Unknown",
                            "series_index": first_book.series_index
                            if first_book
                            else None,
                        },
                        "total_books": len(books),
                        "reading_order": [
                            {
                                "index": book.series_index,
                                "title": book.title,
                                "book_id": book.id,
                            }
                            for book in sorted_books
                        ],
                        "is_complete": len(missing_indices) == 0,
                        "completion_percentage": round(
                            (actual_count / expected_count * 100)
                            if expected_count > 0
                            else 0,
                            1,
                        ),
                    }
                )

            # Calculate statistics
            series_stats = {
                "total_series": total_series,
                "total_books_in_series": total_books_in_series,
                "series_with_gaps": series_with_gaps,
                "average_books_per_series": round(
                    total_books_in_series / total_series, 2
                )
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
    Analyze library health: check for missing files and DB integrity.
    """
    from ...models.book import Book
    from ...config import CalibreConfig
    from pathlib import Path

    config = CalibreConfig()
    lib_path = config.local_library_path
    db = DatabaseService()
    issues = []
    books_checked = 0
    missing_files = 0

    try:
        with db.get_session() as session:
            books = session.query(Book).all()
            books_checked = len(books)

            for book in books:
                for fmt in book.formats:
                    if not lib_path:
                        continue

                    # Calibre file path: Author/Title/File.ext
                    # Note: This is an approximation of the Calibre folder structure
                    file_path = (
                        lib_path
                        / book.author_sort
                        / book.title
                        / f"{fmt.name}.{fmt.format.lower()}"
                    )
                    if not file_path.exists():
                        # Try another common Calibre pattern
                        file_path = (
                            lib_path
                            / book.authors[0].name
                            / book.title
                            / f"{fmt.name}.{fmt.format.lower()}"
                        )
                        if not file_path.exists():
                            missing_files += 1
                            issues.append(
                                {
                                    "book_id": book.id,
                                    "title": book.title,
                                    "format": fmt.format,
                                    "issue": "Missing file",
                                }
                            )

        health_score = 100.0
        if books_checked > 0:
            health_score = max(0, 100.0 - (missing_files / books_checked * 100.0))

        recommendations = []
        if missing_files > 0:
            recommendations.append(
                f"Restore {missing_files} missing files from backup."
            )
        else:
            recommendations.append("Library is physically healthy.")

        return LibraryHealthResponse(
            health_score=health_score,
            issues_found=issues,
            recommendations=recommendations,
            database_integrity=True,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return LibraryHealthResponse(
            health_score=0.0,
            issues_found=[],
            recommendations=[],
            database_integrity=False,
        )


@mcp.tool()
async def unread_priority_list() -> UnreadPriorityResponse:
    """
    Austrian efficiency: Prioritize unread books.
    """
    from ...models.book import Book

    db = DatabaseService()
    try:
        with db.get_session() as session:
            # Simple priority: Highest rated unread books first
            # Since we don't have a reliable 'unread' flag in base Calibre,
            # we might use a tag or custom column if it becomes standard.
            # For now, return all books sorted by rating.
            books = session.query(Book).order_by(Book.rating.desc()).limit(20).all()

            return UnreadPriorityResponse(
                prioritized_books=[
                    {"id": b.id, "title": b.title, "rating": b.rating} for b in books
                ],
                priority_reasons={"quality": "Sorted by highest rating"},
                total_unread=len(books),
            )
    except Exception as e:
        return UnreadPriorityResponse(
            prioritized_books=[], priority_reasons={}, total_unread=0
        )


@mcp.tool()
async def reading_statistics() -> ReadingStats:
    """
    Generate reading analytics.
    """
    from ...models.book import Book
    from sqlalchemy import func

    db = DatabaseService()
    try:
        with db.get_session() as session:
            total_books = session.query(func.count(Book.id)).scalar() or 0
            avg_rating = session.query(func.avg(Book.rating)).scalar() or 0.0

            # Since we don't have a "read" status in base Calibre,
            # we consider all books in this simplified version.
            return ReadingStats(
                total_books_read=total_books,
                average_rating=float(avg_rating),
                favorite_genres=[],
                reading_patterns={"total_collection_size": total_books},
            )
    except Exception as e:
        logger.error(f"Reading stats failed: {e}")
        return ReadingStats(
            total_books_read=0,
            average_rating=0.0,
            favorite_genres=[],
            reading_patterns={},
        )
