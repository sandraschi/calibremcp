"""
CalibreMCP Phase 2 - FastMCP 2.13+ Server for Calibre E-book Library Management

Austrian efficiency for Sandra's 1000+ book collection across multiple libraries.
Now with 23 comprehensive tools including multi-library, Japanese weeb optimization,
and IT book curation. All tools properly categorized and FastMCP 2.13+ compliant.

FastMCP 2.13 introduces persistent storage backends for stateful applications.

Phase 2 adds 19 additional tools:
- Multi-Library Management (4 tools)
- Advanced Organization & Analysis (5 tools)
- Metadata & Database Operations (4 tools)
- File Operations (3 tools)
- Austrian Efficiency Specials (3 tools)
"""

# CRITICAL: Set stdio to binary mode on Windows for Antigravity IDE compatibility
# Antigravity IDE is strict about JSON-RPC protocol and interprets trailing \r as "invalid trailing data"
# This must happen BEFORE any imports that might write to stdout
import os
import sys

if os.name == 'nt':  # Windows only
    try:
        # Force binary mode for stdin/stdout to prevent CRLF conversion
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    except (OSError, AttributeError):
        # Fallback: just ensure no CRLF conversion
        pass

# DevNullStdout class for stdio mode suppression
class DevNullStdout:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout

    def write(self, data):
        # Suppress all writes to stdout during initialization
        pass

    def flush(self):
        pass

    def restore(self):
        sys.stdout = self.original_stdout

# CRITICAL: Suppress all warnings before any imports
# MCP stdio protocol requires clean stdout/stderr for JSON-RPC communication
import warnings

# Suppress all warnings immediately and aggressively
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")
# Suppress specific warning categories
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# For MCP stdio transport, we need to prevent ANY output to stderr
# Warnings are printed to stderr, which breaks JSON-RPC protocol
# Note: This is handled in __main__.py before imports

# CRITICAL: Detect if we're running in stdio mode (MCP server)
# MCP servers use stdio transport, so stdout must be clean for JSON-RPC
_is_stdio_mode = not sys.stdin.isatty() if hasattr(sys.stdin, 'isatty') else True

from typing import Optional, List, Dict, Any, AsyncContextManager
from pathlib import Path
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from pydantic import BaseModel
from dotenv import load_dotenv

# Import structured logging
from .logging_config import get_logger, log_operation, log_error, setup_logging

# Standard imports - no fallbacks needed
from .calibre_api import CalibreAPIClient
from .config import CalibreConfig
from .storage.persistence import CalibreMCPStorage, set_storage

# Load environment variables
load_dotenv()

# Logger will be re-initialized in main() after logging setup
logger = get_logger("calibremcp.server")

# Global API client and database connections (initialized on startup)
api_client: Optional[CalibreAPIClient] = None
current_library: str = "main"
available_libraries: Dict[str, str] = {}
storage: Optional[CalibreMCPStorage] = None


