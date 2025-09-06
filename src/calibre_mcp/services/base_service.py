"""
Base service class for all MCP services.
"""
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseService:
    """Base service class providing common functionality for all services."""
    
    def __init__(self, db):
        """Initialize with a database service instance."""
        self.db = db
    
    def _paginate_results(
        self, 
        items: List[Any], 
        total: int, 
        page: int = 1, 
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Helper method to paginate query results."""
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
        }
    
    def _process_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate filter parameters."""
        processed = {}
        for key, value in filters.items():
            if value is not None:
                processed[key] = value
        return processed
