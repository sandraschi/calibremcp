"""
Delete Book Tool

This module provides functionality to delete a book from the Calibre library.
Uses calibredb remove CLI or BookService.delete() for proper integration.
"""

import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from ...tools.compat import MCPServerError
from ...logging_config import get_logger
from ...config import CalibreConfig
from ...server import current_library
from ...services.book_service import book_service
from ...services.base_service import NotFoundError

logger = get_logger("calibremcp.tools.book_management")


def _find_calibredb() -> Optional[str]:
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


def _get_library_path(library_path: Optional[str] = None) -> Path:
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
        library_name = current_library if current_library in config.discovered_libraries else list(config.discovered_libraries.keys())[0]
        lib_info = config.discovered_libraries[library_name]
        lib_path = Path(lib_info.path)
        if lib_path.exists() and (lib_path / "metadata.db").exists():
            return lib_path
    
    raise MCPServerError(
        "Cannot determine library path. Please specify library_path parameter or configure a library in CalibreConfig."
    )


async def delete_book_helper(
    book_id: str, delete_files: bool = True, force: bool = False, library_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a book from the Calibre library.

    Uses calibredb remove for proper deletion, which handles:
    - Database entry removal
    - File deletion (if requested)
    - Relationship cleanup

    Args:
        book_id: ID of the book to delete (can be numeric ID or UUID)
        delete_files: Whether to delete the book's files from disk (default: True)
        force: If True, skip dependency checks (default: False)
        library_path: Optional path to the Calibre library

    Returns:
        Dictionary with the result of the operation

    Raises:
        MCPServerError: If the book cannot be found or there's an error
    """
    try:
        # Convert book_id to int if it's numeric
        try:
            book_id_int = int(book_id)
        except ValueError:
            # If it's a UUID, we'll use it as-is with calibredb
            book_id_int = None
        
        # Get library path
        lib_path = _get_library_path(library_path)
        
        # Get book info before deletion (for response)
        book_title = "Unknown"
        if book_id_int is not None:
            try:
                existing_book = book_service.get_by_id(book_id_int)
                book_title = existing_book.get("title", "Unknown")
            except NotFoundError:
                # Book doesn't exist - but we'll let calibredb handle the error
                pass
        
        # Check for dependencies if not forcing
        if not force and book_id_int is not None:
            has_dependencies = await _check_book_dependencies(book_id_int)
            if has_dependencies:
                raise MCPServerError(
                    "Cannot delete book: it is referenced by other entities. "
                    "Use force=True to delete anyway."
                )
        
        # Use calibredb remove for proper deletion
        calibredb = _find_calibredb()
        files_deleted = False
        
        if calibredb:
            # Build calibredb remove command
            cmd = [
                calibredb,
                "remove",
                str(book_id),
                "--library-path",
                str(lib_path),
            ]
            
            # Add file deletion flag
            if delete_files:
                cmd.append("--permanent")  # Permanently delete files
            else:
                cmd.append("--dont-delete")  # Keep files, only remove from library
            
            logger.debug(f"Executing calibredb command: {' '.join(cmd)}")
            
            # Execute calibredb remove command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode("utf-8", errors="replace") if stderr else "Unknown error"
                logger.error(f"calibredb remove failed: {error_msg}")
                raise MCPServerError(f"Failed to delete book: {error_msg}")
            
            files_deleted = delete_files
            logger.info(f"Successfully deleted book {book_id} via calibredb")
        
        else:
            # Fallback to BookService if calibredb not available
            if book_id_int is None:
                raise MCPServerError(
                    "calibredb not found and book_id is not numeric. "
                    "Cannot delete book without calibredb."
                )
            
            logger.warning("calibredb not found, using BookService.delete() as fallback")
            
            # Delete from database
            try:
                book_service.delete(book_id_int)
            except NotFoundError:
                raise MCPServerError(f"Book with ID {book_id} not found")
            
            # Delete files if requested
            if delete_files:
                # Note: File deletion requires calibredb for proper Calibre integration
                # BookService.delete() only removes database entries
                logger.warning("File deletion not supported without calibredb")
            
            files_deleted = False  # Can't reliably delete files without calibredb
        
        # Prepare the response
        return {
            "success": True,
            "message": f"Book '{book_title}' deleted successfully",
            "book_id": str(book_id),
            "files_deleted": files_deleted,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    except MCPServerError:
        raise
    except Exception as e:
        logger.error(f"Error deleting book {book_id}: {e}", exc_info=True)
        raise MCPServerError(f"Failed to delete book: {str(e)}")


async def _check_book_dependencies(book_id: int) -> bool:
    """
    Check if a book has dependencies that would prevent deletion.

    Args:
        book_id: ID of the book to check

    Returns:
        bool: True if the book has dependencies, False otherwise
    """
    try:
        # Check if book is in any collections (smart collections reference books)
        # This is a simplified check - in a full implementation, you'd query:
        # 1. Collections table
        # 2. Reading lists
        # 3. Annotations/highlights
        # 4. Other references
        
        # Verify book exists (will raise NotFoundError if not)
        book_service.get_by_id(book_id)
        
        # Check if book has tags, series, etc. (these are relationships, not dependencies)
        # Real dependencies would be things like:
        # - Book is in a collection
        # - Book has annotations that should be preserved
        # - Book is referenced by other books
        
        # For now, return False (no blocking dependencies)
        # In production, implement proper dependency checking
        return False
    
    except NotFoundError:
        # Book doesn't exist, so no dependencies
        return False
    except Exception as e:
        logger.warning(f"Error checking book dependencies: {e}")
        # On error, assume no dependencies (allow deletion)
        return False
