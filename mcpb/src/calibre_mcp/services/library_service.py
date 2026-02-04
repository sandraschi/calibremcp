"""
Service for handling library-level operations in the Calibre MCP application.
"""

from typing import Any

from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import joinedload

from ..db.database import DatabaseService
from ..models.author import Author
from ..models.book import Book
from ..models.library import Library, LibraryCreate, LibraryResponse, LibraryUpdate
from .base_service import BaseService, NotFoundError, ValidationError


class LibraryService(BaseService[Library, LibraryCreate, LibraryUpdate, LibraryResponse]):
    """
    Service class for handling library-related operations.

    This class provides a high-level interface for performing CRUD operations
    on libraries, including managing relationships with books and authors.
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize the LibraryService with a database instance.

        Args:
            db: Database service instance
        """
        super().__init__(db, Library, LibraryResponse)

    def get_by_id(self, library_id: int) -> dict[str, Any]:
        """
        Get a library by ID with related data.

        Args:
            library_id: The ID of the library to retrieve

        Returns:
            Dictionary containing library data with counts and statistics

        Raises:
            NotFoundError: If the library is not found
        """
        with self._get_db_session() as session:
            library = (
                session.query(Library)
                .options(joinedload(Library.books).joinedload(Book.authors))
                .filter(Library.id == library_id)
                .first()
            )

            if not library:
                raise NotFoundError(f"Library with ID {library_id} not found")

            return self._to_response(library)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        is_active: bool | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """
        Get a paginated list of libraries with optional filtering and sorting.

        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            search: Search term to filter libraries by name or path
            is_active: Filter by active status
            sort_by: Field to sort by (e.g., 'name', 'book_count', 'author_count')
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing paginated list of libraries and metadata
        """
        with self._get_db_session() as session:
            # Start with base query
            query = session.query(Library)

            # Add subqueries for counts
            book_count = (
                session.query(
                    Library.id.label("library_id"), func.count(Book.id).label("book_count")
                )
                .join(Library.books, isouter=True)
                .group_by(Library.id)
                .subquery()
            )

            author_count = (
                session.query(
                    Library.id.label("library_id"),
                    func.count(func.distinct(Author.id)).label("author_count"),
                )
                .join(Library.books, isouter=True)
                .join(Book.authors, isouter=True)
                .group_by(Library.id)
                .subquery()
            )

            # Join with subqueries
            query = query.outerjoin(book_count, Library.id == book_count.c.library_id).outerjoin(
                author_count, Library.id == author_count.c.library_id
            )

            # Apply filters
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(Library.name.ilike(search_term), Library.path.ilike(search_term))
                )

            if is_active is not None:
                query = query.filter(Library.is_active == is_active)

            # Apply sorting
            if sort_by == "book_count":
                sort_field = book_count.c.book_count
            elif sort_by == "author_count":
                sort_field = author_count.c.author_count
            else:
                sort_field = getattr(Library, sort_by, Library.name)

            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(asc(sort_field))

            # Get total count before pagination
            total = query.count()

            # Apply pagination
            libraries = query.options(joinedload(Library.books)).offset(skip).limit(limit).all()

            # Convert to response models
            items = [self._to_response(lib) for lib in libraries]

            return {
                "items": items,
                "total": total,
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            }

    def create(self, library_data: LibraryCreate) -> dict[str, Any]:
        """
        Create a new library.

        Args:
            library_data: Data for creating the library

        Returns:
            Dictionary containing the created library data

        Raises:
            ValidationError: If a library with the same name or path already exists
        """
        with self._get_db_session() as session:
            # Check for existing library with same name or path
            existing = (
                session.query(Library)
                .filter(
                    or_(
                        func.lower(Library.name) == library_data.name.lower(),
                        func.lower(Library.path) == library_data.path.lower(),
                    )
                )
                .first()
            )

            if existing:
                if existing.name.lower() == library_data.name.lower():
                    raise ValidationError(
                        f"A library with name '{library_data.name}' already exists"
                    )
                else:
                    raise ValidationError(
                        f"A library with path '{library_data.path}' already exists"
                    )

            # Create new library
            library = Library(
                name=library_data.name,
                path=library_data.path,
                is_local=library_data.is_local,
                is_active=True,
            )

            session.add(library)
            session.commit()
            session.refresh(library)

            return self._to_response(library)

    def update(
        self, library_id: int, library_data: LibraryUpdate | dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update an existing library.

        Args:
            library_id: ID of the library to update
            library_data: Data for updating the library

        Returns:
            Dictionary containing the updated library data

        Raises:
            NotFoundError: If the library is not found
            ValidationError: If the update data is invalid
        """
        if isinstance(library_data, dict):
            update_data = library_data
        else:
            update_data = library_data.dict(exclude_unset=True)

        with self._get_db_session() as session:
            # Get the existing library
            library = session.query(Library).get(library_id)
            if not library:
                raise NotFoundError(f"Library with ID {library_id} not found")

            # Check for name/path conflicts if being updated
            if "name" in update_data or "path" in update_data:
                name = update_data.get("name", library.name)
                path = update_data.get("path", library.path)

                existing = (
                    session.query(Library)
                    .filter(
                        Library.id != library_id,
                        or_(
                            func.lower(Library.name) == name.lower(),
                            func.lower(Library.path) == path.lower(),
                        ),
                    )
                    .first()
                )

                if existing:
                    if existing.name.lower() == name.lower():
                        raise ValidationError(f"A library with name '{name}' already exists")
                    else:
                        raise ValidationError(f"A library with path '{path}' already exists")

            # Update fields
            for field, value in update_data.items():
                if hasattr(library, field):
                    setattr(library, field, value)

            session.add(library)
            session.commit()
            session.refresh(library)

            return self._to_response(library)

    def delete(self, library_id: int) -> bool:
        """
        Delete a library by ID.

        Args:
            library_id: ID of the library to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            NotFoundError: If the library is not found
            ValidationError: If the library contains books
        """
        with self._get_db_session() as session:
            # Get the library with books for counting
            library = (
                session.query(Library)
                .options(joinedload(Library.books))
                .filter(Library.id == library_id)
                .first()
            )

            if not library:
                raise NotFoundError(f"Library with ID {library_id} not found")

            # Check if library has books
            if hasattr(library, "books") and library.books:
                book_count = len(library.books)
                raise ValidationError(
                    f"Cannot delete library with {book_count} books. "
                    "Please remove or move the books first."
                )

            session.delete(library)
            session.commit()
            return True

    def get_library_stats(self, library_id: int | None = None) -> dict[str, Any]:
        """
        Get comprehensive statistics for a library or all libraries.

        Args:
            library_id: Optional ID of the library to get stats for

        Returns:
            Dictionary containing library statistics

        Raises:
            NotFoundError: If a specific library is requested but not found
        """
        with self._get_db_session() as session:
            if library_id:
                # Get stats for a specific library
                library = (
                    session.query(Library)
                    .options(
                        joinedload(Library.books).joinedload(Book.authors),
                        joinedload(Library.books).joinedload(Book.data),
                    )
                    .filter(Library.id == library_id)
                    .first()
                )

                if not library:
                    raise NotFoundError(f"Library with ID {library_id} not found")

                # Get recent books (up to 10)
                recent_books = (
                    session.query(Book)
                    .filter(Book.library_id == library_id)
                    .order_by(desc(Book.created_at))
                    .limit(10)
                    .all()
                )

                # Get format counts
                format_counts = {}
                for book in library.books:
                    for data in book.data:
                        fmt = data.format.lower()
                        format_counts[fmt] = format_counts.get(fmt, 0) + 1

                # Get author counts
                author_counts = {}
                for book in library.books:
                    for author in book.authors:
                        author_counts[author.id] = author_counts.get(author.id, 0) + 1

                # Sort authors by book count
                sorted_authors = sorted(
                    [{"id": k, "count": v} for k, v in author_counts.items()],
                    key=lambda x: x["count"],
                    reverse=True,
                )

                return {
                    "library_id": library.id,
                    "library_name": library.name,
                    "total_books": len(library.books),
                    "total_authors": len(author_counts),
                    "formats": [{"format": k, "count": v} for k, v in format_counts.items()],
                    "top_authors": sorted_authors[:10],  # Top 10 authors
                    "recent_books": [
                        {
                            "id": book.id,
                            "title": book.title,
                            "authors": [{"id": a.id, "name": a.name} for a in book.authors],
                            "created_at": book.created_at.isoformat() if book.created_at else None,
                        }
                        for book in recent_books
                    ],
                }
            else:
                # Get stats for all libraries
                libraries = session.query(Library).all()

                all_stats = []
                for lib in libraries:
                    # For each library, get basic stats
                    stats = {
                        "library_id": lib.id,
                        "library_name": lib.name,
                        "total_books": len(lib.books) if hasattr(lib, "books") else 0,
                        "is_active": lib.is_active,
                        "created_at": lib.created_at.isoformat() if lib.created_at else None,
                    }
                    all_stats.append(stats)

                return {
                    "total_libraries": len(all_stats),
                    "active_libraries": sum(1 for lib in all_stats if lib["is_active"]),
                    "libraries": all_stats,
                }

    def search_across_library(
        self, library_id: int, query: str, limit: int = 50, offset: int = 0
    ) -> dict[str, Any]:
        """
        Search across all content in a specific library.

        Args:
            library_id: ID of the library to search in
            query: Search query
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)

        Returns:
            Dictionary containing search results and metadata

        Raises:
            NotFoundError: If the library is not found
        """
        with self._get_db_session() as session:
            # Verify library exists
            library = session.query(Library).get(library_id)
            if not library:
                raise NotFoundError(f"Library with ID {library_id} not found")

            # Search books in this library
            books_query = (
                session.query(Book)
                .join(Book.authors)
                .filter(
                    Book.library_id == library_id,
                    or_(Book.title.ilike(f"%{query}%"), Author.name.ilike(f"%{query}%")),
                )
                .options(joinedload(Book.authors))
            )

            total_books = books_query.count()
            books = books_query.offset(offset).limit(limit).all()

            # Convert to response format
            from .book_service import BookService

            book_service = BookService(self.db)

            return {
                "books": [book_service._to_response(book) for book in books],
                "total_results": total_books,
                "page": (offset // limit) + 1,
                "per_page": limit,
                "total_pages": (total_books + limit - 1) // limit if total_books > 0 else 1,
            }

    def _to_response(self, library: Library) -> dict[str, Any]:
        """
        Convert a Library model instance to a response dictionary.

        Args:
            library: The Library instance to convert

        Returns:
            Dictionary containing the library data in the response format
        """
        # Get counts if not already loaded
        book_count = len(library.books) if hasattr(library, "books") else 0

        # Get author count if books are loaded
        author_count = 0
        if hasattr(library, "books") and library.books:
            author_count = len({author.id for book in library.books for author in book.authors})

        # Get format counts if books and data are loaded
        format_counts = {}
        if hasattr(library, "books"):
            for book in library.books:
                if hasattr(book, "data"):
                    for data in book.data:
                        fmt = data.format.lower()
                        format_counts[fmt] = format_counts.get(fmt, 0) + 1

        # Get total size if books and data are loaded
        total_size = 0
        if hasattr(library, "books"):
            for book in library.books:
                if hasattr(book, "data"):
                    total_size += sum(
                        data.uncompressed_size for data in book.data if data.uncompressed_size
                    )

        # Build response
        response = {
            "id": library.id,
            "name": library.name,
            "path": library.path,
            "is_local": library.is_local,
            "is_active": library.is_active,
            "book_count": book_count,
            "author_count": author_count,
            "total_size": total_size,
            "format_counts": [{"format": k, "count": v} for k, v in format_counts.items()],
            "created_at": library.created_at.isoformat() if library.created_at else None,
            "updated_at": library.updated_at.isoformat() if library.updated_at else None,
        }

        return response

    def get_library_health(self) -> dict[str, Any]:
        """Get library health information."""
        # This is a placeholder for more comprehensive health checks
        stats = self.get_library_stats()

        health = {
            "status": "healthy",
            "checks": [
                {
                    "name": "database_connection",
                    "status": "ok",
                    "message": "Database connection is healthy",
                },
                {
                    "name": "book_count",
                    "status": "ok" if stats.total_books > 0 else "warning",
                    "message": f"Found {stats.total_books} books in library",
                    "metric": stats.total_books,
                },
                {
                    "name": "author_count",
                    "status": "ok" if stats.total_authors > 0 else "warning",
                    "message": f"Found {stats.total_authors} unique authors",
                    "metric": stats.total_authors,
                },
            ],
        }

        # Update overall status if any checks failed
        if any(check["status"] != "ok" for check in health["checks"]):
            health["status"] = "warning"

        return health


# Create a singleton instance of the service
library_service = LibraryService(DatabaseService())
