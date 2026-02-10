"""Search API endpoints."""

from fastapi import APIRouter, Query

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def search_books(
    query: str | None = Query(None, description="Search query text"),
    author: str | None = None,
    tag: str | None = None,
    min_rating: int | None = Query(None, ge=1, le=5),
    fulltext: bool = Query(False, description="Search inside book content (Calibre FTS)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Book search: metadata (default) or full-text inside book content."""
    try:
        if fulltext and query and query.strip():
            result = await mcp_client.call_tool(
                "search_fulltext",
                {
                    "query": query.strip(),
                    "limit": limit,
                    "offset": offset,
                    "include_snippets": True,
                    "enrich": True,
                },
            )
            if isinstance(result, dict):
                items = result.get("books") or []
                total = result.get("total") or 0
                snippets = result.get("snippets") or {}
                for b in items:
                    bid = b.get("id")
                    if bid is not None and bid in snippets:
                        b["snippet"] = snippets[bid]
                return {"items": items, "total": total}
            return result

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
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
