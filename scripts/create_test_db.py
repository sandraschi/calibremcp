"""
Create a minimal test Calibre database for testing.

This creates a small, reproducible test library with a few sample books
that can be committed to GitHub and used in CI/CD workflows.
"""

import sqlite3
from pathlib import Path

TEST_LIBRARY_DIR = Path(__file__).parent.parent / "tests" / "fixtures" / "test_library"
TEST_DB_PATH = TEST_LIBRARY_DIR / "metadata.db"


def create_test_database():
    """Create a minimal test Calibre database with sample books."""
    # Create directory
    TEST_LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    # Remove existing database
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    conn = sqlite3.connect(str(TEST_DB_PATH))
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Create minimal schema (only tables we actually use)
    print("Creating database schema...")

    # Books table
    cursor.execute("""
        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            sort TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            pubdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            series_index REAL DEFAULT 1.0,
            author_sort TEXT,
            isbn TEXT,
            lccn TEXT,
            path TEXT NOT NULL,
            flags INTEGER DEFAULT 1,
            uuid TEXT,
            has_cover INTEGER DEFAULT 0,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Authors table
    cursor.execute("""
        CREATE TABLE authors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            sort TEXT,
            link TEXT DEFAULT ''
        )
    """)

    # Tags table
    cursor.execute("""
        CREATE TABLE tags (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # Series table
    cursor.execute("""
        CREATE TABLE series (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            sort TEXT
        )
    """)

    # Comments table
    cursor.execute("""
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY,
            book INTEGER NOT NULL,
            text TEXT NOT NULL DEFAULT ''
        )
    """)

    # Data table (book formats)
    cursor.execute("""
        CREATE TABLE data (
            id INTEGER PRIMARY KEY,
            book INTEGER NOT NULL,
            format TEXT NOT NULL,
            uncompressed_size INTEGER DEFAULT 0,
            name TEXT DEFAULT '',
            UNIQUE(book, format)
        )
    """)

    # Link tables
    cursor.execute("""
        CREATE TABLE books_authors_link (
            id INTEGER PRIMARY KEY,
            book INTEGER NOT NULL,
            author INTEGER NOT NULL,
            UNIQUE(book, author)
        )
    """)

    cursor.execute("""
        CREATE TABLE books_tags_link (
            id INTEGER PRIMARY KEY,
            book INTEGER NOT NULL,
            tag INTEGER NOT NULL,
            UNIQUE(book, tag)
        )
    """)

    cursor.execute("""
        CREATE TABLE books_series_link (
            id INTEGER PRIMARY KEY,
            book INTEGER NOT NULL,
            series INTEGER NOT NULL,
            UNIQUE(book, series)
        )
    """)

    # Foreign keys
    cursor.execute("""
        CREATE INDEX idx_books_authors_book ON books_authors_link(book)
    """)
    cursor.execute("""
        CREATE INDEX idx_books_authors_author ON books_authors_link(author)
    """)
    cursor.execute("""
        CREATE INDEX idx_books_tags_book ON books_tags_link(book)
    """)
    cursor.execute("""
        CREATE INDEX idx_books_tags_tag ON books_tags_link(tag)
    """)
    cursor.execute("""
        CREATE INDEX idx_books_series_book ON books_series_link(book)
    """)
    cursor.execute("""
        CREATE INDEX idx_data_book ON data(book)
    """)
    cursor.execute("""
        CREATE INDEX idx_comments_book ON comments(book)
    """)

    print("Inserting test data...")

    # Insert sample authors
    authors = [
        (1, "Arthur Conan Doyle", "Doyle, Arthur Conan"),
        (2, "Jane Austen", "Austen, Jane"),
        (3, "Mark Twain", "Twain, Mark"),
    ]
    cursor.executemany("INSERT INTO authors (id, name, sort) VALUES (?, ?, ?)", authors)

    # Insert sample tags
    tags = [
        (1, "mystery"),
        (2, "detective"),
        (3, "classic"),
        (4, "romance"),
        (5, "adventure"),
    ]
    cursor.executemany("INSERT INTO tags (id, name) VALUES (?, ?)", tags)

    # Insert sample series
    series = [
        (1, "Sherlock Holmes", "Holmes, Sherlock"),
    ]
    cursor.executemany("INSERT INTO series (id, name, sort) VALUES (?, ?, ?)", series)

    # Insert sample books
    # Format: (id, title, sort, path, flags, uuid, has_cover, series_index, author_sort, isbn, lccn)
    books = [
        (
            1,
            "A Study in Scarlet",
            "Study in Scarlet, A",
            "Arthur Conan Doyle/A Study in Scarlet (1)",
            1,
            "test-uuid-1",
            0,
            1.0,
            "Doyle, Arthur Conan",
            None,
            None,
        ),
        (
            2,
            "The Sign of the Four",
            "Sign of the Four, The",
            "Arthur Conan Doyle/The Sign of the Four (2)",
            1,
            "test-uuid-2",
            0,
            2.0,
            "Doyle, Arthur Conan",
            None,
            None,
        ),
        (
            3,
            "Pride and Prejudice",
            "Pride and Prejudice",
            "Jane Austen/Pride and Prejudice (3)",
            1,
            "test-uuid-3",
            0,
            1.0,
            "Austen, Jane",
            None,
            None,
        ),
        (
            4,
            "The Adventures of Tom Sawyer",
            "Adventures of Tom Sawyer, The",
            "Mark Twain/The Adventures of Tom Sawyer (4)",
            1,
            "test-uuid-4",
            0,
            1.0,
            "Twain, Mark",
            None,
            None,
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO books (id, title, sort, path, flags, uuid, has_cover, pubdate, series_index, author_sort, isbn, lccn)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?)
    """,
        books,
    )

    # Link books to authors
    # Format: (id, book, author)
    book_authors = [
        (1, 1, 1),  # A Study in Scarlet -> Arthur Conan Doyle
        (2, 2, 1),  # The Sign of the Four -> Arthur Conan Doyle
        (3, 3, 2),  # Pride and Prejudice -> Jane Austen
        (4, 4, 3),  # Tom Sawyer -> Mark Twain
    ]
    cursor.executemany(
        "INSERT INTO books_authors_link (id, book, author) VALUES (?, ?, ?)", book_authors
    )

    # Link books to tags
    # Format: (id, book, tag)
    book_tags = [
        (1, 1, 1),  # A Study in Scarlet -> mystery
        (2, 1, 2),  # A Study in Scarlet -> detective
        (3, 1, 3),  # A Study in Scarlet -> classic
        (4, 2, 1),  # The Sign of the Four -> mystery
        (5, 2, 2),  # The Sign of the Four -> detective
        (6, 2, 3),  # The Sign of the Four -> classic
        (7, 3, 3),  # Pride and Prejudice -> classic
        (8, 3, 4),  # Pride and Prejudice -> romance
        (9, 4, 3),  # Tom Sawyer -> classic
        (10, 4, 5),  # Tom Sawyer -> adventure
    ]
    cursor.executemany("INSERT INTO books_tags_link (id, book, tag) VALUES (?, ?, ?)", book_tags)

    # Link books to series
    book_series = [
        (1, 1, 1),  # A Study in Scarlet -> Sherlock Holmes
        (2, 2, 1),  # The Sign of the Four -> Sherlock Holmes
    ]
    cursor.executemany(
        "INSERT INTO books_series_link (id, book, series) VALUES (?, ?, ?)", book_series
    )

    # Insert comments
    comments = [
        (1, 1, "The first Sherlock Holmes novel, introducing the detective and Dr. Watson."),
        (2, 2, "The second Sherlock Holmes novel."),
        (3, 3, "A romantic novel of manners written by Jane Austen."),
        (4, 4, "A novel about a young boy growing up along the Mississippi River."),
    ]
    cursor.executemany("INSERT INTO comments (id, book, text) VALUES (?, ?, ?)", comments)

    # Insert format data (will match actual test files created by create_test_files.py)
    format_data = [
        (1, 1, "EPUB", 2456, ""),  # Minimal EPUB ~2KB
        (2, 1, "PDF", 656, ""),  # Minimal PDF ~0.6KB
        (3, 2, "EPUB", 2456, ""),  # Minimal EPUB ~2KB
        (4, 3, "EPUB", 2456, ""),  # Minimal EPUB ~2KB
        (5, 4, "EPUB", 2456, ""),  # Minimal EPUB ~2KB
        (6, 4, "CBZ", 512, ""),  # Minimal CBZ ~0.5KB (comic format)
    ]
    cursor.executemany(
        """
        INSERT INTO data (id, book, format, uncompressed_size, name)
        VALUES (?, ?, ?, ?, ?)
    """,
        format_data,
    )

    conn.commit()
    conn.close()

    print(f"\n[OK] Test database created: {TEST_DB_PATH}")
    print("  - 4 books")
    print("  - 3 authors")
    print("  - 5 tags")
    print("  - 1 series")
    print(f"  - Size: {TEST_DB_PATH.stat().st_size / 1024:.1f} KB")

    print(f"\n[OK] Test library structure created: {TEST_LIBRARY_DIR}")
    print(
        "\n[NOTE] Run 'python scripts/create_test_files.py' to create actual book files (EPUB, PDF, CBZ)"
    )
    print("   The database is ready, but book files need to be created separately.")


if __name__ == "__main__":
    create_test_database()
