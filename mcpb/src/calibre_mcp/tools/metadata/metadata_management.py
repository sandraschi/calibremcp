"""
DEPRECATED: Individual metadata tools are deprecated in favor of the manage_metadata
portmanteau tool (see tools/metadata/manage_metadata.py). These functions are kept
as helpers but are no longer registered with FastMCP 2.13+.

Use manage_metadata(operation="...") instead:
- update_book_metadata() → manage_metadata(operation="update", updates=...)
- auto_organize_tags() → manage_metadata(operation="organize_tags")
- fix_metadata_issues() → manage_metadata(operation="fix_issues")
"""

from typing import List, Dict, Any
from datetime import datetime

# Import the MCP server instance

# Import response models
from ...server import MetadataUpdateRequest, MetadataUpdateResponse, TagStatsResponse

# Import services
from ...services.book_service import book_service
from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.metadata_management")


# NOTE: @mcp.tool() decorator removed - use manage_metadata portmanteau tool instead
async def update_book_metadata_helper(updates: List[MetadataUpdateRequest]) -> MetadataUpdateResponse:
    """
    Update metadata for single or multiple books.

    Allows bulk updates to book metadata including title, author,
    publication date, tags, and other bibliographic information.
    Each update request specifies a book ID, field name, and new value.

    Args:
        updates: List of metadata update requests, where each request contains:
            - book_id: ID of the book to update
            - field: Name of the field to update (e.g., "title", "series_index", "tag_ids")
            - value: New value for the field (type depends on field)

    Returns:
        MetadataUpdateResponse containing:
        {
            "updated_books": List[int] - IDs of successfully updated books
            "failed_updates": List[Dict] - Failed updates with error details
            "success_count": int - Number of successful updates
        }

    Example:
        # Update a book's title
        result = update_book_metadata([
            {"book_id": 123, "field": "title", "value": "New Title"}
        ])

        # Update multiple fields for one book
        result = update_book_metadata([
            {"book_id": 123, "field": "title", "value": "New Title"},
            {"book_id": 123, "field": "series_index", "value": 2.0},
            {"book_id": 123, "field": "rating", "value": 5}
        ])

        # Bulk update multiple books
        result = update_book_metadata([
            {"book_id": 123, "field": "tag_ids", "value": [1, 2, 3]},
            {"book_id": 124, "field": "tag_ids", "value": [1, 2, 3]},
            {"book_id": 125, "field": "tag_ids", "value": [1, 2, 3]}
        ])
    """
    updated_books: List[int] = []
    failed_updates: List[Dict[str, Any]] = []

    # Group updates by book_id to batch them
    updates_by_book: Dict[int, Dict[str, Any]] = {}

    for update in updates:
        book_id = update.book_id
        field = update.field
        value = update.value

        if book_id not in updates_by_book:
            updates_by_book[book_id] = {}

        # Handle special fields that need conversion
        if field == "tag_ids" and isinstance(value, list):
            updates_by_book[book_id]["tag_ids"] = value
        elif field == "author_ids" and isinstance(value, list):
            updates_by_book[book_id]["author_ids"] = value
        elif field == "series_id":
            updates_by_book[book_id]["series_id"] = value
        elif field == "rating":
            # Validate rating range
            if value is not None and (not isinstance(value, int) or value < 1 or value > 5):
                failed_updates.append(
                    {
                        "book_id": book_id,
                        "field": field,
                        "error": f"Rating must be between 1 and 5, got: {value}",
                    }
                )
                continue
            updates_by_book[book_id]["rating"] = value
        elif field == "pubdate" and isinstance(value, str):
            # Convert ISO date string to datetime
            try:
                updates_by_book[book_id]["pubdate"] = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
            except ValueError:
                failed_updates.append(
                    {"book_id": book_id, "field": field, "error": f"Invalid date format: {value}"}
                )
                continue
        else:
            # Simple field update
            updates_by_book[book_id][field] = value

    # Process each book's updates
    for book_id, update_data in updates_by_book.items():
        try:
            book_service.update(book_id, update_data)
            updated_books.append(book_id)
        except Exception as e:
            failed_updates.append(
                {"book_id": book_id, "fields": list(update_data.keys()), "error": str(e)}
            )
            logger.warning(f"Failed to update book {book_id}: {e}")

    return MetadataUpdateResponse(
        updated_books=updated_books, failed_updates=failed_updates, success_count=len(updated_books)
    )


# NOTE: @mcp.tool() decorator removed - use manage_metadata portmanteau tool instead
async def auto_organize_tags_helper() -> TagStatsResponse:
    """
    AI-powered tag organization and cleanup suggestions.

    Uses similarity matching to identify duplicate tags,
    suggests tag hierarchies, and provides cleanup recommendations.

    Returns:
        TagStatsResponse: Tag organization suggestions and cleanup stats
    """
    # Implementation will be moved from server.py
    pass


# NOTE: @mcp.tool() decorator removed - use manage_metadata portmanteau tool instead
async def fix_metadata_issues_helper() -> MetadataUpdateResponse:
    """
    Automatically fix common metadata problems.

    Fixes missing dates, standardizes author names, corrects
    publication information, and resolves other common metadata issues.

    Returns:
        MetadataUpdateResponse: Results of automatic metadata fixes
    """
    # Implementation will be moved from server.py
    pass
