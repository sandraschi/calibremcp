"""
Shared calibredb runner with content-server fallback.

Problem: every ``calibredb ... --library-path`` invocation fails while the
Calibre GUI (or another writer) holds the library::

    Another calibre program such as calibre-server.exe or the main calibre
    program is running.

The only supported route in that state is ``calibredb --with-library <url>``
against the Calibre content server (GUI: Preferences -> Sharing over the
net). These helpers implement exactly that: try direct first (fast when the
GUI is closed), and on lock-contention markers retry via the content server
configured with CALIBRE_SERVER_URL / CALIBRE_USERNAME / CALIBRE_PASSWORD.

Both sync (online_metadata service) and async (MCP tool helpers) entry
points are provided so callers do not need restructuring.
"""

from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("calibremcp.calibredb_runner")

DEFAULT_TIMEOUT_SECONDS = 180

# calibredb stderr markers meaning "another program holds the library".
_LIBRARY_LOCK_MARKERS = (
    "another calibre program",
    "is running",
    "database is locked",
    "could not lock",
)


@dataclass
class CalibredbResult:
    returncode: int
    stdout: str
    stderr: str
    via: str  # "direct" | "content_server"


def find_calibredb() -> str | None:
    """Locate the calibredb executable, or None when Calibre is not installed."""
    for name in ("calibredb", "calibredb.exe"):
        found = shutil.which(name)
        if found:
            return found
    return None


def content_server_target() -> tuple[str | None, str | None, str | None]:
    """Content-server URL + credentials from CalibreConfig (.env).

    Returns (url, username, password); url is None when not configured.
    Import is lazy so lightweight callers do not pay config import cost.
    """
    try:
        from ...config import CalibreConfig

        config = CalibreConfig.load_config()
        url = (config.server_url or "").rstrip("/")
        if not url:
            return None, None, None
        return url, config.username, config.password
    except Exception as e:
        logger.debug("Could not load content-server config: %s", e)
        return None, None, None


def _is_lock_error(stderr: str) -> bool:
    lowered = (stderr or "").lower()
    return any(m in lowered for m in _LIBRARY_LOCK_MARKERS)


def _server_prefix(calibredb: str, server_url: str, username: str | None, password: str | None) -> list[str]:
    """Global calibredb options for content-server mode (must precede subcommand)."""
    prefix = [calibredb, "--with-library", server_url]
    if username:
        prefix += ["--username", username]
    if password:
        prefix += ["--password", password]
    return prefix


def _find_calibredb_or_raise() -> str:
    calibredb = find_calibredb()
    if not calibredb:
        raise _server_error(
            "calibredb not found in PATH. Please install Calibre and ensure calibredb is available. "
            "See: https://calibre-ebook.com/download"
        )
    return calibredb


def _server_error(message: str) -> Exception:
    """MCPServerError when available (tool lane), RuntimeError otherwise (service lane)."""
    try:
        from ...tools.compat import MCPServerError

        return MCPServerError(message)
    except Exception:
        return RuntimeError(message)


def run_calibredb_sync(
    subcmd_args: Sequence[str],
    lib_path: str | Path | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> CalibredbResult:
    """Sync runner (for non-async services like online_metadata)."""
    calibredb = _find_calibredb_or_raise()
    direct_cmd = [calibredb, *subcmd_args]
    if lib_path is not None:
        direct_cmd += ["--library-path", str(lib_path)]
    logger.debug("calibredb (direct): %s", " ".join(direct_cmd))
    try:
        proc = subprocess.run(direct_cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise _server_error(f"calibredb timed out after {timeout}s. The library may be on a slow/network drive.") from e
    except OSError as e:
        raise _server_error(f"Could not run calibredb: {e}") from e
    stdout = (proc.stdout or b"").decode("utf-8", errors="replace")
    stderr = (proc.stderr or b"").decode("utf-8", errors="replace")
    if proc.returncode == 0:
        return CalibredbResult(proc.returncode, stdout, stderr, via="direct")

    if lib_path is not None and _is_lock_error(stderr):
        server_url, username, password = content_server_target()
        if server_url is None:
            logger.error("calibredb failed (library locked, no content server configured): %s", stderr)
            raise _server_error(
                "Library is locked by another Calibre program and no content server is configured. "
                f"Set CALIBRE_SERVER_URL (plus CALIBRE_USERNAME/CALIBRE_PASSWORD if needed). calibredb said: {stderr or 'Unknown error'}"
            )
        server_cmd = [*_server_prefix(calibredb, server_url, username, password), *subcmd_args]
        logger.info("Library locked by running Calibre; retrying via content server %s", server_url)
        try:
            proc2 = subprocess.run(server_cmd, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            raise _server_error(f"calibredb (content server) timed out after {timeout}s.") from e
        except OSError as e:
            raise _server_error(f"Could not run calibredb: {e}") from e
        return CalibredbResult(
            proc2.returncode,
            (proc2.stdout or b"").decode("utf-8", errors="replace"),
            (proc2.stderr or b"").decode("utf-8", errors="replace"),
            via="content_server",
        )
    return CalibredbResult(proc.returncode, stdout, stderr, via="direct")


async def run_calibredb(
    subcmd_args: Sequence[str],
    lib_path: str | Path | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> CalibredbResult:
    """Async runner (for MCP tool helpers). Same two-route behavior as sync."""
    calibredb = _find_calibredb_or_raise()
    direct_cmd = [calibredb, *subcmd_args]
    if lib_path is not None:
        direct_cmd += ["--library-path", str(lib_path)]
    logger.debug("calibredb (direct): %s", " ".join(direct_cmd))
    process = await asyncio.create_subprocess_exec(
        *direct_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except TimeoutError as e:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        raise _server_error(f"calibredb timed out after {timeout}s. The library may be on a slow/network drive.") from e
    stdout = (out or b"").decode("utf-8", errors="replace")
    stderr = (err or b"").decode("utf-8", errors="replace")
    if (process.returncode or 0) == 0:
        return CalibredbResult(process.returncode or 0, stdout, stderr, via="direct")

    if lib_path is not None and _is_lock_error(stderr):
        server_url, username, password = content_server_target()
        if server_url is None:
            logger.error("calibredb failed (library locked, no content server configured): %s", stderr)
            raise _server_error(
                "Library is locked by another Calibre program and no content server is configured. "
                f"Set CALIBRE_SERVER_URL (plus CALIBRE_USERNAME/CALIBRE_PASSWORD if needed). calibredb said: {stderr or 'Unknown error'}"
            )
        server_cmd = [*_server_prefix(calibredb, server_url, username, password), *subcmd_args]
        logger.info("Library locked by running Calibre; retrying via content server %s", server_url)
        process2 = await asyncio.create_subprocess_exec(
            *server_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out2, err2 = await asyncio.wait_for(process2.communicate(), timeout=timeout)
        except TimeoutError as e:
            try:
                process2.kill()
            except ProcessLookupError:
                pass
            raise _server_error(f"calibredb (content server) timed out after {timeout}s.") from e
        return CalibredbResult(
            process2.returncode or 0,
            (out2 or b"").decode("utf-8", errors="replace"),
            (err2 or b"").decode("utf-8", errors="replace"),
            via="content_server",
        )
    return CalibredbResult(process.returncode or 0, stdout, stderr, via="direct")
