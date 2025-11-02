"""
SQLAlchemy and Pydantic models for Author in Calibre MCP.
"""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel, Field

from .base import Base, BaseMixin

if TYPE_CHECKING:
    from .book import Book


class Author(Base, BaseMixin):
    """SQLAlchemy model for authors in the Calibre library"""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    sort: Mapped[Optional[str]] = mapped_column(Text)
    link: Mapped[Optional[str]] = mapped_column(Text, default="")

    # Relationships
    books: Mapped[List["Book"]] = relationship(
        "Book", secondary="books_authors_link", back_populates="authors"
    )

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, name='{self.name}')>"

    @property
    def book_count(self) -> int:
        """Get the number of books by this author"""
        return len(self.books) if hasattr(self, "books") else 0


# Pydantic models for request/response validation
class AuthorBase(BaseModel):
    """Base Pydantic model for Author"""

    name: str = Field(..., description="Author's name")
    sort: Optional[str] = Field(None, description="Sort name")
    link: Optional[str] = Field(None, description="Author URL or link")

    class Config:
        orm_mode = True


class AuthorCreate(AuthorBase):
    """Pydantic model for creating a new author"""

    pass


class AuthorUpdate(BaseModel):
    """Pydantic model for updating an author"""

    name: Optional[str] = Field(None, description="Author's name")
    sort: Optional[str] = Field(None, description="Sort name")
    link: Optional[str] = Field(None, description="Author URL or link")


class AuthorResponse(AuthorBase):
    """Pydantic model for author response"""

    id: int = Field(..., description="Unique identifier for the author")
    book_count: int = Field(0, description="Number of books by this author")

    @classmethod
    def from_orm(cls, obj):
        """Create response model from ORM object"""
        data = super().from_orm(obj)
        if hasattr(obj, "book_count"):
            data.book_count = obj.book_count
        elif hasattr(obj, "books"):
            data.book_count = len(obj.books)
        return data
