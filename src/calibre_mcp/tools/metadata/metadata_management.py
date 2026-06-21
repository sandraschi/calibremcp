"""
DEPRECATED: Individual metadata tools are deprecated in favor of the manage_metadata
portmanteau tool (see tools/metadata/manage_metadata.py). These functions are kept
as helpers but are no longer registered with FastMCP 2.13+.

Use manage_metadata(operation="...") instead:
- update_book_metadata() → manage_metadata(operation="update", updates=...)
- auto_organize_tags() → manage_metadata(operation="organize_tags")
- fix_metadata_issues() → manage_metadata(operation="fix_issues")
"""

from datetime import datetime
from typing import Any

from ...db.models import Author, Series, Tag
from ...logging_config import get_logger

# Import the MCP server instance
# Import response models
from ...server import MetadataUpdateRequest, MetadataUpdateResponse, TagStatsResponse

# Import services
from ...services.book_service import book_service

logger = get_logger("calibremcp.tools.metadata_management")

# Fields that calibredb set_metadata supports (via update_book_helper).
# Any field NOT in this set will be reported as failed rather than silently dropped.
_CALIBREDB_FIELDS = frozenset({
    "title", "authors", "author", "author_ids",
    "tags", "tag_ids",
    "series", "series_id", "series_index",
    "publisher",
    "rating",
    "isbn",
    "languages",
    "comments",
    "pubdate",
})


