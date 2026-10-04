"""BUG-062 follow-up: blocking DB work runs off the event loop.

run_db_blocking() must execute the callable in a worker thread (so a slow
SQLite scan never parks the daemon's event loop) and concurrent blocking
calls must overlap rather than serialize.
"""

import asyncio
import threading
import time

from calibre_mcp.utils.db_async import run_db_blocking


async def test_runs_off_event_loop():
    loop_thread = threading.current_thread()

    def whoami():
        return threading.current_thread()

    worker = await run_db_blocking(whoami)
    assert worker is not loop_thread


async def test_concurrent_blocking_calls_overlap():
    def slow():
        time.sleep(0.5)
        return 1

    start = time.monotonic()
    results = await asyncio.gather(*(run_db_blocking(slow) for _ in range(2)))
    elapsed = time.monotonic() - start
    assert results == [1, 1]
    assert elapsed < 0.9  # serialized on-loop would take >= 1.0s


async def test_propagates_result_and_errors():
    assert await run_db_blocking(lambda: 42) == 42
    try:
        await run_db_blocking(lambda: 1 / 0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("expected ZeroDivisionError")
