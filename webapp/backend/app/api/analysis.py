"""Library analysis API endpoints."""

from fastapi import APIRouter

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/tag-statistics")
async def get_tag_statistics():
    """Analyze tag usage and suggest cleanup operations."""
    try:
        result = await mcp_client.call_tool(
            "analyze_library",
            {
                "operation": "tag_statistics",
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/duplicates")
async def find_duplicate_books():
    """Find potentially duplicate books."""
    try:
        result = await mcp_client.call_tool(
            "analyze_library",
            {
                "operation": "duplicates",
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/series")
async def analyze_series():
    """Analyze book series completion and reading order."""
    try:
        result = await mcp_client.call_tool(
            "analyze_library",
            {
                "operation": "series",
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/health")
async def check_library_health():
    """Perform comprehensive library health check."""
    try:
        result = await mcp_client.call_tool(
            "analyze_library",
            {
                "operation": "health",
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/unread-priority")
async def get_unread_priority():
    """Get prioritized list of unread books."""
    try:
        result = await mcp_client.call_tool(
            "analyze_library",
            {
                "operation": "unread_priority",
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/reading-stats")
async def get_reading_statistics():
    """Generate personal reading analytics."""
    try:
        result = await mcp_client.call_tool(
            "analyze_library",
            {
                "operation": "reading_stats",
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
