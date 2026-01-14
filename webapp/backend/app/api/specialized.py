"""Specialized library organization API endpoints."""

from fastapi import APIRouter

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/japanese-organizer")
async def organize_japanese_library():
    """Organize Japanese library for maximum cultural efficiency."""
    try:
        result = await mcp_client.call_tool(
            "manage_specialized",
            {
                "operation": "japanese_organizer",
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/it-curator")
async def curate_it_books():
    """IT book curation for programming and technology collection."""
    try:
        result = await mcp_client.call_tool(
            "manage_specialized",
            {
                "operation": "it_curator",
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/reading-recommendations")
async def get_reading_recommendations():
    """Austrian efficiency reading recommendations."""
    try:
        result = await mcp_client.call_tool(
            "manage_specialized",
            {
                "operation": "reading_recommendations",
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