@asynccontextmanager
async def server_lifespan(mcp_instance: FastMCP) -> AsyncContextManager[None]:
    """FastMCP 2.13 server lifespan for initialization and cleanup."""
    global api_client, current_library, available_libraries, storage, logger

    # Startup
    logger = get_logger("calibremcp.server")
    log_operation(logger, "server_lifespan_startup", level="INFO")

    try:
        # Initialize storage
        storage_instance = CalibreMCPStorage(mcp_instance)
        await storage_instance.initialize()
        set_storage(storage_instance)
        storage = storage_instance
        logger.info("FastMCP 2.13 storage initialized")

        # Initialize config and discover libraries FIRST
        from .db.database import init_database
        from .config import CalibreConfig
        from .config_discovery import get_active_calibre_library

        config = CalibreConfig()

        # Auto-discover libraries using CalibreConfig's discovery system
        if config.auto_discover_libraries:
            discovered_libs = config.discover_libraries()
            if discovered_libs:
                logger.info(f"Auto-discovered {len(discovered_libs)} Calibre libraries")

        # Restore current library from persistent storage
        persisted_library = await storage.get_current_library()
        if persisted_library:
            current_library = persisted_library
            logger.info(f"Restored current library from storage: {current_library}")

        # Discover libraries (using utils for backward compatibility)
        libraries = await discover_libraries()
        available_libraries = libraries
        log_operation(
            logger,
            "library_discovery",
            level="INFO",
            discovered_libraries=list(libraries.keys()),
            current_library=current_library,
        )

        # CRITICAL: Auto-load default library - ensure database is ALWAYS initialized
        # Priority: 1) persisted library, 2) config.local_library_path, 3) active library from Calibre config, 4) first discovered library

        library_to_load = None
        library_name_loaded = None

        # Try persisted library first
        if persisted_library and libraries.get(persisted_library):
            library_to_load = Path(libraries[persisted_library])
            library_name_loaded = persisted_library
            logger.info(f"Using persisted library: {persisted_library}")
        # Try config.local_library_path
        elif config.local_library_path and (config.local_library_path / "metadata.db").exists():
            library_to_load = config.local_library_path
            # Find library name from discovered libraries
            for name, path in libraries.items():
                if Path(path) == library_to_load:
                    library_name_loaded = name
                    break
            if not library_name_loaded:
                library_name_loaded = library_to_load.name
            logger.info(f"Using library from config: {library_to_load}")
        # Try active library from Calibre's own config
        else:
            active_lib = get_active_calibre_library()
            if (
                active_lib
                and active_lib.path.exists()
                and (active_lib.path / "metadata.db").exists()
            ):
                library_to_load = active_lib.path
                library_name_loaded = active_lib.name
                logger.info(f"Using active Calibre library: {active_lib.name} at {active_lib.path}")
        # Fallback to first discovered library
        if not library_to_load and libraries:
            first_lib_path = list(libraries.values())[0]
            library_to_load = Path(first_lib_path)
            library_name_loaded = list(libraries.keys())[0]
            logger.info(
                f"Auto-loading first discovered library: {library_name_loaded} at {library_to_load}"
            )

        # Initialize database with the selected library
        # NOTE: Allow server to start even if database init fails - tools will handle errors gracefully
        db_initialized = False
        if library_to_load:
            metadata_db = library_to_load / "metadata.db"
            if metadata_db.exists():
                try:
                    init_database(str(metadata_db.absolute()), echo=False)
                    current_library = library_name_loaded or library_to_load.name
                    # Update config to use this library
                    config.local_library_path = library_to_load
                    # Persist to storage
                    try:
                        await storage.set_current_library(current_library)
                    except Exception as storage_e:
                        logger.warning(f"Could not persist library to storage: {storage_e}")
                    logger.info(
                        f"SUCCESS: Database initialized with library: {current_library} at {library_to_load}"
                    )
                    db_initialized = True
                except Exception as e:
                    logger.error(f"Failed to initialize database: {e}", exc_info=True)
                    logger.warning(
                        "Server will start without database initialization. "
                        "Tools will attempt to initialize database on first use."
                    )
            else:
                logger.warning(f"metadata.db not found at {metadata_db.absolute()}")
        else:
            logger.warning("No libraries discovered. Server will start without database initialization.")
        
        if not db_initialized:
            logger.warning(
                "Database not initialized during server startup. "
                "Tools will attempt to initialize database automatically on first use."
            )

        log_operation(logger, "server_lifespan_ready", level="INFO")

        yield  # Server runs here

    finally:
        # Shutdown
        log_operation(logger, "server_lifespan_shutdown", level="INFO")

        # Save current library state
        if storage:
            try:
                await storage.set_current_library(current_library)
                logger.info(f"Saved current library to storage: {current_library}")
            except Exception as e:
                logger.warning(f"Failed to save library state: {e}")

        # Cleanup database connections if needed
        # (FastMCP will handle storage cleanup)

        log_operation(logger, "server_lifespan_complete", level="INFO")


