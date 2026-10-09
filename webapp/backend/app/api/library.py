"""Library management API endpoints."""

from fastapi import APIRouter, Body, Query

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def list_libraries():
    """List all available libraries."""
    try:
        result = await mcp_client.call_tool("manage_libraries", {"operation": "list"})
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/stats")
async def get_library_stats(library_name: str | None = Query(None)):
    """Get statistics for a library. Cached 60s."""
    from ..cache import _ttl_key, get_ttl_cached, set_ttl_cached

    key = _ttl_key("lib_stats", lib=library_name or "")
    cached = get_ttl_cached(key)
    if cached is not None:
        return cached
    try:
        args = {"operation": "stats"}
        if library_name:
            args["library_name"] = library_name
        result = await mcp_client.call_tool("manage_libraries", args)
        set_ttl_cached(key, result)
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/switch")
async def switch_library(data: dict = Body(...)):
    """Switch to a different library."""
    try:
        result = await mcp_client.call_tool(
            "manage_libraries", {"operation": "switch", "library_name": data.get("library_name")}
        )
        if result.get("success") and result.get("library_name"):
            from ..cache import update_current_library

            update_current_library(result["library_name"], result.get("library_path"))
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/search")
async def cross_library_search(data: dict = Body(...)):
    """Search for books across multiple libraries simultaneously."""
    try:
        args: dict = {"operation": "search", "query": data.get("query")}
        if data.get("libraries"):
            args["libraries"] = data.get("libraries")
        result = await mcp_client.call_tool("manage_libraries", args)
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/discover")
async def discover_libraries(data: dict | None = Body(None)):
    """Scan filesystem/CLI to find new Calibre libraries."""
    try:
        data = data or {}
        result = await mcp_client.call_tool(
            "manage_libraries",
            {
                "operation": "discover",
                "wizfile_allowed": data.get("wizfile_allowed", False),
                "calibre_cli_allowed": data.get("calibre_cli_allowed", False),
                "common_paths_allowed": data.get("common_paths_allowed", True),
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/test-connection")
async def test_library_connection():
    """Diagnostic check for library accessibility."""
    try:
        result = await mcp_client.call_tool("manage_libraries", {"operation": "test_connection"})
        return result
    except Exception as e:
        raise handle_mcp_error(e)
