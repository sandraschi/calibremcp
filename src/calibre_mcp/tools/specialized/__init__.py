"""
Specialized tools initialization.

This module registers all specialized tools with the MCP server.
"""

from .specialized_tools import (
    japanese_book_organizer,
    it_book_curator,
    reading_recommendations
)

# List of tools to register
tools = [
    japanese_book_organizer,
    it_book_curator,
    reading_recommendations
]
