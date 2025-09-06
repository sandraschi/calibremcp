"""
Base service class for all MCP services.
"""
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type, Tuple, TypeVar, Union, Callable
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..db.database import Database

T = TypeVar('T', bound=BaseModel)
ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
ResponseSchemaType = TypeVar('ResponseSchemaType', bound=BaseModel)

class ServiceError(Exception):
    """Base exception for service layer errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundError(ServiceError):
    """Raised when a resource is not found."""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status_code=404)

class ValidationError(ServiceError):
    """Raised when validation fails."""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    """
    Base service class providing common CRUD operations and utilities.
    
    This class serves as the foundation for all service classes in the application,
    providing common functionality for data access and manipulation.
    
    Args:
        db: Database service instance
        model: SQLAlchemy model class
        response_schema: Pydantic model for response serialization
    """
    
    def __init__(
        self, 
        db: Database, 
        model: Type[ModelType], 
        response_schema: Type[ResponseSchemaType]
    ):
        """Initialize with database service and model classes."""
        self.db = db
        self.model = model
        self.response_schema = response_schema
    
    def _get_db_session(self) -> Session:
        """Get a database session."""
        return self.db.session
    
    def _commit_or_rollback(self, session: Session) -> None:
        """Commit the session or rollback on error."""
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise ServiceError(f"Database error: {str(e)}", status_code=500) from e
    
    def _paginate_results(
        self, 
        items: List[Any], 
        total: int, 
        page: int = 1, 
        per_page: int = 50
    ) -> Dict[str, Any]:
        """
        Helper method to paginate query results.
        
        Args:
            items: List of items for the current page
            total: Total number of items available
            page: Current page number (1-based)
            per_page: Number of items per page
            
        Returns:
            Dictionary with pagination metadata and items
        """
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
        }
    
    def _process_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate filter parameters.
        
        Args:
            filters: Dictionary of filter parameters
            
        Returns:
            Processed filters with None values removed
        """
        return {k: v for k, v in filters.items() if v is not None}
    
    def _validate_create_data(self, data: CreateSchemaType) -> Dict[str, Any]:
        """
        Validate and prepare data for creation.
        
        Args:
            data: Pydantic model with creation data
            
        Returns:
            Dictionary of validated data
            
        Raises:
            ValidationError: If data validation fails
        """
        try:
            return data.dict(exclude_unset=True)
        except ValidationError as e:
            raise ValidationError(str(e))
    
    def _validate_update_data(
        self, 
        data: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate and prepare data for update.
        
        Args:
            data: Pydantic model or dict with update data
            
        Returns:
            Dictionary of validated data
            
        Raises:
            ValidationError: If data validation fails
        """
        try:
            if isinstance(data, dict):
                return data
            return data.dict(exclude_unset=True)
        except ValidationError as e:
            raise ValidationError(str(e))
    
    def _to_response(
        self, 
        obj: ModelType, 
        schema: Optional[Type[BaseModel]] = None
    ) -> Dict[str, Any]:
        """
        Convert a model instance to a response dictionary.
        
        Args:
            obj: SQLAlchemy model instance
            schema: Optional Pydantic model for custom serialization
            
        Returns:
            Dictionary with serialized data
        """
        if schema is None:
            schema = self.response_schema
        return schema.from_orm(obj).dict()
    
    def _to_response_list(
        self, 
        items: List[ModelType],
        schema: Optional[Type[BaseModel]] = None
    ) -> List[Dict[str, Any]]:
        """
        Convert a list of model instances to a list of response dictionaries.
        
        Args:
            items: List of SQLAlchemy model instances
            schema: Optional Pydantic model for custom serialization
            
        Returns:
            List of dictionaries with serialized data
        """
        return [self._to_response(item, schema) for item in items]
    
    def handle_http_exception(
        self, 
        func: Callable[..., Any]
    ) -> Callable[..., Any]:
        """
        Decorator to handle service exceptions and convert them to HTTP exceptions.
        
        Args:
            func: The function to wrap
            
        Returns:
            Wrapped function with exception handling
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except NotFoundError as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"message": str(e)}
                )
            except ValidationError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"message": str(e)}
                )
            except ServiceError as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail={"message": str(e)}
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"message": f"Internal server error: {str(e)}"}
                )
        return wrapper
    
    def get(self, id: int) -> Dict[str, Any]:
        """
        Retrieve a single item by ID.
        
        Args:
            id: Item ID
            
        Returns:
            Dictionary with item data
            
        Raises:
            NotFoundError: If item is not found
        """
        with self._get_db_session() as session:
            item = session.query(self.model).get(id)
            if not item:
                raise NotFoundError(f"{self.model.__name__} not found")
            return self._to_response(item)
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        **filters: Any
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieve multiple items with optional filtering and pagination.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            **filters: Filter criteria
            
        Returns:
            Tuple of (list of items, total count)
        """
        with self._get_db_session() as session:
            query = session.query(self.model)
            
            # Apply filters
            for key, value in self._process_filters(filters).items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            
            total = query.count()
            items = query.offset(skip).limit(limit).all()
            
            return self._to_response_list(items), total
    
    def create(self, data: CreateSchemaType) -> Dict[str, Any]:
        """
        Create a new item.
        
        Args:
            data: Item data
            
        Returns:
            Dictionary with created item data
        """
        with self._get_db_session() as session:
            item_data = self._validate_create_data(data)
            item = self.model(**item_data)
            session.add(item)
            self._commit_or_rollback(session)
            return self._to_response(item)
    
    def update(
        self, 
        id: int, 
        data: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update an existing item.
        
        Args:
            id: Item ID
            data: Updated data
            
        Returns:
            Dictionary with updated item data
            
        Raises:
            NotFoundError: If item is not found
        """
        with self._get_db_session() as session:
            item = session.query(self.model).get(id)
            if not item:
                raise NotFoundError(f"{self.model.__name__} not found")
            
            update_data = self._validate_update_data(data)
            for key, value in update_data.items():
                setattr(item, key, value)
            
            session.add(item)
            self._commit_or_rollback(session)
            return self._to_response(item)
    
    def delete(self, id: int) -> bool:
        """
        Delete an item by ID.
        
        Args:
            id: Item ID
            
        Returns:
            True if deletion was successful
            
        Raises:
            NotFoundError: If item is not found
        """
        with self._get_db_session() as session:
            item = session.query(self.model).get(id)
            if not item:
                raise NotFoundError(f"{self.model.__name__} not found")
            
            session.delete(item)
            self._commit_or_rollback(session)
            return True
