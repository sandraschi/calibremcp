"""Smart collections API endpoints."""

from fastapi import APIRouter, Query, Body
from typing import Optional, Dict, Any, List

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def list_collections():
    """List all smart collections."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "list",
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{collection_id}")
async def get_collection(collection_id: str):
    """Get collection details by ID."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "get",
                "collection_id": collection_id,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/")
async def create_collection(collection_data: Dict[str, Any] = Body(...)):
    """Create a new smart collection with rules."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "create",
                "collection_data": collection_data,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/series")
async def create_series_collection(
    name: str = Body(...),
    series_name: str = Body(...),
):
    """Create a collection for all books in a specific series."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "create_series",
                "name": name,
                "series_name": series_name,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/recently-added")
async def create_recently_added_collection(
    name: Optional[str] = Body(None),
    days: int = Body(30, ge=1),
):
    """Create a collection for books added recently."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "create_recently_added",
                "name": name,
                "days": days,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/unread")
async def create_unread_collection(name: Optional[str] = Body(None)):
    """Create a collection for unread books."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "create_unread",
                "name": name,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/ai-recommended")
async def create_ai_recommended_collection(name: Optional[str] = Body(None)):
    """Create a collection with AI-recommended books."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "create_ai_recommended",
                "name": name,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.put("/{collection_id}")
async def update_collection(
    collection_id: str,
    updates: Dict[str, Any] = Body(...),
):
    """Update a smart collection's rules or metadata."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "update",
                "collection_id": collection_id,
                "updates": updates,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.delete("/{collection_id}")
async def delete_collection(collection_id: str):
    """Delete a smart collection."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "delete",
                "collection_id": collection_id,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{collection_id}/query")
async def query_collection(
    collection_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Query books that match a collection's rules."""
    try:
        result = await mcp_client.call_tool(
            "manage_smart_collections",
            {
                "operation": "query",
                "collection_id": collection_id,
                "limit": limit,
                "offset": offset,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
