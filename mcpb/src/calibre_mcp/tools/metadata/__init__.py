"""
Metadata tools for Calibre MCP server.

This module provides tools for managing book metadata,
including fetching, updating, and validating metadata.
"""
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from ...models import Book, BookMetadata, BookFormat, BookStatus
from .. import tool

# Import the enhanced metadata tools
from .enhanced_metadata_tools import EnhancedMetadataTools

# Initialize the tools
enhanced_metadata = EnhancedMetadataTools()

# Register the tools
@tool(
    name="enhance_metadata",
    description="Enhance metadata for one or more books using various sources",
    parameters={
        "library_path": {"type": "string", "description": "Path to the Calibre library"},
        "book_ids": {"type": "array", "items": {"type": "string"}, "description": "List of book IDs to process (all books if None)"},
        "options": {
            "type": "object",
            "description": "Enhancement options",
            "properties": {
                "update_titles": {"type": "boolean", "default": True},
                "update_authors": {"type": "boolean", "default": True},
                "update_series": {"type": "boolean", "default": True},
                "update_publisher": {"type": "boolean", "default": False},
                "update_identifiers": {"type": "boolean", "default": True},
                "update_tags": {"type": "boolean", "default": True},
                "update_cover": {"type": "boolean", "default": False},
                "dry_run": {"type": "boolean", "default": True},
                "backup_before_changes": {"type": "boolean", "default": True}
            }
        }
    }
)
async def enhance_metadata(*args, **kwargs):
    """Enhance metadata for one or more books."""
    return await enhanced_metadata.enhance_metadata(*args, **kwargs)

@tool(
    name="standardize_metadata",
    description="Standardize metadata across books according to specified rules",
    parameters={
        "library_path": {"type": "string", "description": "Path to the Calibre library"},
        "book_ids": {"type": "array", "items": {"type": "string"}, "description": "List of book IDs to process (all books if None)"},
        "options": {
            "type": "object",
            "description": "Standardization options",
            "properties": {
                "title_case": {"type": "boolean", "default": True},
                "title_remove_series": {"type": "boolean", "default": True},
                "author_sort": {"type": "boolean", "default": True},
                "author_invert_names": {"type": "boolean", "default": True},
                "isbn_validate": {"type": "boolean", "default": True},
                "isbn_convert_to_13": {"type": "boolean", "default": True},
                "remove_special_chars": {"type": "boolean", "default": True},
                "normalize_unicode": {"type": "boolean", "default": True},
                "deduplicate_tags": {"type": "boolean", "default": True},
                "dry_run": {"type": "boolean", "default": True}
            }
        }
    }
)
async def standardize_metadata(*args, **kwargs):
    """Standardize metadata across books according to specified rules."""
    return await enhanced_metadata.standardize_metadata(*args, **kwargs)
