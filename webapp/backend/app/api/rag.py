"""RAG API: metadata index build, semantic search, full-text RAG, and synopsis."""

import json
from pathlib import Path

from fastapi import APIRouter, Query

from ..cache import get_libraries_cache
from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()

PROGRESS_FILENAME = ".build_progress.json"


# ── Index build ──────────────────────────────────────────────────────────────

@router.get("/metadata/build/status")
async def rag_metadata_build_status():
    """Return current metadata RAG build progress (percentage, status) for the current library."""
    cache = get_libraries_cache()
    current_name = cache.get("current_library")
    libraries = cache.get("libraries", [])
    path = None
    for lib in libraries:
        if lib.get("name") == current_name:
            path = lib.get("path")
            break
    if not path:
        return {"status": "idle", "current": 0, "total": 0, "percentage": 0, "message": ""}
    progress_file = Path(path) / "lancedb_metadata" / PROGRESS_FILENAME
    if not progress_file.exists():
        return {"status": "idle", "current": 0, "total": 0, "percentage": 0, "message": ""}
    try:
        data = json.loads(progress_file.read_text(encoding="utf-8"))
        return {
            "status": data.get("status", "idle"),
            "current": data.get("current", 0),
            "total": data.get("total", 0),
            "percentage": data.get("percentage", 0),
            "message": data.get("message", ""),
        }
    except (json.JSONDecodeError, OSError):
        return {"status": "idle", "current": 0, "total": 0, "percentage": 0, "message": ""}


@router.post("/metadata/build")
async def rag_metadata_build(force_rebuild: bool = False):
    """Start build or rebuild of the LanceDB metadata index.
    Poll GET /api/rag/metadata/build/status for progress."""
    try:
        result = await mcp_client.call_tool(
            "calibre_metadata_index_build",
            {"force_rebuild": force_rebuild},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/content/build")
async def rag_content_build(force_rebuild: bool = False):
    """Start build or rebuild of the LanceDB full-text content index.
    Required before rag_retrieve will return passage-level results."""
    try:
        result = await mcp_client.call_tool(
            "rag_index_build",
            {"force_rebuild": force_rebuild},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


# ── Metadata semantic search ──────────────────────────────────────────────────

@router.get("/metadata/search")
async def rag_metadata_search(
    q: str = Query(..., min_length=1, description="Natural-language search query"),
    top_k: int = Query(10, ge=1, le=50),
):
    """Semantic search over book metadata (title, authors, tags, comments).
    Requires the metadata index to be built first (POST /api/rag/metadata/build)."""
    try:
        result = await mcp_client.call_tool(
            "calibre_metadata_search",
            {"query": q, "top_k": top_k},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


# ── Full-text RAG (passage-level) ─────────────────────────────────────────────

@router.get("/retrieve")
async def rag_retrieve(
    q: str = Query(..., min_length=1, description="Natural-language query over book content"),
    top_k: int = Query(10, ge=1, le=50),
):
    """Semantic passage retrieval from full book content using LanceDB.
    Returns ranked passages with book attribution, page/chapter context.
    Requires the content index to be built first (POST /api/rag/content/build).

    Example: q='Zakalwe manipulated into accepting a mission'"""
    try:
        result = await mcp_client.call_tool(
            "rag_retrieve",
            {"query": q, "top_k": top_k},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


# ── Combined portmanteau RAG (metadata + content, agentic) ────────────────────

@router.post("/search")
async def calibre_rag_search(
    q: str = Query(..., min_length=1, description="Free-form library query"),
    top_k: int = Query(10, ge=1, le=50),
    mode: str = Query("auto", description="'metadata', 'content', or 'auto'"),
):
    """Combined RAG search via the calibre_rag portmanteau tool.
    Selects metadata vs. content search automatically based on query type,
    or use mode= to force a specific index."""
    try:
        result = await mcp_client.call_tool(
            "calibre_rag",
            {"query": q, "top_k": top_k, "mode": mode},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


# ── Media synopsis ────────────────────────────────────────────────────────────

@router.post("/synopsis/{book_id}")
async def rag_synopsis(
    book_id: int,
    spoilers: bool = Query(False, description="Include spoilers in synopsis"),
):
    """Generate a spoiler-aware synopsis for a book using RAG synthesis.
    The synopsis is constructed from the book's actual content index — not hallucinated.
    Requires the content index to be built for this book's library."""
    try:
        result = await mcp_client.call_tool(
            "media_synopsis",
            {"book_id": book_id, "spoilers": spoilers},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


# ── Critical reception (agentic web + library) ────────────────────────────────

@router.post("/critical-reception/{book_id}")
async def rag_critical_reception(book_id: int):
    """Synthesize external critical reviews and academic reception for a book
    using web search + library content (media_critical_reception tool)."""
    try:
        result = await mcp_client.call_tool(
            "media_critical_reception",
            {"book_id": book_id},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


# ── Deep research (multi-book thematic) ──────────────────────────────────────

@router.post("/deep-research")
async def rag_deep_research(
    topic: str = Query(..., min_length=3, description="Thematic topic for cross-book analysis"),
    limit: int = Query(5, ge=1, le=20, description="Max books to include in analysis"),
):
    """Multi-book comparative analysis on a thematic topic using full-text RAG.
    Synthesises passages across multiple books to produce a thematic essay."""
    try:
        result = await mcp_client.call_tool(
            "media_deep_research",
            {"topic": topic, "limit": limit},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


# ── Book deep research ────────────────────────────────────────────────────────

@router.post("/research/{book_id}")
async def rag_research_book(
    book_id: int,
    include_spoilers: bool = Query(False, description="Include plot spoilers"),
):
    """Deep external research on a single book from your Calibre library.

    Fetches Wikipedia (book + author), SF Encyclopedia (genre fiction),
    TVTropes (fiction), Anime News Network (manga/light novels), and Open Library
    (if ISBN present). Combines with your local Calibre data — rating, tags,
    personal notes, and RAG passages if the content index is built.

    Synthesises via LLM sampling into a structured markdown research report.

    Requires a sampling-capable MCP client context (Claude Desktop / Cursor).
    Response time: 10–30 seconds. The frontend should show a live status indicator.
    """
    try:
        result = await mcp_client.call_tool(
            "media_research_book",
            {"book_id": book_id, "include_spoilers": include_spoilers},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/metadata/export")
async def rag_metadata_export(
    output_path: str | None = Query(None, description="Optional output file path"),
):
    """Export all library metadata as JSON for use in external RAG pipelines."""
    try:
        args: dict = {}
        if output_path:
            args["output_path"] = output_path
        result = await mcp_client.call_tool("calibre_metadata_export_json", args)
        return result
    except Exception as e:
        raise handle_mcp_error(e)
