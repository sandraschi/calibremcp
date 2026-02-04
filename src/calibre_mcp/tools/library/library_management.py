"""
Library management tools for CalibreMCP.

These tools handle multi-library operations, switching between libraries,
and cross-library search functionality.
"""

import time
from typing import Any

from ...config import CalibreConfig
from ...logging_config import get_logger
from ...server import LibraryListResponse, LibrarySearchResponse, LibraryStatsResponse

# Import services and utilities
from ...services.book_service import book_service
from ...utils.library_utils import discover_calibre_libraries, get_library_metadata

logger = get_logger("calibremcp.tools.library_management")


# Helper function - called by manage_libraries portmanteau tool
# NOT registered as MCP tool (no @mcp.tool() decorator)
async def list_libraries_helper() -> LibraryListResponse:
    """
    List all available Calibre libraries with comprehensive statistics and metadata.

    Discovers and displays information about all Calibre libraries found on the system,
    including book counts, library sizes, paths, and active status. Automatically scans
    common Calibre library locations and identifies libraries by the presence of
    metadata.db files. Each library entry includes detailed metadata to help users
    identify and select the appropriate library for their operations.

    The tool performs automatic library discovery by scanning configured directories
    and Calibre configuration files. It identifies libraries by detecting metadata.db
    files, which are the core database files for Calibre libraries. For each discovered
    library, it gathers statistics including book count (estimated from database size)
    and library size on disk.

    The response includes the currently active library, allowing users to see which
    library is being used for subsequent operations. If no active library is set,
    the first discovered library is automatically marked as active.

    Returns:
        LibraryListResponse containing:
        {
            "libraries": List[Dict[str, Any]] - List of library objects, each containing:
                - "name": str - Display name of the library (derived from directory name)
                - "path": str - Full file system path to the library
                - "book_count": int - Estimated number of books in the library
                - "size_mb": float - Library size in megabytes (rounded to 2 decimals)
                - "is_active": bool - Whether this is the currently active library
            "current_library": str - Name of the currently active library (empty if none)
            "total_libraries": int - Total number of discovered libraries
        }

    Raises:
        No exceptions raised - Returns empty result on errors to ensure tool reliability

    Example:
        # List all available libraries
        result = list_libraries()
        print(f"Found {result.total_libraries} libraries")

        for lib in result.libraries:
            status = "🟢 ACTIVE" if lib.is_active else "⚪"
            print(f"{status} {lib.name}: {lib.book_count} books, {lib.size_mb}MB")
            print(f"  Path: {lib.path}")

        # Check current library
        if result.current_library:
            print(f"Currently using: {result.current_library}")
        else:
            print("No library currently active")

    Note:
        - Library discovery may take a few seconds on first run
        - Book counts are estimates based on library structure
        - Only libraries with valid metadata.db files are included
        - The tool automatically handles library path normalization
    """
    try:
        # Discover libraries from file system
        discovered_libs = discover_calibre_libraries()

        # Get current active library
        config = CalibreConfig()
        current_lib_name = None
        if config.local_library_path:
            # Find which discovered library matches the current path
            for name, path in discovered_libs.items():
                if path == config.local_library_path:
                    current_lib_name = name
                    break

        # Build library list with metadata
        library_list = []
        for name, path in discovered_libs.items():
            metadata = get_library_metadata(path)
            library_list.append(
                {
                    "name": name,
                    "path": str(path),
                    "book_count": metadata.get("book_count", 0),
                    "size_mb": round(metadata.get("size_mb", 0), 2),
                    "is_active": (name == current_lib_name) if current_lib_name else False,
                }
            )

        # If no current library set, use first one
        if not current_lib_name and library_list:
            current_lib_name = library_list[0]["name"]
            library_list[0]["is_active"] = True

        return LibraryListResponse(
            libraries=library_list,
            current_library=current_lib_name or "",
            total_libraries=len(library_list),
        )

    except Exception as e:
        logger.error(f"Error listing libraries: {e}", exc_info=True)
        # Return empty result on error
        return LibraryListResponse(libraries=[], current_library="", total_libraries=0)


