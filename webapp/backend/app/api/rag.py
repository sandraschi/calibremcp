"""RAG API: metadata index build and semantic search."""

import json
from pathlib import Path

from fastapi import APIRouter, Query

from ..cache import get_libraries_cache
from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()

PROGRESS_FILENAME = ".build_progress.json"


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
    """Start build or rebuild of the LanceDB metadata index in background. Poll GET /metadata/build/status for progress."""
    try:
        result = await mcp_client.call_tool(
            "calibre_metadata_index_build",
            {"force_rebuild": force_rebuild},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/metadata/search")
async def rag_metadata_search(
    q: str = Query(..., min_length=1, description="Natural-language search query"),
    top_k: int = Query(10, ge=1, le=50),
):
    """Semantic search over book metadata (title, authors, tags, comments)."""
    try:
        result = await mcp_client.call_tool(
            "calibre_metadata_search",
            {"query": q, "top_k": top_k},
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
