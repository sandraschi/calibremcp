"""
Chunk book text from Calibre FTS books_text for RAG indexing.

Reads full-text-search.db; yields chunks with metadata (book_id, format, index)
and configurable size/overlap (character-based to avoid tokenizer dependency).

**Filters (environment):**

- ``CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS`` — comma-separated Calibre format codes (e.g. ``PDF``, ``EPUB``).
  If the variable is **unset**, **PDF is excluded** by default from **content** chunking only (metadata RAG
  is unchanged for PDF vs EPUB). Set to empty string to index all formats in chunk RAG.
- ``CALIBRE_RAG_MAX_BOOK_TEXT_CHARS`` — if set to a positive integer, skip any ``books_text`` row whose
  ``searchable_text`` is longer (e.g. giant textbooks). Omit for no limit.
"""

import logging
import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path

from ..utils.fts_utils import find_fts_database

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_CHARS = 1200
DEFAULT_OVERLAP_CHARS = 200


def _exclude_formats_from_env() -> set[str]:
    """Formats to skip for chunk RAG. Default (unset env): exclude PDF only."""
    if "CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS" not in os.environ:
        return {"PDF"}
    raw = os.environ["CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS"].strip()
    if not raw:
        return set()
    return {x.strip().upper() for x in raw.split(",") if x.strip()}


def _max_book_text_chars_from_env() -> int | None:
    raw = os.environ.get("CALIBRE_RAG_MAX_BOOK_TEXT_CHARS", "").strip()
    if not raw:
        return None
    try:
        v = int(raw)
    except ValueError:
        return None
    return v if v > 0 else None


def _split_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_CHARS,
    overlap: int = DEFAULT_OVERLAP_CHARS,
) -> list[str]:
    """Split text into overlapping chunks (character-based)."""
    if not text or not text.strip():
        return []
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            # Try to break at sentence or paragraph
            for sep in ("\n\n", "\n", ". ", " "):
                last = chunk.rfind(sep)
                if last > chunk_size // 2:
                    chunk = chunk[: last + len(sep)].strip()
                    end = start + len(chunk)
                    break
        chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    return chunks


def chunk_books_text(
    metadata_db_path: Path,
    chunk_size: int = DEFAULT_CHUNK_CHARS,
    overlap: int = DEFAULT_OVERLAP_CHARS,
) -> Iterator[dict]:
    """
    Read books_text from Calibre FTS DB and yield chunks with metadata.

    Yields dicts: text, book_id, format, chunk_index.
    """
    fts_path = find_fts_database(metadata_db_path)
    if not fts_path or not fts_path.exists():
        logger.warning("No FTS database at %s", metadata_db_path.parent)
        return

    exclude_formats = _exclude_formats_from_env()
    max_book_chars = _max_book_text_chars_from_env()
    if exclude_formats:
        logger.info(
            "Chunk RAG excluding formats: %s (set CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS= to include them)",
            ", ".join(sorted(exclude_formats)),
        )
    if max_book_chars is not None:
        logger.info(
            "Chunk RAG skipping books_text rows longer than %s chars (CALIBRE_RAG_MAX_BOOK_TEXT_CHARS)",
            max_book_chars,
        )

    conn = sqlite3.connect(str(fts_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            "SELECT id, book, format, searchable_text FROM books_text WHERE searchable_text IS NOT NULL AND trim(searchable_text) != ''"
        )
        for row in cur:
            book_id = int(row["book"])
            fmt = (row["format"] or "").strip().upper() or "UNKNOWN"
            raw = (row["searchable_text"] or "").strip()
            if not raw:
                continue
            if fmt in exclude_formats:
                logger.debug("Skipping chunk RAG for book %s format %s (excluded)", book_id, fmt)
                continue
            if max_book_chars is not None and len(raw) > max_book_chars:
                logger.debug(
                    "Skipping chunk RAG for book %s format %s: text length %s > max %s",
                    book_id,
                    fmt,
                    len(raw),
                    max_book_chars,
                )
                continue
            for i, chunk_text in enumerate(
                _split_into_chunks(raw, chunk_size=chunk_size, overlap=overlap)
            ):
                if not chunk_text.strip():
                    continue
                yield {
                    "text": chunk_text,
                    "book_id": book_id,
                    "format": fmt,
                    "chunk_index": i,
                }
    finally:
        conn.close()
