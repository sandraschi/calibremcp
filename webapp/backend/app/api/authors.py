"""Authors API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def list_authors(
    query: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List authors with optional search."""
    try:
        result = await mcp_client.call_tool(
            "manage_authors",
            {
                "operation": "list",
                "query": query,
                "limit": limit,
                "offset": offset,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{author_id}")
async def get_author(author_id: int):
    """Get author details by ID."""
    try:
        result = await mcp_client.call_tool(
            "manage_authors",
            {
                "operation": "get",
                "author_id": author_id,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{author_id}/books")
async def get_author_books(
    author_id: int,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get all books by an author."""
    try:
        result = await mcp_client.call_tool(
            "manage_authors",
            {
                "operation": "get_books",
                "author_id": author_id,
                "limit": limit,
                "offset": offset,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/stats/summary")
async def get_author_stats():
    """Get author statistics."""
    try:
        result = await mcp_client.call_tool(
            "manage_authors",
            {
                "operation": "stats",
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/by-letter/{letter}")
async def get_authors_by_letter(letter: str):
    """Get authors whose names start with a specific letter."""
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(status_code=400, detail="Letter must be a single alphabetic character")
    try:
        result = await mcp_client.call_tool(
            "manage_authors",
            {
                "operation": "by_letter",
                "letter": letter.upper(),
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
