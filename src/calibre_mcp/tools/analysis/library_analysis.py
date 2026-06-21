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

import sqlite3
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from ...logging_config import get_logger

# Import the MCP server instance
from ...server import (
    DuplicatesResponse,
    LibraryHealthResponse,
    ReadingStats,
    SeriesAnalysisResponse,
    TagStatsResponse,
    UnreadPriorityResponse,
    mcp,
)

logger = get_logger("calibremcp.tools.library_analysis")


def _get_metadata_db() -> Path | None:
    """Return path to the active library's metadata.db, or None if not found."""
    from ...config import CalibreConfig
    from ...utils.library_utils import discover_calibre_libraries

    config = CalibreConfig()
    lib_path = config.local_library_path
    if not lib_path:
        discovered = discover_calibre_libraries()
        if discovered:
            lib_path = next(iter(discovered.values()))
    if lib_path and (lib_path / "metadata.db").exists():
        return lib_path / "metadata.db"
    return None


def _open_db() -> sqlite3.Connection | None:
    """Open the active metadata.db read-only. Returns None if not found."""
    db_path = _get_metadata_db()
    if not db_path:
        return None
    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
async def get_tag_statistics() -> TagStatsResponse:
    """
    Analyze tag usage and suggest cleanup operations.

    Identifies duplicate tags (similar names), unused tags,
    and provides suggestions for tag consolidation and organization.
    """
    try:
        conn = _open_db()
        if conn is None:
            return TagStatsResponse(total_tags=0, unique_tags=0, duplicate_tags=[], unused_tags=[], suggestions=[])
        try:
            rows = conn.execute(
                "SELECT t.id, t.name, COUNT(btl.book) AS book_count "
                "FROM tags t LEFT JOIN books_tags_link btl ON btl.tag = t.id "
                "GROUP BY t.id, t.name ORDER BY t.name"
            ).fetchall()
        finally:
            conn.close()

        tag_usage: dict[str, int] = {r["name"]: r["book_count"] for r in rows}
        unused_tags = [name for name, cnt in tag_usage.items() if cnt == 0]
        tag_names = list(tag_usage.keys())
        total_tags = len(tag_names)

        duplicate_groups: list[dict[str, Any]] = []
        processed: set[str] = set()
        similarity_threshold = 0.85

        for i, t1 in enumerate(tag_names):
            if t1 in processed:
                continue
            similar = [t1]
            for t2 in tag_names[i + 1:]:
                if t2 in processed:
                    continue
                if SequenceMatcher(None, t1.lower(), t2.lower()).ratio() >= similarity_threshold:
                    similar.append(t2)
                    processed.add(t2)
            if len(similar) > 1:
                similar.sort(key=lambda t: tag_usage.get(t, 0), reverse=True)
                duplicate_groups.append({
                    "tags": similar,
                    "similarity_score": similarity_threshold,
                    "recommended": similar[0],
                    "total_usage": sum(tag_usage.get(t, 0) for t in similar),
                })
                processed.add(t1)

        suggestions: list[dict[str, Any]] = []
        for grp in duplicate_groups:
            suggestions.append({
                "type": "merge_tags",
                "description": f"Merge {', '.join(grp['tags'][1:])} into '{grp['recommended']}'",
                "tags_to_merge": grp["tags"][1:],
                "target_tag": grp["recommended"],
                "potential_books_affected": grp["total_usage"],
            })
        if unused_tags:
            suggestions.append({
                "type": "remove_unused",
                "description": f"Remove {len(unused_tags)} unused tags",
                "tags": unused_tags[:10],
                "total_count": len(unused_tags),
            })

        return TagStatsResponse(
            total_tags=total_tags,
            unique_tags=total_tags,
            duplicate_tags=duplicate_groups,
            unused_tags=unused_tags,
            suggestions=suggestions,
        )
    except Exception as e:
        logger.error(f"Error getting tag statistics: {e}", exc_info=True)
        return TagStatsResponse(total_tags=0, unique_tags=0, duplicate_tags=[], unused_tags=[], suggestions=[])


