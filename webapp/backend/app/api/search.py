"""Search API endpoints."""

from fastapi import APIRouter, Query
from typing import Optional

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def search_books(
    query: Optional[str] = Query(None, description="Search query text"),
    author: Optional[str] = None,
    tag: Optional[str] = None,
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Advanced book search."""
    try:
        result = await mcp_client.call_tool(
            "query_books",
            {
                "operation": "search",
                "text": query,
                "author": author,
                "tag": tag,
                "min_rating": min_rating,
                "limit": limit,
                "offset": offset,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
