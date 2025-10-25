"""
Service for handling author-related operations in the Calibre MCP application.
"""
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc, asc

from ..db.database import DatabaseService
from ..models.author import Author, AuthorCreate, AuthorUpdate, AuthorResponse
from ..models.book import Book
from .base_service import BaseService, NotFoundError, ValidationError

class AuthorService(BaseService[Author, AuthorCreate, AuthorUpdate, AuthorResponse]):
    """
    Service class for handling author-related operations.
    
    This class provides a high-level interface for performing CRUD operations
    on authors, including managing relationships with books.
    """
    
    def __init__(self, db: DatabaseService):
        """
        Initialize the AuthorService with a database instance.
        
        Args:
            db: Database service instance
        """
        super().__init__(db, Author, AuthorResponse)
    
    def get_by_id(self, author_id: int) -> Dict[str, Any]:
        """
        Get an author by ID with related data.
        
        Args:
            author_id: The ID of the author to retrieve
            
        Returns:
            Dictionary containing author data with book count
            
        Raises:
            NotFoundError: If the author is not found
        """
        with self._get_db_session() as session:
            author = (
                session.query(Author)
                .options(joinedload(Author.books))
                .filter(Author.id == author_id)
                .first()
            )
            
            if not author:
                raise NotFoundError(f"Author with ID {author_id} not found")
                
            return self._to_response(author)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        sort_by: str = 'name',
        sort_order: str = 'asc'
    ) -> Dict[str, Any]:
        """
        Get a paginated list of authors with optional filtering and sorting.
        
        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            search: Search term to filter authors by name
            sort_by: Field to sort by (e.g., 'name', 'book_count')
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Dictionary containing paginated list of authors and metadata
        """
        with self._get_db_session() as session:
            # Start with base query
            query = session.query(Author)
            
            # Add subquery for book count
            book_count = (
                session.query(
                    Author.id.label('author_id'),
                    func.count(Book.id).label('book_count')
                )
                .join(Author.books)
                .group_by(Author.id)
                .subquery()
            )
            
            # Join with book count
            query = query.outerjoin(
                book_count,
                Author.id == book_count.c.author_id
            )
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(Author.name.ilike(search_term))
            
            # Apply sorting
            if sort_by == 'book_count':
                if sort_order.lower() == 'desc':
                    query = query.order_by(desc(book_count.c.book_count))
                else:
                    query = query.order_by(asc(book_count.c.book_count))
            else:
                sort_field = getattr(Author, sort_by, Author.name)
                if sort_order.lower() == 'desc':
                    query = query.order_by(desc(sort_field))
                else:
                    query = query.order_by(asc(sort_field))
            
            # Get total count before pagination
            total = query.count()
            
            # Apply pagination
            authors = query.options(
                joinedload(Author.books)
            ).offset(skip).limit(limit).all()
            
            # Convert to response models
            items = [self._to_response(author) for author in authors]
            
            return {
                'items': items,
                'total': total,
                'page': (skip // limit) + 1,
                'per_page': limit,
                'total_pages': (total + limit - 1) // limit if total > 0 else 1
            }
    
    def create(self, author_data: AuthorCreate) -> Dict[str, Any]:
        """
        Create a new author.
        
        Args:
            author_data: Data for creating the author
            
        Returns:
            Dictionary containing the created author data
            
        Raises:
            ValidationError: If an author with the same name already exists
        """
        with self._get_db_session() as session:
            # Check if author with same name already exists
            existing = (
                session.query(Author)
                .filter(func.lower(Author.name) == author_data.name.lower())
                .first()
            )
            
            if existing:
                raise ValidationError(f"Author with name '{author_data.name}' already exists")
            
            # Create new author
            author = Author(
                name=author_data.name,
                sort=author_data.sort or author_data.name,
                link=author_data.link or ''
            )
            
            session.add(author)
            session.commit()
            session.refresh(author)
            
            return self._to_response(author)
    
    def update(self, author_id: int, author_data: Union[AuthorUpdate, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update an existing author.
        
        Args:
            author_id: ID of the author to update
            author_data: Data for updating the author
            
        Returns:
            Dictionary containing the updated author data
            
        Raises:
            NotFoundError: If the author is not found
            ValidationError: If the update data is invalid
        """
        if isinstance(author_data, dict):
            update_data = author_data
        else:
            update_data = author_data.dict(exclude_unset=True)
        
        with self._get_db_session() as session:
            # Get the existing author
            author = session.query(Author).get(author_id)
            if not author:
                raise NotFoundError(f"Author with ID {author_id} not found")
            
            # Check if name is being updated and if it conflicts with existing
            if 'name' in update_data and update_data['name'] != author.name:
                existing = (
                    session.query(Author)
                    .filter(
                        func.lower(Author.name) == update_data['name'].lower(),
                        Author.id != author_id
                    )
                    .first()
                )
                if existing:
                    raise ValidationError(f"Author with name '{update_data['name']}' already exists")
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(author, field):
                    setattr(author, field, value)
            
            # Update sort field if name was changed but sort wasn't explicitly set
            if 'name' in update_data and 'sort' not in update_data:
                author.sort = update_data['name']
            
            session.add(author)
            session.commit()
            session.refresh(author)
            
            return self._to_response(author)
    
    def delete(self, author_id: int) -> bool:
        """
        Delete an author by ID.
        
        Args:
            author_id: ID of the author to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            NotFoundError: If the author is not found
            ValidationError: If the author has associated books
        """
        with self._get_db_session() as session:
            author = (
                session.query(Author)
                .options(joinedload(Author.books))
                .filter(Author.id == author_id)
                .first()
            )
            
            if not author:
                raise NotFoundError(f"Author with ID {author_id} not found")
            
            # Check if author has books
            if hasattr(author, 'books') and author.books:
                book_count = len(author.books)
                raise ValidationError(
                    f"Cannot delete author with {book_count} associated books. "
                    "Please remove or reassign the books first."
                )
            
            session.delete(author)
            session.commit()
            return True
    
    def get_books_by_author(
        self, 
        author_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get books by a specific author with pagination.
        
        Args:
            author_id: ID of the author
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            Dictionary containing paginated results and metadata
            
        Raises:
            NotFoundError: If the author is not found
        """
        with self._get_db_session() as session:
            # First verify author exists
            author = session.query(Author).get(author_id)
            if not author:
                raise NotFoundError(f"Author with ID {author_id} not found")
            
            # Get books with pagination
            books_query = (
                session.query(Book)
                .join(Book.authors)
                .filter(Author.id == author_id)
                .options(joinedload(Book.authors))
            )
            
            total = books_query.count()
            books = books_query.offset(offset).limit(limit).all()
            
            # Convert to response format
            from .book_service import BookService
            book_service = BookService(self.db)
            items = [book_service._to_response(book) for book in books]
            
            return {
                'items': items,
                'total': total,
                'page': (offset // limit) + 1,
                'per_page': limit,
                'total_pages': (total + limit - 1) // limit if total > 0 else 1
            }
    
    def get_authors_by_letter(self, letter: str) -> List[Dict[str, Any]]:
        """
        Get all authors whose names start with the given letter.
        
        Args:
            letter: Single letter to filter authors by
            
        Returns:
            List of author dictionaries
        """
        if len(letter) != 1 or not letter.isalpha():
            return []
            
        with self._get_db_session() as session:
            authors = (
                session.query(Author)
                .filter(Author.name.ilike(f"{letter.lower()}%"))
                .order_by(Author.name)
                .all()
            )
            
            return [self._to_response(author) for author in authors]
    
    def get_author_stats(self) -> Dict[str, Any]:
        """
        Get statistics about authors in the library.
        
        Returns:
            Dictionary containing author statistics
        """
        with self._get_db_session() as session:
            # Total number of authors
            total_authors = session.query(func.count(Author.id)).scalar()
            
            # Number of authors by first letter
            letter_counts = (
                session.query(
                    func.upper(func.substr(Author.name, 1, 1)).label('letter'),
                    func.count(Author.id).label('count')
                )
                .group_by('letter')
                .order_by('letter')
                .all()
            )
            
            # Top authors by book count
            top_authors = (
                session.query(
                    Author,
                    func.count(Book.id).label('book_count')
                )
                .join(Author.books)
                .group_by(Author.id)
                .order_by(desc('book_count'))
                .limit(10)
                .all()
            )
            
            return {
                'total_authors': total_authors,
                'authors_by_letter': [
                    {'letter': letter, 'count': count} 
                    for letter, count in letter_counts
                ],
                'top_authors': [
                    {
                        'id': author.id,
                        'name': author.name,
                        'book_count': book_count
                    }
                    for author, book_count in top_authors
                ]
            }


# Create a singleton instance of the service
author_service = AuthorService(DatabaseService())