@mcp.tool()
async def find_duplicate_books() -> DuplicatesResponse:
    """
    Find potentially duplicate books using title/author matching.
    """
    try:
        conn = _open_db()
        if conn is None:
            return DuplicatesResponse(duplicate_groups=[], total_duplicates=0, confidence_scores={})
        try:
            # Exact title+author_sort duplicates
            dupes = conn.execute(
                "SELECT b.title, b.author_sort, COUNT(*) as cnt "
                "FROM books b GROUP BY b.title, b.author_sort HAVING cnt > 1"
            ).fetchall()

            duplicate_groups: list[dict[str, Any]] = []
            for row in dupes:
                title, author, _ = row["title"], row["author_sort"], row["cnt"]
                books = conn.execute(
                    "SELECT b.id, b.title, GROUP_CONCAT(d.format) as formats "
                    "FROM books b LEFT JOIN data d ON d.book = b.id "
                    "WHERE b.title = ? AND b.author_sort = ? GROUP BY b.id",
                    (title, author),
                ).fetchall()
                duplicate_groups.append({
                    "title": title,
                    "author": author,
                    "books": [
                        {"id": b["id"], "formats": (b["formats"] or "").split(",") if b["formats"] else []}
                        for b in books
                    ],
                    "confidence": 1.0,
                })
        finally:
            conn.close()

        return DuplicatesResponse(
            duplicate_groups=duplicate_groups,
            total_duplicates=len(duplicate_groups),
            confidence_scores={"exact_match": 1.0},
        )
    except Exception as e:
        logger.exception(f"Duplicate check failed: {e}")
        return DuplicatesResponse(duplicate_groups=[], total_duplicates=0, confidence_scores={})


@mcp.tool()
async def get_series_analysis() -> SeriesAnalysisResponse:
    """
    Analyze book series completion and provide reading order recommendations.
    """
    try:
        conn = _open_db()
        if conn is None:
            return SeriesAnalysisResponse(incomplete_series=[], reading_order_suggestions=[], series_statistics={})
        try:
            series_rows = conn.execute("SELECT id, name, sort FROM series ORDER BY name").fetchall()
            incomplete_series: list[dict[str, Any]] = []
            reading_order_suggestions: list[dict[str, Any]] = []
            total_books_in_series = 0
            series_with_gaps = 0

            for s in series_rows:
                books = conn.execute(
                    "SELECT b.id, b.title, b.series_index "
                    "FROM books b JOIN books_series_link bsl ON bsl.book = b.id "
                    "WHERE bsl.series = ? ORDER BY b.series_index",
                    (s["id"],),
                ).fetchall()
                if not books:
                    continue
                total_books_in_series += len(books)
                indices = sorted([b["series_index"] for b in books if b["series_index"] is not None])
                if not indices:
                    continue

                min_idx, max_idx = indices[0], indices[-1]
                expected = int(max_idx) - int(min_idx) + 1
                actual = len(indices)
                missing_indices: list[int] = []

                if actual < expected:
                    series_with_gaps += 1
                    present = {int(i) for i in indices}
                    missing_indices = sorted(set(range(int(min_idx), int(max_idx) + 1)) - present)

                    gap_ranges: list[str] = []
                    if missing_indices:
                        gs = ge = missing_indices[0]
                        for mi in missing_indices[1:]:
                            if mi == ge + 1:
                                ge = mi
                            else:
                                gap_ranges.append(f"#{gs}" if gs == ge else f"#{gs}-#{ge}")
                                gs = ge = mi
                        gap_ranges.append(f"#{gs}" if gs == ge else f"#{gs}-#{ge}")

                    incomplete_series.append({
                        "series_id": s["id"],
                        "name": s["name"],
                        "book_count": actual,
                        "expected_count": expected,
                        "missing_count": len(missing_indices),
                        "missing_indices": missing_indices,
                        "gap_description": ", ".join(gap_ranges) if gap_ranges else f"Missing {len(missing_indices)} volumes",
                        "first_index": min_idx,
                        "last_index": max_idx,
                    })

                first = books[0]
                reading_order_suggestions.append({
                    "series_id": s["id"],
                    "series_name": s["name"],
                    "first_book": {"id": first["id"], "title": first["title"], "series_index": first["series_index"]},
                    "total_books": len(books),
                    "reading_order": [{"index": b["series_index"], "title": b["title"], "book_id": b["id"]} for b in books],
                    "is_complete": len(missing_indices) == 0,
                    "completion_percentage": round(actual / expected * 100, 1) if expected > 0 else 0,
                })
        finally:
            conn.close()

        total_series = len(series_rows)
        return SeriesAnalysisResponse(
            incomplete_series=incomplete_series,
            reading_order_suggestions=reading_order_suggestions,
            series_statistics={
                "total_series": total_series,
                "total_books_in_series": total_books_in_series,
                "series_with_gaps": series_with_gaps,
                "average_books_per_series": round(total_books_in_series / total_series, 2) if total_series else 0,
                "complete_series_count": total_series - series_with_gaps,
                "incomplete_series_count": series_with_gaps,
            },
        )
    except Exception as e:
        logger.error(f"Error getting series analysis: {e}", exc_info=True)
        return SeriesAnalysisResponse(
            incomplete_series=[],
            reading_order_suggestions=[],
            series_statistics={"total_series": 0, "total_books_in_series": 0, "series_with_gaps": 0,
                               "average_books_per_series": 0, "complete_series_count": 0, "incomplete_series_count": 0},
        )


