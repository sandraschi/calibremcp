"""Contained-works API: collection TOC index (Delphi-style omnibuses)."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


class IndexBody(BaseModel):
    book_id: int


@router.get("/scan")
async def scan_collections():
    """Metadata-only candidate sweep (no file reads)."""
    try:
        return await mcp_client.call_tool("inspect_contents", {"operation": "scan"})
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/index")
async def index_collection(body: IndexBody):
    """Parse one book's EPUB TOC into the sidecar index."""
    try:
        return await mcp_client.call_tool("inspect_contents", {"operation": "index", "book_id": body.book_id})
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/contents")
async def get_contents(book_id: int = Query(..., ge=1)):
    """Stored contained works for a book (auto-indexes collections on first read)."""
    try:
        return await mcp_client.call_tool("inspect_contents", {"operation": "contents", "book_id": book_id})
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/search")
async def search_contents(q: str = Query(..., min_length=3), limit: int = Query(50, ge=1, le=100)):
    """Find a work across indexed collections (e.g. wisteria lodge)."""
    try:
        return await mcp_client.call_tool("inspect_contents", {"operation": "search", "query": q, "limit": limit})
    except Exception as e:
        raise handle_mcp_error(e)