# Initialize FastMCP server with lifespan
# Persistent storage is configured in CalibreMCPStorage class
# which uses DiskStore in platform-appropriate directory:
# Windows: %APPDATA%\calibre-mcp (survives Windows restarts)
# macOS: ~/Library/Application Support/calibre-mcp
# Linux: ~/.local/share/calibre-mcp
mcp = FastMCP("CalibreMCP Phase 2", lifespan=server_lifespan)

# CRITICAL: For MCP stdio mode, stderr is already redirected to devnull in __main__.py
# We should not set up additional logging to stderr as it would override the redirection
# and break the MCP JSON-RPC protocol.

# For non-MCP modes (if any), we could set up logging here, but since this is MCP-only,
# we rely on the structured logging from logging_config.py which handles MCP compatibility.

if not _is_stdio_mode:
    # Only set up logging for non-MCP modes (if any)
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Register prompt templates
from .prompts import register_prompts
register_prompts(mcp)


# ==================== RESPONSE MODELS ====================


class LibrarySearchResponse(BaseModel):
    """Response model for library search operations"""

    results: List[Dict[str, Any]]
    total_found: int
    query_used: Optional[str] = None
    search_time_ms: int = 0
    library_searched: str = "main"


class BookDetailResponse(BaseModel):
    """Response model for detailed book information"""

    book_id: int
    title: str
    authors: List[str]
    series: Optional[str] = None
    series_index: Optional[float] = None
    rating: Optional[float] = None
    tags: List[str] = []
    comments: Optional[str] = None
    published: Optional[str] = None
    languages: List[str] = ["en"]
    formats: List[str] = []
    identifiers: Dict[str, str] = {}
    last_modified: Optional[str] = None
    cover_url: Optional[str] = None
    download_links: Dict[str, str] = {}
    library_name: str = "main"


class ConnectionTestResponse(BaseModel):
    """Response model for connection testing"""

    connected: bool
    server_url: str
    server_version: Optional[str] = None
    library_count: int = 0
    total_books: int = 0
    response_time_ms: int = 0
    error_message: Optional[str] = None


class LibraryListResponse(BaseModel):
    """Response model for library listing"""

    libraries: List[Dict[str, Any]]
    current_library: str
    total_libraries: int


class LibraryStatsResponse(BaseModel):
    """Response model for library statistics"""

    library_name: str
    total_books: int
    total_authors: int
    total_series: int
    total_tags: int
    format_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    rating_distribution: Dict[str, int]
    last_modified: Optional[str] = None


class TagStatsResponse(BaseModel):
    """Response model for tag statistics"""

    total_tags: int
    unique_tags: int
    duplicate_tags: List[Dict[str, Any]]
    unused_tags: List[str]
    suggestions: List[Dict[str, Any]]


class DuplicatesResponse(BaseModel):
    """Response model for duplicate detection"""

    duplicate_groups: List[Dict[str, Any]]
    total_duplicates: int
    confidence_scores: Dict[str, float]


class SeriesAnalysisResponse(BaseModel):
    """Response model for series analysis"""

    incomplete_series: List[Dict[str, Any]]
    reading_order_suggestions: List[Dict[str, Any]]
    series_statistics: Dict[str, Any]


class LibraryHealthResponse(BaseModel):
    """Response model for library health analysis"""

    health_score: float
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    database_integrity: bool


class UnreadPriorityResponse(BaseModel):
    """Response model for unread priority list"""

    prioritized_books: List[Dict[str, Any]]
    priority_reasons: Dict[str, str]
    total_unread: int


class MetadataUpdateRequest(BaseModel):
    """Request model for metadata updates"""

    book_id: int
    field: str
    value: Any


class MetadataUpdateResponse(BaseModel):
    """Response model for metadata updates"""

    updated_books: List[int]
    failed_updates: List[Dict[str, Any]]
    success_count: int


