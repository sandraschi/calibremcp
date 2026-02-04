"""
Author management tools for CalibreMCP.

This module provides the manage_authors portmanteau tool for comprehensive author management.
"""

# Import portmanteau tool (this is registered with @mcp.tool() and visible to Claude)
# Helper functions are imported but NOT registered (they have no @mcp.tool() decorator)
from .author_helpers import (  # noqa: F401
    get_author_books_helper,
    get_author_helper,
    get_author_stats_helper,
    get_authors_by_letter_helper,
    list_authors_helper,
)
from .manage_authors import manage_authors  # noqa: F401

__all__ = ["manage_authors"]
