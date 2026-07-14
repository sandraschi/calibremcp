"""FastAPI application for Calibre webapp."""

import contextlib
import logging
import logging.handlers
import os
import sys
import time
from pathlib import Path

# CRITICAL: Set up Python path BEFORE any other imports
# This ensures calibre_mcp is importable even in uvicorn reloader subprocesses
_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent.parent.parent
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
    # Use direct import; HTTP mount has no tools (main() never runs)
    os.environ["MCP_USE_HTTP"] = "false"
    # Use direct import for MCP tools (HTTP mount has no tools - they are registered only in main())
    # Then ensure it's in sys.path
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
    elif sys.path.index(src_str) != 0:
        sys.path.remove(src_str)
        sys.path.insert(0, src_str)

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import PlainTextResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 404:
            response = await super().get_response("index.html", scope)
        return response

from .api import (  # noqa: E402, I001
    analysis,
    annas,
    arxiv,
    authors,
    books,
    bulk,
    collections,
    comments,
    export,
    files,
    fleet,
    gutenberg,
    library,
    llm,
    logs,
    metadata,
    publishers,
    rag,
    search,
    series,
    skills,
    specialized,
    system,
    tags,
    viewer,
    webapp_launch,
    settings as api_settings,
)
from .cache import get_libraries_cache, update_current_library, update_libraries_cache  # noqa: E402
from .config import settings  # noqa: E402
from .mcp_access_log_filter import configure_quiet_mcp_http_logging  # noqa: E402

try:
    import prometheus_client
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Ensure logs dir exists and add file handler for webapp (rotation via logging.handlers)
_log_dir = project_root / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / "webapp.log"
_handler = logging.handlers.RotatingFileHandler(
    _log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logging.getLogger("uvicorn").addHandler(_handler)
logging.getLogger("uvicorn.error").addHandler(_handler)
logging.getLogger("uvicorn.access").addHandler(_handler)
logging.getLogger("app").addHandler(_handler)

# MCP clients poll POST /mcp often (e.g. prompts/list); avoid filling webapp.log
configure_quiet_mcp_http_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# Mount FastMCP HTTP endpoints BEFORE other routers
# FastMCP HTTP endpoints run on the same port as the API (10720 reservoir; 13000 in Docker container).
# Dual interface: stdio for MCP clients, HTTP for webapp backend
logger = logging.getLogger(__name__)

try:
    from calibre_mcp.server import create_app as create_mcp_app

    # create_app() returns mcp.http_app(path="/") which doesn't take a path argument
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
        # Register MCP tools on the shared mcp instance for tool_count to be accurate
        try:
            from calibre_mcp.server import mcp as _calibre_mcp
            from calibre_mcp.tools import register_tools

            register_tools(_calibre_mcp)
            logger.info("MCP tools registered for webapp backend")
        except Exception as e:
            logger.warning(f"Could not register MCP tools: {e}")

        from .mcp.client import mcp_client

        # Step 1: List available libraries
        logger.info("Discovering Calibre libraries...")
        libraries_result = await mcp_client.call_tool("manage_libraries", {"operation": "list"})

        if not libraries_result.get("success", True):
            logger.warning(
                f"Failed to list libraries: {libraries_result.get('error', 'Unknown error')}"
            )
            return

        libraries = libraries_result.get("libraries", [])
        total_libraries = libraries_result.get("total_libraries", 0)
        current_library = libraries_result.get("current_library")
        update_libraries_cache(libraries, current_library, total_libraries)
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
                "manage_libraries", {"operation": "switch", "library_name": library_to_load}
            )

            if switch_result.get("success"):
                update_current_library(library_to_load, switch_result.get("library_path"))

                logger.info(
                    f"SUCCESS: Library '{library_to_load}' loaded. "
                    f"Database initialized and ready for searches and book reading."
                )
                logger.info(f"Library path: {switch_result.get('library_path', 'N/A')}")
            else:
                error_msg = switch_result.get(
                    "error", switch_result.get("message", "Unknown error")
                )
                logger.error(f"Failed to switch to library '{library_to_load}': {error_msg}")
        else:
            logger.warning("No library available to load")

    except Exception as e:
        logger.error(f"Failed to initialize database/library on startup: {e}", exc_info=True)
        logger.warning(
            "Server will start but database/library operations may fail until manually initialized"
        )


# CORS middleware (Tauri webview origin is http(s)://tauri.localhost, not localhost:10721)
_tauri_desktop = os.environ.get("CALIBRE_TAURI", "").lower() in ("1", "true", "yes")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https?://tauri\.localhost(:\d+)?" if _tauri_desktop else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (with trailing_slash=False to avoid 307 redirects)
# Core functionality
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(viewer.router, prefix="/api/viewer", tags=["viewer"])
app.include_router(metadata.router, prefix="/api/metadata", tags=["metadata"])
app.include_router(library.router, prefix="/api/libraries", tags=["libraries"])

