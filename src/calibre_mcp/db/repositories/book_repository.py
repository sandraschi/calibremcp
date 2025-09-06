"""
Repository for handling book-related database operations using SQLAlchemy ORM.
"""
from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import or_, and_, func, desc, asc, text

from ...db import BaseRepository
from ...models import Book, Author, Tag, Series, Rating, Comment, Data, Identifier

class BookRepository(BaseRepository[Book]):
    """Repository for book-related database operations using SQLAlchemy ORM."""
    
    def __init__(self, db):
        super().__init__(db, Book)
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a book by its ID with all related data.
        
        Args:
            book_id: The ID of the book to retrieve
            
        Returns:
            Dictionary containing book data or None if not found
        """
        with self._db.session_scope() as session:
            book = (
                session.query(Book)
                .options(
                    joinedload(Book.authors),
                    joinedload(Book.tags),
                    joinedload(Book.series),
                    joinedload(Book.ratings),
                    joinedload(Book.comments),
                    joinedload(Book.data),
                    joinedload(Book.identifiers)
                )
                .filter(Book.id == book_id)
                .first()
            )
            
            if not book:
                return None
                
            return self._format_book(book)
    
    def search_books(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        series: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = 'title',
        sort_order: str = 'asc'
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search for books with various filters and sorting options.
        
        Args:
            query: Search term to match against title, author, tags, etc.
            author: Filter by author name
            tag: Filter by tag name
            series: Filter by series name
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            sort_by: Field to sort by (title, author, series, rating, date_added, pubdate)
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Tuple of (list of book dictionaries, total count)
        """
        with self._db.session_scope() as session:
            # Start building the query
            query_obj = session.query(Book).options(
                joinedload(Book.authors),
                joinedload(Book.tags),
                joinedload(Book.series),
                joinedload(Book.ratings)
            )
            
            # Apply filters
            if query:
                search = f"%{query}%"
                query_obj = query_obj.join(Book.authors, isouter=True)
                query_obj = query_obj.filter(
                    or_(
                        Book.title.ilike(search),
                        Author.name.ilike(search),
                        Book.comments.any(Comment.text.ilike(search))
                    )
                )
                
            if author:
                query_obj = query_obj.join(Book.authors)
                query_obj = query_obj.filter(Author.name.ilike(f"%{author}%"))
                
            if tag:
                query_obj = query_obj.join(Book.tags)
                query_obj = query_obj.filter(Tag.name.ilike(f"%{tag}%"))
                
            if series:
                query_obj = query_obj.join(Book.series)
                query_obj = query_obj.filter(Series.name.ilike(f"%{series}%"))
            
            # Get total count before pagination
            total = query_obj.with_entities(func.count(Book.id)).scalar()
            
            # Apply sorting
            sort_field = self._get_sort_field(sort_by)
            if sort_field is not None:
                if sort_order.lower() == 'desc':
                    sort_field = desc(sort_field)
                query_obj = query_obj.order_by(sort_field)
            
            # Apply pagination
            query_obj = query_obj.offset(offset).limit(limit)
            
            # Execute query and format results
            books = query_obj.all()
            return [self._format_book(book) for book in books], total
    
    def get_recent_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recently added books.
        
        Args:
            limit: Maximum number of books to return
            
        Returns:
            List of recently added books
        """
        with self._db.session_scope() as session:
            books = (
                session.query(Book)
                .options(
                    joinedload(Book.authors),
                    joinedload(Book.series)
                )
                .order_by(desc(Book.timestamp))
                .limit(limit)
                .all()
            )
            return [self._format_book(book) for book in books]
    
    def get_books_by_series(self, series_id: int) -> List[Dict[str, Any]]:
        """
        Get all books in a series, ordered by series index.
        
        Args:
            series_id: ID of the series
            
        Returns:
            List of books in the series
        """
        with self._db.session_scope() as session:
            books = (
                session.query(Book)
                .options(
                    joinedload(Book.authors),
                    joinedload(Book.ratings)
                )
                .join(Book.series)
                .filter(Series.id == series_id)
                .order_by(Book.series_index)
                .all()
            )
            return [self._format_book(book) for book in books]
    
    def get_books_by_author(
        self, 
        author_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get books by a specific author with pagination.
        
        Args:
            author_id: ID of the author
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            Tuple of (list of book dictionaries, total count)
        """
        with self._db.session_scope() as session:
            # Get total count
            total = (
                session.query(func.count(Book.id))
                .join(Book.authors)
                .filter(Author.id == author_id)
                .scalar()
            )
            
            # Get paginated results
            books = (
                session.query(Book)
                .options(
                    joinedload(Book.authors),
                    joinedload(Book.series),
                    joinedload(Book.ratings)
                )
                .join(Book.authors)
                .filter(Author.id == author_id)
                .order_by(Book.sort, Book.pubdate.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            
            return [self._format_book(book) for book in books], total
    
    def _format_book(self, book: Book) -> Dict[str, Any]:
        """
        Format a Book object into a dictionary.
        
        Args:
            book: The Book object to format
            
        Returns:
            Dictionary with book data
        """
        if not book:
            return None
            
        return {
            'id': book.id,
            'title': book.title,
            'sort': book.sort,
            'timestamp': book.timestamp.isoformat() if book.timestamp else None,
            'pubdate': book.pubdate.isoformat() if book.pubdate else None,
            'series_index': book.series_index,
            'author_sort': book.author_sort,
            'isbn': book.isbn,
            'lccn': book.lccn,
            'path': book.path,
            'has_cover': bool(book.has_cover),
            'last_modified': book.last_modified.isoformat() if book.last_modified else None,
            'authors': [{'id': a.id, 'name': a.name} for a in book.authors],
            'tags': [{'id': t.id, 'name': t.name} for t in book.tags],
            'series': book.series[0].name if book.series else None,
            'series_id': book.series[0].id if book.series else None,
            'rating': book.ratings[0].rating if book.ratings else 0,
            'comment': book.comments[0].text if book.comments else None,
            'formats': [{
                'format': d.format,
                'size': d.uncompressed_size,
                'name': d.name
            } for d in book.data],
            'identifiers': {i.type: i.val for i in book.identifiers}
        }
    
    def _get_sort_field(self, sort_by: str):
        """
        Get the SQLAlchemy field to sort by.
        
        Args:
            sort_by: Field name to sort by
            
        Returns:
            SQLAlchemy column expression or None if invalid
        """
        sort_fields = {
            'title': Book.sort,
            'author': Book.author_sort,
            'series': Book.series_index,
            'rating': Book.ratings.any(Rating.rating),
            'date_added': Book.timestamp,
            'pubdate': Book.pubdate,
            'size': Book.data.any(Data.uncompressed_size)
        }
        return sort_fields.get(sort_by.lower(), Book.sort)
        """Search for books with optional filters."""
        base_query = """
            SELECT b.*, 
                   GROUP_CONCAT(DISTINCT a.name, '|') as authors,
                   GROUP_CONCAT(DISTINCT t.name, '|') as tags,
                   s.name as series_name,
                   b.series_index as series_index,
                   r.rating as rating,
                   p.name as publisher,
                   l.lang_code as language
            FROM books b
            LEFT JOIN books_authors_link bal ON b.id = bal.book
            LEFT JOIN authors a ON bal.author = a.id
            LEFT JOIN books_tags_link btl ON b.id = btl.book
            LEFT JOIN tags t ON btl.tag = t.id
            LEFT JOIN books_series_link bsl ON b.id = bsl.book
            LEFT JOIN series s ON bsl.series = s.id
            LEFT JOIN books_ratings_link brl ON b.id = brl.book
            LEFT JOIN ratings r ON brl.rating = r.id
            LEFT JOIN books_publishers_link bpl ON b.id = bpl.book
            LEFT JOIN publishers p ON bpl.publisher = p.id
            LEFT JOIN books_languages_link bll ON b.id = bll.book
            LEFT JOIN languages l ON bll.lang_code = l.id
        """
        
        conditions = []
        params = []
        
        if query:
            conditions.append("""
                (b.title LIKE ? OR 
                 b.comments LIKE ? OR 
                 a.name LIKE ? OR 
                 t.name LIKE ? OR 
                 s.name LIKE ?)
            """)
            search_term = f"%{query}%"
            params.extend([search_term] * 5)
            
        if author:
            conditions.append("a.name LIKE ?")
            params.append(f"%{author}%")
            
        if tag:
            conditions.append("t.name LIKE ?")
            params.append(f"%{tag}%")
            
        if series:
            conditions.append("s.name LIKE ?")
            params.append(f"%{series}%")
        
        # Build the WHERE clause
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        # Add GROUP BY and ORDER BY
        full_query = f"""
            {base_query}
            {where_clause}
            GROUP BY b.id
            ORDER BY b.sort
            LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        
        # Execute the query
        results = self._fetch_all(full_query, tuple(params))
        
        # Process the results
        return [self._process_book_result(row) for row in results]
    
    def get_books_by_ids(self, book_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple books by their IDs."""
        if not book_ids:
            return []
            
        placeholders = ','.join('?' * len(book_ids))
        query = f"""
            SELECT b.*, 
                   GROUP_CONCAT(DISTINCT a.name, '|') as authors,
                   GROUP_CONCAT(DISTINCT t.name, '|') as tags,
                   s.name as series_name,
                   b.series_index as series_index,
                   r.rating as rating,
                   p.name as publisher,
                   l.lang_code as language
            FROM books b
            LEFT JOIN books_authors_link bal ON b.id = bal.book
            LEFT JOIN authors a ON bal.author = a.id
            LEFT JOIN books_tags_link btl ON b.id = btl.book
            LEFT JOIN tags t ON btl.tag = t.id
            LEFT JOIN books_series_link bsl ON b.id = bsl.book
            LEFT JOIN series s ON bsl.series = s.id
            LEFT JOIN books_ratings_link brl ON b.id = brl.book
            LEFT JOIN ratings r ON brl.rating = r.id
            LEFT JOIN books_publishers_link bpl ON b.id = bpl.book
            LEFT JOIN publishers p ON bpl.publisher = p.id
            LEFT JOIN books_languages_link bll ON b.id = bll.book
            LEFT JOIN languages l ON bll.lang_code = l.id
            WHERE b.id IN ({placeholders})
            GROUP BY b.id
            ORDER BY b.sort
        """
        
        results = self._fetch_all(query, book_ids)
        return [self._process_book_result(row) for row in results]
    
    def get_library_stats(self) -> Dict[str, Any]:
        """Get library statistics."""
        stats = {}
        
        # Total books
        stats['total_books'] = self._fetch_one("SELECT COUNT(*) as count FROM books")['count']
        
        # Total authors
        stats['total_authors'] = self._fetch_one("SELECT COUNT(DISTINCT author) as count FROM books_authors_link")['count']
        
        # Total series
        stats['total_series'] = self._fetch_one("SELECT COUNT(DISTINCT series) as count FROM books_series_link")['count']
        
        # Total tags
        stats['total_tags'] = self._fetch_one("SELECT COUNT(DISTINCT tag) as count FROM books_tags_link")['count']
        
        # Books by format
        stats['formats'] = self._fetch_all("""
            SELECT format, COUNT(*) as count 
            FROM data 
            GROUP BY format 
            ORDER BY count DESC
        """)
        
        # Books by rating
        stats['ratings'] = self._fetch_all("""
            SELECT r.rating, COUNT(*) as count 
            FROM books_ratings_link brl
            JOIN ratings r ON brl.rating = r.id
            GROUP BY r.rating
            ORDER BY r.rating DESC
        """)
        
        # Recent additions
        stats['recent_books'] = self._fetch_all("""
            SELECT b.id, b.title, b.timestamp
            FROM books b
            ORDER BY b.timestamp DESC
            LIMIT 10
        """)
        
        return stats
    
    def _process_book_result(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Process a book result row into a more usable format."""
        if not row:
            return {}
            
        # Convert timestamp to datetime
        timestamp = row.get('timestamp')
        if timestamp and isinstance(timestamp, str):
            try:
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        
        # Process authors and tags from pipe-separated strings to lists
        authors = row.get('authors', '').split('|') if row.get('authors') else []
        tags = row.get('tags', '').split('|') if row.get('tags') else []
        
        # Create the book dictionary
        book = {
            'id': row['id'],
            'title': row['title'],
            'sort': row.get('sort'),
            'timestamp': timestamp,
            'pubdate': row.get('pubdate'),
            'series_index': row.get('series_index', 0.0),
            'author_sort': row.get('author_sort'),
            'isbn': row.get('isbn'),
            'lccn': row.get('lccn'),
            'path': row.get('path'),
            'flags': row.get('flags', 0),
            'uuid': row.get('uuid'),
            'has_cover': bool(row.get('has_cover', 0)),
            'last_modified': row.get('last_modified'),
            'authors': [a for a in authors if a],  # Remove empty strings
            'tags': [t for t in tags if t],  # Remove empty strings
            'series': row.get('series_name'),
            'rating': row.get('rating'),
            'publisher': row.get('publisher'),
            'language': row.get('language'),
            'comments': row.get('comments'),
        }
        
        return book
