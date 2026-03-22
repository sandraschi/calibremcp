"""
RAG over Calibre book text: FTS chunks → LanceDB (``lancedb/books_rag``), semantic retrieve.

Legacy optional Chroma helpers remain in ``store`` (``calibre-mcp[rag]``); primary path is LanceDB.
"""

from .chunking import chunk_books_text
from .store import get_rag_store
from .indexer import build_rag_index
from .retriever import retrieve_chunks

__all__ = [
    "chunk_books_text",
    "get_rag_store",
    "build_rag_index",
    "retrieve_chunks",
]
