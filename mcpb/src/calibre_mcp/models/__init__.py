"""
Data models for Calibre MCP.
"""
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from .book import Book
from .author import Author
from .series import Series
from .tag import Tag
from .rating import Rating
from .comment import Comment
from .data import Data
from .identifier import Identifier
from .library import Library, LibraryInfo

# Association tables for many-to-many relationships
books_authors_link = Table(
    'books_authors_link',
    Base.metadata,
    Column('book', Integer, ForeignKey('books.id'), primary_key=True),
    Column('author', Integer, ForeignKey('authors.id'), primary_key=True)
)

books_series_link = Table(
    'books_series_link',
    Base.metadata,
    Column('book', Integer, ForeignKey('books.id'), primary_key=True),
    Column('series', Integer, ForeignKey('series.id'), primary_key=True)
)

books_tags_link = Table(
    'books_tags_link',
    Base.metadata,
    Column('book', Integer, ForeignKey('books.id'), primary_key=True),
    Column('tag', Integer, ForeignKey('tags.id'), primary_key=True)
)

books_ratings_link = Table(
    'books_ratings_link',
    Base.metadata,
    Column('book', Integer, ForeignKey('books.id'), primary_key=True),
    Column('rating', Integer, ForeignKey('ratings.id'), primary_key=True)
)

# Update relationship configurations
Book.authors = relationship(
    'Author',
    secondary=books_authors_link,
    back_populates='books',
    lazy='selectin'
)

Book.series_rel = relationship(
    'Series',
    secondary=books_series_link,
    back_populates='books',
    lazy='selectin'
)

Book.tags = relationship(
    'Tag',
    secondary=books_tags_link,
    back_populates='books',
    lazy='selectin'
)

Book.ratings = relationship(
    'Rating',
    secondary=books_ratings_link,
    back_populates='books',
    lazy='selectin'
)

# Export all models and tables
__all__ = [
    'Base',
    'Book',
    'Author',
    'Series',
    'Tag',
    'Rating',
    'Comment',
    'Data',
    'Identifier',
    'Library',
    'LibraryInfo',
    'books_authors_link',
    'books_series_link',
    'books_tags_link',
    'books_ratings_link'
]
