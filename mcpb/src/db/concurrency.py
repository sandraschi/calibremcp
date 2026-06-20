"""
Database concurrency for calibre-mcp.

Two problems solved here:

1. Within-process: multiple async tool calls hitting write paths simultaneously.
   SQLAlchemy scoped_session serializes at session-creation level but not at
   transaction commit level. An asyncio.Lock around all writes fixes this.

2. Cross-process: stdio (Claude Desktop) + SSE (webapp fleet) both open
   metadata.db. WAL mode handles concurrent readers fine; for writers we set
   busy_timeout=10000 so SQLite retries for 10s before raising OperationalError
   instead of failing immediately.

Usage (write path):
    async with write_session(db) as session:
        session.add(obj)
        # commit happens automatically on exit

Usage (read path — no lock needed with WAL):
    with db.session_scope() as session:
        results = session.query(Model).all()
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session

logger = logging.getLogger("calibremcp.db.concurrency")

# One write lock per process. All write operations acquire this before
# opening a transaction. Reads bypass it entirely — WAL allows concurrent reads.
_write_lock = asyncio.Lock()


@asynccontextmanager
async def write_session(db_service) -> AsyncGenerator[Session, None]:
    """
    Async context manager that serializes write transactions within this process.

    Acquires the process-wide write lock, opens a session, yields it, then
    commits on clean exit or rolls back on exception.

    Cross-process safety is handled by SQLite WAL + busy_timeout=10000ms set
    in DatabaseService.initialize().

    Example:
        async with write_session(db) as session:
            session.add(Book(...))
    """
    async with _write_lock:
        if db_service._session_factory is None:
            raise RuntimeError("DatabaseService not initialized")
        session: Session = db_service._session_factory()
        try:
            yield session
            session.commit()
        except Exception as exc:
            session.rollback()
            logger.exception("Write transaction rolled back: %s", exc)
            raise
        finally:
            session.close()


def is_write_locked() -> bool:
    """Diagnostic: returns True if a write is currently in progress."""
    return _write_lock.locked()
