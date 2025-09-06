"""
Service for handling book-related operations.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from ..db import get_database
from .base_service import BaseService

class BookSearchResult(BaseModel):
    """Model for book search results."""
    id: int = Field(..., description="Unique book ID")
    title: str = Field(..., description="Book title")
    authors: List[str] = Field(..., description="List of authors")
    series: Optional[str] = Field(None, description="Series name if part of a series")
    series_index: Optional[float] = Field(None, description="Position in series")
    rating: Optional[float] = Field(None, description="Rating (0-5)")
    tags: List[str] = Field(default_factory=list, description="Book tags/categories")
    formats: List[str] = Field(default_factory=list, description="Available formats")
    has_cover: bool = Field(False, description="Whether the book has a cover")
    timestamp: Optional[datetime] = Field(None, description="When the book was added")
    publisher: Optional[str] = Field(None, description="Publisher name")
    language: Optional[str] = Field(None, description="Language code")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class BookDetail(BookSearchResult):
    """Detailed book information."""
    isbn: Optional[str] = Field(None, description="ISBN")
    comments: Optional[str] = Field(None, description="Book description/comments")
    identifiers: Dict[str, str] = Field(default_factory=dict, description="Additional identifiers")
    pubdate: Optional[datetime] = Field(None, description="Publication date")
    last_modified: Optional[datetime] = Field(None, description="When the book was last modified")
    path: Optional[str] = Field(None, description="Relative path to book files")
    
    class Config(BookSearchResult.Config):
        pass

class BookService(BaseService):
    """Service for book-related operations."""
    
    def __init__(self, db=None):
        """Initialize with an optional database instance."""
        super().__init__(db or get_database())
    
    def get_book(self, book_id: int) -> Optional[BookDetail]:
        """Get detailed information about a book by ID."""
        book_data = self.db.books.get_book_by_id(book_id)
        if not book_data:
            return None
        return BookDetail(**book_data)
    
    def search_books(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        series: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for books with optional filters.
        
        Args:
            query: Search query (searches in title, authors, tags, series, comments)
            author: Filter by author name
            tag: Filter by tag
            series: Filter by series name
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            Dictionary containing paginated results and metadata
        """
        # Get books from repository
        books_data = self.db.books.search_books(
            query=query,
            author=author,
            tag=tag,
            series=series,
            limit=limit,
            offset=offset
        )
        
        # Convert to Pydantic models
        books = [BookSearchResult(**book) for book in books_data]
        
        # Get total count for pagination
        # Note: This could be optimized with a separate count query if needed
        total = len(books)
        
        return self._paginate_results(books, total, offset // limit + 1, limit)
    
    def get_library_stats(self) -> Dict[str, Any]:
        """Get statistics about the library."""
        return self.db.books.get_library_stats()
    
    def get_books_by_series(self, series_id: int) -> List[BookSearchResult]:
        """Get all books in a series."""
        books_data = self.db.books.search_books(series_id=series_id, limit=1000)
        return [BookSearchResult(**book) for book in books_data]
    
    def get_books_by_author(self, author_id: int) -> List[BookSearchResult]:
        """Get all books by an author."""
        books_data = self.db.authors.get_books_by_author(author_id, limit=1000)
        return [BookSearchResult(**book) for book in books_data]
    
    def get_recent_books(self, limit: int = 10) -> List[BookSearchResult]:
        """Get the most recently added books."""
        books_data = self.db.books.search_books(limit=limit, order_by='timestamp', ascending=False)
        return [BookSearchResult(**book) for book in books_data]
