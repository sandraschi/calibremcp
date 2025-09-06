"""
Repository for handling library-related database operations using SQLAlchemy ORM.
"""
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import joinedload

from ...db import BaseRepository
from ...models import Book, Author, Series, Tag, Rating, Data, Comment

class LibraryRepository(BaseRepository):
    """Repository for library-related database operations using SQLAlchemy ORM."""
    
    def __init__(self, db):
        super().__init__(db, None)  # No single model for the library
    
    def get_library_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the library.
        
        Returns:
            Dictionary containing library statistics
        """
        with self._db.session_scope() as session:
            # Basic counts
            stats = {
                'total_books': session.query(func.count(Book.id)).scalar(),
                'total_authors': session.query(func.count(Author.id)).scalar(),
                'total_series': session.query(func.count(Series.id)).scalar(),
                'total_tags': session.query(func.count(Tag.id)).scalar(),
            }
            
            # Books by format
            formats = (
                session.query(
                    Data.format,
                    func.count(Data.id).label('count')
                )
                .group_by(Data.format)
                .order_by(desc('count'))
                .all()
            )
            stats['formats'] = [{'format': f, 'count': c} for f, c in formats]
            
            # Books added in the last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            stats['recently_added'] = (
                session.query(func.count(Book.id))
                .filter(Book.timestamp >= thirty_days_ago)
                .scalar()
            )
            
            # Top tags
            top_tags = (
                session.query(
                    Tag.name,
                    func.count(Book.id).label('book_count')
                )
                .join(Tag.books)
                .group_by(Tag.id, Tag.name)
                .order_by(desc('book_count'))
                .limit(10)
                .all()
            )
            stats['top_tags'] = [{'name': name, 'count': count} for name, count in top_tags]
            
            # Top series
            top_series = (
                session.query(
                    Series.name,
                    func.count(Book.id).label('book_count')
                )
                .join(Series.books)
                .group_by(Series.id, Series.name)
                .order_by(desc('book_count'))
                .limit(10)
                .all()
            )
            stats['top_series'] = [{'name': name, 'count': count} for name, count in top_series]
            
            # Ratings distribution
            ratings = (
                session.query(
                    Rating.rating,
                    func.count(Book.id).label('book_count')
                )
                .join(Rating.books)
                .group_by(Rating.rating)
                .order_by(Rating.rating.desc())
                .all()
            )
            stats['ratings'] = [{'rating': r, 'count': c} for r, c in ratings]
            
            # Publication years
            pub_years = (
                session.query(
                    func.strftime('%Y', Book.pubdate).label('year'),
                    func.count(Book.id).label('count')
                )
                .filter(Book.pubdate.isnot(None))
                .group_by('year')
                .order_by(desc('count'))
                .limit(10)
                .all()
            )
            stats['publication_years'] = [{'year': y, 'count': c} for y, c in pub_years]
            
            return stats
    
    def search_across_library(
        self,
        query: str,
        limit: int = 20
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across books, authors, and series with a single query.
        
        Args:
            query: Search term
            limit: Maximum number of results per category
            
        Returns:
            Dictionary with search results grouped by type
        """
        if not query:
            return {'books': [], 'authors': [], 'series': []}
            
        search = f"%{query}%"
        
        with self._db.session_scope() as session:
            # Search books
            books = (
                session.query(Book)
                .options(joinedload(Book.authors))
                .filter(Book.title.ilike(search))
                .order_by(Book.sort)
                .limit(limit)
                .all()
            )
            
            # Search authors
            authors = (
                session.query(Author)
                .filter(Author.name.ilike(search))
                .order_by(Author.sort)
                .limit(limit)
                .all()
            )
            
            # Search series
            series = (
                session.query(Series)
                .filter(Series.name.ilike(search))
                .order_by(Series.name)
                .limit(limit)
                .all()
            )
            
            # Format results
            return {
                'books': [
                    {
                        'id': b.id,
                        'title': b.title,
                        'authors': [{'id': a.id, 'name': a.name} for a in b.authors],
                        'has_cover': bool(b.has_cover)
                    }
                    for b in books
                ],
                'authors': [
                    {
                        'id': a.id,
                        'name': a.name,
                        'book_count': len(a.books)
                    }
                    for a in authors
                ],
                'series': [
                    {
                        'id': s.id,
                        'name': s.name,
                        'book_count': len(s.books)
                    }
                    for s in series
                ]
            }
    
    def get_recently_added(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recently added books.
        
        Args:
            limit: Maximum number of books to return
            
        Returns:
            List of recently added books with basic info
        """
        with self._db.session_scope() as session:
            books = (
                session.query(Book)
                .options(joinedload(Book.authors))
                .order_by(Book.timestamp.desc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    'id': b.id,
                    'title': b.title,
                    'authors': [{'id': a.id, 'name': a.name} for a in b.authors],
                    'timestamp': b.timestamp.isoformat() if b.timestamp else None,
                    'has_cover': bool(b.has_cover)
                }
                for b in books
            ]
    
    def get_recently_modified(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recently modified books.
        
        Args:
            limit: Maximum number of books to return
            
        Returns:
            List of recently modified books with basic info
        """
        with self._db.session_scope() as session:
            books = (
                session.query(Book)
                .options(joinedload(Book.authors))
                .order_by(Book.last_modified.desc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    'id': b.id,
                    'title': b.title,
                    'authors': [{'id': a.id, 'name': a.name} for a in b.authors],
                    'last_modified': b.last_modified.isoformat() if b.last_modified else None,
                    'has_cover': bool(b.has_cover)
                }
                for b in books
            ]
    
    def get_books_without_metadata(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get books that are missing important metadata.
        
        Args:
            limit: Maximum number of books to return
            
        Returns:
            List of books missing metadata
        """
        with self._db.session_scope() as session:
            # Find books missing authors, description, or publication date
            books = (
                session.query(Book)
                .options(joinedload(Book.authors))
                .outerjoin(Book.comments)
                .group_by(Book.id)
                .having(
                    or_(
                        func.count(Book.authors) == 0,  # No authors
                        func.count(Comment.id) == 0,     # No description
                        Book.pubdate.is_(None)           # No publication date
                    )
                )
                .order_by(Book.timestamp.desc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    'id': b.id,
                    'title': b.title or 'Untitled',
                    'authors': [{'id': a.id, 'name': a.name} for a in b.authors],
                    'missing': []
                }
                for b in books
            ]
