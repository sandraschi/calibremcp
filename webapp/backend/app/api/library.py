"""Library management API endpoints."""

from fastapi import APIRouter, Query, Body
from typing import Optional

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def list_libraries():
    """List all available libraries."""
    try:
        result = await mcp_client.call_tool(
            "manage_libraries",
            {"operation": "list"}
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/stats")
async def get_library_stats(library_name: Optional[str] = Query(None)):
    """Get statistics for a library."""
    try:
        args = {"operation": "stats"}
        if library_name:
            args["library_name"] = library_name
        result = await mcp_client.call_tool(
            "manage_libraries",
            args
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/switch")
async def switch_library(data: dict = Body(...)):
    """Switch to a different library."""
    try:
        result = await mcp_client.call_tool(
            "manage_libraries",
            {
                "operation": "switch",
                "library_name": data.get("library_name")
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
