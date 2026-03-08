"""
Semantic retrieval: embed query, search LanceDB, return top-k chunks with metadata.
"""

import logging
import sys
import os
from pathlib import Path

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

        def search(self, query, limit=5, where=None):
            return []


logger = logging.getLogger(__name__)


def retrieve_chunks(
    metadata_db_path: Path,
    query: str,
    top_k: int = 10,
    *,
    persist_directory: Path | None = None,
    use_ollama: bool = True,  # Ignored (BaseVectorStore does this)
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

    if not HAS_RAG:
        logger.error("RAG Core unavailable.")
        return []

    if not persist_directory:
        db_path = str(metadata_db_path.parent / "lancedb")
    else:
        db_path = str(persist_directory / "lancedb")

    store = BaseVectorStore(db_path=db_path, table_name="books_rag")

    where_clause = None
    if book_ids:
        # LanceDB SQL filter syntax
        id_list = ", ".join(str(bid) for bid in book_ids)
        where_clause = f"metadata.book_id IN ({id_list})"

    try:
        results = store.search(query.strip(), limit=top_k, where=where_clause)
    except Exception as e:
        logger.warning(f"RAG search failed or table empty: {e}")
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
                "distance": res.get(
                    "_distance", 0.0
                ),  # distance is _distance in lancedb default query
            }
        )
    return out
