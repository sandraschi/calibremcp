"""
Viewer management portmanteau tool for CalibreMCP.

Consolidates all book viewer operations into a single unified interface.
"""

from pathlib import Path
from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ...services.viewer_service import viewer_service
from ..shared.error_handling import format_error_response, handle_tool_error

logger = get_logger("calibremcp.tools.viewer")


@mcp.tool()
async def manage_viewer(
    operation: str,
    book_id: int | None = None,
    file_path: str | None = None,
    # Page-specific parameters
    page_number: int = 0,
    # State update parameters
    current_page: int | None = None,
    reading_direction: str | None = None,
    page_layout: str | None = None,
    zoom_mode: str | None = None,
    zoom_level: float | None = None,
    # Search parameters for open_random operation
    author: str | None = None,
    tag: str | None = None,
    series: str | None = None,
    format_preference: str = "EPUB",
) -> dict[str, Any]:
    """
    Comprehensive book viewer and reading interaction interface.

    Operations:
    - open: Initialize a viewer session and retrieve initial book data.
    - get_page: Fetch specific page content, dimensions, and text.
    - get_metadata: Detailed book metrics required for rendering (page count, etc.).
    - get_state / update_state: Sync reading progress, zoom, and orientation.
    - close: Terminate a viewer session and release memory.
    - open_file: Launch the book in the system's default external application.
    - open_random: Search and automatically open a random book matching filters.

    Example:
    - manage_viewer(operation="open_file", book_id=123)
    - manage_viewer(operation="get_page", book_id=123, page_number=5)
    """
    try:
        # Handle open_random operation first (doesn't require book_id/file_path)
        if operation == "open_random":
            try:
                import os
                import platform
                import random
                import subprocess

                from sqlalchemy.orm import joinedload

                from ...db.database import get_database
                from ...db.models import Book
                from ...tools.book_tools import search_books_helper

                # Build search parameters
                search_params = {"limit": 100}  # Get up to 100 books for random selection
                if author:
                    search_params["author"] = author
                if tag:
                    search_params["tag"] = tag
                if series:
                    search_params["series"] = series

                # Validate at least one search criterion
                if not author and not tag and not series:
                    return format_error_response(
                        error_msg="At least one search filter (author, tag, or series) is required for open_random operation.",
                        error_code="MISSING_SEARCH_CRITERIA",
                        error_type="ValueError",
                        operation=operation,
                        suggestions=[
                            "Provide author parameter: author='John Dickson Carr'",
                            "Provide tag parameter: tag='mystery'",
                            "Provide series parameter: series='Sherlock Holmes'",
                        ],
                        related_tools=["query_books"],
                    )

                # Search for books
                search_result = await search_books_helper(**search_params)
                books = search_result.get("items", [])

                if not books:
                    return format_error_response(
                        error_msg=f"No books found matching the search criteria (author={author}, tag={tag}, series={series}).",
                        error_code="NO_BOOKS_FOUND",
                        error_type="ValueError",
                        operation=operation,
                        suggestions=[
                            "Check spelling of author/tag/series names",
                            "Try a broader search (e.g., partial author name)",
                            "Use query_books() to verify books exist with these criteria",
                        ],
                        related_tools=["query_books"],
                    )

                # Randomly select a book
                selected_book = random.choice(books)
                selected_book_id = selected_book["id"]
                selected_title = selected_book.get("title", "Unknown")
                authors_list = selected_book.get("authors", [])
                if authors_list and isinstance(authors_list[0], dict):
                    selected_author = ", ".join([a.get("name", "") for a in authors_list])
                else:
                    selected_author = ", ".join(authors_list) if authors_list else "Unknown"

                # Get file path from database
                db = get_database()
                with db.session_scope() as session:
                    book_obj = (
                        session.query(Book)
                        .options(joinedload(Book.data))
                        .filter(Book.id == selected_book_id)
                        .first()
                    )
                    if not book_obj:
                        return format_error_response(
                            error_msg=f"Book {selected_book_id} not found in database.",
                            error_code="BOOK_NOT_FOUND",
                            error_type="NotFoundError",
                            operation=operation,
                            suggestions=["Verify the book exists in the library"],
                            related_tools=["query_books"],
                        )

                    # Get library path
                    from ...config import CalibreConfig

                    config = CalibreConfig()
                    libraries = config.discover_libraries()
                    if not libraries:
                        return format_error_response(
                            error_msg="No libraries found.",
                            error_code="NO_LIBRARIES",
                            error_type="ValueError",
                            operation=operation,
                            suggestions=["Configure Calibre library paths"],
                            related_tools=["manage_libraries"],
                        )
                    first_lib_path = next(iter(libraries.values())).path

                    # Find format
                    formats = book_obj.data
                    format_obj = None

                    # Try preferred format first
                    for fmt in formats:
                        if fmt.format.upper() == format_preference.upper():
                            format_obj = fmt
                            break

                    # If not found, use first available
                    if not format_obj and formats:
                        format_obj = formats[0]

                    if not format_obj:
                        return format_error_response(
                            error_msg=f"Book {selected_book_id} has no available formats.",
                            error_code="NO_FORMATS",
                            error_type="ValueError",
                            operation=operation,
                            suggestions=["Check that the book has file formats in the library"],
                            related_tools=["manage_books"],
                        )

                    # Build file path
                    file_format = format_obj.format.upper()
                    file_name = (
                        format_obj.name
                        if format_obj.name
                        else f"{book_obj.title}.{format_obj.format.lower()}"
                    )
                    # Ensure filename has extension
                    if not file_name.lower().endswith(f".{format_obj.format.lower()}"):
                        file_name = f"{file_name}.{format_obj.format.lower()}"
                    # Clean filename
                    import re

                    file_name = re.sub(r'[<>:"/\\|?*]', "_", file_name)
                    file_path = Path(first_lib_path) / book_obj.path / file_name

                    # If file doesn't exist, try without extension
                    if not file_path.exists():
                        file_path_no_ext = Path(first_lib_path) / book_obj.path / format_obj.name
                        if file_path_no_ext.exists():
                            file_path = file_path_no_ext

                    if not file_path.exists():
                        return format_error_response(
                            error_msg=f"File not found: {file_path}",
                            error_code="FILE_NOT_FOUND",
                            error_type="FileNotFoundError",
                            operation=operation,
                            suggestions=["Verify the book file exists in the library"],
                            related_tools=["manage_books"],
                        )

                    # Open file with system default application
                    file_path_str = str(file_path.resolve())
                    system = platform.system()

                    if system == "Windows":
                        os.startfile(file_path_str)
                    elif system == "Darwin":  # macOS
                        subprocess.run(["open", file_path_str], check=False)
                    else:  # Linux and others
                        subprocess.run(["xdg-open", file_path_str], check=False)

                    return {
                        "success": True,
                        "book_id": selected_book_id,
                        "title": selected_title,
                        "author": selected_author,
                        "file_path": file_path_str,
                        "format": file_format,
                        "message": f"Opened random book: {selected_title} by {selected_author}",
                    }

            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={
                        "author": author,
                        "tag": tag,
                        "series": series,
                        "format_preference": format_preference,
                    },
                    tool_name="manage_viewer",
                    context="Opening random book",
                )

        # Validate book_id and file_path for other operations
        if not book_id:
            return format_error_response(
                error_msg=f"book_id is required for operation '{operation}'. Use 'open_random' operation if you want to search and open a random book.",
                error_code="MISSING_BOOK_ID",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Provide book_id parameter",
                    "Or use operation='open_random' with author/tag/series filters",
                ],
                related_tools=["query_books", "manage_viewer"],
            )

        # For open_file: resolve file_path from book_id if not provided (webapp sends only book_id)
        if operation == "open_file" and not file_path:
            try:
                import re

                from sqlalchemy.orm import joinedload

                from ...db.database import get_database
                from ...db.models import Book

                db = get_database()
                if not db._current_db_path:
                    return format_error_response(
                        error_msg="No library loaded. Use manage_libraries to switch to a library.",
                        error_code="NO_LIBRARY",
                        error_type="ValueError",
                        operation=operation,
                        suggestions=["Ensure a library is loaded via manage_libraries"],
                        related_tools=["manage_libraries"],
                    )
                lib_path = str(Path(db._current_db_path).parent)
                with db.session_scope() as session:
                    book_obj = (
                        session.query(Book)
                        .options(joinedload(Book.data))
                        .filter(Book.id == book_id)
                        .first()
                    )
                    if not book_obj or not book_obj.data:
                        return format_error_response(
                            error_msg=f"Book {book_id} has no formats to open.",
                            error_code="NO_FORMATS",
                            error_type="ValueError",
                            operation=operation,
                            suggestions=["Verify the book has file formats in the library"],
                            related_tools=["manage_books"],
                        )
                    fmt = next(
                        (
                            f
                            for f in book_obj.data
                            if f.format.upper() in ("EPUB", "PDF", "MOBI", "AZW3")
                        ),
                        book_obj.data[0],
                    )
                    fname = (
                        fmt.name.strip()
                        if fmt.name and fmt.name.strip()
                        else f"{book_obj.id}.{fmt.format.lower()}"
                    )
                    if not fname.lower().endswith(f".{fmt.format.lower()}"):
                        fname = f"{fname}.{fmt.format.lower()}"
                    fname = re.sub(r'[<>:"/\\|?*]', "_", fname)
                    file_path = str(Path(lib_path) / book_obj.path / fname)
                    if not Path(file_path).exists():
                        alt = Path(lib_path) / book_obj.path / (fmt.name or "")
                        file_path = str(alt) if alt.exists() else file_path
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id},
                    tool_name="manage_viewer",
                    context="Resolving file path from book_id",
                )

        if not file_path:
            return format_error_response(
                error_msg=f"file_path is required for operation '{operation}'. Use 'open_random' operation if you want to search and open a random book.",
                error_code="MISSING_FILE_PATH",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Provide file_path parameter",
                    "Or use operation='open_random' with author/tag/series filters",
                ],
                related_tools=["query_books", "manage_viewer"],
            )

        # Validate file_path exists for operations that need it
        if operation != "close":  # close doesn't need file validation
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return format_error_response(
                    error_msg=f"Book file not found: {file_path}. Verify the file exists and the path is correct. Use query_books to get valid format paths.",
                    error_code="FILE_NOT_FOUND",
                    error_type="FileNotFoundError",
                    operation=operation,
                    suggestions=[
                        "Use query_books() to get valid file paths from book.formats[].path",
                        "Verify the book file exists at the specified path",
                        "Check that the file hasn't been moved or deleted",
                    ],
                    related_tools=["query_books", "manage_books"],
                )

        if operation == "open":
            try:
                metadata = viewer_service.get_metadata(book_id, file_path)
                state = viewer_service.get_state(book_id, file_path)

                return {
                    "success": True,
                    "metadata": metadata.dict(),
                    "state": state.dict(),
                    "pages": {
                        "total": metadata.page_count,
                        "first_page": viewer_service.get_page(book_id, file_path, 0).dict(),
                    },
                }
            except ValueError as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book in viewer",
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book in viewer",
                )

        elif operation == "get_page":
            try:
                page_obj = viewer_service.get_page(book_id, file_path, page_number)
                # Also get the rendered page content from the viewer
                viewer = viewer_service.get_viewer(book_id, file_path)
                page_data = viewer.render_page(page_number)

                return {
                    "success": True,
                    "book_id": book_id,
                    "file_path": file_path,
                    "page_number": page_number,
                    "page_index": page_number + 1,  # 1-based for display
                    "content": page_data.get("content", ""),
                    "image_url": page_obj.url,
                    "width": page_obj.width,
                    "height": page_obj.height,
                    "has_text": bool(page_data.get("text", "")),
                    "is_blank": False,  # Could be enhanced to detect blank pages
                }
            except IndexError:
                return format_error_response(
                    error_msg=f"Page {page_number} is out of range for book {book_id}. Page numbers are 0-based (first page is 0).",
                    error_code="PAGE_OUT_OF_RANGE",
                    error_type="IndexError",
                    operation=operation,
                    suggestions=[
                        "Use get_metadata to check total page count",
                        "Page numbers are 0-based (first page is 0, second page is 1, etc.)",
                        f"Valid page range for this book is 0 to {page_number - 1}",
                    ],
                    related_tools=["manage_viewer"],
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={
                        "book_id": book_id,
                        "file_path": file_path,
                        "page_number": page_number,
                    },
                    tool_name="manage_viewer",
                    context="Getting page from book",
                )

        elif operation == "get_metadata":
            try:
                return {
                    "success": True,
                    **viewer_service.get_metadata(book_id, file_path).dict(),
                }
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Getting book metadata",
                )

        elif operation == "get_state":
            try:
                return {
                    "success": True,
                    **viewer_service.get_state(book_id, file_path).dict(),
                }
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Getting viewer state",
                )

        elif operation == "update_state":
            try:
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

                return {
                    "success": True,
                    **viewer_service.update_state(book_id, file_path, **state_updates).dict(),
                }
            except ValueError as e:
                return format_error_response(
                    error_msg=f"Invalid viewer state parameter: {str(e)}. Check parameter values and ranges.",
                    error_code="INVALID_STATE_PARAMETER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Check that zoom_level is between 0.1 and 5.0",
                        "Verify reading_direction is one of: ltr, rtl, vertical",
                        "Verify page_layout is one of: single, double, auto",
                        "Verify zoom_mode is one of: fit-width, fit-height, fit-both, original, custom",
                    ],
                    related_tools=["manage_viewer"],
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={
                        "book_id": book_id,
                        "file_path": file_path,
                        "current_page": current_page,
                        "reading_direction": reading_direction,
                        "page_layout": page_layout,
                        "zoom_mode": zoom_mode,
                        "zoom_level": zoom_level,
                    },
                    tool_name="manage_viewer",
                    context="Updating viewer state",
                )

        elif operation == "close":
            try:
                viewer_service.close_viewer(book_id)
                return {"success": True}
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Closing viewer",
                )

        elif operation == "open_file":
            try:
                import os
                import platform
                import re
                import subprocess

                # If file_path is not provided or invalid, build from database
                if not file_path or not Path(file_path).exists():
                    try:
                        from sqlalchemy.orm import joinedload

                        from ...config import CalibreConfig
                        from ...db.database import get_database
                        from ...db.models import Book

                        db = get_database()
                        config = CalibreConfig()
                        lib_path = (
                            str(config.local_library_path) if config.local_library_path else None
                        )
                        if not lib_path:
                            libraries = config.discover_libraries()
                            if libraries:
                                first = next(iter(libraries.values()))
                                lib_path = str(getattr(first, "path", first))
                        if lib_path:
                            with db.session_scope() as session:
                                book_obj = (
                                    session.query(Book)
                                    .options(joinedload(Book.data))
                                    .filter(Book.id == book_id)
                                    .first()
                                )
                                if book_obj and book_obj.data:
                                    preferred = [
                                        "EPUB",
                                        "PDF",
                                        "MOBI",
                                        "AZW3",
                                        "CBZ",
                                        "CBR",
                                        "TXT",
                                        "HTML",
                                        "RTF",
                                    ]
                                    format_obj = None
                                    for fmt_name in preferred:
                                        for d in book_obj.data:
                                            if d.format.upper() == fmt_name:
                                                format_obj = d
                                                break
                                        if format_obj:
                                            break
                                    if not format_obj:
                                        format_obj = book_obj.data[0]
                                    fname = (
                                        format_obj.name
                                        or f"{book_obj.title}.{format_obj.format.lower()}"
                                    )
                                    if not fname.lower().endswith(f".{format_obj.format.lower()}"):
                                        fname = f"{fname}.{format_obj.format.lower()}"
                                    fname = re.sub(r'[<>:"/\\|?*]', "_", fname)
                                    candidate = Path(lib_path) / book_obj.path / fname
                                    if candidate.exists():
                                        file_path = str(candidate)
                                    elif (
                                        format_obj.name
                                        and (
                                            Path(lib_path) / book_obj.path / format_obj.name
                                        ).exists()
                                    ):
                                        file_path = str(
                                            (
                                                Path(lib_path) / book_obj.path / format_obj.name
                                            ).resolve()
                                        )
                    except Exception as e:
                        logger.warning(
                            f"Could not resolve file path for book_id={book_id}: {e}",
                            exc_info=True,
                        )

                if not file_path:
                    return format_error_response(
                        error_msg=f"Cannot open book {book_id}: No file path provided and could not get from book formats. Use query_books to get format paths first.",
                        error_code="NO_FILE_PATH",
                        error_type="ValueError",
                        operation=operation,
                        suggestions=[
                            "Use query_books() to get valid file paths from book.formats[].path",
                            "Provide file_path parameter with full path to book file",
                        ],
                        related_tools=["query_books"],
                    )

                file_path_obj = Path(file_path)

                # Normalize path separators for Windows
                if platform.system() == "Windows":
                    file_path_str = str(file_path_obj.resolve())
                else:
                    file_path_str = str(file_path_obj.absolute())

                # Verify file exists
                if not file_path_obj.exists():
                    return format_error_response(
                        error_msg=f"File not found: {file_path_str}. Check that the file exists and the path is correct. The file path should come from query_books results (formats[].path).",
                        error_code="FILE_NOT_FOUND",
                        error_type="FileNotFoundError",
                        operation=operation,
                        suggestions=[
                            "Use query_books() to get valid file paths",
                            "Verify the file hasn't been moved or deleted",
                        ],
                        related_tools=["query_books"],
                    )

                # Open file with system default application
                system = platform.system()

                if system == "Windows":
                    os.startfile(file_path_str)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", file_path_str], check=False)
                else:  # Linux and others
                    subprocess.run(["xdg-open", file_path_str], check=False)

                return {
                    "success": True,
                    "message": f"Opened {file_path_obj.name} with default application",
                    "file_path": file_path_str,
                }
            except PermissionError as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book file with default application",
                )
            except OSError as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book file with default application",
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book file with default application",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'open', 'get_page', 'get_metadata', 'get_state', 'update_state', 'close', 'open_file', 'open_random'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='open' to open a book in the viewer",
                    "Use operation='get_page' to get a specific page",
                    "Use operation='get_metadata' to get book metadata",
                    "Use operation='get_state' to get current viewer state",
                    "Use operation='update_state' to save reading progress",
                    "Use operation='close' to close a viewer session",
                    "Use operation='open_file' to open book in default application",
                    "Use operation='open_random' to search and open a random book (requires author/tag/series filter)",
                ],
                related_tools=["manage_viewer"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "book_id": book_id,
                "file_path": file_path,
            },
            tool_name="manage_viewer",
            context="Viewer operation",
        )
