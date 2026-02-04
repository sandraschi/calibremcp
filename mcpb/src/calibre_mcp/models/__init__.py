"""
Data models for Calibre MCP.
"""

# Import Pydantic models (BookFormat, BookStatus) from the parent package's models.py
# These are in the Pydantic models.py file, not SQLAlchemy models
from pathlib import Path

from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship

from .author import Author
from .base import Base
from .book import Book
from .comment import Comment
from .data import Data
from .identifier import Identifier
from .library import Library, LibraryInfo
from .rating import Rating
from .series import Series
from .tag import Tag

if __name__ != "__main__":
    # Find the parent calibre_mcp package directory
    calibre_mcp_dir = Path(__file__).parent.parent
    models_py_path = calibre_mcp_dir / "models.py"
    if models_py_path.exists():
        # Import BookFormat and BookStatus from the Pydantic models.py file
        import importlib.util

        spec = importlib.util.spec_from_file_location("calibre_mcp_pydantic_models", models_py_path)
        pydantic_models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pydantic_models)
        BookFormat = pydantic_models.BookFormat
        BookStatus = pydantic_models.BookStatus
    else:
        # Fallback: define minimal enums
        from enum import Enum

        class BookFormat(str, Enum):
            EPUB = "epub"
            PDF = "pdf"
            MOBI = "mobi"

        class BookStatus(str, Enum):
            UNREAD = "unread"
            READING = "reading"
            FINISHED = "finished"
else:
    # Fallback for direct execution
    from enum import Enum

    class BookFormat(str, Enum):
        EPUB = "epub"
        PDF = "pdf"
        MOBI = "mobi"

    class BookStatus(str, Enum):
        UNREAD = "unread"
        READING = "reading"
        FINISHED = "finished"


# Association tables for many-to-many relationships
books_authors_link = Table(
    "books_authors_link",
    Base.metadata,
    Column("book", Integer, ForeignKey("books.id"), primary_key=True),
    Column("author", Integer, ForeignKey("authors.id"), primary_key=True),
)

books_series_link = Table(
    "books_series_link",
    Base.metadata,
    Column("book", Integer, ForeignKey("books.id"), primary_key=True),
    Column("series", Integer, ForeignKey("series.id"), primary_key=True),
)

books_tags_link = Table(
    "books_tags_link",
    Base.metadata,
    Column("book", Integer, ForeignKey("books.id"), primary_key=True),
    Column("tag", Integer, ForeignKey("tags.id"), primary_key=True),
)

books_ratings_link = Table(
    "books_ratings_link",
    Base.metadata,
    Column("book", Integer, ForeignKey("books.id"), primary_key=True),
    Column("rating", Integer, ForeignKey("ratings.id"), primary_key=True),
)

# Update relationship configurations
Book.authors = relationship(
    "Author", secondary=books_authors_link, back_populates="books", lazy="selectin"
)

Book.series_rel = relationship(
    "Series", secondary=books_series_link, back_populates="books", lazy="selectin"
)

Book.tags = relationship("Tag", secondary=books_tags_link, back_populates="books", lazy="selectin")

Book.ratings = relationship(
    "Rating", secondary=books_ratings_link, back_populates="books", lazy="selectin"
)

# Export all models and tables
__all__ = [
    "Base",
    "Book",
    "Author",
    "Series",
    "Tag",
    "Rating",
    "Comment",
    "Data",
    "Identifier",
    "Library",
    "LibraryInfo",
    "BookFormat",  # Pydantic enum from models.py
    "BookStatus",  # Pydantic enum from models.py
    "books_authors_link",
    "books_series_link",
    "books_tags_link",
    "books_ratings_link",
]
