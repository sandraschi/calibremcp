"""
SQLAlchemy models for Calibre database.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Association tables
books_authors_link = Table(
    "books_authors_link",
    Base.metadata,
    Column("book", Integer, ForeignKey("books.id"), primary_key=True),
    Column("author", Integer, ForeignKey("authors.id"), primary_key=True),
    Column("id", Integer, primary_key=True),
)

books_series_link = Table(
    "books_series_link",
    Base.metadata,
    Column("book", Integer, ForeignKey("books.id"), primary_key=True),
    Column("series", Integer, ForeignKey("series.id"), primary_key=True),
    Column("id", Integer, primary_key=True),
)

books_tags_link = Table(
    "books_tags_link",
    Base.metadata,
    Column("book", Integer, ForeignKey("books.id"), primary_key=True),
    Column("tag", Integer, ForeignKey("tags.id"), primary_key=True),
    Column("id", Integer, primary_key=True),
)

books_ratings_link = Table(
    "books_ratings_link",
    Base.metadata,
    Column("book", Integer, ForeignKey("books.id"), primary_key=True),
    Column("rating", Integer, ForeignKey("ratings.id"), primary_key=True),
    Column("id", Integer, primary_key=True),
)


class Book(Base):
    """Represents a book in the library."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False, index=True)
    sort = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pubdate = Column(DateTime, default=datetime.utcnow)
    series_index = Column(Float, default=1.0)
    author_sort = Column(Text)
    isbn = Column(String(32))
    lccn = Column(String(32))
    path = Column(Text, nullable=False)
    flags = Column(Integer, default=1)
    uuid = Column(String(36))
    has_cover = Column(Integer, default=0)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    authors = relationship("Author", secondary=books_authors_link, back_populates="books")
    series = relationship("Series", secondary=books_series_link, back_populates="books")
    tags = relationship("Tag", secondary=books_tags_link, back_populates="books")
    ratings = relationship("Rating", secondary=books_ratings_link, back_populates="books")
    comments = relationship("Comment", back_populates="book_rel", uselist=False)
    data = relationship("Data", back_populates="book_rel")
    identifiers = relationship(
        "Identifier",
        back_populates="book_rel",
        primaryjoin="Book.id == Identifier.book",
        foreign_keys="[Identifier.book]",
        lazy="noload",  # Never load automatically - access manually if needed
    )

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"


class Author(Base):
    """Represents an author."""

    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, index=True)
    sort = Column(Text)
    link = Column(Text, default="")

    # Relationships
    books = relationship("Book", secondary=books_authors_link, back_populates="authors")

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"


class Series(Base):
    """Represents a book series."""

    __tablename__ = "series"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    sort = Column(Text)

    # Relationships
    books = relationship("Book", secondary=books_series_link, back_populates="series")

    def __repr__(self):
        return f"<Series(id={self.id}, name='{self.name}')>"


class Tag(Base):
    """Represents a tag that can be applied to books."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)

    # Relationships
    books = relationship("Book", secondary=books_tags_link, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class Rating(Base):
    """Represents a rating that can be applied to books."""

    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    rating = Column(Integer, nullable=False, default=0)

    # Relationships
    books = relationship("Book", secondary=books_ratings_link, back_populates="ratings")

    def __repr__(self):
        return f"<Rating(id={self.id}, rating={self.rating})>"


class Comment(Base):
    """Represents a comment/description for a book."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey("books.id"), unique=True)
    text = Column(Text, default="")

    # Relationships
    book_rel = relationship("Book", back_populates="comments")

    def __repr__(self):
        return f"<Comment(book_id={self.book}, length={len(self.text) if self.text else 0})>"


class Data(Base):
    """Represents additional data for books (like format, size, etc.)."""

    __tablename__ = "data"

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey("books.id"), nullable=False)
    format = Column(String(8), nullable=False)
    uncompressed_size = Column(Integer, default=0)
    name = Column(Text, default="")

    # Relationships
    book_rel = relationship("Book", back_populates="data")

    __table_args__ = (UniqueConstraint("book", "format", name="data_book_format_uc"),)

    def __repr__(self):
        return f"<Data(book_id={self.book}, format='{self.format}')>"


class Identifier(Base):
    """Represents an identifier for a book (ISBN, DOI, etc.)."""

    __tablename__ = "identifiers"

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey("books.id"), nullable=False)
    type = Column(String(32), nullable=False)
    val = Column(Text, nullable=False)

    # Relationships
    book_rel = relationship("Book", back_populates="identifiers")

    __table_args__ = (UniqueConstraint("book", "type", name="identifiers_book_type_uc"),)

    def __repr__(self):
        return f"<Identifier(book_id={self.book}, type='{self.type}', val='{self.val}')>"


# Create indexes for better query performance
Index("idx_books_title", Book.title)
Index("idx_books_author_sort", Book.author_sort)
Index("idx_books_pubdate", Book.pubdate)
Index("idx_authors_name", Author.name)
Index("idx_series_name", Series.name)
Index("idx_tags_name", Tag.name)