@mcp.tool()
async def analyze_library_health() -> LibraryHealthResponse:
    """
    Analyze library health: check for missing files and DB integrity.
    """
    from ...config import CalibreConfig
    from ...utils.library_utils import discover_calibre_libraries

    config = CalibreConfig()
    lib_path = config.local_library_path
    if not lib_path:
        discovered = discover_calibre_libraries()
        if discovered:
            lib_path = next(iter(discovered.values()))

    if not lib_path or not lib_path.exists():
        return LibraryHealthResponse(
            health_score=0.0,
            issues_found=[{"issue": "No library path found — check CALIBRE_BASE_PATH or CALIBRE_LIBRARY_PATH"}],
            recommendations=["Set CALIBRE_BASE_PATH or CALIBRE_LIBRARY_PATH to your Calibre library location."],
            database_integrity=False,
        )

    metadata_db = lib_path / "metadata.db"
    if not metadata_db.exists():
        return LibraryHealthResponse(
            health_score=0.0,
            issues_found=[{"issue": f"metadata.db not found at {metadata_db}"}],
            recommendations=["Verify the library path points to a valid Calibre library."],
            database_integrity=False,
        )

    issues: list[dict[str, Any]] = []
    missing_files = 0
    db_integrity_ok = False

    try:
        conn = sqlite3.connect(str(metadata_db), timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            db_integrity_ok = (integrity == "ok")
            if not db_integrity_ok:
                issues.append({"issue": f"Database integrity check failed: {integrity}"})

            rows = conn.execute(
                "SELECT b.id, b.title, b.path, d.name, d.format "
                "FROM books b JOIN data d ON d.book = b.id"
            ).fetchall()
            books_checked_ids: set[int] = set()
            for row in rows:
                book_id, title, book_path, fname, fmt = row["id"], row["title"], row["path"], row["name"], row["format"]
                books_checked_ids.add(book_id)
                file_path = lib_path / book_path / f"{fname}.{fmt.lower()}"
                if not file_path.exists():
                    missing_files += 1
                    issues.append({"book_id": book_id, "title": title, "format": fmt, "issue": "Missing file"})
            books_checked = len(books_checked_ids)
        finally:
            conn.close()

        health_score = 100.0
        if books_checked > 0:
            health_score = max(0.0, 100.0 - (missing_files / books_checked * 100.0))
        if not db_integrity_ok:
            health_score = min(health_score, 50.0)

        recommendations: list[str] = []
        if missing_files > 0:
            recommendations.append(f"Restore {missing_files} missing book file(s) from backup.")
        if not db_integrity_ok:
            recommendations.append("Run 'calibredb check_library' to repair database integrity.")
        if not issues:
            recommendations.append("Library is healthy — all files present and database intact.")

        return LibraryHealthResponse(
            health_score=health_score,
            issues_found=issues[:50],
            recommendations=recommendations,
            database_integrity=db_integrity_ok,
        )
    except Exception as e:
        logger.exception(f"Health check failed: {e}")
        return LibraryHealthResponse(
            health_score=0.0,
            issues_found=[{"issue": f"Health check error: {e}"}],
            recommendations=["Check server logs for details."],
            database_integrity=False,
        )


@mcp.tool()
async def unread_priority_list() -> UnreadPriorityResponse:
    """
    Austrian efficiency: Prioritize unread books by rating.
    """
    try:
        conn = _open_db()
        if conn is None:
            return UnreadPriorityResponse(prioritized_books=[], priority_reasons={}, total_unread=0)
        try:
            rows = conn.execute(
                "SELECT b.id, b.title, r.rating "
                "FROM books b LEFT JOIN ratings r ON r.id = ("
                "  SELECT book_ratings_link.rating FROM books_ratings_link book_ratings_link "
                "  WHERE book_ratings_link.book = b.id LIMIT 1"
                ") ORDER BY r.rating DESC NULLS LAST LIMIT 20"
            ).fetchall()
        finally:
            conn.close()

        return UnreadPriorityResponse(
            prioritized_books=[{"id": r["id"], "title": r["title"], "rating": r["rating"]} for r in rows],
            priority_reasons={"quality": "Sorted by highest rating"},
            total_unread=len(rows),
        )
    except Exception:
        return UnreadPriorityResponse(prioritized_books=[], priority_reasons={}, total_unread=0)


@mcp.tool()
async def reading_statistics() -> ReadingStats:
    """
    Generate reading analytics.
    """
    try:
        conn = _open_db()
        if conn is None:
            return ReadingStats(total_books_read=0, average_rating=0.0, favorite_genres=[], reading_patterns={})
        try:
            total_books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] or 0
            rated_row = conn.execute(
                "SELECT COUNT(*), AVG(r.rating) FROM ratings r "
                "JOIN books_ratings_link brl ON brl.rating = r.id "
                "WHERE r.rating > 0"
            ).fetchone()
            rated_count = int(rated_row[0] or 0)
            # Calibre stores ratings as 0-10 (multiples of 2); divide by 2 for 0-5 star scale
            avg_rating_raw = float(rated_row[1] or 0.0)
            avg_rating_stars = round(avg_rating_raw / 2.0, 2) if rated_count > 0 else 0.0
        finally:
            conn.close()

        return ReadingStats(
            # Note: Calibre has no explicit 'read' tracking; total_books_read = library size
            total_books_read=total_books,
            # average_rating is on the 0–5 star scale (Calibre stores 0–10 internally)
            average_rating=avg_rating_stars,
            favorite_genres=[],
            reading_patterns={
                "total_collection_size": total_books,
                "rated_books_count": rated_count,
                "note": (
                    "total_books_read = total library size (Calibre has no read/unread tracking). "
                    "average_rating is on a 0-5 star scale, computed over rated books only."
                ),
            },
        )
    except Exception as e:
        logger.exception(f"Reading stats failed: {e}")
        return ReadingStats(total_books_read=0, average_rating=0.0, favorite_genres=[], reading_patterns={})
