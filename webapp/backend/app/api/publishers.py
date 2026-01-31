"""Publishers API endpoints. Uses DatabaseService (same as books, authors, tags)."""

from fastapi import APIRouter, Query
from typing import Optional

from ..cache import get_libraries_cache, get_ttl_cached, set_ttl_cached, _ttl_key
from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def list_publishers(
    query: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List publishers with filtering and pagination. Cached 60s. Uses active library."""
    lib = get_libraries_cache().get("current_library") or ""
    key = _ttl_key("publishers", lib=lib, query=query or "", limit=limit, offset=offset)
    cached = get_ttl_cached(key)
    if cached is not None:
        return cached
    try:
        result = await mcp_client.call_tool(
            "manage_publishers",
            {
                "operation": "list",
                "query": query,
                "limit": limit,
                "offset": offset,
            },
        )
        set_ttl_cached(key, result)
        return result
    except Exception as e:
        raise handle_mcp_error(e)
