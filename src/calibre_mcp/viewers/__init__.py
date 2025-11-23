"""
Viewer module for CalibreMCP - Handles rendering and displaying different book formats.
"""

from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, Protocol


class ViewerType(str, Enum):
    """Supported viewer types."""

    EPUB = "epub"
    PDF = "pdf"
    CBZ = "cbz"
    CBR = "cbr"


class BookViewer(Protocol):
    """Interface for all book viewers."""

    @classmethod
    def supports_format(cls, file_extension: str) -> bool:
        """Check if this viewer supports the given file format."""
        ...

    def load(self, file_path: str) -> None:
        """Load a book file into the viewer."""
        ...

    def render_page(self, page_number: int = 0) -> Dict[str, Any]:
        """
        Render a specific page.

        Returns:
            Dictionary containing:
            - content: Rendered content (HTML, image data, etc.)
            - total_pages: Total number of pages
            - current_page: Current page number
            - metadata: Additional metadata
        """
        ...

    def get_metadata(self) -> Dict[str, Any]:
        """Extract metadata from the book."""
        ...

    def close(self) -> None:
        """Clean up resources."""
        ...


def get_viewer(file_path: str) -> Optional[BookViewer]:
    """
    Get the appropriate viewer for the given file.

    Args:
        file_path: Path to the book file

    Returns:
        An instance of the appropriate viewer, or None if no viewer supports the format
    """
    # Lazy imports to avoid circular dependencies
    from .epub import EpubViewer
    from .pdf import PdfViewer
    from .comic import ComicViewer

    path = Path(file_path)
    if not path.exists():
        return None

    ext = path.suffix.lower()[1:]  # Remove the dot

    # Check which viewer supports this format
    viewers = [EpubViewer, PdfViewer, ComicViewer]
    for viewer_cls in viewers:
        if hasattr(viewer_cls, "supports_format") and viewer_cls.supports_format(ext):
            viewer = viewer_cls()
            # Load the file into the viewer
            viewer.load(file_path)
            return viewer

    return None
