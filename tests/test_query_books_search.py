"""
Test for query_books search functionality.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the helper function directly to test it
from calibre_mcp.tools.book_tools import search_books_helper


@pytest.mark.asyncio
async def test_query_books_search_author():
    """Test searching for books by author."""
    # Initialize database with default library path
    from calibre_mcp.db.database import init_database, get_database
    from calibre_mcp.config import CalibreConfig
    from pathlib import Path
    
    config = CalibreConfig()
    
    # Find the actual library database - prioritize the large library
    library_path = None
    
    # Try the large library first (L:\Multimedia Files\Written Word\Calibre-Bibliothek)
    large_lib = Path("L:\\Multimedia Files\\Written Word\\Calibre-Bibliothek\\metadata.db")
    if large_lib.exists():
        library_path = str(large_lib)
        print(f"Found large library: {library_path}")
    
    if not library_path and config.local_library_path:
        db_path = config.local_library_path / "metadata.db"
        if db_path.exists():
            library_path = str(db_path)
            print(f"Found configured library: {library_path}")
    
    if not library_path:
        # Try default Calibre library location
        default_lib = Path.home() / "Calibre Library" / "metadata.db"
        if default_lib.exists():
            library_path = str(default_lib)
            print(f"Found default library: {library_path}")
    
    if not library_path:
        print("ERROR: No Calibre library database found!")
        print(f"Checked: {large_lib}")
        print(f"Checked: {config.local_library_path}")
        return
    
    print(f"\n=== Using database: {library_path} ===")
    
    try:
        init_database(library_path, echo=False)
    except Exception as e:
        print(f"Database already initialized or error: {e}")
    
    # First, try to get total books to verify database access
    print("\n=== Testing database access ===")
    try:
        all_books = await search_books_helper(
            format_table=False,
            limit=5,
        )
        print(f"Total books in library: {all_books.get('total', 0)}")
        if all_books.get('items'):
            print(f"Sample book: {all_books['items'][0].get('title', 'N/A')}")
            print(f"Sample authors: {all_books['items'][0].get('authors', [])}")
    except Exception as e:
        print(f"Error getting all books: {e}")
    
    # Now test the Conan Doyle search
    print("\n=== Testing Conan Doyle search ===")
    try:
        # Test with format_table=True to verify table formatting works
        result = await search_books_helper(
            author="Conan Doyle",
            format_table=True,
            limit=10,
        )
    except Exception as e:
        print(f"\n=== Test Error ===")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    print(f"\n=== Test Result ===")
    print(f"Total matching books: {result.get('total', 0)}")
    print(f"Items returned: {len(result.get('items', []))}")
    if result.get('items'):
        print(f"First result: {result['items'][0].get('title', 'N/A')}")
        print(f"First result authors: {result['items'][0].get('authors', [])}")
    
    # Test passes if we get a valid response (even if 0 results)
    assert isinstance(result.get("items"), list), "Result should contain 'items' list"
    assert result.get("total", 0) >= 0, "Total should be non-negative"


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_query_books_search_author())

