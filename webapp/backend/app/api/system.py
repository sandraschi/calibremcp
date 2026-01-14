"""System management API endpoints."""

from fastapi import APIRouter, Query
from typing import Optional

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/help")
async def get_help(
    level: str = Query("basic", regex="^(basic|intermediate|advanced|expert)$"),
    topic: Optional[str] = None,
):
    """Get comprehensive help system."""
    try:
        result = await mcp_client.call_tool(
            "manage_system",
            {
                "operation": "help",
                "level": level,
                "topic": topic,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/status")
async def get_system_status(
    status_level: str = Query("basic", regex="^(basic|intermediate|advanced|diagnostic)$"),
    focus: Optional[str] = None,
):
    """Get system status and diagnostic information."""
    try:
        result = await mcp_client.call_tool(
            "manage_system",
            {
                "operation": "status",
                "status_level": status_level,
                "focus": focus,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/tools")
async def list_tools(category: Optional[str] = None):
    """List all available tools."""
    try:
        result = await mcp_client.call_tool(
            "manage_system",
            {
                "operation": "list_tools",
                "category": category,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/tools/{tool_name}/help")
async def get_tool_help(
    tool_name: str,
    tool_help_level: str = Query("basic", regex="^(basic|intermediate|advanced|expert)$"),
):
    """Get detailed help for a specific tool."""
    try:
        result = await mcp_client.call_tool(
            "manage_system",
            {
                "operation": "tool_help",
                "tool_name": tool_name,
                "tool_help_level": tool_help_level,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/health")
async def health_check():
    """Machine-readable health check for monitoring."""
    try:
        result = await mcp_client.call_tool(
            "manage_system",
            {
                "operation": "health_check",
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
