"""
Book model for Calibre MCP.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Book(BaseModel):
    """Represents a book in the Calibre library"""
    id: int = Field(..., description="Unique identifier for the book")
    title: str = Field(..., description="Title of the book")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    timestamp: Optional[str] = Field(None, description="When the book was added to the library")
    pubdate: Optional[str] = Field(None, description="Publication date")
    series_index: float = Field(1.0, description="Position in series")
    path: str = Field("", description="Path to the book's directory")
    has_cover: bool = Field(False, description="Whether the book has a cover")
    last_modified: Optional[str] = Field(None, description="When the book was last modified")
    uuid: str = Field("", description="Unique identifier for the book")
    
    # Additional metadata that might be useful
    formats: List[str] = Field(default_factory=list, description="Available formats")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the book")
    comments: str = Field("", description="Book description/comments")
    series: Optional[str] = Field(None, description="Series name")
    publisher: Optional[str] = Field(None, description="Publisher")
    languages: List[str] = Field(default_factory=list, description="Languages")
    identifiers: Dict[str, str] = Field(default_factory=dict, description="Book identifiers (ISBN, etc.)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def get_cover_path(self) -> Optional[str]:
        """Get the path to the book's cover image"""
        if not self.has_cover or not self.path:
            return None
        return f"{self.path.rstrip('/')}/cover.jpg"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert book to dictionary"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        """Create book from dictionary"""
        return cls(**data)
