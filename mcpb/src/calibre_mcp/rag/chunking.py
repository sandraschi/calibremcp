"""
Chunk book text from Calibre FTS books_text for RAG indexing.

Reads full-text-search.db; yields chunks with metadata (book_id, format, index)
and configurable size/overlap (character-based to avoid tokenizer dependency).
"""

import logging
import sqlite3
from pathlib import Path
from typing import Iterator

from ..utils.fts_utils import find_fts_database

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_CHARS = 1200
DEFAULT_OVERLAP_CHARS = 200


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
