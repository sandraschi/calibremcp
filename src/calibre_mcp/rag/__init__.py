"""
RAG over Calibre book text: chunk, embed, store in Chroma, retrieve by semantic query.

Enables queries like "book where somebody was stabbed with an icicle" (weapon melts,
no evidence) without keyword match. Optional deps: pip install calibre-mcp[rag].
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
