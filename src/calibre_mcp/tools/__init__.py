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
                    if inspect.isclass(attr) and issubclass(attr, BaseTool) and attr != BaseTool:
                        tool_classes.append(attr)

        except Exception as e:
            logger.warning(f"Failed to import tool module {name}: {e}", exc_info=True)

    return tool_classes


# @mcp.tool()
# async def test_tool() -> str:
#     """Simple test tool to verify MCP is working."""
#     return "MCP is working!"

def register_tools(mcp: Any) -> None:
    """
    Register all tools with an MCP server instance.

    This function registers all FastMCP 2.12 compliant tools from categorized modules.

    FastMCP 2.12 auto-registers tools decorated with @mcp.tool() when modules are imported.
    This function only registers BaseTool classes that need explicit registration.

    Args:
        mcp: MCP server instance (FastMCP or similar)
    """
    import_count = 0
    error_count = 0

    # Import all tool modules to trigger auto-registration of @mcp.tool() decorated functions
    # These are already registered when imported (FastMCP 2.13+ behavior)
    import_modules = [
        (".core", "tools", "_core_tools"),
        (".library", "tools", "_library_tools"),
        (".analysis", "tools", "_analysis_tools"),
        (".analysis", "manage_analysis", None),
        (".metadata", "tools", "_metadata_tools"),
        (".files", "tools", "_file_tools"),
        (".specialized", "tools", "_specialized_tools"),
        (".system", "tools", "_system_tools"),
        (".ocr", "tools", "_ocr_tools"),
        (".book_management", "query_books", None),
        (".book_management", "manage_books", None),
        (".authors", "manage_authors", None),
        (".tags", "manage_tags", None),
        (".comments", "manage_comments", None),
        (".viewer", "manage_viewer", None),
        (".specialized", "manage_specialized", None),
        (".metadata", "manage_metadata", None),
        (".files", "manage_files", None),
        (".system", "manage_system", None),
        (".analysis", "analyze_library", None),
        (".advanced_features", "manage_bulk_operations", None),
        (".advanced_features", "manage_content_sync", None),
        (".user_management", "manage_users", None),
        (".import_export", "export_books", None),
    ]
    
    for module_path, attr_name, alias in import_modules:
        try:
            if attr_name == "tools":
                # Import as module
                module = importlib.import_module(f"calibre_mcp.tools{module_path}.{attr_name}", package="calibre_mcp.tools")
                import_count += 1
                logger.debug(f"Imported {module_path}.{attr_name}")
            else:
                # Import specific attribute
                module = importlib.import_module(f"calibre_mcp.tools{module_path}", package="calibre_mcp.tools")
                if hasattr(module, attr_name):
                    getattr(module, attr_name)  # Trigger decorator execution
                    import_count += 1
                    logger.debug(f"Imported {module_path}.{attr_name}")
                else:
                    logger.warning(f"Module {module_path} does not have attribute {attr_name}")
                    error_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"Failed to import {module_path}.{attr_name}: {e}", exc_info=True)
    
    # Only register BaseTool classes (functions with @mcp.tool() are already auto-registered)
    tool_classes: List[Type[BaseTool]] = []

    # Import BaseTool classes that need explicit registration
    try:
        from .ocr.calibre_ocr_tool import OCRTool
        tool_classes = [OCRTool]
        logger.debug("Imported OCRTool")
    except Exception as e:
        logger.error(f"Failed to import OCRTool: {e}", exc_info=True)

    # Register BaseTool classes
    registered_base_tools = 0
    for tool_class in tool_classes:
        try:
            tool_class.register(mcp)
            registered_base_tools += 1
            logger.debug(f"Registered BaseTool: {tool_class.__name__}")
        except Exception as e:
            logger.error(f"Failed to register BaseTool {tool_class.__name__}: {e}", exc_info=True)

    # Get count of registered tools from FastMCP
    try:
        # FastMCP stores tools in mcp._tools or similar
        if hasattr(mcp, '_tools'):
            registered_tools_count = len(mcp._tools)
        elif hasattr(mcp, 'tools'):
            registered_tools_count = len(mcp.tools) if isinstance(mcp.tools, dict) else 0
        else:
            registered_tools_count = "unknown"
    except Exception:
        registered_tools_count = "unknown"

    # Log registration summary
    logger.info(
        f"Tool registration complete: {import_count} modules imported, "
        f"{error_count} errors, {registered_base_tools} BaseTool classes registered, "
        f"{registered_tools_count} total tools registered"
    )

    if error_count > 0:
        logger.warning(f"Tool registration had {error_count} errors - some tools may not be available")

    if registered_tools_count == 0 or registered_tools_count == "unknown":
        logger.error("No tools registered! Check import errors above.")
