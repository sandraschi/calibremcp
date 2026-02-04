"""
Tools package for Calibre MCP server.

This package contains all the tools available in the Calibre MCP server,
organized by functionality into submodules. Tools are automatically discovered
and loaded from all subdirectories.
"""

from typing import Dict, Any, Callable, Optional, TypeVar, List, Type, cast
from functools import wraps
import importlib
import pkgutil
import inspect
import logging
from pathlib import Path

# Set up logging (stderr is OK for MCP servers)
logger = logging.getLogger(__name__)

# Type variable for tool functions
T = TypeVar("T", bound=Callable[..., Any])

# Global tool registry
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}

# Base directory for Calibre libraries
CALIBRE_BASE_DIR = Path("L:/Multimedia Files/Written Word")

# Set of directories to ignore when discovering tools
IGNORE_DIRS = {"__pycache__", ".mypy_cache", ".pytest_cache"}

# Import the base tool class (after type definitions)
from .base_tool import BaseTool, mcp_tool  # noqa: E402, F401


def tool(
    name: str, description: str, parameters: Optional[Dict[str, Any]] = None, **kwargs
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


def get_available_tools() -> List[Dict[str, Any]]:
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


def discover_tools() -> List[Type["BaseTool"]]:
    """
    Discover and import all tool classes from subdirectories.

    Returns:
        List of tool classes that should be registered
    """
    tools_dir = Path(__file__).parent
    tool_classes: List[Type[BaseTool]] = []

    # Import all modules in the tools directory
    for finder, name, is_pkg in pkgutil.iter_modules([str(tools_dir)]):
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
                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, BaseTool)
                        and attr != BaseTool
                    ):
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
        from .library import manage_libraries  # noqa: F401
        import_time = time.time() - import_start
        logger.info(f"Library tools loaded in {import_time:.2f}s")

        # Book management
        import_start = time.time()
        from .book_management import manage_books  # noqa: F401
        import_time = time.time() - import_start
        logger.info(f"Book management loaded in {import_time:.2f}s")

        # Metadata, tags, comments, series, publishers, authors (core)
        import_start = time.time()
        from .metadata import manage_metadata  # noqa: F401
        from .tags import manage_tags  # noqa: F401
        from .comments import manage_comments  # noqa: F401
        from .series import manage_series  # noqa: F401
        from .publishers import manage_publishers  # noqa: F401
        from .authors import manage_authors  # noqa: F401
        import_time = time.time() - import_start
        logger.info(f"Metadata/tags/authors loaded in {import_time:.2f}s")

        # Files, analysis, library operations, system, import/export, viewer
        import_start = time.time()
        from .files import manage_files  # noqa: F401
        from .analysis import manage_analysis  # noqa: F401
        from .library_operations import manage_library_operations  # noqa: F401
        from .system import manage_system  # noqa: F401
        from .import_export import export_books  # noqa: F401
        from .viewer import manage_viewer  # noqa: F401
        import_time = time.time() - import_start
        logger.info(f"Files/analysis/system loaded in {import_time:.2f}s")

        # OCR
        import_start = time.time()
        from .ocr.calibre_ocr_tool import OCRTool
        OCRTool.register(mcp)
        import_time = time.time() - import_start
        logger.info(f"OCR loaded in {import_time:.2f}s")

        # Beta tools: manage_import, descriptions, user_comments, extended_metadata, times,
        # content_sync, ai_operations, bulk_operations, organization, users, specialized, agentic
        if load_beta:
            import_start = time.time()
            from .import_export.manage_import import manage_import  # noqa: F401
            from .descriptions import manage_descriptions  # noqa: F401
            from .user_comments import manage_user_comments  # noqa: F401
            from .extended_metadata import manage_extended_metadata  # noqa: F401
            from .times import manage_times  # noqa: F401
            from .advanced_features import manage_bulk_operations, manage_content_sync  # noqa: F401
            from .ai import manage_ai_operations  # noqa: F401
            from .organization import manage_organization  # noqa: F401
            from .specialized import manage_specialized  # noqa: F401
            from .user_management import manage_users  # noqa: F401
            from .agentic import register_agentic_tools
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
            registered_tools_count = (
                len(mcp.tools) if isinstance(mcp.tools, dict) else 0
            )
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
