"""
SQLAlchemy and Pydantic models for Library in Calibre MCP.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, BaseMixin

if TYPE_CHECKING:
    pass


class Library(Base, BaseMixin):
    """SQLAlchemy model for Calibre library"""

    __tablename__ = "library"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    path: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    is_local: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    # NOTE: Calibre's actual database schema does NOT have a library table or foreign key.
    # Each metadata.db file IS a library. Books don't have a library_id FK.
    # Therefore, we CANNOT define a SQLAlchemy relationship here - it will fail because
    # there's no foreign key to join on. The Library model is for application-level
    # library management, not for Calibre's actual database schema.
    #
    # If you need to get books for a library, query the books table directly - all books
    # in a metadata.db file belong to that library.
    #
    # books relationship removed - use direct queries instead
    # books: Mapped[List["Book"]] = relationship(...)  # REMOVED - no FK in Calibre schema

    def __repr__(self) -> str:
        return f"<Library(id={self.id}, name='{self.name}', path='{self.path}')>"

    @property
    def book_count(self) -> int:
        """Get the number of books in the library"""
        return len(self.books) if hasattr(self, "books") else 0

    @property
    def author_count(self) -> int:
        """Get the number of unique authors in the library"""
        if not hasattr(self, "books") or not self.books:
            return 0
        return len({author.id for book in self.books for author in book.authors})

    @property
    def format_counts(self) -> dict[str, int]:
        """Get count of books by format"""
        if not hasattr(self, "books") or not self.books:
            return {}

        counts = {}
        for book in self.books:
            for data in book.data:
                fmt = data.format.lower()
                counts[fmt] = counts.get(fmt, 0) + 1
        return counts

    @property
    def total_size(self) -> int:
        """Get total size of all book files in the library"""
        if not hasattr(self, "books") or not self.books:
            return 0
        return sum(data.uncompressed_size for book in self.books for data in book.data)


# Pydantic models for request/response validation
class LibraryBase(BaseModel):
    """Base Pydantic model for Library"""

    name: str = Field(..., description="Name of the library")
    path: str = Field(..., description="Path or URL to the library")
    is_local: bool = Field(True, description="Whether this is a local library")

    class Config:
        orm_mode = True


class LibraryCreate(LibraryBase):
    """Pydantic model for creating a new library"""

    pass


class LibraryUpdate(BaseModel):
    """Pydantic model for updating a library"""

    name: str | None = Field(None, description="Name of the library")
    path: str | None = Field(None, description="Path or URL to the library")
    is_local: bool | None = Field(None, description="Whether this is a local library")
    is_active: bool | None = Field(None, description="Whether the library is active")


class LibraryResponse(LibraryBase):
    """Pydantic model for library response"""

    id: int = Field(..., description="Unique identifier for the library")
    is_active: bool = Field(True, description="Whether the library is active")
    book_count: int = Field(0, description="Number of books in the library")
    author_count: int = Field(0, description="Number of unique authors")
    total_size: int = Field(0, description="Total size of the library in bytes")
    format_counts: dict[str, int] = Field(
        default_factory=dict, description="Count of books by format"
    )
    created_at: datetime = Field(..., description="When the library was created")
    updated_at: datetime | None = Field(None, description="When the library was last updated")

    @classmethod
    def from_orm(cls, obj):
        """Create response model from ORM object"""
        data = super().from_orm(obj)
        data.book_count = obj.book_count
        data.author_count = obj.author_count
        data.total_size = obj.total_size
        data.format_counts = obj.format_counts
        return data


# Keep the original LibraryInfo for backward compatibility
class LibraryInfo(LibraryResponse):
    """Legacy Pydantic model for library information"""

    last_updated: datetime | None = Field(None, alias="updated_at")

    class Config(LibraryResponse.Config):
        fields = {"updated_at": {"exclude": True}}
