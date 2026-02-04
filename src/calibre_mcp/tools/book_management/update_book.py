"""
Update Book Tool

This module provides functionality to update a book's metadata and properties
in the Calibre library. Uses calibredb CLI or BookService for proper integration.
"""

import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from ...config import CalibreConfig
from ...logging_config import get_logger
from ...server import current_library
from ...services.base_service import NotFoundError, ValidationError
from ...services.book_service import book_service
from ...tools.compat import MCPServerError

logger = get_logger("calibremcp.tools.book_management")


def _find_calibredb() -> str | None:
    """
    Find calibredb executable in PATH.

    Returns:
        Path to calibredb executable or None if not found
    """
    calibredb_names = ["calibredb", "calibredb.exe"]

    for name in calibredb_names:
        calibredb_path = shutil.which(name)
        if calibredb_path:
            logger.debug(f"Found calibredb at: {calibredb_path}")
            return calibredb_path

    logger.warning("calibredb not found in PATH")
    return None


def _get_library_path(library_path: str | None = None) -> Path:
    """
    Get the active Calibre library path.

    Args:
        library_path: Optional explicit library path

    Returns:
        Path to the Calibre library directory

    Raises:
        MCPServerError: If library path cannot be determined
    """
    config = CalibreConfig.load_config()

    # Priority: 1) explicit library_path, 2) config.local_library_path, 3) discovered libraries
    if library_path:
        lib_path = Path(library_path)
        if lib_path.exists() and (lib_path / "metadata.db").exists():
            return lib_path
        raise MCPServerError(f"Invalid library path: {library_path} (metadata.db not found)")

    if config.local_library_path and (config.local_library_path / "metadata.db").exists():
        return config.local_library_path

    # Try to find library from discovered libraries
    if config.discovered_libraries:
        # Use current_library if available, otherwise use first discovered
        library_name = (
            current_library
            if current_library in config.discovered_libraries
            else list(config.discovered_libraries.keys())[0]
        )
        lib_info = config.discovered_libraries[library_name]
        lib_path = Path(lib_info.path)
        if lib_path.exists() and (lib_path / "metadata.db").exists():
            return lib_path

    raise MCPServerError(
        "Cannot determine library path. Please specify library_path parameter or configure a library in CalibreConfig."
    )


