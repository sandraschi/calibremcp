"""
Tools package for Calibre MCP server.

This package contains all the tools available in the Calibre MCP server,
organized by functionality into submodules.
"""
from typing import Dict, Any, Callable, Optional, TypeVar, cast, List, Type
from functools import wraps
import importlib
import pkgutil
import inspect
import sys
import os
from pathlib import Path

# Type variable for tool functions
T = TypeVar('T', bound=Callable[..., Any])

# Global tool registry
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}

# Base directory for Calibre libraries
CALIBRE_BASE_DIR = Path("L:/Multimedia Files/Written Word")

def tool(
    name: str,
    description: str,
    parameters: Optional[Dict[str, Any]] = None,
    **kwargs
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
            'name': name,
            'description': description,
            'parameters': parameters or {},
            'func': func,
            **kwargs
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
            'name': tool_info['name'],
            'description': tool_info['description'],
            'parameters': tool_info.get('parameters', {}),
        }
        for tool_info in TOOL_REGISTRY.values()
    ]

def register_tools(mcp: Any) -> None:
    """
    Register all tools with an MCP server instance.
    
    This function imports all tool modules to ensure they're registered
    and then registers each tool with the MCP server.
    
    Args:
        mcp: MCP server instance (FastMCP or similar)
    """
    # Import all tool modules to ensure they're registered
    tools_dir = os.path.dirname(__file__)
    for _, module_name, _ in pkgutil.iter_modules([tools_dir]):
        if module_name != "__init__":
            try:
                module = importlib.import_module(f"calibre_mcp.tools.{module_name}")
                
                # Register tools from the module's tools list
                if hasattr(module, 'tools'):
                    for tool in module.tools:
                        mcp.tool()(tool)
            except Exception as e:
                import traceback
                print(f"Error loading module {module_name}: {e}")
                traceback.print_exc()
    
    # Register each tool with the MCP server
    for tool_name, tool_info in TOOL_REGISTRY.items():
        tool_func = tool_info['func']
        
        # Get the function's docstring for better documentation
        doc = inspect.getdoc(tool_func) or ''
        
        # Register the tool with the MCP server
        mcp.tool(
            name=tool_name,
            description=tool_info['description'],
            parameters=tool_info.get('parameters', {}),
            **{k: v for k, v in tool_info.items() 
               if k not in ('name', 'description', 'parameters', 'func')}
        )(tool_func)
        
        # Log the registered tool
        print(f"Registered tool: {tool_name} - {tool_info['description']}")
