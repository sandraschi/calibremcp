"""MCP client wrapper for calling CalibreMCP tools."""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx

# CRITICAL: Set up Python path BEFORE any other imports
# Calculate paths once at module load
_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent.parent.parent.parent
src_path = project_root / "src"

# Strategy 2: If that doesn't work, try finding setup.py or pyproject.toml
if not src_path.exists():
    current = _current_file.parent
    while current != current.parent:
        if (current / "setup.py").exists() or (current / "pyproject.toml").exists():
            project_root = current
            src_path = project_root / "src"
            break
        current = current.parent

# ALWAYS ensure src path is in Python path (must be FIRST, before any imports)
if src_path.exists():
    src_str = str(src_path)
    # Set PYTHONPATH environment variable for subprocesses
    os.environ["PYTHONPATH"] = src_str
    # Remove if already present to avoid duplicates
    if src_str in sys.path:
        sys.path.remove(src_str)
    # Insert at position 0 (highest priority)
    sys.path.insert(0, src_str)

# Now try importing calibre_mcp
_calibre_mcp_available = False
try:
    import calibre_mcp.tools  # noqa: F401

    _calibre_mcp_available = True
except ImportError as e:
    import logging

    logging.error(
        f"Failed to import calibre_mcp.tools: {e}\n"
        f"Python path (first 5): {sys.path[:5]}\n"
        f"Source path: {src_path}\n"
        f"Source exists: {src_path.exists()}\n"
        f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'not set')}\n"
        f"Try: pip install -e . from project root"
    )

from ..utils.errors import MCPError


def _verify_imports():
    """Verify that calibre_mcp can be imported."""
    try:
        import calibre_mcp

        assert hasattr(calibre_mcp, "tools"), "calibre_mcp.tools not found"
        import calibre_mcp.tools

        return True
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        # Use globals() to access module-level variables
        src = globals().get("src_path", "unknown")
        calibre_path = globals().get("calibre_mcp_path", "unknown")
        logger.error(
            f"Failed to verify calibre_mcp imports: {e}\n"
            f"Python path (first 5): {sys.path[:5]}\n"
            f"Source path: {src}\n"
            f"Source exists: {Path(src).exists() if isinstance(src, (str, Path)) else False}\n"
            f"calibre_mcp path: {calibre_path}\n"
            f"calibre_mcp exists: {Path(calibre_path).exists() if isinstance(calibre_path, (str, Path)) else False}"
        )
        return False


# Verify imports work at module load time
_imports_ok = _verify_imports()
if not _imports_ok:
    import logging

    logger = logging.getLogger(__name__)
    logger.warning(
        "calibre_mcp imports failed at module load time. "
        "Individual tool imports will be attempted at call time."
    )


