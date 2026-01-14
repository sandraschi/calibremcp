"""Comments API endpoints."""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/{book_id}")
async def get_comment(book_id: str):
    """Get comment for a book."""
    try:
        result = await mcp_client.call_tool(
            "manage_comments",
            {
                "operation": "read",
                "book_id": book_id,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/{book_id}")
async def create_comment(book_id: str, text: str = Body(...)):
    """Create a new comment for a book."""
    try:
        result = await mcp_client.call_tool(
            "manage_comments",
            {
                "operation": "create",
                "book_id": book_id,
                "text": text,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.put("/{book_id}")
async def update_comment(book_id: str, text: str = Body(...)):
    """Update a comment (replaces entire text)."""
    try:
        result = await mcp_client.call_tool(
            "manage_comments",
            {
                "operation": "update",
                "book_id": book_id,
                "text": text,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.patch("/{book_id}")
async def append_comment(book_id: str, text: str = Body(...)):
    """Append text to existing comment."""
    try:
        result = await mcp_client.call_tool(
            "manage_comments",
            {
                "operation": "append",
                "book_id": book_id,
                "text": text,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.delete("/{book_id}")
async def delete_comment(book_id: str):
    """Delete a comment."""
    try:
        result = await mcp_client.call_tool(
            "manage_comments",
            {
                "operation": "delete",
                "book_id": book_id,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
