"""
Tag management tools for CalibreMCP.

This module provides the manage_tags portmanteau tool for comprehensive tag management.
"""

# Import portmanteau tool (this is registered with @mcp.tool() and visible to Claude)
from .manage_tags import manage_tags  # noqa: F401

# Helper functions are imported but NOT registered (they have no @mcp.tool() decorator)
# They are used internally by the portmanteau tool

__all__ = ["manage_tags"]