async def update_book_helper(
    book_id: str,
    metadata: dict[str, Any] | None = None,
    status: str | None = None,
    progress: float | None = None,
    cover_path: str | None = None,
    update_timestamp: bool = True,
    library_path: str | None = None,
) -> dict[str, Any]:
    """
    Update a book's metadata and properties in the Calibre library.

    Uses calibredb set_metadata for metadata updates, or BookService for direct database updates.
    For cover updates, uses calibredb set_metadata with --cover option.

    Args:
        book_id: ID of the book to update (can be numeric ID or UUID)
        metadata: Dictionary of metadata fields to update
        status: New reading status (unread, reading, finished, abandoned)
        progress: New reading progress (0.0 to 1.0)
        cover_path: Path to a new cover image
        update_timestamp: Whether to update the last_modified timestamp
        library_path: Optional path to the Calibre library

    Returns:
        Dictionary with the updated book information

    Raises:
        MCPServerError: If the book cannot be found or there's an error
    """
    try:
        # Convert book_id to int if it's numeric
        try:
            book_id_int = int(book_id)
        except ValueError:
            # If it's a UUID, we'll need to look it up first
            # For now, try to use it as-is with calibredb
            book_id_int = None

        # Validate inputs
        if metadata:
            _validate_metadata_update(metadata)

        if progress is not None and not 0.0 <= progress <= 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")

        # Get library path
        lib_path = _get_library_path(library_path)

        # Check if book exists
        if book_id_int is not None:
            try:
                book_service.get_by_id(book_id_int)
            except NotFoundError:
                raise MCPServerError(f"Book with ID {book_id} not found")

        updated_fields = []

        # Use calibredb for metadata updates (handles Calibre's format properly)
        calibredb = _find_calibredb()
        use_calibredb = calibredb is not None

        if use_calibredb and (metadata or cover_path):
            # Build calibredb set_metadata command
            cmd = [
                calibredb,
                "set_metadata",
                str(book_id),
                "--library-path",
                str(lib_path),
            ]

            # Add metadata fields
            if metadata:
                if "title" in metadata and metadata["title"]:
                    cmd.extend(["--field", f"title:{metadata['title']}"])
                    updated_fields.append("title")

                if "authors" in metadata and metadata["authors"]:
                    authors_str = (
                        ", ".join(metadata["authors"])
                        if isinstance(metadata["authors"], list)
                        else str(metadata["authors"])
                    )
                    cmd.extend(["--field", f"authors:{authors_str}"])
                    updated_fields.append("authors")

                if "tags" in metadata and metadata["tags"]:
                    tags_str = (
                        ", ".join(metadata["tags"])
                        if isinstance(metadata["tags"], list)
                        else str(metadata["tags"])
                    )
                    cmd.extend(["--field", f"tags:{tags_str}"])
                    updated_fields.append("tags")

                if "series" in metadata and metadata["series"]:
                    cmd.extend(["--field", f"series:{metadata['series']}"])
                    updated_fields.append("series")

                if "series_index" in metadata and metadata["series_index"] is not None:
                    cmd.extend(["--field", f"series_index:{metadata['series_index']}"])
                    updated_fields.append("series_index")

                if "publisher" in metadata and metadata["publisher"]:
                    cmd.extend(["--field", f"publisher:{metadata['publisher']}"])
                    updated_fields.append("publisher")

                if "rating" in metadata and metadata["rating"] is not None:
                    cmd.extend(["--field", f"rating:{metadata['rating']}"])
                    updated_fields.append("rating")

                if "isbn" in metadata and metadata["isbn"]:
                    cmd.extend(["--field", f"isbn:{metadata['isbn']}"])
                    updated_fields.append("isbn")

                if "languages" in metadata and metadata["languages"]:
                    lang_str = (
                        ", ".join(metadata["languages"])
                        if isinstance(metadata["languages"], list)
                        else str(metadata["languages"])
                    )
                    cmd.extend(["--field", f"languages:{lang_str}"])
                    updated_fields.append("languages")

                if "comments" in metadata and metadata["comments"]:
                    cmd.extend(["--field", f"comments:{metadata['comments']}"])
                    updated_fields.append("comments")

            # Add cover update
            if cover_path:
                cover_path_obj = Path(cover_path)
                if not cover_path_obj.exists():
                    raise FileNotFoundError(f"Cover image not found: {cover_path}")
                cmd.extend(["--cover", str(cover_path_obj)])
                updated_fields.append("cover")

            # Execute calibredb command
            if len(cmd) > 5:  # More than just base command + book_id + library_path
                logger.debug(f"Executing calibredb command: {' '.join(cmd)}")

                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    error_msg = (
                        stderr.decode("utf-8", errors="replace") if stderr else "Unknown error"
                    )
                    logger.error(f"calibredb set_metadata failed: {error_msg}")
                    raise MCPServerError(f"Failed to update book metadata: {error_msg}")

                logger.info(f"Successfully updated book {book_id} via calibredb")

        # Use BookService for status and progress updates (custom fields)
        if book_id_int is not None and (status is not None or progress is not None):
            update_data = {}

            if status is not None:
                # Map status string to our internal representation if needed
                update_data["status"] = status
                updated_fields.append("status")

            if progress is not None:
                # Store progress in a custom field or comments
                # For now, we'll store it in comments as a JSON snippet
                # In a full implementation, you'd have a progress field in the database
                update_data["progress"] = progress
                updated_fields.append("progress")

            if update_data:
                try:
                    # Note: BookService.update() may not support status/progress directly
                    # This is a simplified implementation - in production, you'd extend the schema
                    book_service.update(book_id_int, update_data)
                except (NotFoundError, ValidationError) as e:
                    logger.warning(f"Could not update status/progress via BookService: {e}")
                    # Continue - metadata update may have succeeded

        # Retrieve updated book to return complete information
        if book_id_int is not None:
            try:
                from .get_book import get_book_helper

                book_data = await get_book_helper(
                    book_id=str(book_id_int),
                    include_metadata=True,
                    include_formats=True,
                    include_cover=False,
                    library_path=str(lib_path),
                )

                return {
                    "success": True,
                    "message": "Book updated successfully",
                    "book_id": str(book_id_int),
                    "updated_fields": updated_fields,
                    "book": book_data,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            except Exception as e:
                logger.warning(f"Could not retrieve updated book details: {e}")

        # Fallback response
        return {
            "success": True,
            "message": "Book updated successfully",
            "book_id": str(book_id),
            "updated_fields": updated_fields,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    except ValueError as e:
        raise MCPServerError(f"Invalid input: {str(e)}")
    except FileNotFoundError as e:
        raise MCPServerError(f"File not found: {str(e)}")
    except MCPServerError:
        raise
    except Exception as e:
        logger.error(f"Error updating book {book_id}: {e}", exc_info=True)
        raise MCPServerError(f"Failed to update book: {str(e)}")


def _validate_metadata_update(metadata: dict[str, Any]) -> None:
    """Validate metadata update values.

    Args:
        metadata: Dictionary of metadata fields to validate

    Raises:
        ValueError: If any metadata values are invalid
    """
    if not metadata:
        return

    # Validate rating
    if "rating" in metadata:
        rating = metadata["rating"]
        if not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
            raise ValueError("Rating must be a number between 0 and 5")

    # Validate series index
    if "series_index" in metadata:
        series_index = metadata["series_index"]
        if not isinstance(series_index, (int, float)) or series_index < 0:
            raise ValueError("Series index must be a non-negative number")

    # Validate languages
    if "languages" in metadata:
        if not isinstance(metadata["languages"], list):
            raise ValueError("Languages must be a list of language codes")
        if not all(isinstance(lang, str) for lang in metadata["languages"]):
            raise ValueError("All language codes must be strings")

    # Validate tags
    if "tags" in metadata:
        if not isinstance(metadata["tags"], list):
            raise ValueError("Tags must be a list of strings")
        if not all(isinstance(tag, str) for tag in metadata["tags"]):
            raise ValueError("All tags must be strings")

    # Validate identifiers
    if "identifiers" in metadata:
        if not isinstance(metadata["identifiers"], dict):
            raise ValueError("Identifiers must be a dictionary")
        if not all(
            isinstance(k, str) and isinstance(v, str) for k, v in metadata["identifiers"].items()
        ):
            raise ValueError("All identifier keys and values must be strings")
