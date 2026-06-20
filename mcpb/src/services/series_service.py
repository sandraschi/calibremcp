"""
Service for series-related operations in the Calibre MCP application.
"""

from typing import Any

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import joinedload

from ..db.database import DatabaseService
from ..db.models import Book, Series, books_series_link
from ..logging_config import get_logger
from .base_service import NotFoundError
from .book_service import BookService

logger = get_logger("calibremcp.services.series")


class SeriesService:
    """Service for series operations (list, get, get_books, stats, by_letter)."""

    def __init__(self, db: DatabaseService):
        self.db = db

    def _get_db_session(self):
        return self.db.session_scope()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """Get paginated list of series with optional search."""
        with self._get_db_session() as session:
            query = session.query(Series)

            if search:
                query = query.filter(Series.name.ilike(f"%{search}%"))

            total = query.count()

            sort_field = getattr(Series, sort_by, Series.name)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(asc(sort_field))

            series_list = query.offset(skip).limit(limit).all()

            items = []
            for s in series_list:
                book_count = (
                    session.query(func.count(Book.id))
                    .join(books_series_link, Book.id == books_series_link.c.book)
                    .filter(books_series_link.c.series == s.id)
                    .scalar()
                ) or 0
                items.append(
                    {
                        "id": s.id,
                        "name": s.name,
                        "sort": s.sort,
                        "book_count": book_count,
                    }
                )

            return {
                "items": items,
                "total": total,
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            }

    def get_by_id(self, series_id: int) -> dict[str, Any]:
        """Get series details by ID."""
        with self._get_db_session() as session:
            series = session.query(Series).filter(Series.id == series_id).first()
            if not series:
                raise NotFoundError(f"Series with ID {series_id} not found")

            book_count = (
                session.query(func.count(Book.id))
                .join(books_series_link, Book.id == books_series_link.c.book)
                .filter(books_series_link.c.series == series_id)
                .scalar()
            ) or 0

            return {
                "id": series.id,
                "name": series.name,
                "sort": series.sort,
                "book_count": book_count,
            }

    def get_books_by_series(
        self, series_id: int, limit: int = 50, offset: int = 0
    ) -> dict[str, Any]:
        """Get books in a series with pagination."""
        with self._get_db_session() as session:
            series = session.query(Series).filter(Series.id == series_id).first()
            if not series:
                raise NotFoundError(f"Series with ID {series_id} not found")

            books_query = (
                session.query(Book)
                .join(books_series_link, Book.id == books_series_link.c.book)
                .filter(books_series_link.c.series == series_id)
                .options(
                    joinedload(Book.authors),
                    joinedload(Book.tags),
                    joinedload(Book.data),
                )
            )

            total = books_query.count()
            books = books_query.order_by(Book.series_index).offset(offset).limit(limit).all()

            book_service = BookService(self.db)
            items = [book_service._to_response(b) for b in books]

            return {
                "series": {"id": series.id, "name": series.name},
                "items": items,
                "total": total,
                "page": (offset // limit) + 1,
                "per_page": limit,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            }

    def get_series_by_letter(self, letter: str) -> list[dict[str, Any]]:
        """Get series whose names start with the given letter."""
        if len(letter) != 1 or not letter.isalpha():
            return []

        with self._get_db_session() as session:
            series_list = (
                session.query(Series)
                .filter(Series.name.ilike(f"{letter.lower()}%"))
                .order_by(Series.name)
                .all()
            )

            result = []
            for s in series_list:
                book_count = (
                    session.query(func.count(Book.id))
                    .join(books_series_link, Book.id == books_series_link.c.book)
                    .filter(books_series_link.c.series == s.id)
                    .scalar()
                ) or 0
                result.append(
                    {
                        "id": s.id,
                        "name": s.name,
                        "sort": s.sort,
                        "book_count": book_count,
                    }
                )
            return result

    def get_series_stats(self) -> dict[str, Any]:
        """Get series statistics."""
        with self._get_db_session() as session:
            total_series = session.query(func.count(Series.id)).scalar()

            letter_counts = (
                session.query(
                    func.upper(func.substr(Series.name, 1, 1)).label("letter"),
                    func.count(Series.id).label("count"),
                )
                .group_by("letter")
                .order_by("letter")
                .all()
            )

            top_series_subq = (
                session.query(
                    books_series_link.c.series,
                    func.count(Book.id).label("book_count"),
                )
                .join(Book, Book.id == books_series_link.c.book)
                .group_by(books_series_link.c.series)
                .subquery()
            )

            top_series = (
                session.query(Series, top_series_subq.c.book_count)
                .join(top_series_subq, Series.id == top_series_subq.c.series)
                .order_by(desc(top_series_subq.c.book_count))
                .limit(10)
                .all()
            )

            return {
                "total_series": total_series,
                "series_by_letter": [
                    {"letter": letter, "count": count} for letter, count in letter_counts
                ],
                "top_series": [
                    {"id": s.id, "name": s.name, "book_count": bc} for s, bc in top_series
                ],
            }


def get_series_service() -> SeriesService:
    """Get series service with current database."""
    from ..db.database import get_database

    return SeriesService(get_database())
