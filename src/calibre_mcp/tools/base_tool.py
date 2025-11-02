"""
Base classes for MCP tools.
"""

from typing import Optional, Type, TypeVar, Callable
from pydantic import BaseModel
from fastmcp import FastMCP

T = TypeVar("T", bound=BaseModel)


class BaseTool:
    """Base class for all MCP tools."""

    def __init__(self, mcp: FastMCP):
        """Initialize with a FastMCP instance."""
        self.mcp = mcp
        # Use singleton service instances (already initialized with DatabaseService)
        from ..services.book_service import book_service
        from ..services.author_service import author_service
        from ..services.library_service import library_service

        self.book_service = book_service
        self.author_service = author_service
        self.library_service = library_service

    @classmethod
    def register(cls, mcp: FastMCP) -> None:
        """Register the tool with the MCP instance."""
        tool = cls(mcp)
        tool._register_methods()

    def _register_methods(self) -> None:
        """Register all methods decorated with @mcp_tool."""
        for attr_name in dir(self):
            if attr_name.startswith("_"):
                continue

            attr = getattr(self, attr_name)
            if hasattr(attr, "_mcp_tool"):
                self._register_method(attr_name, attr)

    def _register_method(self, name: str, method: Callable) -> None:
        """Register a single method as an MCP tool."""
        tool_info = getattr(method, "_mcp_tool", {})

        # FastMCP 2.12 only accepts name and description
        # Type inference is done from function signature
        tool_name = tool_info.get("name", name)
        tool_description = tool_info.get("description", method.__doc__ or "")

        import inspect

        is_async = inspect.iscoroutinefunction(method)

        # Get method signature (skip 'self')
        sig = inspect.signature(method)
        params = list(sig.parameters.values())[1:]  # Skip 'self'

        # Create wrapper function with same signature as method
        # FastMCP requires explicit parameters matching the method signature
        param_defs = []
        param_names = []
        for param in params:
            param_names.append(param.name)
            # Build parameter definition string
            param_str = param.name
            if param.annotation != inspect.Parameter.empty:
                # Convert annotation to string properly
                ann_str = str(param.annotation)
                # Handle forward references and complex types
                if ann_str.startswith("<class"):
                    # Extract class name from <class 'type'>
                    import re

                    match = re.search(r"'([^']+)'", ann_str)
                    if match:
                        ann_str = match.group(1)
                    else:
                        ann_str = "Any"
                param_str += f": {ann_str}"
            if param.default != inspect.Parameter.empty:
                param_str += f" = {repr(param.default)}"
            param_defs.append(param_str)

        # Create function code dynamically
        params_str = ", ".join(param_defs)

        # Create wrapper function without Pydantic validation (FastMCP handles validation)
        exec_code = f"""
async def wrapper({params_str}):
    # Build kwargs dict
    call_kwargs = {{{", ".join([f'"{name}": {name}' for name in param_names])}}}
    
    # Call method (handle both sync and async)
    if is_async:
        return await method(self, **call_kwargs)
    else:
        return method(self, **call_kwargs)
"""

        # Execute in local scope - capture variables needed in closure
        import typing

        local_vars = {
            "method": method,
            "self": self,
            "is_async": is_async,
            "typing": typing,
        }
        exec_globals = {**globals(), "typing": typing}
        exec(exec_code, exec_globals, local_vars)
        wrapper = local_vars["wrapper"]

        # Register with FastMCP - wrapper already has correct signature
        # FastMCP 2.12 infers name and description from function signature and docstring
        # Set docstring on wrapper so FastMCP can infer description
        wrapper.__name__ = tool_name
        wrapper.__doc__ = tool_description
        self.mcp.tool()(wrapper)


def mcp_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    input_model: Optional[Type[BaseModel]] = None,
    output_model: Optional[Type[BaseModel]] = None,
):
    """
    Decorator to mark a method as an MCP tool.

    Args:
        name: Tool name (defaults to method name)
        description: Tool description (defaults to method docstring)
        input_model: Pydantic model for input validation
        output_model: Pydantic model for output validation
    """

    def decorator(method):
        method._mcp_tool = {
            "name": name or method.__name__,
            "description": description or method.__doc__ or "",
            "input_model": input_model,
            "output_model": output_model,
        }
        return method

    return decorator
