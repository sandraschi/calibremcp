"""
Smart Collections portmanteau tool for CalibreMCP.

Migrated from SmartCollectionsTool (MCPTool) to FastMCP 2.13+ @mcp.tool() pattern.
Consolidates all smart collection operations into a single portmanteau tool.
"""

from datetime import datetime
from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error
from .smart_collections import (
    CollectionRule,
    SmartCollection,
    SmartCollectionsTool,  # Keep for backwards compatibility
)

logger = get_logger("calibremcp.tools.smart_collections")

# Global instance for state (will be migrated to persistent storage)
_collections_storage: dict[str, SmartCollection] = {}


@mcp.tool()
async def manage_smart_collections(
    operation: str,
    collection_id: str | None = None,
    collection_data: dict[str, Any] | None = None,
    updates: dict[str, Any] | None = None,
    library_path: str | None = None,
    limit: int = 100,
    offset: int = 0,
    # Specialized collection creation parameters
    name: str
    | None = None,  # For create_series, create_recently_added, create_unread, create_ai_recommended
    series_name: str | None = None,  # For create_series
    days: int | None = None,  # For create_recently_added
) -> dict[str, Any]:
    """
    Manage smart collections with multiple operations in a single unified interface.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 10 separate tools (one per operation), this tool consolidates related
    smart collection operations into a single interface. This design:
    - Prevents tool explosion (10 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with collection management tasks
    - Enables consistent collection interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    Smart collections automatically filter books based on rules (e.g., "all books
    with tag 'scifi' and rating >= 4"). Collections are dynamically updated as
    books are added or modified.

    SUPPORTED OPERATIONS:
    - create: Create a new smart collection with rules
    - create_series: Create a collection for all books in a specific series
    - create_recently_added: Create a collection for books added recently
    - create_unread: Create a collection for unread books
    - create_ai_recommended: Create a collection with AI-recommended books
    - get: Retrieve a smart collection by ID
    - update: Update a smart collection's rules or metadata
    - delete: Delete a smart collection
    - list: List all smart collections
    - query: Query books that match a collection's rules

    OPERATIONS DETAIL:

    create: Create a new smart collection
    - Creates a collection with custom rules for filtering books
    - Parameters: collection_data (required) with name and rules
    - Returns: Created collection with ID

    create_series: Create collection for a series
    - Automatically creates collection for all books in a specific series
    - Parameters: name (required), series_name (required)
    - Returns: Created collection

    create_recently_added: Create collection for recently added books
    - Creates collection for books added within specified days
    - Parameters: name (optional), days (optional, default: 30)
    - Returns: Created collection

    create_unread: Create collection for unread books
    - Creates collection for all unread books
    - Parameters: name (optional)
    - Returns: Created collection

    create_ai_recommended: Create collection with AI recommendations
    - Creates collection with AI-recommended books
    - Parameters: name (optional)
    - Returns: Created collection

    get: Retrieve collection by ID
    - Gets collection details including rules and metadata
    - Parameters: collection_id (required)
    - Returns: Collection data

    update: Update collection
    - Updates collection rules, name, or metadata
    - Parameters: collection_id (required), updates (required)
    - Returns: Updated collection

    delete: Delete collection
    - Removes collection from system
    - Parameters: collection_id (required)
    - Returns: Deletion confirmation

    list: List all collections
    - Returns all smart collections in the system
    - No parameters required
    - Returns: List of collections

    query: Query books matching collection rules
    - Returns books that match a collection's rules
    - Parameters: collection_id (required), limit (optional), offset (optional)
    - Returns: Paginated list of matching books

    Prerequisites:
        - For 'create': Provide collection_data with name and rules
        - For 'get', 'update', 'delete', 'query': Collection must exist (collection_id required)
        - For 'query': Library must be accessible

    Parameters:
        operation: The operation to perform. Must be one of: "create", "create_series", "create_recently_added", "create_unread", "create_ai_recommended", "get", "update", "delete", "list", "query"
            - "create": Create a new collection. Requires `collection_data` parameter.
            - "create_series": Create collection for a series. Requires `name` and `series_name` parameters.
            - "create_recently_added": Create collection for recently added books. Optional `name` and `days` parameters.
            - "create_unread": Create collection for unread books. Optional `name` parameter.
            - "create_ai_recommended": Create collection with AI recommendations. Optional `name` parameter.
            - "get": Get collection by ID. Requires `collection_id` parameter.
            - "update": Update collection. Requires `collection_id` and `updates` parameters.
            - "delete": Delete collection. Requires `collection_id` parameter.
            - "list": List all collections. No additional parameters required.
            - "query": Query books matching collection rules. Requires `collection_id` parameter.

        collection_id: ID of the collection (required for 'get', 'update', 'delete', 'query')
            - Use operation="list" to see all collection IDs
            - Example: "col_1" or "my-favorite-books"

        collection_data: Collection data for creation (required for 'create')
            - Must include "name": str - Collection name
            - Must include "rules": List[Dict] - Collection rules
            - Optional: "match_all": bool - Match all rules (AND) or any rule (OR), default: True
            - Example: {"name": "High-Rated SciFi", "rules": [{"field": "tags", "operator": "contains", "value": "scifi"}, {"field": "rating", "operator": ">=", "value": 4}], "match_all": True}

        name: Collection name (for specialized create operations)
            - Required for 'create_series'
            - Optional for 'create_recently_added', 'create_unread', 'create_ai_recommended' (has defaults)

        series_name: Series name for 'create_series' operation (required for 'create_series')
            - Example: "Sherlock Holmes"

        days: Number of days for 'create_recently_added' (optional, default: 30)
            - Books added within this many days will be included

        updates: Updates to apply (required for 'update')
            - Can update: name, description, rules, match_all
            - Example: {"name": "Updated Name", "rules": [...]}

        library_path: Path to library (optional, for 'query' operation)
            - Auto-detected if not provided

        limit: Maximum results to return (for 'query', default: 100)

        offset: Results offset for pagination (for 'query', default: 0)

    Returns:
        Dictionary containing operation-specific results:

        For operation="create":
            {
                "success": bool - Whether creation succeeded
                "collection": Dict - Created collection data with ID
            }

        For operation="get":
            {
                "success": bool - Whether collection was found
                "collection": Dict - Collection data
            }

        For operation="update":
            {
                "success": bool - Whether update succeeded
                "collection": Dict - Updated collection data
            }

        For operation="delete":
            {
                "success": bool - Whether deletion succeeded
            }

        For operation="list":
            {
                "success": bool - Always True
                "collections": List[Dict] - List of all collections
            }

        For operation="query":
            {
                "success": bool - Whether query succeeded
                "collection_id": str - Collection ID queried
                "total_matches": int - Total books matching rules
                "books": List[Dict] - Matching books (paginated)
                "offset": int - Results offset
                "limit": int - Results limit
            }

    Usage:
        # Create a smart collection
        result = await manage_smart_collections(
            operation="create",
            collection_data={
                "name": "High-Rated SciFi",
                "rules": [
                    {"field": "tags", "operator": "contains", "value": "scifi"},
                    {"field": "rating", "operator": ">=", "value": 4}
                ],
                "match_all": True
            }
        )
        collection_id = result["collection"]["id"]

        # List all collections
        result = await manage_smart_collections(operation="list")
        for col in result["collections"]:
            print(f"{col['name']}: {col['id']}")

        # Query books in a collection
        result = await manage_smart_collections(
            operation="query",
            collection_id="col_1",
            limit=50
        )
        print(f"Found {result['total_matches']} matching books")

    Examples:
        # Create collection for unread books with specific tags
        result = await manage_smart_collections(
            operation="create",
            collection_data={
                "name": "Unread Programming Books",
                "description": "All unread books tagged 'programming'",
                "rules": [
                    {"field": "status", "operator": "==", "value": "unread"},
                    {"field": "tags", "operator": "contains", "value": "programming"}
                ],
                "match_all": True
            }
        )

        # Update collection rules
        result = await manage_smart_collections(
            operation="update",
            collection_id="col_1",
            updates={
                "rules": [
                    {"field": "tags", "operator": "contains", "value": "python"}
                ]
            }
        )

        # Query collection with pagination
        page1 = await manage_smart_collections(
            operation="query",
            collection_id="col_1",
            limit=20,
            offset=0
        )
        page2 = await manage_smart_collections(
            operation="query",
            collection_id="col_1",
            limit=20,
            offset=20
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "create", "get", "update", "delete", "list", "query"
        - Missing collection_id: Provide collection_id for get/update/delete/query operations
        - Missing collection_data: Provide collection_data for create operation
        - Collection not found: Use operation="list" to see all available collection IDs
        - Invalid rule: Rules must have field, operator, and value fields

    See Also:
        - SmartCollectionsTool: Legacy tool (deprecated in favor of this portmanteau tool)
    """
    global _collections_storage

    try:
        if operation == "create":
            if not collection_data:
                return format_error_response(
                    error_msg="collection_data is required for operation='create'.",
                    error_code="MISSING_COLLECTION_DATA",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide collection_data with 'name' and 'rules' fields",
                        "Example: collection_data={'name': 'My Collection', 'rules': [...]}",
                    ],
                    related_tools=["manage_smart_collections"],
                )
            return await _handle_create(collection_data)

        elif operation == "create_series":
            if not name or not series_name:
                return format_error_response(
                    error_msg="name and series_name are required for operation='create_series'.",
                    error_code="MISSING_PARAMETERS",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide name and series_name parameters",
                        "Example: operation='create_series', name='Sherlock Holmes Collection', series_name='Sherlock Holmes'",
                    ],
                    related_tools=["manage_smart_collections"],
                )
            try:
                legacy_tool = SmartCollectionsTool()
                return await legacy_tool.collection_create_series(
                    name=name, series_name=series_name, library_path=library_path
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"name": name, "series_name": series_name},
                    tool_name="manage_smart_collections",
                    context=f"Creating series collection '{name}' for series '{series_name}'",
                )

        elif operation == "create_recently_added":
            if not name:
                name = "Recently Added"
            if days is None:
                days = 30
            try:
                legacy_tool = SmartCollectionsTool()
                return await legacy_tool.collection_create_recently_added(
                    name=name, days=days, library_path=library_path
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"name": name, "days": days},
                    tool_name="manage_smart_collections",
                    context=f"Creating recently added collection '{name}'",
                )

        elif operation == "create_unread":
            if not name:
                name = "Unread"
            try:
                legacy_tool = SmartCollectionsTool()
                return await legacy_tool.collection_create_unread(
                    name=name, library_path=library_path
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"name": name},
                    tool_name="manage_smart_collections",
                    context=f"Creating unread collection '{name}'",
                )

        elif operation == "create_ai_recommended":
            if not name:
                name = "AI Recommendations"
            try:
                legacy_tool = SmartCollectionsTool()
                return await legacy_tool.collection_create_ai_recommended(
                    name=name, library_path=library_path
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"name": name},
                    tool_name="manage_smart_collections",
                    context=f"Creating AI recommended collection '{name}'",
                )

        elif operation == "get":
            if not collection_id:
                return format_error_response(
                    error_msg="collection_id is required for operation='get'.",
                    error_code="MISSING_COLLECTION_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Use operation='list' to see all available collection IDs"],
                    related_tools=["manage_smart_collections"],
                )
            return await _handle_get(collection_id)

        elif operation == "update":
            if not collection_id:
                return format_error_response(
                    error_msg="collection_id is required for operation='update'.",
                    error_code="MISSING_COLLECTION_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Use operation='list' to see all available collection IDs"],
                    related_tools=["manage_smart_collections"],
                )
            if not updates:
                return format_error_response(
                    error_msg="updates is required for operation='update'.",
                    error_code="MISSING_UPDATES",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide updates dictionary with fields to update"],
                    related_tools=["manage_smart_collections"],
                )
            return await _handle_update(collection_id, updates)

        elif operation == "delete":
            if not collection_id:
                return format_error_response(
                    error_msg="collection_id is required for operation='delete'.",
                    error_code="MISSING_COLLECTION_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Use operation='list' to see all available collection IDs"],
                    related_tools=["manage_smart_collections"],
                )
            return await _handle_delete(collection_id)

        elif operation == "list":
            return await _handle_list()

        elif operation == "query":
            if not collection_id:
                return format_error_response(
                    error_msg="collection_id is required for operation='query'.",
                    error_code="MISSING_COLLECTION_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Use operation='list' to see all available collection IDs"],
                    related_tools=["manage_smart_collections"],
                )
            return await _handle_query(collection_id, library_path, limit, offset)

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'create', 'create_series', 'create_recently_added', 'create_unread', "
                    "'create_ai_recommended', 'get', 'update', 'delete', 'list', 'query'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='create' to create a new smart collection with custom rules",
                    "Use operation='create_series' to create a collection for a series",
                    "Use operation='create_recently_added' to create a collection for recently added books",
                    "Use operation='create_unread' to create a collection for unread books",
                    "Use operation='create_ai_recommended' to create a collection with AI recommendations",
                    "Use operation='get' to retrieve a collection",
                    "Use operation='update' to update collection rules",
                    "Use operation='delete' to delete a collection",
                    "Use operation='list' to list all collections",
                    "Use operation='query' to query books matching collection rules",
                ],
                related_tools=["manage_smart_collections"],
            )
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "collection_id": collection_id,
                "collection_data": collection_data,
            },
            tool_name="manage_smart_collections",
            context="Smart collection management operation",
        )


