"""Error handling utilities."""

from fastapi import HTTPException


class MCPError(Exception):
    """Base exception for MCP-related errors."""

    pass


def handle_mcp_error(error: Exception) -> HTTPException:
    """Convert MCP errors to HTTP exceptions."""
    if isinstance(error, MCPError):
        return HTTPException(status_code=500, detail=str(error))
    return HTTPException(status_code=500, detail=f"Internal server error: {str(error)}")
