"""
Help tools for Calibre MCP server.

This module provides tools for getting help and documentation
about the Calibre MCP server and its features.
"""

# Import all help tools to register them
from .help import help_tool  # noqa: F401

# Re-export models for convenience
from ...models import Book, BookFormat, BookStatus  # noqa: F401
