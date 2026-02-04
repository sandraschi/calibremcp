"""Viewer API endpoints."""

from fastapi import APIRouter, Body, Query

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.post("/open-random")
async def open_random_book(
    author: str | None = None,
    tag: str | None = None,
    series: str | None = None,
    format_preference: str = Query("EPUB", description="Preferred file format"),
):
    """Open a random book matching criteria."""
    try:
        result = await mcp_client.call_tool(
            "manage_viewer",
            {
                "operation": "open_random",
                "author": author,
                "tag": tag,
                "series": series,
                "format_preference": format_preference,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/open")
async def open_book(data: dict = Body(...)):
    """Open a book in the viewer."""
    try:
        result = await mcp_client.call_tool(
            "manage_viewer",
            {
                "operation": "open",
                "book_id": data.get("book_id"),
                "file_path": data.get("file_path"),
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/page")
async def get_page(
    book_id: int = Query(..., description="Book ID"),
    file_path: str = Query(..., description="Path to book file"),
    page_number: int = Query(0, description="Zero-based page number"),
):
    """Get a specific page from a book."""
    try:
        result = await mcp_client.call_tool(
            "manage_viewer",
            {
                "operation": "get_page",
                "book_id": book_id,
                "file_path": file_path,
                "page_number": page_number,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/metadata")
async def get_viewer_metadata(
    book_id: int = Query(..., description="Book ID"),
    file_path: str = Query(..., description="Path to book file"),
):
    """Get comprehensive metadata for a book."""
    try:
        result = await mcp_client.call_tool(
            "manage_viewer",
            {
                "operation": "get_metadata",
                "book_id": book_id,
                "file_path": file_path,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/state")
async def get_viewer_state(
    book_id: int = Query(..., description="Book ID"),
    file_path: str = Query(..., description="Path to book file"),
):
    """Get the current viewer state."""
    try:
        result = await mcp_client.call_tool(
            "manage_viewer",
            {
                "operation": "get_state",
                "book_id": book_id,
                "file_path": file_path,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.put("/state")
async def update_viewer_state(data: dict = Body(...)):
    """Update viewer state (save reading progress)."""
    try:
        result = await mcp_client.call_tool(
            "manage_viewer",
            {
                "operation": "update_state",
                "book_id": data.get("book_id"),
                "file_path": data.get("file_path"),
                "current_page": data.get("current_page"),
                "reading_direction": data.get("reading_direction"),
                "page_layout": data.get("page_layout"),
                "zoom_mode": data.get("zoom_mode"),
                "zoom_level": data.get("zoom_level"),
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/close")
async def close_viewer(data: dict = Body(...)):
    """Close a viewer session."""
    try:
        result = await mcp_client.call_tool(
            "manage_viewer",
            {
                "operation": "close",
                "book_id": data.get("book_id"),
                "file_path": data.get("file_path"),
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/open-file")
async def open_book_file(data: dict = Body(...)):
    """Open a book file with the system's default application."""
    try:
        result = await mcp_client.call_tool(
            "manage_viewer",
            {
                "operation": "open_file",
                "book_id": data.get("book_id"),
                "file_path": data.get("file_path"),
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
