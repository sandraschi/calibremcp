"""
Export library metadata to JSON using the same SQLAlchemy path as the MCP server.

Parity with ``scripts/export_metadata_for_rag.py`` (Calibre ``new_api``) for fields used in RAG pipelines.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import joinedload

from calibre_mcp.db.database import get_database
from calibre_mcp.db.models import Book
from calibre_mcp.rag.text_utils import strip_html_for_embedding

logger = logging.getLogger("calibremcp.rag.metadata_export")


def build_export_records(*, strip_html: bool = True) -> list[dict[str, Any]]:
    """
    Load all books from the current library and return JSON-serializable records.

    Schema aligns with ``scripts/export_metadata_for_rag.py`` (id, title, authors, tags, series,
    series_index, publisher, comments, formats, path).
    """
    db_svc = get_database()
    current = db_svc.get_current_path()
    if not current:
        raise RuntimeError(
            "Database not initialized. Use manage_libraries(operation='switch') first."
        )

    session = db_svc.session
    records: list[dict[str, Any]] = []
    try:
        books = (
            session.query(Book)
            .options(
                joinedload(Book.authors),
                joinedload(Book.tags),
                joinedload(Book.series),
                joinedload(Book.publishers),
                joinedload(Book.data),
                joinedload(Book.comments),
            )
            .order_by(Book.id)
            .all()
        )
        for book in books:
            raw_comment = ""
            c = book.comments
            if c is not None and getattr(c, "text", None):
                raw_comment = c.text or ""

            comments_out = strip_html_for_embedding(raw_comment) if strip_html else raw_comment

            authors = [a.name for a in book.authors] if book.authors else []
            tags = [t.name for t in book.tags] if book.tags else []
            series_name = ""
            if book.series:
                series_name = book.series[0].name
            publisher = ""
            if book.publishers:
                publisher = book.publishers[0].name
            formats = sorted({d.format.upper() for d in (book.data or [])})

            records.append(
                {
                    "id": book.id,
                    "title": book.title,
                    "authors": authors,
                    "tags": tags,
                    "series": series_name,
                    "series_index": float(book.series_index)
                    if book.series_index is not None
                    else None,
                    "publisher": publisher,
                    "comments": comments_out,
                    "formats": formats,
                    "path": book.path,
                }
            )
    finally:
        session.close()

    return records


def write_metadata_json_file(
    output_path: str | Path,
    *,
    strip_html: bool = True,
) -> tuple[int, Path]:
    """
    Write metadata export JSON. Returns (book_count, resolved path).
    """
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    records = build_export_records(strip_html=strip_html)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote metadata export: %d books -> %s", len(records), path)
    return len(records), path
