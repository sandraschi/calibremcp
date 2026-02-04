"""
Tools package for Calibre MCP server.

This package contains all the tools available in the Calibre MCP server,
organized by functionality into submodules. Tools are automatically discovered
and loaded from all subdirectories.
"""

import importlib
import inspect
import logging
import pkgutil
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for tool functions
T = TypeVar("T", bound=Callable[..., Any])

# Global tool registry
TOOL_REGISTRY: dict[str, dict[str, Any]] = {}

# Base directory for Calibre libraries
CALIBRE_BASE_DIR = Path("L:/Multimedia Files/Written Word")

# Set of directories to ignore when discovering tools
IGNORE_DIRS = {"__pycache__", ".mypy_cache", ".pytest_cache"}

# Import the base tool class (after type definitions)
from .base_tool import BaseTool, mcp_tool  # noqa: E402, F401


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
    # Import advanced features portmanteau tools
    from .advanced_features import (
        manage_bulk_operations,  # noqa: F401 - Portmanteau tool
        manage_content_sync,  # noqa: F401 - Portmanteau tool
    )

    # Import analysis portmanteau tools
    from .analysis import (
        analyze_library,  # noqa: F401 - Portmanteau tool
        manage_analysis,  # noqa: F401 - Portmanteau tool
    )
    from .analysis import tools as _analysis_tools  # noqa: F401

    # Import authors portmanteau tool
    from .authors import manage_authors  # noqa: F401 - Portmanteau tool

    # DEPRECATED: Individual tag tools removed - use manage_tags portmanteau tool instead
    # from .tag_tools import (
    #     list_tags,
    #     get_tag,
    #     create_tag,
    #     update_tag,
    #     delete_tag,
    #     find_duplicate_tags,
    #     merge_tags,
    #     get_unused_tags,
    #     delete_unused_tags,
    # )
    # Import book_management to register portmanteau tools
    from .book_management import manage_books, query_books  # noqa: F401 - Portmanteau tools

    # Import comments portmanteau tool
    from .comments import manage_comments  # noqa: F401 - Portmanteau tool
    from .core import tools as _core_tools  # noqa: F401

    # Import files portmanteau tool
    from .files import manage_files  # noqa: F401 - Portmanteau tool
    from .files import tools as _file_tools  # noqa: F401

    # Import export portmanteau tool
    from .import_export import export_books  # noqa: F401 - Portmanteau tool
    from .library import (
        tools as _library_tools,  # noqa: F401 - Includes manage_libraries portmanteau
    )

    # Import metadata portmanteau tool
    from .metadata import manage_metadata  # noqa: F401 - Portmanteau tool
    from .metadata import tools as _metadata_tools  # noqa: F401

    # NOTE: Individual system tools (help, status, etc.) are deprecated
    # They are now accessed via manage_system portmanteau tool
    # Helper functions (help_helper, status_helper, etc.) are imported by manage_system
    # No need to import them here - they don't have @mcp.tool() decorators
    # NOTE: Individual export tools (export_books_csv, etc.) are deprecated
    # They are now accessed via export_books portmanteau tool
    # Helper functions are imported by export_books_portmanteau
    # No need to import them here - they don't have @mcp.tool() decorators
    from .ocr import tools as _ocr_tools  # noqa: F401

    # Import specialized portmanteau tool
    from .specialized import manage_specialized  # noqa: F401 - Portmanteau tool
    from .specialized import tools as _specialized_tools  # noqa: F401

    # Import system portmanteau tool
    from .system import manage_system  # noqa: F401 - Portmanteau tool
    from .system import tools as _system_tools  # noqa: F401

    # Import tags portmanteau tool
    from .tags import manage_tags  # noqa: F401 - Portmanteau tool

    # Import user management portmanteau tool
    from .user_management import manage_users  # noqa: F401 - Portmanteau tool

    # Import viewer portmanteau tool
    from .viewer import manage_viewer  # noqa: F401 - Portmanteau tool

    # Only register BaseTool classes (functions with @mcp.tool() are already auto-registered)
    tool_classes: list[type[BaseTool]] = []

    # Import BaseTool classes that need explicit registration
    # BookTools removed - use manage_books portmanteau tool instead
    # ViewerTools removed - use manage_viewer portmanteau tool instead
    # AuthorTools removed - use manage_authors portmanteau tool instead
    from .ocr.calibre_ocr_tool import OCRTool

    tool_classes = [OCRTool]
    # Only OCRTool remains - specialized tool that doesn't fit portmanteau pattern

    # Register BaseTool classes
    for tool_class in tool_classes:
        tool_class.register(mcp)

    # Log registration
    logger.info(
        f"Registered {len(tool_classes)} BaseTool classes (functions auto-registered on import)"
    )
