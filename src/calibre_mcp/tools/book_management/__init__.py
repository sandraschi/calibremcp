"""
Book Management Tools

This package contains tools for managing books in the Calibre library.
"""
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging
from typing import List, Type

from ..tool import Tool

# Import all tool modules to register them
from .add_book import add_book  # noqa: F401
from .get_book import get_book  # noqa: F401
from .update_book import update_book  # noqa: F401
from .delete_book import delete_book  # noqa: F401

logger = logging.getLogger(__name__)

# List of all tool functions in this package
__all__ = [
    'add_book',
    'get_book',
    'update_book',
    'delete_book'
]

def get_tools() -> List[Type[Tool]]:
    """
    Get all tools defined in this package.
    
    Returns:
        List of Tool classes
    """
    tools = []
    
    # Get all tool functions from this package
    for tool_name in __all__:
        try:
            tool = globals()[tool_name]
            if hasattr(tool, '_tool_metadata'):
                tools.append(tool)
        except Exception as e:
            logger.warning(f"Failed to load tool {tool_name}: {e}")
    
    return tools

# Re-export models for convenience
from ...models import Book, BookFormat, BookStatus  # noqa: F401
