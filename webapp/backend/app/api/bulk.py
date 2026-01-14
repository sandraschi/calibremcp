"""Bulk operations API endpoints."""

from fastapi import APIRouter, Body
from typing import Optional, Dict, Any, List

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.post("/metadata/update")
async def bulk_update_metadata(
    book_ids: List[int] = Body(...),
    updates: Dict[str, Any] = Body(...),
    batch_size: int = Body(10, ge=1, le=100),
):
    """Update metadata for multiple books in bulk."""
    try:
        result = await mcp_client.call_tool(
            "manage_bulk_operations",
            {
                "operation": "update_metadata",
                "book_ids": book_ids,
                "updates": updates,
                "batch_size": batch_size,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/export")
async def bulk_export_books(
    book_ids: List[int] = Body(...),
    export_path: str = Body(...),
    format: str = Body("directory", regex="^(directory|zip)$"),
):
    """Export multiple books to a specified location."""
    try:
        result = await mcp_client.call_tool(
            "manage_bulk_operations",
            {
                "operation": "export",
                "book_ids": book_ids,
                "export_path": export_path,
                "format": format,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/delete")
async def bulk_delete_books(
    book_ids: List[int] = Body(...),
    delete_files: bool = Body(True),
):
    """Delete multiple books from the library."""
    try:
        result = await mcp_client.call_tool(
            "manage_bulk_operations",
            {
                "operation": "delete",
                "book_ids": book_ids,
                "delete_files": delete_files,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/convert")
async def bulk_convert_books(
    book_ids: List[int] = Body(...),
    target_format: str = Body(...),
    output_path: Optional[str] = Body(None),
):
    """Convert multiple books to a different format."""
    try:
        result = await mcp_client.call_tool(
            "manage_bulk_operations",
            {
                "operation": "convert",
                "book_ids": book_ids,
                "target_format": target_format,
                "output_path": output_path,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
