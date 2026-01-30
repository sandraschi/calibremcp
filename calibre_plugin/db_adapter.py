"""
Direct SQLite access to calibre_mcp_data.db.
Matches CalibreMCP schema - no MCP process required.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any


def _get_db_path() -> Path:
    from calibre_plugins.calibre_mcp_integration.config import get_mcp_user_data_dir

    data_dir = Path(get_mcp_user_data_dir())
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        data_dir = Path.cwd() / ".calibre-mcp-data"
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "calibre_mcp_data.db"


def _ensure_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS book_extended_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            library_path TEXT NOT NULL,
            translator TEXT,
            first_published TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS user_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            library_path TEXT NOT NULL,
            comment_text TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT
        );
    """)


def get_extended_metadata(book_id: int, library_path: str) -> Dict[str, Any]:
    """Get translator and first_published for a book."""
    path = _get_db_path()
    conn = sqlite3.connect(str(path))
    try:
        _ensure_tables(conn)
        cur = conn.execute(
            "SELECT translator, first_published FROM book_extended_metadata "
            "WHERE book_id=? AND library_path=?",
            (book_id, library_path),
        )
        row = cur.fetchone()
        if row:
            return {"translator": row[0] or "", "first_published": row[1] or ""}
        return {"translator": "", "first_published": ""}
    finally:
        conn.close()


def set_extended_metadata(
    book_id: int,
    library_path: str,
    translator: str = "",
    first_published: str = "",
) -> None:
    """Upsert extended metadata."""
    path = _get_db_path()
    conn = sqlite3.connect(str(path))
    try:
        _ensure_tables(conn)
        cur = conn.execute(
            "SELECT id FROM book_extended_metadata WHERE book_id=? AND library_path=?",
            (book_id, library_path),
        )
        row = cur.fetchone()
        if row:
            conn.execute(
                "UPDATE book_extended_metadata SET translator=?, first_published=?, "
                "updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (translator, first_published, row[0]),
            )
        else:
            conn.execute(
                "INSERT INTO book_extended_metadata (book_id, library_path, translator, first_published) "
                "VALUES (?, ?, ?, ?)",
                (book_id, library_path, translator, first_published),
            )
        conn.commit()
    finally:
        conn.close()


def get_user_comment(book_id: int, library_path: str) -> str:
    """Get user comment for a book."""
    path = _get_db_path()
    conn = sqlite3.connect(str(path))
    try:
        _ensure_tables(conn)
        cur = conn.execute(
            "SELECT comment_text FROM user_comments WHERE book_id=? AND library_path=?",
            (book_id, library_path),
        )
        row = cur.fetchone()
        return (row[0] or "") if row else ""
    finally:
        conn.close()


def set_user_comment(book_id: int, library_path: str, comment_text: str) -> None:
    """Upsert user comment."""
    path = _get_db_path()
    conn = sqlite3.connect(str(path))
    try:
        _ensure_tables(conn)
        cur = conn.execute(
            "SELECT id FROM user_comments WHERE book_id=? AND library_path=?",
            (book_id, library_path),
        )
        row = cur.fetchone()
        if row:
            conn.execute(
                "UPDATE user_comments SET comment_text=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (comment_text, row[0]),
            )
        else:
            conn.execute(
                "INSERT INTO user_comments (book_id, library_path, comment_text) VALUES (?, ?, ?)",
                (book_id, library_path, comment_text),
            )
        conn.commit()
    finally:
        conn.close()
