"""
Get Book Tool

This module provides functionality to retrieve detailed information about a specific book
from the Calibre library.
"""

from typing import Dict, Any, Optional

from ...tools.compat import MCPServerError
from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.book_management")


# Helper function - called by manage_books portmanteau tool
# NOT registered as MCP tool (no @tool or @mcp.tool() decorator)
async def get_book_helper(
    book_id: str,
    include_metadata: bool = True,
    include_formats: bool = True,
    include_cover: bool = False,
    library_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get detailed information about a specific book from the Calibre library.

    Uses the same data source as search_books_helper - either API client or database service.

    Args:
        book_id: ID of the book to retrieve (can be numeric ID or UUID)
        include_metadata: Whether to include full metadata
        include_formats: Whether to include format information
        include_cover: Whether to include cover image data
        library_path: Optional path to the Calibre library (for future use)

    Returns:
        Dictionary containing the book's information

    Raises:
        MCPServerError: If the book cannot be found or there's an error
    """
    try:
        # Try API client first (same as search_books_helper and details operation)
        from ...server import get_api_client
        
        client = await get_api_client()
        if client:
            # Use API client to get book details (same as details operation)
            try:
                book_data = await client.get_book_details(int(book_id))
                if not book_data:
                    raise MCPServerError(f"Book with ID {book_id} not found")
                
                # Format response similar to storage backend format
                result = {
                    "id": book_data.get("id", int(book_id)),
                    "title": book_data.get("title", "Unknown"),
                    "authors": book_data.get("authors", []),
                    "has_cover": book_data.get("has_cover", False),
                    "timestamp": book_data.get("timestamp"),
                    "last_modified": book_data.get("last_modified"),
                    "path": book_data.get("path"),
                    "uuid": book_data.get("uuid"),
                }
                
                # Add additional metadata if requested
                if include_metadata:
                    result.update({
                        "publisher": book_data.get("publisher"),
                        "pubdate": book_data.get("pubdate"),
                        "series": book_data.get("series"),
                        "series_index": book_data.get("series_index"),
                        "rating": book_data.get("rating"),
                        "tags": book_data.get("tags", []),
                        "identifiers": book_data.get("identifiers", {}),
                        "comments": book_data.get("comments", ""),
                    })
                
                # Add format information if requested
                if include_formats:
                    result["formats"] = book_data.get("formats", [])
                
                # Add cover if requested
                if include_cover and book_data.get("cover_url"):
                    # Note: Cover data would need to be fetched separately if needed
                    result["cover_url"] = book_data.get("cover_url")
                
                return result
            except (ValueError, TypeError):
                # book_id might be UUID, try UUID lookup
                logger.debug(f"book_id {book_id} is not numeric, trying UUID lookup")
                # Fall through to database lookup
                pass
        
        # Fall back to database service (same as search_books_helper)
        from ...db.database import get_database
        from ...services.book_service import BookService
        
        db = get_database()
        book_service = BookService(db)
        
        try:
            book_id_int = int(book_id)
        except (ValueError, TypeError):
            # Try UUID lookup
            with db.session_scope() as session:
                from ...db.models import Book
                book = session.query(Book).filter(Book.uuid == book_id).first()
                if not book:
                    raise MCPServerError(f"Book with ID or UUID {book_id} not found")
                book_id_int = book.id
        
        # Get book using book service (same database as search)
        try:
            book_data = book_service.get_by_id(book_id_int)
        except Exception as e:
            if "not found" in str(e).lower():
                raise MCPServerError(f"Book with ID {book_id} not found")
            raise
        
        if not book_data:
            raise MCPServerError(f"Book with ID {book_id} not found")

        # book_data is already a dict from BookResponse model
        # Extract authors list from the response
        authors_list = []
        if isinstance(book_data.get("authors"), list):
            authors_list = [a.get("name", "") if isinstance(a, dict) else str(a) for a in book_data["authors"]]
        elif book_data.get("authors"):
            authors_list = [str(book_data["authors"])]

        # Prepare the result dictionary
        result = {
            "id": book_data.get("id", book_id_int),
            "title": book_data.get("title", "Unknown"),
            "authors": authors_list,
            "has_cover": book_data.get("has_cover", False),
            "timestamp": book_data.get("timestamp"),
            "last_modified": book_data.get("last_modified"),
            "path": book_data.get("path"),
            "uuid": book_data.get("uuid"),
        }

        # Add additional metadata if requested
        if include_metadata:
            result.update({
                "publisher": book_data.get("publisher"),
                "pubdate": book_data.get("pubdate"),
                "series": book_data.get("series", {}).get("name") if isinstance(book_data.get("series"), dict) else book_data.get("series"),
                "series_index": book_data.get("series_index"),
                "rating": book_data.get("rating"),
                "tags": [t.get("name", "") if isinstance(t, dict) else str(t) for t in book_data.get("tags", [])] if isinstance(book_data.get("tags"), list) else [],
                "identifiers": book_data.get("identifiers", {}),
                "comments": book_data.get("comments", ""),
            })

        # Add format information if requested
        if include_formats:
            formats = book_service.get_book_formats(book_id_int)
            result["formats"] = formats

        # Add cover if requested
        if include_cover and book_data.get("has_cover"):
            cover_data = book_service.get_book_cover(book_id_int)
            if cover_data:
                import base64
                result["cover"] = {
                    "format": "jpeg",
                    "data": base64.b64encode(cover_data).decode("utf-8"),
                    "size": len(cover_data),
                }

        return result

    except MCPServerError:
        raise
    except Exception as e:
        logger.error(f"Error getting book {book_id}: {e}", exc_info=True)
        raise MCPServerError(f"Failed to get book: {str(e)}")


