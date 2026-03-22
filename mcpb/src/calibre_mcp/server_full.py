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

if os.name == "nt":  # Windows only
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
_is_stdio_mode = not sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else True

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncContextManager

from fastmcp import FastMCP
from pydantic import BaseModel

# Load environment variables first
# load_dotenv()  # Temporarily disabled for testing

# Lazy imports - only import when actually needed to avoid heavy initialization during module import
# These will be imported in main() or lifespan when actually needed
logger = logging.getLogger("calibremcp.server")  # Temporary logger until proper setup

# Global API client and database connections (initialized on startup)
api_client = None  # CalibreAPIClient
current_library: str = "main"
available_libraries: dict[str, str] = {}
storage = None  # CalibreMCPStorage


def create_app(path: str = "/mcp"):
    """
    Create FastMCP HTTP ASGI app for mounting in FastAPI.

    Args:
        path: Mount path (ignored, handled by FastAPI mount)

    Returns the ASGI app that can be mounted at the specified path.
    FastMCP 2.13+ provides http_app() method for this.
    """
    # FastMCP http_app() returns ASGI app - path is handled by FastAPI mount
    # The path parameter is kept for API compatibility but not used
    return mcp.http_app()


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
        from .config import CalibreConfig
        from .config_discovery import get_active_calibre_library
        from .db.database import init_database

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
            logger.warning(
                "No libraries discovered. Server will start without database initialization."
            )

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
# Lazy MCP instance creation - created only when needed
_mcp_instance = None


def get_mcp() -> FastMCP:
    """Get or create the MCP instance lazily"""
    global _mcp_instance
    if _mcp_instance is None:
        _mcp_instance = FastMCP("CalibreMCP Phase 2")
    return _mcp_instance


# For backward compatibility, provide mcp as a property
@property
def mcp() -> FastMCP:
    return get_mcp()


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
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

# Register prompt templates
from .prompts import register_prompts

register_prompts(mcp)


# ==================== RESPONSE MODELS ====================


class LibrarySearchResponse(BaseModel):
    """Response model for library search operations"""

    model_config = {"from_attributes": True}

    results: list[dict[str, Any]]
    total_found: int
    query_used: str | None = None
    search_time_ms: int = 0
    library_searched: str = "main"


class BookDetailResponse(BaseModel):
    """Response model for detailed book information"""

    model_config = {"from_attributes": True}

    book_id: int
    title: str
    authors: list[str]
    series: str | None = None
    series_index: float | None = None
    rating: float | None = None
    tags: list[str] = []
    comments: str | None = None
    published: str | None = None
    languages: list[str] = ["en"]
    formats: list[str] = []
    identifiers: dict[str, str] = {}
    last_modified: str | None = None
    cover_url: str | None = None
    download_links: dict[str, str] = {}
    library_name: str = "main"


class ConnectionTestResponse(BaseModel):
    """Response model for connection testing"""

    connected: bool
    server_url: str
    server_version: str | None = None
    library_count: int = 0
    total_books: int = 0
    response_time_ms: int = 0
    error_message: str | None = None


class LibraryListResponse(BaseModel):
    """Response model for library listing"""

    model_config = {"from_attributes": True}

    libraries: list[dict[str, Any]]
    current_library: str
    total_libraries: int


class LibraryStatsResponse(BaseModel):
    """Response model for library statistics"""

    model_config = {"from_attributes": True}

    library_name: str
    total_books: int
    total_authors: int
    total_series: int
    total_tags: int
    format_distribution: dict[str, int]
    language_distribution: dict[str, int]
    rating_distribution: dict[str, int]
    last_modified: str | None = None


class TagStatsResponse(BaseModel):
    """Response model for tag statistics"""

    model_config = {"from_attributes": True}

    total_tags: int
    unique_tags: int
    duplicate_tags: list[dict[str, Any]]
    unused_tags: list[str]
    suggestions: list[dict[str, Any]]


class DuplicatesResponse(BaseModel):
    """Response model for duplicate detection"""

    model_config = {"from_attributes": True}

    duplicate_groups: list[dict[str, Any]]
    total_duplicates: int
    confidence_scores: dict[str, float]


class SeriesAnalysisResponse(BaseModel):
    """Response model for series analysis"""

    model_config = {"from_attributes": True}

    incomplete_series: list[dict[str, Any]]
    reading_order_suggestions: list[dict[str, Any]]
    series_statistics: dict[str, Any]


class LibraryHealthResponse(BaseModel):
    """Response model for library health analysis"""

    model_config = {"from_attributes": True}

    health_score: float
    issues_found: list[dict[str, Any]]
    recommendations: list[str]
    database_integrity: bool


class UnreadPriorityResponse(BaseModel):
    """Response model for unread priority list"""

    model_config = {"from_attributes": True}

    prioritized_books: list[dict[str, Any]]
    priority_reasons: dict[str, str]
    total_unread: int


class MetadataUpdateRequest(BaseModel):
    """Request model for metadata updates"""

    model_config = {"from_attributes": True}

    book_id: int
    field: str
    value: Any


class MetadataUpdateResponse(BaseModel):
    """Response model for metadata updates"""

    model_config = {"from_attributes": True}

    updated_books: list[int]
    failed_updates: list[dict[str, Any]]
    success_count: int


