"""
Repository for handling author-related database operations using SQLAlchemy ORM.
"""
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import func, desc, asc, or_

from ...db import BaseRepository
from ...models import Author, Book

class AuthorRepository(BaseRepository[Author]):
    """Repository for author-related database operations using SQLAlchemy ORM."""
    
    def __init__(self, db):
        super().__init__(db, Author)
    
    def get_author_by_id(self, author_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an author by ID with related book count.
        
        Args:
            author_id: The ID of the author to retrieve
            
        Returns:
            Dictionary containing author data or None if not found
        """
        with self._db.session_scope() as session:
            # Get author with book count using a subquery
            stmt = (
                session.query(
                    Author,
                    func.count(Book.id).label('book_count')
                )
                .outerjoin(Author.books)
                .group_by(Author.id)
                .filter(Author.id == author_id)
            )
            
            result = stmt.first()
            if not result:
                return None
                
            author, book_count = result
            return self._format_author(author, book_count)
    
    def get_authors(
        self, 
        query: Optional[str] = None, 
        sort_by: str = 'name',
        ascending: bool = True,
        limit: int = 50,
        offset: int = 0,
        with_books: bool = False
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get a list of authors with optional filtering, sorting, and pagination.
        
        Args:
            query: Search term to match against author names
            sort_by: Field to sort by (name, book_count, sort)
            ascending: Sort in ascending order if True, descending if False
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            with_books: If True, include list of book IDs for each author
            
        Returns:
            Tuple of (list of author dictionaries, total count)
        """
        with self._db.session_scope() as session:
            # Start with a base query to get authors and their book counts
            query_obj = (
                session.query(
                    Author,
                    func.count(Book.id).label('book_count')
                )
                .outerjoin(Author.books)
                .group_by(Author.id)
            )
            
            # Apply search filter if provided
            if query:
                search = f"%{query}%"
                query_obj = query_obj.filter(Author.name.ilike(search))
            
            # Get total count before pagination
            total = query_obj.with_entities(func.count(Author.id)).scalar()
            
            # Apply sorting
            sort_field = self._get_sort_field(sort_by)
            if sort_field is not None:
                if not ascending:
                    sort_field = desc(sort_field)
                query_obj = query_obj.order_by(sort_field)
            
            # Apply pagination
            query_obj = query_obj.offset(offset).limit(limit)
            
            # Execute query
            results = query_obj.all()
            
            # Format results
            authors = []
            for author, book_count in results:
                author_data = self._format_author(author, book_count)
                if with_books:
                    author_data['books'] = [book.id for book in author.books]
                authors.append(author_data)
            
            return authors, total
    
    def get_author_stats(self) -> Dict[str, Any]:
        """
        Get statistics about authors in the library.
        
        Returns:
            Dictionary containing author statistics
        """
        with self._db.session_scope() as session:
            # Total number of authors
            total_authors = session.query(func.count(Author.id)).scalar()
            
            # Number of authors with only one book
            single_book_authors = (
                session.query(func.count(Author.id))
                .join(Author.books)
                .group_by(Author.id)
                .having(func.count(Book.id) == 1)
                .subquery()
            )
            
            single_book_count = session.query(func.count()).select_from(single_book_authors).scalar() or 0
            
            # Top 10 most prolific authors
            top_authors = (
                session.query(
                    Author.name,
                    func.count(Book.id).label('book_count')
                )
                .join(Author.books)
                .group_by(Author.id, Author.name)
                .order_by(desc('book_count'))
                .limit(10)
                .all()
            )
            
            # Author name length statistics
            name_lengths = (
                session.query(
                    func.min(func.length(Author.name)).label('min_length'),
                    func.max(func.length(Author.name)).label('max_length'),
                    func.avg(func.length(Author.name)).label('avg_length')
                )
                .scalar()
            )
            
            return {
                'total_authors': total_authors,
                'authors_with_single_book': single_book_count,
                'top_authors': [
                    {'name': name, 'book_count': count}
                    for name, count in top_authors
                ],
                'name_statistics': {
                    'min_length': name_lengths[0],
                    'max_length': name_lengths[1],
                    'avg_length': float(name_lengths[2]) if name_lengths[2] else 0.0
                }
            }
    
    def _format_author(self, author: Author, book_count: int = 0) -> Dict[str, Any]:
        """
        Format an Author object into a dictionary.
        
        Args:
            author: The Author object to format
            book_count: Number of books by this author
            
        Returns:
            Dictionary with author data
        """
        if not author:
            return None
            
        return {
            'id': author.id,
            'name': author.name,
            'sort': author.sort,
            'link': author.link,
            'book_count': book_count
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
            'name': Author.name,
            'sort': Author.sort,
            'book_count': func.count(Book.id)
        }
        return sort_fields.get(sort_by.lower(), Author.name)
    
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
                    joinedload(Book.ratings),
                    joinedload(Book.tags)
                )
                .join(Book.authors)
                .filter(Author.id == author_id)
                .order_by(Book.sort, Book.pubdate.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            
            # Format results using the Book model's to_dict method if available,
            # or fall back to a basic format
            book_repo = self._db.get_repository('books')
            if hasattr(book_repo, '_format_book'):
                formatted_books = [book_repo._format_book(book) for book in books]
            else:
                formatted_books = [
                    {
                        'id': book.id,
                        'title': book.title,
                        'authors': [{'id': a.id, 'name': a.name} for a in book.authors],
                        'series': book.series[0].name if book.series else None,
                        'series_id': book.series[0].id if book.series else None,
                        'series_index': book.series_index,
                        'rating': book.ratings[0].rating if book.ratings else 0,
                        'tags': [{'id': t.id, 'name': t.name} for t in book.tags]
                    }
                    for book in books
                ]
            
            return formatted_books, total
        
        
        # Authors by first letter
        stats['authors_by_letter'] = self._fetch_all("""
            SELECT UPPER(SUBSTR(name, 1, 1)) as letter, 
                   COUNT(*) as count
            FROM authors
            GROUP BY letter
            ORDER BY letter
        """)
        
        return stats
    
    def search_authors(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for authors by name."""
        search_term = f"%{query}%"
        query_sql = """
            SELECT a.*, COUNT(ba.book) as book_count
            FROM authors a
            LEFT JOIN books_authors_link ba ON a.id = ba.author
            WHERE a.name LIKE ? OR a.sort LIKE ?
            GROUP BY a.id
            ORDER BY book_count DESC, a.name
            LIMIT ?
        """
        results = self._fetch_all(query_sql, (search_term, search_term, limit))
        return [self._process_author_result(row) for row in results]
    
    def _process_author_result(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Process an author result row into a more usable format."""
        if not row:
            return {}
            
        return {
            'id': row['id'],
            'name': row['name'],
            'sort': row.get('sort', row['name']),
            'link': row.get('link', ''),
            'book_count': row.get('book_count', 0)
        }
    
    def _process_book_result(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Process a book result row into a more usable format."""
        if not row:
            return {}
            
        # Process authors and tags from pipe-separated strings to lists
        authors = row.get('authors', '').split('|') if row.get('authors') else []
        tags = row.get('tags', '').split('|') if row.get('tags') else []
        
        return {
            'id': row['id'],
            'title': row['title'],
            'sort': row.get('sort'),
            'timestamp': row.get('timestamp'),
            'pubdate': row.get('pubdate'),
            'series_index': row.get('series_index', 0.0),
            'author_sort': row.get('author_sort'),
            'isbn': row.get('isbn'),
            'path': row.get('path'),
            'has_cover': bool(row.get('has_cover', 0)),
            'authors': [a for a in authors if a],  # Remove empty strings
            'tags': [t for t in tags if t],  # Remove empty strings
            'series': row.get('series_name'),
            'rating': row.get('rating')
        }
