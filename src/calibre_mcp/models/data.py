"""
SQLAlchemy and Pydantic models for Data (book formats) in Calibre MCP.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseMixin

if TYPE_CHECKING:
    from .book import Book


class Data(Base, BaseMixin):
    """SQLAlchemy model for book data/formats in the Calibre library"""

    __tablename__ = "data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    format: Mapped[str] = mapped_column(String(8), nullable=False)  # EPUB, PDF, MOBI, etc.
    uncompressed_size: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, default="")

    # File modification time
    mtime: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    book: Mapped["Book"] = relationship("Book", back_populates="data")

    def __repr__(self) -> str:
        return f"<Data(id={self.id}, book_id={self.book_id}, format='{self.format}')>"

    @property
    def file_path(self) -> str:
        """Get the relative file path for this format"""
        if not hasattr(self, "book") or not hasattr(self.book, "path"):
            return ""
        return f"{self.book.path}/{self.id}.{self.format.lower()}"


# Pydantic models for request/response validation
class DataBase(BaseModel):
    """Base Pydantic model for Data"""

    format: str = Field(..., description="File format (e.g., EPUB, PDF, MOBI)", max_length=8)
    uncompressed_size: int = Field(..., description="Size of the file in bytes")
    name: str = Field("", description="Original filename")

    class Config:
        orm_mode = True


class DataCreate(DataBase):
    """Pydantic model for creating a new data entry"""

    book_id: int = Field(..., description="ID of the book this data belongs to")


class DataResponse(DataBase):
    """Pydantic model for data response"""

    id: int = Field(..., description="Unique identifier for the data entry")
    book_id: int = Field(..., description="ID of the book this data belongs to")
    mtime: datetime | None = Field(None, description="Last modification time")
    file_path: str | None = Field(None, description="Relative path to the file")

    @classmethod
    def from_orm(cls, obj):
        """Create response model from ORM object"""
        data = super().from_orm(obj)
        if hasattr(obj, "file_path"):
            data.file_path = obj.file_path
        return data
