"""
Database service for managing SQLAlchemy connections and sessions.
"""

import logging
import os
from contextlib import contextmanager
from typing import Any, TypeVar

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from .models import Base
from .repositories import AuthorRepository, BookRepository, LibraryRepository

T = TypeVar("T")

# Get logger once at module level (stderr logging is OK for MCP servers)
logger = logging.getLogger("calibremcp.db.database")


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
        self._current_db_path = None

    def initialize(self, db_url: str, echo: bool = False, force: bool = False) -> None:
        """
        Initialize the database service with a database URL.

        Args:
            db_url: Path to database or SQLAlchemy connection URL
            echo: If True, log all SQL statements
            force: If True, close existing connection and re-initialize (for library switching)
        """
        if not db_url:
            raise ValueError("Database URL cannot be None or empty")

        # If already initialized and not forcing, check if it's the same path
        if self._engine is not None and not force:
            if self.is_initialized_with(db_url):
                return
            else:
                logger.warning(
                    "Database initialized with different path. Use force=True to switch.",
                    extra={"service": "database", "action": "skip_reinit_different_path"},
                )
                return

        # If forcing, close existing connection
        if force and self._engine is not None:
            self.close()

        # Convert path to SQLite URL if it's a file path
        try:
            if "://" not in db_url and os.path.exists(db_url):
                abs_path = os.path.abspath(db_url).replace("\\\\", "/")
                db_url = f"sqlite:///{abs_path}"
                self._current_db_path = abs_path
            else:
                # Extract path from SQLite URL if it's already a URL
                if db_url.startswith("sqlite:///"):
                    path_part = db_url.replace("sqlite:///", "").replace("/", os.sep)
                    self._current_db_path = os.path.abspath(path_part).replace("\\\\", "/")
                else:
                    # Store original URL if it's not a file path
                    self._current_db_path = db_url
        except (OSError, ValueError, TypeError) as e:
            logger.error(
                f"Failed to process database URL: {e}",
                extra={
                    "service": "database",
                    "action": "process_db_url_failed",
                    "db_url": str(db_url),
                    "error": str(e),
                },
            )
            raise ValueError(f"Invalid database URL: {db_url}") from e

        self._engine = create_engine(
            db_url,
            echo=echo,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
        )

        # Create session factory
        self._session_factory = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
        )

        # Initialize repositories
        self._repositories = {
            "books": BookRepository(self),
            "authors": AuthorRepository(self),
            "library": LibraryRepository(self),
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
        self._current_db_path = None

    def get_current_path(self) -> str | None:
        """Get the current database path, if initialized."""
        return self._current_db_path

    def is_initialized_with(self, db_path: str) -> bool:
        """Check if database is initialized with the given path."""
        if not self._current_db_path or not self._engine:
            return False
        return self._current_db_path == db_path


# Global instance
db = DatabaseService()


def init_database(db_path: str, echo: bool = False, force: bool = False) -> None:
    """
    Initialize the global database instance.

    Args:
        db_path: Path to the Calibre metadata.db file or SQLAlchemy connection URL
        echo: If True, log all SQL statements
        force: If True, close existing connection and re-initialize (for library switching)
    """
    db.initialize(db_path, echo=echo, force=force)


def close_database() -> None:
    """Close the global database connection."""
    db.close()


def get_database() -> DatabaseService:
    """Get the global database instance."""
    if db._engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return db
