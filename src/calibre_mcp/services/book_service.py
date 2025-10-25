"""
Service for handling book-related operations in the Calibre MCP application.
"""
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

from ..db.database import DatabaseService
from ..models.book import Book, BookCreate, BookUpdate, BookResponse
from ..models.author import Author
from ..models.series import Series
from ..models.tag import Tag
from ..models.rating import Rating
from ..models.comment import Comment
from .base_service import BaseService, NotFoundError, ValidationError

class BookSearchResult(BookResponse):
    """Model for book search results with additional metadata."""
    class Config(BookResponse.Config):
        fields = {
            'authors': {
                'exclude': {'books', 'sort'},
            },
            'series': {
                'exclude': {'books'},
            },
            'tags': {
                'exclude': {'books'},
            },
        }

class BookService(BaseService[Book, BookCreate, BookUpdate, BookResponse]):
    """
    Service class for handling book-related operations.
    
    This class provides a high-level interface for performing CRUD operations
    on books, including managing relationships with authors, series, and tags.
    """
    
    def __init__(self, db: DatabaseService):
        """
        Initialize the BookService with a database instance.
        
        Args:
            db: Database service instance
        """
        super().__init__(db, Book, BookResponse)
    
    def get_by_id(self, book_id: int) -> Dict[str, Any]:
        """
        Get a book by its ID with all related data.
        
        Args:
            book_id: The ID of the book to retrieve
            
        Returns:
            Dictionary containing book data
            
        Raises:
            NotFoundError: If the book is not found
        """
        with self._get_db_session() as session:
            book = session.query(Book).options(
                joinedload(Book.authors),
                joinedload(Book.tags),
                joinedload(Book.series),
                joinedload(Book.ratings),
                joinedload(Book.comments),
                joinedload(Book.data),
                joinedload(Book.identifiers)
            ).filter(Book.id == book_id).first()
            
            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")
                
            return self._to_response(book)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        author_id: Optional[int] = None,
        author_name: Optional[str] = None,
        series_id: Optional[int] = None,
        series_name: Optional[str] = None,
        tag_id: Optional[int] = None,
        tag_name: Optional[str] = None,
        comment: Optional[str] = None,
        has_cover: Optional[bool] = None,
        sort_by: str = 'title',
        sort_order: str = 'asc',
        **filters: Any
    ) -> Dict[str, Any]:
        """
        Get a paginated list of books with optional filtering and sorting.
        
        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return (1-1000)
            search: Search term to filter books by title, author, or series
            author_id: Filter books by author ID
            author_name: Filter books by author name (case-insensitive partial match)
            series_id: Filter books by series ID
            series_name: Filter books by series name (case-insensitive partial match)
            tag_id: Filter books by tag ID
            tag_name: Filter books by tag name (case-insensitive partial match)
            comment: Search in book comments (case-insensitive partial match)
            has_cover: Filter books by cover availability
            sort_by: Field to sort by (title, author, series, rating, timestamp)
            sort_order: Sort order (asc or desc)
            **filters: Additional filter criteria
            
        Returns:
            Dictionary containing paginated results and metadata
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        # Validate inputs
        if limit < 1 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
            
        if skip < 0:
            raise ValueError("Skip cannot be negative")
            
        if sort_order.lower() not in ('asc', 'desc'):
            raise ValueError("sort_order must be 'asc' or 'desc'")
            
        valid_sort_fields = {'title', 'author', 'series', 'rating', 'timestamp', 'pubdate'}
        if sort_by.lower() not in valid_sort_fields:
            raise ValueError(f"sort_by must be one of {valid_sort_fields}")
            
        with self._get_db_session() as session:
            # Start building the query
            query = session.query(Book).options(
                joinedload(Book.authors),
                joinedload(Book.tags),
                joinedload(Book.series),
                joinedload(Book.ratings).joinedload(Rating.rating),
                joinedload(Book.comments),
                joinedload(Book.data),
                joinedload(Book.identifiers)
            )
            
            # Apply search filter (title, author, series, tags)
            if search:
                search = f"%{search}%"
                query = query.join(Book.authors, isouter=True)\
                            .join(Book.series, isouter=True)\
                            .join(Book.tags, isouter=True)\
                            .filter(
                                or_(
                                    Book.title.ilike(search),
                                    Author.name.ilike(search),
                                    Series.name.ilike(search),
                                    Tag.name.ilike(search)
                                )
                            ).distinct()
            
            # Apply author filters
            if author_id:
                query = query.filter(Book.authors.any(Author.id == author_id))
                
            if author_name:
                author_name = f"%{author_name}%"
                query = query.join(Book.authors)\
                            .filter(Author.name.ilike(author_name))\
                            .distinct()
            
            # Apply series filters
            if series_id:
                query = query.filter(Book.series_id == series_id)
                
            if series_name:
                series_name = f"%{series_name}%"
                query = query.join(Book.series)\
                            .filter(Series.name.ilike(series_name))\
                            .distinct()
            
            # Apply tag filters
            if tag_id:
                query = query.filter(Book.tags.any(Tag.id == tag_id))
                
            if tag_name:
                tag_name = f"%{tag_name}%"
                query = query.join(Book.tags)\
                            .filter(Tag.name.ilike(tag_name))\
                            .distinct()
            
            # Apply comment search
            if comment:
                comment = f"%{comment}%"
                query = query.join(Book.comments)\
                            .filter(Comment.text.ilike(comment))\
                            .distinct()
            
            # Apply cover filter
            if has_cover is not None:
                query = query.filter(Book.has_cover == has_cover)
            
            # Apply additional filters from **filters
            for field, value in filters.items():
                if hasattr(Book, field):
                    column = getattr(Book, field)
                    if isinstance(value, (list, tuple, set)):
                        query = query.filter(column.in_(value))
                    else:
                        query = query.filter(column == value)
            
            # Apply sorting
            sort_mapping = {
                'title': Book.title,
                'author': Author.sort,
                'series': Series.name,
                'rating': Book.rating,
                'timestamp': Book.timestamp,
                'pubdate': Book.pubdate
            }
            
            sort_field = sort_mapping.get(sort_by.lower(), Book.title)
            if sort_order.lower() == 'desc':
                sort_field = sort_field.desc()
            else:
                sort_field = sort_field.asc()
            
            # Special handling for author/series sorting to avoid duplicates
            if sort_by.lower() in ('author', 'series'):
                query = query.order_by(sort_field, Book.sort)
            else:
                query = query.order_by(sort_field)
            
            # Get total count before pagination
            total = query.distinct().count()
            
            # Apply pagination
            books = query.offset(skip).limit(limit).all()
            
            # Convert to response models
            items = [self._to_response(book) for book in books]
            
            return {
                "items": items,
                "total": total,
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "page_size": limit,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1
            }
    
    def create(self, book_data: BookCreate) -> Dict[str, Any]:
        """
        Create a new book with the given data.
        
        Args:
            book_data: Data for creating the book
            
        Returns:
            Dictionary containing the created book data
            
        Raises:
            ValidationError: If the input data is invalid
        """
        with self._get_db_session() as session:
            # Create book instance
            book_dict = book_data.dict(exclude={'author_ids', 'series_id', 'tag_ids', 'rating'}, exclude_unset=True)
            book = Book(**book_dict)
            
            # Handle relationships
            if book_data.author_ids:
                authors = session.query(Author).filter(Author.id.in_(book_data.author_ids)).all()
                if len(authors) != len(book_data.author_ids):
                    found_ids = {a.id for a in authors}
                    missing_ids = set(book_data.author_ids) - found_ids
                    raise ValidationError(f"Authors not found: {', '.join(map(str, missing_ids))}")
                book.authors = authors
            
            if book_data.series_id is not None:
                series = session.query(Series).get(book_data.series_id)
                if not series:
                    raise ValidationError(f"Series with ID {book_data.series_id} not found")
                book.series = [series]
            
            if book_data.tag_ids:
                tags = session.query(Tag).filter(Tag.id.in_(book_data.tag_ids)).all()
                if len(tags) != len(book_data.tag_ids):
                    found_ids = {t.id for t in tags}
                    missing_ids = set(book_data.tag_ids) - found_ids
                    raise ValidationError(f"Tags not found: {', '.join(map(str, missing_ids))}")
                book.tags = tags
            
            if book_data.rating is not None:
                rating = Rating(rating=book_data.rating, book=book)
                session.add(rating)
            
            session.add(book)
            session.commit()
            session.refresh(book)
            
            return self._to_response(book)
    
    def update(self, book_id: int, book_data: Union[BookUpdate, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update an existing book with the given data.
        
        Args:
            book_id: ID of the book to update
            book_data: Data for updating the book
            
        Returns:
            Dictionary containing the updated book data
            
        Raises:
            NotFoundError: If the book is not found
            ValidationError: If the input data is invalid
        """
        if isinstance(book_data, dict):
            update_data = book_data
        else:
            update_data = book_data.dict(exclude_unset=True)
        
        with self._get_db_session() as session:
            # Get the existing book
            book = session.query(Book).get(book_id)
            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")
            
            # Update simple fields
            for field, value in update_data.items():
                if hasattr(book, field) and field not in ['author_ids', 'series_id', 'tag_ids', 'rating']:
                    setattr(book, field, value)
            
            # Handle relationships if provided
            if 'author_ids' in update_data:
                authors = session.query(Author).filter(
                    Author.id.in_(update_data['author_ids'])
                ).all()
                if len(authors) != len(update_data['author_ids']):
                    found_ids = {a.id for a in authors}
                    missing_ids = set(update_data['author_ids']) - found_ids
                    raise ValidationError(f"Authors not found: {', '.join(map(str, missing_ids))}")
                book.authors = authors
            
            if 'series_id' in update_data:
                if update_data['series_id'] is not None:
                    series = session.query(Series).get(update_data['series_id'])
                    if not series:
                        raise ValidationError(f"Series with ID {update_data['series_id']} not found")
                    book.series = [series]
                else:
                    book.series = []
            
            if 'tag_ids' in update_data:
                tags = session.query(Tag).filter(
                    Tag.id.in_(update_data['tag_ids'])
                ).all()
                if len(tags) != len(update_data['tag_ids']):
                    found_ids = {t.id for t in tags}
                    missing_ids = set(update_data['tag_ids']) - found_ids
                    raise ValidationError(f"Tags not found: {', '.join(map(str, missing_ids))}")
                book.tags = tags
            
            if 'rating' in update_data:
                # Update or create rating
                rating = session.query(Rating).filter(
                    Rating.book_id == book.id
                ).first()
                
                if update_data['rating'] is None and rating:
                    session.delete(rating)
                elif update_data['rating'] is not None:
                    if rating:
                        rating.rating = update_data['rating']
                    else:
                        rating = Rating(rating=update_data['rating'], book=book)
                        session.add(rating)
            
            session.add(book)
            session.commit()
            session.refresh(book)
            
            return self._to_response(book)
    
    def delete(self, book_id: int) -> bool:
        """
        Delete a book by its ID.
        
        Args:
            book_id: ID of the book to delete
            
        Returns:
            True if the book was deleted successfully
            
        Raises:
            NotFoundError: If the book is not found
        """
        with self._get_db_session() as session:
            book = session.query(Book).get(book_id)
            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")
            
            session.delete(book)
            session.commit()
            return True
    
    def get_book_formats(self, book_id: int) -> List[Dict[str, Any]]:
        """
        Get all available formats for a book.
        
        Args:
            book_id: ID of the book
            
        Returns:
            List of dictionaries containing format information
            
        Raises:
            NotFoundError: If the book is not found
        """
        with self._get_db_session() as session:
            book = session.query(Book).options(joinedload(Book.data)).get(book_id)
            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")
            
            return [
                {
                    'format': data.format.upper(),
                    'size': data.size,
                    'name': data.name,
                    'mtime': data.mtime.isoformat() if data.mtime else None
                }
                for data in book.data
            ]
    
    def get_book_cover(self, book_id: int) -> Optional[bytes]:
        """
        Get the cover image for a book.
        
        Args:
            book_id: ID of the book
            
        Returns:
            Bytes of the cover image, or None if no cover exists
            
        Raises:
            NotFoundError: If the book is not found
        """
        with self._get_db_session() as session:
            book = session.query(Book).get(book_id)
            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")
            
            if not book.has_cover:
                return None
                
            # This assumes you have a method to retrieve the cover data
            # You'll need to implement this based on your storage solution
            return self._get_cover_data(book_id)
    
    def _get_cover_data(self, book_id: int) -> Optional[bytes]:
        """
        Internal method to retrieve cover data for a book.
        
        This is a placeholder that should be implemented based on your
        specific storage solution for book covers.
        
        Args:
            book_id: ID of the book
            
        Returns:
            Bytes of the cover image, or None if no cover exists
        """
        # TODO: Implement cover data retrieval based on your storage solution
        # This could read from the filesystem, a blob store, etc.
        return None
    
    def _to_response(self, book: Book) -> Dict[str, Any]:
        """
        Convert a Book model instance to a response dictionary.
        
        Args:
            book: The Book instance to convert
            
        Returns:
            Dictionary containing the book data in the response format
        """
        return BookResponse.from_orm(book).dict()


# Create a singleton instance of the service
book_service = BookService(DatabaseService())
