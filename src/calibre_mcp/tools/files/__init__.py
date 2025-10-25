"""
File operations tools initialization.

This module registers all file operations tools with the MCP server.
"""

from .file_operations import (
    convert_book_format,
    download_book,
    bulk_format_operations
)

# List of tools to register
tools = [
    convert_book_format,
    download_book,
    bulk_format_operations
]