class ReadingStats(BaseModel):
    """Response model for reading statistics"""

    total_books_read: int
    average_rating: float
    favorite_genres: List[str]
    reading_patterns: Dict[str, Any]


class ConversionRequest(BaseModel):
    """Request model for format conversion"""

    book_id: int
    source_format: str
    target_format: str
    quality: str = "high"


class ConversionResponse(BaseModel):
    """Response model for format conversion"""

    book_id: int
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None


class JapaneseBookOrganization(BaseModel):
    """Response model for Japanese book organization"""

    manga_series: List[Dict[str, Any]]
    light_novels: List[Dict[str, Any]]
    language_learning: List[Dict[str, Any]]
    reading_recommendations: List[str]


class ITBookCuration(BaseModel):
    """Response model for IT book curation"""

    programming_languages: Dict[str, List[Dict[str, Any]]]
    outdated_books: List[Dict[str, Any]]
    learning_paths: List[Dict[str, Any]]


class ReadingRecommendations(BaseModel):
    """Response model for reading recommendations"""

    recommendations: List[Dict[str, Any]]
    reasoning: Dict[str, str]
    confidence_scores: Dict[str, float]


# ==================== HELPER FUNCTIONS ====================


async def get_api_client() -> Optional[CalibreAPIClient]:
    """
    Get or create API client instance for remote Calibre Content Server access.

    Only creates HTTP client if use_remote=True in config.
    For local libraries, this returns None and tools should use direct SQLite access.
    """
    global api_client
    config = CalibreConfig()

    # Only create HTTP client if remote access is enabled
    if not config.use_remote:
        return None

    if api_client is None:
        api_client = CalibreAPIClient(config)
        await api_client.initialize()
    return api_client


async def discover_libraries() -> Dict[str, str]:
    """Discover available Calibre libraries"""
    global available_libraries

    if available_libraries:
        return available_libraries

    config = CalibreConfig()
    libraries = {}

    # Check configured library path
    if config.local_library_path and config.local_library_path.exists():
        libraries["main"] = str(config.local_library_path)

    # Discover additional libraries
    base_dir = Path("L:/Multimedia Files/Written Word")
    if base_dir.exists():
        for item in base_dir.iterdir():
            if item.is_dir() and (item / "metadata.db").exists():
                libraries[item.name] = str(item)

    available_libraries = libraries
    return libraries


# ==================== SERVER INITIALIZATION ====================


def create_app() -> FastMCP:
    """Create and configure the FastMCP application"""
    return mcp


