"""
Build RAG index: read chunks from Calibre FTS, embed, upsert into LanceDB (FTS path, table ``books_rag``).
"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from calibre_mcp.rag.lancedb_vector_store import LanceVectorStore

from .chunking import chunk_books_text
from .storage_paths import fts_chunks_lancedb_dir

logger = logging.getLogger(__name__)

BATCH_SIZE = 128


def build_rag_index(
    metadata_db_path: Path,
    *,
    persist_directory: Path | None = None,
    chunk_size: int = 1200,
    overlap: int = 200,
    use_ollama: bool = True,  # Kept for API compatibility; embeddings use fastembed in LanceVectorStore
    ollama_base_url: str = "",
    ollama_model: str = "",
    force_rebuild: bool = False,
    on_progress: Callable[[int, int], None] | None = None,
) -> int:
    """
    Build or rebuild RAG index for the library at metadata_db_path.

    Returns number of chunks indexed.
    """
    if persist_directory:
        db_path = str(Path(persist_directory) / "lancedb")
    else:
        db_path = str(fts_chunks_lancedb_dir(metadata_db_path))

    store = LanceVectorStore(db_path=db_path, table_name="books_rag")

    batch_docs: list[dict[str, Any]] = []
    total = 0

    def flush() -> None:
        nonlocal total
        if not batch_docs:
            return

        store.add_documents(batch_docs, overwrite=force_rebuild and total == 0)
        total += len(batch_docs)
        if on_progress:
            on_progress(total, total)

    for chunk in chunk_books_text(metadata_db_path, chunk_size=chunk_size, overlap=overlap):
        chunk_id = f"b{chunk['book_id']}_f{chunk['format']}_i{chunk['chunk_index']}"
        batch_docs.append(
            {
                "id": chunk_id,
                "content": chunk["text"],
                "metadata": {
                    "book_id": chunk["book_id"],
                    "format": chunk["format"],
                    "chunk_index": chunk["chunk_index"],
                },
            }
        )

        if len(batch_docs) >= BATCH_SIZE:
            flush()
            batch_docs.clear()

    flush()
    logger.info("RAG index built: %s chunks", total)
    return total
