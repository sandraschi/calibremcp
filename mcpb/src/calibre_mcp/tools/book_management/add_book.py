"""
Add Book Tool

This module provides functionality to add new books to the Calibre library.
"""
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from fastmcp import MCPServerError

from ...models import Book, BookFormat, BookStatus
from ...utils import (
    get_book_format_from_extension,
    extract_metadata,
    convert_book,
    generate_thumbnail,
    calculate_file_hash,
    FileTypeNotSupportedError
)

# Import the tool decorator from the parent package
from .. import tool

logger = logging.getLogger("calibremcp.tools.book_management")

@tool(
    name="add_book",
    description="Add a new book to the library from a file or URL",
    parameters={
        "file_path": {
            "type": "string",
            "description": "Path to the book file to add",
            "required": True
        },
        "metadata": {
            "type": "object",
            "description": "Optional metadata to override extracted metadata",
            "required": False
        },
        "fetch_metadata": {
            "type": "boolean",
            "description": "Whether to fetch metadata from online sources",
            "default": True
        },
        "convert_to": {
            "type": "string",
            "description": "Convert the book to this format before adding",
            "enum": [fmt.value for fmt in BookFormat],
            "required": False
        }
    }
)
async def add_book(
    file_path: str,
    metadata: Optional[Dict[str, Any]] = None,
    fetch_metadata: bool = True,
    convert_to: Optional[str] = None,
    library_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a new book to the Calibre library.
    
    Args:
        file_path: Path to the book file to add
        metadata: Optional metadata to override extracted metadata
        fetch_metadata: Whether to fetch metadata from online sources
        convert_to: Convert the book to this format before adding
        library_path: Path to the Calibre library
        
    Returns:
        Dictionary containing the added book's information
        
    Raises:
        MCPServerError: If there's an error adding the book
    """
    try:
        # Validate input parameters
        file_path = Path(file_path)
        if not file_path.exists():
            raise MCPServerError(f"File not found: {file_path}")
            
        # Set up library paths
        library_path = Path(library_path) if library_path else None
        if not library_path or not library_path.exists():
            raise MCPServerError("Invalid or missing library path")
            
        # Create necessary directories
        books_dir = library_path / "books"
        books_dir.mkdir(exist_ok=True)
        
        # Process the file
        file_hash = await calculate_file_hash(file_path)
        file_extension = file_path.suffix.lower()
        
        try:
            book_format = get_book_format_from_extension(file_extension)
        except FileTypeNotSupportedError:
            raise MCPServerError(f"Unsupported file format: {file_extension}")
        
        # Extract metadata
        book_metadata = await extract_metadata(file_path)
        
        # Apply any provided metadata overrides
        if metadata:
            for key, value in metadata.items():
                if hasattr(book_metadata, key) and value is not None:
                    setattr(book_metadata, key, value)
        
        # Generate a unique book ID (in a real implementation, this would come from a database)
        book_id = file_hash[:8]  # Use first 8 chars of hash as ID for this example
        
        # Create book directory
        book_dir = books_dir / str(book_id)
        book_dir.mkdir(exist_ok=True)
        
        # Copy the file to the library
        dest_filename = f"{book_id}{file_extension}"
        dest_path = book_dir / dest_filename
        shutil.copy2(file_path, dest_path)
        
        # Generate thumbnail
        thumbnail_path = book_dir / "cover.jpg"
        await generate_thumbnail(dest_path, output_path=thumbnail_path)
        
        # Create book record
        book = Book(
            id=book_id,
            title=book_metadata.title or file_path.stem,
            authors=book_metadata.authors or ["Unknown"],
            formats=[book_format],
            tags=book_metadata.tags or [],
            rating=book_metadata.rating,
            publisher=book_metadata.publisher,
            pubdate=book_metadata.pubdate,
            description=book_metadata.description,
            series=book_metadata.series,
            series_index=book_metadata.series_index,
            languages=book_metadata.languages or ["en"],
            size=dest_path.stat().st_size,
            file_path=str(dest_path),
            cover_path=str(thumbnail_path) if thumbnail_path.exists() else None,
            status=BookStatus.UNREAD,
            progress=0.0,
            date_added=book_metadata.date_added,
            last_modified=book_metadata.last_modified,
        )
        
        # In a real implementation, save the book to a database here
        
        # Convert to requested format if needed
        if convert_to and convert_to.lower() != book_format.value:
            try:
                target_format = BookFormat(convert_to.lower())
                converted_path = await convert_book(
                    dest_path,
                    target_format,
                    metadata=book_metadata
                )
                
                # Update book record with new format
                book.formats.append(target_format)
                
                # In a real implementation, update the database
                
            except Exception as e:
                logger.warning(f"Failed to convert book to {convert_to}: {e}")
        
        return {
            "id": book.id,
            "title": book.title,
            "authors": book.authors,
            "formats": [fmt.value for fmt in book.formats],
            "cover_url": f"/covers/{book.id}" if book.cover_path else None,
            "status": book.status.value,
            "progress": book.progress,
            "date_added": book.date_added.isoformat() if book.date_added else None,
        }
        
    except Exception as e:
        logger.error(f"Error adding book: {e}", exc_info=True)
        raise MCPServerError(f"Failed to add book: {str(e)}")
