"""
Tag management portmanteau tool for CalibreMCP.

Consolidates all tag-related operations into a single unified interface.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Import helper functions (NOT registered as MCP tools)
from .tag_helpers import (
    create_tag_helper,
    delete_tag_helper,
    delete_unused_tags_helper,
    find_duplicate_tags_helper,
    get_tag_helper,
    get_tag_statistics_helper,
    get_unused_tags_helper,
    list_tags_helper,
    merge_tags_helper,
    update_tag_helper,
)

logger = get_logger("calibremcp.tools.tags")


@mcp.tool()
async def manage_tags(
    operation: str,
    # List operation parameters
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "name",
    sort_order: str = "asc",
    unused_only: bool = False,
    min_book_count: int | None = None,
    max_book_count: int | None = None,
    # Get operation parameters
    tag_id: int | None = None,
    tag_name: str | None = None,
    # Create operation parameters
    name: str | None = None,
    # Update operation parameters
    new_name: str | None = None,
    # Delete operation parameters
    force: bool = False,
    # Find duplicates operation parameters
    similarity_threshold: float = 0.8,
    # Merge operation parameters
    source_tag_ids: list[int] | None = None,
    target_tag_id: int | None = None,
) -> dict[str, Any]:
    """
    Comprehensive tag management for Calibre.

    Operations:
    - list: List tags with filtering, sorting, and pagination.
    - get: Get tag details by ID or name.
    - create: Create a new tag.
    - update: Rename an existing tag.
    - delete: Delete a tag from the library.
    - find_duplicates/merge: Tag weeding and consolidation.
    - get_unused/delete_unused: Cleanup of orphaned tags.
    - statistics: Tag usage metrics.

    Examples:
    - manage_tags(operation="list", search="mystery", sort_by="book_count")
    - manage_tags(operation="find_duplicates", similarity_threshold=0.9)
    """
    try:
        if operation == "list":
            try:
                return await list_tags_helper(
                    search=search,
                    limit=limit,
                    offset=offset,
                    sort_by=sort_by,
                    sort_order=sort_order,
                    unused_only=unused_only,
                    min_book_count=min_book_count,
                    max_book_count=max_book_count,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"search": search, "limit": limit, "offset": offset},
                    tool_name="manage_tags",
                    context="Listing tags",
                )

        elif operation == "get":
            if not tag_id and not tag_name:
                return format_error_response(
                    error_msg=(
                        "Either tag_id or tag_name is required for operation='get'. "
                        "Use operation='list' to find available tags."
                    ),
                    error_code="MISSING_TAG_IDENTIFIER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide tag_id parameter (e.g., tag_id=123)",
                        "OR provide tag_name parameter (e.g., tag_name='mystery')",
                        "Use operation='list' to see all available tags",
                    ],
                    related_tools=["manage_tags"],
                )
            try:
                return await get_tag_helper(tag_id=tag_id, tag_name=tag_name)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"tag_id": tag_id, "tag_name": tag_name},
                    tool_name="manage_tags",
                    context=f"Getting tag details for {tag_id or tag_name}",
                )

        elif operation == "create":
            if not name:
                return format_error_response(
                    error_msg=(
                        "name is required for operation='create'. "
                        "Provide the name of the tag to create."
                    ),
                    error_code="MISSING_NAME",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide name parameter (e.g., name='mystery')",
                        "Tag names are automatically normalized (trimmed and title-cased)",
                    ],
                    related_tools=["manage_tags"],
                )
            try:
                return await create_tag_helper(name=name)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"name": name},
                    tool_name="manage_tags",
                    context=f"Creating tag '{name}'",
                )

        elif operation == "update":
            if not tag_id:
                return format_error_response(
                    error_msg=(
                        "tag_id is required for operation='update'. "
                        "Use operation='list' to find tag IDs."
                    ),
                    error_code="MISSING_TAG_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide tag_id parameter (e.g., tag_id=123)",
                        "Use operation='list' to find available tag IDs",
                    ],
                    related_tools=["manage_tags"],
                )
            if not new_name:
                return format_error_response(
                    error_msg=(
                        "new_name is required for operation='update'. "
                        "Provide the new name for the tag."
                    ),
                    error_code="MISSING_NEW_NAME",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide new_name parameter (e.g., new_name='detective fiction')",
                        "Tag names are automatically normalized",
                    ],
                    related_tools=["manage_tags"],
                )
            try:
                return await update_tag_helper(tag_id=tag_id, name=new_name)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"tag_id": tag_id, "new_name": new_name},
                    tool_name="manage_tags",
                    context=f"Updating tag {tag_id} to '{new_name}'",
                )

        elif operation == "delete":
            if not tag_id:
                return format_error_response(
                    error_msg=(
                        "tag_id is required for operation='delete'. "
                        "Use operation='list' to find tag IDs."
                    ),
                    error_code="MISSING_TAG_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide tag_id parameter (e.g., tag_id=123)",
                        "Use operation='list' to find available tag IDs",
                        "Warning: Deletion removes tag from all books",
                    ],
                    related_tools=["manage_tags"],
                )
            try:
                return await delete_tag_helper(tag_id=tag_id, force=force)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"tag_id": tag_id, "force": force},
                    tool_name="manage_tags",
                    context=f"Deleting tag {tag_id}",
                )

        elif operation == "find_duplicates":
            try:
                return await find_duplicate_tags_helper(similarity_threshold=similarity_threshold)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"similarity_threshold": similarity_threshold},
                    tool_name="manage_tags",
                    context="Finding duplicate tags",
                )

        elif operation == "merge":
            if not source_tag_ids:
                return format_error_response(
                    error_msg=(
                        "source_tag_ids is required for operation='merge'. "
                        "Provide a list of tag IDs to merge from."
                    ),
                    error_code="MISSING_SOURCE_TAG_IDS",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide source_tag_ids parameter (e.g., source_tag_ids=[2, 3])",
                        "These tags will be merged into target_tag_id and then deleted",
                    ],
                    related_tools=["manage_tags"],
                )
            if not target_tag_id:
                return format_error_response(
                    error_msg=(
                        "target_tag_id is required for operation='merge'. "
                        "Provide the tag ID to merge into."
                    ),
                    error_code="MISSING_TARGET_TAG_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide target_tag_id parameter (e.g., target_tag_id=1)",
                        "All source tags will be merged into this target tag",
                    ],
                    related_tools=["manage_tags"],
                )
            try:
                return await merge_tags_helper(
                    source_tag_ids=source_tag_ids, target_tag_id=target_tag_id
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"source_tag_ids": source_tag_ids, "target_tag_id": target_tag_id},
                    tool_name="manage_tags",
                    context=f"Merging tags {source_tag_ids} into {target_tag_id}",
                )

        elif operation == "get_unused":
            try:
                return await get_unused_tags_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_tags",
                    context="Getting unused tags",
                )

        elif operation == "delete_unused":
            try:
                return await delete_unused_tags_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_tags",
                    context="Deleting unused tags",
                )

        elif operation == "statistics":
            try:
                return await get_tag_statistics_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_tags",
                    context="Getting tag statistics",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'list', 'get', 'create', 'update', 'delete', 'find_duplicates', "
                    "'merge', 'get_unused', 'delete_unused', 'statistics'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='list' to list tags",
                    "Use operation='get' to get tag details",
                    "Use operation='create' to create a new tag",
                    "Use operation='update' to rename a tag",
                    "Use operation='delete' to delete a tag",
                    "Use operation='find_duplicates' to find duplicate tags",
                    "Use operation='merge' to merge tags",
                    "Use operation='get_unused' to get unused tags",
                    "Use operation='delete_unused' to delete unused tags",
                    "Use operation='statistics' to get tag statistics",
                ],
                related_tools=["manage_tags"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "tag_id": tag_id,
                "tag_name": tag_name,
                "name": name,
            },
            tool_name="manage_tags",
            context="Tag management operation",
        )
