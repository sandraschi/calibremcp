"""
LanceDB-backed RAG over Calibre metadata (title, authors, tags, comments, series).

Reads from metadata.db via existing DatabaseService, builds one searchable text blob per book,
embeds with fastembed, stores in LanceDB. Enables semantic search without full-text book content.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from calibre_mcp.db.database import get_database
from calibre_mcp.db.models import Book, Comment
from calibre_mcp.rag.text_utils import (
    get_comment_max_chars,
    should_strip_html_metadata,
    strip_html_for_embedding,
)

logger = logging.getLogger("calibremcp.rag.metadata_rag")

PROGRESS_FILENAME = ".build_progress.json"


def _write_progress(
    lancedb_dir: Path, status: str, current: int, total: int, message: str = ""
) -> None:
    path = lancedb_dir / PROGRESS_FILENAME
    try:
        data = {"status": status, "current": current, "total": total, "message": message}
        if total > 0:
            data["percentage"] = round(100 * current / total, 1)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data), encoding="utf-8")
        tmp.replace(path)
    except Exception as e:
        logger.debug("Could not write progress file: %s", e)


def write_build_started(lancedb_dir: Path) -> None:
    """Write initial progress so UI can show build started. Called before starting background build."""
    _write_progress(lancedb_dir, "building", 0, 0, "Starting...")


# Back-compat alias; use ``get_comment_max_chars()`` (env ``CALIBRE_METADATA_COMMENT_MAX_CHARS``).
COMMENT_SNIPPET_LEN = 20 * 1024  # 20 KiB; matches ``text_utils`` default


def _book_to_searchable_text(
    session: Any,
    book: Book,
    library_path: str = "",
) -> str:
    """Build a single searchable text string for a book from metadata.

    Includes: title, authors, series, tags, Calibre comment, and — if
    library_path is provided — extended metadata from calibre_mcp_data.db
    (original_language, mood, read_status, locked_room_type, personal notes).
    """
    parts = [book.title or ""]
    # Authors
    try:
        authors = [a.name for a in book.authors] if book.authors else []
        if authors:
            parts.append(" ".join(authors))
    except Exception as e:
        logger.debug("authors for book %s: %s", book.id, e)
    # Series
    try:
        if book.series:
            series_names = [s.name for s in book.series]
            if series_names:
                parts.append(" ".join(series_names))
    except Exception as e:
        logger.debug("series for book %s: %s", book.id, e)
    # Tags
    try:
        if book.tags:
            parts.append(" ".join(t.name for t in book.tags))
    except Exception as e:
        logger.debug("tags for book %s: %s", book.id, e)
    # Comment (curated blurbs/notes — primary semantic signal for many libraries)
    try:
        comment = session.query(Comment).filter(Comment.book == book.id).first()
        if comment and comment.text:
            text = comment.text
            if should_strip_html_metadata():
                text = strip_html_for_embedding(text)
            max_c = get_comment_max_chars()
            if len(text) > max_c:
                text = text[:max_c] + "..."
            parts.append(text)
    except Exception as e:
        logger.debug("Could not load comment for book %s: %s", book.id, e)
    base = " ".join(p for p in parts if p).strip() or book.title or ""
    if library_path:
        ext = _get_extended_metadata_text(book.id, library_path)
        if ext:
            return f"{base} {ext}".strip()
    return base


def _get_extended_metadata_text(book_id: int, library_path: str) -> str:
    """Pull extended metadata fields from calibre_mcp_data.db and format
    them as natural-language phrases for semantic embedding.

    Returns empty string if DB not available or no data for this book.
    The phrases are designed to be semantically meaningful so queries like
    'locked room', 'impossible crime', 'unread japanese fiction' etc. work.
    """
    try:
        import sqlite3
        import os

        # Locate calibre_mcp_data.db using same logic as plugin db_adapter
        if os.name == "nt":
            appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
            db_path = os.path.join(appdata, "calibre-mcp", "calibre_mcp_data.db")
        else:
            import platform
            home = os.path.expanduser("~")
            if platform.system() == "Darwin":
                db_path = os.path.join(home, "Library", "Application Support",
                                       "calibre-mcp", "calibre_mcp_data.db")
            else:
                db_path = os.path.join(home, ".local", "share",
                                       "calibre-mcp", "calibre_mcp_data.db")

        # Allow env override
        env_dir = os.getenv("CALIBRE_MCP_USER_DATA_DIR")
        if env_dir:
            db_path = os.path.join(env_dir, "calibre_mcp_data.db")

        if not os.path.exists(db_path):
            return ""

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT original_language, mood, read_status, culprit, "
                "locked_room_type, edition_notes "
                "FROM book_extended_metadata "
                "WHERE book_id=? AND library_path=?",
                (book_id, library_path),
            ).fetchone()

            # Also get personal notes from user_comments
            note_row = conn.execute(
                "SELECT comment_text FROM user_comments "
                "WHERE book_id=? AND library_path=?",
                (book_id, library_path),
            ).fetchone()
        finally:
            conn.close()

        if not row and not note_row:
            return ""

        phrases = []
        if row:
            if row["original_language"]:
                phrases.append(f"original language: {row['original_language']}")
            if row["mood"]:
                phrases.append(f"mood: {row['mood']}")
            if row["read_status"]:
                phrases.append(f"read status: {row['read_status']}")
            if row["culprit"]:
                # Don't embed the actual culprit name — just note it's annotated
                phrases.append("culprit annotated")
            if row["locked_room_type"]:
                phrases.append(f"locked room type: {row['locked_room_type']}")
                phrases.append("impossible crime mystery")
            if row["edition_notes"]:
                phrases.append(f"edition: {row['edition_notes']}")
        if note_row and note_row["comment_text"]:
            phrases.append(note_row["comment_text"][:500])

        return " ".join(phrases)

    except Exception as e:
        logger.debug("Extended metadata lookup failed for book %s: %s", book_id, e)
        return ""


def get_metadata_rag_path(metadata_db_path: str | Path) -> Path:
    """Return LanceDB path for metadata RAG (next to library or in configurable dir)."""
    p = Path(metadata_db_path).resolve()
    if p.is_file():
        p = p.parent
    return p / "lancedb_metadata"


def build_metadata_index(
    metadata_db_path: str | Path | None = None,
    *,
    force_rebuild: bool = False,
    embedding_model: str = "BAAI/bge-small-en-v1.5",
) -> int:
    """
    Ingest all books from metadata.db into LanceDB for semantic search.

    Reads books with authors, tags, comments, series; builds searchable text per book;
    embeds with fastembed; writes to LanceDB table calibre_metadata.

    Returns:
        Number of books indexed.
    """
    import lancedb
    from fastembed import TextEmbedding

    db_svc = get_database()
    current = db_svc.get_current_path()
    if not current:
        raise RuntimeError(
            "Database not initialized. Use manage_libraries(operation='switch') first."
        )
    metadata_db_path = metadata_db_path or current

    lancedb_dir = get_metadata_rag_path(metadata_db_path)
    lancedb_dir.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(lancedb_dir))

    table_name = "calibre_metadata"
    if force_rebuild and table_name in db.table_names():
        db.drop_table(table_name)

    from sqlalchemy.orm import joinedload

    try:
        session = db_svc.session
        books = (
            session.query(Book)
            .options(
                joinedload(Book.authors),
                joinedload(Book.tags),
                joinedload(Book.series),
            )
            .all()
        )
    finally:
        session.close()

    if not books:
        logger.warning("No books found in library")
        return 0

    total_books = len(books)
    _write_progress(lancedb_dir, "building", 0, total_books, "Gathering metadata")

    library_path_str = str(Path(metadata_db_path).resolve())
    if Path(library_path_str).is_file():
        library_path_str = str(Path(library_path_str).parent)

    try:
        # Re-open session for comment lookups per book
        session = db_svc.session
        documents = []
        rows = []
        progress_interval = 50
        try:
            for i, book in enumerate(books):
                text = _book_to_searchable_text(session, book,
                                                library_path=library_path_str)
                if not text:
                    continue
                documents.append(text)
                rows.append(
                    {
                        "book_id": book.id,
                        "title": book.title or "",
                        "text": text,
                    }
                )
                if (i + 1) % progress_interval == 0:
                    _write_progress(
                        lancedb_dir, "building", i + 1, total_books, "Gathering metadata"
                    )
        finally:
            session.close()

        if not documents:
            _write_progress(lancedb_dir, "done", 0, 0, "No searchable text")
            return 0

        num_docs = len(rows)
        _write_progress(
            lancedb_dir,
            "loading_model",
            0,
            num_docs,
            "Loading embedding model (first run may download ~130 MB)...",
        )

        embedding = TextEmbedding(model_name=embedding_model, cache_dir=str(lancedb_dir / "cache"))

        _write_progress(lancedb_dir, "embedding", 0, num_docs, "Embedding")
        batch_size = 100
        for start in range(0, num_docs, batch_size):
            end = min(start + batch_size, num_docs)
            batch_docs = [rows[i]["text"] for i in range(start, end)]
            batch_embeddings = list(embedding.embed(batch_docs))
            for j, row in enumerate(rows[start:end]):
                if j < len(batch_embeddings):
                    row["vector"] = batch_embeddings[j]
            _write_progress(
                lancedb_dir, "embedding", end, num_docs, f"Embedding ({end}/{num_docs})"
            )

        if table_name in db.table_names():
            tbl = db.open_table(table_name)
            tbl.add(rows)
        else:
            db.create_table(table_name, rows, mode="overwrite")

        _write_progress(lancedb_dir, "done", num_docs, num_docs, "Done")
        logger.info("Metadata RAG index built: %d books", num_docs)
        return num_docs
    except Exception as e:
        _write_progress(lancedb_dir, "error", 0, 0, str(e))
        raise


def search_metadata(
    query: str,
    metadata_db_path: str | Path | None = None,
    *,
    top_k: int = 10,
    embedding_model: str = "BAAI/bge-small-en-v1.5",
) -> list[dict[str, Any]]:
    """
    Semantic search over book metadata. Returns list of hits with book_id, title, text snippet, score.
    """
    import lancedb
    from fastembed import TextEmbedding

    if metadata_db_path is None:
        db_svc = get_database()
        current = db_svc.get_current_path()
        if not current:
            return []
        metadata_db_path = current
    lancedb_dir = get_metadata_rag_path(metadata_db_path)
    if not lancedb_dir.exists():
        return []

    db = lancedb.connect(str(lancedb_dir))
    table_name = "calibre_metadata"
    if table_name not in db.table_names():
        return []

    embedding = TextEmbedding(model_name=embedding_model, cache_dir=str(lancedb_dir / "cache"))
    query_vector = list(embedding.embed([query]))[0]

    tbl = db.open_table(table_name)
    results = tbl.search(query_vector).limit(top_k).to_list()
    return [
        {
            "book_id": r.get("book_id"),
            "title": r.get("title", ""),
            "text": (r.get("text") or "")[:500],
            "score": float(r.get("_distance", 0.0)),
        }
        for r in results
    ]
