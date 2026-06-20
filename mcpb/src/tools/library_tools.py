"""
Library management tools for CalibreMCP.

Provides functionality to manage Calibre libraries including CRUD operations,
statistics, and search capabilities through the FastMCP interface.
"""

from enum import Enum
from typing import Any

try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool

from ..db.database import Database
from ..models.library import LibraryCreate
from ..services.base_service import NotFoundError, ValidationError
from ..services.library_service import library_service as lib_service


class LibrarySortField(str, Enum):
    """Available fields to sort libraries by."""

    NAME = "name"
    BOOK_COUNT = "book_count"
    AUTHOR_COUNT = "author_count"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class SortOrder(str, Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class LibraryTools(MCPTool):
    """MCP Tool for managing Calibre libraries."""

    name = "library"
    description = "Manage Calibre libraries with CRUD operations and statistics"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = Database()

    async def _run(self, action: str, **kwargs) -> dict[str, Any]:
        """Route to the appropriate handler based on action."""
        handler = getattr(self, f"handle_{action}", None)
        if not handler:
            return {"error": f"Unknown library action: {action}", "success": False}

        try:
            return await handler(**kwargs)
        except NotFoundError as e:
            return {"error": str(e), "code": "not_found", "success": False}
        except ValidationError as e:
            return {"error": str(e), "code": "validation_error", "success": False}
        except Exception as e:
            return {
                "error": f"Internal server error: {str(e)}",
                "code": "internal_error",
                "success": False,
            }

    async def handle_list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        is_active: bool | None = None,
        sort_by: LibrarySortField = LibrarySortField.NAME,
        sort_order: SortOrder = SortOrder.ASC,
    ) -> dict[str, Any]:
        """
        List libraries with pagination, filtering, and sorting.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term to filter libraries
            is_active: Filter by active status
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Dictionary with paginated list of libraries and metadata
        """
        return lib_service.get_all(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            sort_by=sort_by.value,
            sort_order=sort_order.value,
        )

    async def handle_get(self, library_id: int) -> dict[str, Any]:
        """
        Get a library by ID.

        Args:
            library_id: ID of the library to retrieve

        Returns:
            Library details
        """
        return lib_service.get_by_id(library_id)

    async def handle_create(self, library: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new library.

        Args:
            library: Library data including name and path

        Returns:
            Created library details
        """
        # Validate input using Pydantic model
        library_data = LibraryCreate(**library)
        return lib_service.create(library_data)

    async def handle_update(self, library_id: int, updates: dict[str, Any]) -> dict[str, Any]:
        """
        Update an existing library.

        Args:
            library_id: ID of the library to update
            updates: Dictionary of fields to update

        Returns:
            Updated library details
        """
        return lib_service.update(library_id, updates)

    async def handle_delete(self, library_id: int) -> dict[str, Any]:
        """
        Delete a library.

        Args:
            library_id: ID of the library to delete

        Returns:
            Success status
        """
        success = lib_service.delete(library_id)
        return {"success": success, "message": "Library deleted successfully"}

    async def handle_stats(self, library_id: int | None = None) -> dict[str, Any]:
        """
        Get statistics for a library or all libraries.

        Args:
            library_id: Optional ID of a specific library

        Returns:
            Library statistics
        """
        return lib_service.get_library_stats(library_id=library_id)

    async def handle_search(
        self, library_id: int, query: str, limit: int = 50, offset: int = 0
    ) -> dict[str, Any]:
        """
        Search within a library.

        Args:
            library_id: ID of the library to search in
            query: Search query
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Search results with metadata
        """
        return lib_service.search_across_library(
            library_id=library_id, query=query, limit=limit, offset=offset
        )


# Create an instance of the LibraryTools for MCP
library_tools = LibraryTools()

# Register tools for MCP
tools = [library_tools]
