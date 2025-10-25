"""
Base classes for MCP tools.
"""
from typing import Optional, Type, TypeVar, Callable
from pydantic import BaseModel
from fastmcp import FastMCP
from ..services import BookService, AuthorService, LibraryService

T = TypeVar('T', bound=BaseModel)

class BaseTool:
    """Base class for all MCP tools."""
    
    def __init__(self, mcp: FastMCP):
        """Initialize with a FastMCP instance."""
        self.mcp = mcp
        # Initialize services with connection manager
        self.book_service = BookService()
        self.author_service = AuthorService()
        self.library_service = LibraryService()
    
    @classmethod
    def register(cls, mcp: FastMCP) -> None:
        """Register the tool with the MCP instance."""
        tool = cls(mcp)
        tool._register_methods()
    
    def _register_methods(self) -> None:
        """Register all methods decorated with @mcp_tool."""
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue
                
            attr = getattr(self, attr_name)
            if hasattr(attr, '_mcp_tool'):
                self._register_method(attr_name, attr)
    
    def _register_method(self, name: str, method: Callable) -> None:
        """Register a single method as an MCP tool."""
        tool_info = getattr(method, '_mcp_tool', {})
        
        @self.mcp.tool(
            name=tool_info.get('name', name),
            description=tool_info.get('description', method.__doc__ or ''),
            input_model=tool_info.get('input_model'),
            output_model=tool_info.get('output_model')
        )
        async def wrapper(**kwargs):
            return method(self, **kwargs)

def mcp_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    input_model: Optional[Type[BaseModel]] = None,
    output_model: Optional[Type[BaseModel]] = None
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
            'name': name or method.__name__,
            'description': description or method.__doc__ or '',
            'input_model': input_model,
            'output_model': output_model
        }
        return method
    return decorator
