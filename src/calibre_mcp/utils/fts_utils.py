"""
Utilities for Calibre Full-Text Search (FTS) database detection and querying.

Calibre creates FTS databases in the same directory as metadata.db when FTS indexing
is enabled. The database is always named:
- full-text-search.db
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Tuple, Dict

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
    include_snippets: bool = True,
) -> Tuple[List[int], int, Dict[int, str]]:
    """
    Query the FTS database for book IDs matching the search text.

    This function attempts to use Calibre's FTS virtual table first, but falls back
    to direct queries on the underlying `books_text` content table when the custom
    tokenizer is not available.

    Args:
        fts_db_path: Path to FTS database
        search_text: Text to search for (searches actual book content)
        limit: Maximum number of results
        offset: Number of results to skip
        include_snippets: If True, extract text snippets showing where matches occur

    Returns:
        Tuple of (list of book IDs, total count, dict mapping book_id to snippet)
    """
    fts_table = get_fts_table_name(fts_db_path)
    if not fts_table:
        logger.warning(f"No FTS table found in {fts_db_path}")
        return [], 0, {}

    try:
        conn = sqlite3.connect(str(fts_db_path))
        cursor = conn.cursor()

        # Clean and prepare the search text
        search_text_clean = search_text.strip()

        # First, try using the FTS virtual table (requires custom tokenizer)
        try:
            # Build FTS query - escape special characters and use proper syntax
            # For phrase search: wrap in quotes for exact phrase matching
            words = search_text_clean.split()
            if len(words) > 1:
                # Quote phrases for exact phrase matching in FTS
                fts_query = f'"{search_text_clean}"'
            else:
                # Single word - use as-is
                fts_query = search_text_clean

            # Try to query FTS table
            cursor.execute(f"PRAGMA table_info({fts_table})")
            columns = [row[1] for row in cursor.fetchall()]

            # Find the book ID column
            book_id_columns = ["book", "id", "book_id", "rowid"]
            book_id_col = None
            for col in book_id_columns:
                if col in columns:
                    book_id_col = col
                    break

            if not book_id_col:
                book_id_col = "rowid"

            # Try to get total count
            try:
                count_query = f"""
                    SELECT COUNT(DISTINCT {book_id_col}) FROM {fts_table}
                    WHERE {fts_table} MATCH ?
                """
                cursor.execute(count_query, (fts_query,))
                total = cursor.fetchone()[0] or 0
            except sqlite3.Error:
                total = 0

            # Query FTS table with snippet extraction if requested
            snippets = {}
            if include_snippets:
                # Try to extract snippets using FTS5 snippet() function
                # snippet(table, column_index, start_marker, end_marker, ellipsis, max_tokens)
                # For FTS5, column index 0 is typically rowid, 1+ are content columns
                # Find the searchable text column index (usually index 1 or 2)
                try:
                    # Determine text column index - usually the last column or column 1
                    text_col_index = len(columns) - 1 if len(columns) > 1 else 1
                    # Try column 1 first (most common), fall back to last column
                    for test_idx in [1, text_col_index]:
                        try:
                            query_with_snippets = f"""
                                SELECT DISTINCT {book_id_col}, 
                                       snippet({fts_table}, {test_idx}, '<mark>', '</mark>', '...', 64) as snippet_text
                                FROM {fts_table}
                                WHERE {fts_table} MATCH ?
                                ORDER BY rank
                                LIMIT ? OFFSET ?
                            """
                            cursor.execute(query_with_snippets, (fts_query, limit, offset))
                            results = cursor.fetchall()
                            book_ids = [row[0] for row in results]
                            snippets = {row[0]: row[1] for row in results if row[1] and row[1].strip()}
                            if snippets:
                                break  # Success, use this column index
                        except sqlite3.Error:
                            continue  # Try next column index
                    
                    # If snippet extraction failed, fall back to simple query
                    if not snippets:
                        logger.debug("Snippet extraction failed for all columns, using simple query")
                        query = f"""
                            SELECT DISTINCT {book_id_col} FROM {fts_table}
                            WHERE {fts_table} MATCH ?
                            ORDER BY rank
                            LIMIT ? OFFSET ?
                        """
                        cursor.execute(query, (fts_query, limit, offset))
                        results = cursor.fetchall()
                        book_ids = [row[0] for row in results]
                except Exception as snippet_error:
                    # Snippet extraction failed completely, fall back to simple query
                    logger.debug(f"Snippet extraction failed: {snippet_error}, using simple query")
                    query = f"""
                        SELECT DISTINCT {book_id_col} FROM {fts_table}
                        WHERE {fts_table} MATCH ?
                        ORDER BY rank
                        LIMIT ? OFFSET ?
                    """
                    cursor.execute(query, (fts_query, limit, offset))
                    results = cursor.fetchall()
                    book_ids = [row[0] for row in results]
            else:
                # Simple query without snippets
                query = f"""
                    SELECT DISTINCT {book_id_col} FROM {fts_table}
                    WHERE {fts_table} MATCH ?
                    ORDER BY rank
                    LIMIT ? OFFSET ?
                """
                cursor.execute(query, (fts_query, limit, offset))
                results = cursor.fetchall()
                book_ids = [row[0] for row in results]

            if book_ids:
                conn.close()
                logger.info(
                    f"FTS query (via virtual table) returned {len(book_ids)} book IDs from {total} total matches, {len(snippets)} snippets"
                )
                return book_ids, total, snippets

        except sqlite3.Error as fts_error:
            # FTS virtual table query failed (likely custom tokenizer not available)
            logger.debug(
                f"FTS virtual table query failed: {fts_error}, falling back to content table"
            )

        # Fallback: Query the underlying books_text content table directly
        # This works without the custom tokenizer, but is slower
        logger.info("Using fallback: querying books_text content table directly")

        # Build LIKE query for phrase search
        # For phrases, search for the exact phrase
        # For single words, search for the word
        like_pattern = f"%{search_text_clean}%"

        # Get total count from content table
        try:
            count_query = """
                SELECT COUNT(DISTINCT book) FROM books_text
                WHERE searchable_text LIKE ?
            """
            cursor.execute(count_query, (like_pattern,))
            total = cursor.fetchone()[0] or 0
        except sqlite3.Error:
            total = 0

        # Query content table for book IDs with snippets if requested
        snippets = {}
        if include_snippets:
            # Extract snippets from the content table
            # Find position of search term and extract surrounding text
            query = """
                SELECT DISTINCT book, 
                       CASE 
                           WHEN instr(lower(searchable_text), lower(?)) > 0 THEN
                               substr(searchable_text, 
                                      max(1, instr(lower(searchable_text), lower(?)) - 50),
                                      150)
                           ELSE substr(searchable_text, 1, 150)
                       END as snippet_text
                FROM books_text
                WHERE searchable_text LIKE ?
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (search_text_clean, search_text_clean, like_pattern, limit, offset))
            results = cursor.fetchall()
            book_ids = [row[0] for row in results]
            snippets = {row[0]: row[1] for row in results if row[1] and row[1].strip()}
        else:
            query = """
                SELECT DISTINCT book FROM books_text
                WHERE searchable_text LIKE ?
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (like_pattern, limit, offset))
            results = cursor.fetchall()
            book_ids = [row[0] for row in results]

        conn.close()

        logger.info(
            f"FTS query (via content table) returned {len(book_ids)} book IDs from {total} total matches, {len(snippets)} snippets"
        )
        return book_ids, total, snippets

    except sqlite3.Error as e:
        logger.error(f"Error querying FTS database: {e}")
        return [], 0, {}
