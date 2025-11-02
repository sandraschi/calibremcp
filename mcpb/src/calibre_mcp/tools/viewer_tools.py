"""
MCP tools for book viewing operations.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from ..services.viewer_service import viewer_service, ViewerState, ViewerPage, ViewerMetadata
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
        None, description="Reading direction (ltr, rtl, vertical)"
    )
    page_layout: Optional[str] = Field(None, description="Page layout mode (single, double, auto)")
    zoom_mode: Optional[str] = Field(
        None, description="Zoom mode (fit-width, fit-height, fit-both, original, custom)"
    )
    zoom_level: Optional[float] = Field(None, ge=0.1, le=5.0, description="Zoom level (1.0 = 100%)")


class ViewerTools(BaseTool):
    """MCP tools for book viewing operations."""

    @mcp_tool(
        name="open_book",
        description="Open a book in the viewer",
        input_model=OpenBookInput,
        output_model=Dict[str, Any],
    )
    async def open_book(self, book_id: int, file_path: str) -> Dict[str, Any]:
        """
        Open a book in the viewer and return its metadata and initial state.

        Initializes a book viewer session and retrieves all information needed to start
        displaying the book. This includes book metadata (page count, format, dimensions),
        current reading state (if previously saved), and the first page content for immediate display.

        The viewer will maintain session state for this book until explicitly closed, allowing
        seamless reading across multiple page requests.

        Args:
            book_id: The unique identifier of the book in the Calibre library
            file_path: Full path to the book file (PDF, EPUB, etc.) to open

        Returns:
            Dictionary containing complete viewer initialization data:
            {
                "metadata": dict - ViewerMetadata with book information (page_count, format, dimensions, etc.)
                "state": dict - ViewerState with current reading position and preferences
                "pages": dict - First page information:
                    {
                        "total": int - Total number of pages in the book
                        "first_page": dict - ViewerPage object for page 0 (first page)
                    }
            }

        Example:
            # Open a book and get initial data
            book_data = open_book(
                book_id=123,
                file_path="/path/to/library/123/book.pdf"
            )
            print(f"Opened book with {book_data['pages']['total']} pages")
            print(f"Starting on page {book_data['state']['current_page'] + 1}")
        """
        # This will initialize the viewer if it doesn't exist
        metadata = viewer_service.get_metadata(book_id, file_path)
        state = viewer_service.get_state(book_id, file_path)

        return {
            "metadata": metadata.dict(),
            "state": state.dict(),
            "pages": {
                "total": metadata.page_count,
                "first_page": viewer_service.get_page(book_id, file_path, 0).dict(),
            },
        }

    @mcp_tool(
        name="get_page",
        description="Get a specific page from a book",
        input_model=GetPageInput,
        output_model=ViewerPage,
    )
    async def get_page(self, book_id: int, file_path: str, page_number: int = 0) -> Dict[str, Any]:
        """
        Get a specific page from a book for display in the viewer.

        Retrieves page content, dimensions, and rendering information needed to display
        a single page of the book. This is used for paginated reading and navigation.

        Args:
            book_id: The unique identifier of the book in the Calibre library
            file_path: Full path to the book file (PDF, EPUB, etc.)
            page_number: Zero-based page index to retrieve (0 = first page, 1 = second page, etc.)

        Returns:
            Dictionary containing ViewerPage with the following structure:
            {
                "book_id": int - Book identifier
                "file_path": str - Path to the book file
                "page_number": int - The page number (0-based)
                "page_index": int - Display page number (1-based for user display)
                "content": str - Page text content if available (for EPUB/HTML)
                "image_url": str - URL or path to page image if available (for PDF/images)
                "width": int - Page width in pixels
                "height": int - Page height in pixels
                "has_text": bool - Whether the page contains extractable text
                "is_blank": bool - Whether the page is blank
            }

        Example:
            # Get the first page
            first_page = get_page(
                book_id=123,
                file_path="/path/to/library/123/book.pdf",
                page_number=0
            )

            # Get page 50 (49 in 0-based indexing)
            page_50 = get_page(
                book_id=123,
                file_path="/path/to/library/123/book.pdf",
                page_number=49
            )
        """
        return viewer_service.get_page(book_id, file_path, page_number).dict()

    @mcp_tool(
        name="get_metadata",
        description="Get metadata for a book",
        input_model=OpenBookInput,
        output_model=ViewerMetadata,
    )
    async def get_metadata(self, book_id: int, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive metadata for a book in the viewer.

        Retrieves detailed metadata including page count, dimensions, format information,
        and book structure. This metadata is used by the viewer to initialize display
        settings and navigate through the document.

        Args:
            book_id: The unique identifier of the book in the Calibre library
            file_path: Full path to the book file (PDF, EPUB, etc.)

        Returns:
            Dictionary containing ViewerMetadata with the following structure:
            {
                "book_id": int - Book identifier
                "file_path": str - Path to the book file
                "page_count": int - Total number of pages in the document
                "format": str - File format (PDF, EPUB, etc.)
                "dimensions": dict - Page dimensions if available
                "title": str - Book title from metadata
                "author": str - Author name from metadata
                ... (other metadata fields)
            }

        Example:
            # Get metadata for a specific book
            metadata = get_metadata(
                book_id=123,
                file_path="/path/to/library/123/book.pdf"
            )
            print(f"Book has {metadata['page_count']} pages")
        """
        return viewer_service.get_metadata(book_id, file_path).dict()

    @mcp_tool(
        name="get_state",
        description="Get the current viewer state for a book",
        input_model=OpenBookInput,
        output_model=ViewerState,
    )
    async def get_state(self, book_id: int, file_path: str) -> Dict[str, Any]:
        """
        Get the current viewer state for a book.

        Retrieves the saved reading position and viewer settings for a specific book,
        including current page, zoom level, reading direction, and layout preferences.
        This state persists across sessions to maintain reading continuity.

        Args:
            book_id: The unique identifier of the book in the Calibre library
            file_path: Full path to the book file (used for state identification)

        Returns:
            Dictionary containing ViewerState with the following structure:
            {
                "book_id": int - Book identifier
                "file_path": str - Path to the book file
                "current_page": int - Current page number (0-based index)
                "reading_direction": str - Reading direction: "ltr", "rtl", or "vertical"
                "page_layout": str - Layout mode: "single", "double", or "auto"
                "zoom_mode": str - Zoom mode: "fit-width", "fit-height", "fit-both", "original", or "custom"
                "zoom_level": float - Zoom level (1.0 = 100%, 0.5 = 50%, 2.0 = 200%)
                "last_updated": str - ISO timestamp of last state update
            }

        Example:
            # Get current reading position for a book
            state = get_state(
                book_id=123,
                file_path="/path/to/library/123/book.pdf"
            )
            print(f"Currently on page {state['current_page'] + 1} of {state['total_pages']}")
            print(f"Zoom level: {state['zoom_level'] * 100}%")
        """
        return viewer_service.get_state(book_id, file_path).dict()

    @mcp_tool(
        name="update_state",
        description="Update the viewer state for a book",
        input_model=UpdateStateInput,
        output_model=ViewerState,
    )
    async def update_state(
        self,
        book_id: int,
        file_path: str,
        current_page: Optional[int] = None,
        reading_direction: Optional[str] = None,
        page_layout: Optional[str] = None,
        zoom_mode: Optional[str] = None,
        zoom_level: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Update the viewer state for a book to save reading progress and preferences.

        Persists changes to the current reading position, zoom settings, layout preferences,
        and reading direction. All parameters are optional - only provided values will be updated.
        The state persists across sessions, so you can resume reading from the last position.

        Args:
            book_id: The unique identifier of the book in the Calibre library
            file_path: Full path to the book file (used for state identification)
            current_page: Zero-based page number to save as current position (e.g., 0 = first page)
            reading_direction: Reading direction to save:
                - "ltr" - Left-to-right (default for most languages)
                - "rtl" - Right-to-left (Arabic, Hebrew)
                - "vertical" - Vertical reading (some Asian languages)
            page_layout: Page layout mode to save:
                - "single" - Display one page at a time
                - "double" - Display two pages side-by-side (spread)
                - "auto" - Automatically choose based on book format
            zoom_mode: Zoom mode to save:
                - "fit-width" - Fit page width to viewer
                - "fit-height" - Fit page height to viewer
                - "fit-both" - Fit entire page to viewer
                - "original" - Display at original size (100%)
                - "custom" - Use custom zoom_level value
            zoom_level: Custom zoom level (1.0 = 100%, 0.5 = 50%, 2.0 = 200%).
                Only used when zoom_mode is "custom". Range: 0.1 to 5.0

        Returns:
            Dictionary containing updated ViewerState with all current settings:
            {
                "book_id": int - Book identifier
                "file_path": str - Path to the book file
                "current_page": int - Updated current page number (0-based)
                "reading_direction": str - Updated reading direction
                "page_layout": str - Updated page layout mode
                "zoom_mode": str - Updated zoom mode
                "zoom_level": float - Updated zoom level
                "last_updated": str - ISO timestamp of this update
            }

        Example:
            # Save reading progress (just update current page)
            state = update_state(
                book_id=123,
                file_path="/path/to/library/123/book.pdf",
                current_page=42
            )

            # Update multiple settings at once
            state = update_state(
                book_id=123,
                file_path="/path/to/library/123/book.pdf",
                current_page=50,
                zoom_mode="fit-width",
                reading_direction="ltr"
            )
        """
        state_updates = {}
        if current_page is not None:
            state_updates["current_page"] = current_page
        if reading_direction is not None:
            state_updates["reading_direction"] = reading_direction
        if page_layout is not None:
            state_updates["page_layout"] = page_layout
        if zoom_mode is not None:
            state_updates["zoom_mode"] = zoom_mode
        if zoom_level is not None:
            state_updates["zoom_level"] = zoom_level

        return viewer_service.update_state(book_id, file_path, **state_updates).dict()

    @mcp_tool(
        name="close_viewer",
        description="Close a viewer and clean up resources",
        input_model=OpenBookInput,
        output_model=Dict[str, bool],
    )
    async def close_viewer(self, book_id: int, file_path: str) -> Dict[str, bool]:
        """
        Close a viewer session and clean up associated resources.

        Closes the viewer session for the specified book, releasing any held resources
        such as file handles, cached pages, or memory buffers. The book's reading state
        is preserved and can be restored when reopening the book.

        This is useful for memory management when working with many books or when
        explicitly finishing a reading session. State changes are automatically saved
        before closing.

        Args:
            book_id: The unique identifier of the book in the Calibre library
            file_path: Path to the book file (kept for consistency with other viewer methods,
                       but not used for closing - book_id is sufficient)

        Returns:
            Dictionary with operation result:
            {
                "success": bool - True if viewer was successfully closed
            }

        Example:
            # Close a viewer session after finishing reading
            result = close_viewer(
                book_id=123,
                file_path="/path/to/library/123/book.pdf"
            )
            if result["success"]:
                print("Viewer closed successfully")
        """
        viewer_service.close_viewer(book_id)
        return {"success": True}

    @mcp_tool(
        name="open_book_file",
        description="Open a book file with the system's default application (e.g., EPUB reader, PDF reader)",
        input_model=OpenBookInput,
        output_model=Dict[str, bool],
    )
    async def open_book_file(self, book_id: int, file_path: str) -> Dict[str, bool]:
        """
        Open a book file with the system's default application.

        This tool launches the book file in your default EPUB/PDF reader application
        (e.g., Calibre E-book Viewer, Adobe Digital Editions, Edge, SumatraPDF, etc.).
        This is useful when you want to read a book using your preferred desktop reader.

        The system will use:
        - Windows: Default application associated with the file type (via os.startfile)
        - macOS: Default application (via 'open' command)
        - Linux: Default application (via 'xdg-open' command)

        Args:
            book_id: The unique identifier of the book in the Calibre library
            file_path: Full path to the book file (EPUB, PDF, etc.) to open

        Returns:
            Dictionary with operation result:
            {
                "success": bool - True if file was opened successfully
                "message": str - Status message
            }

        Example:
            # Open "A Tale of Two Cities" in default EPUB reader
            # First, find the book
            books = search_books(title="A Tale of Two Cities")
            if books["items"]:
                book = books["items"][0]
                # Get the file path (you may need to query the book's formats)
                result = open_book_file(
                    book_id=book["id"],
                    file_path="/path/to/library/123/A Tale of Two Cities.epub"
                )
                if result["success"]:
                    print("Book opened in default reader!")
        """
        import os
        import platform
        import subprocess
        from pathlib import Path

        try:
            file_path_obj = Path(file_path)

            # Verify file exists
            if not file_path_obj.exists():
                return {"success": False, "message": f"File not found: {file_path}"}

            # Open file with system default application
            system = platform.system()
            file_path_str = str(file_path_obj.absolute())

            if system == "Windows":
                os.startfile(file_path_str)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", file_path_str], check=False)
            else:  # Linux and others
                subprocess.run(["xdg-open", file_path_str], check=False)

            return {
                "success": True,
                "message": f"Opened {file_path_obj.name} with default application",
            }

        except Exception as e:
            return {"success": False, "message": f"Failed to open file: {str(e)}"}
