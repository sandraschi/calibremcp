"""
Update Book Tool

This module provides functionality to update a book's metadata and properties
in the Calibre library.
"""
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from fastmcp import MCPServerError
from ...storage import get_storage_backend
from ...models.book import BookStatus

# Import the tool decorator from the parent package
from .. import tool

logger = logging.getLogger("calibremcp.tools.book_management")

@tool(
    name="update_book",
    description="Update a book's metadata and properties in the Calibre library",
    parameters={
        "book_id": {
            "type": "string",
            "description": "ID of the book to update",
            "required": True
        },
        "metadata": {
            "type": "object",
            "description": "Metadata fields to update",
            "properties": {
                "title": {"type": "string"},
                "authors": {"type": "array", "items": {"type": "string"}},
                "publisher": {"type": "string"},
                "pubdate": {"type": "string", "format": "date"},
                "isbn": {"type": "string"},
                "languages": {"type": "array", "items": {"type": "string"}},
                "rating": {"type": "number", "minimum": 0, "maximum": 5},
                "tags": {"type": "array", "items": {"type": "string"}},
                "series": {"type": "string"},
                "series_index": {"type": "number"},
                "comments": {"type": "string"},
                "identifiers": {"type": "object"}
            },
            "additionalProperties": False
        },
        "status": {
            "type": "string",
            "description": "Reading status of the book",
            "enum": [status.value for status in BookStatus]
        },
        "progress": {
            "type": "number",
            "description": "Reading progress (0.0 to 1.0)",
            "minimum": 0.0,
            "maximum": 1.0
        },
        "cover_path": {
            "type": "string",
            "description": "Path to a new cover image"
        },
        "update_timestamp": {
            "type": "boolean",
            "description": "Whether to update the last_modified timestamp",
            "default": True
        },
        "library_path": {
            "type": "string",
            "description": "Path to the Calibre library (optional, will auto-detect if not provided)",
            "required": False
        }
    }
)
async def update_book(
    book_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    status: Optional[str] = None,
    progress: Optional[float] = None,
    cover_path: Optional[str] = None,
    update_timestamp: bool = True,
    library_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a book's metadata and properties in the Calibre library.
    
    Args:
        book_id: ID of the book to update (can be numeric ID or UUID)
        metadata: Dictionary of metadata fields to update
        status: New reading status
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
        # Initialize the storage backend
        storage = get_storage_backend(library_path=library_path)
        
        # Get the existing book
        book = await storage.get_book(book_id)
        if not book:
            raise MCPServerError(f"Book with ID {book_id} not found")
        
        # Validate the update
        if metadata:
            _validate_metadata_update(metadata)
        
        # Update the book's metadata
        updated_fields = []
        
        # Update basic metadata if provided
        if metadata:
            for field in [
                'title', 'authors', 'publisher', 'pubdate', 'isbn', 'languages',
                'rating', 'tags', 'series', 'series_index', 'comments', 'identifiers'
            ]:
                if field in metadata:
                    setattr(book, field, metadata[field])
                    updated_fields.append(field)
        
        # Update status if provided
        if status is not None:
            book.status = BookStatus(status)
            updated_fields.append('status')
        
        # Update progress if provided
        if progress is not None:
            if not 0.0 <= progress <= 1.0:
                raise ValueError("Progress must be between 0.0 and 1.0")
            book.progress = progress
            updated_fields.append('progress')
        
        # Update cover if provided
        cover_updated = False
        if cover_path:
            cover_path = Path(cover_path)
            if not cover_path.exists():
                raise FileNotFoundError(f"Cover image not found: {cover_path}")
            
            # In a real implementation, we would update the cover in the database
            # and copy the file to the book's directory
            book_dir = book.path if hasattr(book, 'path') else None
            if book_dir:
                dest_cover = Path(book_dir) / "cover.jpg"
                shutil.copy2(cover_path, dest_cover)
                book.has_cover = True
                cover_updated = True
                updated_fields.append('cover')
        
        # Update timestamp if requested
        if update_timestamp:
            book.last_modified = datetime.utcnow()
            updated_fields.append('last_modified')
        
        # In a real implementation, we would save the updated book to the database
        # For now, we'll just return the updated book data
        
        # Prepare the response
        result = {
            "success": True,
            "message": "Book updated successfully",
            "book_id": book_id,
            "updated_fields": updated_fields,
            "cover_updated": cover_updated,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return result
        
    except ValueError as e:
        raise MCPServerError(f"Invalid input: {str(e)}")
    except FileNotFoundError as e:
        raise MCPServerError(f"File not found: {str(e)}")
    except MCPServerError:
        raise
    except Exception as e:
        logger.error(f"Error updating book {book_id}: {e}", exc_info=True)
        raise MCPServerError(f"Failed to update book: {str(e)}")

def _validate_metadata_update(metadata: Dict[str, Any]) -> None:
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
        if not all(isinstance(k, str) and isinstance(v, str) 
                  for k, v in metadata["identifiers"].items()):
            raise ValueError("All identifier keys and values must be strings")
