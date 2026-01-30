"""
Service for publisher-related operations in the Calibre MCP application.

Uses Calibre's publishers table and books_publishers_link.
Falls back to identifiers table (type='publisher') if publishers table does not exist.
"""

from typing import Dict, List, Optional, Any

from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc, asc
from sqlalchemy.exc import OperationalError

from ..db.database import DatabaseService
from ..db.models import Book, Identifier
from .book_service import BookService
from .base_service import NotFoundError
from ..logging_config import get_logger

logger = get_logger("calibremcp.services.publisher")


def _use_publishers_table(session) -> bool:
    """Check if publishers table exists."""
    try:
        session.execute("SELECT 1 FROM publishers LIMIT 1")
        return True
    except OperationalError:
        return False


class PublisherService:
    """Service for publisher operations. Uses publishers table or identifiers fallback."""

    def __init__(self, db: DatabaseService):
        self.db = db

    def _get_db_session(self):
        return self.db.session_scope()

    def _get_publisher_model(self, session):
        """Get Publisher model if publishers table exists."""
        try:
            from ..db.models import Publisher, books_publishers_link
            from sqlalchemy import text
            result = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='publishers'")
            )
            if result.fetchone():
                return Publisher, books_publishers_link
        except Exception:
            pass
        return None, None

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get paginated list of publishers."""
        with self._get_db_session() as session:
            Publisher, books_publishers_link = self._get_publisher_model(session)
            if Publisher is not None:
                return self._get_all_from_table(
                    session, Publisher, books_publishers_link, skip, limit, search, sort_by, sort_order
                )
            return self._get_all_from_identifiers(session, skip, limit, search, sort_by, sort_order)

    def _get_all_from_table(
        self, session, Publisher, books_publishers_link, skip, limit, search, sort_by, sort_order
    ) -> Dict[str, Any]:
        query = session.query(Publisher)
        if search:
            query = query.filter(Publisher.name.ilike(f"%{search}%"))
        total = query.count()
        sort_field = getattr(Publisher, sort_by, Publisher.name)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        publishers = query.offset(skip).limit(limit).all()
        items = []
        for p in publishers:
            book_count = (
                session.query(func.count(Book.id))
                .join(books_publishers_link, Book.id == books_publishers_link.c.book)
                .filter(books_publishers_link.c.publisher == p.id)
                .scalar()
            ) or 0
            items.append({"id": p.id, "name": p.name, "sort": getattr(p, "sort", None), "book_count": book_count})
        return {
            "items": items,
            "total": total,
            "page": (skip // limit) + 1,
            "per_page": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1,
        }

    def _get_all_from_identifiers(
        self, session, skip, limit, search, sort_by, sort_order
    ) -> Dict[str, Any]:
        subq = (
            session.query(Identifier.val.label("name"), func.count(Identifier.book).label("bc"))
            .filter(Identifier.type == "publisher")
            .filter(Identifier.val.isnot(None))
            .filter(Identifier.val != "")
            .group_by(Identifier.val)
        )
        if search:
            subq = subq.filter(Identifier.val.ilike(f"%{search}%"))
        subq = subq.subquery()
        q = session.query(subq)
        total = q.count()
        ord_col = subq.c.bc if sort_by == "book_count" else subq.c.name
        q = q.order_by(desc(ord_col) if sort_order.lower() == "desc" else asc(ord_col))
        rows = q.offset(skip).limit(limit).all()
        items = [{"id": None, "name": r.name, "sort": None, "book_count": r.bc} for r in rows]
        return {
            "items": items,
            "total": total,
            "page": (skip // limit) + 1,
            "per_page": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1,
        }

    def get_by_id(self, publisher_id: int) -> Dict[str, Any]:
        """Get publisher details by ID (publishers table only)."""
        with self._get_db_session() as session:
            from ..db.models import Publisher, books_publishers_link
            pub = session.query(Publisher).filter(Publisher.id == publisher_id).first()
            if not pub:
                raise NotFoundError(f"Publisher with ID {publisher_id} not found")
            book_count = (
                session.query(func.count(Book.id))
                .join(books_publishers_link, Book.id == books_publishers_link.c.book)
                .filter(books_publishers_link.c.publisher == publisher_id)
                .scalar()
            ) or 0
            return {"id": pub.id, "name": pub.name, "sort": pub.sort, "book_count": book_count}

    def get_by_name(self, name: str) -> Dict[str, Any]:
        """Get publisher by name (works with both publishers table and identifiers)."""
        with self._get_db_session() as session:
            Publisher, books_publishers_link = self._get_publisher_model(session)
            if Publisher is not None:
                pub = session.query(Publisher).filter(Publisher.name.ilike(f"%{name}%")).first()
                if not pub:
                    raise NotFoundError(f"Publisher matching '{name}' not found")
                book_count = (
                    session.query(func.count(Book.id))
                    .join(books_publishers_link, Book.id == books_publishers_link.c.book)
                    .filter(books_publishers_link.c.publisher == pub.id)
                    .scalar()
                ) or 0
                return {"id": pub.id, "name": pub.name, "sort": pub.sort, "book_count": book_count}
            cnt = (
                session.query(func.count(Identifier.book))
                .filter(Identifier.type == "publisher")
                .filter(Identifier.val.ilike(f"%{name}%"))
                .scalar()
            ) or 0
            if cnt == 0:
                raise NotFoundError(f"Publisher matching '{name}' not found")
            return {"id": None, "name": name, "sort": None, "book_count": cnt}

    def get_books_by_publisher(
        self,
        publisher_id: Optional[int] = None,
        publisher_name: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get books by publisher (ID or name)."""
        with self._get_db_session() as session:
            Publisher, books_publishers_link = self._get_publisher_model(session)
            if Publisher is not None and publisher_id is not None:
                pub = session.query(Publisher).filter(Publisher.id == publisher_id).first()
                if not pub:
                    raise NotFoundError(f"Publisher with ID {publisher_id} not found")
                books_query = (
                    session.query(Book)
                    .join(books_publishers_link, Book.id == books_publishers_link.c.book)
                    .filter(books_publishers_link.c.publisher == publisher_id)
                    .options(
                        joinedload(Book.authors),
                        joinedload(Book.tags),
                        joinedload(Book.data),
                    )
                )
                total = books_query.count()
                books = books_query.offset(offset).limit(limit).all()
                book_service = BookService(self.db)
                items = [book_service._to_response(b) for b in books]
                return {
                    "publisher": {"id": pub.id, "name": pub.name},
                    "items": items,
                    "total": total,
                    "page": (offset // limit) + 1,
                    "per_page": limit,
                    "total_pages": (total + limit - 1) // limit if total > 0 else 1,
                }
            name = publisher_name
            if publisher_id and not name and Publisher:
                pub = session.query(Publisher).filter(Publisher.id == publisher_id).first()
                name = pub.name if pub else None
            if not name:
                raise NotFoundError("Publisher ID or name required")
            book_ids = [
                r[0]
                for r in session.query(Identifier.book)
                .filter(Identifier.type == "publisher")
                .filter(Identifier.val.ilike(f"%{name}%"))
                .distinct()
                .all()
            ]
            if not book_ids:
                return {
                    "publisher": {"id": None, "name": name},
                    "items": [],
                    "total": 0,
                    "page": 1,
                    "per_page": limit,
                    "total_pages": 0,
                }
            books_query = (
                session.query(Book)
                .filter(Book.id.in_(book_ids))
                .options(
                    joinedload(Book.authors),
                    joinedload(Book.tags),
                    joinedload(Book.data),
                )
            )
            total = books_query.count()
            books = books_query.offset(offset).limit(limit).all()
            book_service = BookService(self.db)
            items = [book_service._to_response(b) for b in books]
            return {
                "publisher": {"id": None, "name": name},
                "items": items,
                "total": total,
                "page": (offset // limit) + 1,
                "per_page": limit,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            }

    def get_by_letter(self, letter: str) -> List[Dict[str, Any]]:
        """Get publishers whose names start with the given letter."""
        if len(letter) != 1 or not letter.isalpha():
            return []
        with self._get_db_session() as session:
            Publisher, books_publishers_link = self._get_publisher_model(session)
            if Publisher is not None:
                pubs = (
                    session.query(Publisher)
                    .filter(Publisher.name.ilike(f"{letter.lower()}%"))
                    .order_by(Publisher.name)
                    .all()
                )
                result = []
                for p in pubs:
                    book_count = (
                        session.query(func.count(Book.id))
                        .join(books_publishers_link, Book.id == books_publishers_link.c.book)
                        .filter(books_publishers_link.c.publisher == p.id)
                        .scalar()
                    ) or 0
                    result.append({"id": p.id, "name": p.name, "sort": p.sort, "book_count": book_count})
                return result
            rows = (
                session.query(Identifier.val.label("name"), func.count(Identifier.book).label("book_count"))
                .filter(Identifier.type == "publisher")
                .filter(Identifier.val.ilike(f"{letter.lower()}%"))
                .group_by(Identifier.val)
                .order_by(Identifier.val)
                .all()
            )
            return [{"id": None, "name": r.name, "sort": None, "book_count": r.book_count} for r in rows]

    def get_stats(self) -> Dict[str, Any]:
        """Get publisher statistics."""
        with self._get_db_session() as session:
            Publisher, books_publishers_link = self._get_publisher_model(session)
            if Publisher is not None:
                total = session.query(func.count(Publisher.id)).scalar()
                letter_counts = (
                    session.query(
                        func.upper(func.substr(Publisher.name, 1, 1)).label("letter"),
                        func.count(Publisher.id).label("count"),
                    )
                    .group_by("letter")
                    .order_by("letter")
                    .all()
                )
                top_subq = (
                    session.query(
                        books_publishers_link.c.publisher,
                        func.count(Book.id).label("book_count"),
                    )
                    .join(Book, Book.id == books_publishers_link.c.book)
                    .group_by(books_publishers_link.c.publisher)
                    .subquery()
                )
                top = (
                    session.query(Publisher, top_subq.c.book_count)
                    .join(top_subq, Publisher.id == top_subq.c.publisher)
                    .order_by(desc(top_subq.c.book_count))
                    .limit(10)
                    .all()
                )
                return {
                    "total_publishers": total,
                    "publishers_by_letter": [{"letter": l, "count": c} for l, c in letter_counts],
                    "top_publishers": [{"id": p.id, "name": p.name, "book_count": bc} for p, bc in top],
                }
            total = (
                session.query(func.count(func.distinct(Identifier.val)))
                .filter(Identifier.type == "publisher")
                .filter(Identifier.val.isnot(None))
                .filter(Identifier.val != "")
                .scalar()
            )
            letter_counts = (
                session.query(
                    func.upper(func.substr(Identifier.val, 1, 1)).label("letter"),
                    func.count(func.distinct(Identifier.val)).label("count"),
                )
                .filter(Identifier.type == "publisher")
                .filter(Identifier.val.isnot(None))
                .filter(Identifier.val != "")
                .group_by("letter")
                .order_by("letter")
                .all()
            )
            top = (
                session.query(Identifier.val.label("name"), func.count(Identifier.book).label("book_count"))
                .filter(Identifier.type == "publisher")
                .filter(Identifier.val.isnot(None))
                .filter(Identifier.val != "")
                .group_by(Identifier.val)
                .order_by(desc("book_count"))
                .limit(10)
                .all()
            )
            return {
                "total_publishers": total or 0,
                "publishers_by_letter": [{"letter": l, "count": c} for l, c in letter_counts],
                "top_publishers": [{"id": None, "name": n, "book_count": bc} for n, bc in top],
            }


def get_publisher_service() -> PublisherService:
    """Get publisher service with current database."""
    from ..db.database import get_database
    return PublisherService(get_database())