async def _handle_create(collection_data: dict[str, Any]) -> dict[str, Any]:
    """Handle create collection operation."""
    try:
        rules = []
        for rule in collection_data.get("rules", []):
            if not isinstance(rule, CollectionRule):
                rule = CollectionRule(**rule)
            rules.append(rule)

        collection_data["rules"] = rules
        collection = SmartCollection(**collection_data)

        if not collection.id:
            global _collections_storage
            collection.id = f"col_{len(_collections_storage) + 1}"

        _collections_storage[collection.id] = collection
        return {"success": True, "collection": collection.to_dict()}
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="create",
            parameters={"collection_data": collection_data},
            tool_name="manage_smart_collections",
            context="Creating smart collection",
        )


async def _handle_get(collection_id: str) -> dict[str, Any]:
    """Handle get collection operation."""
    try:
        global _collections_storage
        if collection_id not in _collections_storage:
            return format_error_response(
                error_msg=f"Collection {collection_id} not found",
                error_code="COLLECTION_NOT_FOUND",
                error_type="KeyError",
                operation="get",
                suggestions=["Use operation='list' to see all available collections"],
                related_tools=["manage_smart_collections"],
            )
        return {"success": True, "collection": _collections_storage[collection_id].to_dict()}
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="get",
            parameters={"collection_id": collection_id},
            tool_name="manage_smart_collections",
            context=f"Getting collection {collection_id}",
        )


