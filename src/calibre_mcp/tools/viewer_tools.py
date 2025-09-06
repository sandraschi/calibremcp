"""
MCP tools for book viewing operations.
"""
from typing import Dict, Any, Optional, List, BinaryIO
from pydantic import BaseModel, Field
from ..services.viewer_service import (
    viewer_service, 
    ViewerState, 
    ViewerPage, 
    ViewerMetadata
)
from .base_tool import BaseTool, mcp_tool

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
        None, 
        description="Reading direction (ltr, rtl, vertical)"
    )
    page_layout: Optional[str] = Field(
        None, 
        description="Page layout mode (single, double, auto)"
    )
    zoom_mode: Optional[str] = Field(
        None, 
        description="Zoom mode (fit-width, fit-height, fit-both, original, custom)"
    )
    zoom_level: Optional[float] = Field(
        None, 
        ge=0.1, 
        le=5.0, 
        description="Zoom level (1.0 = 100%)"
    )

class ViewerTools(BaseTool):
    """MCP tools for book viewing operations."""
    
    @mcp_tool(
        name="open_book",
        description="Open a book in the viewer",
        input_model=OpenBookInput,
        output_model=Dict[str, Any]
    )
    async def open_book(self, book_id: int, file_path: str) -> Dict[str, Any]:
        """
        Open a book in the viewer and return its metadata and initial state.
        
        Args:
            book_id: The ID of the book to open
            file_path: Path to the book file
            
        Returns:
            Dictionary containing book metadata and initial viewer state
        """
        # This will initialize the viewer if it doesn't exist
        metadata = viewer_service.get_metadata(book_id, file_path)
        state = viewer_service.get_state(book_id, file_path)
        
        return {
            "metadata": metadata.dict(),
            "state": state.dict(),
            "pages": {
                "total": metadata.page_count,
                "first_page": viewer_service.get_page(book_id, file_path, 0).dict()
            }
        }
    
    @mcp_tool(
        name="get_page",
        description="Get a specific page from a book",
        input_model=GetPageInput,
        output_model=ViewerPage
    )
    async def get_page(
        self, 
        book_id: int, 
        file_path: str, 
        page_number: int = 0
    ) -> Dict[str, Any]:
        """
        Get a specific page from a book.
        
        Args:
            book_id: The ID of the book
            file_path: Path to the book file
            page_number: Page number to retrieve (0-based)
            
        Returns:
            ViewerPage object containing page information
        """
        return viewer_service.get_page(book_id, file_path, page_number).dict()
    
    @mcp_tool(
        name="get_metadata",
        description="Get metadata for a book",
        input_model=OpenBookInput,
        output_model=ViewerMetadata
    )
    async def get_metadata(
        self, 
        book_id: int, 
        file_path: str
    ) -> Dict[str, Any]:
        """
        Get metadata for a book.
        
        Args:
            book_id: The ID of the book
            file_path: Path to the book file
            
        Returns:
            ViewerMetadata object containing book metadata
        """
        return viewer_service.get_metadata(book_id, file_path).dict()
    
    @mcp_tool(
        name="get_state",
        description="Get the current viewer state for a book",
        input_model=OpenBookInput,
        output_model=ViewerState
    )
    async def get_state(
        self, 
        book_id: int, 
        file_path: str
    ) -> Dict[str, Any]:
        """
        Get the current viewer state for a book.
        
        Args:
            book_id: The ID of the book
            file_path: Path to the book file
            
        Returns:
            ViewerState object containing the current state
        """
        return viewer_service.get_state(book_id, file_path).dict()
    
    @mcp_tool(
        name="update_state",
        description="Update the viewer state for a book",
        input_model=UpdateStateInput,
        output_model=ViewerState
    )
    async def update_state(
        self, 
        book_id: int, 
        file_path: str, 
        current_page: Optional[int] = None,
        reading_direction: Optional[str] = None,
        page_layout: Optional[str] = None,
        zoom_mode: Optional[str] = None,
        zoom_level: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update the viewer state for a book.
        
        Args:
            book_id: The ID of the book
            file_path: Path to the book file
            current_page: Current page number to set
            reading_direction: Reading direction to set (ltr, rtl, vertical)
            page_layout: Page layout mode to set (single, double, auto)
            zoom_mode: Zoom mode to set (fit-width, fit-height, fit-both, original, custom)
            zoom_level: Zoom level to set (1.0 = 100%)
            
        Returns:
            Updated ViewerState object
        """
        state_updates = {}
        if current_page is not None:
            state_updates['current_page'] = current_page
        if reading_direction is not None:
            state_updates['reading_direction'] = reading_direction
        if page_layout is not None:
            state_updates['page_layout'] = page_layout
        if zoom_mode is not None:
            state_updates['zoom_mode'] = zoom_mode
        if zoom_level is not None:
            state_updates['zoom_level'] = zoom_level
            
        return viewer_service.update_state(book_id, file_path, **state_updates).dict()
    
    @mcp_tool(
        name="close_viewer",
        description="Close a viewer and clean up resources",
        input_model=OpenBookInput,
        output_model=Dict[str, bool]
    )
    async def close_viewer(self, book_id: int, file_path: str) -> Dict[str, bool]:
        """
        Close a viewer and clean up resources.
        
        Args:
            book_id: The ID of the book
            file_path: Path to the book file (unused, but kept for consistency)
            
        Returns:
            Dictionary with success status
        """
        viewer_service.close_viewer(book_id)
        return {"success": True}
