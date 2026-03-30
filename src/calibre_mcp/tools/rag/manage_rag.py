"""
RAG portmanteau: FTS text chunks → LanceDB (``lancedb/books_rag``), separate from metadata RAG.

Semantic search over passages from Calibre's ``full-text-search.db`` (FTS must be enabled).
Not the same as ``lancedb_metadata`` (metadata-only) or ``lancedb_calibre`` (portmanteau ingest).
"""

import asyncio
import threading
from pathlib import Path
from typing import Any

from fastmcp import Context

from calibre_mcp.db.database import get_database
from calibre_mcp.logging_config import get_logger
from calibre_mcp.server import mcp
from calibre_mcp.services.book_service import book_service
from calibre_mcp.tools.shared.error_handling import format_error_response, handle_tool_error

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
    Build/rebuild the semantic content index from Calibre FTS data into LanceDB.
    """
    start = __import__("time").time()

    def _run() -> dict[str, Any]:
        meta_path = _get_metadata_path()
        if not meta_path or not meta_path.exists():
            return format_error_response(
                error_msg="No library loaded. Use manage_libraries(operation='switch') first."
            )
        try:
            from calibre_mcp.rag.indexer import build_rag_index
        except ImportError as e:
            return format_error_response(
                error_msg="RAG extras not installed. Run: pip install calibre-mcp[rag]",
                error_code="RAG_DEPS_MISSING",
                error_type="ImportError",
                diagnostic_info={"detail": str(e)},
            )
        from calibre_mcp.utils.fts_utils import find_fts_database

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
            "recommendations": [
                "Use rag_retrieve(query=...) to search by meaning (e.g. icicle murder)."
            ],
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
    Semantic 'trope' search over book passages (e.g. 'murder with an icicle').
    """
    start = __import__("time").time()

    def _run() -> dict[str, Any]:
        meta_path = _get_metadata_path()
        if not meta_path or not meta_path.exists():
            return format_error_response(
                error_msg="No library loaded. Use manage_libraries(operation='switch') first.",
                error_code="NO_LIBRARY",
                error_type="RuntimeError",
            )
        try:
            from calibre_mcp.rag.retriever import retrieve_chunks
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
            "recommendations": [
                "Use search_fulltext for keyword search; rag_retrieve for semantic (trope/scene) search."
            ],
        }

    try:
        return await asyncio.to_thread(_run)
    except Exception as e:
        return handle_tool_error(e, tool_name="rag_retrieve")


def _run_metadata_build_background(force_rebuild: bool) -> None:
    """Run metadata RAG build in background; progress written to lancedb_metadata/.build_progress.json."""
    try:
        from calibre_mcp.rag.metadata_rag import build_metadata_index

        build_metadata_index(force_rebuild=force_rebuild)
    except Exception as e:
        logger.exception("Metadata RAG build failed: %s", e)


@mcp.tool()
async def calibre_metadata_index_build(
    force_rebuild: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Build/rebuild the semantic metadata index (titles, authors, tags, comments, series).
    """

    def _start() -> dict[str, Any]:
        try:
            from calibre_mcp.rag.metadata_rag import get_metadata_rag_path, write_build_started
        except ImportError as e:
            return format_error_response(
                error_msg="Metadata RAG requires lancedb and fastembed. Install calibre-mcp dependencies.",
                error_code="RAG_DEPS_MISSING",
                error_type="ImportError",
                diagnostic_info={"detail": str(e)},
            )
        db = get_database()
        path = db.get_current_path()
        if not path:
            return format_error_response(
                error_msg="No library loaded. Use manage_libraries(operation='switch') first.",
                error_code="NO_LIBRARY",
                error_type="RuntimeError",
            )
        lancedb_dir = get_metadata_rag_path(path)
        lancedb_dir.mkdir(parents=True, exist_ok=True)
        write_build_started(lancedb_dir)
        thread = threading.Thread(
            target=_run_metadata_build_background,
            args=(force_rebuild,),
            daemon=True,
        )
        thread.start()
        return {
            "status": "started",
            "message": "Build started in background. Poll GET /api/rag/metadata/build/status for progress.",
            "recommendations": [
                "Use calibre_metadata_search(query=...) to search by meaning when done."
            ],
        }

    try:
        return await asyncio.to_thread(_start)
    except Exception as e:
        return handle_tool_error(e, tool_name="calibre_metadata_index_build")


@mcp.tool()
async def calibre_metadata_search(
    query: str,
    top_k: int = 10,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Semantic search over book metadata (e.g. 'Japanese mystery light novels').
    """
    start = __import__("time").time()

    def _run() -> dict[str, Any]:
        try:
            from calibre_mcp.rag.metadata_rag import search_metadata
        except ImportError as e:
            return format_error_response(
                error_msg="Metadata RAG requires lancedb and fastembed.",
                error_code="RAG_DEPS_MISSING",
                error_type="ImportError",
                diagnostic_info={"detail": str(e)},
            )
        k = max(1, min(50, top_k))
        import logging

        logger = logging.getLogger("calibremcp.tools.rag")
        logger.debug(f"Calling search_metadata with type {type(search_metadata)}")

        results = search_metadata(query.strip(), top_k=k)
        if not results:
            return {
                "results": [],
                "message": "No results. Run calibre_metadata_index_build first, or try a different query.",
                "execution_time_ms": int((__import__("time").time() - start) * 1000),
            }
        return {
            "results": results,
            "message": f"Found {len(results)} book(s) matching the meaning of your query.",
            "execution_time_ms": int((__import__("time").time() - start) * 1000),
        }

    try:
        return await asyncio.to_thread(_run)
    except Exception as e:
        return handle_tool_error(e, tool_name="calibre_metadata_search")


@mcp.tool()
async def calibre_metadata_export_json(
    output_path: str | None = None,
    strip_html: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Export all library metadata to JSON for external RAG or bulk processing.
    """
    start = __import__("time").time()

    def _run() -> dict[str, Any]:
        try:
            from calibre_mcp.rag.metadata_export import write_metadata_json_file
        except ImportError as e:
            return format_error_response(
                error_msg="Metadata export failed to load.",
                error_code="EXPORT_DEPS",
                error_type="ImportError",
                diagnostic_info={"detail": str(e)},
            )
        meta = _get_metadata_path()
        if not meta or not meta.exists():
            return format_error_response(
                error_msg="No library loaded. Use manage_libraries(operation='switch') first.",
                error_code="NO_LIBRARY",
                error_type="RuntimeError",
            )
        out = Path(output_path) if output_path else meta / "calibre_mcp_metadata_export.json"
        try:
            n, resolved = write_metadata_json_file(out, strip_html=strip_html)
        except RuntimeError as e:
            return format_error_response(
                error_msg=str(e),
                error_code="NO_LIBRARY",
                error_type="RuntimeError",
            )
        except OSError as e:
            return format_error_response(
                error_msg=f"Could not write file: {e}",
                error_code="WRITE_ERROR",
                error_type="OSError",
            )
        elapsed = int((__import__("time").time() - start) * 1000)
        return {
            "books_exported": n,
            "output_path": str(resolved),
            "message": f"Exported {n} book(s) to {resolved}.",
            "execution_time_ms": elapsed,
            "recommendations": [
                "Ingest JSON into an external vector DB for cross-library RAG, or rebuild metadata index after bulk comment edits.",
            ],
        }

    try:
        return await asyncio.to_thread(_run)
    except Exception as e:
        return handle_tool_error(e, tool_name="calibre_metadata_export_json")
