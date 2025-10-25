"""
SQLAlchemy and Pydantic models for Identifiers in Calibre MCP.
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel, Field, validator

from .base import Base, BaseMixin

if TYPE_CHECKING:
    from .book import Book

class Identifier(Base, BaseMixin):
    """SQLAlchemy model for book identifiers in the Calibre library"""
    __tablename__ = 'identifiers'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('books.id', ondelete='CASCADE'), 
        nullable=False,
        index=True
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)  # isbn, amazon, google, etc.
    val: Mapped[str] = mapped_column(Text, nullable=False)  # The actual identifier value
    
    # Ensure unique constraint on (book_id, type)
    __table_args__ = (
        UniqueConstraint('book_id', 'type', name='ix_identifiers_book_id_type'),
    )
    
    # Relationships
    book: Mapped["Book"] = relationship("Book", back_populates="identifiers")
    
    def __repr__(self) -> str:
        return f"<Identifier(id={self.id}, type='{self.type}', val='{self.val[:10]}...')>"

# Pydantic models for request/response validation
class IdentifierBase(BaseModel):
    """Base Pydantic model for Identifier"""
    type: str = Field(..., description="Type of identifier (e.g., isbn, amazon, google)", max_length=32)
    val: str = Field(..., description="The identifier value")
    
    class Config:
        orm_mode = True
    
    @validator('type')
    def validate_type(cls, v):
        """Validate identifier type"""
        if not v or not v.strip():
            raise ValueError('Identifier type cannot be empty')
        return v.lower().strip()
    
    @validator('val')
    def validate_val(cls, v):
        """Validate identifier value"""
        if not v or not v.strip():
            raise ValueError('Identifier value cannot be empty')
        return v.strip()

class IdentifierCreate(IdentifierBase):
    """Pydantic model for creating a new identifier"""
    book_id: int = Field(..., description="ID of the book this identifier belongs to")

class IdentifierUpdate(BaseModel):
    """Pydantic model for updating an identifier"""
    val: Optional[str] = Field(None, description="The identifier value")
    
    @validator('val')
    def validate_val(cls, v):
        """Validate identifier value is not empty if provided"""
        if v is not None and not v.strip():
            raise ValueError('Identifier value cannot be empty')
        return v.strip() if v else None

class IdentifierResponse(IdentifierBase):
    """Pydantic model for identifier response"""
    id: int = Field(..., description="Unique identifier for the identifier entry")
    book_id: int = Field(..., description="ID of the book this identifier belongs to")
