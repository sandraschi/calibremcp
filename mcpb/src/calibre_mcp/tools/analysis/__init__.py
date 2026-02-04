"""
Analysis tools initialization.

This module registers the manage_analysis portmanteau tool with the MCP server.
"""

# Import portmanteau tools (these are registered with @mcp.tool() and visible to Claude)
# Helper functions are imported but NOT registered (they have no @mcp.tool() decorator)
from .analysis_helpers import (  # noqa: F401
    analyze_library_health_helper,
    find_duplicate_books_helper,
    get_series_analysis_helper,
    get_tag_statistics_helper,
    reading_statistics_helper,
    unread_priority_list_helper,
)
from .analyze_library import analyze_library  # noqa: F401

# Legacy individual tools (deprecated - use manage_analysis portmanteau instead)
# These are kept as helper functions for backward compatibility but are NOT registered
# @mcp.tool() decorators have been removed - only manage_analysis portmanteau is visible to Claude
from .library_analysis import (  # noqa: F401
    analyze_library_health,
    find_duplicate_books,
    get_series_analysis,
    get_tag_statistics,
    reading_statistics,
    unread_priority_list,
)
from .manage_analysis import manage_analysis  # noqa: F401

# NOTE: These functions are NOT registered as tools (no @mcp.tool() decorator)
# They are kept as helpers for backward compatibility only
# Use manage_analysis(operation="...") instead
tools = []  # Empty - only portmanteau tool is registered

__all__ = ["manage_analysis", "analyze_library"]
