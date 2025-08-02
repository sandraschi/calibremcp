"""
Library model for Calibre MCP.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class LibraryInfo(BaseModel):
    """Represents information about a Calibre library"""
    name: str = Field(..., description="Name of the library")
    path: str = Field(..., description="Path or URL to the library")
    book_count: int = Field(0, description="Number of books in the library")
    total_size: int = Field(0, description="Total size of the library in bytes")
    is_local: bool = Field(True, description="Whether this is a local library")
    
    # Additional metadata
    last_updated: Optional[str] = Field(None, description="When the library was last updated")
    format_counts: Dict[str, int] = Field(
        default_factory=dict, 
        description="Count of books by format"
    )
    author_count: int = Field(0, description="Number of unique authors")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert library info to dictionary"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LibraryInfo':
        """Create library info from dictionary"""
        return cls(**data)
