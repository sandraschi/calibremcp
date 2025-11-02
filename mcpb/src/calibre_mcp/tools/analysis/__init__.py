"""
Analysis tools initialization.

This module registers all analysis and statistics tools with the MCP server.
"""

from .library_analysis import (
    get_tag_statistics,
    find_duplicate_books,
    get_series_analysis,
    analyze_library_health,
    unread_priority_list,
    reading_statistics,
)

# List of tools to register
tools = [
    get_tag_statistics,
    find_duplicate_books,
    get_series_analysis,
    analyze_library_health,
    unread_priority_list,
    reading_statistics,
]
