"""
Viewer tools - DEPRECATED: Use manage_viewer portmanteau tool instead.

This module contains helper models used by the manage_viewer portmanteau tool.
The ViewerTools BaseTool class has been removed - all functionality is now in manage_viewer.

All 7 operations (open, get_page, get_metadata, get_state, update_state, close, open_file)
are now available via manage_viewer(operation="...")
"""

from typing import Optional
from pydantic import BaseModel, Field
from ..logging_config import get_logger

logger = get_logger("calibremcp.tools.viewer_tools")


class OpenBookInput(BaseModel):
    """Input model for opening a book in the viewer."""

    book_id: int = Field(..., description="ID of the book to open")
    file_path: str = Field(..., description="Path to the book file")


class GetPageInput(BaseModel):
    """Input model for getting a specific page."""

    book_id: int = Field(..., description="ID of the book")
    file_path: str = Field(..., description="Path to the book file")
    page_number: int = Field(0, ge=0, description="Page number (0-based)")


class UpdateStateInput(BaseModel):
    """Input model for updating viewer state."""

    book_id: int = Field(..., description="ID of the book")
    file_path: str = Field(..., description="Path to the book file")
    current_page: Optional[int] = Field(None, ge=0, description="Current page number")
    reading_direction: Optional[str] = Field(
        None, description="Reading direction (ltr, rtl, vertical)"
    )
    page_layout: Optional[str] = Field(None, description="Page layout mode (single, double, auto)")
    zoom_mode: Optional[str] = Field(
        None, description="Zoom mode (fit-width, fit-height, fit-both, original, custom)"
    )
    zoom_level: Optional[float] = Field(None, ge=0.1, le=5.0, description="Zoom level (1.0 = 100%)")
