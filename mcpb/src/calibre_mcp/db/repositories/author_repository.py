"""
Repository for handling author-related database operations.
"""

from typing import Any

from sqlalchemy import desc, func
from sqlalchemy.orm import joinedload

from ...db.base_repository import BaseRepository
from ...models.author import Author
from ...models.book import Book
from ...models.series import Series


class AuthorRepository(BaseRepository[Author]):
    """Repository for author-related database operations."""

    def __init__(self, db):
        """Initialize with database service."""
        super().__init__(db, Author)

    def get_by_name(self, name: str) -> Author | None:
        """Get an author by their exact name."""
        with self._db.session_scope() as session:
            return session.query(Author).filter(Author.name == name).first()

    def search(self, query: str, limit: int = 10) -> list[Author]:
        """Search for authors by name."""
        with self._db.session_scope() as session:
            return (
                session.query(Author)
                .filter(Author.name.ilike(f"%{query}%"))
                .order_by(Author.sort)
                .limit(limit)
                .all()
            )

    def get_books_count(self, author_id: int) -> int:
        """Get the number of books by an author."""
        with self._db.session_scope() as session:
            return (
                session.query(func.count(Book.id))
                .join(Book.authors)
                .filter(Author.id == author_id)
                .scalar()
                or 0
            )

    def get_books(self, author_id: int, limit: int = 10, offset: int = 0) -> list[dict]:
        """Get books by an author with pagination."""
        with self._db.session_scope() as session:
            books = (
                session.query(Book)
                .join(Book.authors)
                .filter(Author.id == author_id)
                .options(joinedload(Book.authors))
                .order_by(Book.sort)
                .offset(offset)
                .limit(limit)
                .all()
            )
            return [{"id": b.id, "title": b.title, "sort": b.sort} for b in books]

    def get_series(self, author_id: int) -> list[dict]:
        """Get all series by an author."""
        with self._db.session_scope() as session:
            series = (
                session.query(Series, func.count(Book.id).label("book_count"))
                .join(Book.series_rel)
                .join(Book.authors)
                .filter(Author.id == author_id)
                .group_by(Series.id)
                .order_by(Series.name)
                .all()
            )
            return [{"id": s.id, "name": s.name, "book_count": count} for s, count in series]

    def get_stats(self) -> dict[str, Any]:
        """Get author statistics."""
        with self._db.session_scope() as session:
            stats = {}

            # Total authors
            stats["total_authors"] = session.query(func.count(Author.id)).scalar()

            # Authors by book count
            top_authors = (
                session.query(Author.id, Author.name, func.count(Book.id).label("book_count"))
                .join(Author.books)
                .group_by(Author.id, Author.name)
                .order_by(desc("book_count"))
                .limit(10)
                .all()
            )
            stats["top_authors"] = [
                {"id": a_id, "name": name, "book_count": count} for a_id, name, count in top_authors
            ]

            return stats

    def get_author_stats(self) -> dict[str, Any]:
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

            single_book_count = (
                session.query(func.count()).select_from(single_book_authors).scalar() or 0
            )

            # Top 10 most prolific authors
            top_authors = (
                session.query(Author.name, func.count(Book.id).label("book_count"))
                .join(Author.books)
                .group_by(Author.id, Author.name)
                .order_by(desc("book_count"))
                .limit(10)
                .all()
            )

            # Author name length statistics
            name_lengths = session.query(
                func.min(func.length(Author.name)).label("min_length"),
                func.max(func.length(Author.name)).label("max_length"),
                func.avg(func.length(Author.name)).label("avg_length"),
            ).scalar()

            return {
                "total_authors": total_authors,
                "authors_with_single_book": single_book_count,
                "top_authors": [{"name": name, "book_count": count} for name, count in top_authors],
                "name_statistics": {
                    "min_length": name_lengths[0],
                    "max_length": name_lengths[1],
                    "avg_length": float(name_lengths[2]) if name_lengths[2] else 0.0,
                },
            }

    def _format_author(self, author: Author, book_count: int = 0) -> dict[str, Any]:
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
            "id": author.id,
            "name": author.name,
            "sort": author.sort,
            "link": author.link,
            "book_count": book_count,
        }

    def _get_sort_field(self, sort_by: str):
        """
        Get the SQLAlchemy field to sort by.

        Args:
            sort_by: Field name to sort by

        Returns:
            SQLAlchemy column expression or None if invalid
        """
        sort_fields = {"name": Author.name, "sort": Author.sort, "book_count": func.count(Book.id)}
        return sort_fields.get(sort_by.lower(), Author.name)

    def get_books_by_author(
        self, author_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[dict[str, Any]], int]:
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
                    joinedload(Book.tags),
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
            book_repo = self._db.get_repository("books")
            if hasattr(book_repo, "_format_book"):
                formatted_books = [book_repo._format_book(book) for book in books]
            else:
                formatted_books = [
                    {
                        "id": book.id,
                        "title": book.title,
                        "authors": [{"id": a.id, "name": a.name} for a in book.authors],
                        "series": book.series[0].name if book.series else None,
                        "series_id": book.series[0].id if book.series else None,
                        "series_index": book.series_index,
                        "rating": book.ratings[0].rating if book.ratings else 0,
                        "tags": [{"id": t.id, "name": t.name} for t in book.tags],
                    }
                    for book in books
                ]

            return formatted_books, total

    def search_authors(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
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

    def _process_author_result(self, row: dict[str, Any]) -> dict[str, Any]:
        """Process an author result row into a more usable format."""
        if not row:
            return {}

        return {
            "id": row["id"],
            "name": row["name"],
            "sort": row.get("sort", row["name"]),
            "link": row.get("link", ""),
            "book_count": row.get("book_count", 0),
        }

    def _process_book_result(self, row: dict[str, Any]) -> dict[str, Any]:
        """Process a book result row into a more usable format."""
        if not row:
            return {}

        # Process authors and tags from pipe-separated strings to lists
        authors = row.get("authors", "").split("|") if row.get("authors") else []
        tags = row.get("tags", "").split("|") if row.get("tags") else []

        return {
            "id": row["id"],
            "title": row["title"],
            "sort": row.get("sort"),
            "timestamp": row.get("timestamp"),
            "pubdate": row.get("pubdate"),
            "series_index": row.get("series_index", 0.0),
            "author_sort": row.get("author_sort"),
            "isbn": row.get("isbn"),
            "path": row.get("path"),
            "has_cover": bool(row.get("has_cover", 0)),
            "authors": [a for a in authors if a],  # Remove empty strings
            "tags": [t for t in tags if t],  # Remove empty strings
            "series": row.get("series_name"),
            "rating": row.get("rating"),
        }
