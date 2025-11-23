"""
Import/Export tools for Calibre MCP server.

This module provides the export_books portmanteau tool for comprehensive book export.
"""

# Import portmanteau tool (this is registered with @mcp.tool() and visible to Claude)
from .export_books_portmanteau import export_books  # noqa: F401

# Helper functions are imported but NOT registered (they have no @mcp.tool() decorator)
# They are used internally by the portmanteau tool

__all__ = ["export_books"]
