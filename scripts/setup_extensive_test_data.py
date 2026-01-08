"""
Create extensive test data for comprehensive testing.

This script extends the basic test database with more diverse data
to test edge cases, complex queries, and various scenarios.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

TEST_LIBRARY_DIR = Path(__file__).parent.parent / "tests" / "fixtures" / "test_library"
TEST_DB_PATH = TEST_LIBRARY_DIR / "metadata.db"


def create_extensive_test_data():
    """Create extensive test data for comprehensive testing."""
    if not TEST_DB_PATH.exists():
        print(f"ERROR: Test database not found at {TEST_DB_PATH}")
        print("Run 'python scripts/create_test_db.py' first to create the base database.")
        return
    
    conn = sqlite3.connect(str(TEST_DB_PATH))
    cursor = conn.cursor()
    
    print("Adding extensive test data...")
    
    # Add more authors
    additional_authors = [
        (5, "Agatha Christie", "Christie, Agatha"),
        (6, "Stephen King", "King, Stephen"),
        (7, "J.K. Rowling", "Rowling, J.K."),
        (8, "George R.R. Martin", "Martin, George R.R."),
        (9, "Isaac Asimov", "Asimov, Isaac"),
        (10, "Ray Bradbury", "Bradbury, Ray"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO authors (id, name, sort) VALUES (?, ?, ?)",
        additional_authors
    )
    print(f"  Added {len(additional_authors)} authors")
    
    # Add more tags
    additional_tags = [
        (6, "horror"),
        (7, "fantasy"),
        (8, "sci-fi"),
        (9, "thriller"),
        (10, "young-adult"),
        (11, "non-fiction"),
        (12, "biography"),
        (13, "poetry"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO tags (id, name) VALUES (?, ?)",
        additional_tags
    )
    print(f"  Added {len(additional_tags)} tags")
    
    # Add more series
    additional_series = [
        (2, "Harry Potter", "Potter, Harry"),
        (3, "A Song of Ice and Fire", "Song of Ice and Fire, A"),
        (4, "Foundation", "Foundation"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO series (id, name, sort) VALUES (?, ?, ?)",
        additional_series
    )
    print(f"  Added {len(additional_series)} series")
    
    # Add more books with diverse metadata
    base_date = datetime.now() - timedelta(days=365)
    additional_books = [
        (
            5, "Murder on the Orient Express", "Murder on the Orient Express",
            "Agatha Christie/Murder on the Orient Express (5)",
            1, "test-uuid-5", 1, 1.0, "Christie, Agatha",
            "9780062693662", None, base_date.strftime("%Y-%m-%d")
        ),
        (
            6, "The Shining", "Shining, The",
            "Stephen King/The Shining (6)",
            1, "test-uuid-6", 1, 1.0, "King, Stephen",
            "9780307743657", None, (base_date + timedelta(days=30)).strftime("%Y-%m-%d")
        ),
        (
            7, "Harry Potter and the Philosopher's Stone", "Harry Potter and the Philosopher's Stone",
            "J.K. Rowling/Harry Potter and the Philosopher's Stone (7)",
            1, "test-uuid-7", 1, 1.0, "Rowling, J.K.",
            "9780747532699", None, (base_date + timedelta(days=60)).strftime("%Y-%m-%d")
        ),
        (
            8, "A Game of Thrones", "Game of Thrones, A",
            "George R.R. Martin/A Game of Thrones (8)",
            1, "test-uuid-8", 1, 1.0, "Martin, George R.R.",
            "9780553381689", None, (base_date + timedelta(days=90)).strftime("%Y-%m-%d")
        ),
        (
            9, "Foundation", "Foundation",
            "Isaac Asimov/Foundation (9)",
            1, "test-uuid-9", 0, 1.0, "Asimov, Isaac",
            "9780553293357", None, (base_date + timedelta(days=120)).strftime("%Y-%m-%d")
        ),
        (
            10, "Fahrenheit 451", "Fahrenheit 451",
            "Ray Bradbury/Fahrenheit 451 (10)",
            1, "test-uuid-10", 0, 1.0, "Bradbury, Ray",
            "9781451673319", None, (base_date + timedelta(days=150)).strftime("%Y-%m-%d")
        ),
        (
            11, "And Then There Were None", "And Then There Were None",
            "Agatha Christie/And Then There Were None (11)",
            1, "test-uuid-11", 1, 1.0, "Christie, Agatha",
            None, None, (base_date + timedelta(days=180)).strftime("%Y-%m-%d")
        ),
        (
            12, "The Stand", "Stand, The",
            "Stephen King/The Stand (12)",
            1, "test-uuid-12", 1, 1.0, "King, Stephen",
            "9780307743688", None, (base_date + timedelta(days=210)).strftime("%Y-%m-%d")
        ),
    ]
    cursor.executemany(
        """
        INSERT OR IGNORE INTO books 
        (id, title, sort, path, flags, uuid, has_cover, pubdate, series_index, author_sort, isbn, lccn)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        additional_books
    )
    print(f"  Added {len(additional_books)} books")
    
    # Link books to authors
    book_authors = [
        (5, 5, 5),  # Murder on the Orient Express -> Agatha Christie
        (6, 6, 6),  # The Shining -> Stephen King
        (7, 7, 7),  # Harry Potter -> J.K. Rowling
        (8, 8, 8),  # A Game of Thrones -> George R.R. Martin
        (9, 9, 9),  # Foundation -> Isaac Asimov
        (10, 10, 10),  # Fahrenheit 451 -> Ray Bradbury
        (11, 11, 5),  # And Then There Were None -> Agatha Christie
        (12, 12, 6),  # The Stand -> Stephen King
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO books_authors_link (id, book, author) VALUES (?, ?, ?)",
        book_authors
    )
    print(f"  Linked {len(book_authors)} books to authors")
    
    # Link books to tags
    book_tags = [
        (11, 5, 1),  # Murder on the Orient Express -> mystery
        (12, 5, 2),  # Murder on the Orient Express -> detective
        (13, 6, 6),  # The Shining -> horror
        (14, 6, 9),  # The Shining -> thriller
        (15, 7, 7),  # Harry Potter -> fantasy
        (16, 7, 10),  # Harry Potter -> young-adult
        (17, 8, 7),  # A Game of Thrones -> fantasy
        (18, 8, 9),  # A Game of Thrones -> thriller
        (19, 9, 8),  # Foundation -> sci-fi
        (20, 10, 8),  # Fahrenheit 451 -> sci-fi
        (21, 10, 3),  # Fahrenheit 451 -> classic
        (22, 11, 1),  # And Then There Were None -> mystery
        (23, 11, 2),  # And Then There Were None -> detective
        (24, 12, 6),  # The Stand -> horror
        (25, 12, 8),  # The Stand -> sci-fi
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO books_tags_link (id, book, tag) VALUES (?, ?, ?)",
        book_tags
    )
    print(f"  Linked {len(book_tags)} books to tags")
    
    # Link books to series
    book_series = [
        (3, 7, 2),  # Harry Potter -> Harry Potter series
        (4, 8, 3),  # A Game of Thrones -> A Song of Ice and Fire
        (5, 9, 4),  # Foundation -> Foundation series
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO books_series_link (id, book, series) VALUES (?, ?, ?)",
        book_series
    )
    print(f"  Linked {len(book_series)} books to series")
    
    # Add comments with diverse content
    comments = [
        (5, 5, "A classic Hercule Poirot mystery set on a train."),
        (6, 6, "A psychological horror novel about a writer's descent into madness."),
        (7, 7, "The first book in the Harry Potter series, introducing the wizarding world."),
        (8, 8, "The first book in A Song of Ice and Fire series, featuring political intrigue."),
        (9, 9, "A science fiction classic about the fall and rise of civilizations."),
        (10, 10, "A dystopian novel about censorship and book burning."),
        (11, 11, "One of Agatha Christie's most famous mystery novels."),
        (12, 12, "A post-apocalyptic horror novel about a plague and good vs evil."),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO comments (id, book, text) VALUES (?, ?, ?)",
        comments
    )
    print(f"  Added {len(comments)} comments")
    
    # Add format data
    format_data = [
        (7, 5, "EPUB", 3456, ""),
        (8, 5, "PDF", 1234, ""),
        (9, 6, "EPUB", 4567, ""),
        (10, 6, "MOBI", 3456, ""),
        (11, 7, "EPUB", 5678, ""),
        (12, 7, "PDF", 2345, ""),
        (13, 8, "EPUB", 6789, ""),
        (14, 9, "EPUB", 3456, ""),
        (15, 9, "PDF", 1234, ""),
        (16, 10, "EPUB", 2345, ""),
        (17, 11, "EPUB", 3456, ""),
        (18, 12, "EPUB", 7890, ""),
        (19, 12, "PDF", 4567, ""),
    ]
    cursor.executemany(
        """
        INSERT OR IGNORE INTO data (id, book, format, uncompressed_size, name)
        VALUES (?, ?, ?, ?, ?)
        """,
        format_data
    )
    print(f"  Added {len(format_data)} format entries")
    
    conn.commit()
    
    # Print summary
    cursor.execute("SELECT COUNT(*) FROM books")
    book_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM authors")
    author_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tags")
    tag_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM series")
    series_count = cursor.fetchone()[0]
    
    conn.close()
    
    print()
    print(f"[OK] Extensive test data added to {TEST_DB_PATH}")
    print(f"  - Total books: {book_count}")
    print(f"  - Total authors: {author_count}")
    print(f"  - Total tags: {tag_count}")
    print(f"  - Total series: {series_count}")
    print()
    print("Test database is now ready for comprehensive testing!")


if __name__ == "__main__":
    create_extensive_test_data()