# NOTE: @mcp.tool() decorator removed - use manage_metadata portmanteau tool instead
async def update_book_metadata_helper(
    updates: list[MetadataUpdateRequest],
) -> MetadataUpdateResponse:
    """
    Update metadata for single or multiple books.

    Allows bulk updates to book metadata including title, author,
    publication date, tags, and other bibliographic information.
    Each update request specifies a book ID, field name, and new value.

    Args:
        updates: List of metadata update requests, where each request contains:
            - book_id: ID of the book to update
            - field: Name of the field to update (e.g., "title", "series_index", "tag_ids")
            - value: New value for the field (type depends on field)

    Returns:
        MetadataUpdateResponse containing:
        {
            "updated_books": List[int] - IDs of successfully updated books
            "failed_updates": List[Dict] - Failed updates with error details
            "success_count": int - Number of successful updates
        }

    Example:
        # Update a book's title
        result = update_book_metadata([
            {"book_id": 123, "field": "title", "value": "New Title"}
        ])

        # Update multiple fields for one book
        result = update_book_metadata([
            {"book_id": 123, "field": "title", "value": "New Title"},
            {"book_id": 123, "field": "series_index", "value": 2.0},
            {"book_id": 123, "field": "rating", "value": 5}
        ])

        # Bulk update multiple books
        result = update_book_metadata([
            {"book_id": 123, "field": "tag_ids", "value": [1, 2, 3]},
            {"book_id": 124, "field": "tag_ids", "value": [1, 2, 3]},
            {"book_id": 125, "field": "tag_ids", "value": [1, 2, 3]}
        ])
    """
    updated_books: list[int] = []
    failed_updates: list[dict[str, Any]] = []

    from ..book_management.update_book import update_book_helper
    from ..shared.db_init import ensure_db_initialized

    db_err = ensure_db_initialized()
    if db_err:
        return MetadataUpdateResponse(
            updated_books=[],
            failed_updates=[{"error": db_err}],
            success_count=0,
        )

    # Per-book accumulators: metadata dict (for calibredb) and per-field failure tracking.
    updates_by_book: dict[int, dict[str, Any]] = {}
    # Track which original field names each book_id received, for error messages.
    fields_by_book: dict[int, list[str]] = {}

    for update in updates:
        book_id = update.book_id
        field = update.field
        value = update.value

        if book_id not in updates_by_book:
            updates_by_book[book_id] = {}
            fields_by_book[book_id] = []

        fields_by_book[book_id].append(field)

        # --- Reject unknown fields immediately so they never count as success ---
        if field not in _CALIBREDB_FIELDS:
            failed_updates.append({
                "book_id": book_id,
                "field": field,
                "error": (
                    f"Unsupported field '{field}'. "
                    f"Supported fields: {sorted(_CALIBREDB_FIELDS)}"
                ),
            })
            continue

        # --- Normalize field names into the metadata dict update_book_helper expects ---

        # author / authors by name (string or list of strings)
        if field in ("author", "authors"):
            if isinstance(value, list):
                authors_list = [str(v).strip() for v in value if str(v).strip()]
            elif isinstance(value, str):
                # Allow comma-separated or single name
                authors_list = [v.strip() for v in value.split("&") if v.strip()] or [value.strip()]
            else:
                failed_updates.append({
                    "book_id": book_id,
                    "field": field,
                    "error": f"authors value must be a string or list of strings, got {type(value).__name__}",
                })
                continue
            updates_by_book[book_id]["authors"] = authors_list

        # author_ids — resolve IDs to names via DB so calibredb can accept them
        elif field == "author_ids":
            if not isinstance(value, list):
                failed_updates.append({
                    "book_id": book_id,
                    "field": field,
                    "error": "author_ids must be a list of integer author IDs",
                })
                continue
            try:
                session = book_service.db.session
                db_authors = session.query(Author).filter(Author.id.in_(value)).all()
                found_ids = {a.id for a in db_authors}
                missing = {int(v) for v in value} - found_ids
                if missing:
                    failed_updates.append({
                        "book_id": book_id,
                        "field": field,
                        "error": f"Author IDs not found in library: {sorted(missing)}",
                    })
                    continue
                updates_by_book[book_id]["authors"] = [a.name for a in db_authors]
            except Exception as e:
                failed_updates.append({
                    "book_id": book_id,
                    "field": field,
                    "error": f"Failed to resolve author IDs: {e}",
                })
                continue

        # tags by name (string or list)
        elif field == "tags":
            if isinstance(value, list):
                tags_list = [str(v).strip() for v in value if str(v).strip()]
            elif isinstance(value, str):
                tags_list = [v.strip() for v in value.split(",") if v.strip()]
            else:
                failed_updates.append({
                    "book_id": book_id,
                    "field": field,
                    "error": f"tags value must be a string or list of strings, got {type(value).__name__}",
                })
                continue
            updates_by_book[book_id]["tags"] = tags_list

        # tag_ids — resolve to names
        elif field == "tag_ids":
            if not isinstance(value, list):
                failed_updates.append({
                    "book_id": book_id,
                    "field": field,
                    "error": "tag_ids must be a list of integer tag IDs",
                })
                continue
            try:
                session = book_service.db.session
                db_tags = session.query(Tag).filter(Tag.id.in_(value)).all()
                found_ids = {t.id for t in db_tags}
                missing = {int(v) for v in value} - found_ids
                if missing:
                    failed_updates.append({
                        "book_id": book_id,
                        "field": field,
                        "error": f"Tag IDs not found in library: {sorted(missing)}",
                    })
                    continue
                updates_by_book[book_id]["tags"] = [t.name for t in db_tags]
            except Exception as e:
                failed_updates.append({
                    "book_id": book_id,
                    "field": field,
                    "error": f"Failed to resolve tag IDs: {e}",
                })
                continue

        # series_id — resolve to series name
        elif field == "series_id":
            if value is None:
                updates_by_book[book_id]["series"] = ""
            else:
                try:
                    session = book_service.db.session
                    db_series = session.query(Series).get(value)
                    if not db_series:
                        failed_updates.append({
                            "book_id": book_id,
                            "field": field,
                            "error": f"Series ID {value} not found in library",
                        })
                        continue
                    updates_by_book[book_id]["series"] = db_series.name
                except Exception as e:
                    failed_updates.append({
                        "book_id": book_id,
                        "field": field,
                        "error": f"Failed to resolve series ID: {e}",
                    })
                    continue

        # rating — validate range (calibredb uses 0-10 internally but we accept 1-5)
        elif field == "rating":
            if value is not None and (not isinstance(value, (int, float)) or value < 0 or value > 5):
                failed_updates.append({
                    "book_id": book_id,
                    "field": field,
                    "error": f"Rating must be between 0 and 5, got: {value}",
                })
                continue
            updates_by_book[book_id]["rating"] = value

        # pubdate — accept ISO string or datetime, normalise to string for calibredb
        elif field == "pubdate":
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    updates_by_book[book_id]["pubdate"] = dt
                except ValueError:
                    failed_updates.append({
                        "book_id": book_id,
                        "field": field,
                        "error": f"Invalid date format (expected ISO 8601): {value}",
                    })
                    continue
            elif hasattr(value, "isoformat"):
                updates_by_book[book_id]["pubdate"] = value
            else:
                failed_updates.append({
                    "book_id": book_id,
                    "field": field,
                    "error": f"pubdate must be an ISO date string or datetime, got {type(value).__name__}",
                })
                continue

        # Remaining supported fields pass through directly
        else:
            updates_by_book[book_id][field] = value

    # --- Execute one calibredb write per book, check actual persisted fields ---
    for book_id, metadata_dict in updates_by_book.items():
        if not metadata_dict:
            # All fields for this book ended up in failed_updates; nothing to write.
            continue
        try:
            result = await update_book_helper(
                book_id=str(book_id),
                metadata=metadata_dict,
            )
            # Hard-fail: only count as success when calibredb actually wrote at least one field.
            written = result.get("updated_fields", [])
            if not written:
                failed_updates.append({
                    "book_id": book_id,
                    "fields": list(metadata_dict.keys()),
                    "error": (
                        "calibredb reported success but no fields were written. "
                        "The metadata dict may not have contained any recognised calibredb fields."
                    ),
                })
            else:
                updated_books.append(book_id)
                logger.info(f"Book {book_id}: updated fields {written}")
        except Exception as e:
            failed_updates.append({
                "book_id": book_id,
                "fields": list(metadata_dict.keys()),
                "error": str(e),
            })
            logger.warning(f"Failed to update book {book_id}: {e}")

    return MetadataUpdateResponse(
        updated_books=updated_books, failed_updates=failed_updates, success_count=len(updated_books)
    )


