"""
Shared utilities for MCP tools.

This package contains common utilities used across multiple tool modules.
"""

from .error_handling import handle_tool_error, format_error_response

__all__ = [
    "handle_tool_error",
    "format_error_response",
]

