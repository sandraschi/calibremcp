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
        page = viewer.get_page(page_number)

        return ViewerPage(
            number=page_number,
            width=page.get("width"),
            height=page.get("height"),
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

        return ViewerMetadata(
            title=metadata.get("title", ""),
            author=metadata.get("author", ""),
            series=metadata.get("series", ""),
            volume=metadata.get("volume", ""),
            publisher=metadata.get("publisher", ""),
            year=metadata.get("year"),
            page_count=metadata.get("page_count", 0),
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
        viewer = self.get_viewer(book_id, file_path)
        state = viewer.get_state()

        return ViewerState(
            current_page=state.current_page,
            total_pages=state.total_pages,
            reading_direction=state.reading_direction.value,
            page_layout=state.page_layout.value,
            zoom_mode=state.zoom_mode.value,
            zoom_level=state.zoom_level,
            scroll_position=state.scroll_position,
            bookmarks=state.bookmarks,
            reading_progress=state.reading_progress,
            show_controls=state.show_controls,
            show_thumbnails=state.show_thumbnails,
            show_page_numbers=state.show_page_numbers,
            background_color=state.background_color,
            custom_css=state.custom_css,
        )

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
        viewer = self.get_viewer(book_id, file_path)

        # Update the state with the provided values
        if "current_page" in kwargs:
            viewer.navigate(kwargs["current_page"] - viewer.get_state().current_page)

        if "reading_direction" in kwargs:
            viewer.set_reading_direction(kwargs["reading_direction"])

        if "page_layout" in kwargs:
            viewer.set_page_layout(kwargs["page_layout"])

        if "zoom_mode" in kwargs:
            viewer.set_zoom_mode(kwargs["zoom_mode"])

        if "zoom_level" in kwargs:
            viewer.set_zoom_level(kwargs["zoom_level"])

        # Get the updated state
        return self.get_state(book_id, file_path)

    def close_viewer(self, book_id: int):
        """
        Close a viewer and clean up resources.

        Args:
            book_id: The ID of the book
        """
        if book_id in self._viewers:
            viewer = self._viewers.pop(book_id)
            viewer.close()


# Global instance
viewer_service = ViewerService()
