"""
Metadata management tools initialization.

This module registers all metadata management tools with the MCP server.
"""

from .metadata_management import (
    update_book_metadata,
    auto_organize_tags,
    fix_metadata_issues
)

# List of tools to register
tools = [
    update_book_metadata,
    auto_organize_tags,
    fix_metadata_issues
]