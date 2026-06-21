"""
Tools package for Calibre MCP server.

This package contains all the tools available in the Calibre MCP server,
organized by functionality into submodules. Tools are automatically discovered
and loaded from all subdirectories.
"""

import contextlib
import importlib
import inspect
import logging
import pkgutil
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar, cast

from .base_tool import BaseTool, mcp_tool

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Callable[..., Any])

TOOL_REGISTRY: dict[str, dict[str, Any]] = {}

__all__ = ["BaseTool", "mcp_tool"]

# Base directory for Calibre libraries
import os as _os
_bp = _os.environ.get("CALIBRE_BASE_PATH", "").strip().strip('"')
CALIBRE_BASE_DIR = Path(_bp) if _bp else Path("L:/Multimedia Files/Written Word")

IGNORE_DIRS = {"__pycache__", ".mypy_cache", ".pytest_cache"}


def tool(
    name: str, description: str, parameters: dict[str, Any] | None = None, **kwargs
) -> Callable[[T], T]:
    """
    Decorator to register a function as an MCP tool.

    Args:
        name: Unique name of the tool
        description: Description of what the tool does
        parameters: Dictionary describing the tool's parameters
        **kwargs: Additional tool metadata

    Returns:
        Decorated function
    """

    def decorator(func: T) -> T:
        # Add tool metadata to the function
        func._mcp_tool = {  # type: ignore
            "name": name,
            "description": description,
            "parameters": parameters or {},
            "func": func,
            **kwargs,
        }

        # Register the tool
        TOOL_REGISTRY[name] = func._mcp_tool  # type: ignore

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)

        return cast(T, wrapper)

    return decorator


def get_available_tools() -> list[dict[str, Any]]:
    """
    Get a list of all available tools with their metadata.

    Returns:
        List of tool metadata dictionaries
    """
    return [
        {
            "name": tool_info["name"],
            "description": tool_info["description"],
            "parameters": tool_info.get("parameters", {}),
        }
        for tool_info in TOOL_REGISTRY.values()
    ]


def discover_tools() -> list[type["BaseTool"]]:
    """
    Discover and import all tool classes from subdirectories.

    Returns:
        List of tool classes that should be registered
    """
    tools_dir = Path(__file__).parent
    tool_classes: list[type[BaseTool]] = []

    # Import all modules in the tools directory
    for _finder, name, is_pkg in pkgutil.iter_modules([str(tools_dir)]):
        if name == "__init__" or name.startswith("_"):
            continue

        try:
            module = importlib.import_module(f"calibre_mcp.tools.{name}")

            # If it's a package, look for tools in its __init__.py
            if is_pkg:
                if hasattr(module, "tools"):
                    tool_classes.extend(module.tools)
            # If it's a module, look for tool classes
            else:
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if inspect.isclass(attr) and issubclass(attr, BaseTool) and attr != BaseTool:
                        tool_classes.append(attr)

        except Exception as e:
            logger.warning(f"Failed to import tool module {name}: {e}", exc_info=True)

    return tool_classes


