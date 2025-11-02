"""
SQLAlchemy and Pydantic models for Book in Calibre MCP.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel, Field, validator

from .base import Base, BaseMixin

if TYPE_CHECKING:
    from .author import Author
    from .series import Series
    from .tag import Tag
    from .rating import Rating
    from .comment import Comment
    from .data import Data
    from .identifier import Identifier

# Association tables are defined in models/__init__.py


class Book(Base, BaseMixin):
    """SQLAlchemy model for books in the Calibre library"""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    sort: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime)
    pubdate: Mapped[Optional[datetime]] = mapped_column(DateTime)
    series_index: Mapped[float] = mapped_column(Float, default=1.0)
    author_sort: Mapped[Optional[str]] = mapped_column(Text)
    isbn: Mapped[Optional[str]] = mapped_column(String(32))
    lccn: Mapped[Optional[str]] = mapped_column(String(32))
    path: Mapped[str] = mapped_column(Text, nullable=False)
    flags: Mapped[int] = mapped_column(Integer, default=1)
    uuid: Mapped[Optional[str]] = mapped_column(String(36))
    has_cover: Mapped[bool] = mapped_column(Integer, default=0)
    last_modified: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    authors: Mapped[List["Author"]] = relationship(
        "Author", secondary="books_authors_link", back_populates="books"
    )

    series_rel: Mapped[List["Series"]] = relationship(
        "Series", secondary="books_series_link", back_populates="books"
    )

    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary="books_tags_link", back_populates="books"
    )

    ratings: Mapped[List["Rating"]] = relationship(
        "Rating", secondary="books_ratings_link", back_populates="books"
    )

    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="book")

    data: Mapped[List["Data"]] = relationship("Data", back_populates="book")

    identifiers: Mapped[List["Identifier"]] = relationship("Identifier", back_populates="book")

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}')>"

    @property
    def series(self) -> Optional["Series"]:
        """Get the first series this book belongs to, if any."""
        return self.series_rel[0] if self.series_rel else None

    def get_cover_path(self) -> Optional[str]:
        """Get the path to the book's cover image"""
        if not self.has_cover or not self.path:
            return None
        return f"{self.path.rstrip('/')}/cover.jpg"


# Pydantic models for request/response validation
class BookBase(BaseModel):
    """Base Pydantic model for Book"""

    title: str = Field(..., description="Title of the book")
    sort: Optional[str] = Field(None, description="Sort title")
    timestamp: Optional[datetime] = Field(
        None, description="When the book was added to the library"
    )
    pubdate: Optional[datetime] = Field(None, description="Publication date")
    series_index: float = Field(1.0, description="Position in series")
    path: str = Field(..., description="Path to the book's directory")
    has_cover: bool = Field(False, description="Whether the book has a cover")
    author_sort: Optional[str] = Field(None, description="Author sort string")
    isbn: Optional[str] = Field(None, description="ISBN")
    lccn: Optional[str] = Field(None, description="Library of Congress Control Number")

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class BookCreate(BookBase):
    """Pydantic model for creating a new book"""

    author_ids: List[int] = Field(default_factory=list, description="List of author IDs")
    series_id: Optional[int] = Field(None, description="Series ID")
    tag_ids: List[int] = Field(default_factory=list, description="List of tag IDs")
    rating: Optional[int] = Field(None, description="Rating (1-5)", ge=1, le=5)


class BookUpdate(BaseModel):
    """Pydantic model for updating a book"""

    title: Optional[str] = Field(None, description="Title of the book")
    sort: Optional[str] = Field(None, description="Sort title")
    pubdate: Optional[datetime] = Field(None, description="Publication date")
    series_index: Optional[float] = Field(None, description="Position in series")
    path: Optional[str] = Field(None, description="Path to the book's directory")
    has_cover: Optional[bool] = Field(None, description="Whether the book has a cover")
    author_sort: Optional[str] = Field(None, description="Author sort string")
    isbn: Optional[str] = Field(None, description="ISBN")
    lccn: Optional[str] = Field(None, description="Library of Congress Control Number")
    author_ids: Optional[List[int]] = Field(None, description="List of author IDs")
    series_id: Optional[int] = Field(None, description="Series ID")
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs")
    rating: Optional[int] = Field(None, description="Rating (1-5)", ge=1, le=5)


class BookResponse(BookBase):
    """Pydantic model for book response"""

    id: int = Field(..., description="Unique identifier for the book")
    uuid: Optional[str] = Field(None, description="Unique identifier for the book")
    last_modified: Optional[datetime] = Field(None, description="When the book was last modified")

    # Computed fields
    authors: List[Dict[str, Any]] = Field(default_factory=list, description="List of authors")
    series: Optional[Dict[str, Any]] = Field(None, description="Series information")
    tags: List[Dict[str, Any]] = Field(default_factory=list, description="List of tags")
    rating: Optional[int] = Field(None, description="Book rating (1-5)")
    formats: List[Dict[str, Any]] = Field(default_factory=list, description="Available formats")
    identifiers: Dict[str, str] = Field(default_factory=dict, description="Book identifiers")

    @validator("formats", pre=True)
    def format_data_to_formats(cls, v, values):
        """Convert Data objects to format dictionaries"""
        if v is None:
            return []
        if isinstance(v, list) and v and hasattr(v[0], "format"):
            return [{"format": d.format, "size": d.uncompressed_size} for d in v]
        return v

    @validator("authors", "tags", pre=True)
    def convert_relationships(cls, v):
        """Convert relationship objects to dictionaries"""
        if v is None:
            return []
        if v and hasattr(v[0], "to_dict"):
            return [item.to_dict() for item in v]
        return v

    @validator("series", pre=True)
    def convert_series(cls, v):
        """Convert series relationship to dictionary"""
        if v is None:
            return None
        if hasattr(v, "to_dict"):
            return v.to_dict()
        return v

    @validator("rating", pre=True)
    def get_rating_value(cls, v, values):
        """Extract rating value from ratings relationship"""
        if v is not None:
            return v
        if "ratings" in values and values["ratings"]:
            return values["ratings"][0].rating if hasattr(values["ratings"][0], "rating") else None
        return None

    class Config(BookBase.Config):
        fields = {"series_rel": {"exclude": True}, "ratings": {"exclude": True}}
