"""
RAG portmanteau: build semantic index from book text, retrieve by natural-language query.

Enables queries like "book where somebody was stabbed with an icicle" (weapon melts,
no evidence) via embedding similarity, not keywords. Requires: Calibre FTS DB, pip install calibre-mcp[rag].
"""

import asyncio
from pathlib import Path
from typing import Any

from fastmcp import Context

from ...db.database import get_database
from ...logging_config import get_logger
from ...server import mcp
from ...services.book_service import book_service
from ..shared.error_handling import format_error_response, handle_tool_error

logger = get_logger("calibremcp.tools.rag")


def _get_metadata_path() -> Path | None:
    try:
        db = get_database()
        path = db.get_current_path()
        return Path(path) if path else None
    except RuntimeError:
        return None


@mcp.tool()
async def rag_index_build(
    force_rebuild: bool = False,
    use_ollama: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Build or rebuild the semantic (RAG) index for the current library.

    Reads book text from Calibre's full-text-search.db, chunks it, embeds with
    Ollama (nomic-embed-text) or FastEmbed, and stores vectors in Chroma. Run
    once per library (and after adding many books). Enables rag_retrieve.

    Args:
        force_rebuild: If True, clear existing index and rebuild. Default False.
        use_ollama: Use Ollama for embeddings (recommended). If False, uses FastEmbed.

    Returns:
        Dict with chunks_indexed, message, execution_time_ms.
    """
    start = __import__("time").time()

    @handle_tool_error(logger, "rag_index_build")
    def _run() -> dict[str, Any]:
        meta_path = _get_metadata_path()
        if not meta_path or not meta_path.exists():
            return format_error_response(
                error_msg="No library loaded. Use manage_libraries(operation='switch') first."
            )
        try:
            from ...rag.indexer import build_rag_index
        except ImportError as e:
            return format_error_response(
                error_msg="RAG extras not installed. Run: pip install calibre-mcp[rag]",
                error_code="RAG_DEPS_MISSING",
                error_type="ImportError",
                diagnostic_info={"detail": str(e)},
            )
        from ...utils.fts_utils import find_fts_database
        if not find_fts_database(meta_path):
            return format_error_response(
                error_msg="No Calibre FTS database (full-text-search.db). Enable FTS in Calibre and index books first.",
                error_code="FTS_MISSING",
                error_type="FileNotFoundError",
            )
        n = build_rag_index(
            meta_path,
            force_rebuild=force_rebuild,
            use_ollama=use_ollama,
        )
        return {
            "chunks_indexed": n,
            "message": f"RAG index built: {n} chunks indexed.",
            "execution_time_ms": int((__import__("time").time() - start) * 1000),
            "recommendations": ["Use rag_retrieve(query=...) to search by meaning (e.g. icicle murder)."],
        }

    try:
        return await asyncio.to_thread(_run)
    except Exception as e:
        return handle_tool_error(e, tool_name="rag_index_build")


@mcp.tool()
async def rag_retrieve(
    query: str,
    top_k: int = 10,
    use_ollama: bool = True,
    enrich: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Semantic search over book content: find passages that match the *meaning* of the query.

    Example: "book where somebody was stabbed with an icicle" finds scenes where the
    weapon melts (icicle/ice bullet trope), not just keyword "icicle". Uses the
    RAG index built by rag_index_build.

    Args:
        query: Natural-language question or description (e.g. "murder with melting weapon").
        top_k: Number of passages to return (default 10).
        use_ollama: Use Ollama for query embedding (must match index).
        enrich: Attach book title/authors for each chunk (default True).

    Returns:
        Dict with chunks (text, book_id, format, chunk_index, distance[, title, authors]), execution_time_ms.
    """
    start = __import__("time").time()

    @handle_tool_error(logger, "rag_retrieve")
    def _run() -> dict[str, Any]:
        meta_path = _get_metadata_path()
        if not meta_path or not meta_path.exists():
            return format_error_response(
                error_msg="No library loaded. Use manage_libraries(operation='switch') first.",
                error_code="NO_LIBRARY",
                error_type="RuntimeError",
            )
        try:
            from ...rag.retriever import retrieve_chunks
        except ImportError:
            return format_error_response(
                error_msg="RAG extras not installed. Run: pip install calibre-mcp[rag]",
                error_code="RAG_DEPS_MISSING",
                error_type="ImportError",
            )
        k = max(1, min(50, top_k))
        chunks = retrieve_chunks(
            meta_path,
            query.strip(),
            top_k=k,
            use_ollama=use_ollama,
        )
        if not chunks:
            return {
                "chunks": [],
                "message": "No results. Run rag_index_build first, or try a different query.",
                "execution_time_ms": int((__import__("time").time() - start) * 1000),
            }
        if enrich:
            for c in chunks:
                bid = c.get("book_id")
                if bid is not None:
                    try:
                        b = book_service.get_by_id(int(bid))
                        c["title"] = b.get("title")
                        c["authors"] = b.get("authors", [])
                    except Exception:
                        c["title"] = None
                        c["authors"] = []
        return {
            "chunks": chunks,
            "message": f"Found {len(chunks)} passage(s) matching the meaning of your query.",
            "execution_time_ms": int((__import__("time").time() - start) * 1000),
            "recommendations": ["Use search_fulltext for keyword search; rag_retrieve for semantic (trope/scene) search."],
        }

    try:
        return await asyncio.to_thread(_run)
    except Exception as e:
        return handle_tool_error(e, tool_name="rag_retrieve")
