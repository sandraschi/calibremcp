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
    Comprehensive tag management tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 10 separate tools (one per operation), this tool consolidates related
    tag operations into a single interface. This design:
    - Prevents tool explosion (10 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with tag management tasks
    - Enables consistent tag interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - list: List tags with filtering, sorting, and pagination
    - get: Get tag details by ID or name
    - create: Create new tag
    - update: Update (rename) existing tag
    - delete: Delete tag (removes from all books)
    - find_duplicates: Find duplicate or similar tags for weeding
    - merge: Merge multiple tags into a target tag
    - get_unused: Get all tags not assigned to any books
    - delete_unused: Delete all unused tags
    - statistics: Get comprehensive tag statistics

    OPERATIONS DETAIL:

    list: List tags with filtering and pagination
    - Supports searching tags by name (case-insensitive partial match)
    - Filter by usage (book count) with min_book_count/max_book_count
    - Find unused tags with unused_only=True
    - Sort by name or book_count in ascending/descending order
    - Pagination with limit and offset
    - Parameters: search, limit, offset, sort_by, sort_order, unused_only, min_book_count, max_book_count

    get: Get tag details by ID or name
    - Retrieve tag information including book count
    - Can search by numeric tag_id or string tag_name
    - Returns tag details or error if not found
    - Parameters: tag_id OR tag_name (one required)

    create: Create new tag
    - Tag names are automatically normalized (trimmed and title-cased)
    - Returns error if tag with same name already exists
    - Parameters: name (required)

    update: Update (rename) existing tag
    - Renames tag and updates all books with the old tag
    - Tag name is automatically normalized
    - Parameters: tag_id (required), new_name (required)

    delete: Delete tag
    - Removes tag from all books that have it
    - Deletes the tag itself
    - Parameters: tag_id (required), force (optional, default: False)

    find_duplicates: Find duplicate or similar tags
    - Uses string similarity matching to find likely duplicates
    - Example: "sci-fi" and "scifi", "mystery" and "mysteries"
    - Returns groups of similar tags with similarity scores
    - Parameters: similarity_threshold (0.0-1.0, default: 0.8)

    merge: Merge multiple tags into target tag
    - Consolidates duplicate tags found by find_duplicates
    - All books with source tags are retagged with target tag
    - Source tags are deleted after merging
    - Parameters: source_tag_ids (required, list), target_tag_id (required)

    get_unused: Get unused tags
    - Returns all tags not assigned to any books
    - Good candidates for deletion during tag weeding
    - No parameters required

    delete_unused: Delete all unused tags
    - Safe cleanup operation that removes orphaned tags
    - Use after reviewing with get_unused
    - No parameters required

    statistics: Get tag statistics
    - Comprehensive statistics about tag usage
    - Includes total tags, unused count, top tags, average books per tag
    - Useful for understanding tag structure and planning weeding
    - No parameters required

    Prerequisites:
        - Library must be configured (use manage_libraries(operation='switch'))
        - For operations requiring tag_id: Tag must exist (use operation='list' to find IDs)
        - For merge: Both source and target tags must exist

    Parameters:
        operation: The operation to perform. Must be one of:
            "list", "get", "create", "update", "delete", "find_duplicates",
            "merge", "get_unused", "delete_unused", "statistics"

        # List operation parameters
        search: Search term to filter tags by name (case-insensitive partial match)
        limit: Maximum number of results (1-1000, default: 100)
        offset: Results offset for pagination (default: 0)
        sort_by: Field to sort by - "name" or "book_count" (default: "name")
        sort_order: Sort order - "asc" or "desc" (default: "asc")
        unused_only: If True, only return tags with 0 books (default: False)
        min_book_count: Minimum number of books using this tag (optional)
        max_book_count: Maximum number of books using this tag (optional)

        # Get operation parameters
        tag_id: Tag ID (required for 'get' if tag_name not provided)
        tag_name: Tag name (required for 'get' if tag_id not provided)

        # Create operation parameters
        name: Tag name to create (required for 'create')

        # Update operation parameters
        tag_id: Tag ID to update (required for 'update')
        new_name: New name for the tag (required for 'update')

        # Delete operation parameters
        tag_id: Tag ID to delete (required for 'delete')
        force: Skip dependency checks (default: False)

        # Find duplicates operation parameters
        similarity_threshold: Similarity score threshold 0.0-1.0 (default: 0.8)
            Higher values = more strict (only very similar tags)
            Lower values = less strict (more potential matches)

        # Merge operation parameters
        source_tag_ids: List of tag IDs to merge from (required for 'merge')
        target_tag_id: Tag ID to merge into (required for 'merge')

    Returns:
        Dictionary containing operation-specific results:

        For operation="list":
            {
                "items": List[Dict] - Tag objects with id, name, book_count
                "total": int - Total number of matching tags
                "page": int - Current page number
                "per_page": int - Items per page
                "total_pages": int - Total number of pages
            }

        For operation="get":
            {
                "id": int - Tag ID
                "name": str - Tag name
                "book_count": int - Number of books with this tag
            }

        For operation="create":
            {
                "id": int - Created tag ID
                "name": str - Created tag name (normalized)
                "book_count": int - Always 0 for new tags
            }

        For operation="update":
            {
                "id": int - Updated tag ID
                "name": str - New tag name (normalized)
                "book_count": int - Number of books with this tag
            }

        For operation="delete":
            {
                "success": bool - Whether deletion succeeded
                "message": str - Status message
            }

        For operation="find_duplicates":
            {
                "duplicate_groups": List[Dict] - Groups of similar tags
                "total_duplicates": int - Number of duplicate groups found
                "similarity_threshold": float - Threshold used
            }

        For operation="merge":
            {
                "success": bool - Whether merge succeeded
                "target_tag": Dict - Target tag details
                "merged_tags": List[str] - Names of merged tags
                "books_affected": int - Number of books affected
            }

        For operation="get_unused":
            {
                "unused_tags": List[Dict] - Unused tag objects
                "count": int - Number of unused tags
            }

        For operation="delete_unused":
            {
                "success": bool - Whether deletion succeeded
                "deleted_count": int - Number of tags deleted
                "deleted_tags": List[str] - Names of deleted tags
            }

        For operation="statistics":
            {
                "total_tags": int - Total number of tags
                "unused_tags_count": int - Number of unused tags
                "used_tags_count": int - Number of tags in use
                "top_tags": List[Dict] - Top tags by book count
                "average_books_per_tag": float - Average books per tag
            }

    Usage:
        # List all tags
        result = await manage_tags(operation="list")

        # Search for tags containing "mystery"
        result = await manage_tags(operation="list", search="mystery")

        # Find unused tags
        result = await manage_tags(operation="get_unused")

        # Create a new tag
        result = await manage_tags(operation="create", name="locked room mystery")

        # Get tag by name
        result = await manage_tags(operation="get", tag_name="mystery")

        # Update tag name
        result = await manage_tags(operation="update", tag_id=123, new_name="detective fiction")

        # Find duplicate tags
        result = await manage_tags(operation="find_duplicates", similarity_threshold=0.8)

        # Merge duplicate tags
        result = await manage_tags(
            operation="merge",
            source_tag_ids=[2, 3],
            target_tag_id=1
        )

        # Delete unused tags
        result = await manage_tags(operation="delete_unused")

        # Get tag statistics
        result = await manage_tags(operation="statistics")

    Examples:
        # List popular tags (used by 10+ books)
        popular = await manage_tags(
            operation="list",
            min_book_count=10,
            sort_by="book_count",
            sort_order="desc"
        )

        # Find rarely used tags (1-5 books)
        rare = await manage_tags(
            operation="list",
            min_book_count=1,
            max_book_count=5,
            sort_by="book_count"
        )

        # Tag weeding workflow
        # 1. Find duplicates
        duplicates = await manage_tags(operation="find_duplicates", similarity_threshold=0.8)
        # 2. Review duplicate groups
        for group in duplicates["duplicate_groups"]:
            print(f"Similar tags: {group['tags']}")
        # 3. Merge duplicates
        await manage_tags(
            operation="merge",
            source_tag_ids=[2, 3],
            target_tag_id=1
        )
        # 4. Get unused tags
        unused = await manage_tags(operation="get_unused")
        # 5. Delete unused tags
        await manage_tags(operation="delete_unused")

        # Get comprehensive statistics
        stats = await manage_tags(operation="statistics")
        print(f"Total tags: {stats['total_tags']}")
        print(f"Unused tags: {stats['unused_tags_count']}")
        print(f"Top tag: {stats['top_tags'][0]['name']}")

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of the supported operations listed above
        - Missing tag_id (get/update/delete): Provide tag_id parameter
        - Missing tag_name (get): Provide tag_name parameter if tag_id not provided
        - Missing name (create): Provide name parameter for create operation
        - Missing new_name (update): Provide new_name parameter for update operation
        - Missing source_tag_ids (merge): Provide source_tag_ids list for merge operation
        - Missing target_tag_id (merge): Provide target_tag_id for merge operation
        - Tag not found: Verify tag_id or tag_name is correct using operation='list'
        - No library configured: Use manage_libraries(operation='switch') to configure library

    See Also:
        - manage_libraries(): For library management and switching
        - query_books(): For finding books by tags
        - manage_books(): For book management operations
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