def main():
    """Main server entry point"""
    try:
        # Initialize logging (stderr is OK for MCP servers, stdout reserved for JSON-RPC)
        log_file_path = Path("logs/calibremcp.log")
        setup_logging(
            level="INFO",
            log_file=log_file_path,
            enable_console=True,  # Enable stderr logging (MCP allows stderr for logs)
        )

        # Re-get logger after setup (logging config changed)
        logger = get_logger("calibremcp.server")

        # Log server startup
        log_operation(
            logger,
            "server_startup",
            level="INFO",
            version="1.0.0",
            collection_size="1000+ books",
            fastmcp_version="2.13.0+",
        )

        # Register tools with FastMCP server
        # Tools with @mcp.tool() auto-register when imported (FastMCP 2.12+)
        # BaseTool classes need explicit registration
        # NOTE: Server lifespan handles initialization (database, libraries, storage)
        
        # Verify mcp instance is valid before registering tools
        if mcp is None:
            logger.error("MCP instance is None - cannot register tools!")
            raise RuntimeError("MCP instance not initialized")
        
        logger.info(f"Registering tools with MCP instance: {type(mcp).__name__}")
        logger.info(f"MCP instance attributes: {[attr for attr in dir(mcp) if not attr.startswith('_')][:10]}")
        
        # Import and register tools
        from .tools import register_tools
        register_tools(mcp)
        
        # Verify tools were registered
        try:
            # Check if FastMCP has registered tools - try multiple ways to access
            tool_count = None
            tool_names = []
            
            # Method 1: Check _tools attribute (internal)
            if hasattr(mcp, '_tools'):
                if isinstance(mcp._tools, dict):
                    tool_count = len(mcp._tools)
                    tool_names = list(mcp._tools.keys())
                elif hasattr(mcp._tools, '__len__'):
                    tool_count = len(mcp._tools)
            
            # Method 2: Check tools attribute (public API)
            if tool_count is None and hasattr(mcp, 'tools'):
                if isinstance(mcp.tools, dict):
                    tool_count = len(mcp.tools)
                    tool_names = list(mcp.tools.keys())
                elif hasattr(mcp.tools, '__len__'):
                    tool_count = len(mcp.tools)
            
            # Method 3: Check _server attribute (FastMCP internal)
            if tool_count is None and hasattr(mcp, '_server'):
                server = mcp._server
                if hasattr(server, '_tools'):
                    if isinstance(server._tools, dict):
                        tool_count = len(server._tools)
                        tool_names = list(server._tools.keys())
            
            # Method 4: Try FastMCP's list_tools method
            if tool_count is None:
                try:
                    # FastMCP 2.13+ has list_tools() method
                    if hasattr(mcp, 'list_tools'):
                        tools_list = mcp.list_tools()
                        if tools_list:
                            tool_count = len(tools_list) if isinstance(tools_list, list) else 0
                            if isinstance(tools_list, list):
                                tool_names = [t.get('name', t if isinstance(t, str) else 'unknown') for t in tools_list]
                    # Also try _server.list_tools if available
                    elif hasattr(mcp, '_server') and hasattr(mcp._server, 'list_tools'):
                        tools_list = mcp._server.list_tools()
                        if tools_list:
                            tool_count = len(tools_list) if isinstance(tools_list, list) else 0
                            if isinstance(tools_list, list):
                                tool_names = [t.get('name', t if isinstance(t, str) else 'unknown') for t in tools_list]
                except Exception as e:
                    logger.debug(f"Could not use list_tools(): {e}")
            
            if tool_count is None:
                tool_count = "unknown (could not determine)"
            
            logger.info(f"Tool registration verification: {tool_count} tools found")
            if tool_names:
                logger.info(f"Registered tool names (first 20): {', '.join(tool_names[:20])}")
            if tool_count == 0:
                logger.error("CRITICAL: No tools registered! Check tool imports and @mcp.tool() decorators.")
                logger.error("Possible causes:")
                logger.error("1. Tool modules failed to import (check import errors in register_tools)")
                logger.error("2. @mcp.tool() decorators are not executing (check if mcp instance is valid)")
                logger.error("3. Circular import issue (tools import mcp before mcp is created)")
                logger.error("4. FastMCP version mismatch or API change")
        except Exception as e:
            logger.error(f"Could not verify tool count: {e}", exc_info=True)

        # Run the FastMCP server (handles event loop internally)
        # Server lifespan handles initialization/cleanup (FastMCP 2.13+)
        # Disable banner for STDIO transport (Rich console fails on Windows STDIO)
        mcp.run(show_banner=False)

    except Exception as e:
        # Log error to file only (no stdout/stderr output for MCP stdio protocol)
        log_error(logger, "server_startup_error", e)
        # Re-raise to let FastMCP handle it properly
        raise


if __name__ == "__main__":
    # Handle both direct execution and module execution
    import sys
    from pathlib import Path

    # If running directly (not as module), fix imports
    # Add src directory to path to allow absolute imports
    current_file = Path(__file__).resolve()
    src_path = current_file.parent.parent  # Go from src/calibre_mcp/server.py to src/

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Now re-import using absolute imports
    from calibre_mcp.server import main

    main()
