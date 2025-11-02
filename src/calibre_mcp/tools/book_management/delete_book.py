"""
Delete Book Tool

This module provides functionality to delete a book from the Calibre library.
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from ...tools.compat import MCPServerError
from ...storage import get_storage_backend

logger = logging.getLogger("calibremcp.tools.book_management")


# Helper function - called by manage_books portmanteau tool
# NOT registered as MCP tool (no @tool or @mcp.tool() decorator)
async def delete_book_helper(
    book_id: str, delete_files: bool = True, force: bool = False, library_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a book from the Calibre library.

    Args:
        book_id: ID of the book to delete (can be numeric ID or UUID)
        delete_files: Whether to delete the book's files from disk
        force: If True, skip dependency checks
        library_path: Optional path to the Calibre library

    Returns:
        Dictionary with the result of the operation

    Raises:
        MCPServerError: If the book cannot be found or there's an error
    """
    try:
        # Initialize the storage backend
        storage = get_storage_backend(library_path=library_path)

        # Get the book to verify it exists
        book = await storage.get_book(book_id)
        if not book:
            raise MCPServerError(f"Book with ID {book_id} not found")

        # Check for dependencies if not forcing
        if not force:
            # In a real implementation, we would check if the book is referenced
            # by any collections, reading lists, or other entities
            has_dependencies = await _check_book_dependencies(storage, book_id)
            if has_dependencies:
                raise MCPServerError(
                    "Cannot delete book: it is referenced by other entities. "
                    "Use force=True to delete anyway."
                )

        # Get the book's path before deletion if we need to delete files
        book_path = None
        if delete_files and hasattr(book, "path") and book.path:
            book_path = Path(book.path)

        # Delete the book from the database
        success = await storage.delete_book(book_id)
        if not success:
            raise MCPServerError(f"Failed to delete book {book_id} from database")

        # Delete the book's files if requested
        files_deleted = False
        if delete_files and book_path and book_path.exists():
            try:
                if book_path.is_dir():
                    # Delete the entire book directory
                    shutil.rmtree(book_path)
                else:
                    # Just delete the file if it's not a directory
                    book_path.unlink()
                files_deleted = True
            except Exception as e:
                logger.warning(f"Failed to delete book files at {book_path}: {e}")

        # Prepare the response
        result = {
            "success": True,
            "message": f"Book '{getattr(book, 'title', book_id)}' deleted successfully",
            "book_id": book_id,
            "files_deleted": files_deleted,
            "timestamp": storage.get_current_timestamp(),
        }
        #                 raise
        #             logger.warning(f"Failed to delete book files: {e}")
        #             result["files_deleted"] = False
        #             result["warning"] = f"Book record deleted but files could not be removed: {e}"

        return result

    except MCPServerError:
        raise
    except Exception as e:
        logger.error(f"Error deleting book {book_id}: {e}", exc_info=True)
        raise MCPServerError(f"Failed to delete book: {str(e)}")


async def _check_book_dependencies(storage, book_id: str) -> bool:
    """
    Check if a book has dependencies that would prevent deletion.

    Args:
        storage: Storage backend instance
        book_id: ID of the book to check

    Returns:
        bool: True if the book has dependencies, False otherwise
    """
    # In a real implementation, we would check:
    # 1. If the book is in any collections
    # 2. If the book is in any reading lists
    # 3. If the book has any annotations or highlights
    # 4. If the book is referenced by any other entities

    # For now, we'll just return False (no dependencies)
    return False


# Add a helper function to safely remove book files
def _remove_book_files(book_path: Path, force: bool = False) -> bool:
    """Safely remove book files from disk.

    Args:
        book_path: Path to the book's directory
        force: Continue even if there are errors

    Returns:
        bool: True if all files were deleted successfully
    """
    try:
        if not book_path.exists():
            return True

        if not book_path.is_dir():
            if force:
                return True
            raise ValueError(f"Book path is not a directory: {book_path}")

        # Remove the directory and all its contents
        shutil.rmtree(book_path)
        return True

    except Exception as e:
        logger.error(f"Error removing book files from {book_path}: {e}")
        if not force:
            raise
        return False
