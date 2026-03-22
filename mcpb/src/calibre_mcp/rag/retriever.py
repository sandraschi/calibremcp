"""
Semantic retrieval: embed query, search LanceDB (FTS chunk index), return top-k chunks with metadata.
"""

import logging
from pathlib import Path

from calibre_mcp.rag.lancedb_vector_store import LanceVectorStore

from .storage_paths import fts_chunks_lancedb_dir

logger = logging.getLogger(__name__)


def retrieve_chunks(
    metadata_db_path: Path,
    query: str,
    top_k: int = 10,
    *,
    persist_directory: Path | None = None,
    use_ollama: bool = True,  # Kept for API compatibility
    ollama_base_url: str = "",
    ollama_model: str = "",
    book_ids: list[int] | None = None,
) -> list[dict]:
    """
    Return top-k chunks most similar to the query (semantic search).

    Each result: text, book_id, format, chunk_index, distance (lower = more similar).
    """
    if not query or not query.strip():
        return []

    if persist_directory:
        db_path = str(Path(persist_directory) / "lancedb")
    else:
        db_path = str(fts_chunks_lancedb_dir(metadata_db_path))

    store = LanceVectorStore(db_path=db_path, table_name="books_rag")

    where_clause = None
    if book_ids:
        id_list = ", ".join(str(bid) for bid in book_ids)
        where_clause = f"metadata.book_id IN ({id_list})"

    try:
        results = store.search(query.strip(), limit=top_k, where=where_clause)
    except Exception as e:
        logger.warning("RAG search failed or table empty: %s", e)
        return []

    out = []
    for res in results:
        meta = res.get("metadata", {})
        out.append(
            {
                "text": res.get("content", ""),
                "book_id": meta.get("book_id"),
                "format": meta.get("format"),
                "chunk_index": meta.get("chunk_index"),
                "distance": res.get("_distance", 0.0),
            }
        )
    return out
