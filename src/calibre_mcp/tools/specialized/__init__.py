"""
Specialized tools for CalibreMCP.

NOTE: Only portmanteau tools are registered with @mcp.tool() and visible to Claude.
Helper functions are imported but NOT registered (they have no @mcp.tool() decorator).
"""

# Helper functions (no @mcp.tool(); kept for reference / future manage_specialized)
from .specialized_tools import (
    it_book_curator_helper,  # noqa: F401
    japanese_book_organizer_helper,  # noqa: F401
    reading_recommendations_helper,  # noqa: F401
)

# Portmanteau tool: optional until manage_specialized.py exists
try:
    from .manage_specialized import manage_specialized  # noqa: F401
    tools = [manage_specialized]
    __all__ = ["manage_specialized", "it_book_curator_helper", "japanese_book_organizer_helper", "reading_recommendations_helper"]
except ModuleNotFoundError:
    manage_specialized = None  # type: ignore[misc, assignment]
    tools = []
    __all__ = ["it_book_curator_helper", "japanese_book_organizer_helper", "reading_recommendations_helper"]
