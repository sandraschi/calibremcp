"""Canon coverage API: holdings checks against external canon lists."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


class CheckListBody(BaseModel):
    items: list[dict] = []
    limit: int = 100


@router.get("/canons")
async def list_canons():
    """Enumerate available canon lists."""
    try:
        return await mcp_client.call_tool("canon_coverage", {"operation": "list_canons"})
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/gutenberg-top100")
async def gutenberg_top100(limit: int = Query(100, ge=1, le=100)):
    """Live Gutenberg Top 100 checked against library holdings."""
    try:
        return await mcp_client.call_tool("canon_coverage", {"operation": "gutenberg_top100", "limit": limit})
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/nobel-laureates")
async def nobel_laureates():
    """Live Nobel literature laureates checked against library holdings (author level)."""
    try:
        return await mcp_client.call_tool("canon_coverage", {"operation": "nobel_laureates"})
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/check-list")
async def check_list(body: CheckListBody):
    """Check caller-supplied [{title, author?}] against holdings (max 200)."""
    try:
        return await mcp_client.call_tool(
            "canon_coverage",
            {"operation": "check_list", "items": body.items, "limit": body.limit},
        )
    except Exception as e:
        raise handle_mcp_error(e)
