"""
Service for description/comment operations (Calibre's comment field = book description).

Read-only operations for browsing: list, get, get_books, stats, by_letter.
For create/update/delete use manage_comments.
"""

from typing import Dict, List, Optional, Any

from sqlalchemy.orm import joinedload
from sqlalchemy import func, asc

from ..db.database import DatabaseService
from ..db.models import Book, Comment, Author
from .book_service import BookService
from ..logging_config import get_logger

logger = get_logger("calibremcp.services.description")


class DescriptionService:
    """Service for description (Calibre comment field) browse operations."""

    def __init__(self, db: DatabaseService):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        has_description: Optional[bool] = None,
        sort_by: str = "title",
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """
        List books with description info.
        If has_description=True, only books with non-empty descriptions.
        If has_description=False, only books without descriptions.
        If search provided, search in description text.
        """
        with self.db.session_scope() as session:
            query = (
                session.query(Book)
                .outerjoin(Comment, Book.id == Comment.book)
                .options(
                    joinedload(Book.authors),
                    joinedload(Book.tags),
                    joinedload(Book.comments),
                )
            )

            if has_description is True:
                query = query.filter(
                    Comment.id.isnot(None),
                    func.length(Comment.text) > 0,
                    Comment.text.isnot(None),
                )
            elif has_description is False:
                query = query.filter(
                    (Comment.id.is_(None)) |
                    (Comment.text.is_(None)) |
                    (func.length(Comment.text) == 0)
                )

            if search:
                query = query.filter(Comment.text.ilike(f"%{search}%"))

            total = query.count()

            sort_field = getattr(Book, sort_by, Book.title)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(asc(sort_field))

            books = query.offset(skip).limit(limit).all()
            book_service = BookService(self.db)

            items = []
            for b in books:
                d = book_service._to_response(b)
                comm = getattr(b, "comments", None)
                if comm is None:
                    comm = session.query(Comment).filter(Comment.book == b.id).first()
                desc_text = (comm.text or "") if comm else ""
                d["description_preview"] = desc_text[:200] + "..." if len(desc_text) > 200 else desc_text
                d["has_description"] = bool(desc_text.strip())
                items.append(d)

            return {
                "items": items,
                "total": total,
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            }

    def get_by_book_id(self, book_id: int) -> Dict[str, Any]:
        """Get description for a book."""
        with self.db.session_scope() as session:
            book = (
                session.query(Book)
                .options(joinedload(Book.authors), joinedload(Book.comments))
                .filter(Book.id == book_id)
                .first()
            )
            if not book:
                return {"success": False, "error": "Book not found", "book_id": book_id}

            # Comment is 1:1 with book (relationship or direct query)
            comm = getattr(book, "comments", None) or session.query(Comment).filter(Comment.book == book_id).first()
            desc_text = (comm.text or "") if comm else ""

            book_service = BookService(self.db)
            book_dict = book_service._to_response(book)

            return {
                "success": True,
                "book_id": book_id,
                "title": book_dict.get("title", ""),
                "description": desc_text,
                "has_description": bool(desc_text.strip()),
                "description_length": len(desc_text),
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get description coverage statistics."""
        with self.db.session_scope() as session:
            total_books = session.query(func.count(Book.id)).scalar() or 0
            with_desc = (
                session.query(func.count(Comment.id))
                .filter(
                    Comment.text.isnot(None),
                    func.length(Comment.text) > 0,
                )
                .scalar()
            ) or 0
            without_desc = total_books - with_desc
            avg_len = (
                session.query(func.avg(func.length(Comment.text)))
                .filter(
                    Comment.text.isnot(None),
                    func.length(Comment.text) > 0,
                )
                .scalar()
            )
            avg_len = int(avg_len) if avg_len else 0

            return {
                "total_books": total_books,
                "with_description": with_desc,
                "without_description": without_desc,
                "coverage_percent": round(100.0 * with_desc / total_books, 1) if total_books else 0,
                "avg_description_length": avg_len,
            }

    def get_by_letter(self, letter: str) -> List[Dict[str, Any]]:
        """Get books whose title starts with letter and have descriptions."""
        if len(letter) != 1 or not letter.isalpha():
            return []

        with self.db.session_scope() as session:
            books = (
                session.query(Book)
                .join(Comment, Book.id == Comment.book)
                .filter(
                    Book.title.ilike(f"{letter.lower()}%"),
                    Comment.text.isnot(None),
                    func.length(Comment.text) > 0,
                )
                .options(joinedload(Book.authors))
                .order_by(Book.title)
                .all()
            )

            book_service = BookService(self.db)
            result = []
            for b in books:
                d = book_service._to_response(b)
                comm = session.query(Comment).filter(Comment.book == b.id).first()
                desc = (comm.text or "")[:150] + "..." if comm and comm.text and len(comm.text) > 150 else (comm.text or "") if comm else ""
                d["description_preview"] = desc
                result.append(d)
            return result


def get_description_service() -> "DescriptionService":
    """Get description service with current database."""
    from ..db.database import get_database
    return DescriptionService(get_database())
