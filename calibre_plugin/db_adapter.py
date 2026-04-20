"""
Direct SQLite access to calibre_mcp_data.db.
Matches CalibreMCP schema - no MCP process required.

Schema v2 (2026-04-16):
  book_extended_metadata — translator, first_published, original_language,
                           edition_notes, read_status, date_read, mood,
                           culprit, locked_room_type
  user_comments          — free-text personal notes
"""

import sqlite3
from pathlib import Path
from typing import Any


def _get_db_path() -> Path:
    from calibre_plugins.calibre_mcp_integration.config import get_mcp_user_data_dir

    data_dir = Path(get_mcp_user_data_dir())
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        data_dir = Path.cwd() / ".calibre-mcp-data"
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "calibre_mcp_data.db"


# ── Schema ────────────────────────────────────────────────────────────────────

def _ensure_tables(conn: sqlite3.Connection) -> None:
    """Create tables if missing, then migrate any missing columns."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS book_extended_metadata (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id          INTEGER NOT NULL,
            library_path     TEXT NOT NULL,
            translator       TEXT,
            first_published  TEXT,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS user_comments (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id      INTEGER NOT NULL,
            library_path TEXT NOT NULL,
            comment_text TEXT NOT NULL DEFAULT '',
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id      TEXT
        );
    """)
    _migrate(conn)


# Columns added in schema v2 — each entry is (column_name, sql_type, default)
_V2_COLUMNS = [
    ("original_language", "TEXT",    "NULL"),
    ("edition_notes",     "TEXT",    "NULL"),
    ("read_status",       "TEXT",    "NULL"),   # unread/reading/read/abandoned/re-reading
    ("date_read",         "TEXT",    "NULL"),   # ISO date string YYYY-MM-DD
    ("mood",              "TEXT",    "NULL"),   # comma-separated mood tags
    ("culprit",           "TEXT",    "NULL"),   # *** SPOILER *** who did it
    ("locked_room_type",  "TEXT",    "NULL"),   # Dickson Carr taxonomy
]


def _migrate(conn: sqlite3.Connection) -> None:
    """Add any v2 columns that don't yet exist (non-destructive)."""
    cur = conn.execute("PRAGMA table_info(book_extended_metadata)")
    existing = {row[1] for row in cur.fetchall()}
    for col, typ, default in _V2_COLUMNS:
        if col not in existing:
            conn.execute(
                f"ALTER TABLE book_extended_metadata "
                f"ADD COLUMN {col} {typ} DEFAULT {default}"
            )
    conn.commit()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_get_db_path()))
    conn.row_factory = sqlite3.Row
    _ensure_tables(conn)
    return conn


# ── Extended metadata ─────────────────────────────────────────────────────────

# All fields stored in book_extended_metadata
_EXT_FIELDS = [
    "translator", "first_published", "original_language", "edition_notes",
    "read_status", "date_read", "mood", "culprit", "locked_room_type",
]


def get_extended_metadata(book_id: int, library_path: str) -> dict[str, Any]:
    """Return all extended metadata fields for a book."""
    conn = _connect()
    try:
        cols = ", ".join(_EXT_FIELDS)
        row = conn.execute(
            f"SELECT {cols} FROM book_extended_metadata "
            f"WHERE book_id=? AND library_path=?",
            (book_id, library_path),
        ).fetchone()
        if row:
            return {f: row[f] or "" for f in _EXT_FIELDS}
        return dict.fromkeys(_EXT_FIELDS, "")
    finally:
        conn.close()


def set_extended_metadata(
    book_id: int,
    library_path: str,
    **kwargs: str,
) -> None:
    """Upsert any subset of extended metadata fields.

    Pass only the fields you want to update as keyword arguments.
    Unknown keys are silently ignored.
    """
    fields = {k: v for k, v in kwargs.items() if k in _EXT_FIELDS}
    if not fields:
        return

    conn = _connect()
    try:
        row = conn.execute(
            "SELECT id FROM book_extended_metadata WHERE book_id=? AND library_path=?",
            (book_id, library_path),
        ).fetchone()

        if row:
            set_clause = ", ".join(f"{k}=?" for k in fields)
            conn.execute(
                f"UPDATE book_extended_metadata "
                f"SET {set_clause}, updated_at=CURRENT_TIMESTAMP "
                f"WHERE id=?",
                (*fields.values(), row["id"]),
            )
        else:
            cols = "book_id, library_path, " + ", ".join(fields)
            placeholders = ", ".join("?" * (2 + len(fields)))
            conn.execute(
                f"INSERT INTO book_extended_metadata ({cols}) VALUES ({placeholders})",
                (book_id, library_path, *fields.values()),
            )
        conn.commit()
    finally:
        conn.close()


# ── User comments ─────────────────────────────────────────────────────────────

def get_user_comment(book_id: int, library_path: str) -> str:
    """Get personal notes for a book."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT comment_text FROM user_comments WHERE book_id=? AND library_path=?",
            (book_id, library_path),
        ).fetchone()
        return (row["comment_text"] or "") if row else ""
    finally:
        conn.close()


def set_user_comment(book_id: int, library_path: str, comment_text: str) -> None:
    """Upsert personal notes."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT id FROM user_comments WHERE book_id=? AND library_path=?",
            (book_id, library_path),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE user_comments SET comment_text=?, updated_at=CURRENT_TIMESTAMP "
                "WHERE id=?",
                (comment_text, row["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO user_comments (book_id, library_path, comment_text) "
                "VALUES (?, ?, ?)",
                (book_id, library_path, comment_text),
            )
        conn.commit()
    finally:
        conn.close()