async def _handle_update(collection_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """Handle update collection operation."""
    try:
        global _collections_storage
        if collection_id not in _collections_storage:
            return format_error_response(
                error_msg=f"Collection {collection_id} not found",
                error_code="COLLECTION_NOT_FOUND",
                error_type="KeyError",
                operation="update",
                suggestions=["Use operation='list' to see all available collections"],
                related_tools=["manage_smart_collections"],
            )

        collection = _collections_storage[collection_id]

        for field, value in updates.items():
            if hasattr(collection, field) and field not in ["id", "created_at"]:
                if field == "rules":
                    rules = []
                    for rule in value:
                        if not isinstance(rule, CollectionRule):
                            rule = CollectionRule(**rule)
                        rules.append(rule)
                    setattr(collection, field, rules)
                else:
                    setattr(collection, field, value)

        collection.updated_at = datetime.utcnow()
        return {"success": True, "collection": collection.to_dict()}
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="update",
            parameters={"collection_id": collection_id, "updates": updates},
            tool_name="manage_smart_collections",
            context=f"Updating collection {collection_id}",
        )


async def _handle_delete(collection_id: str) -> dict[str, Any]:
    """Handle delete collection operation."""
    try:
        global _collections_storage
        if collection_id not in _collections_storage:
            return format_error_response(
                error_msg=f"Collection {collection_id} not found",
                error_code="COLLECTION_NOT_FOUND",
                error_type="KeyError",
                operation="delete",
                suggestions=["Use operation='list' to see all available collections"],
                related_tools=["manage_smart_collections"],
            )

        del _collections_storage[collection_id]
        return {"success": True}
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="delete",
            parameters={"collection_id": collection_id},
            tool_name="manage_smart_collections",
            context=f"Deleting collection {collection_id}",
        )


