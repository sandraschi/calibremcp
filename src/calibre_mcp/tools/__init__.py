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
    Register all tools with an MCP server instance.

    This function registers all FastMCP compliant tools.
    Explicit imports are used instead of dynamic discovery to ensure reliability.

    Args:
        mcp: MCP server instance (FastMCP)
    """
    import_count = 0
    error_count = 0

    # 1. CORE TOOLS
    try:
        from .core import tools as _core_tools

        import_count += 1
    except Exception as e:
        logger.error(f"Failed to load core tools: {e}")
        error_count += 1

    # 2. LIBRARY MANAGEMENT
    try:
        from .library import tools as _library_tools

        import_count += 1
    except Exception as e:
        logger.error(f"Failed to load library tools: {e}")
        error_count += 1

    # 3. BOOK MANAGEMENT
    try:
        from .book_management import query_books, manage_books

        import_count += 2
    except Exception as e:
        logger.error(f"Failed to load book management tools: {e}")
        error_count += 1

    # 4. METADATA & TAGS
    try:
        from .metadata import tools as _metadata_tools, manage_metadata
        from .tags import manage_tags
        from .comments import manage_comments

        import_count += 4
    except Exception as e:
        logger.error(f"Failed to load metadata/tags tools: {e}")
        error_count += 1

    # 5. AUTHORS
    try:
        from .authors import manage_authors

        import_count += 1
    except Exception as e:
        logger.error(f"Failed to load author tools: {e}")
        error_count += 1

    # 6. FILE MANAGEMENT
    try:
        from .files import tools as _file_tools, manage_files

        import_count += 2
    except Exception as e:
        logger.error(f"Failed to load file tools: {e}")
        error_count += 1

    # 7. ANALYSIS & ADVANCED FEATURES
    try:
        from .analysis import tools as _analysis_tools, manage_analysis, analyze_library
        from .advanced_features import manage_bulk_operations, manage_content_sync

        import_count += 5
    except Exception as e:
        logger.error(f"Failed to load analysis/advanced tools: {e}")
        error_count += 1

    # 8. SYSTEM & SPECIALIZED
    try:
        from .system import tools as _system_tools, manage_system
        from .specialized import tools as _specialized_tools, manage_specialized
        from .user_management import manage_users
        from .import_export import export_books
        from .viewer import manage_viewer

        import_count += 7
    except Exception as e:
        logger.error(f"Failed to load system/specialized tools: {e}")
        error_count += 1

    # 9. OCR & BASE TOOLS
    try:
        from .ocr import tools as _ocr_tools
        from .ocr.calibre_ocr_tool import OCRTool

        OCRTool.register(mcp)
        import_count += 2
    except Exception as e:
        logger.error(f"Failed to load/register OCR tools: {e}")
        error_count += 1

    # 10. AGENTIC WORKFLOW (SEP-1577)
    try:
        # Import the module - @mcp.tool() decorators auto-register
        from . import agentic_workflow
        import_count += 1
        logger.info("Agentic library workflow tool registered (SEP-1577)")
    except Exception as e:
        logger.error(f"Failed to load agentic workflow tool: {e}")
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

    logger.info(
        f"Tool registration complete: {import_count} modules/tools processed, "
        f"{error_count} errors, "
        f"{registered_tools_count} total tools registered"
    )
