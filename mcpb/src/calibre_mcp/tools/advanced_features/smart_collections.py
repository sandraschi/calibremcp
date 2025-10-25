"""Smart collections and dynamic grouping for CalibreMCP."""
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
import re

from fastmcp import MCPTool

# Models
class CollectionRule(BaseModel):
    """Rule for dynamic collection membership."""
    field: str
    operator: str  # '==', '!=', '>', '<', '>=', '<=', 'contains', 'not_contains', 'regex', 'in', 'not_in'
    value: Any
    
    @validator('operator')
    def validate_operator(cls, v):
        valid_operators = ['==', '!=', '>', '<', '>=', '<=', 'contains', 'not_contains', 'regex', 'in', 'not_in']
        if v not in valid_operators:
            raise ValueError(f"Invalid operator. Must be one of {valid_operators}")
        return v

class SmartCollection(BaseModel):
    """Smart collection definition."""
    id: str
    name: str
    description: Optional[str] = None
    rules: List[Union[Dict, CollectionRule]]
    match_all: bool = True  # If False, use OR logic instead of AND
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def to_dict(self):
        """Convert to dictionary with proper datetime handling."""
        data = self.dict()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

# Main tool
class SmartCollectionsTool(MCPTool):
    """Manage and query smart collections."""
    
    name = "smart_collections"
    description = "Create and manage smart collections"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._collections = {}  # In-memory storage (replace with database in production)
    
    async def _run(self, action: str, **kwargs) -> Dict:
        """Route to the appropriate collection handler."""
        handler = getattr(self, f"collection_{action}", None)
        if not handler:
            return {"error": f"Unknown collection action: {action}", "success": False}
        
        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}
    
    # CRUD Operations
    async def collection_create(self, collection_data: Dict) -> Dict:
        """Create a new smart collection."""
        # Convert rules to CollectionRule objects
        rules = []
        for rule in collection_data.get('rules', []):
            if not isinstance(rule, CollectionRule):
                rule = CollectionRule(**rule)
            rules.append(rule)
        
        collection_data['rules'] = rules
        collection = SmartCollection(**collection_data)
        
        # Generate ID if not provided
        if not collection.id:
            collection.id = f"col_{len(self._collections) + 1}"
        
        self._collections[collection.id] = collection
        return {"success": True, "collection": collection.dict()}
    
    async def collection_get(self, collection_id: str) -> Dict:
        """Get a smart collection by ID."""
        if collection_id not in self._collections:
            return {"error": f"Collection {collection_id} not found", "success": False}
        
        return {"success": True, "collection": self._collections[collection_id].to_dict()}
    
    async def collection_update(self, collection_id: str, updates: Dict) -> Dict:
        """Update a smart collection."""
        if collection_id not in self._collections:
            return {"error": f"Collection {collection_id} not found", "success": False}
        
        collection = self._collections[collection_id]
        
        # Update fields
        for field, value in updates.items():
            if hasattr(collection, field) and field not in ['id', 'created_at']:
                if field == 'rules':
                    # Convert rules to CollectionRule objects
                    rules = []
                    for rule in value:
                        if not isinstance(rule, CollectionRule):
                            rule = CollectionRule(**rule)
                        rules.append(rule)
                    setattr(collection, field, rules)
                else:
                    setattr(collection, field, value)
        
        # Update timestamp
        collection.updated_at = datetime.utcnow()
        
        return {"success": True, "collection": collection.to_dict()}
    
    async def collection_delete(self, collection_id: str) -> Dict:
        """Delete a smart collection."""
        if collection_id not in self._collections:
            return {"error": f"Collection {collection_id} not found", "success": False}
        
        del self._collections[collection_id]
        return {"success": True}
    
    async def collection_list(self) -> Dict:
        """List all smart collections."""
        return {
            "success": True,
            "collections": [col.to_dict() for col in self._collections.values()]
        }
    
    # Query Operations
    async def collection_query(self, collection_id: str, 
                             library_path: Optional[str] = None,
                             limit: int = 100,
                             offset: int = 0) -> Dict:
        """Query books that match a smart collection's rules."""
        if collection_id not in self._collections:
            return {"error": f"Collection {collection_id} not found", "success": False}
        
        collection = self._collections[collection_id]
        
        # Get all books from the library
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        storage = LocalStorage(library_path)
        all_books = await storage.get_all_books()
        
        # Filter books based on collection rules
        matching_books = []
        for book in all_books:
            if self._matches_rules(book, collection.rules, collection.match_all):
                matching_books.append(book)
        
        # Apply pagination
        total = len(matching_books)
        paginated = matching_books[offset:offset+limit]
        
        return {
            "success": True,
            "collection_id": collection_id,
            "total_matches": total,
            "books": [book.dict() for book in paginated],
            "offset": offset,
            "limit": limit
        }
    
    # Helper Methods
    def _matches_rules(self, book, rules: List[CollectionRule], match_all: bool = True) -> bool:
        """Check if a book matches all the rules of a collection."""
        if not rules:
            return True
        
        results = []
        for rule in rules:
            if not isinstance(rule, CollectionRule):
                rule = CollectionRule(**rule)
            
            field_value = getattr(book, rule.field, None)
            results.append(self._evaluate_rule(field_value, rule.operator, rule.value))
        
        if match_all:
            return all(results)
        return any(results)
    
    def _evaluate_rule(self, field_value, operator: str, rule_value) -> bool:
        """Evaluate a single rule against a field value."""
        try:
            if operator == '==':
                return field_value == rule_value
            elif operator == '!=':
                return field_value != rule_value
            elif operator == '>':
                return field_value > rule_value
            elif operator == '<':
                return field_value < rule_value
            elif operator == '>=':
                return field_value >= rule_value
            elif operator == '<=':
                return field_value <= rule_value
            elif operator == 'contains':
                if field_value is None:
                    return False
                if isinstance(field_value, str):
                    return rule_value in field_value
                if isinstance(field_value, (list, set)):
                    return rule_value in field_value
                return False
            elif operator == 'not_contains':
                if field_value is None:
                    return True
                if isinstance(field_value, str):
                    return rule_value not in field_value
                if isinstance(field_value, (list, set)):
                    return rule_value not in field_value
                return True
            elif operator == 'regex':
                if not field_value:
                    return False
                return bool(re.search(rule_value, str(field_value), re.IGNORECASE))
            elif operator == 'in':
                if not field_value:
                    return False
                if isinstance(rule_value, (list, set, tuple)):
                    return field_value in rule_value
                return str(field_value) == str(rule_value)
            elif operator == 'not_in':
                if not field_value:
                    return True
                if isinstance(rule_value, (list, set, tuple)):
                    return field_value not in rule_value
                return str(field_value) != str(rule_value)
            return False
        except Exception:
            return False
    
    # Special Collection Types
    async def collection_create_series(self, name: str, series_name: str, **kwargs) -> Dict:
        """Create a collection for a book series."""
        collection = {
            'name': name,
            'description': f"Books in the {series_name} series",
            'rules': [
                {'field': 'series', 'operator': '==', 'value': series_name}
            ],
            **kwargs
        }
        return await self.collection_create(collection)
    
    async def collection_create_recently_added(self, name: str = "Recently Added", days: int = 30, **kwargs) -> Dict:
        """Create a collection for recently added books."""
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        collection = {
            'name': name,
            'description': f"Books added in the last {days} days",
            'rules': [
                {'field': 'added_at', 'operator': '>=', 'value': cutoff_date}
            ],
            'icon': 'clock',
            **kwargs
        }
        return await self.collection_create(collection)
    
    async def collection_create_unread(self, name: str = "Unread", **kwargs) -> Dict:
        """Create a collection for unread books."""
        collection = {
            'name': name,
            'description': "Books you haven't read yet",
            'rules': [
                {'field': 'read_status', 'operator': '==', 'value': 'unread'}
            ],
            'icon': 'book',
            **kwargs
        }
        return await self.collection_create(collection)
    
    async def collection_create_ai_recommended(self, name: str = "AI Recommendations", **kwargs) -> Dict:
        """Create a collection with AI-recommended books."""
        # This would integrate with the AI enhancements tool
        # For now, it's a placeholder that returns an empty collection
        collection = {
            'name': name,
            'description': "Books recommended for you by AI",
            'rules': [],  # Would be populated by AI
            'icon': 'stars',
            **kwargs
        }
        return await self.collection_create(collection)
