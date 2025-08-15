"""
Get Book Tool

This module provides functionality to retrieve detailed information about a specific book
from the Calibre library.
"""
import logging
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastmcp import MCPServerError
from ...storage import get_storage_backend
from ...models.book import Book, BookStatus, BookFormat

# Import the tool decorator from the parent package
from .. import tool

logger = logging.getLogger("calibremcp.tools.book_management")

@tool(
    name="get_book",
    description="Get detailed information about a specific book from the Calibre library",
    parameters={
        "book_id": {
            "type": "string",
            "description": "ID of the book to retrieve",
            "required": True
        },
        "include_metadata": {
            "type": "boolean",
            "description": "Whether to include full metadata in the response",
            "default": True
        },
        "include_formats": {
            "type": "boolean",
            "description": "Whether to include information about available formats",
            "default": True
        },
        "include_cover": {
            "type": "boolean",
            "description": "Whether to include cover image data (as base64)",
            "default": False
        },
        "library_path": {
            "type": "string",
            "description": "Path to the Calibre library (optional, will auto-detect if not provided)",
            "required": False
        }
    }
)
async def get_book(
    book_id: str,
    include_metadata: bool = True,
    include_formats: bool = True,
    include_cover: bool = False,
    library_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific book from the Calibre library.
    
    Args:
        book_id: ID of the book to retrieve (can be numeric ID or UUID)
        include_metadata: Whether to include full metadata
        include_formats: Whether to include format information
        include_cover: Whether to include cover image data
        library_path: Optional path to the Calibre library
        
    Returns:
        Dictionary containing the book's information
        
    Raises:
        MCPServerError: If the book cannot be found or there's an error
    """
    try:
        # Initialize the storage backend
        storage = get_storage_backend(library_path=library_path)
        
        # Get the basic book information
        book = await storage.get_book(book_id)
        if not book:
            raise MCPServerError(f"Book with ID {book_id} not found")
        
        # Prepare the result dictionary
        result = {
            "id": book.id,
            "title": book.title,
            "authors": book.authors,
            "has_cover": book.has_cover,
            "timestamp": book.timestamp.isoformat() if book.timestamp else None,
            "last_modified": book.last_modified.isoformat() if book.last_modified else None,
            "path": str(book.path) if book.path else None,
            "uuid": book.uuid
        }
        
        # Add additional metadata if requested
        if include_metadata:
            # Get additional metadata from the database
            result.update(await _get_book_metadata(storage, book))
        
        # Add format information if requested
        if include_formats:
            result["formats"] = await _get_book_formats(storage, book)
        
        # Add cover if requested
        if include_cover and book.has_cover and book.path:
            cover_data = await _get_cover_data(book.path)
            if cover_data:
                result["cover"] = cover_data
        
        return result
        
    except MCPServerError:
        raise
    except Exception as e:
        logger.error(f"Error getting book {book_id}: {e}", exc_info=True)
        raise MCPServerError(f"Failed to get book: {str(e)}")

async def _get_book_metadata(storage, book) -> Dict[str, Any]:
    """Get additional metadata for a book"""
    # This is a simplified implementation. In a real app, you would query the database
    # for additional metadata like tags, series, etc.
    return {
        "publisher": book.publisher,
        "pubdate": book.pubdate.isoformat() if book.pubdate else None,
        "series": book.series,
        "series_index": book.series_index,
        "rating": book.rating,
        "tags": book.tags if hasattr(book, 'tags') else [],
        "identifiers": book.identifiers if hasattr(book, 'identifiers') else {},
        "comments": book.comments if hasattr(book, 'comments') else ""
    }

async def _get_book_formats(storage, book) -> List[Dict[str, Any]]:
    """Get information about available formats for a book"""
    # This is a simplified implementation. In a real app, you would query the database
    # for available formats and their sizes
    formats = []
    if hasattr(book, 'formats') and book.formats:
        for fmt in book.formats:
            formats.append({
                "format": fmt.upper(),
                "size": 0,  # Would get actual file size in a real implementation
                "path": str(book.path / f"book.{fmt.lower()}") if book.path else None
            })
    return formats

async def _get_cover_data(book_path: Path) -> Optional[Dict[str, Any]]:
    """Read cover image data as base64"""
    try:
        cover_path = book_path / "cover.jpg"
        if not cover_path.exists():
            return None
            
        with open(cover_path, "rb") as f:
            image_data = f.read()
            
        return {
            "format": "jpeg",
            "data": base64.b64encode(image_data).decode('utf-8'),
            "size": len(image_data)
        }
    except Exception as e:
        logger.warning(f"Failed to read cover image: {e}")
        return None
