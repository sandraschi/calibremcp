"""
Base repository class with common CRUD operations.
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""

    def __init__(self, db, model: type[T]):
        """Initialize with database service and model class."""
        self._db = db
        self.model = model

    @property
    def session(self) -> Session:
        """Get a database session."""
        return self._db.session

    def get(self, id: int) -> T | None:
        """Get a single record by ID."""
        with self._db.session_scope() as session:
            return session.query(self.model).get(id)

    def get_by_ids(self, ids: list[int]) -> list[T]:
        """Get multiple records by their IDs."""
        if not ids:
            return []

        with self._db.session_scope() as session:
            return session.query(self.model).filter(self.model.id.in_(ids)).all()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Get all records with pagination."""
        with self._db.session_scope() as session:
            return session.query(self.model).offset(offset).limit(limit).all()

    def find(self, **filters) -> list[T]:
        """Find records matching the given filters."""
        with self._db.session_scope() as session:
            query = session.query(self.model)
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.all()

    def find_one(self, **filters) -> T | None:
        """Find a single record matching the given filters."""
        with self._db.session_scope() as session:
            query = session.query(self.model)
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.first()

    def create(self, data: dict[str, Any] | T, commit: bool = True) -> T:
        """Create a new record."""
        if isinstance(data, dict):
            obj = self.model(**data)
        else:
            obj = data

        with self._db.session_scope() as session:
            session.add(obj)
            if commit:
                session.commit()
                session.refresh(obj)
            return obj

    def update(self, id: int, data: dict[str, Any], commit: bool = True) -> T | None:
        """Update a record by ID."""
        with self._db.session_scope() as session:
            obj = session.query(self.model).get(id)
            if not obj:
                return None

            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            if commit:
                session.commit()
                session.refresh(obj)

            return obj

    def delete(self, id: int, commit: bool = True) -> bool:
        """Delete a record by ID."""
        with self._db.session_scope() as session:
            obj = session.query(self.model).get(id)
            if not obj:
                return False

            session.delete(obj)
            if commit:
                session.commit()

            return True

    def count(self, **filters) -> int:
        """Count records matching the given filters."""
        with self._db.session_scope() as session:
            query = session.query(func.count(self.model.id))
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.scalar()

    def exists(self, **filters) -> bool:
        """Check if a record exists with the given filters."""
        return self.count(**filters) > 0

    def search(self, query: str, fields: list[str], limit: int = 50, offset: int = 0) -> list[T]:
        """
        Search for records where any of the specified fields contain the query.

        Args:
            query: Search term
            fields: List of field names to search in
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)

        Returns:
            List of matching records
        """
        if not query or not fields:
            return []

        search_terms = [f"%{term}%" for term in query.split() if term.strip()]
        if not search_terms:
            return []

        with self._db.session_scope() as session:
            conditions = []
            for field in fields:
                if hasattr(self.model, field):
                    field_expr = getattr(self.model, field)
                    for term in search_terms:
                        conditions.append(field_expr.ilike(term))

            if not conditions:
                return []

            return (
                session.query(self.model).filter(or_(*conditions)).offset(offset).limit(limit).all()
            )
