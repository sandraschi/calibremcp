"""
Database connection and base repository implementation for CalibreMCP.
"""

from pathlib import Path
import sqlite3
from typing import Dict, List, Optional, TypeVar, Generic
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DatabaseError(Exception):
    """Base exception for database-related errors."""

    pass


class ConnectionManager:
    """Manages database connections and provides context management."""

    def __init__(self, db_path: str):
        """Initialize with path to the Calibre metadata.db file."""
        self.db_path = Path(db_path).absolute()
        if not self.db_path.exists():
            raise DatabaseError(f"Database file not found: {self.db_path}")

        # Set connection attributes
        self.conn = None
        self._in_transaction = False

    def connect(self) -> None:
        """Establish a database connection."""
        if self.conn is not None:
            return

        try:
            self.conn = sqlite3.connect(
                str(self.db_path),
                isolation_level=None,  # Use autocommit mode
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            self.conn.row_factory = sqlite3.Row

            # Enable foreign key support
            self.conn.execute("PRAGMA foreign_keys = ON")

            # Optimize for read-heavy workload
            self.conn.execute("PRAGMA journal_mode = WAL")
            self.conn.execute("PRAGMA cache_size = -2000")  # 2MB cache

            logger.info(f"Connected to database: {self.db_path}")

        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}")

    def close(self) -> None:
        """Close the database connection."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        if self._in_transaction:
            yield self
            return

        self._in_transaction = True
        try:
            self.conn.execute("BEGIN")
            try:
                yield self
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise DatabaseError(f"Transaction failed: {e}")
        finally:
            self._in_transaction = False


class BaseRepository(Generic[T]):
    """Base repository class for database operations."""

    def __init__(self, conn_manager: ConnectionManager):
        """Initialize with a connection manager."""
        self.conn_manager = conn_manager

    def _fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Execute a query and return a single row as a dict."""
        try:
            cursor = self.conn_manager.conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise DatabaseError(f"Query failed: {e}\nQuery: {query}")

    def _fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a query and return all rows as a list of dicts."""
        try:
            cursor = self.conn_manager.conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Query failed: {e}\nQuery: {query}")

    def _execute(self, query: str, params: tuple = ()) -> int:
        """Execute a query and return the last row ID."""
        try:
            cursor = self.conn_manager.conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Execute failed: {e}\nQuery: {query}")

    def _execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute a query multiple times with different parameters."""
        try:
            cursor = self.conn_manager.conn.cursor()
            cursor.executemany(query, params_list)
        except sqlite3.Error as e:
            raise DatabaseError(f"Execute many failed: {e}\nQuery: {query}")

    def _get_last_insert_id(self) -> int:
        """Get the last inserted row ID."""
        cursor = self.conn_manager.conn.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]
