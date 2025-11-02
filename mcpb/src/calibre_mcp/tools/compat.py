"""
Compatibility shim for MCPTool (FastMCP 2.13 migration).

FastMCP 2.13+ doesn't have MCPTool base class - tools should use @mcp.tool() decorator.
This shim provides temporary compatibility while tools are migrated.
"""

from typing import Dict, Any, Optional
from fastmcp import FastMCP


class MCPTool:
    """
    Compatibility shim for MCPTool base class.

    NOTE: This is temporary. Tools should be migrated to use @mcp.tool() decorator pattern.
    See: docs/mcp-technical/FASTMCP_2.13_PERSISTENT_STORAGE_PATTERN.md
    """

    def __init__(self, *args, **kwargs):
        """Initialize compatibility shim."""
        self.mcp: Optional[FastMCP] = None
        if args and isinstance(args[0], FastMCP):
            self.mcp = args[0]

    async def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Route to appropriate handler based on action.

        Subclasses should override this or implement action-specific handlers.
        """
        handler = getattr(self, f"handle_{action}", None)
        if not handler:
            return {"error": f"Unknown action: {action}", "success": False}

        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}

    def register(self, mcp: FastMCP) -> None:
        """
        Register tool methods with FastMCP instance.

        This should be replaced with @mcp.tool() decorators.
        """
        self.mcp = mcp
        # Tools should be migrated to use @mcp.tool() decorator directly
        # This is a temporary compatibility method
        pass


# Param compatibility - FastMCP 2.13 doesn't use Param, just function parameters
class Param:
    """Compatibility shim for Param (not needed in FastMCP 2.13)."""

    pass


# Export for backward compatibility
__all__ = ["MCPTool", "Param"]
