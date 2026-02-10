"""
Full-text search inside book content using Calibre's full-text-search.db.

Calibre builds full-text-search.db (FTS5) next to metadata.db when FTS is enabled.
Searches the extracted text of books, not just metadata. Uses Calibre schema:
books_text JOIN books_fts ON books_text.id = books_fts.rowid; falls back to
LIKE on books_text if the custom tokenizer is unavailable.
"""

import asyncio
from pathlib import Path
from typing import Any

from fastmcp import Context

from ...db.database import get_database
from ...logging_config import get_logger
from ...server import mcp
from ...services.book_service import book_service
from ...utils.fts_utils import find_fts_database, query_fts
from ..shared.error_handling import format_error_response, handle_tool_error

logger = get_logger("calibremcp.tools.book_management.fulltext_search")


@mcp.tool()
async def search_fulltext(
    query: str,
    limit: int = 50,
    offset: int = 0,
    use_stemming: bool = False,
    include_snippets: bool = True,
    enrich: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Search inside book content (full text) using Calibre's FTS database.

    Requires Calibre to have built the full-text index (full-text-search.db in the
    same folder as metadata.db). Searches the actual text of books, not just
    title/author/tags. Uses FTS5 when available; falls back to LIKE search if
    the Calibre tokenizer is not available (e.g. when using standard SQLite).

    Args:
        query: Search string (word or phrase). FTS5: use quotes for exact phrase.
        limit: Max number of books to return (1-200). Default 50.
        offset: Pagination offset. Default 0.
        use_stemming: Use stemmed index (e.g. "running" matches "run"). Default False.
        include_snippets: Include a short snippet per book showing the match. Default True.
        enrich: If True, attach full book metadata for each result. Default True.

    Returns:
        Dict with:
        - total: Total number of books with matching content
        - book_ids: List of book IDs in this page
        - snippets: Dict book_id -> snippet text (if include_snippets)
        - books: List of book dicts with metadata (if enrich)
        - fts_available: True if FTS virtual table was used, False if LIKE fallback
    """
    start_ms = __import__("time").time()
    if ctx:
        try:
            ctx.info("search_fulltext query=%s limit=%s", query, limit)
        except Exception:
            pass

    @handle_tool_error(logger, "search_fulltext")
    def _run() -> dict[str, Any]:
        limit_val = max(1, min(200, limit))
        offset_val = max(0, offset)

        try:
            db = get_database()
        except RuntimeError:
            return format_error_response(
                error_msg="No library loaded. Use manage_libraries(operation='list') then operation='switch')."
            )

        meta_path = db.get_current_path()
        if not meta_path:
            return format_error_response(
                error_msg="Current library path unknown. Switch library with manage_libraries(operation='switch')."
            )

        fts_path = find_fts_database(Path(meta_path))
        if not fts_path:
            return format_error_response(
                error_msg=(
                    "Full-text search database not found. Calibre creates full-text-search.db "
                    "in the library folder when FTS is enabled. Enable FTS in Calibre and run "
                    "indexing, or use query_books to search metadata only."
                )
            )

        book_ids, total, snippets = query_fts(
            fts_path,
            search_text=query,
            limit=limit_val,
            offset=offset_val,
            use_stemming=use_stemming,
            include_snippets=include_snippets,
        )

        out: dict[str, Any] = {
            "total": total,
            "book_ids": book_ids,
            "snippets": snippets,
            "books": [],
            "fts_available": total > 0 or not book_ids,
        }

        if enrich and book_ids:
            try:
                for bid in book_ids:
                    b = book_service.get_by_id(bid)
                    if b:
                        rec = dict(b)
                        if include_snippets and bid in snippets:
                            rec["snippet"] = snippets[bid]
                        out["books"].append(rec)
            except Exception as e:
                logger.warning("Enrich failed for fulltext results: %s", e)
                out["books"] = []
                out["enrich_error"] = str(e)

        out["execution_time_ms"] = int((__import__("time").time() - start_ms) * 1000)
        out["recommendations"] = [
            "Use query_books for metadata-only search",
            "Use manage_books(operation='get') for full book details",
        ]
        return out

    return await asyncio.to_thread(_run)
