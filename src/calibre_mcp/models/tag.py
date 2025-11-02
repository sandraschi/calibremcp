"""
SQLAlchemy and Pydantic models for Tags in Calibre MCP.
"""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel, Field

from .base import Base, BaseMixin

if TYPE_CHECKING:
    from .book import Book


class Tag(Base, BaseMixin):
    """SQLAlchemy model for tags in the Calibre library"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)

    # Relationships
    books: Mapped[List["Book"]] = relationship(
        "Book", secondary="books_tags_link", back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"

    @property
    def book_count(self) -> int:
        """Get the number of books with this tag"""
        return len(self.books) if hasattr(self, "books") else 0


# Pydantic models for request/response validation
class TagBase(BaseModel):
    """Base Pydantic model for Tag"""

    name: str = Field(..., description="Name of the tag")

    class Config:
        orm_mode = True


class TagCreate(TagBase):
    """Pydantic model for creating a new tag"""

    pass


class TagUpdate(BaseModel):
    """Pydantic model for updating a tag"""

    name: Optional[str] = Field(None, description="New name for the tag")

    class Config:
        orm_mode = True


class TagResponse(TagBase):
    """Pydantic model for tag response"""

    id: int = Field(..., description="Unique identifier for the tag")
    book_count: int = Field(0, description="Number of books with this tag")

    @classmethod
    def from_orm(cls, obj):
        """Create response model from ORM object"""
        data = super().from_orm(obj)
        if hasattr(obj, "book_count"):
            data.book_count = obj.book_count
        elif hasattr(obj, "books"):
            data.book_count = len(obj.books)
        return data
