"""
Core library operations tools for CalibreMCP.

These tools provide essential functionality for listing, searching,
and retrieving book information from Calibre libraries.
"""

import asyncio

from ...logging_config import get_logger, log_error
from ...server import (
    ConnectionTestResponse,
    LibrarySearchResponse,
    current_library,
    get_api_client,
)

logger = get_logger("calibremcp.tools.core")


# Helper function - called by query_books portmanteau tool
# NOT registered as MCP tool (no @mcp.tool() decorator)
async def list_books_helper(
    query: str | None = None, limit: int = 50, sort: str = "title"
) -> LibrarySearchResponse:
    """
    List books from the current Calibre library with optional filtering and sorting.

    Provides a paginated list of books with basic metadata. Supports text-based
    filtering and multiple sorting options for efficient browsing.

    Args:
        query: Optional text filter for title, author, or tags
        limit: Maximum number of books to return (1-200)
        sort: Sort order - title, author, rating, or date

    Returns:
        LibrarySearchResponse: List of books with metadata and pagination info
    """
    try:
        start_time = asyncio.get_event_loop().time()
        client = await get_api_client()

        # Validate limit
        limit = max(1, min(200, limit))

        # Perform search
        results = await client.search_library(query=query, limit=limit, sort=sort)

        end_time = asyncio.get_event_loop().time()
        search_time_ms = int((end_time - start_time) * 1000)

        return LibrarySearchResponse(
            results=results,
            total_found=len(results),
            query_used=query,
            search_time_ms=search_time_ms,
            library_searched=current_library,
        )

    except Exception as e:
        log_error(logger, "list_books", e)
        return LibrarySearchResponse(
            results=[],
            total_found=0,
            query_used=query,
            search_time_ms=0,
            library_searched=current_library,
        )


# get_book_details_helper removed (dead remote-API code) -
# use manage_books(operation="details", book_id=...) which reads from the local DB.


async def test_calibre_connection_helper() -> ConnectionTestResponse:
    """Helper for connection test. Use manage_libraries(operation='test_connection') or test_calibre_connection."""
    try:
        start_time = asyncio.get_event_loop().time()
        client = await get_api_client()

        # Check if using local library mode (client is None)
        if client is None:
            # Local library mode - check database connection instead
            from calibre_mcp.config import CalibreConfig
            from calibre_mcp.db.database import get_database

            config = CalibreConfig()
            db = get_database()

            # Test local database connection
            try:
                with db.session_scope() as session:
                    from calibre_mcp.db.models import Book

                    book_count = session.query(Book).count()

                end_time = asyncio.get_event_loop().time()
                response_time_ms = int((end_time - start_time) * 1000)

                return ConnectionTestResponse(
                    connected=True,
                    server_url="local://"
                    + (str(config.local_library_path) if config.local_library_path else "local"),
                    server_version="Local SQLite",
                    library_count=1,
                    total_books=book_count,
                    response_time_ms=response_time_ms,
                )
            except Exception as db_e:
                return ConnectionTestResponse(
                    connected=False,
                    server_url="local://unknown",
                    server_version=None,
                    library_count=0,
                    total_books=0,
                    response_time_ms=0,
                    error_message=f"Local database connection failed: {str(db_e)}",
                )

        # Remote server mode - test HTTP connection
        server_info = await client.test_connection()

        end_time = asyncio.get_event_loop().time()
        response_time_ms = int((end_time - start_time) * 1000)

        return ConnectionTestResponse(
            connected=True,
            server_url=str(client.config.server_url),
            server_version=server_info.get("version"),
            library_count=len(await client.list_libraries()),
            total_books=server_info.get("total_books", 0),
            response_time_ms=response_time_ms,
        )

    except Exception as e:
        log_error(logger, "test_calibre_connection", e)
        return ConnectionTestResponse(
            connected=False, server_url="unknown", response_time_ms=0, error_message=str(e)
        )
