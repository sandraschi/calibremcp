"""
SQLAlchemy and Pydantic models for Book in Calibre MCP.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field, validator
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseMixin

if TYPE_CHECKING:
    from .author import Author
    from .comment import Comment
    from .data import Data
    from .identifier import Identifier
    from .rating import Rating
    from .series import Series
    from .tag import Tag

# Association tables are defined in models/__init__.py


class Book(Base, BaseMixin):
    """SQLAlchemy model for books in the Calibre library"""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    sort: Mapped[str | None] = mapped_column(Text)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    pubdate: Mapped[datetime | None] = mapped_column(DateTime)
    series_index: Mapped[float] = mapped_column(Float, default=1.0)
    author_sort: Mapped[str | None] = mapped_column(Text)
    isbn: Mapped[str | None] = mapped_column(String(32))
    lccn: Mapped[str | None] = mapped_column(String(32))
    path: Mapped[str] = mapped_column(Text, nullable=False)
    flags: Mapped[int] = mapped_column(Integer, default=1)
    uuid: Mapped[str | None] = mapped_column(String(36))
    has_cover: Mapped[bool] = mapped_column(Integer, default=0)
    last_modified: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    authors: Mapped[list["Author"]] = relationship(
        "Author", secondary="books_authors_link", back_populates="books"
    )

    series_rel: Mapped[list["Series"]] = relationship(
        "Series", secondary="books_series_link", back_populates="books"
    )

    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="books_tags_link", back_populates="books"
    )

    ratings: Mapped[list["Rating"]] = relationship(
        "Rating", secondary="books_ratings_link", back_populates="books"
    )

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="book")

    data: Mapped[list["Data"]] = relationship("Data", back_populates="book")

    identifiers: Mapped[list["Identifier"]] = relationship("Identifier", back_populates="book")

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}')>"

    @property
    def series(self) -> Optional["Series"]:
        """Get the first series this book belongs to, if any."""
        return self.series_rel[0] if self.series_rel else None

    def get_cover_path(self) -> str | None:
        """Get the path to the book's cover image"""
        if not self.has_cover or not self.path:
            return None
        return f"{self.path.rstrip('/')}/cover.jpg"


# Pydantic models for request/response validation
class BookBase(BaseModel):
    """Base Pydantic model for Book"""

    title: str = Field(..., description="Title of the book")
    sort: str | None = Field(None, description="Sort title")
    timestamp: datetime | None = Field(None, description="When the book was added to the library")
    pubdate: datetime | None = Field(None, description="Publication date")
    series_index: float = Field(1.0, description="Position in series")
    path: str = Field(..., description="Path to the book's directory")
    has_cover: bool = Field(False, description="Whether the book has a cover")
    author_sort: str | None = Field(None, description="Author sort string")
    isbn: str | None = Field(None, description="ISBN")
    lccn: str | None = Field(None, description="Library of Congress Control Number")

    class Config:
        from_attributes = True  # Pydantic V2 replacement for orm_mode
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class BookCreate(BookBase):
    """Pydantic model for creating a new book"""

    author_ids: list[int] = Field(default_factory=list, description="List of author IDs")
    series_id: int | None = Field(None, description="Series ID")
    tag_ids: list[int] = Field(default_factory=list, description="List of tag IDs")
    rating: int | None = Field(None, description="Rating (1-5)", ge=1, le=5)


class BookUpdate(BaseModel):
    """Pydantic model for updating a book"""

    title: str | None = Field(None, description="Title of the book")
    sort: str | None = Field(None, description="Sort title")
    pubdate: datetime | None = Field(None, description="Publication date")
    series_index: float | None = Field(None, description="Position in series")
    path: str | None = Field(None, description="Path to the book's directory")
    has_cover: bool | None = Field(None, description="Whether the book has a cover")
    author_sort: str | None = Field(None, description="Author sort string")
    isbn: str | None = Field(None, description="ISBN")
    lccn: str | None = Field(None, description="Library of Congress Control Number")
    author_ids: list[int] | None = Field(None, description="List of author IDs")
    series_id: int | None = Field(None, description="Series ID")
    tag_ids: list[int] | None = Field(None, description="List of tag IDs")
    rating: int | None = Field(None, description="Rating (1-5)", ge=1, le=5)


class BookResponse(BookBase):
    """Pydantic model for book response"""

    id: int = Field(..., description="Unique identifier for the book")
    uuid: str | None = Field(None, description="Unique identifier for the book")
    last_modified: datetime | None = Field(None, description="When the book was last modified")

    # Computed fields
    authors: list[dict[str, Any]] = Field(default_factory=list, description="List of authors")
    series: dict[str, Any] | None = Field(None, description="Series information")
    tags: list[dict[str, Any]] = Field(default_factory=list, description="List of tags")
    rating: int | None = Field(None, description="Book rating (1-5)")
    formats: list[dict[str, Any]] = Field(default_factory=list, description="Available formats")
    identifiers: dict[str, str] = Field(default_factory=dict, description="Book identifiers")

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
