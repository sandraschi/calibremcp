"""
Library operation tools for Calibre MCP server.

This module provides tools for working with the library as a whole,
including searching, filtering, and managing library settings.
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path

# Import all library operation tools to register them
from .list_books import list_books  # noqa: F401
from .series_manager import SeriesManager, SeriesInfo, SeriesMergeOptions
from .. import tool

# Re-export models for convenience
from ...models import Book, BookFormat, BookStatus  # noqa: F401

# Initialize tools
series_manager = SeriesManager()


# Register tools with MCP
@tool(
    name="analyze_series",
    description="Analyze series in the library and identify issues",
    parameters={
        "library_path": {"type": "string", "description": "Path to the Calibre library"},
        "update_metadata": {
            "type": "boolean",
            "description": "Whether to update book metadata with series information",
        },
    },
)
async def analyze_series(library_path: str, update_metadata: bool = False) -> Dict:
    """Analyze all series in the library."""
    return await series_manager.analyze_series(library_path, update_metadata)


@tool(
    name="fix_series_metadata",
    description="Fix common series metadata issues",
    parameters={
        "library_path": {"type": "string", "description": "Path to the Calibre library"},
        "dry_run": {"type": "boolean", "description": "If True, only show what would be changed"},
    },
)
async def fix_series_metadata(library_path: str, dry_run: bool = True) -> Dict:
    """Fix common series metadata issues."""
    return await series_manager.fix_series_metadata(library_path, dry_run)


@tool(
    name="merge_series",
    description="Merge one series into another",
    parameters={
        "library_path": {"type": "string", "description": "Path to the Calibre library"},
        "source_series": {"type": "string", "description": "Name of the series to merge from"},
        "target_series": {"type": "string", "description": "Name of the series to merge into"},
        "dry_run": {"type": "boolean", "description": "If True, only show what would be changed"},
    },
)
async def merge_series(
    library_path: str, source_series: str, target_series: str, dry_run: bool = True
) -> Dict:
    """Merge one series into another."""
    return await series_manager.merge_series(library_path, source_series, target_series, dry_run)
