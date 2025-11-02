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

# Set up logging
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
                    if inspect.isclass(attr) and issubclass(attr, BaseTool) and attr != BaseTool:
                        tool_classes.append(attr)

        except Exception as e:
            logger.warning(f"Failed to import tool module {name}: {e}", exc_info=True)

    return tool_classes


def register_tools(mcp: Any) -> None:
    """
    Register all tools with an MCP server instance.

    This function registers all FastMCP 2.12 compliant tools from categorized modules.

    FastMCP 2.12 auto-registers tools decorated with @mcp.tool() when modules are imported.
    This function only registers BaseTool classes that need explicit registration.

    Args:
        mcp: MCP server instance (FastMCP or similar)
    """
    # Import all tool modules to trigger auto-registration of @mcp.tool() decorated functions
    # These are already registered when imported (FastMCP 2.13+ behavior)
    from .core import tools as _core_tools  # noqa: F401
    from .library import tools as _library_tools  # noqa: F401 - Includes manage_libraries portmanteau
    from .analysis import tools as _analysis_tools  # noqa: F401
    from .metadata import tools as _metadata_tools  # noqa: F401
    from .files import tools as _file_tools  # noqa: F401
    from .specialized import tools as _specialized_tools  # noqa: F401
    from .system import tools as _system_tools  # noqa: F401

    # Explicitly import system_tools to ensure tools are registered
    from .system.system_tools import (  # noqa: F401
        help,
        status,
        health_check,
        tool_help,
        list_tools,
        hello_world,
    )

    # Import export tools to register them
    from .import_export.export_books import (  # noqa: F401
        export_books_csv,
        export_books_json,
        export_books_html,
        export_books_pandoc,
    )
    from .ocr import tools as _ocr_tools  # noqa: F401

    # Import tag tools to register them (CRUD and weeding)
    from .tag_tools import (  # noqa: F401
        list_tags,
        get_tag,
        create_tag,
        update_tag,
        delete_tag,
        find_duplicate_tags,
        merge_tags,
        get_unused_tags,
        delete_unused_tags,
        get_tag_statistics,
    )

    # Import book_management to register portmanteau tools
    from .book_management import query_books, manage_books  # noqa: F401 - Portmanteau tools

    # Only register BaseTool classes (functions with @mcp.tool() are already auto-registered)
    tool_classes: List[Type[BaseTool]] = []

    # Import BaseTool classes that need explicit registration
    from .book_tools import BookTools
    from .author_tools import AuthorTools
    from .viewer_tools import ViewerTools
    from .ocr.calibre_ocr_tool import OCRTool

    tool_classes = [BookTools, AuthorTools, ViewerTools, OCRTool]

    # Register BaseTool classes
    for tool_class in tool_classes:
        tool_class.register(mcp)

    # Log registration
    logger.info(
        f"Registered {len(tool_classes)} BaseTool classes (functions auto-registered on import)"
    )