# NOTE: @mcp.tool() decorator removed - use manage_metadata portmanteau tool instead
async def auto_organize_tags_helper() -> TagStatsResponse:
    """
    AI-powered tag organization and cleanup suggestions.

    Uses similarity matching to identify duplicate tags,
    suggests tag hierarchies, and provides cleanup recommendations.

    Returns:
        TagStatsResponse: Tag organization suggestions and cleanup stats
    """
    import sqlite3
    from pathlib import Path

    from ..shared.db_init import ensure_db_initialized

    err = ensure_db_initialized()
    if err:
        return TagStatsResponse(
            total_tags=0,
            unique_tags=0,
            duplicate_tags=[],
            unused_tags=[],
            suggestions=[{"error": err}],
        )

    # Resolve metadata.db path from the live engine
    from ...db.database import db as database_singleton
    engine_url = str(database_singleton._engine.url) if database_singleton._engine else ""
    db_path: Path | None = None
    if engine_url.startswith("sqlite:///"):
        db_path = Path(engine_url.replace("sqlite:///", ""))

    if not db_path or not db_path.exists():
        return TagStatsResponse(
            total_tags=0,
            unique_tags=0,
            duplicate_tags=[],
            unused_tags=[],
            suggestions=[{"error": "Cannot locate metadata.db"}],
        )

    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        # All tags and their book counts
        rows = conn.execute(
            "SELECT t.id, t.name, COUNT(btl.book) AS cnt "
            "FROM tags t LEFT JOIN books_tags_link btl ON btl.tag = t.id "
            "GROUP BY t.id, t.name ORDER BY t.name"
        ).fetchall()

        total_tags = len(rows)
        unused = [r["name"] for r in rows if r["cnt"] == 0]

        # Find near-duplicate names (case/whitespace variants)
        seen: dict[str, list[str]] = {}
        for r in rows:
            key = r["name"].lower().strip()
            seen.setdefault(key, []).append(r["name"])
        dup_groups = [
            {"canonical": names[0], "variants": names[1:], "merge_suggestion": names[0]}
            for names in seen.values()
            if len(names) > 1
        ]

        # Top-10 used tags as suggestions for controlled vocabulary
        top_tags = sorted(rows, key=lambda r: r["cnt"], reverse=True)[:10]
        suggestions = [
            {
                "type": "top_tag",
                "tag": r["name"],
                "book_count": r["cnt"],
                "note": "High-usage tag — good candidate for controlled vocabulary",
            }
            for r in top_tags
        ]
        if dup_groups:
            suggestions.insert(
                0,
                {
                    "type": "dedup_summary",
                    "duplicate_group_count": len(dup_groups),
                    "note": "Merge duplicate_tags variants into their canonical form",
                },
            )

        return TagStatsResponse(
            total_tags=total_tags,
            unique_tags=total_tags - len(unused),
            duplicate_tags=dup_groups,
            unused_tags=unused,
            suggestions=suggestions,
        )
    finally:
        conn.close()