async def _handle_list() -> dict[str, Any]:
    """Handle list collections operation."""
    try:
        global _collections_storage
        return {
            "success": True,
            "collections": [col.to_dict() for col in _collections_storage.values()],
        }
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="list",
            parameters={},
            tool_name="manage_smart_collections",
            context="Listing smart collections",
        )


async def _handle_query(
    collection_id: str, library_path: str | None, limit: int, offset: int
) -> dict[str, Any]:
    """Handle query collection operation."""
    try:
        global _collections_storage
        if collection_id not in _collections_storage:
            return format_error_response(
                error_msg=f"Collection {collection_id} not found",
                error_code="COLLECTION_NOT_FOUND",
                error_type="KeyError",
                operation="query",
                suggestions=["Use operation='list' to see all available collections"],
                related_tools=["manage_smart_collections"],
            )

        # Use legacy tool's query logic for now
        # TODO: Migrate to use book_service directly
        legacy_tool = SmartCollectionsTool()
        result = await legacy_tool.collection_query(
            collection_id=collection_id, library_path=library_path, limit=limit, offset=offset
        )
        return result
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="query",
            parameters={"collection_id": collection_id, "limit": limit, "offset": offset},
            tool_name="manage_smart_collections",
            context=f"Querying collection {collection_id}",
        )
