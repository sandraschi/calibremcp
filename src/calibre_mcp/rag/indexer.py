"""
Build RAG index: read chunks from Calibre FTS, embed, upsert into Chroma.
"""

import logging
from pathlib import Path
from typing import Callable

from .chunking import chunk_books_text
from .embedding import embed_texts
from .store import get_rag_store

logger = logging.getLogger(__name__)

BATCH_SIZE = 32


def build_rag_index(
    metadata_db_path: Path,
    *,
    persist_directory: Path | None = None,
    chunk_size: int = 1200,
    overlap: int = 200,
    use_ollama: bool = True,
    ollama_base_url: str = "http://127.0.0.1:11434",
    ollama_model: str = "nomic-embed-text",
    force_rebuild: bool = False,
    on_progress: Callable[[int, int], None] | None = None,
) -> int:
    """
    Build or rebuild RAG index for the library at metadata_db_path.

    Returns number of chunks indexed.
    """
    store = get_rag_store(metadata_db_path, persist_directory)
    if force_rebuild:
        store.clear()

    batch_ids: list[str] = []
    batch_docs: list[str] = []
    batch_metas: list[dict] = []
    total = 0

    def flush():
        nonlocal total
        if not batch_ids:
            return
        embs = embed_texts(
            batch_docs,
            use_ollama=use_ollama,
            ollama_base_url=ollama_base_url,
            ollama_model=ollama_model,
        )
        store.add_chunks(batch_ids, embs, batch_docs, batch_metas)
        total += len(batch_ids)
        if on_progress:
            on_progress(total, total)

    chunk_count = 0
    for chunk in chunk_books_text(metadata_db_path, chunk_size=chunk_size, overlap=overlap):
        chunk_id = f"b{chunk['book_id']}_f{chunk['format']}_i{chunk['chunk_index']}"
        batch_ids.append(chunk_id)
        batch_docs.append(chunk["text"])
        batch_metas.append({
            "book_id": chunk["book_id"],
            "format": chunk["format"],
            "chunk_index": chunk["chunk_index"],
        })
        chunk_count += 1
        if len(batch_ids) >= BATCH_SIZE:
            flush()
            batch_ids.clear()
            batch_docs.clear()
            batch_metas.clear()

    flush()
    logger.info("RAG index built: %s chunks", total)
    return total
