"""
SQLAlchemy and Pydantic models for Series in Calibre MCP.
"""

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseMixin

if TYPE_CHECKING:
    from .book import Book


class Series(Base, BaseMixin):
    """SQLAlchemy model for series in the Calibre library"""

    __tablename__ = "series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True, unique=True)
    sort: Mapped[str | None] = mapped_column(Text)

    # Relationships
    books: Mapped[list["Book"]] = relationship(
        "Book", secondary="books_series_link", back_populates="series_rel"
    )

    def __repr__(self) -> str:
        return f"<Series(id={self.id}, name='{self.name}')>"

    @property
    def book_count(self) -> int:
        """Get the number of books in this series"""
        return len(self.books) if hasattr(self, "books") else 0


# Pydantic models for request/response validation
class SeriesBase(BaseModel):
    """Base Pydantic model for Series"""

    name: str = Field(..., description="Name of the series")
    sort: str | None = Field(None, description="Sort name")

    class Config:
        orm_mode = True


class SeriesCreate(SeriesBase):
    """Pydantic model for creating a new series"""

    pass


class SeriesUpdate(BaseModel):
    """Pydantic model for updating a series"""

    name: str | None = Field(None, description="Name of the series")
    sort: str | None = Field(None, description="Sort name")


class SeriesResponse(SeriesBase):
    """Pydantic model for series response"""

    id: int = Field(..., description="Unique identifier for the series")
    book_count: int = Field(0, description="Number of books in this series")

    @classmethod
    def from_orm(cls, obj):
        """Create response model from ORM object"""
        data = super().from_orm(obj)
        if hasattr(obj, "book_count"):
            data.book_count = obj.book_count
        elif hasattr(obj, "books"):
            data.book_count = len(obj.books)
        return data
