"""
Service for handling author-related operations.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from ..db import get_database
from .base_service import BaseService
from .book_service import BookSearchResult

class Author(BaseModel):
    """Author model."""
    id: int = Field(..., description="Unique author ID")
    name: str = Field(..., description="Author's name")
    sort: str = Field(..., description="Sortable version of author's name")
    book_count: int = Field(0, description="Number of books by this author")
    
class AuthorService(BaseService):
    """Service for author-related operations."""
    
    def __init__(self, db=None):
        """Initialize with an optional database instance."""
        super().__init__(db or get_database())
    
    def get_author(self, author_id: int) -> Optional[Author]:
        """Get an author by ID."""
        author_data = self.db.authors.get_author_by_id(author_id)
        if not author_data:
            return None
        return Author(**author_data)
    
    def search_authors(
        self,
        query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for authors.
        
        Args:
            query: Search query (searches in author names)
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            Dictionary containing paginated results and metadata
        """
        # Get authors from repository
        authors_data = self.db.authors.get_authors(
            query=query,
            limit=limit,
            offset=offset
        )
        
        # Convert to Pydantic models
        authors = [Author(**author) for author in authors_data]
        
        # Get total count for pagination
        # Note: This could be optimized with a separate count query if needed
        total = len(authors)
        
        return self._paginate_results(authors, total, offset // limit + 1, limit)
    
    def get_author_stats(self) -> Dict[str, Any]:
        """Get statistics about authors in the library."""
        return self.db.authors.get_author_stats()
    
    def get_books_by_author(
        self, 
        author_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get books by a specific author.
        
        Args:
            author_id: ID of the author
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            Dictionary containing paginated results and metadata
        """
        # Get books from repository
        books_data = self.db.authors.get_books_by_author(
            author_id=author_id,
            limit=limit,
            offset=offset
        )
        
        # Convert to Pydantic models
        books = [BookSearchResult(**book) for book in books_data]
        
        # Get total count for pagination
        # Note: This could be optimized with a separate count query if needed
        total = len(books)
        
        return self._paginate_results(books, total, offset // limit + 1, limit)
    
    def get_authors_by_letter(self, letter: str) -> List[Author]:
        """Get all authors whose names start with the given letter."""
        if len(letter) != 1 or not letter.isalpha():
            return []
            
        authors_data = self.db.authors.search_authors(
            query=f"{letter.lower()}%",
            limit=1000
        )
        return [Author(**author) for author in authors_data]
