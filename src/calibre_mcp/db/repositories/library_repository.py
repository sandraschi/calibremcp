"""
Repository for handling library-related database operations.
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import func, or_

from ...db.base_repository import BaseRepository
from ...models.library import Library
from ...models.book import Book
from ...models.author import Author
from ...models.series import Series
from ...models.tag import Tag
from ...models.rating import Rating
from ...models.comment import Comment
from ...models.data import Data


class LibraryRepository(BaseRepository[Library]):
    """Repository for library-related database operations."""

    def __init__(self, db):
        """Initialize with database service."""
        super().__init__(db, Library)

    def get_by_name(self, name: str) -> Optional[Library]:
        """Get a library by its exact name."""
        with self._db.session_scope() as session:
            return session.query(Library).filter(Library.name == name).first()

    def get_by_path(self, path: str) -> Optional[Library]:
        """Get a library by its path."""
        with self._db.session_scope() as session:
            return session.query(Library).filter(Library.path == path).first()

    def get_active_libraries(self) -> List[Library]:
        """Get all active libraries."""
        with self._db.session_scope() as session:
            return session.query(Library).filter(Library.is_active).order_by(Library.name).all()

    def get_library_stats(self, library_id: int) -> Dict[str, Any]:
        """Get statistics for a library."""
        with self._db.session_scope() as session:
            library = session.query(Library).get(library_id)
            if not library:
                return {}

            stats = {
                "id": library.id,
                "name": library.name,
                "path": library.path,
                "book_count": 0,
                "author_count": 0,
                "newest_book": None,
                "last_updated": None,
                "formats": {},
            }

            # Get book count
            book_count = (
                session.query(func.count(Book.id)).filter(Book.library_id == library_id).scalar()
            )
            stats["book_count"] = book_count or 0

            # Get author count
            author_count = (
                session.query(func.count(func.distinct(Book.author_sort)))
                .filter(Book.library_id == library_id)
                .scalar()
            )
            stats["author_count"] = author_count or 0

            # Get newest book
            newest_book = (
                session.query(Book)
                .filter(Book.library_id == library_id)
                .order_by(Book.timestamp.desc())
                .first()
            )

            if newest_book:
                stats["newest_book"] = {
                    "id": newest_book.id,
                    "title": newest_book.title,
                    "author_sort": newest_book.author_sort,
                    "timestamp": newest_book.timestamp.isoformat(),
                }
                stats["last_updated"] = newest_book.timestamp.isoformat()

            # Get format distribution
            formats = (
                session.query(Data.format, func.count(Data.id).label("count"))
                .join(Book)
                .filter(Book.library_id == library_id)
                .group_by(Data.format)
                .all()
            )

            stats["formats"] = {f: c for f, c in formats}

            return stats

    def get_library_books(
        self,
        library_id: int,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "title",
        ascending: bool = True,
        query: str = None,
        author_id: int = None,
        tag_id: int = None,
        series_id: int = None,
        rating_min: int = None,
        rating_max: int = None,
    ) -> Tuple[List[Dict], int]:
        """
        Get books in a library with filtering and pagination.

        Args:
            library_id: ID of the library
            limit: Maximum number of results to return
            offset: Number of results to skip
            sort_by: Field to sort by (title, author, date_added, pubdate)
            ascending: Sort in ascending order
            query: Search term to match against title/author
            author_id: Filter by author ID
            tag_id: Filter by tag ID
            series_id: Filter by series ID
            rating_min: Minimum rating (1-5)
            rating_max: Maximum rating (1-5)

        Returns:
            Tuple of (list of books, total count)
        """
        with self._db.session_scope() as session:
            # Start building the query
            query_obj = session.query(Book).filter(Book.library_id == library_id)

            # Apply filters
            if query:
                query_obj = query_obj.filter(
                    or_(
                        Book.title.ilike(f"%{query}%"),
                        Book.author_sort.ilike(f"%{query}%"),
                        Book.comments.any(Comment.text.ilike(f"%{query}%")),
                    )
                )

            if author_id:
                query_obj = query_obj.join(Book.authors).filter(Author.id == author_id)

            if series_id:
                query_obj = query_obj.join(Book.series_rel).filter(Series.id == series_id)

            if tag_id:
                query_obj = query_obj.join(Book.tags).filter(Tag.id == tag_id)

            if rating_min is not None or rating_max is not None:
                query_obj = query_obj.join(Book.ratings)
                if rating_min is not None:
                    query_obj = query_obj.filter(Rating.rating >= rating_min)
                if rating_max is not None:
                    query_obj = query_obj.filter(Rating.rating <= rating_max)

            # Get total count before pagination
            total = query_obj.distinct().count()

            # Apply sorting
            sort_field = self._get_sort_field(sort_by)
            if sort_field is not None:
                sort_field = sort_field.asc() if ascending else sort_field.desc()
                query_obj = query_obj.order_by(sort_field)

            # Apply pagination and load relationships
            books = (
                query_obj.options(
                    joinedload(Book.authors),
                    joinedload(Book.series_rel),
                    joinedload(Book.tags),
                    joinedload(Book.ratings),
                    joinedload(Book.comments),
                    joinedload(Book.data),
                )
                .distinct()
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Format results
            formatted_books = []
            for book in books:
                book_data = {
                    "id": book.id,
                    "title": book.title,
                    "author_sort": book.author_sort,
                    "has_cover": book.has_cover == 1,
                    "timestamp": book.timestamp.isoformat(),
                    "pubdate": book.pubdate.isoformat() if book.pubdate else None,
                    "series_index": book.series_index,
                    "authors": [{"id": a.id, "name": a.name} for a in book.authors],
                    "series": book.series_rel[0].name if book.series_rel else None,
                    "series_id": book.series_rel[0].id if book.series_rel else None,
                    "tags": [{"id": t.id, "name": t.name} for t in book.tags],
                    "rating": book.ratings[0].rating if book.ratings else None,
                    "comment": book.comments[0].text if book.comments else None,
                    "formats": [d.format for d in book.data],
                }
                formatted_books.append(book_data)

            return formatted_books, total

    def _get_sort_field(self, sort_by: str):
        """Get the SQLAlchemy field to sort by."""
        sort_fields = {
            "title": Book.sort,
            "author": Book.author_sort,
            "date_added": Book.timestamp,
            "pubdate": Book.pubdate,
            "series": Series.name,
            "rating": Rating.rating,
        }
        return sort_fields.get(sort_by.lower(), Book.sort)

    def update_library_stats(self, library_id: int) -> bool:
        """Update the cached statistics for a library."""
        with self._db.session_scope() as session:
            library = session.query(Library).get(library_id)
            if not library:
                return False

            # Update book count
            book_count = (
                session.query(func.count(Book.id)).filter(Book.library_id == library_id).scalar()
            )

            # Update author count
            author_count = (
                session.query(func.count(func.distinct(Book.author_sort)))
                .filter(Book.library_id == library_id)
                .scalar()
            )

            # Update format counts
            formats = (
                session.query(Data.format, func.count(Data.id).label("count"))
                .join(Book)
                .filter(Book.library_id == library_id)
                .group_by(Data.format)
                .all()
            )

            # Update the library
            library.book_count = book_count or 0
            library.author_count = author_count or 0
            library.format_counts = {f: c for f, c in formats}
            library.updated_at = datetime.utcnow()

            session.commit()
            return True

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
                    "id": b.id,
                    "title": b.title,
                    "authors": [{"id": a.id, "name": a.name} for a in b.authors],
                    "timestamp": b.timestamp.isoformat() if b.timestamp else None,
                    "has_cover": bool(b.has_cover),
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
                    "id": b.id,
                    "title": b.title,
                    "authors": [{"id": a.id, "name": a.name} for a in b.authors],
                    "last_modified": b.last_modified.isoformat() if b.last_modified else None,
                    "has_cover": bool(b.has_cover),
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
                        func.count(Comment.id) == 0,  # No description
                        Book.pubdate.is_(None),  # No publication date
                    )
                )
                .order_by(Book.timestamp.desc())
                .limit(limit)
                .all()
            )

            return [
                {
                    "id": b.id,
                    "title": b.title or "Untitled",
                    "authors": [{"id": a.id, "name": a.name} for a in b.authors],
                    "missing": [],
                }
                for b in books
            ]
