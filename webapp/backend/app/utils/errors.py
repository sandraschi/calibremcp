"""Error handling utilities."""

import logging

from fastapi import HTTPException

logger = logging.getLogger(__name__)


class MCPError(Exception):
    """Base exception for MCP-related errors."""

    pass


def handle_mcp_error(error: Exception) -> HTTPException:
    """Convert MCP errors to HTTP exceptions. Logs full traceback to app log."""
    logger.exception("MCP error: %s", error)
    if isinstance(error, MCPError):
        return HTTPException(status_code=500, detail=str(error))
    return HTTPException(status_code=500, detail=f"Internal server error: {str(error)}")
