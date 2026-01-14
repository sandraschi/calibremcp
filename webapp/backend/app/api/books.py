"""Book API endpoints."""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def list_books(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    author: Optional[str] = None,
    tag: Optional[str] = None,
    text: Optional[str] = None,
):
    """List books with optional filters."""
    try:
        result = await mcp_client.call_tool(
            "query_books",
            {
                "operation": "search",
                "limit": limit,
                "offset": offset,
                "author": author,
                "tag": tag,
                "text": text,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{book_id}")
async def get_book(book_id: int):
    """Get book details by ID."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "get",
                "book_id": str(book_id),
                "include_metadata": True,
                "include_formats": True,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{book_id}/details")
async def get_book_details(book_id: int):
    """Get complete metadata and file information for a book."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "details",
                "book_id": str(book_id),
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/")
async def add_book(data: dict = Body(...)):
    """Add a new book to the library."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "add",
                "file_path": data.get("file_path"),
                "metadata": data.get("metadata"),
                "fetch_metadata": data.get("fetch_metadata", True),
                "convert_to": data.get("convert_to"),
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.put("/{book_id}")
async def update_book(book_id: int, data: dict = Body(...)):
    """Update a book's metadata and properties."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "update",
                "book_id": str(book_id),
                "metadata": data.get("metadata"),
                "status": data.get("status"),
                "progress": data.get("progress"),
                "cover_path": data.get("cover_path"),
                "update_timestamp": data.get("update_timestamp", True),
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    delete_files: bool = Query(True, description="Delete files from disk"),
    force: bool = Query(False, description="Skip dependency checks"),
):
    """Delete a book from the library."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "delete",
                "book_id": str(book_id),
                "delete_files": delete_files,
                "force": force,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
