"""
inspect_contents portmanteau: contained-works indexing for collection ebooks.

Delphi-style "Complete Works" editions hide dozens/hundreds of works inside a
single library row. This tool finds them (scan), reads their TOC (index),
serves the works (contents), and searches across them (search) — without ever
creating fake book rows. Contained works are second-class citizens: findable,
never counted.

Collection threshold: 25 non-group works (agreed 2026-10-15).
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from ...config import CalibreConfig
from ...db.database import db as database_singleton
from ...db.user_data import CollectionIndex, get_user_data_db
from ...logging_config import get_logger
from ...server import mcp
from ...services.book_service import BookService
from ..book_tools import search_books_helper as _search_books_helper
from ..shared.error_handling import handle_tool_error
from .epub_toc import looks_like_collection, parse_epub_toc

logger = get_logger("calibremcp.tools.contents")

COLLECTION_THRESHOLD = 25
SCAN_PATTERNS = ("complete works", "collected works", "complete novels", "omnibus", "delphi")


def _norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _active_library() -> str:
    config = CalibreConfig.load_config()
    lib = str(config.local_library_path or "").strip()
    if not lib:
        raise ValueError("No library configured (CALIBRE_LIBRARY_PATH).")
    return lib


def _book_service() -> BookService:
    return BookService(database_singleton)


def _epub_for_book(book: dict[str, Any], lib_path: str) -> Path | None:
    rel = book.get("path", "")
    if not rel:
        return None
    folder = Path(lib_path) / rel
    if not folder.is_dir():
        return None
    epubs = sorted(folder.glob("*.epub"))
    return epubs[0] if epubs else None


def _row_to_dict(row: CollectionIndex) -> dict[str, Any]:
    try:
        works = json.loads(row.works_json or "[]")
    except (ValueError, TypeError):
        works = []
    return {
        "book_id": row.book_id,
        "book_title": row.book_title,
        "book_author": row.book_author,
        "is_collection": bool(row.is_collection),
        "work_count": row.work_count,
        "source": row.source,
        "indexed_at": row.indexed_at.isoformat() if row.indexed_at else None,
        "works": works,
    }


def _store_index(book_id: int, lib_path: str, title: str, author: str, parsed: dict[str, Any]) -> dict[str, Any]:
    works = parsed.get("works", [])
    # attach group context: nearest preceding group header
    current_group = ""
    for w in works:
        if w.get("is_group"):
            current_group = w.get("title", "")
        else:
            w["group"] = current_group
    real_works = [w for w in works if not w.get("is_group")]
    is_collection = len(real_works) >= COLLECTION_THRESHOLD
    db = get_user_data_db()
    with db.session_scope() as session:
        session.query(CollectionIndex).filter(
            CollectionIndex.book_id == book_id, CollectionIndex.library_path == lib_path
        ).delete()
        session.add(
            CollectionIndex(
                book_id=book_id,
                library_path=lib_path,
                book_title=title,
                book_author=author,
                is_collection=1 if is_collection else 0,
                work_count=len(real_works),
                works_json=json.dumps(works, ensure_ascii=False),
                source=parsed.get("source", "none"),
                indexed_at=datetime.utcnow(),
            )
        )
    return {
        "book_id": book_id,
        "is_collection": is_collection,
        "work_count": len(real_works),
        "total_navpoints": len(works),
        "source": parsed.get("source", "none"),
    }


def search_contents_rows(query: str, library_path: str, limit: int = 50) -> list[dict[str, Any]]:
    """Search indexed contained works (sync helper, reused by canon + REST)."""
    needle = _norm(query)
    if len(needle) < 3:
        return []
    db = get_user_data_db()
    hits: list[dict[str, Any]] = []
    with db.session_scope() as session:
        rows = (
            session.query(CollectionIndex)
            .filter(
                CollectionIndex.library_path == library_path,
                CollectionIndex.is_collection == 1,
            )
            .all()
        )
        for row in rows:
            try:
                works = json.loads(row.works_json or "[]")
            except (ValueError, TypeError):
                continue
            for w in works:
                if w.get("is_group"):
                    continue
                if needle in _norm(w.get("title", "")):
                    hits.append(
                        {
                            "book_id": row.book_id,
                            "book_title": row.book_title,
                            "book_author": row.book_author,
                            "work_title": w.get("title", ""),
                            "group": w.get("group", ""),
                        }
                    )
                    if len(hits) >= limit:
                        return hits
    return hits


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def inspect_contents(
    operation: str,
    book_id: int | None = None,
    query: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Contained-works index for omnibus/collection ebooks (Delphi Complete Works etc.).

    Operations:
    - scan: metadata-only candidate sweep (title/tag patterns, no file reads).
      Returns candidates with reasons; nothing is indexed yet.
    - index: parse one book's EPUB TOC and store its works (book_id required).
      Reports work_count, source (ncx/nav/spine), is_collection (>=25 works).
    - contents: read stored works for a book (book_id required). Auto-indexes
      on first read when the book looks like a collection.
    - search: find a work across all indexed collections
      (e.g. "wisteria lodge" → the Sherlock omnibus holding it).

    Contained works are NEVER library books: no counts, no fake rows — they
    surface in search results and canon coverage only, always attributed to
    their host volume.

    ## Examples
    `inspect_contents(operation="scan")`
    `inspect_contents(operation="index", book_id=13284)`
    `inspect_contents(operation="contents", book_id=13284)`
    `inspect_contents(operation="search", query="wisteria lodge")`
    """
    try:
        lib_path = _active_library()

        if operation == "scan":
            # NOTE: text= (full-text) searches take ~90s on a 10k library, so
            # scan uses indexed title=/tag= lookups only (milliseconds each).
            seen: dict[int, dict[str, Any]] = {}

            def _collect(items: Any) -> None:
                for b in items or []:
                    if not isinstance(b, dict) or b.get("id") is None:
                        continue
                    tags = [t.get("name", "") if isinstance(t, dict) else str(t) for t in b.get("tags", [])]
                    if looks_like_collection(b.get("title", ""), tags):
                        series = b.get("series")
                        seen[b["id"]] = {
                            "book_id": b["id"],
                            "title": b.get("title", ""),
                            "authors": b.get("authors", []),
                            "series": series.get("name") if isinstance(series, dict) else series,
                            "tags": tags,
                            "reason": "title/tag pattern",
                        }

            for pattern in SCAN_PATTERNS:
                for kwargs in ({"title": pattern}, {"tag": pattern}):
                    try:
                        result = await _search_books_helper(limit=100, **kwargs)
                    except Exception as e:
                        logger.warning("Scan search failed for %r: %s", kwargs, e)
                        continue
                    _collect(result.get("items"))
            return {
                "success": True,
                "operation": operation,
                "candidates": sorted(seen.values(), key=lambda c: str(c["title"])),
                "candidate_count": len(seen),
                "note": "Candidates only — run index per book_id to parse TOCs.",
            }

        if operation == "index":
            if book_id is None:
                return {
                    "success": False,
                    "operation": operation,
                    "error": "book_id is required for operation='index'.",
                    "error_code": "MISSING_BOOK_ID",
                }
            svc = _book_service()
            try:
                book = svc.get_by_id(int(book_id))
            except Exception as e:
                return {"success": False, "operation": operation, "error": str(e), "error_code": "BOOK_NOT_FOUND"}
            authors = book.get("authors", []) or []
            author_str = ", ".join(a.get("name", "") if isinstance(a, dict) else str(a) for a in authors)
            epub = _epub_for_book(book, lib_path)
            if epub is None:
                return {
                    "success": False,
                    "operation": operation,
                    "error": f"No EPUB format found for book {book_id}.",
                    "error_code": "NO_EPUB",
                }
            parsed = parse_epub_toc(epub)
            if not parsed.get("ok"):
                return {
                    "success": False,
                    "operation": operation,
                    "error": parsed.get("error", "parse failed"),
                    "error_code": "TOC_PARSE_ERROR",
                }
            stored = _store_index(int(book_id), lib_path, book.get("title", ""), author_str, parsed)
            return {"success": True, "operation": operation, **stored}

        if operation == "contents":
            if book_id is None:
                return {
                    "success": False,
                    "operation": operation,
                    "error": "book_id is required for operation='contents'.",
                    "error_code": "MISSING_BOOK_ID",
                }
            db = get_user_data_db()
            with db.session_scope() as session:
                row = (
                    session.query(CollectionIndex)
                    .filter(CollectionIndex.book_id == int(book_id), CollectionIndex.library_path == lib_path)
                    .first()
                )
                if row is not None:
                    data = _row_to_dict(row)
                    return {"success": True, "operation": operation, "indexed": True, **data}
            # Not indexed: auto-index when it looks like a collection.
            svc = _book_service()
            try:
                book = svc.get_by_id(int(book_id))
            except Exception as e:
                return {"success": False, "operation": operation, "error": str(e), "error_code": "BOOK_NOT_FOUND"}
            tags = [t.get("name", "") if isinstance(t, dict) else str(t) for t in book.get("tags", [])]
            if not looks_like_collection(book.get("title", ""), tags):
                return {
                    "success": True,
                    "operation": operation,
                    "indexed": False,
                    "is_collection": False,
                    "book_id": int(book_id),
                    "note": "Does not look like a collection (title/tag patterns); use index to force-parse.",
                }
            authors = book.get("authors", []) or []
            author_str = ", ".join(a.get("name", "") if isinstance(a, dict) else str(a) for a in authors)
            epub = _epub_for_book(book, lib_path)
            if epub is None:
                return {"success": False, "operation": operation, "error": "No EPUB found.", "error_code": "NO_EPUB"}
            parsed = parse_epub_toc(epub)
            if not parsed.get("ok"):
                return {
                    "success": False,
                    "operation": operation,
                    "error": parsed.get("error", ""),
                    "error_code": "TOC_PARSE_ERROR",
                }
            stored = _store_index(int(book_id), lib_path, book.get("title", ""), author_str, parsed)
            with db.session_scope() as session:
                row = (
                    session.query(CollectionIndex)
                    .filter(CollectionIndex.book_id == int(book_id), CollectionIndex.library_path == lib_path)
                    .first()
                )
                data = _row_to_dict(row) if row else stored
            return {"success": True, "operation": operation, "indexed": True, **data}

        if operation == "search":
            if not query or len(query.strip()) < 3:
                return {
                    "success": False,
                    "operation": operation,
                    "error": "query (min 3 chars) is required for operation='search'.",
                    "error_code": "MISSING_QUERY",
                }
            hits = search_contents_rows(query, lib_path, limit=max(1, min(limit, 100)))
            return {"success": True, "operation": operation, "query": query, "total": len(hits), "hits": hits}

        return {
            "success": False,
            "operation": operation,
            "error": f"Invalid operation: '{operation}'. Must be one of: 'scan', 'index', 'contents', 'search'.",
            "error_code": "INVALID_OPERATION",
        }
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={"book_id": book_id, "query": query},
            tool_name="inspect_contents",
            context="Inspecting collection contents",
        )
