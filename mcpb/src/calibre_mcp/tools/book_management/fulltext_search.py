"""
Full-text search inside book content using Calibre's full-text-search.db.

Calibre builds full-text-search.db (FTS5) next to metadata.db when FTS is enabled.
Searches the extracted text of books, not just metadata. Uses Calibre schema:
books_text JOIN books_fts ON books_text.id = books_fts.rowid; falls back to
LIKE on books_text if the Calibre tokenizer is unavailable.
"""

import asyncio
from pathlib import Path
from typing import Any

from fastmcp import Context

from ...db.database import get_database
from ...logging_config import get_logger
from ...server import mcp
from ...services.book_service import book_service
from ...utils.fts_location_resolver import resolve_location_for_file
from ...utils.fts_utils import find_fts_database, query_fts, query_fts_detailed
from ..shared.error_handling import format_error_response, handle_tool_error

logger = get_logger("calibremcp.tools.book_management.fulltext_search")


def _pick_format_path(book: dict[str, Any], want_fmt: str) -> str | None:
    want = (want_fmt or "").upper()
    for f in book.get("formats") or []:
        if (f.get("format") or "").upper() == want:
            p = f.get("path")
            if p:
                return str(p)
    # Fallback: first path
    for f in book.get("formats") or []:
        p = f.get("path")
        if p:
            return str(p)
    return None


@mcp.tool()
async def search_fulltext(
    query: str,
    limit: int = 50,
    offset: int = 0,
    use_stemming: bool = False,
    include_snippets: bool = True,
    enrich: bool = True,
    resolve_locations: bool = False,
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
        resolve_locations: If True, add per-format locations: char offsets in Calibre's
            indexed text, PDF page (PyMuPDF), EPUB spine href, and Calibre
            ``ebook-viewer --open-at search:...`` hints so you can jump to the phrase.

    Returns:
        Dict with:
        - total: Total number of distinct books with matching content
        - book_ids: List of book IDs in this page
        - snippets: Dict book_id -> snippet text (if include_snippets)
        - books: List of book dicts with metadata (if enrich)
        - fts_available: True if FTS virtual table was used, False if LIKE fallback
        - locations: (if resolve_locations) list of match rows with file paths and hints
    """
    start_ms = __import__("time").time()
    if ctx:
        try:
            ctx.info(
                "search_fulltext query=%s limit=%s resolve_locations=%s",
                query,
                limit,
                resolve_locations,
            )
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

        used_fts5 = True
        locations: list[dict[str, Any]] = []

        if resolve_locations:
            detailed, total_books, used_fts5 = query_fts_detailed(
                fts_path,
                search_text=query,
                limit=limit_val,
                offset=offset_val,
                use_stemming=use_stemming,
                include_snippets=include_snippets,
            )
            book_ids: list[int] = []
            seen: set[int] = set()
            snippets: dict[int, str] = {}
            for row in detailed:
                bid = row["book_id"]
                if bid not in snippets and row.get("snippet"):
                    snippets[bid] = row["snippet"]
                if bid not in seen:
                    seen.add(bid)
                    book_ids.append(bid)
            total = total_books

            for row in detailed:
                bid = row["book_id"]
                fmt = row["format"]
                try:
                    b = book_service.get_by_id(bid)
                except Exception as e:
                    logger.warning("get_by_id failed for %s: %s", bid, e)
                    continue
                fpath = _pick_format_path(b, fmt)
                loc_bundle: dict[str, Any] = {
                    "books_text_id": row["books_text_id"],
                    "book_id": bid,
                    "format": fmt,
                    "snippet": row.get("snippet"),
                    "char_offset": row.get("char_offset"),
                    "char_end": row.get("char_end"),
                }
                if fpath:
                    try:
                        resolved = resolve_location_for_file(fpath, fmt, query)
                        loc_bundle.update(resolved)
                        pdf = (
                            loc_bundle.get("pdf") if isinstance(loc_bundle.get("pdf"), dict) else {}
                        )
                        if pdf.get("resolved"):
                            loc_bundle["manage_viewer_get_page"] = {
                                "operation": "get_page",
                                "book_id": bid,
                                "file_path": fpath,
                                "page_number": pdf.get("page_0based", 0),
                            }
                    except Exception as e:
                        loc_bundle["resolution_error"] = str(e)
                else:
                    loc_bundle["resolution_error"] = "no_file_path_for_format"
                locations.append(loc_bundle)
        else:
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
        }
        if resolve_locations:
            out["locations"] = locations
            out["fts_used_virtual_table"] = used_fts5
            out["fts_available"] = used_fts5
        else:
            out["fts_available"] = total > 0 or not book_ids

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
        if resolve_locations:
            out["recommendations"].append(
                "With resolve_locations: use locations[].calibre_viewer for ebook-viewer --open-at search:… "
                "or locations[].pdf / locations[].epub for page/spine when resolved."
            )
        return out

    return await asyncio.to_thread(_run)
