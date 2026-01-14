"""Metadata API endpoints."""

from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/show")
async def show_metadata(
    query: Optional[str] = Query(None, description="Book title or partial title"),
    author: Optional[str] = None,
    open_browser: bool = Query(False, description="Open HTML popup in browser"),
):
    """Show comprehensive book metadata."""
    try:
        result = await mcp_client.call_tool(
            "manage_metadata",
            {
                "operation": "show",
                "query": query,
                "author": author,
                "open_browser": open_browser,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/update")
async def update_metadata(updates: List[Dict[str, Any]] = Body(...)):
    """Update metadata for single or multiple books."""
    try:
        result = await mcp_client.call_tool(
            "manage_metadata",
            {
                "operation": "update",
                "updates": updates,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/organize-tags")
async def organize_tags():
    """AI-powered tag organization and cleanup suggestions."""
    try:
        result = await mcp_client.call_tool(
            "manage_metadata",
            {
                "operation": "organize_tags",
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/fix-issues")
async def fix_metadata_issues():
    """Automatically fix common metadata problems."""
    try:
        result = await mcp_client.call_tool(
            "manage_metadata",
            {
                "operation": "fix_issues",
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
