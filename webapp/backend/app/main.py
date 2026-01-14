"""FastAPI application for Calibre webapp."""

import logging
import os
import sys
from pathlib import Path

# CRITICAL: Set up Python path BEFORE any other imports
# This ensures calibre_mcp is importable even in uvicorn reloader subprocesses
_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent.parent.parent.parent
src_path = project_root / "src"

if not src_path.exists():
    current = _current_file.parent
    while current != current.parent:
        if (current / "setup.py").exists() or (current / "pyproject.toml").exists():
            project_root = current
            src_path = project_root / "src"
            break
        current = current.parent

if src_path.exists():
    src_str = str(src_path)
    # CRITICAL: Set PYTHONPATH environment variable FIRST (for uvicorn subprocesses)
    os.environ["PYTHONPATH"] = src_str
    # Then ensure it's in sys.path
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
    elif sys.path.index(src_str) != 0:
        sys.path.remove(src_str)
        sys.path.insert(0, src_str)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    analysis,
    authors,
    books,
    bulk,
    collections,
    comments,
    export,
    files,
    library,
    metadata,
    search,
    specialized,
    system,
    tags,
    viewer,
)
from .config import settings

# Global cache for libraries list (populated at startup)
_libraries_cache: dict = {
    "libraries": [],
    "current_library": None,
    "total_libraries": 0,
    "loaded": False
}

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# Mount FastMCP HTTP endpoints BEFORE other routers
# FastMCP HTTP endpoints run on same port 13000 - no port hopping!
# Dual interface: stdio for MCP clients, HTTP for webapp backend
logger = logging.getLogger(__name__)

try:
    from calibre_mcp.server import create_app as create_mcp_app
    # create_app() returns mcp.http_app() which doesn't take a path argument
    # The path is handled by FastAPI's app.mount()
    mcp_app = create_mcp_app()
    if mcp_app:
        app.mount("/mcp", mcp_app)
        logger.info("FastMCP HTTP endpoints mounted at /mcp (dual interface: stdio + HTTP)")
except Exception as e:
    logger.warning(f"Could not mount FastMCP HTTP app: {e}")
    logger.warning("Falling back to direct import mode")


@app.on_event("startup")
async def startup_event():
    """Initialize database and load library on startup."""
    
    # Re-check path on startup (uvicorn reloader may reset it)
    _current_file = Path(__file__).resolve()
    project_root = _current_file.parent.parent.parent.parent.parent
    src_path = project_root / "src"
    
    if not src_path.exists():
        current = _current_file.parent
        while current != current.parent:
            if (current / "setup.py").exists() or (current / "pyproject.toml").exists():
                project_root = current
                src_path = project_root / "src"
                break
            current = current.parent
    
    if src_path.exists():
        src_str = str(src_path)
        # Set PYTHONPATH environment variable for uvicorn reloader subprocesses
        os.environ["PYTHONPATH"] = src_str
        # Also ensure it's in sys.path
        if src_str not in sys.path:
            sys.path.insert(0, src_str)
        elif sys.path.index(src_str) != 0:
            sys.path.remove(src_str)
            sys.path.insert(0, src_str)
        
        # Verify import works
        try:
            import calibre_mcp  # noqa: F401
            logger.info(f"calibre_mcp imported successfully from {src_str}")
        except ImportError as e:
            logger.error(f"Failed to import calibre_mcp: {e}")
            return
    
    # Initialize database and load library
    try:
        from .mcp.client import mcp_client
        
        # Step 1: List available libraries
        logger.info("Discovering Calibre libraries...")
        libraries_result = await mcp_client.call_tool(
            "manage_libraries",
            {"operation": "list"}
        )
        
        if not libraries_result.get("success", True):
            logger.warning(f"Failed to list libraries: {libraries_result.get('error', 'Unknown error')}")
            return
        
        libraries = libraries_result.get("libraries", [])
        total_libraries = libraries_result.get("total_libraries", 0)
        current_library = libraries_result.get("current_library")
        
        # Cache libraries list for dropdown population
        global _libraries_cache
        _libraries_cache = {
            "libraries": libraries,
            "current_library": current_library,
            "total_libraries": total_libraries,
            "loaded": True
        }
        
        logger.info(f"Found {total_libraries} Calibre libraries (cached for dropdown)")
        
        if total_libraries == 0:
            logger.warning("No Calibre libraries found. Database will not be initialized.")
            return
        
        # Step 2: Switch to a library (use current if set, otherwise first available)
        library_to_load = None
        
        # Check if there's already a current library
        if current_library:
            # Verify it still exists
            for lib in libraries:
                if lib.get("name") == current_library:
                    library_to_load = current_library
                    logger.info(f"Using existing current library: {current_library}")
                    break
        
        # If no current library or it doesn't exist, use first available
        if not library_to_load and libraries:
            library_to_load = libraries[0].get("name")
            logger.info(f"No current library set, switching to first available: {library_to_load}")
        
        if library_to_load:
            # Switch to the library (this initializes the database)
            logger.info(f"Switching to library: {library_to_load}")
            switch_result = await mcp_client.call_tool(
                "manage_libraries",
                {
                    "operation": "switch",
                    "library_name": library_to_load
                }
            )
            
            if switch_result.get("success"):
                # Update cache with new current library
                _libraries_cache["current_library"] = library_to_load
                
                logger.info(
                    f"SUCCESS: Library '{library_to_load}' loaded. "
                    f"Database initialized and ready for searches and book reading."
                )
                logger.info(f"Library path: {switch_result.get('library_path', 'N/A')}")
            else:
                error_msg = switch_result.get("error", switch_result.get("message", "Unknown error"))
                logger.error(f"Failed to switch to library '{library_to_load}': {error_msg}")
        else:
            logger.warning("No library available to load")
            
    except Exception as e:
        logger.error(f"Failed to initialize database/library on startup: {e}", exc_info=True)
        logger.warning("Server will start but database/library operations may fail until manually initialized")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (with trailing_slash=False to avoid 307 redirects)
