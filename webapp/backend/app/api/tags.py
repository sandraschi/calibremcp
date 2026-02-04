"""Tags API endpoints."""

from fastapi import APIRouter, Body, Query

from ..cache import _ttl_key, get_libraries_cache, get_ttl_cached, set_ttl_cached
from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def list_tags(
    search: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("name", regex="^(name|book_count)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    unused_only: bool = Query(False),
    min_book_count: int | None = None,
    max_book_count: int | None = None,
):
    """List tags with filtering and pagination. Cached 60s for dropdown performance."""
    lib = get_libraries_cache().get("current_library") or ""
    key = _ttl_key(
        "tags",
        lib=lib,
        search=search or "",
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
        unused_only=unused_only,
        min_book_count=min_book_count or 0,
        max_book_count=max_book_count or 0,
    )
    cached = get_ttl_cached(key)
    if cached is not None:
        return cached
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "list",
                "search": search,
                "limit": limit,
                "offset": offset,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "unused_only": unused_only,
                "min_book_count": min_book_count,
                "max_book_count": max_book_count,
            },
        )
        set_ttl_cached(key, result)
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{tag_id}")
async def get_tag(tag_id: int):
    """Get tag details by ID."""
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "get",
                "tag_id": tag_id,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/")
async def create_tag(name: str = Body(...)):
    """Create a new tag."""
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "create",
                "name": name,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.put("/{tag_id}")
async def update_tag(tag_id: int, new_name: str = Body(...)):
    """Update (rename) a tag."""
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "update",
                "tag_id": tag_id,
                "new_name": new_name,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, force: bool = Query(False)):
    """Delete a tag."""
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "delete",
                "tag_id": tag_id,
                "force": force,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/duplicates/find")
async def find_duplicate_tags(similarity_threshold: float = Query(0.8, ge=0.0, le=1.0)):
    """Find duplicate or similar tags."""
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "find_duplicates",
                "similarity_threshold": similarity_threshold,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/merge")
async def merge_tags(
    source_tag_ids: list[int] = Body(...),
    target_tag_id: int = Body(...),
):
    """Merge multiple tags into a target tag."""
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "merge",
                "source_tag_ids": source_tag_ids,
                "target_tag_id": target_tag_id,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/unused/list")
async def get_unused_tags():
    """Get all tags not assigned to any books."""
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "get_unused",
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.delete("/unused/all")
async def delete_unused_tags():
    """Delete all unused tags."""
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "delete_unused",
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/stats/summary")
async def get_tag_statistics():
    """Get comprehensive tag statistics."""
    try:
        result = await mcp_client.call_tool(
            "manage_tags",
            {
                "operation": "statistics",
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
