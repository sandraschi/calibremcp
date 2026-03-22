"""On-disk layout for LanceDB indexes (kept separate per purpose)."""

from __future__ import annotations

from pathlib import Path


def _library_dir(metadata_db_path: str | Path) -> Path:
    p = Path(metadata_db_path).resolve()
    return p.parent if p.is_file() else p


def fts_chunks_lancedb_dir(metadata_db_path: str | Path) -> Path:
    """Calibre FTS text chunks → semantic index (table ``books_rag``)."""
    return _library_dir(metadata_db_path) / "lancedb"


def portmanteau_lancedb_dir(metadata_db_path: str | Path) -> Path:
    """Neural ingest: tables ``calibre_media``, ``calibre_fulltext``."""
    return _library_dir(metadata_db_path) / "lancedb_calibre"
