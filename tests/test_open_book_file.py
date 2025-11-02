"""Test the open_book_file tool with actual library data."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calibre_mcp.db.database import init_database
from calibre_mcp.services.book_service import book_service
from calibre_mcp.tools.viewer_tools import ViewerTools
from calibre_mcp.server import mcp


async def test_open_book_file():
    """Test opening a book file from search results."""
    # Initialize database with actual library
    library_path = r"L:\Multimedia Files\Written Word\Calibre-Bibliothek"
    db_path = Path(library_path) / "metadata.db"
    
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return
    
    print(f"=== Using database: {db_path} ===\n")
    
    # Initialize database
    init_database(str(db_path))
    
    # Search for Conan Doyle books
    print("=== Searching for Conan Doyle books ===")
    results = book_service.get_all(
        search="Conan Doyle",
        limit=5
    )
    
    if not results.get("items"):
        print("No books found!")
        return
    
    print(f"Found {len(results['items'])} books\n")
    
    # Get first book
    book = results["items"][0]
    book_id = book["id"]
    print(f"=== Testing with book: {book.get('title', 'Unknown')} (ID: {book_id}) ===\n")
    
    # Check formats
    if not book.get("formats"):
        print("ERROR: Book has no formats in results!")
        print(f"Book data: {book.keys()}")
        return
    
    print(f"Formats available: {[f.get('format') for f in book['formats']]}\n")
    
    # Get file path from formats
    file_path = None
    for fmt in book["formats"]:
        if fmt.get("format", "").upper() in ["EPUB", "PDF"]:
            file_path = fmt.get("path")
            if file_path and Path(file_path).exists():
                print(f"Using format: {fmt.get('format')}")
                print(f"File path: {file_path}\n")
                break
    
    if not file_path:
        # Use first format
        file_path = book["formats"][0].get("path")
        print(f"Using first format: {book['formats'][0].get('format')}")
        print(f"File path: {file_path}\n")
    
    if not file_path:
        print("ERROR: No file path found in formats!")
        return
    
    # Check if file exists
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f"ERROR: File does not exist: {file_path}")
        return
    
    print(f"✓ File exists: {file_path_obj.name} ({file_path_obj.stat().st_size / 1024:.1f} KB)\n")
    
    # Test the tool
    print("=== Testing open_book_file tool ===")
    viewer_tools = ViewerTools(mcp)
    
    try:
        result = await viewer_tools.open_book_file(book_id, file_path)
        
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        if result.get('file_path'):
            print(f"File opened: {result.get('file_path')}")
        
        if result.get('success'):
            print("\n✓ SUCCESS: Book should have opened in your default application!")
        else:
            print(f"\n✗ FAILED: {result.get('message')}")
    
    except Exception as e:
        print(f"\n✗ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_open_book_file())

