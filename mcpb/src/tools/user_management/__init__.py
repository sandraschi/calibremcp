"""
User management tools for Calibre MCP server.

This module provides tools for managing users, permissions, and authentication.
"""

# Import portmanteau tool (this is registered with @mcp.tool() and visible to Claude)
from .manage_users import manage_users  # noqa: F401

__all__ = ["manage_users"]