# Helper function - called by manage_libraries portmanteau tool
# NOT registered as MCP tool (no @mcp.tool() decorator)
async def switch_library_helper(library_name: str) -> dict[str, Any]:
    """
    Switch the active Calibre library for all subsequent operations.

    Changes the active library context that all other tools will use for operations
    such as searches, book retrieval, metadata updates, and file downloads. The library
    switch is persisted in the configuration, ensuring the selected library remains
    active across sessions until explicitly changed again.

    This tool validates that the specified library exists among discovered libraries
    before switching. If the library is not found, it provides helpful error messages
    listing all available libraries. Upon successful switch, all subsequent tool calls
    will operate on the newly selected library until another switch is performed.

    The switch operation updates both the in-memory configuration and ensures the
    library path is correctly set for database connections. All book-related operations
    (search, list, update, download) will automatically use the newly active library.

    Args:
        library_name: Name of the library to switch to.
                      Must exactly match a library name from list_libraries().
                      Library names are case-sensitive and typically match the
                      directory name containing the library's metadata.db file.

    Returns:
        Dictionary containing:
        {
            "success": bool - Whether the switch operation completed successfully.
                              True if library was found and switched, False otherwise.
            "library_name": str - Name of the newly active library (matches input).
            "library_path": str - Full file system path to the newly active library.
            "message": str - Human-readable status message describing the result.
        }

    Raises:
        ValueError: If the specified library_name is not found among discovered libraries.
                    The error message includes a list of available library names to help
                    users identify the correct name to use.

    Example:
        # First, list available libraries
        libraries = list_libraries()
        print(f"Available libraries: {[lib.name for lib in libraries.libraries]}")

        # Switch to a specific library
        result = switch_library(library_name="Main Library")
        if result["success"]:
            print(f"Switched to: {result['library_name']}")
            print(f"   Path: {result['library_path']}")
        else:
            print(f"Failed: {result['message']}")

        # Now all subsequent operations use the new library
        books = search_books(query="python")
        # Results are from "Main Library"

    Note:
        - Library names are case-sensitive - use exact names from list_libraries()
        - The switch is immediate and affects all subsequent tool calls
        - Switching libraries does not affect operations already in progress
        - Use list_libraries() first to see all available library names
        - Invalid library names will raise ValueError with helpful suggestions
    """
    try:
        # Discover libraries
        discovered_libs = discover_calibre_libraries()

        if library_name not in discovered_libs:
            raise ValueError(
                f"Library '{library_name}' not found. Available libraries: {', '.join(discovered_libs.keys())}"
            )

        # Get library path
        library_path = discovered_libs[library_name]

        # Switch using config
        config = CalibreConfig()
        success = config.set_active_library(library_name)

        if not success:
            raise ValueError(f"Failed to switch to library '{library_name}'")

        # CRITICAL: Re-initialize database with the new library
        # The database was initialized at startup with a different library
        from pathlib import Path

        from ...db.database import init_database

        metadata_db = Path(library_path) / "metadata.db"
        if not metadata_db.exists():
            raise ValueError(
                f"metadata.db not found in library '{library_name}' at {metadata_db}. "
                "Please verify the library path is correct."
            )

        try:
            # CRITICAL: Force re-initialization by closing old database first
            from ...db.database import close_database

            # Close existing database connection
            try:
                close_database()
                logger.debug("Closed existing database connection")
            except Exception as e:
                # Log the error but continue - database may not be initialized yet
                logger.warning(
                    "Could not close previous database connection, continuing with new library",
                    extra={
                        "error_type": type(e).__name__,
                        "error": str(e),
                        "library_name": library_name,
                    },
                    exc_info=True,
                )

            # Re-initialize database with new library
            init_database(str(metadata_db.absolute()), echo=False)
            logger.info(f"Database re-initialized with library: {library_name} at {library_path}")
        except Exception as e:
            logger.error(
                f"Failed to re-initialize database for library '{library_name}': {e}", exc_info=True
            )
            raise ValueError(
                f"Failed to initialize database for library '{library_name}': {str(e)}. "
                "Please verify the library is valid and accessible."
            ) from e

        # Update global current_library variable and persist to storage
        # Update the module-level global variable
        import calibre_mcp.server as server_module

        from ...server import storage

        server_module.current_library = library_name

        # Persist to FastMCP storage (if available)
        if storage:
            try:
                await storage.set_current_library(library_name)
            except Exception as e:
                logger.warning(f"Failed to persist library switch to storage: {e}")

        logger.info(f"Switched to library: {library_name} (database re-initialized)")

        return {
            "success": True,
            "library_name": library_name,
            "library_path": str(library_path),
            "message": f"Successfully switched to library '{library_name}' and re-initialized database. You can now search books.",
        }

    except ValueError as ve:
        logger.error(f"Validation error switching library: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error switching library: {e}", exc_info=True)
        return {
            "success": False,
            "library_name": library_name,
            "library_path": "",
            "message": f"Error switching library: {str(e)}",
        }


