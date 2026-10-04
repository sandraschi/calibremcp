"""Off-loop helpers for blocking SQLite work (BUG-062 follow-up).

FastMCP tool handlers are async: any synchronous sqlite3/SQLAlchemy call made
on the event loop stalls EVERY connection until it returns. Wrap blocking DB
calls with run_db_blocking() so they execute in a worker thread.

Thread-safety contract: the wrapped callable must open, use, and close its
own connection/session inside the call -- no shared Connection/Session object
may cross threads. All current call sites satisfy this (scoped_session is
thread-local; every wrapped helper provisions per-call sessions).
"""

import asyncio
from collections.abc import Callable
from typing import Any


async def run_db_blocking(func: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    """Run a synchronous DB callable in a worker thread and return its result."""
    return await asyncio.to_thread(func, *args, **kwargs)
