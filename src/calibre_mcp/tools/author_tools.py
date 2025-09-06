"""
MCP tools for author-related operations.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .base_tool import BaseTool, mcp_tool

class Author(BaseModel):
    """Author model."""
    id: int = Field(..., description="Unique author ID")
    name: str = Field(..., description="Author's name")
    sort: str = Field(..., description="Sortable version of author's name")
    book_count: int = Field(0, description="Number of books by this author")
    
    class Config:
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }

class AuthorSearchInput(BaseModel):
    """Input model for author search."""
    query: Optional[str] = Field(
        None,
        description="Search query to filter authors by name"
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

class AuthorSearchOutput(BaseModel):
    """Output model for paginated author search results."""
    items: List[Author] = Field(
        ...,
        description="List of matching authors"
    )
    total: int = Field(
        ...,
        description="Total number of matching authors"
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

class AuthorBooksOutput(BaseModel):
    """Output model for an author's books."""
    author: Author = Field(
        ...,
        description="Author information"
    )
    books: List[Dict[str, Any]] = Field(
        ...,
        description="List of books by this author"
    )
    total: int = Field(
        ...,
        description="Total number of books by this author"
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

class AuthorStats(BaseModel):
    """Author statistics model."""
    total_authors: int = Field(..., description="Total number of authors")
    top_authors: List[Dict[str, Any]] = Field(..., description="Authors with most books")
    authors_by_letter: List[Dict[str, Any]] = Field(..., description="Author count by first letter")

class AuthorTools(BaseTool):
    """MCP tools for author-related operations."""
    
    @mcp_tool(
        name="list_authors",
        description="Search and list authors with filtering and pagination",
        input_model=AuthorSearchInput,
        output_model=AuthorSearchOutput
    )
    async def list_authors(
        self,
        query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search and list authors with optional name filtering.
        
        This tool allows searching through all authors in the library with
        flexible name-based filtering. Results are paginated for efficient
        browsing of large author lists.
        
        Example:
            # Search for authors with "martin" in the name
            list_authors(query="martin")
            
            # Get second page of authors
            list_authors(limit=20, offset=20)
        """
        return await self.author_service.search_authors(
            query=query,
            limit=limit,
            offset=offset
        )
    
    @mcp_tool(
        name="get_author",
        description="Get detailed information about an author by ID",
        output_model=Author
    )
    async def get_author(self, author_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific author.
        
        Args:
            author_id: The unique identifier of the author
            
        Returns:
            Author information or None if not found
            
        Example:
            # Get details for author with ID 42
            get_author(author_id=42)
        """
        author = await self.author_service.get_author(author_id)
        return author.dict() if author else None
    
    @mcp_tool(
        name="get_author_books",
        description="Get all books by a specific author",
        output_model=AuthorBooksOutput
    )
    async def get_author_books(
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
            limit: Maximum number of books to return (default: 50)
            offset: Number of books to skip (for pagination)
            
        Returns:
            Dictionary containing author information and paginated list of books
            
        Example:
            # Get first page of books by author with ID 42
            get_author_books(author_id=42, limit=10, offset=0)
            
            # Get next page
            get_author_books(author_id=42, limit=10, offset=10)
        """
        # Get author info
        author = await self.author_service.get_author(author_id)
        if not author:
            return {
                'author': None,
                'books': [],
                'total': 0,
                'page': 1,
                'per_page': limit,
                'total_pages': 0
            }
        
        # Get author's books
        result = await self.author_service.get_books_by_author(
            author_id=author_id,
            limit=limit,
            offset=offset
        )
        
        return {
            'author': author.dict(),
            'books': result['items'],
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'total_pages': result['total_pages']
        }
    
    @mcp_tool(
        name="get_author_stats",
        description="Get statistics about authors in the library",
        output_model=AuthorStats
    )
    async def get_author_stats(self) -> Dict[str, Any]:
        """
        Get statistics about authors in the library.
        
        Returns information such as total number of authors, 
        authors with the most books, and distribution of authors
        by the first letter of their names.
        
        Example:
            # Get author statistics
            get_author_stats()
        """
        return await self.author_service.get_author_stats()
    
    @mcp_tool(
        name="get_authors_by_letter",
        description="Get authors whose names start with a specific letter",
        output_model=List[Author]
    )
    async def get_authors_by_letter(self, letter: str) -> List[Dict[str, Any]]:
        """
        Get all authors whose names start with the specified letter.
        
        Args:
            letter: The starting letter (case-insensitive)
            
        Returns:
            List of authors whose names start with the specified letter
            
        Example:
            # Get all authors whose names start with 'A'
            get_authors_by_letter(letter='A')
        """
        authors = await self.author_service.get_authors_by_letter(letter.upper())
        return [author.dict() for author in authors]
