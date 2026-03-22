"""
Service for date/time-based book queries.

Uses Calibre's books.timestamp (added date) and books.pubdate (edition publication date).
"""

from datetime import datetime
from typing import Any

from sqlalchemy import func

from ..db.database import DatabaseService, get_database
from ..db.models import Book
from ..logging_config import get_logger
from .book_service import BookService

logger = get_logger("calibremcp.services.times")


def _parse_date(s: str) -> datetime | None:
    """Parse YYYY-MM-DD or partial date string."""
    if not s or not isinstance(s, str):
        return None
    raw = s.strip().split("T")[0][:10]
    for fmt, n in (("%Y-%m-%d", 10), ("%Y-%m", 7), ("%Y", 4)):
        try:
            return datetime.strptime(raw[:n], fmt)
        except (ValueError, TypeError, IndexError):
            continue
    return None


class TimesService:
    """Date-based book queries: added, published, stats by month."""

    def __init__(self, db: DatabaseService | None = None):
        self.db = db or get_database()
        self._book_svc = BookService(self.db)

    def _get_session(self):
        return self.db.session_scope()

    def added_in_range(
        self,
        after: str,
        before: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Books added (timestamp) between after and before."""
        start = _parse_date(after)
        if not start:
            return {"items": [], "total": 0, "error": "Invalid after date (use YYYY-MM-DD)"}
        end = _parse_date(before) if before else datetime.utcnow()
        if end and start > end:
            return {"items": [], "total": 0, "error": "after must be before before"}

        return self._book_svc.get_all(
            skip=offset,
            limit=limit,
            sort_by="timestamp",
            sort_order="desc",
            added_after=after,
            added_before=before,
        )

    def published_in_range(
        self,
        after: str,
        before: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Books with pubdate (edition date) between after and before."""
        start = _parse_date(after)
        if not start:
            return {"items": [], "total": 0, "error": "Invalid after date (use YYYY-MM-DD)"}
        end = _parse_date(before) if before else None

        return self._book_svc.get_all(
            skip=offset,
            limit=limit,
            sort_by="pubdate",
            sort_order="desc",
            pubdate_start=after,
            pubdate_end=before,
        )

    def recent_additions(self, limit: int = 20) -> dict[str, Any]:
        """Most recently added books."""
        return self._book_svc.get_all(
            skip=0,
            limit=limit,
            sort_by="timestamp",
            sort_order="desc",
        )

    def stats_by_month_added(self, year: int | None = None) -> dict[str, Any]:
        """Count of books added per month. Optionally filter by year."""
        with self._get_session() as session:
            q = (
                session.query(
                    func.strftime("%Y", Book.timestamp).label("yr"),
                    func.strftime("%m", Book.timestamp).label("mo"),
                    func.count(Book.id).label("count"),
                )
                .filter(Book.timestamp.isnot(None))
                .group_by(func.strftime("%Y-%m", Book.timestamp))
                .order_by(func.strftime("%Y-%m", Book.timestamp))
            )
            if year:
                q = q.filter(func.strftime("%Y", Book.timestamp) == str(year))
            rows = q.all()
            items = [
                {
                    "year": int(r.yr) if r.yr else None,
                    "month": int(r.mo) if r.mo else None,
                    "count": r.count,
                }
                for r in rows
            ]
            return {"by_month": items, "total_books": sum(r.count for r in rows)}

    def stats_by_month_published(self, year: int | None = None) -> dict[str, Any]:
        """Count of books by pubdate (edition) per month."""
        with self._get_session() as session:
            q = (
                session.query(
                    func.strftime("%Y", Book.pubdate).label("yr"),
                    func.strftime("%m", Book.pubdate).label("mo"),
                    func.count(Book.id).label("count"),
                )
                .filter(Book.pubdate.isnot(None))
                .group_by(func.strftime("%Y-%m", Book.pubdate))
                .order_by(func.strftime("%Y-%m", Book.pubdate))
            )
            if year:
                q = q.filter(func.strftime("%Y", Book.pubdate) == str(year))
            rows = q.all()
            items = [
                {
                    "year": int(r.yr) if r.yr else None,
                    "month": int(r.mo) if r.mo else None,
                    "count": r.count,
                }
                for r in rows
            ]
            return {"by_month": items, "total_books": sum(r.count for r in rows)}

    def date_stats(self) -> dict[str, Any]:
        """Summary: date ranges, totals with dates."""
        with self._get_session() as session:
            ts = (
                session.query(
                    func.min(Book.timestamp).label("min_added"),
                    func.max(Book.timestamp).label("max_added"),
                    func.count(Book.id).label("total"),
                )
                .filter(Book.timestamp.isnot(None))
                .first()
            )
            pd = (
                session.query(
                    func.min(Book.pubdate).label("min_pub"),
                    func.max(Book.pubdate).label("max_pub"),
                )
                .filter(Book.pubdate.isnot(None))
                .first()
            )
            return {
                "added_date_range": {
                    "earliest": ts.min_added.isoformat() if ts and ts.min_added else None,
                    "latest": ts.max_added.isoformat() if ts and ts.max_added else None,
                    "books_with_timestamp": ts.total if ts else 0,
                },
                "pubdate_range": {
                    "earliest": pd.min_pub.isoformat() if pd and pd.min_pub else None,
                    "latest": pd.max_pub.isoformat() if pd and pd.max_pub else None,
                },
            }
