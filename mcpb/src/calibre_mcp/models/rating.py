"""
SQLAlchemy and Pydantic models for Ratings in Calibre MCP.
"""
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel, Field, validator

from .base import Base, BaseMixin

if TYPE_CHECKING:
    from .book import Book

class Rating(Base, BaseMixin):
    """SQLAlchemy model for ratings in the Calibre library"""
    __tablename__ = 'ratings'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    
    # Relationships
    books: Mapped[List["Book"]] = relationship(
        "Book", 
        secondary="books_ratings_link", 
        back_populates="ratings"
    )
    
    def __repr__(self) -> str:
        return f"<Rating(id={self.id}, rating={self.rating})>"
    
    @property
    def book_count(self) -> int:
        """Get the number of books with this rating"""
        return len(self.books) if hasattr(self, 'books') else 0

# Pydantic models for request/response validation
class RatingBase(BaseModel):
    """Base Pydantic model for Rating"""
    rating: float = Field(..., description="Rating value (0-5)", ge=0, le=5)
    
    class Config:
        orm_mode = True
    
    @validator('rating')
    def validate_rating(cls, v):
        """Validate that rating is between 0 and 5"""
        if v < 0 or v > 5:
            raise ValueError('Rating must be between 0 and 5')
        return v

class RatingCreate(RatingBase):
    """Pydantic model for creating a new rating"""
    pass

class RatingResponse(RatingBase):
    """Pydantic model for rating response"""
    id: int = Field(..., description="Unique identifier for the rating")
    book_count: int = Field(0, description="Number of books with this rating")
    
    @classmethod
    def from_orm(cls, obj):
        """Create response model from ORM object"""
        data = super().from_orm(obj)
        if hasattr(obj, 'book_count'):
            data.book_count = obj.book_count
        elif hasattr(obj, 'books'):
            data.book_count = len(obj.books)
        return data
