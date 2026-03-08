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


# Max characters from comment to include in searchable text
COMMENT_SNIPPET_LEN = 2000


def _book_to_searchable_text(
    session: Any,
    book: Book,
) -> str:
    """Build a single searchable text string for a book from metadata."""
    parts = [book.title or ""]
    # Authors
    try:
        authors = [a.name for a in book.authors] if book.authors else []
        if authors:
            parts.append(" ".join(authors))
    except Exception:
        pass
    # Series
    try:
        if book.series:
            series_names = [s.name for s in book.series]
            if series_names:
                parts.append(" ".join(series_names))
    except Exception:
        pass
    # Tags
    try:
        if book.tags:
            parts.append(" ".join(t.name for t in book.tags))
    except Exception:
        pass
    # Comment (snippet)
    try:
        comment = session.query(Comment).filter(Comment.book == book.id).first()
        if comment and comment.text:
            text = (
                comment.text[:COMMENT_SNIPPET_LEN] + "..."
                if len(comment.text) > COMMENT_SNIPPET_LEN
                else comment.text
            )
            parts.append(text)
    except Exception:
        pass
    return " ".join(p for p in parts if p).strip() or book.title or ""


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

    try:
        # Re-open session for comment lookups per book
        session = db_svc.session
        documents = []
        rows = []
        progress_interval = 50
        try:
            for i, book in enumerate(books):
                text = _book_to_searchable_text(session, book)
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