class ReadingStats(BaseModel):
    """Response model for reading statistics"""

    model_config = {"from_attributes": True}

    total_books_read: int
    average_rating: float
    favorite_genres: list[str]
    reading_patterns: dict[str, Any]


class ConversionRequest(BaseModel):
    """Request model for format conversion"""

    model_config = {"from_attributes": True}

    book_id: int
    source_format: str
    target_format: str
    quality: str = "high"


class ConversionResponse(BaseModel):
    """Response model for format conversion"""

    model_config = {"from_attributes": True}

    book_id: int
    success: bool
    output_path: str | None = None
    error_message: str | None = None


class JapaneseBookOrganization(BaseModel):
    """Response model for Japanese book organization"""

    model_config = {"from_attributes": True}

    manga_series: list[dict[str, Any]]
    light_novels: list[dict[str, Any]]
    language_learning: list[dict[str, Any]]
    reading_recommendations: list[str]


class ITBookCuration(BaseModel):
    """Response model for IT book curation"""

    model_config = {"from_attributes": True}

    programming_languages: dict[str, list[dict[str, Any]]]
    outdated_books: list[dict[str, Any]]
    learning_paths: list[dict[str, Any]]


class ReadingRecommendations(BaseModel):
    """Response model for reading recommendations"""

    model_config = {"from_attributes": True}

    recommendations: list[dict[str, Any]]
    reasoning: dict[str, str]
    confidence_scores: dict[str, float]


# ==================== HELPER FUNCTIONS ====================


async def get_api_client() -> CalibreAPIClient | None:
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


async def discover_libraries() -> dict[str, str]:
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


async def main():
    """Main server entry point"""
    try:
        # Import heavy modules only when actually running the server
        from .logging_config import get_logger, log_error, log_operation, setup_logging

        # Initialize logging (stderr is OK for MCP servers, stdout reserved for JSON-RPC)
        log_file_path = Path("logs/calibremcp.log")
        setup_logging(
            level="INFO",
            log_file=log_file_path,
            enable_console=False,  # Disable console logging to prevent JSON-RPC corruption
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
            fastmcp_version="2.14.1+",
        )

        # Get the MCP instance (created lazily)
        mcp = get_mcp()

        # Initialize server lifespan manually (deferred from module import)
        logger.info("Initializing server lifespan...")

        lifespan_context = server_lifespan(mcp)
        lifespan_manager = await lifespan_context.__aenter__()
        logger.info("Server lifespan initialized successfully")

        # Register tools with FastMCP server
        # Verify mcp instance is valid before registering tools
        if mcp is None:
            logger.error("MCP instance is None - cannot register tools!")
            raise RuntimeError("MCP instance not initialized")

        logger.info(f"Registering tools with MCP instance: {type(mcp).__name__}")

        # Import and register tools
        # CRITICAL: Suppress potential stdout noise from heavy imports (transformers, etc.)
        # Temporarily disabled for testing
        # from .tools import register_tools
        # register_tools(mcp)
        logger.info("Tool registration disabled for testing")

        # Verify tools were registered
        try:
            # Check if FastMCP has registered tools
            tool_count = "unknown"
            if hasattr(mcp, "_tools"):
                tool_count = len(mcp._tools)

            logger.info(f"Tool registration verification: {tool_count} tools found")
            if tool_count == 0:
                logger.error("CRITICAL: No tools registered! Check tool imports.")
        except Exception as e:
            logger.error(f"Could not verify tool count: {e}")

        # Restore stdout explicitly for JSON-RPC communication
        import calibre_mcp

        if hasattr(calibre_mcp, "_original_stdout") and calibre_mcp._original_stdout:
            sys.stdout.flush()
            sys.stdout = calibre_mcp._original_stdout

            # Re-configure binary mode for Windows if needed
            if os.name == "nt":
                import msvcrt

                try:
                    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
                except Exception:
                    pass

        # Run the FastMCP server using the SOTA-recommended async stdio transport
        # Standard logic for FastMCP 2.14.1+: use run_stdio_async()
        try:
            await mcp.run_stdio_async()
        finally:
            # Cleanup lifespan
            try:
                await lifespan_context.__aexit__(None, None, None)
                logger.info("Server lifespan cleaned up successfully")
            except Exception as cleanup_error:
                logger.error(f"Error during lifespan cleanup: {cleanup_error}")

    except Exception as e:
        # Cleanup lifespan on error
        try:
            await lifespan_context.__aexit__(type(e), e, e.__traceback__)
        except Exception as cleanup_error:
            logger.error(f"Error during lifespan cleanup on exception: {cleanup_error}")

        # Log error to file only (no stdout/stderr output for MCP stdio protocol)
        log_error(logger, "server_startup_error", e)
        # Re-raise to let FastMCP handle it properly
        raise


if __name__ == "__main__":
    # Handle both direct execution and module execution
    import asyncio
    import sys
    from pathlib import Path

    # If running directly (not as module), fix imports
    current_file = Path(__file__).resolve()
    src_path = current_file.parent.parent

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Now re-import using absolute imports
    from calibre_mcp.server import main

    asyncio.run(main())