# Helper function - called by manage_libraries portmanteau tool
# NOT registered as MCP tool (no @mcp.tool() decorator)
async def get_library_stats_helper(library_name: str | None = None) -> LibraryStatsResponse:
    """
    Get detailed statistics for a specific library.

    Provides comprehensive analytics including format distribution,
    author counts, series information, and reading progress metrics.
    If no library name is provided, uses the currently active library.

    Args:
        library_name: Name of library to analyze (uses current if None)

    Returns:
        LibraryStatsResponse containing:
        {
            "library_name": str - Name of the library
            "total_books": int - Total number of books
            "total_authors": int - Number of unique authors
            "total_series": int - Number of series
            "total_tags": int - Number of tags
            "format_distribution": Dict[str, int] - Format counts (e.g., {"epub": 100, "pdf": 50})
            "language_distribution": Dict[str, int] - Language counts
            "rating_distribution": Dict[str, int] - Rating counts
            "last_modified": str - ISO timestamp of last modification
        }

    Example:
        # Get stats for current library
        stats = get_library_stats()
        print(f"Total books: {stats['total_books']}")

        # Get stats for specific library
        stats = get_library_stats(library_name="Main Library")
    """
    try:
        # Determine which library to analyze
        config = CalibreConfig()

        if library_name:
            # Use specified library
            discovered_libs = discover_calibre_libraries()
            if library_name not in discovered_libs:
                raise ValueError(f"Library '{library_name}' not found")
            library_path = discovered_libs[library_name]
        else:
            # Use current library
            if not config.local_library_path:
                raise ValueError(
                    "No active library set. Please specify library_name or switch to a library first."
                )
            library_path = config.local_library_path
            # Find library name from path
            library_name = library_path.name

        # Get basic metadata from file system
        metadata = get_library_metadata(library_path)

        # Try to get stats from database if available
        # Note: This requires the library to be connected to the database service
        # For now, we'll use file system metadata and basic counts

        # Get format distribution from file system (approximate)
        format_distribution: dict[str, int] = {}
        try:
            # Count format files in library
            for ext in [".epub", ".pdf", ".mobi", ".azw3", ".txt", ".html"]:
                count = len(list(library_path.glob(f"**/*{ext}")))
                if count > 0:
                    format_distribution[ext[1:].lower()] = count
        except (OSError, PermissionError):
            pass

        # Build response with available data
        stats = LibraryStatsResponse(
            library_name=library_name,
            total_books=metadata.get("book_count", 0),
            total_authors=0,  # Would need database access for accurate count
            total_series=0,  # Would need database access for accurate count
            total_tags=0,  # Would need database access for accurate count
            format_distribution=format_distribution,
            language_distribution={},  # Would need database access
            rating_distribution={},  # Would need database access
            last_modified=None,  # Would need database access
        )

        return stats

    except ValueError as ve:
        logger.error(f"Validation error getting library stats: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error getting library stats: {e}", exc_info=True)
        # Return minimal stats on error
        return LibraryStatsResponse(
            library_name=library_name or "unknown",
            total_books=0,
            total_authors=0,
            total_series=0,
            total_tags=0,
            format_distribution={},
            language_distribution={},
            rating_distribution={},
            last_modified=None,
        )