# Core functionality
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(viewer.router, prefix="/api/viewer", tags=["viewer"])
app.include_router(metadata.router, prefix="/api/metadata", tags=["metadata"])
app.include_router(library.router, prefix="/api/libraries", tags=["libraries"])

# Full MCP client functionality
app.include_router(authors.router, prefix="/api/authors", tags=["authors"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(specialized.router, prefix="/api/specialized", tags=["specialized"])
app.include_router(bulk.router, prefix="/api/bulk", tags=["bulk"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(collections.router, prefix="/api/collections", tags=["collections"])
app.include_router(system.router, prefix="/api/system", tags=["system"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Calibre Webapp API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/debug/import")
async def debug_import():
    """Debug endpoint to test calibre_mcp import."""
    info = {
        "python_path": sys.path[:10],
        "pythonpath_env": os.environ.get("PYTHONPATH", "not set"),
        "import_attempt": None,
        "error": None
    }
    
    try:
        import calibre_mcp
        info["import_attempt"] = "SUCCESS"
        info["calibre_mcp_file"] = calibre_mcp.__file__
        info["has_tools"] = hasattr(calibre_mcp, "tools")
    except ImportError as e:
        info["import_attempt"] = "FAILED"
        info["error"] = str(e)
    
    return info


@app.get("/api/libraries/list")
async def get_libraries_list():
    """Get cached libraries list for dropdown population."""
    global _libraries_cache
    
    # If cache not loaded yet, try to load it now
    if not _libraries_cache.get("loaded"):
        try:
            from .mcp.client import mcp_client
            libraries_result = await mcp_client.call_tool(
                "manage_libraries",
                {"operation": "list"}
            )
            if libraries_result.get("success", True):
                _libraries_cache = {
                    "libraries": libraries_result.get("libraries", []),
                    "current_library": libraries_result.get("current_library"),
                    "total_libraries": libraries_result.get("total_libraries", 0),
                    "loaded": True
                }
        except Exception as e:
            logger.warning(f"Failed to load libraries list: {e}")
    
    return {
        "libraries": _libraries_cache.get("libraries", []),
        "current_library": _libraries_cache.get("current_library"),
        "total_libraries": _libraries_cache.get("total_libraries", 0),
        "loaded": _libraries_cache.get("loaded", False)
    }
