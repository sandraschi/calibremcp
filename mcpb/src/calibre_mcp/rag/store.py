"""
Chroma vector store for RAG. One collection per library (keyed by path hash or name).
"""

import hashlib
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _collection_name(metadata_db_path: Path) -> str:
    """Stable collection name from library path."""
    path_str = str(metadata_db_path.resolve())
    h = hashlib.sha256(path_str.encode("utf-8")).hexdigest()[:16]
    return f"calibre_rag_{h}"


def get_rag_store(
    metadata_db_path: Path,
    persist_directory: Path | None = None,
):
    """
    Return a Chroma-backed store for the given library.

    If persist_directory is None, uses metadata_db_path.parent / ".calibre-rag".
    """
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        raise ImportError("Install RAG extras: pip install calibre-mcp[rag]")

    persist = persist_directory or (metadata_db_path.parent / ".calibre-rag")
    persist.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(persist),
        settings=Settings(anonymized_telemetry=False),
    )
    name = _collection_name(metadata_db_path)
    collection = client.get_or_create_collection(
        name=name,
        metadata={"description": "Calibre book text chunks for RAG"},
    )
    return _ChromaStore(collection, name)


class _ChromaStore:
    def __init__(self, collection: Any, name: str):
        self._collection = collection
        self._name = name

    def count(self) -> int:
        return self._collection.count()

    def clear(self) -> None:
        self._collection.delete(self._collection.get()["ids"])

    def add_chunks(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        if not ids:
            return
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int = 10,
        where: dict | None = None,
    ) -> dict:
        res = self._collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return res
