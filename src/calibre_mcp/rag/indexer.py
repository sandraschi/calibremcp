"""
Build RAG index: read chunks from Calibre FTS, embed, upsert into LanceDB via shared BaseVectorStore.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Callable

from .chunking import chunk_books_text

central_docs_src = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../../mcp-central-docs/src")
)
if os.path.exists(central_docs_src) and central_docs_src not in sys.path:
    sys.path.append(central_docs_src)

try:
    from docs_mcp.backend.rag_core import BaseVectorStore

    HAS_RAG = True
except ImportError:
    HAS_RAG = False

    class BaseVectorStore:
        def __init__(self, *args, **kwargs):
            pass

        def add_documents(self, documents, overwrite=True):
            pass


logger = logging.getLogger(__name__)

BATCH_SIZE = 128


def build_rag_index(
    metadata_db_path: Path,
    *,
    persist_directory: Path | None = None,
    chunk_size: int = 1200,
    overlap: int = 200,
    use_ollama: bool = True,  # Kept for signature compatibility but ignored (BaseVectorStore manages embedding)
    ollama_base_url: str = "",
    ollama_model: str = "",
    force_rebuild: bool = False,
    on_progress: Callable[[int, int], None] | None = None,
) -> int:
    """
    Build or rebuild RAG index for the library at metadata_db_path.

    Returns number of chunks indexed.
    """
    if not HAS_RAG:
        logger.error("docs_mcp.backend.rag_core not found.")
        return 0

    if not persist_directory:
        db_path = str(metadata_db_path.parent / "lancedb")
    else:
        db_path = str(persist_directory / "lancedb")

    store = BaseVectorStore(db_path=db_path, table_name="books_rag")

    batch_docs = []
    total = 0

    def flush():
        nonlocal total
        if not batch_docs:
            return

        store.add_documents(batch_docs, overwrite=force_rebuild and total == 0)
        total += len(batch_docs)
        if on_progress:
            on_progress(total, total)

    for chunk in chunk_books_text(
        metadata_db_path, chunk_size=chunk_size, overlap=overlap
    ):
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
