"""
MCP tools for book-related operations.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ..services.book_service import BookSearchResult, BookDetail
from .base_tool import BaseTool, mcp_tool

class BookSearchInput(BaseModel):
    """Input model for book search."""
    query: Optional[str] = Field(
        None,
        description="Search query (searches in title, authors, tags, series, comments)"
    )
    author: Optional[str] = Field(
        None,
        description="Filter by author name"
    )
    tag: Optional[str] = Field(
        None,
        description="Filter by tag"
    )
    series: Optional[str] = Field(
        None,
        description="Filter by series name"
    )
    limit: int = Field(
        50,
        description="Maximum number of results to return",
        ge=1,
        le=1000
    )
    offset: int = Field(
        0,
        description="Number of results to skip (for pagination)",
        ge=0
    )

class BookSearchResultOutput(BookSearchResult):
    """Output model for book search results."""
    class Config:
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }

class BookSearchOutput(BaseModel):
    """Output model for paginated book search results."""
    items: List[BookSearchResultOutput] = Field(
        ...,
        description="List of matching books"
    )
    total: int = Field(
        ...,
        description="Total number of matching books"
    )
    page: int = Field(
        ...,
        description="Current page number"
    )
    per_page: int = Field(
        ...,
        description="Number of items per page"
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages"
    )

class BookDetailOutput(BookDetail):
    """Output model for book details."""
    class Config:
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }

class BookTools(BaseTool):
    """MCP tools for book-related operations."""
    
    @mcp_tool(
        name="list_books",
        description="Search and list books with filtering and pagination",
        input_model=BookSearchInput,
        output_model=BookSearchOutput
    )
    async def list_books(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        series: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search and list books with various filters.
        
        This tool allows searching through the entire library with flexible filtering
        by title, author, tags, and series. Results are paginated for efficient
        browsing of large libraries.
        
        Example:
            # Search for books about Python
            list_books(query="python")
            
            # Get books by a specific author
            list_books(author="Martin Fowler")
            
            # Get books in a series
            list_books(series="The Lord of the Rings")
        """
        return self.book_service.search_books(
            query=query,
            author=author,
            tag=tag,
            series=series,
            limit=limit,
            offset=offset
        )
    
    @mcp_tool(
        name="get_book",
        description="Get detailed information about a book by ID",
        output_model=BookDetailOutput
    )
    async def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific book.
        
        This tool retrieves comprehensive information about a book, including
        all metadata, formats, and related entities like authors, series, and tags.
        
        Args:
            book_id: The unique identifier of the book
            
        Returns:
            Detailed book information or None if not found
            
        Example:
            # Get details for book with ID 123
            get_book(book_id=123)
        """
        book = self.book_service.get_book(book_id)
        return book.dict() if book else None
    
    @mcp_tool(
        name="get_recent_books",
        description="Get recently added books",
        output_model=List[BookSearchResultOutput]
    )
    async def get_recent_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get a list of the most recently added books.
        
        This is useful for displaying a "recently added" section in the UI.
        
        Args:
            limit: Maximum number of recent books to return (default: 10)
            
        Returns:
            List of recently added books
            
        Example:
            # Get 5 most recently added books
            get_recent_books(limit=5)
        """
        books = self.book_service.get_recent_books(limit=limit)
        return [book.dict() for book in books]
    
    @mcp_tool(
        name="get_books_by_series",
        description="Get all books in a series",
        output_model=List[BookSearchResultOutput]
    )
    async def get_books_by_series(self, series_id: int) -> List[Dict[str, Any]]:
        """
        Get all books that belong to a specific series.
        
        Books are returned in series order (based on series_index).
        
        Args:
            series_id: The ID of the series
            
        Returns:
            List of books in the series, ordered by series index
            
        Example:
            # Get all books in series with ID 42
            get_books_by_series(series_id=42)
        """
        books = self.book_service.get_books_by_series(series_id)
        return [book.dict() for book in books]
    
    @mcp_tool(
        name="get_books_by_author",
        description="Get all books by a specific author",
        output_model=List[BookSearchResultOutput]
    )
    async def get_books_by_author(
        self, 
        author_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get all books written by a specific author.
        
        Results are paginated for efficient browsing of large collections.
        
        Args:
            author_id: The ID of the author
            limit: Maximum number of results to return (default: 50)
            offset: Number of results to skip (for pagination)
            
        Returns:
            Paginated list of books by the author
            
        Example:
            # Get first page of books by author with ID 42
            get_books_by_author(author_id=42, limit=10, offset=0)
            
            # Get next page
            get_books_by_author(author_id=42, limit=10, offset=10)
        """
        return self.author_service.get_books_by_author(
            author_id=author_id,
            limit=limit,
            offset=offset
        )
