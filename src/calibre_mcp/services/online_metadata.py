"""
Download book metadata from Calibre's online sources and apply to the local library.

Uses ``fetch-ebook-metadata`` and ``calibredb set_metadata`` (same flow as Calibre GUI
"Download metadata") when a local ``metadata.db`` is in use.
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..db.database import DatabaseService
from ..utils.subprocess_utils import _cmd
from .base_service import NotFoundError
from .book_service import BookService

logger = logging.getLogger(__name__)

_FETCH_NAMES = ("fetch-ebook-metadata", "fetch-ebook-metadata.exe")
_CALIBREDB_NAMES = ("calibredb", "calibredb.exe")
_WIN_FETCH_GUESSES = (
    Path(r"C:\Program Files\Calibre2\fetch-ebook-metadata.exe"),
    Path(r"C:\Program Files\Calibre\fetch-ebook-metadata.exe"),
)
_WIN_DB_GUESSES = (
    Path(r"C:\Program Files\Calibre2\calibredb.exe"),
    Path(r"C:\Program Files\Calibre\calibredb.exe"),
)


def find_fetch_ebook_metadata() -> str | None:
    for name in _FETCH_NAMES:
        found = shutil.which(name)
        if found:
            return found
    for guess in _WIN_FETCH_GUESSES:
        if guess.is_file():
            return str(guess)
    return None


def find_calibredb() -> str | None:
    for name in _CALIBREDB_NAMES:
        found = shutil.which(name)
        if found:
            return found
    for guess in _WIN_DB_GUESSES:
        if guess.is_file():
            return str(guess)
    return None


def _normalize_isbn(raw: str) -> str:
    return re.sub(r"[\s-]", "", raw.strip())


def _book_identifiers(book: dict[str, Any]) -> dict[str, str]:
    idents = book.get("identifiers") or {}
    if not isinstance(idents, dict):
        return {}
    out: dict[str, str] = {}
    for k, v in idents.items():
        if k and v is not None and str(v).strip():
            out[str(k).lower()] = str(v).strip()
    top_isbn = book.get("isbn")
    if top_isbn and "isbn" not in out:
        out["isbn"] = str(top_isbn).strip()
    return out


def apply_online_metadata_for_book(
    book_id: int,
    *,
    include_cover: bool = True,
    fetch_timeout: int = 90,
) -> dict[str, Any]:
    """
    Fetch metadata from the internet and write it into the Calibre library for ``book_id``.

    Returns:
        ``{"success": True, "message": "..."}`` or ``{"success": False, "error": "..."}``.
    """
    fetch_exe = find_fetch_ebook_metadata()
    calibredb = find_calibredb()
    if not fetch_exe:
        return {
            "success": False,
            "error": "fetch-ebook-metadata was not found. Install Calibre and ensure its folder is on PATH.",
        }
    if not calibredb:
        return {
            "success": False,
            "error": "calibredb was not found in PATH. Install Calibre and ensure its folder is on PATH.",
        }

    db = DatabaseService()
    if db._engine is None or not db._current_db_path:
        return {
            "success": False,
            "error": "No local Calibre library is loaded. Metadata download works only for direct-library mode.",
        }

    svc = BookService(db)
    try:
        book = svc.get_by_id(book_id)
    except NotFoundError:
        return {"success": False, "error": f"Book {book_id} was not found."}

    library_path = svc._get_library_base_path()
    if not library_path:
        return {"success": False, "error": "Could not resolve the library directory for calibredb."}

    title = (book.get("title") or "").strip()
    authors = book.get("authors") or []
    author_names: list[str] = []
    for a in authors:
        n = (a.get("name") or "").strip() if isinstance(a, dict) else str(a).strip()
        if n:
            author_names.append(n)
    authors_str = " & ".join(author_names) if author_names else ""

    idents = _book_identifiers(book)
    isbn_raw = (
        idents.get("isbn")
        or idents.get("isbn13")
        or idents.get("isbn10")
        or idents.get("isbn-13")
        or idents.get("isbn-10")
        or ""
    )
    isbn_clean = _normalize_isbn(isbn_raw) if isbn_raw else ""

    if not title and not authors_str and not isbn_clean:
        return {
            "success": False,
            "error": "This record has no title, authors, or ISBN — add at least one before downloading metadata.",
        }

    cmd: list[str] = [
        fetch_exe,
        "-o",
        "-d",
        str(fetch_timeout),
    ]
    if title:
        cmd.extend(["--title", title])
    if authors_str:
        cmd.extend(["--authors", authors_str])
    if isbn_clean and re.match(r"^[\dX]{10,17}$", isbn_clean, re.I):
        cmd.extend(["--isbn", isbn_clean])

    skip_ident_keys = frozenset(
        {"isbn", "isbn10", "isbn13", "isbn-10", "isbn-13", "lccn", "uuid"}
    )
    extra = 0
    for k, v in idents.items():
        if k in skip_ident_keys or not v:
            continue
        cmd.extend(["--identifier", f"{k}:{v}"])
        extra += 1
        if extra >= 8:
            break

    with tempfile.TemporaryDirectory(prefix="calibre_fetch_meta_") as tmp:
        tmp_path = Path(tmp)
        opf_path = tmp_path / "metadata.opf"
        cover_path = tmp_path / "cover.jpg"
        run_cmd = list(cmd)
        if include_cover:
            run_cmd.extend(["--cover", str(cover_path)])

        try:
            proc = _cmd(
                run_cmd,
                timeout=fetch_timeout + 60,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Timed out after {fetch_timeout + 60}s while fetching metadata."}
        except OSError as e:
            return {"success": False, "error": f"Could not run fetch-ebook-metadata: {e}"}

        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip()
            if "Another calibre program" in err or "another calibre program" in err.lower():
                return {
                    "success": False,
                    "error": "Calibre has the library locked (e.g. main Calibre or Content server). Close it or use calibredb against the Content server URL.",
                }
            return {
                "success": False,
                "error": err or "fetch-ebook-metadata exited with an error.",
            }

        opf_text = (proc.stdout or "").strip()
        if len(opf_text) < 80 or "<package" not in opf_text.lower():
            return {
                "success": False,
                "error": "Online lookup returned no usable OPF metadata. Try filling in ISBN or title/author in Calibre.",
            }

        opf_path.write_text(opf_text, encoding="utf-8")

        set_cmd = [
            calibredb,
            f"--with-library={library_path}",
            "set_metadata",
            str(book_id),
            str(opf_path),
        ]
        try:
            proc2 = _cmd(
                set_cmd,
                timeout=120,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timed out while applying metadata with calibredb."}
        except OSError as e:
            return {"success": False, "error": f"Could not run calibredb: {e}"}

        if proc2.returncode != 0:
            err = (proc2.stderr or proc2.stdout or "").strip()
            if "Another calibre program" in err or "another calibre program" in err.lower():
                return {
                    "success": False,
                    "error": "Calibre has the library locked. Close the main Calibre app (or disconnect the Content server) and try again.",
                }
            return {"success": False, "error": err or "calibredb set_metadata failed."}

        warnings: list[str] = []
        if include_cover and cover_path.is_file() and cover_path.stat().st_size > 64:
            cover_cmd = [
                calibredb,
                f"--with-library={library_path}",
                "set_metadata",
                str(book_id),
                "--field",
                f"cover:{cover_path}",
            ]
            try:
                proc3 = _cmd(
                    cover_cmd,
                    timeout=90,
                    encoding="utf-8",
                    errors="replace",
                )
                if proc3.returncode != 0:
                    w = (proc3.stderr or proc3.stdout or "").strip()
                    if w:
                        warnings.append(f"Cover was not updated: {w}")
            except (subprocess.TimeoutExpired, OSError) as e:
                warnings.append(f"Cover step skipped: {e}")

        msg = "Metadata was updated from online sources."
        if warnings:
            msg += " " + " ".join(warnings)
        out: dict[str, Any] = {"success": True, "message": msg}
        if warnings:
            out["warning"] = warnings[0]
        logger.info("Online metadata applied for book_id=%s", book_id)
        return out