# Full MCP client functionality
app.include_router(authors.router, prefix="/api/authors", tags=["authors"])
app.include_router(series.router, prefix="/api/series", tags=["series"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(publishers.router, prefix="/api/publishers", tags=["publishers"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(specialized.router, prefix="/api/specialized", tags=["specialized"])
app.include_router(bulk.router, prefix="/api/bulk", tags=["bulk"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(collections.router, prefix="/api/collections", tags=["collections"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(webapp_launch.router, prefix="/api", tags=["webapp-launch"])
app.include_router(fleet.router, prefix="/api", tags=["fleet"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
app.include_router(annas.router, prefix="/api/annas", tags=["annas"])
app.include_router(gutenberg.router, prefix="/api/gutenberg", tags=["gutenberg"])
app.include_router(arxiv.router, prefix="/api/arxiv", tags=["arxiv"])
app.include_router(api_settings.router, prefix="/api/settings", tags=["settings"])

# Mount frontend SPA at /app/ for Tauri WebView navigation
_frontend_dist = None
_try_paths = []
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    _mei = sys._MEIPASS
    _try_paths = [
        os.path.join(_mei, "webapp", "frontend", "out"),
        os.path.join(_mei, "frontend", "out"),
        os.path.join(os.path.dirname(_mei), "webapp", "frontend", "out"),
    ]
_try_paths.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend", "out"))
for _p in _try_paths:
    if _p and os.path.isdir(_p):
        _frontend_dist = _p
        break
if _frontend_dist and os.path.isdir(_frontend_dist):
    _frontend_dist = os.path.realpath(_frontend_dist)
    try:
        app.mount("/app", SPAStaticFiles(directory=_frontend_dist, html=True, follow_symlink=True), name="frontend")
    except TypeError:
        app.mount("/app", SPAStaticFiles(directory=_frontend_dist, html=True), name="frontend")
    logger.info("Frontend SPA mounted at /app from %s", _frontend_dist)
else:
    logger.warning("Frontend dist not found (tried: %s) — API only", "; ".join(str(p) for p in _try_paths))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Calibre Webapp API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


def _count_tools() -> int:
    try:
        from calibre_mcp.server import mcp as _mcp

        if hasattr(_mcp, "_tools"):
            return len(_mcp._tools)
    except Exception:
        pass
    return 0


def _get_calibre_status() -> dict:
    try:
        base_path = os.environ.get("CALIBRE_BASE_PATH", "").strip().strip('"')
        server_url = os.environ.get("CALIBRE_SERVER_URL", "").strip()
        if base_path and Path(base_path).exists():
            return {"mode": "local", "base_path": base_path, "reachable": True}
        if server_url:
            return {"mode": "remote", "server_url": server_url, "reachable": True}
        return {"mode": "unconfigured", "reachable": False}
    except Exception:
        return {"mode": "unknown", "reachable": False}


_SERVER_START = time.time()


@app.get("/health")
@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "server": "calibre-mcp",
        "version": settings.API_VERSION,
        "uptime_seconds": int(time.time() - _SERVER_START),
        "tool_count": _count_tools(),
        "providers": {"calibre": _get_calibre_status()},
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    if PROMETHEUS_AVAILABLE:
        return PlainTextResponse(
            content=prometheus_client.generate_latest().decode("utf-8"),
            media_type="text/plain; version=0.0.4",
        )
    return PlainTextResponse("# prometheus_client not installed", status_code=501)


@app.get("/debug/import")
async def debug_import():
    """Debug endpoint to test calibre_mcp import."""
    info = {
        "python_path": sys.path[:10],
        "pythonpath_env": os.environ.get("PYTHONPATH", "not set"),
        "import_attempt": None,
        "error": None,
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


@app.get("/api/v1/diagnostics")
async def get_cua_diagnostics():
    """CUA diagnostics - backend, system, tools, window, Tesseract status."""
    SERVER_START = getattr(app.state, "server_start_time", time.time())
    uptime = int(time.time() - SERVER_START)
    cpu = mem = disk = None
    tesseract = False
    window = False
    with contextlib.suppress(Exception):
        import psutil
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage(os.environ.get("SystemDrive","C:")+"\\").percent
    with contextlib.suppress(Exception):
        import subprocess
        tesseract = subprocess.run([r"C:\Program Files\Tesseract-OCR\tesseract.exe","--version"],capture_output=True,timeout=5).returncode==0
    with contextlib.suppress(Exception):
        import pywinauto
        a = pywinauto.Application(backend="uia").connect(title_re="Calibre MCP")
        win = a.window(title_re="Calibre MCP")
        win.wait("visible", timeout=2)
        window = True
    return {"success":True,"data":{"backend":{"status":"ok","version":"1.8.6","uptime_seconds":uptime,"port":10720},"system":{"cpu_percent":cpu,"memory_percent":mem,"disk_percent":disk},"tools":{"total":_count_tools(),"categories":["calibre"]},"errors":{"count":0,"recent":[]},"cua_status":{"window_found":window,"backend_reachable":True,"tesseract_available":tesseract}}}


@app.get("/api/libraries/list")
async def get_libraries_list():
    """Get cached libraries list (fast; uses startup cache)."""
    cache = get_libraries_cache()
    if not cache.get("loaded"):
        try:
            from .mcp.client import mcp_client

            libraries_result = await mcp_client.call_tool("manage_libraries", {"operation": "list"})
            if libraries_result.get("success", True):
                update_libraries_cache(
                    libraries_result.get("libraries", []),
                    libraries_result.get("current_library"),
                    libraries_result.get("total_libraries", 0),
                )
        except Exception as e:
            logger.warning(f"Failed to load libraries list: {e}")

    cache = get_libraries_cache()
    return {
        "libraries": cache.get("libraries", []),
        "current_library": cache.get("current_library"),
        "total_libraries": cache.get("total_libraries", 0),
        "loaded": cache.get("loaded", False),
    }