class MCPClient:
    """Wrapper for MCP client to call CalibreMCP tools."""

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self._lock = asyncio.Lock()
        # Use HTTP transport via backend's mounted FastMCP endpoints
        # FastMCP HTTP is mounted at /mcp on the same backend server (port 13000)
        # No separate port needed - everything on 13000!
        self.use_http = os.getenv("MCP_USE_HTTP", "true").lower() == "true"
        backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:13000")
        self.mcp_url = f"{backend_url}/mcp"
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for MCP server."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self.mcp_url, timeout=30.0, follow_redirects=True
            )
        return self._http_client

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Call an MCP tool via HTTP (preferred) or stdio fallback.

        HTTP mode: Calls FastMCP HTTP server directly
        STDIO mode: Falls back to direct import (for compatibility)
        """
        # CRITICAL: Check cache FIRST, before HTTP attempt
        # This ensures cached tools are used even if HTTP fails
        import logging

        logger = logging.getLogger(__name__)

        # Check cache BEFORE any other operations
        if tool_name in _tool_cache and _tool_cache[tool_name] is not None:
            cached_func = _tool_cache[tool_name]
            if callable(cached_func):
                logger.debug("Cache hit for tool %s", tool_name)
                try:
                    result = await cached_func(**arguments)
                    if isinstance(result, str):
                        try:
                            return json.loads(result)
                        except json.JSONDecodeError:
                            return {"result": result}
                    if isinstance(result, dict):
                        return result
                    return {"result": result}
                except Exception as cache_err:
                    logger.warning(
                        f"Cache call failed for {tool_name}: {cache_err}, falling back to HTTP/import"
                    )
                    # Fall through to HTTP/import

        # Try HTTP transport first if enabled
        if self.use_http:
            try:
                client = await self._get_http_client()
                # FastMCP HTTP API: POST to root path with JSON-RPC format
                # Format: {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}
                response = await client.post(
                    "",
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {"name": tool_name, "arguments": arguments},
                    },
                )
                response.raise_for_status()
                result = response.json()
                # FastMCP returns {"content": [...]} format, extract actual result
                if isinstance(result, dict) and "content" in result:
                    content = result["content"]
                    if isinstance(content, list) and len(content) > 0:
                        # Extract text from first content item
                        first_item = content[0]
                        if isinstance(first_item, dict) and "text" in first_item:
                            import json as json_lib

                            try:
                                return json_lib.loads(first_item["text"])
                            except (json_lib.JSONDecodeError, TypeError):
                                return {"result": first_item["text"]}
                return result
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"HTTP call to MCP server failed: {e}, falling back to direct import"
                )
                # Fall through to direct import

        # Fallback: Direct import approach (for stdio mode or HTTP failure)
        try:
            # CRITICAL: ALWAYS ensure path is set before ANY import attempt
            # This must happen EVERY time, not just at module load, because uvicorn
            # may reset sys.path in worker processes
            if src_path.exists():
                src_str = str(src_path)
                # Set environment variable FIRST (for subprocesses and reloader)
                os.environ["PYTHONPATH"] = src_str
                # Then ensure it's first in sys.path
                if src_str in sys.path:
                    if sys.path.index(src_str) != 0:
                        sys.path.remove(src_str)
                        sys.path.insert(0, src_str)
                else:
                    sys.path.insert(0, src_str)

            # Try to use cached tool function first
            # CRITICAL: Check cache BEFORE attempting any imports
            import logging

            logger = logging.getLogger(__name__)

            if tool_name in _tool_cache:
                cached_func = _tool_cache[tool_name]
                if cached_func is not None and callable(cached_func):
                    logger.debug("Cache hit for tool %s", tool_name)
                    tool_func = cached_func
                else:
                    logger.debug("Tool %s in cache but not callable", tool_name)
                    tool_func = None
            else:
                logger.debug("Tool %s not in cache", tool_name)
                tool_func = None

            # Only attempt import if cache miss
            if tool_func is None:
                logger.debug("Cache miss for %s, dynamic import", tool_name)
                # Fallback: Import the tool dynamically
                # Map tool names to their import paths - ALL MCP tools
                tool_map = {
                    # Book management
                    "query_books": "calibre_mcp.tools.book_management.query_books",
                    "manage_books": "calibre_mcp.tools.book_management.manage_books",
                    "manage_viewer": "calibre_mcp.tools.viewer.manage_viewer",
                    # Library management
                    "manage_libraries": "calibre_mcp.tools.library.manage_libraries",
                    # Metadata management
                    "manage_metadata": "calibre_mcp.tools.metadata.manage_metadata",
                    # Authors, series, tags, publishers, comments
                    "manage_authors": "calibre_mcp.tools.authors.manage_authors",
                    "manage_series": "calibre_mcp.tools.series.manage_series",
                    "manage_tags": "calibre_mcp.tools.tags.manage_tags",
                    "manage_publishers": "calibre_mcp.tools.publishers.manage_publishers",
                    "manage_comments": "calibre_mcp.tools.comments.manage_comments",
                    # File operations
                    "manage_files": "calibre_mcp.tools.files.manage_files",
                    # Analysis
                    "analyze_library": "calibre_mcp.tools.analysis.analyze_library",
                    "manage_analysis": "calibre_mcp.tools.analysis.manage_analysis",
                    # Specialized tools
                    "manage_specialized": "calibre_mcp.tools.specialized.manage_specialized",
                    # System tools
                    "manage_system": "calibre_mcp.tools.system.manage_system",
                    # Advanced features
                    "manage_bulk_operations": "calibre_mcp.tools.advanced_features.manage_bulk_operations",
                    "manage_content_sync": "calibre_mcp.tools.advanced_features.manage_content_sync",
                    "manage_smart_collections": "calibre_mcp.tools.advanced_features.manage_smart_collections",
                    # User management
                    "manage_users": "calibre_mcp.tools.user_management.manage_users",
                    # Export / Import
                    "export_books": "calibre_mcp.tools.import_export.export_books",
                    "manage_import": "calibre_mcp.tools.import_export.manage_import",
                }

                if tool_name not in tool_map:
                    raise MCPError(f"Unknown tool: {tool_name}")

                module_path = tool_map[tool_name]

                # Import the function directly using importlib
                # First ensure calibre_mcp base module is imported
                # Use multiple strategies to ensure import works
                calibre_mcp_imported = False
                import_err = None

                # Strategy 1: Normal import
                try:
                    import calibre_mcp  # noqa: F401

                    calibre_mcp_imported = True
                except ImportError as e:
                    import_err = e

                # Strategy 2: Force reload if already imported but broken
                if not calibre_mcp_imported:
                    # Force path and retry
                    if src_path.exists():
                        src_str = str(src_path)
                        os.environ["PYTHONPATH"] = src_str
                        if src_str not in sys.path:
                            sys.path.insert(0, src_str)
                        elif sys.path.index(src_str) != 0:
                            sys.path.remove(src_str)
                            sys.path.insert(0, src_str)
                    try:
                        import calibre_mcp  # noqa: F401

                        calibre_mcp_imported = True
                    except ImportError:
                        pass

                # Strategy 3: Use importlib.util to force import from file
                if not calibre_mcp_imported and src_path.exists():
                    try:
                        import importlib.util

                        init_file = src_path / "calibre_mcp" / "__init__.py"
                        if init_file.exists():
                            spec = importlib.util.spec_from_file_location("calibre_mcp", init_file)
                            if spec and spec.loader:
                                calibre_mcp = importlib.util.module_from_spec(spec)
                                sys.modules["calibre_mcp"] = calibre_mcp
                                spec.loader.exec_module(calibre_mcp)
                                calibre_mcp_imported = True
                    except Exception:
                        pass

                if not calibre_mcp_imported:
                    raise MCPError(
                        f"Failed to import calibre_mcp after all strategies\n"
                        f"Original error: {import_err}\n"
                        f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'not set')}\n"
                        f"sys.path (first 5): {sys.path[:5]}\n"
                        f"src_path: {src_path}\n"
                        f"src_path exists: {src_path.exists()}\n"
                        f"__init__.py exists: {(src_path / 'calibre_mcp' / '__init__.py').exists()}"
                    )

                # Now import the specific tool module
                import importlib

                try:
                    module = importlib.import_module(module_path)
                except ImportError as module_err:
                    # Provide detailed error information
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.error(
                        f"Failed to import module {module_path}:\n"
                        f"Error: {module_err}\n"
                        f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'not set')}\n"
                        f"sys.path (first 10): {sys.path[:10]}\n"
                        f"calibre_mcp in sys.modules: {'calibre_mcp' in sys.modules}\n"
                        f"src_path: {src_path}\n"
                        f"Attempting to verify calibre_mcp import..."
                    )
                    # Try to verify calibre_mcp is actually importable
                    try:
                        import calibre_mcp

                        logger.error(f"calibre_mcp IS importable: {calibre_mcp.__file__}")
                        # Try importing submodules
                        try:
                            import calibre_mcp.tools

                            logger.error("calibre_mcp.tools IS importable")
                        except ImportError as tools_err:
                            logger.error(f"calibre_mcp.tools NOT importable: {tools_err}")
                    except ImportError as verify_err:
                        logger.error(f"calibre_mcp verification FAILED: {verify_err}")
                    raise MCPError(
                        f"Failed to import module {module_path}: {module_err}\n"
                        f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'not set')}\n"
                        f"sys.path: {sys.path[:5]}"
                    )

                # Extract function name from module path (last component)
                func_name = module_path.split(".")[-1]

                # Get the function from the module
                if not hasattr(module, func_name):
                    available_attrs = [attr for attr in dir(module) if not attr.startswith("_")]
                    raise MCPError(
                        f"Tool function '{func_name}' not found in module '{module_path}'. "
                        f"Available attributes: {available_attrs[:10]}"
                    )

                tool_obj = getattr(module, func_name)

                # FastMCP tools are FunctionTool objects, need to access .fn attribute
                if hasattr(tool_obj, "fn"):
                    tool_func = tool_obj.fn
                elif callable(tool_obj):
                    tool_func = tool_obj
                else:
                    raise MCPError(
                        f"Tool '{func_name}' from '{module_path}' is not callable. "
                        f"Type: {type(tool_obj)}, has .fn: {hasattr(tool_obj, 'fn')}"
                    )

                # Cache for next time
                _tool_cache[tool_name] = tool_func

            # Verify it's callable
            if not callable(tool_func):
                raise MCPError(
                    f"Tool function '{tool_name}' is not callable. Type: {type(tool_func)}"
                )

            # Call the tool function directly
            # Note: MCP tools are async, so we await them
            result = await tool_func(**arguments)

            # Parse result if it's a string (JSON)
            if isinstance(result, str):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"result": result}

            # If result is already a dict, return it
            if isinstance(result, dict):
                return result

            # Otherwise, wrap it
            return {"result": result}

        except ImportError as e:
            # Add detailed error info
            import logging

            logger = logging.getLogger(__name__)
            error_msg = str(e)
            # Check if tool is in cache (shouldn't happen, but verify)
            cache_status = f"Cache has {len(_tool_cache)} tools: {list(_tool_cache.keys())}"
            logger.error(
                f"Import failed for {tool_name}: {error_msg}\n"
                f"Module path: {module_path if 'module_path' in locals() else 'N/A'}\n"
                f"Python path (first 5): {sys.path[:5]}\n"
                f"src_path exists: {src_path.exists()}\n"
                f"src_path: {src_path}\n"
                f"{cache_status}\n"
                f"Tool in cache: {tool_name in _tool_cache}\n"
                f"Full error: {repr(e)}"
            )
            # If tool IS in cache, something is very wrong - try using cache anyway
            if tool_name in _tool_cache and _tool_cache[tool_name] is not None:
                logger.warning(
                    f"Tool {tool_name} IS in cache but import failed - using cache anyway"
                )
                try:
                    tool_func = _tool_cache[tool_name]
                    result = await tool_func(**arguments)
                    if isinstance(result, str):
                        try:
                            return json.loads(result)
                        except json.JSONDecodeError:
                            return {"result": result}
                    if isinstance(result, dict):
                        return result
                    return {"result": result}
                except Exception as cache_err:
                    logger.error(f"Cache fallback also failed: {cache_err}")
            raise MCPError(f"Failed to import tool {tool_name}: {error_msg}")
        except AttributeError as e:
            raise MCPError(f"Tool {tool_name} not found in module: {str(e)}")
        except Exception as e:
            raise MCPError(f"Error calling tool {tool_name}: {str(e)}")

    async def close(self):
        """Close MCP connection."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        if self.process:
            self.process.terminate()
            await asyncio.sleep(0.1)
            if self.process.poll() is None:
                self.process.kill()
            self.process = None


