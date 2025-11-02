"""
Test for full-text search functionality.
"""
import pytest
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calibre_mcp.tools.book_tools import search_books_helper
from calibre_mcp.db.database import init_database
from calibre_mcp.config import CalibreConfig


@pytest.mark.asyncio
async def test_fts_search():
    """Test full-text search for 'it was the worst of times'."""
    # Initialize database with default library
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
    
    if not library_path:
        print("ERROR: Large library not found!")
        return
    
    print(f"\n=== Using database: {library_path} ===")
    
    try:
        init_database(library_path, echo=False)
    except Exception as e:
        print(f"Database already initialized or error: {e}")
    
    # Test full-text search - try a phrase that might exist
    print("\n=== Testing full-text search ===")
    try:
        # First try a simple word that definitely exists
        result = await search_books_helper(
            text="Holmes",
            format_table=False,
            limit=10,
        )
        
        print(f"\n=== Test Result (simple word) ===")
        print(f"Success: {result.get('success', 'Key not present')}")
        print(f"Error: {result.get('error', 'None')}")
        if 'items' in result:
            print(f"Items: {len(result.get('items', []))}")
            if result['items']:
                print(f"First result: {result['items'][0].get('title', 'No title')}")
        
        # Now try the phrase
        print("\n=== Testing phrase search ===")
        result = await search_books_helper(
            text="it was the worst of times",
            format_table=False,
            limit=10,
        )
        
        print(f"\n=== Test Result ===")
        print(f"Success: {result.get('success', 'Key not present')}")
        print(f"Error: {result.get('error', 'None')}")
        if 'items' in result:
            print(f"Items: {len(result.get('items', []))}")
            if result['items']:
                print(f"First result: {result['items'][0].get('title', 'No title')}")
        
        assert result.get("success") is not False, f"Query failed: {result.get('error')}"
        if "items" in result:
            assert isinstance(result["items"], list)
    except Exception as e:
        print(f"\n=== Test Error ===")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(test_fts_search())