def register_tools(mcp: Any) -> None:
    """
    Register all tools with an MCP server instance with detailed error handling and timing.

    This function registers all FastMCP compliant tools.
    Explicit imports are used instead of dynamic discovery to ensure reliability.

    Args:
        mcp: MCP server instance (FastMCP)
    """
    import time

    import_count = 0
    error_count = 0

    logger.info("TOOL REGISTRATION: Starting tool registration process...")
    start_time = time.time()

    # Import and register all portmanteau tools
    # Tools are automatically registered with FastMCP via @mcp.tool() decorators
    # Just importing them ensures they're loaded and registered

    try:
        logger.info("Importing portmanteau tools (target: 15 core tools)...")

        # Config for beta tools (CALIBRE_BETA_TOOLS=true)
        from ..config import CalibreConfig

        config = CalibreConfig.load_config()
        load_beta = getattr(config, "load_beta_tools", False)

        # Core: manage_libraries (includes test_connection, discover); no standalone core/library_discovery
        import_start = time.time()
        importlib.import_module("calibre_mcp.tools.library")

        import_time = time.time() - import_start
        logger.info(f"Library tools loaded in {import_time:.2f}s")

        # Book management (manage_books, query_books, search_fulltext)
        import_start = time.time()
        importlib.import_module("calibre_mcp.tools.book_management")

        import_time = time.time() - import_start
        logger.info(f"Book management loaded in {import_time:.2f}s")

        # RAG (semantic search over book text and metadata; lancedb/fastembed in main deps)
        import_start = time.time()
        with contextlib.suppress(ImportError):
            importlib.import_module("calibre_mcp.tools.rag")

        try:
            importlib.import_module("calibre_mcp.tools.portmanteau.search")
        except Exception as e:
            logger.error(f"Failed to load RAG portmanteaus: {e}", exc_info=True)

        import_time = time.time() - import_start
        logger.info(f"RAG tools loaded in {import_time:.2f}s")

        # Metadata, tags, comments, series, publishers, authors (core)
        import_start = time.time()
        importlib.import_module("calibre_mcp.tools.authors")
        importlib.import_module("calibre_mcp.tools.comments")
        importlib.import_module("calibre_mcp.tools.metadata")
        importlib.import_module("calibre_mcp.tools.publishers")
        importlib.import_module("calibre_mcp.tools.series")
        importlib.import_module("calibre_mcp.tools.tags")

        import_time = time.time() - import_start
        logger.info(f"Metadata/tags/authors loaded in {import_time:.2f}s")

        # Files, analysis, library operations, system, import/export, viewer
        import_start = time.time()
        importlib.import_module("calibre_mcp.tools.analysis")
        importlib.import_module("calibre_mcp.tools.files")
        importlib.import_module("calibre_mcp.tools.import_export")
        importlib.import_module("calibre_mcp.tools.library_operations")
        importlib.import_module("calibre_mcp.tools.system")
        importlib.import_module("calibre_mcp.tools.viewer")

        import_time = time.time() - import_start
        logger.info(f"Files/analysis/system loaded in {import_time:.2f}s")

        # Help system
        import_start = time.time()
        importlib.import_module("calibre_mcp.tools.help_tools")

        import_time = time.time() - import_start
        logger.info(f"Help tools loaded in {import_time:.2f}s")

        # MCP Apps / Prefab (prefab-ui required)
        from .prefab import register_prefab_tools

        register_prefab_tools()

        # OCR
        import_start = time.time()
        try:
            from .ocr.calibre_ocr_tool import OCRTool

            OCRTool.register(mcp)
        except Exception as e:
            logger.warning(f"Failed to load OCRTool, skipping: {e}")
        import_time = time.time() - import_start
        logger.info(f"OCR loaded in {import_time:.2f}s")

        # Beta tools: manage_import, descriptions, user_comments, extended_metadata, times,
        # content_sync, ai_operations, bulk_operations, organization, users, specialized, agentic
        if load_beta:
            import_start = time.time()
            importlib.import_module("calibre_mcp.tools.advanced_features")
            from .agentic import register_agentic_tools
            importlib.import_module("calibre_mcp.tools.agentic_workflow")
            importlib.import_module("calibre_mcp.tools.ai")
            importlib.import_module("calibre_mcp.tools.descriptions")
            importlib.import_module("calibre_mcp.tools.extended_metadata")
            importlib.import_module("calibre_mcp.tools.import_export.manage_import")
            importlib.import_module("calibre_mcp.tools.organization")
            importlib.import_module("calibre_mcp.tools.specialized")
            importlib.import_module("calibre_mcp.tools.times")
            importlib.import_module("calibre_mcp.tools.user_comments")
            importlib.import_module("calibre_mcp.tools.user_management")

            register_agentic_tools()
            import_time = time.time() - import_start
            logger.info(f"Beta tools loaded in {import_time:.2f}s (CALIBRE_BETA_TOOLS=true)")

        import_count = 15 if not load_beta else 26

    except Exception as e:
        logger.error(f"Failed to load portmanteau tools: {e}", exc_info=True)
        error_count += 1

    # Get count of registered tools from FastMCP
    try:
        if hasattr(mcp, "_tools"):
            registered_tools_count = len(mcp._tools)
        elif hasattr(mcp, "tools"):
            registered_tools_count = len(mcp.tools) if isinstance(mcp.tools, dict) else 0
        else:
            registered_tools_count = "unknown"
    except Exception:
        registered_tools_count = "unknown"

    total_time = time.time() - start_time
    logger.info(
        f"Tool registration complete in {total_time:.2f}s: {import_count} modules/tools processed, "
        f"{error_count} errors, "
        f"{registered_tools_count} total tools registered"
    )

    if error_count > 0:
        logger.warning(f"{error_count} tool modules failed to load - check logs above for details")
    else:
        logger.info("SUCCESS: All tool modules loaded successfully")
