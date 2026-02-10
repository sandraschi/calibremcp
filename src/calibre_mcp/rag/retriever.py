"""
Semantic retrieval: embed query, search Chroma, return top-k chunks with metadata.
"""

import logging
from pathlib import Path

from .embedding import embed_texts
from .store import get_rag_store

logger = logging.getLogger(__name__)


def retrieve_chunks(
    metadata_db_path: Path,
    query: str,
    top_k: int = 10,
    *,
    persist_directory: Path | None = None,
    use_ollama: bool = True,
    ollama_base_url: str = "http://127.0.0.1:11434",
    ollama_model: str = "nomic-embed-text",
    book_ids: list[int] | None = None,
) -> list[dict]:
    """
    Return top-k chunks most similar to the query (semantic search).

    Each result: text, book_id, format, chunk_index, distance (lower = more similar).
    If book_ids is set, filter to those books only (Chroma where clause).
    """
    if not query or not query.strip():
        return []
    store = get_rag_store(metadata_db_path, persist_directory)
    if store.count() == 0:
        logger.warning("RAG index empty; run rag_index_build first")
        return []

    query_emb = embed_texts(
        [query.strip()],
        use_ollama=use_ollama,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
    )
    if not query_emb:
        return []

    where = None
    if book_ids:
        where = {"book_id": {"$in": book_ids}}

    res = store.query(
        query_embeddings=query_emb,
        n_results=min(top_k, store.count()),
        where=where,
    )
    ids = res.get("ids", [[]])[0]
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    out = []
    for i, doc in enumerate(docs):
        meta = metas[i] if i < len(metas) else {}
        dist = dists[i] if i < len(dists) else None
        out.append({
            "text": doc,
            "book_id": meta.get("book_id"),
            "format": meta.get("format"),
            "chunk_index": meta.get("chunk_index"),
            "distance": dist,
        })
    return out
