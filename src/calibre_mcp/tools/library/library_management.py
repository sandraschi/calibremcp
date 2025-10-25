"""
Library management tools for CalibreMCP.

These tools handle multi-library operations, switching between libraries,
and cross-library search functionality.
"""

from typing import Optional, List

# Import the MCP server instance
from ...server import mcp

# Import response models
from ...server import LibraryListResponse, LibraryStatsResponse, LibrarySearchResponse


@mcp.tool()
async def list_libraries() -> LibraryListResponse:
    """
    List all available Calibre libraries with statistics.
    
    Discovers and displays information about all configured libraries
    including book counts, last modified dates, and library paths.
    
    Returns:
        LibraryListResponse: List of available libraries with metadata
    """
    # Implementation will be moved from server.py
    pass


@mcp.tool()
async def switch_library(library_name: str):
    """
    Switch to a different Calibre library for subsequent operations.
    
    Changes the active library context for all other tools.
    This affects which library is used for searches, book operations,
    and other library-specific functions.
    
    Args:
        library_name: Name of the library to switch to
        
    Returns:
        Success confirmation with new active library info
    """
    # Implementation will be moved from server.py
    pass


@mcp.tool()
async def get_library_stats(library_name: Optional[str] = None) -> LibraryStatsResponse:
    """
    Get detailed statistics for a specific library.
    
    Provides comprehensive analytics including format distribution,
    author counts, series information, and reading progress metrics.
    
    Args:
        library_name: Name of library to analyze (uses current if None)
        
    Returns:
        LibraryStatsResponse: Detailed library statistics and metrics
    """
    # Implementation will be moved from server.py
    pass


@mcp.tool()
async def cross_library_search(
    query: str,
    libraries: Optional[List[str]] = None
) -> LibrarySearchResponse:
    """
    Search for books across multiple Calibre libraries simultaneously.
    
    Performs unified search across specified libraries or all available
    libraries, providing consolidated results with library identification.
    
    Args:
        query: Search query text
        libraries: List of library names to search (searches all if None)
        
    Returns:
        LibrarySearchResponse: Consolidated search results from multiple libraries
    """
    # Implementation will be moved from server.py
    pass
