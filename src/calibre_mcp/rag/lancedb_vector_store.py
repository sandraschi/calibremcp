"""
LanceDB + fastembed vector store for Calibre content RAG (portmanteau ingest / full-text chunks).

Self-contained in calibre-mcp — no dependency on other repos. FTS-derived indexes use
``indexer``/``retriever`` with table ``books_rag`` under ``{library}/lancedb``; neural
ingest uses tables ``calibre_media`` / ``calibre_fulltext`` under ``{library}/lancedb_calibre``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import lancedb
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)


class LanceVectorStore:
    """Document embeddings and retrieval using LanceDB (same role as legacy external BaseVectorStore)."""

    def __init__(
        self,
        db_path: str | Path,
        embedding_model_name: str = "BAAI/bge-small-en-v1.5",
        table_name: str = "documents",
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(str(self.db_path))
        self.embedding_model = TextEmbedding(
            model_name=embedding_model_name,
            cache_dir=str(self.db_path / "cache"),
        )
        self.table_name = table_name

    def add_documents(self, documents: list[dict[str, Any]], overwrite: bool = True) -> None:
        """
        Embed and index documents.

        Each item: ``id``, ``content``, ``metadata`` (dict); optional ``source``.
        """
        if not documents:
            return

        logger.info("Embedding %s items into '%s'...", len(documents), self.table_name)

        contents = [doc["content"] for doc in documents]
        embeddings = list(self.embedding_model.embed(contents))

        data: list[dict[str, Any]] = []
        for doc, emb in zip(documents, embeddings, strict=True):
            vec = emb.tolist() if hasattr(emb, "tolist") else list(emb)
            entry: dict[str, Any] = {
                "id": doc.get("id"),
                "vector": vec,
                "content": doc.get("content"),
                "metadata": doc.get("metadata", {}),
            }
            if "source" in doc:
                entry["source"] = doc["source"]
            data.append(entry)

        if overwrite or self.table_name not in self.db.table_names():
            self.db.create_table(self.table_name, data=data, mode="overwrite")
        else:
            tbl = self.db.open_table(self.table_name)
            tbl.add(data)

        logger.info("Indexed %s items into LanceDB table '%s'.", len(data), self.table_name)

    def search(self, query: str, limit: int = 5, where: str | None = None) -> list[dict[str, Any]]:
        """Semantic search with optional LanceDB prefilter."""
        if self.table_name not in self.db.table_names():
            logger.warning("Table '%s' not found.", self.table_name)
            return []

        tbl = self.db.open_table(self.table_name)
        qemb = list(self.embedding_model.embed([query]))[0]
        qvec = qemb.tolist() if hasattr(qemb, "tolist") else list(qemb)

        search_req = tbl.search(qvec).limit(limit)
        if where:
            search_req = search_req.where(where)

        return search_req.to_arrow().to_pylist()

    def get_table_metadata(self) -> dict[str, Any]:
        if self.table_name not in self.db.table_names():
            return {"exists": False, "row_count": 0}

        tbl = self.db.open_table(self.table_name)
        return {"exists": True, "row_count": tbl.count_rows()}