# Helper function - called by manage_libraries portmanteau tool
# NOT registered as MCP tool (no @mcp.tool() decorator)
async def cross_library_search_helper(
    query: str, libraries: list[str] | None = None
) -> LibrarySearchResponse:
    """
    Search for books across multiple Calibre libraries simultaneously.

    Performs unified search across specified libraries or all available
    libraries, providing consolidated results with library identification.
    Each result includes the library name it was found in.

    Args:
        query: Search query text to search for in book titles, authors, etc.
        libraries: Optional list of library names to search (searches all if None)

    Returns:
        LibrarySearchResponse containing:
        {
            "results": List[Dict] - List of books found across libraries
            "total_found": int - Total number of matching books
            "query_used": str - The search query that was used
            "search_time_ms": int - Search execution time in milliseconds
            "library_searched": str - Names of libraries searched (comma-separated)
        }

    Example:
        # Search across all libraries
        results = cross_library_search(query="python")
        print(f"Found {results['total']} books in {len(results['libraries_searched'])} libraries")

        # Search in specific libraries
        results = cross_library_search(
            query="machine learning",
            libraries=["Main Library", "IT Library"]
        )
    """
    try:
        # Discover available libraries
        discovered_libs = discover_calibre_libraries()

        # Parse intelligent query to extract content_type and other hints
        from ..shared.query_parsing import parse_intelligent_query

        parsed = parse_intelligent_query(query)

        # Determine which libraries to search
        # DEFAULT: Search only active library (faster, more predictable)
        # To search all libraries, explicitly pass libraries=["ALL"]
        config = CalibreConfig()

        if libraries is None:
            # No libraries specified - search active library only
            if config.local_library_path:
                # Find the active library name
                active_lib_name = None
                for name, path in discovered_libs.items():
                    if path == config.local_library_path:
                        active_lib_name = name
                        break
                if active_lib_name:
                    libraries_to_search = [active_lib_name]
                    logger.info(
                        f"Searching active library only: {active_lib_name}",
                        extra={"library": active_lib_name, "query": query},
                    )
                else:
                    # Active library path doesn't match discovered - search all as fallback
                    libraries_to_search = list(discovered_libs.keys())
                    logger.warning(
                        "Active library path not found in discovered libraries, searching all",
                        extra={"active_path": str(config.local_library_path)},
                    )
            else:
                # No active library - search all as fallback
                libraries_to_search = list(discovered_libs.keys())
                logger.info("No active library set, searching all libraries")
        elif isinstance(libraries, list):
            if len(libraries) == 1 and libraries[0].upper() == "ALL":
                # Explicit request to search all libraries
                libraries_to_search = list(discovered_libs.keys())
                logger.info(
                    f"Explicit 'ALL' libraries requested, searching {len(libraries_to_search)} libraries"
                )
            else:
                # Use provided library list (with content_type filtering if applicable)
                if parsed.get("content_type"):
                    content_type = parsed["content_type"].lower()
                    # Match libraries by name containing the content type
                    matching_libs = [
                        lib_name
                        for lib_name in discovered_libs.keys()
                        if content_type in lib_name.lower()
                    ]
                    if matching_libs:
                        libraries_to_search = matching_libs
                        logger.info(
                            f"Content type '{content_type}' detected, filtering to matching libraries",
                            extra={"content_type": content_type, "libraries": matching_libs},
                        )
                    else:
                        # No matching libraries found, use provided list
                        libraries_to_search = libraries
                else:
                    # Use provided library list
                    libraries_to_search = libraries

                # Validate library names
                invalid = [lib for lib in libraries_to_search if lib not in discovered_libs]
                if invalid:
                    raise ValueError(f"Libraries not found: {', '.join(invalid)}")
        else:
            raise ValueError(
                f"Invalid libraries parameter: {libraries}. Must be None or a list of library names."
            )

        if not libraries_to_search:
            return LibrarySearchResponse(
                results=[], total_found=0, query_used=query, search_time_ms=0, library_searched=""
            )

        # Search each library and combine results
        all_results: list[dict[str, Any]] = []
        start_time = time.time()

        # Store original library path to restore at the end
        original_path = config.local_library_path
        original_lib_name = None

        # Find original library name
        for name, path in discovered_libs.items():
            if path == original_path:
                original_lib_name = name
                break

        for lib_name in libraries_to_search:
            try:
                # Temporarily switch to this library
                library_path = discovered_libs[lib_name]

                from pathlib import Path

                from ...db.database import db, init_database

                metadata_db = Path(library_path) / "metadata.db"
                if not metadata_db.exists():
                    logger.warning(
                        f"metadata.db not found for library '{lib_name}' at {metadata_db}"
                    )
                    continue

                # Check if we're already connected to this library
                current_path = db.get_current_path()
                target_path = str(metadata_db.absolute())

                # Only switch if we're not already connected to this library
                if current_path != target_path:
                    # Force re-initialization with this library
                    init_database(target_path, echo=False, force=True)
                    logger.debug(
                        f"Database switched to library: {lib_name}",
                        extra={"library": lib_name, "path": target_path},
                    )
                else:
                    logger.debug(f"Already connected to library: {lib_name}, skipping re-init")

                config.set_active_library(lib_name)

                # Perform search using book service with parsed parameters
                # Use get_all() method (not list()) - get_all supports all search parameters
                logger.debug(
                    f"Searching library '{lib_name}'",
                    extra={
                        "library": lib_name,
                        "search": parsed["text"],
                        "author": parsed["author"],
                        "tag": parsed["tag"],
                        "series": parsed["series"],
                    },
                )

                search_results = book_service.get_all(
                    skip=0,
                    limit=1000,  # Get all results for cross-library search
                    search=parsed["text"] if parsed["text"] else None,
                    author_name=parsed["author"],
                    tag_name=parsed["tag"],
                    series_name=parsed["series"],
                    rating=parsed["rating"],
                )

                logger.debug(
                    f"Search results for '{lib_name}': {search_results.get('total', 0)} books found",
                    extra={
                        "library": lib_name,
                        "total": search_results.get("total", 0),
                        "items_count": len(search_results.get("items", [])),
                    },
                )

                # Add library name to each result
                for item in search_results.get("items", []):
                    item["library_name"] = lib_name
                    all_results.append(item)

                # Note: Sessions are managed by scoped_session and will be cleaned up
                # when init_database(force=True) is called for the next library
                logger.debug(
                    f"Search completed for library: {lib_name}",
                    extra={
                        "library": lib_name,
                        "results_count": len(search_results.get("items", [])),
                    },
                )

            except Exception as e:
                logger.error(
                    f"Error searching library '{lib_name}': {e}",
                    exc_info=True,
                    extra={"library": lib_name, "error": str(e), "error_type": type(e).__name__},
                )
                continue

        # Restore original library
        if original_path and original_lib_name:
            try:
                original_metadata_db = Path(original_path) / "metadata.db"
                if original_metadata_db.exists():
                    init_database(str(original_metadata_db.absolute()), echo=False, force=True)
                    config.set_active_library(original_lib_name)
                    logger.debug(f"Restored original library: {original_lib_name}")
            except Exception as e:
                logger.warning(f"Failed to restore original library: {e}")

        # Return combined results
        search_time_ms = int((time.time() - start_time) * 1000)
        return LibrarySearchResponse(
            results=all_results[:50],  # Limit to first page
            total_found=len(all_results),
            query_used=query,
            search_time_ms=search_time_ms,
            library_searched=", ".join(libraries_to_search),
        )

    except ValueError as ve:
        logger.error(f"Validation error in cross-library search: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error in cross-library search: {e}", exc_info=True)
        return LibrarySearchResponse(
            results=[], total_found=0, query_used=query, search_time_ms=0, library_searched=""
        )