# Pre-import and cache tool functions at module load time
# This avoids importlib issues in uvicorn reloader subprocesses
_tool_cache: dict[str, Any] = {}
_tools_preloaded = False


def _preload_tools():
    """Pre-load all tool functions into cache."""
    global _tool_cache, _tools_preloaded
    if _tools_preloaded:
        return  # Already attempted

    _tools_preloaded = True

    # CRITICAL: Ensure path is set before importing
    if src_path.exists():
        src_str = str(src_path)
        os.environ["PYTHONPATH"] = src_str
        if src_str not in sys.path:
            sys.path.insert(0, src_str)
        elif sys.path.index(src_str) != 0:
            sys.path.remove(src_str)
            sys.path.insert(0, src_str)

    # ALL MCP tools - comprehensive list for full webapp functionality
    tool_modules = {
        # Book management
        "query_books": "calibre_mcp.tools.book_management.query_books",
        "manage_books": "calibre_mcp.tools.book_management.manage_books",
        "manage_viewer": "calibre_mcp.tools.viewer.manage_viewer",
        # Library management
        "manage_libraries": "calibre_mcp.tools.library.manage_libraries",
        # Metadata management
        "manage_metadata": "calibre_mcp.tools.metadata.manage_metadata",
        # Authors, series, tags, publishers, comments
        "manage_authors": "calibre_mcp.tools.authors.manage_authors",
        "manage_series": "calibre_mcp.tools.series.manage_series",
        "manage_tags": "calibre_mcp.tools.tags.manage_tags",
        "manage_publishers": "calibre_mcp.tools.publishers.manage_publishers",
        "manage_comments": "calibre_mcp.tools.comments.manage_comments",
        # File operations
        "manage_files": "calibre_mcp.tools.files.manage_files",
        # Analysis
        "analyze_library": "calibre_mcp.tools.analysis.analyze_library",
        "manage_analysis": "calibre_mcp.tools.analysis.manage_analysis",
        # Specialized: skip until manage_specialized.py exists (optional portmanteau)
        # System tools
        "manage_system": "calibre_mcp.tools.system.manage_system",
        # Advanced features
        "manage_bulk_operations": "calibre_mcp.tools.advanced_features.manage_bulk_operations",
        "manage_content_sync": "calibre_mcp.tools.advanced_features.manage_content_sync",
        "manage_smart_collections": "calibre_mcp.tools.advanced_features.manage_smart_collections",
        # User management
        "manage_users": "calibre_mcp.tools.user_management.manage_users",
        # Export / Import
        "export_books": "calibre_mcp.tools.import_export.export_books",
        "manage_import": "calibre_mcp.tools.import_export.manage_import",
        # OCR (if available)
        # Note: OCR tool may be a BaseTool class, handle separately if needed
    }

    for tool_name, module_path in tool_modules.items():
        try:
            # First ensure base module is imported
            try:
                import calibre_mcp  # noqa: F401
            except ImportError:
                # Try importlib.util approach
                import importlib.util

                init_file = src_path / "calibre_mcp" / "__init__.py"
                if init_file.exists():
                    spec = importlib.util.spec_from_file_location("calibre_mcp", init_file)
                    if spec and spec.loader:
                        calibre_mcp = importlib.util.module_from_spec(spec)
                        sys.modules["calibre_mcp"] = calibre_mcp
                        spec.loader.exec_module(calibre_mcp)

            import importlib

            module = importlib.import_module(module_path)
            func_name = module_path.split(".")[-1]
            tool_obj = getattr(module, func_name)

            # FastMCP tools are FunctionTool objects, need to access .fn attribute
            if hasattr(tool_obj, "fn"):
                _tool_cache[tool_name] = tool_obj.fn
            elif callable(tool_obj):
                _tool_cache[tool_name] = tool_obj
            import logging

            logging.debug("Preloaded tool: %s", tool_name)
        except Exception as e:
            import logging

            logging.error(f"Failed to preload tool {tool_name}: {e}", exc_info=True)


# ALWAYS try to preload tools at module load time
# This happens before uvicorn starts, so path should be correct
try:
    _preload_tools()
except Exception as e:
    import logging

    logging.warning(f"Failed to preload tools at module load: {e}")

# Global client instance
mcp_client = MCPClient()
