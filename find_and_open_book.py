#!/usr/bin/env python3
"""
Find and open a book for reading.

Example usage:
    python find_and_open_book.py "The Crooked Hinge"
    python find_and_open_book.py "crooked hinge" --author "Carr"
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

async def find_and_open_book(title: str, author: str = None, format_pref: str = "EPUB"):
    """Find a book by title and open it for reading."""
    
    print(f"Searching for: {title}")
    if author:
        print(f"Author filter: {author}")
    print("=" * 60)
    
    try:
        # Import services and helpers directly
        from calibre_mcp.services.book_service import book_service
        from calibre_mcp.tools.book_tools import search_books_helper
        from calibre_mcp.services.viewer_service import viewer_service
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database, get_database
        from sqlalchemy.orm import joinedload
        from calibre_mcp.db.models import Book, Data
        
        # Initialize database
        config = CalibreConfig()
        libraries = config.discover_libraries()
        
        if not libraries:
            print("[ERROR] No libraries found")
            return False
        
        first_lib_name = next(iter(libraries.keys()))
        first_lib_path = libraries[first_lib_name].path
        init_database(str(first_lib_path / "metadata.db"), echo=False)
        print(f"[OK] Using library: {first_lib_name}\n")
        
        # Step 1: Search for the book
        print("[STEP 1] Searching for book...")
        search_params = {"text": title, "limit": 10}
        if author:
            search_params["author"] = author
        
        search_result = await search_books_helper(**search_params)
        
        books = search_result.get("items", [])
        if not books:
            print(f"[ERROR] Book '{title}' not found")
            if author:
                print(f"       Tried with author filter: {author}")
            return False
        
        # Find best match (exact title match preferred)
        book = None
        title_lower = title.lower()
        for b in books:
            if title_lower in b.get("title", "").lower():
                book = b
                break
        
        if not book:
            book = books[0]  # Use first result
        
        book_id = book["id"]
        book_title = book.get("title", "Unknown")
        authors_list = book.get("authors", [])
        # Handle authors as dicts or strings
        if authors_list and isinstance(authors_list[0], dict):
            book_author = ", ".join([a.get("name", "") for a in authors_list])
        else:
            book_author = ", ".join(authors_list) if authors_list else "Unknown"
        
        print(f"[OK] Found: {book_title} by {book_author}")
        print(f"     Book ID: {book_id}\n")
        
        # Step 2: Get file path directly from book data
        print("[STEP 2] Getting book file...")
        from calibre_mcp.db.database import get_database
        from calibre_mcp.db.models import Book, Data
        
        db = get_database()
        with db.session_scope() as session:
            book = session.query(Book).options(joinedload(Book.data)).filter(Book.id == book_id).first()
            if not book:
                print(f"[ERROR] Book {book_id} not found")
                return False
            
            # Get library path
            library_path = first_lib_path
            
            # Find format
            formats = book.data
            format_obj = None
            
            # Try preferred format first
            for fmt in formats:
                if fmt.format.upper() == format_pref.upper():
                    format_obj = fmt
                    break
            
            # If not found, use first available
            if not format_obj and formats:
                format_obj = formats[0]
            
            if not format_obj:
                print(f"[ERROR] Book has no available formats")
                return False
            
            # Build file path: library_path / book.path / format_name.format
            file_format = format_obj.format.upper()
            file_name = format_obj.name if format_obj.name else f"{book.title}.{format_obj.format.lower()}"
            # Ensure filename has extension
            if not file_name.lower().endswith(f".{format_obj.format.lower()}"):
                file_name = f"{file_name}.{format_obj.format.lower()}"
            # Clean filename
            import re
            file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
            file_path = Path(library_path) / book.path / file_name
            
            # If file doesn't exist, try without extension (Calibre sometimes stores without)
            if not file_path.exists():
                file_path_no_ext = Path(library_path) / book.path / format_obj.name
                if file_path_no_ext.exists():
                    file_path = file_path_no_ext
            
            print(f"[OK] File found: {file_path}")
            print(f"     Format: {file_format}\n")
        
        # Step 3: Open the book
        print("[STEP 3] Opening book...")
        
        # Open with system default application
        try:
            import os
            import subprocess
            import platform
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                print(f"[ERROR] File not found: {file_path}")
                return False
            
            # Open file with default application based on OS
            system = platform.system()
            if system == "Windows":
                os.startfile(str(file_path_obj))
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(file_path_obj)])
            else:  # Linux
                subprocess.run(["xdg-open", str(file_path_obj)])
            
            print(f"[OK] Book opened with default application")
            print(f"     File: {file_path}")
            return True
        except Exception as e:
            print(f"[WARN] Error opening file: {e}")
            print(f"       File path: {file_path}")
            print(f"       You can open it manually from: {file_path}")
            return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python find_and_open_book.py <title> [--author <author>] [--format <EPUB|PDF|MOBI>]")
        print("\nExample:")
        print('  python find_and_open_book.py "The Crooked Hinge"')
        print('  python find_and_open_book.py "crooked hinge" --author "Carr"')
        print('  python find_and_open_book.py "The Crooked Hinge" --format PDF')
        sys.exit(1)
    
    title = sys.argv[1]
    author = None
    format_pref = "EPUB"
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--author" and i + 1 < len(sys.argv):
            author = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--format" and i + 1 < len(sys.argv):
            format_pref = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    success = asyncio.run(find_and_open_book(title, author, format_pref))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
