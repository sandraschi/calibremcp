"""
Calibre MCP - A FastMCP 2.10 compliant MCP server for Calibre ebook management.

This module provides a Model-Controller-Protocol (MCP) server interface for
interacting with Calibre libraries, allowing for programmatic management of
ebooks, metadata, and library operations.
"""

__version__ = "1.0.0"
__author__ = "Sandra"
__email__ = "sandra@windsurf.io"

# Import main components
from calibremcp.mcp_server import CalibreMCPServer  # noqa: F401

__all__ = ["CalibreMCPServer"]
