"""
Utilities for Calibre Full-Text Search (FTS) database detection and querying.

Calibre uses a separate SQLite DB next to metadata.db: full-text-search.db.
Schema (FTS5 content tables):
- books_text: id, book, timestamp, format, searchable_text, ...
- books_fts: FTS5(content='books_text', content_rowid='id') -> rowid = books_text.id
- books_fts_stemmed: same with porter stemming

Queries must JOIN books_text WITH books_fts ON books_text.id = books_fts.rowid
and select books_text.book (the FTS virtual table has no 'book' column).
Calibre uses a custom tokenizer ('calibre remove_diacritics'); if unavailable
we fall back to LIKE on books_text.searchable_text.
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

FTS_DB_FILENAME = "full-text-search.db"
# Calibre FTS5 table names (content tables linked to books_text)
FTS_TABLE = "books_fts"
FTS_TABLE_STEMMED = "books_fts_stemmed"
BOOKS_TEXT_TABLE = "books_text"


def find_fts_database(metadata_db_path: Path) -> Path | None:
    """
    Find the FTS database next to a metadata.db file.

    Calibre uses "full-text-search.db" in the same directory as metadata.db.

    Args:
        metadata_db_path: Path to metadata.db

    Returns:
        Path to full-text-search.db if it exists, else None
    """
    if not metadata_db_path.exists():
        return None
    fts_path = metadata_db_path.parent / FTS_DB_FILENAME
    if fts_path.exists():
        logger.info("Found Calibre FTS database: %s", fts_path)
        return fts_path
    logger.debug("FTS database not found at %s", fts_path)
    return None


def _escape_fts5_query(raw: str) -> str:
    """
    Escape user text for FTS5 MATCH. FTS5: " for phrases, - for exclude,
    OR/AND, * prefix. Internal " must be doubled.
    """
    s = raw.strip()
    if not s:
        return s
    # If already looks like FTS syntax (quotes, OR, AND, *), use as-is
    if '"' in s or s.upper().startswith("OR ") or s.upper().startswith("AND "):
        return s.replace('"', '""')
    words = s.split()
    if len(words) > 1:
        return '"' + s.replace('"', '""') + '"'
    return s


def _query_via_fts(
    conn: sqlite3.Connection,
    fts_table: str,
    fts_query: str,
    limit: int,
    offset: int,
    include_snippets: bool,
    snippet_size: int = 64,
) -> tuple[list[int], int, dict[int, str]]:
    """
    Run FTS using Calibre schema: JOIN books_text WITH fts_table ON id = rowid.
    Returns (book_ids, total_count, book_id -> snippet).
    """
    cursor = conn.cursor()
    # Total count (distinct books matching)
    cursor.execute(
        f"""
        SELECT COUNT(DISTINCT books_text.book) FROM books_text
        JOIN {fts_table} ON books_text.id = {fts_table}.rowid
        WHERE {fts_table} MATCH ?
        """,
        (fts_query,),
    )
    total = cursor.fetchone()[0] or 0

    if include_snippets:
        # FTS5 snippet(fts_table, column_index, start, end, ellipsis, max_tokens)
        # Single content column -> index 0
        sel = f"""
            books_text.book,
            snippet({fts_table}, 0, '<mark>', '</mark>', '...', ?) AS snippet_text
        """
    else:
        sel = "books_text.book"

    q = f"""
        SELECT {sel}
        FROM books_text
        JOIN {fts_table} ON books_text.id = {fts_table}.rowid
        WHERE {fts_table} MATCH ?
        ORDER BY {fts_table}.rank
        LIMIT ? OFFSET ?
    """
    args = (snippet_size, fts_query, limit, offset) if include_snippets else (fts_query, limit, offset)
    cursor.execute(q, args)
    rows = cursor.fetchall()

    book_ids = [r[0] for r in rows]
    snippets = {}
    if include_snippets and rows:
        snippets = {r[0]: (r[1] or "").strip() for r in rows if r[1] and (r[1] or "").strip()}
    return book_ids, total, snippets


def _query_via_like(
    conn: sqlite3.Connection,
    like_pattern: str,
    search_text: str,
    limit: int,
    offset: int,
    include_snippets: bool,
) -> tuple[list[int], int, dict[int, str]]:
    """
    Fallback: search books_text.searchable_text with LIKE (no FTS5 tokenizer).
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(DISTINCT book) FROM books_text
        WHERE searchable_text LIKE ?
        """,
        (like_pattern,),
    )
    total = cursor.fetchone()[0] or 0

    if include_snippets:
        # Crude snippet: 50 chars before match, 150 total
        cursor.execute(
            """
            SELECT book,
                   substr(searchable_text,
                          max(1, instr(lower(searchable_text), lower(?)) - 50),
                          150) AS snippet_text
            FROM books_text
            WHERE searchable_text LIKE ?
            LIMIT ? OFFSET ?
            """,
            (search_text, like_pattern, limit, offset),
        )
    else:
        cursor.execute(
            """
            SELECT DISTINCT book FROM books_text
            WHERE searchable_text LIKE ?
            LIMIT ? OFFSET ?
            """,
            (like_pattern, limit, offset),
        )
    rows = cursor.fetchall()
    book_ids = [r[0] for r in rows]
    snippets = {}
    if include_snippets and rows and len(rows[0]) > 1:
        snippets = {r[0]: (r[1] or "").strip() for r in rows if r[1] and (r[1] or "").strip()}
    return book_ids, total, snippets


def query_fts(
    fts_db_path: Path,
    search_text: str,
    limit: int = 50,
    offset: int = 0,
    use_stemming: bool = False,
    include_snippets: bool = True,
    snippet_size: int = 64,
) -> tuple[list[int], int, dict[int, str]]:
    """
    Search Calibre FTS database. Uses FTS5 when available (books_fts or
    books_fts_stemmed with JOIN on books_text); falls back to LIKE on
    books_text.searchable_text if the custom tokenizer is not available.

    Args:
        fts_db_path: Path to full-text-search.db
        search_text: Query string (words or phrase)
        limit: Max results
        offset: Pagination offset
        use_stemming: Use stemmed index (books_fts_stemmed) when trying FTS
        include_snippets: Include snippet per book
        snippet_size: Max tokens in snippet (FTS path)

    Returns:
        (list of book IDs, total match count, dict book_id -> snippet text)
    """
    if not fts_db_path.exists():
        logger.warning("FTS database does not exist: %s", fts_db_path)
        return [], 0, {}

    search_clean = search_text.strip()
    if not search_clean:
        return [], 0, {}

    like_pattern = f"%{search_clean}%"
    fts_query = _escape_fts5_query(search_clean)
    fts_table = FTS_TABLE_STEMMED if use_stemming else FTS_TABLE

    try:
        conn = sqlite3.connect(str(fts_db_path))
        try:
            # Ensure tables exist
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (BOOKS_TEXT_TABLE,),
            )
            if not cursor.fetchone():
                logger.warning("Table %s not found in %s", BOOKS_TEXT_TABLE, fts_db_path)
                return [], 0, {}

            # Try FTS5 path (JOIN books_text with virtual table)
            try:
                book_ids, total, snippets = _query_via_fts(
                    conn, fts_table, fts_query, limit, offset, include_snippets, snippet_size
                )
                logger.info(
                    "FTS query (virtual table %s) returned %s book IDs, total %s",
                    fts_table,
                    len(book_ids),
                    total,
                )
                return book_ids, total, snippets
            except sqlite3.OperationalError as e:
                # Custom tokenizer or FTS5 not available
                logger.debug(
                    "FTS virtual table query failed (%s), falling back to content table",
                    e,
                )

            # Fallback: LIKE on books_text
            book_ids, total, snippets = _query_via_like(
                conn, like_pattern, search_clean, limit, offset, include_snippets
            )
            logger.info(
                "FTS query (content table LIKE) returned %s book IDs, total %s",
                len(book_ids),
                total,
            )
            return book_ids, total, snippets
        finally:
            conn.close()
    except sqlite3.Error as e:
        logger.error("Error querying FTS database: %s", e)
        return [], 0, {}
