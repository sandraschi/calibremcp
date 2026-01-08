"""
File operations tools for CalibreMCP.

This module provides the manage_files portmanteau tool for comprehensive file operations.
"""

# Import portmanteau tool (this is registered with @mcp.tool() and visible to Claude)
from .manage_files import manage_files  # noqa: F401

# Helper functions are imported but NOT registered (they have no @mcp.tool() decorator)
# They are used internally by the portmanteau tool

# List of tools to register - ONLY portmanteau tool is registered
# Helper functions are NOT in this list (they have no @mcp.tool() decorator)
tools = [
    manage_files,  # Portmanteau tool (ONLY ONE visible to Claude)
]

__all__ = ["manage_files"]
