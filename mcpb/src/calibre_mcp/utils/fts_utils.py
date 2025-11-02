"""
Utilities for Calibre Full-Text Search (FTS) database detection and querying.

Calibre creates FTS databases in the same directory as metadata.db when FTS indexing
is enabled. The database is always named:
- full-text-search.db
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

# Calibre FTS database filename (always named this)
FTS_DB_FILENAME = "full-text-search.db"


def find_fts_database(metadata_db_path: Path) -> Optional[Path]:
    """
    Find the FTS database associated with a metadata.db file.

    Calibre always names the FTS database "full-text-search.db" in the same directory
    as metadata.db.

    Args:
        metadata_db_path: Path to metadata.db file

    Returns:
        Path to FTS database if found, None otherwise
    """
    if not metadata_db_path.exists():
        return None

    db_dir = metadata_db_path.parent

    # Calibre always uses this exact filename
    fts_path = db_dir / FTS_DB_FILENAME

    if fts_path.exists():
        logger.info(f"Found Calibre FTS database: {fts_path}")
        return fts_path

    logger.debug(f"FTS database not found at {fts_path}")
    return None


def get_fts_table_name(fts_db_path: Path) -> Optional[str]:
    """
    Get the name of the FTS table in the FTS database.

    Args:
        fts_db_path: Path to FTS database

    Returns:
        Name of FTS table if found, None otherwise
    """
    try:
        conn = sqlite3.connect(str(fts_db_path))
        cursor = conn.cursor()

        # Check for FTS5 tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND sql LIKE '%USING fts5%'
        """)
        fts5_tables = cursor.fetchall()

        if fts5_tables:
            conn.close()
            return fts5_tables[0][0]  # Return first FTS5 table

        # Check for FTS4 tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND sql LIKE '%USING fts4%'
        """)
        fts4_tables = cursor.fetchall()

        conn.close()

        if fts4_tables:
            return fts4_tables[0][0]  # Return first FTS4 table

    except sqlite3.Error as e:
        logger.error(f"Error getting FTS table name: {e}")

    return None


def query_fts(
    fts_db_path: Path,
    search_text: str,
    limit: int = 50,
    offset: int = 0,
    min_score: Optional[float] = None,
) -> Tuple[List[int], int]:
    """
    Query the FTS database for book IDs matching the search text.

    Args:
        fts_db_path: Path to FTS database
        search_text: Text to search for
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        Tuple of (list of book IDs, total count)
    """
    fts_table = get_fts_table_name(fts_db_path)
    if not fts_table:
        logger.warning(f"No FTS table found in {fts_db_path}")
        return [], 0

    try:
        conn = sqlite3.connect(str(fts_db_path))
        cursor = conn.cursor()

        # Calibre FTS typically stores book metadata in columns like:
        # title, authors, tags, series, comments, etc.
        # The exact schema varies, but we try common patterns

        # Build FTS query - escape special characters and use proper syntax
        # For FTS5: simple text matching
        # For phrase search: wrap in quotes for exact phrase matching

        # Clean and prepare the search text
        search_text_clean = search_text.strip()

        # Check if it's a phrase (multiple words) - quote for exact phrase matching
        words = search_text_clean.split()
        if len(words) > 1:
            # Quote phrases for exact phrase matching in FTS
            # This ensures "it was the worst of times" matches the exact phrase
            fts_query = f'"{search_text_clean}"'
        else:
            # Single word - use as-is (FTS will handle word matching)
            fts_query = search_text_clean

        # Try to get total count first
        try:
            count_query = f"""
                SELECT COUNT(*) FROM {fts_table}
                WHERE {fts_table} MATCH ?
            """
            cursor.execute(count_query, (fts_query,))
            total = cursor.fetchone()[0] or 0
        except sqlite3.Error:
            # If count fails, we'll estimate from results
            total = 0

        # Query for book IDs
        # Calibre FTS typically has a 'book' or 'id' column linking to books table
        # We need to get the book IDs from the FTS results

        # Try common column names for book ID
        book_id_columns = ["book", "id", "book_id", "rowid"]

        # First, check what columns exist
        cursor.execute(f"PRAGMA table_info({fts_table})")
        columns = [row[1] for row in cursor.fetchall()]

        # Find the book ID column
        book_id_col = None
        for col in book_id_columns:
            if col in columns:
                book_id_col = col
                break

        if not book_id_col:
            # If no explicit book ID column, use rowid
            book_id_col = "rowid"

        # Query FTS table
        query = f"""
            SELECT {book_id_col} FROM {fts_table}
            WHERE {fts_table} MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        """

        cursor.execute(query, (fts_query, limit, offset))
        results = cursor.fetchall()
        book_ids = [row[0] for row in results]

        # If total wasn't available, use an estimate
        if total == 0 and len(book_ids) > 0:
            total = len(book_ids) + offset  # Estimate

        conn.close()

        logger.info(f"FTS query returned {len(book_ids)} book IDs from {total} total matches")
        return book_ids, total

    except sqlite3.Error as e:
        logger.error(f"Error querying FTS database: {e}")
        return [], 0
