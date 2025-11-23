"""
Service for handling book viewing operations.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field
from ..viewers import get_viewer


class ViewerState(BaseModel):
    """Current state of the viewer."""

    current_page: int = Field(0, ge=0, description="Current page number (0-based)")
    total_pages: int = Field(0, ge=0, description="Total number of pages")
    reading_direction: str = Field("ltr", description="Reading direction (ltr, rtl, vertical)")
    page_layout: str = Field("single", description="Page layout mode (single, double, auto)")
    zoom_mode: str = Field(
        "fit-width", description="Zoom mode (fit-width, fit-height, fit-both, original, custom)"
    )
    zoom_level: float = Field(1.0, ge=0.1, le=5.0, description="Zoom level (1.0 = 100%)")
    scroll_position: Tuple[float, float] = Field(
        (0, 0), description="Current scroll position (x, y)"
    )
    bookmarks: List[Dict[str, Any]] = Field(default_factory=list, description="List of bookmarks")
    reading_progress: float = Field(
        0.0, ge=0.0, le=100.0, description="Reading progress percentage"
    )
    show_controls: bool = Field(True, description="Whether to show controls")
    show_thumbnails: bool = Field(True, description="Whether to show thumbnails")
    show_page_numbers: bool = Field(True, description="Whether to show page numbers")
    background_color: str = Field("#000000", description="Background color in hex")
    custom_css: str = Field("", description="Custom CSS for the viewer")


class ViewerPage(BaseModel):
    """A page in the viewer."""

    number: int = Field(..., ge=0, description="Page number (0-based)")
    width: Optional[int] = Field(None, description="Page width in pixels")
    height: Optional[int] = Field(None, description="Page height in pixels")
    url: Optional[str] = Field(None, description="URL to access the page image")
    thumbnail_url: Optional[str] = Field(None, description="URL to access the thumbnail")


class ViewerMetadata(BaseModel):
    """Metadata for the book being viewed."""

    title: str = Field("", description="Book title")
    author: str = Field("", description="Book author")
    series: str = Field("", description="Series name")
    volume: str = Field("", description="Volume number")
    publisher: str = Field("", description="Publisher name")
    year: Optional[int] = Field(None, description="Publication year")
    page_count: int = Field(0, description="Total number of pages")
    format: str = Field("", description="File format (epub, pdf, cbz, etc.)")
    cover_url: Optional[str] = Field(None, description="URL to the cover image")


class ViewerService:
    """Service for handling book viewing operations."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the viewer service."""
        self._viewers = {}
        self._states = {}  # Track viewer state per book
        self._db_path = db_path

    def get_viewer(self, book_id: int, file_path: str):
        """
        Get or create a viewer for the specified book.

        Args:
            book_id: The ID of the book
            file_path: Path to the book file

        Returns:
            A viewer instance for the book
        """
        # Check if we already have a viewer for this book
        if book_id in self._viewers:
            return self._viewers[book_id]

        # Create a new viewer for the book
        viewer = get_viewer(file_path)
        if viewer is None:
            raise ValueError(f"No viewer available for file: {file_path}")

        # Initialize state for this book
        self._states[book_id] = ViewerState(
            current_page=0,
            total_pages=0,  # Will be updated when we get metadata
        )

        # Store the viewer for future use
        self._viewers[book_id] = viewer
        return viewer

    def get_page(self, book_id: int, file_path: str, page_number: int) -> ViewerPage:
        """
        Get a specific page from a book.

        Args:
            book_id: The ID of the book
            file_path: Path to the book file
            page_number: Page number (0-based)

        Returns:
            ViewerPage object containing page information
        """
        viewer = self.get_viewer(book_id, file_path)
        page_data = viewer.render_page(page_number)

        # Update state
        if book_id in self._states:
            self._states[book_id].current_page = page_number
            self._states[book_id].total_pages = page_data.get("total_pages", 0)

        return ViewerPage(
            number=page_number,
            width=page_data.get("width"),
            height=page_data.get("height"),
            url=f"/api/books/{book_id}/pages/{page_number}",
            thumbnail_url=f"/api/books/{book_id}/thumbnails/{page_number}",
        )

    def get_metadata(self, book_id: int, file_path: str) -> ViewerMetadata:
        """
        Get metadata for a book.

        Args:
            book_id: The ID of the book
            file_path: Path to the book file

        Returns:
            ViewerMetadata object containing book metadata
        """
        viewer = self.get_viewer(book_id, file_path)
        metadata = viewer.get_metadata()

        # Get page count from rendered page if available
        page_count = metadata.get("page_count", 0)
        if page_count == 0:
            # Try to get it from rendering the first page
            try:
                first_page = viewer.render_page(0)
                page_count = first_page.get("total_pages", 0)
            except Exception:
                pass

        # Update state with page count
        if book_id in self._states:
            self._states[book_id].total_pages = page_count

        return ViewerMetadata(
            title=metadata.get("title", ""),
            author=metadata.get("author", "") or metadata.get("creator", ""),
            series=metadata.get("series", ""),
            volume=metadata.get("volume", ""),
            publisher=metadata.get("publisher", ""),
            year=metadata.get("year"),
            page_count=page_count,
            format=Path(file_path).suffix[1:].lower(),
            cover_url=f"/api/books/{book_id}/cover",
        )

    def get_state(self, book_id: int, file_path: str) -> ViewerState:
        """
        Get the current viewer state for a book.

        Args:
            book_id: The ID of the book
            file_path: Path to the book file

        Returns:
            ViewerState object containing the current state
        """
        # Ensure viewer is loaded
        self.get_viewer(book_id, file_path)

        # Get or create state
        if book_id not in self._states:
            self._states[book_id] = ViewerState()

        state = self._states[book_id]

        # Update total_pages from metadata if needed
        if state.total_pages == 0:
            try:
                metadata = self.get_metadata(book_id, file_path)
                state.total_pages = metadata.page_count
            except Exception:
                pass

        return state

    def update_state(self, book_id: int, file_path: str, **kwargs) -> ViewerState:
        """
        Update the viewer state for a book.

        Args:
            book_id: The ID of the book
            file_path: Path to the book file
            **kwargs: State fields to update

        Returns:
            Updated ViewerState object
        """
        # Ensure viewer is loaded
        self.get_viewer(book_id, file_path)

        # Get or create state
        if book_id not in self._states:
            self._states[book_id] = ViewerState()

        state = self._states[book_id]

        # Update the state with the provided values
        if "current_page" in kwargs:
            state.current_page = kwargs["current_page"]
            # Calculate reading progress
            if state.total_pages > 0:
                state.reading_progress = (state.current_page / state.total_pages) * 100.0

        if "reading_direction" in kwargs:
            state.reading_direction = kwargs["reading_direction"]

        if "page_layout" in kwargs:
            state.page_layout = kwargs["page_layout"]

        if "zoom_mode" in kwargs:
            state.zoom_mode = kwargs["zoom_mode"]

        if "zoom_level" in kwargs:
            state.zoom_level = kwargs["zoom_level"]

        if "scroll_position" in kwargs:
            state.scroll_position = kwargs["scroll_position"]

        return state

    def close_viewer(self, book_id: int):
        """
        Close a viewer and clean up resources.

        Args:
            book_id: The ID of the book
        """
        if book_id in self._viewers:
            viewer = self._viewers.pop(book_id)
            viewer.close()
        
        # Clean up state
        if book_id in self._states:
            del self._states[book_id]


# Global instance
viewer_service = ViewerService()
