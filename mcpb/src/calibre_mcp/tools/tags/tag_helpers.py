"""
Helper functions for tag management operations.

These functions are NOT registered as MCP tools - they are used internally
by the manage_tags portmanteau tool.
"""

from typing import List, Optional, Dict, Any

from ...logging_config import get_logger
from ...services.tag_service import tag_service
from ...services.base_service import NotFoundError, ValidationError
from ...models.tag import TagCreate, TagUpdate
from ...config import CalibreConfig

logger = get_logger("calibremcp.tools.tags.helpers")


async def list_tags_helper(
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "name",
    sort_order: str = "asc",
    unused_only: bool = False,
    min_book_count: Optional[int] = None,
    max_book_count: Optional[int] = None,
) -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
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


async def get_tag_helper(
    tag_id: Optional[int] = None, tag_name: Optional[str] = None
) -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
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


async def create_tag_helper(name: str) -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
            }

        result = tag_service.create(TagCreate(name=name))
        return result

    except ValidationError as e:
        return {"error": str(e), "message": str(e)}
    except Exception as e:
        logger.error(f"Error creating tag: {e}", exc_info=True)
        return {"error": str(e)}


async def update_tag_helper(tag_id: int, name: str) -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
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


async def delete_tag_helper(tag_id: int, force: bool = False) -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
            }

        result = tag_service.delete(tag_id, force=force)
        return {"success": result, "message": f"Tag {tag_id} deleted successfully"}

    except NotFoundError as e:
        return {"success": False, "error": str(e), "message": str(e)}
    except Exception as e:
        logger.error(f"Error deleting tag: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def find_duplicate_tags_helper(similarity_threshold: float = 0.8) -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
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


async def merge_tags_helper(
    source_tag_ids: List[int], target_tag_id: int
) -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
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


async def get_unused_tags_helper() -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
            }

        unused_tags = tag_service.get_unused_tags()
        return {"unused_tags": unused_tags, "count": len(unused_tags)}

    except Exception as e:
        logger.error(f"Error getting unused tags: {e}", exc_info=True)
        return {"error": str(e), "unused_tags": [], "count": 0}


async def delete_unused_tags_helper() -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
            }

        result = tag_service.delete_unused_tags()
        return result

    except Exception as e:
        logger.error(f"Error deleting unused tags: {e}", exc_info=True)
        return {"success": False, "error": str(e), "deleted_count": 0, "deleted_tags": []}


async def get_tag_statistics_helper() -> Dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        config = CalibreConfig()
        if not config.local_library_path:
            return {
                "error": "No library configured",
                "message": "Please use manage_libraries(operation='switch') to configure a library first.",
            }

        result = tag_service.get_tag_statistics()
        return result

    except Exception as e:
        logger.error(f"Error getting tag statistics: {e}", exc_info=True)
        return {"error": str(e)}


