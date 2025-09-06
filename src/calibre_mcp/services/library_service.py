"""
Service for handling library-level operations.
"""
from typing import Dict, List, Optional, Any
import os
from pathlib import Path
from pydantic import BaseModel, Field
from ..db import get_database
from .base_service import BaseService
from .book_service import BookSearchResult

class LibraryStats(BaseModel):
    """Library statistics model."""
    total_books: int = Field(..., description="Total number of books")
    total_authors: int = Field(..., description="Total number of unique authors")
    total_series: int = Field(..., description="Total number of series")
    total_tags: int = Field(..., description="Total number of unique tags")
    formats: List[Dict[str, Any]] = Field(..., description="Book counts by format")
    ratings: List[Dict[str, Any]] = Field(..., description="Book counts by rating")
    recent_books: List[BookSearchResult] = Field(..., description="Recently added books")

class LibraryService(BaseService):
    """Service for library-level operations."""
    
    def __init__(self, db=None):
        """Initialize with an optional database instance."""
        super().__init__(db or get_database())
    
    def get_library_stats(self) -> LibraryStats:
        """Get comprehensive library statistics."""
        # Get basic stats
        stats = self.db.books.get_library_stats()
        
        # Get recent books
        recent_books_data = stats.pop('recent_books', [])
        recent_books = [BookSearchResult(**book) for book in recent_books_data]
        
        return LibraryStats(
            total_books=stats.get('total_books', 0),
            total_authors=stats.get('total_authors', 0),
            total_series=stats.get('total_series', 0),
            total_tags=stats.get('total_tags', 0),
            formats=stats.get('formats', []),
            ratings=stats.get('ratings', []),
            recent_books=recent_books
        )
    
    def search_across_library(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search across all library content (books, authors, series, tags).
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            Dictionary containing search results and metadata
        """
        # Search books
        book_results = self.db.books.search_books(
            query=query,
            limit=limit,
            offset=offset
        )
        
        # Search authors
        author_results = self.db.authors.search_authors(
            query=query,
            limit=limit
        )
        
        # Convert to Pydantic models
        books = [BookSearchResult(**book) for book in book_results['items']]
        authors = [
            {
                'id': author['id'],
                'name': author['name'],
                'book_count': author['book_count']
            }
            for author in author_results['items']
        ]
        
        # Combine results
        total_results = book_results['total'] + len(authors)
        
        return {
            'books': books,
            'authors': authors,
            'total_results': total_results,
            'page': offset // limit + 1,
            'per_page': limit,
            'total_pages': (total_results + limit - 1) // limit if total_results > 0 else 1
        }
    
    def get_library_health(self) -> Dict[str, Any]:
        """Get library health information."""
        # This is a placeholder for more comprehensive health checks
        stats = self.get_library_stats()
        
        health = {
            'status': 'healthy',
            'checks': [
                {
                    'name': 'database_connection',
                    'status': 'ok',
                    'message': 'Database connection is healthy'
                },
                {
                    'name': 'book_count',
                    'status': 'ok' if stats.total_books > 0 else 'warning',
                    'message': f'Found {stats.total_books} books in library',
                    'metric': stats.total_books
                },
                {
                    'name': 'author_count',
                    'status': 'ok' if stats.total_authors > 0 else 'warning',
                    'message': f'Found {stats.total_authors} unique authors',
                    'metric': stats.total_authors
                }
            ]
        }
        
        # Update overall status if any checks failed
        if any(check['status'] != 'ok' for check in health['checks']):
            health['status'] = 'warning'
        
        return health
