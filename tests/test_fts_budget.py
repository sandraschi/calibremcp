"""FTS time-budget tests: runaway content queries abort instead of hanging the call."""

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calibre_mcp.utils.fts_utils import _budgeted_connection, query_fts


def _small_fts_db(path: Path) -> Path:
    pytest.importorskip("sqlite3")
    db = path / "full-text-search.db"
    conn = sqlite3.connect(str(db))
    try:
        conn.execute("CREATE TABLE books_text (id INTEGER PRIMARY KEY, book INTEGER, searchable_text TEXT)")
        conn.execute(
            "INSERT INTO books_text (book, searchable_text) VALUES (1, 'Dickson Carr wrote locked room mysteries')"
        )
        conn.execute("INSERT INTO books_text (book, searchable_text) VALUES (2, 'something entirely different')")
        try:
            conn.execute(
                "CREATE VIRTUAL TABLE books_fts USING fts5(searchable_text, content='books_text', content_rowid='id')"
            )
            conn.execute("INSERT INTO books_fts(rowid, searchable_text) SELECT id, searchable_text FROM books_text")
        except sqlite3.OperationalError:
            pytest.skip("FTS5 not available in this sqlite build")
        conn.commit()
    finally:
        conn.close()
    return db


def test_fts_normal_query_under_budget(tmp_path):
    from calibre_mcp.utils.fts_utils import BOOKS_TEXT_TABLE

    db = _small_fts_db(tmp_path)
    # sanity: our fixture uses the expected table names
    assert BOOKS_TEXT_TABLE == "books_text"
    ids, total, snips = query_fts(db, "Dickson", limit=20, offset=0, include_snippets=True)
    assert total >= 1
    assert 1 in ids


def test_budget_aborts_runaway_query(tmp_path):
    db = _small_fts_db(tmp_path)
    conn = _budgeted_connection(db, budget_s=0.0001)
    try:
        with pytest.raises(sqlite3.OperationalError):
            # 10M-row recursive scan: guaranteed to outlive a ~0ms budget
            conn.execute(
                "WITH RECURSIVE cnt(x) AS "
                "(SELECT 1 UNION ALL SELECT x+1 FROM cnt LIMIT 10000000) "
                "SELECT sum(x) FROM cnt"
            ).fetchall()
    finally:
        conn.close()