# NOTE: @mcp.tool() decorator removed - use manage_metadata portmanteau tool instead
async def fix_metadata_issues_helper() -> dict[str, Any]:
    """
    Scan the library for common metadata problems (report-only).

    Detects books with missing titles, missing authors, undefined publication
    dates, and books with no format files. Returns a structured report rather
    than mutating data, so it is safe to run against a large library.

    Returns:
        dict: {"success", "total_books", "issues": {category: [book dicts]}, "summary"}
    """
    import sqlite3
    from pathlib import Path

    from ..shared.db_init import ensure_db_initialized

    err = ensure_db_initialized()
    if err:
        return {"success": False, "error": err, "issues": {}}

    from ...db.database import db as database_singleton

    engine_url = str(database_singleton._engine.url) if database_singleton._engine else ""
    db_path: Path | None = None
    if engine_url.startswith("sqlite:///"):
        db_path = Path(engine_url.replace("sqlite:///", ""))

    if not db_path or not db_path.exists():
        return {"success": False, "error": "Cannot locate metadata.db", "issues": {}}

    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        total_books = conn.execute("SELECT COUNT(*) AS c FROM books").fetchone()["c"]

        # Missing or placeholder title
        missing_title = [
            {"book_id": r["id"], "title": r["title"]}
            for r in conn.execute(
                "SELECT id, title FROM books "
                "WHERE title IS NULL OR TRIM(title) = '' OR title = 'Unknown'"
            ).fetchall()
        ]

        # No author link (or only the Calibre 'Unknown' author)
        missing_author = [
            {"book_id": r["id"], "title": r["title"]}
            for r in conn.execute(
                "SELECT b.id, b.title FROM books b "
                "WHERE NOT EXISTS (SELECT 1 FROM books_authors_link bal WHERE bal.book = b.id) "
                "OR b.author_sort IS NULL OR TRIM(b.author_sort) = '' "
                "OR b.author_sort = 'Unknown'"
            ).fetchall()
        ]

        # Undefined pubdate — Calibre uses year 0101 as the 'undefined' sentinel
        missing_pubdate = [
            {"book_id": r["id"], "title": r["title"], "pubdate": r["pubdate"]}
            for r in conn.execute(
                "SELECT id, title, pubdate FROM books "
                "WHERE pubdate IS NULL OR pubdate LIKE '0101-%'"
            ).fetchall()
        ]

        # Books with no format files
        no_formats = [
            {"book_id": r["id"], "title": r["title"]}
            for r in conn.execute(
                "SELECT b.id, b.title FROM books b "
                "WHERE NOT EXISTS (SELECT 1 FROM data d WHERE d.book = b.id)"
            ).fetchall()
        ]

        issues = {
            "missing_title": missing_title,
            "missing_author": missing_author,
            "missing_pubdate": missing_pubdate,
            "no_formats": no_formats,
        }
        summary = {k: len(v) for k, v in issues.items()}
        total_issues = sum(summary.values())

        return {
            "success": True,
            "report_only": True,
            "total_books": total_books,
            "total_issues": total_issues,
            "summary": summary,
            "issues": issues,
            "note": (
                "Report-only scan — no metadata was modified. Use manage_metadata("
                "operation='update', ...) to fix individual books."
            ),
        }
    finally:
        conn.close()
