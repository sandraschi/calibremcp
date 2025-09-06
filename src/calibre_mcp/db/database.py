"""
Database service for managing SQLAlchemy connections and sessions.
"""
import os
from pathlib import Path
from typing import Optional, Type, TypeVar, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.engine import Engine

from .models import Base
from .repositories import BookRepository, AuthorRepository, LibraryRepository

T = TypeVar('T')

class DatabaseService:
    """Service for managing database connections and sessions."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._engine = None
        self._session_factory = None
        self._repositories = {}
        self._initialized = True
    
    def initialize(self, db_url: str, echo: bool = False) -> None:
        """Initialize the database service with a database URL."""
        if self._engine is not None:
            return
            
        # Convert path to SQLite URL if it's a file path
        if '://' not in db_url and os.path.exists(db_url):
            db_url = f"sqlite:///{os.path.abspath(db_url).replace('\\\\', '/')}"
        
        self._engine = create_engine(
            db_url,
            echo=echo,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600
        )
        
        # Create session factory
        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
        )
        
        # Initialize repositories
        self._repositories = {
            'books': BookRepository(self),
            'authors': AuthorRepository(self),
            'library': LibraryRepository(self)
        }
        
        # Enable WAL mode for SQLite
        if "sqlite" in db_url:
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=-2000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
    
    @property
    def session(self) -> Session:
        """Get a database session."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._session_factory()
    
    @contextmanager
    def session_scope(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
            
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_repository(self, name: str) -> Any:
        """Get a repository by name."""
        if name not in self._repositories:
            raise ValueError(f"Repository '{name}' not found.")
        return self._repositories[name]
    
    def create_tables(self) -> None:
        """Create all database tables."""
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        Base.metadata.create_all(self._engine)
    
    def close(self) -> None:
        """Close the database connection and clean up resources."""
        if self._session_factory:
            self._session_factory.remove()
            self._session_factory = None
        
        if self._engine:
            self._engine.dispose()
            self._engine = None
            
        self._repositories = {}


# Global instance
db = DatabaseService()


def init_database(db_path: str, echo: bool = False) -> None:
    """
    Initialize the global database instance.
    
    Args:
        db_path: Path to the Calibre metadata.db file or SQLAlchemy connection URL
        echo: If True, log all SQL statements
    """
    db.initialize(db_path, echo=echo)


def close_database() -> None:
    """Close the global database connection."""
    db.close()


def get_database() -> DatabaseService:
    """Get the global database instance."""
    if db._engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return db
