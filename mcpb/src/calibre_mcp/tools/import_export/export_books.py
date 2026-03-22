"""
Re-export export_books for MCP client preload.

The mcp client expects calibre_mcp.tools.import_export.export_books module
with export_books attribute. This module provides that.
"""

from .export_books_portmanteau import export_books  # noqa: F401

__all__ = ["export_books"]
