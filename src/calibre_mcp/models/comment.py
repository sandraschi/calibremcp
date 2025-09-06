"""
SQLAlchemy and Pydantic models for Comments in Calibre MCP.
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel, Field

from .base import Base, BaseMixin

if TYPE_CHECKING:
    from .book import Book

class Comment(Base, BaseMixin):
    """SQLAlchemy model for comments/descriptions in the Calibre library"""
    __tablename__ = 'comments'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Foreign key to books table
    book_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('books.id', ondelete='CASCADE'), 
        nullable=False,
        unique=True
    )
    
    # Relationships
    book: Mapped["Book"] = relationship("Book", back_populates="comments")
    
    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, book_id={self.book_id}, text_length={len(self.text) if self.text else 0})>"

# Pydantic models for request/response validation
class CommentBase(BaseModel):
    """Base Pydantic model for Comment"""
    text: str = Field(..., description="Comment/description text")
    
    class Config:
        orm_mode = True

class CommentCreate(CommentBase):
    """Pydantic model for creating a new comment"""
    book_id: int = Field(..., description="ID of the book this comment belongs to")

class CommentUpdate(BaseModel):
    """Pydantic model for updating a comment"""
    text: Optional[str] = Field(None, description="Comment/description text")

class CommentResponse(CommentBase):
    """Pydantic model for comment response"""
    id: int = Field(..., description="Unique identifier for the comment")
    book_id: int = Field(..., description="ID of the book this comment belongs to")
