"""File operations API endpoints."""

from typing import Any

from fastapi import APIRouter, Body, Query

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.post("/convert")
async def convert_book(
    conversion_requests: list[dict[str, Any]] = Body(...),
):
    """Convert book formats."""
    try:
        result = await mcp_client.call_tool(
            "manage_files",
            {
                "operation": "convert",
                "conversion_requests": conversion_requests,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{book_id}/download")
async def download_book(
    book_id: int,
    format_preference: str = Query("EPUB", regex="^(EPUB|PDF|MOBI|AZW3|TXT)$"),
):
    """Download a book file in the specified format."""
    try:
        result = await mcp_client.call_tool(
            "manage_files",
            {
                "operation": "download",
                "book_id": book_id,
                "format_preference": format_preference,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/bulk")
async def bulk_file_operations(
    operation_type: str = Body(..., regex="^(convert|validate|cleanup)$"),
    target_format: str | None = None,
    book_ids: list[int] | None = None,
):
    """Perform bulk file operations."""
    try:
        result = await mcp_client.call_tool(
            "manage_files",
            {
                "operation": "bulk",
                "operation_type": operation_type,
                "target_format": target_format,
                "book_ids": book_ids,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
