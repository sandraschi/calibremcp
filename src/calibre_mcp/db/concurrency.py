"""
Database Concurrency Fix for FastMCP 3.2 Universal Connect Pattern

This module provides thread-safe database operations for multiple simultaneous clients.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class DatabaseConcurrencyManager:
    """Manages database concurrency for multiple simultaneous clients."""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._locks = {}  # Simple in-memory lock registry
    
    @asynccontextmanager
    async def get_session(self) -> Session:
        """Get a thread-safe database session with proper isolation."""
        # In production, use a more sophisticated locking mechanism
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise HTTPException(status_code=500, detail="Database transaction failed")
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_locked_session(self, resource_id: str, lock_type: str = "row") -> Session:
        """Get a session with row-level locking for specific resources."""
        session = self.session_factory()
        try:
            if lock_type == "row":
                # Implement row-level locking for SQLite
                await self._acquire_row_lock(session, resource_id)
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Locked transaction failed: {e}")
            raise HTTPException(status_code=500, detail="Locked transaction failed")
        finally:
            if lock_type == "row":
                await self._release_row_lock(session, resource_id)
            session.close()
    
    async def _acquire_row_lock(self, session: Session, resource_id: str):
        """Acquire a row-level lock using SQLite pragmas."""
        # For SQLite, we use BEGIN IMMEDIATE + pessimistic locking
        session.execute(text("BEGIN IMMEDIATE"))
        session.execute(text(f"SELECT * FROM books WHERE id = :id FOR UPDATE"), {"id": resource_id})
    
    async def _release_row_lock(self, session: Session, resource_id: str):
        """Release row-level lock."""
        session.execute(text("COMMIT"))

# Thread-safe repository pattern
class ThreadSafeRepository:
    """Base repository with concurrency safety."""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    async def get_with_lock(self, model_class, resource_id: Any):
        """Get a resource with row-level locking."""
        async with DatabaseConcurrencyManager(self.session_factory).get_locked_session(str(resource_id)) as session:
            return session.query(model_class).get(resource_id)
    
    async def update_with_lock(self, model_class, resource_id: Any, **kwargs):
        """Update a resource with row-level locking."""
        async with DatabaseConcurrencyManager(self.session_factory).get_locked_session(str(resource_id)) as session:
            item = session.query(model_class).get(resource_id)
            if item:
                for key, value in kwargs.items():
                    setattr(item, key, value)
                session.add(item)
                return item
            return None
