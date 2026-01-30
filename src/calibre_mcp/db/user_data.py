"""
CalibreMCP-owned SQLite database for user data.

Stores data outside of Calibre's metadata.db:
- User comments (annotations on books, distinct from Calibre description/comment field)
- Future: auth, preferences, reading progress, etc.

Database file: %APPDATA%/calibre-mcp/calibre_mcp_data.db (Windows)
               ~/.local/share/calibre-mcp/calibre_mcp_data.db (Linux)
               ~/Library/Application Support/calibre-mcp/calibre_mcp_data.db (macOS)
"""

import os
import platform
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, Column, Integer, Text, DateTime, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.engine import Engine

from ..logging_config import get_logger

logger = get_logger("calibremcp.db.user_data")

Base = declarative_base()


def _get_user_data_dir() -> Path:
    """Return platform-appropriate directory for CalibreMCP user data."""
    env_dir = os.getenv("CALIBRE_MCP_USER_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    if os.name == "nt":
        appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        return Path(appdata) / "calibre-mcp"
    home = Path.home()
    if platform.system() == "Darwin":
        return home / "Library" / "Application Support" / "calibre-mcp"
    return home / ".local" / "share" / "calibre-mcp"


def _get_db_path() -> Path:
    """Return path to the CalibreMCP user data SQLite database."""
    data_dir = _get_user_data_dir()
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        data_dir = Path.cwd() / ".calibre-mcp-data"
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "calibre_mcp_data.db"


class UserComment(Base):
    """
    User annotation/comment on a book, stored separately from Calibre's description.

    book_id + library_path identify the book uniquely across libraries.
    """

    __tablename__ = "user_comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, nullable=False, index=True)
    library_path = Column(Text, nullable=False, index=True)
    comment_text = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(String(64), nullable=True, index=True)  # Placeholder for future auth

    def __repr__(self) -> str:
        return f"<UserComment(id={self.id}, book_id={self.book_id}, len={len(self.comment_text or '')})>"


class BookExtendedMetadata(Base):
    """
    Extended metadata for books, stored outside Calibre's metadata.db.

    - translator: Translator name (not in Calibre schema)
    - first_published: Original/first publication date (e.g. "1599", "44 BC").
      Calibre's pubdate is edition date; this stores the true first publication.
    book_id + library_path scope the record per library.
    """

    __tablename__ = "book_extended_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, nullable=False, index=True)
    library_path = Column(Text, nullable=False, index=True)
    translator = Column(Text, nullable=True, default="")
    first_published = Column(Text, nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BookExtendedMetadata(id={self.id}, book_id={self.book_id})>"


# Placeholder for future auth table - schema ready for extension
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     ...


class UserDataDB:
    """
    Database service for CalibreMCP-owned user data (SQLite).
    Separate from Calibre's metadata.db.
    """

    _instance: Optional["UserDataDB"] = None

    def __new__(cls) -> "UserDataDB":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._engine = None
            cls._instance._session_factory = None
        return cls._instance

    def initialize(self, db_path: Optional[Path] = None) -> None:
        """Initialize or ensure database exists and tables are created."""
        if self._engine is not None:
            return

        path = db_path or _get_db_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{path}"

        self._engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )
        logger.info(
            "User data database initialized",
            extra={"path": str(path), "service": "user_data_db"},
        )

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self.initialize()
        return self._engine

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope."""
        if self._session_factory is None:
            self.initialize()
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Close database connection."""
        if self._session_factory:
            self._session_factory.close_all()
            self._session_factory = None
        if self._engine:
            self._engine.dispose()
            self._engine = None
        UserDataDB._instance = None


_user_data_db = UserDataDB()


def get_user_data_db() -> UserDataDB:
    """Get the global user data database instance."""
    return _user_data_db


def init_user_data_db() -> None:
    """Initialize the user data database (call at server startup)."""
    _user_data_db.initialize()
