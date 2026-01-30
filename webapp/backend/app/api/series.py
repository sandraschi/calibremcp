"""Series API endpoints."""

from fastapi import APIRouter, Query
from typing import Optional

from ..cache import get_libraries_cache, get_ttl_cached, set_ttl_cached, _ttl_key
from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def list_series(
    query: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    letter: Optional[str] = Query(None, description="Filter by first letter"),
):
    """List series with optional search. Cached 60s."""
    lib = get_libraries_cache().get("current_library") or ""
    key = _ttl_key("series", lib=lib, query=query or "", limit=limit, offset=offset, letter=letter or "")
    cached = get_ttl_cached(key)
    if cached is not None:
        return cached
    try:
        args = {"operation": "list", "limit": limit, "offset": offset}
        if query:
            args["query"] = query
        if letter:
            args["operation"] = "by_letter"
            args["letter"] = letter
        result = await mcp_client.call_tool("manage_series", args)
        set_ttl_cached(key, result)
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/stats")
async def get_series_stats():
    """Library-wide series statistics."""
    lib = get_libraries_cache().get("current_library") or ""
    key = _ttl_key("series_stats", lib=lib)
    cached = get_ttl_cached(key)
    if cached is not None:
        return cached
    try:
        result = await mcp_client.call_tool("manage_series", {"operation": "stats"})
        set_ttl_cached(key, result)
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{series_id}")
async def get_series(series_id: int):
    """Get series details by ID."""
    try:
        return await mcp_client.call_tool(
            "manage_series",
            {"operation": "get", "series_id": series_id}
        )
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{series_id}/books")
async def get_series_books(
    series_id: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Get all books in a series."""
    try:
        return await mcp_client.call_tool(
            "manage_series",
            {"operation": "get_books", "series_id": series_id, "limit": limit, "offset": offset}
        )
    except Exception as e:
        raise handle_mcp_error(e)
