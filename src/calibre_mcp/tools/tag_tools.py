"""
DEPRECATED: Individual tag tools are deprecated in favor of the manage_tags
portmanteau tool (see tools/tags/manage_tags.py). These functions are kept
as legacy helpers but are no longer registered with FastMCP 2.13+.

Use manage_tags(operation="...") instead:
- list_tags() → manage_tags(operation="list", ...)
- get_tag() → manage_tags(operation="get", ...)
- create_tag() → manage_tags(operation="create", ...)
- update_tag() → manage_tags(operation="update", ...)
- delete_tag() → manage_tags(operation="delete", ...)
- find_duplicate_tags() → manage_tags(operation="find_duplicates", ...)
- merge_tags() → manage_tags(operation="merge", ...)
- get_unused_tags() → manage_tags(operation="get_unused")
- delete_unused_tags() → manage_tags(operation="delete_unused")
- get_simple_tag_statistics() → manage_tags(operation="statistics")
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..logging_config import get_logger
from ..services.tag_service import tag_service
from ..services.base_service import NotFoundError, ValidationError
from ..models.tag import TagCreate, TagUpdate
from ..config import CalibreConfig

logger = get_logger("calibremcp.tools.tag_tools")


class TagInfo(BaseModel):
    """Tag model with book count."""

    id: int = Field(..., description="Unique tag ID")
    name: str = Field(..., description="Tag name")
    book_count: int = Field(0, description="Number of books with this tag")

    class Config:
        json_encoders = {"datetime": lambda v: v.isoformat() if v else None}


class TagListInput(BaseModel):
    """Input model for listing tags."""

    search: Optional[str] = Field(None, description="Search query to filter tags by name")
    limit: int = Field(100, description="Maximum number of results to return", ge=1, le=1000)
    offset: int = Field(0, description="Number of results to skip (for pagination)", ge=0)
    sort_by: str = Field(
        "name", description="Field to sort by (name, book_count)", pattern="^(name|book_count)$"
    )
    sort_order: str = Field("asc", description="Sort order (asc, desc)", pattern="^(asc|desc)$")
    unused_only: bool = Field(False, description="If True, only return tags with 0 books")
    min_book_count: Optional[int] = Field(
        None, description="Minimum number of books using this tag", ge=0
    )
    max_book_count: Optional[int] = Field(
        None, description="Maximum number of books using this tag", ge=0
    )


class TagListOutput(BaseModel):
    """Output model for paginated tag list."""

    items: List[TagInfo] = Field(..., description="List of matching tags")
    total: int = Field(..., description="Total number of matching tags")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class TagCreateInput(BaseModel):
    """Input model for creating a tag."""

    name: str = Field(..., description="Name of the tag to create", min_length=1)


class TagUpdateInput(BaseModel):
    """Input model for updating a tag."""

    name: str = Field(..., description="New name for the tag", min_length=1)


class TagMergeInput(BaseModel):
    """Input model for merging tags."""

    source_tag_ids: List[int] = Field(..., description="List of tag IDs to merge from", min_items=1)
    target_tag_id: int = Field(..., description="Tag ID to merge into (target tag)")


class DuplicateTagsOutput(BaseModel):
    """Output model for duplicate tags detection."""

    duplicate_groups: List[Dict[str, Any]] = Field(
        ..., description="List of groups of similar/duplicate tags"
    )
    total_duplicates: int = Field(..., description="Total number of duplicate groups found")
    similarity_threshold: float = Field(..., description="Similarity threshold used (0.0-1.0)")


class TagStatsOutput(BaseModel):
    """Output model for tag statistics."""

    total_tags: int = Field(..., description="Total number of tags")
    unused_tags_count: int = Field(..., description="Number of unused tags")
    used_tags_count: int = Field(..., description="Number of tags in use")
    top_tags: List[Dict[str, Any]] = Field(..., description="Top tags by book count")
    average_books_per_tag: float = Field(..., description="Average books per tag")


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def list_tags(
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "name",
    sort_order: str = "asc",
    unused_only: bool = False,
    min_book_count: Optional[int] = None,
    max_book_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    List all tags with filtering, sorting, and pagination.

    Supports searching tags by name, filtering by usage (book count),
    and finding unused tags. Essential for tag management and weeding.

    Args:
        search: Search term to filter tags by name (case-insensitive partial match)
        limit: Maximum number of results to return (1-1000, default: 100)
        offset: Number of results to skip for pagination (default: 0)
        sort_by: Field to sort by - "name" or "book_count" (default: "name")
        sort_order: Sort order - "asc" or "desc" (default: "asc")
        unused_only: If True, only return tags with 0 books (default: False)
        min_book_count: Minimum number of books using this tag (default: None)
        max_book_count: Maximum number of books using this tag (default: None)

    Returns:
        Dictionary containing paginated list of tags:
        {
            "items": [{"id": 1, "name": "mystery", "book_count": 42}, ...],
            "total": 150,
            "page": 1,
            "per_page": 100,
            "total_pages": 2
        }

    Examples:
        # List all tags
        list_tags()

        # Search for tags containing "mystery"
        list_tags(search="mystery")

        # Find unused tags only
        list_tags(unused_only=True)

        # Find popular tags (used by 10+ books)
        list_tags(min_book_count=10, sort_by="book_count", sort_order="desc")

        # Find rarely used tags (1-5 books)
        list_tags(min_book_count=1, max_book_count=5, sort_by="book_count")
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        result = tag_service.get_all(
            skip=offset,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            unused_only=unused_only,
            min_book_count=min_book_count,
            max_book_count=max_book_count,
        )

        return result

    except Exception as e:
        logger.error(f"Error listing tags: {e}", exc_info=True)
        return {
            "error": str(e),
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": limit,
            "total_pages": 0,
        }


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def get_tag(tag_id: Optional[int] = None, tag_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get details for a specific tag by ID or name.

    Args:
        tag_id: The ID of the tag (either tag_id or tag_name required)
        tag_name: The name of the tag (either tag_id or tag_name required)

    Returns:
        Dictionary containing tag details with book count

    Examples:
        # Get by ID
        get_tag(tag_id=123)

        # Get by name
        get_tag(tag_name="mystery")
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        if tag_id:
            result = tag_service.get_by_id(tag_id)
        elif tag_name:
            result = tag_service.get_by_name(tag_name)
            if not result:
                return {
                    "error": "Tag not found",
                    "message": f"Tag with name '{tag_name}' not found",
                }
        else:
            return {
                "error": "Missing parameter",
                "message": "Either tag_id or tag_name must be provided",
            }

        return result

    except NotFoundError as e:
        return {"error": str(e), "message": str(e)}
    except Exception as e:
        logger.error(f"Error getting tag: {e}", exc_info=True)
        return {"error": str(e)}


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def create_tag(name: str) -> Dict[str, Any]:
    """
    Create a new tag.

    Tag names are automatically normalized (trimmed and title-cased).
    If a tag with the same name already exists, an error is returned.

    Args:
        name: Name of the tag to create

    Returns:
        Dictionary containing the created tag details

    Examples:
        create_tag(name="locked room mystery")
        # Returns: {"id": 123, "name": "Locked Room Mystery", "book_count": 0}
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        result = tag_service.create(TagCreate(name=name))
        return result

    except ValidationError as e:
        return {"error": str(e), "message": str(e)}
    except Exception as e:
        logger.error(f"Error creating tag: {e}", exc_info=True)
        return {"error": str(e)}


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def update_tag(tag_id: int, name: str) -> Dict[str, Any]:
    """
    Update (rename) an existing tag.

    The tag name is automatically normalized. All books with the old tag
    will now have the new tag name.

    Args:
        tag_id: ID of the tag to update
        name: New name for the tag

    Returns:
        Dictionary containing the updated tag details

    Examples:
        update_tag(tag_id=123, name="detective fiction")
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        result = tag_service.update(tag_id, TagUpdate(name=name))
        return result

    except NotFoundError as e:
        return {"error": str(e), "message": str(e)}
    except ValidationError as e:
        return {"error": str(e), "message": str(e)}
    except Exception as e:
        logger.error(f"Error updating tag: {e}", exc_info=True)
        return {"error": str(e)}


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def delete_tag(tag_id: int, force: bool = False) -> Dict[str, Any]:
    """
    Delete a tag.

    The tag is removed from all books that have it. The tag itself is deleted.

    Args:
        tag_id: ID of the tag to delete
        force: If True, delete even if tag has books (currently always removes from books)

    Returns:
        Dictionary with success status

    Examples:
        delete_tag(tag_id=123)
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        result = tag_service.delete(tag_id, force=force)
        return {"success": result, "message": f"Tag {tag_id} deleted successfully"}

    except NotFoundError as e:
        return {"success": False, "error": str(e), "message": str(e)}
    except Exception as e:
        logger.error(f"Error deleting tag: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def find_duplicate_tags(similarity_threshold: float = 0.8) -> Dict[str, Any]:
    """
    Find duplicate or similar tags that should be merged (tag weeding).

    Uses string similarity matching to find tags that are likely duplicates
    (e.g., "sci-fi" and "scifi", "mystery" and "mysteries").

    Args:
        similarity_threshold: Similarity score threshold (0.0-1.0) for considering tags similar.
                             Higher values = more strict (only very similar tags).
                             Lower values = less strict (more potential matches).
                             Default: 0.8 (80% similar)

    Returns:
        Dictionary containing groups of similar tags:
        {
            "duplicate_groups": [
                {
                    "tags": [
                        {"id": 1, "name": "sci-fi", "book_count": 50},
                        {"id": 2, "name": "scifi", "book_count": 3}
                    ],
                    "suggested_name": "sci-fi",  # Most popular tag
                    "total_books": 53
                },
                ...
            ],
            "total_duplicates": 5,
            "similarity_threshold": 0.8
        }

    Examples:
        # Find duplicates with default threshold (0.8)
        find_duplicate_tags()

        # More strict (only 90%+ similar)
        find_duplicate_tags(similarity_threshold=0.9)

        # Less strict (70%+ similar)
        find_duplicate_tags(similarity_threshold=0.7)
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        duplicates = tag_service.find_duplicates(similarity_threshold=similarity_threshold)

        return {
            "duplicate_groups": duplicates,
            "total_duplicates": len(duplicates),
            "similarity_threshold": similarity_threshold,
        }

    except Exception as e:
        logger.error(f"Error finding duplicate tags: {e}", exc_info=True)
        return {
            "error": str(e),
            "duplicate_groups": [],
            "total_duplicates": 0,
            "similarity_threshold": similarity_threshold,
        }


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def merge_tags(source_tag_ids: List[int], target_tag_id: int) -> Dict[str, Any]:
    """
    Merge multiple source tags into a target tag (tag weeding).

    All books tagged with source tags will be retagged with the target tag.
    Source tags will be deleted after merging.

    This is useful for consolidating duplicate tags found by find_duplicate_tags().

    Args:
        source_tag_ids: List of tag IDs to merge from (these will be deleted)
        target_tag_id: Tag ID to merge into (this tag will be kept)

    Returns:
        Dictionary with merge results:
        {
            "success": True,
            "target_tag": {"id": 1, "name": "sci-fi", "book_count": 53},
            "merged_tags": ["scifi", "science fiction"],
            "books_affected": 53
        }

    Examples:
        # Merge duplicate tags into the most popular one
        merge_tags(source_tag_ids=[2, 3], target_tag_id=1)
        # This merges tags 2 and 3 into tag 1, then deletes tags 2 and 3
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        result = tag_service.merge_tags(source_tag_ids, target_tag_id)
        return result

    except NotFoundError as e:
        return {"success": False, "error": str(e), "message": str(e)}
    except ValidationError as e:
        return {"success": False, "error": str(e), "message": str(e)}
    except Exception as e:
        logger.error(f"Error merging tags: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def get_unused_tags() -> Dict[str, Any]:
    """
    Get all tags that are not assigned to any books.

    These are good candidates for deletion during tag weeding.

    Returns:
        Dictionary containing list of unused tags:
        {
            "unused_tags": [
                {"id": 123, "name": "old tag", "book_count": 0},
                ...
            ],
            "count": 5
        }

    Examples:
        unused = get_unused_tags()
        print(f"Found {unused['count']} unused tags")
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        unused_tags = tag_service.get_unused_tags()
        return {"unused_tags": unused_tags, "count": len(unused_tags)}

    except Exception as e:
        logger.error(f"Error getting unused tags: {e}", exc_info=True)
        return {"error": str(e), "unused_tags": [], "count": 0}


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def delete_unused_tags() -> Dict[str, Any]:
    """
    Delete all tags that are not assigned to any books.

    This is a safe cleanup operation that removes orphaned tags.
    Use after reviewing unused tags with get_unused_tags().

    Returns:
        Dictionary with deletion results:
        {
            "success": True,
            "deleted_count": 5,
            "deleted_tags": ["old tag 1", "old tag 2", ...]
        }

    Examples:
        # First check what will be deleted
        unused = get_unused_tags()
        print(f"Will delete {unused['count']} unused tags")

        # Then delete them
        result = delete_unused_tags()
        print(f"Deleted {result['deleted_count']} tags")
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        result = tag_service.delete_unused_tags()
        return result

    except Exception as e:
        logger.error(f"Error deleting unused tags: {e}", exc_info=True)
        return {"success": False, "error": str(e), "deleted_count": 0, "deleted_tags": []}


# NOTE: @mcp.tool() decorator removed - use manage_tags portmanteau tool instead
async def get_simple_tag_statistics() -> Dict[str, Any]:
    """
    Get comprehensive statistics about tags in the library.

    Useful for understanding tag usage and planning tag weeding operations.

    Returns:
        Dictionary containing tag statistics:
        {
            "total_tags": 500,
            "unused_tags_count": 25,
            "used_tags_count": 475,
            "top_tags": [
                {"id": 1, "name": "fiction", "book_count": 1000},
                {"id": 2, "name": "mystery", "book_count": 500},
                ...
            ],
            "average_books_per_tag": 10.5
        }

    Examples:
        stats = get_simple_tag_statistics()
        print(f"Total tags: {stats['total_tags']}")
        print(f"Unused tags: {stats['unused_tags_count']}")
        print(f"Top tag: {stats['top_tags'][0]['name']}")
    """
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use 'switch_library' to configure a library first.",
            }

        result = tag_service.get_tag_statistics()
        return result

    except Exception as e:
        logger.error(f"Error getting tag statistics: {e}", exc_info=True)
        return {"error": str(e)}

