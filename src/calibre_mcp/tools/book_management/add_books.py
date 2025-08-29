"""Tool for adding new books to the Calibre library."""
import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

from fastmcp import MCPTool, Param
from calibre_plugins.calibremcp.storage.local import LocalStorage

class AddBooksTool(MCPTool):
    """Add new books to the Calibre library."""
    
    name = "add_books"
    description = "Add new books to the Calibre library"
    parameters = [
        Param("paths", List[str], "List of file paths to add"),
        Param("library_path", str, "Path to the Calibre library", required=False),
        Param("copy_files", bool, "Whether to copy files to the library", default=True),
        Param("auto_convert", bool, "Automatically convert to preferred format", default=False),
    ]
    
    async def _run(self, paths: List[str], library_path: Optional[str] = None, 
                  copy_files: bool = True, auto_convert: bool = False) -> Dict:
        """Add books to the library."""
        storage = LocalStorage(library_path)
        results = {"added": [], "failed": [], "skipped": []}
        
        for path in paths:
            try:
                path = Path(path).resolve()
                if not path.exists():
                    results["failed"].append({"path": str(path), "error": "File not found"})
                    continue
                
                # Check if book already exists
                file_hash = self._calculate_file_hash(path)
                if storage.book_exists(file_hash):
                    results["skipped"].append({"path": str(path), "reason": "Book already exists"})
                    continue
                
                # Add book to library
                book_id = await storage.add_book(
                    path=path,
                    copy_to_library=copy_files,
                    auto_convert=auto_convert
                )
                
                results["added"].append({
                    "path": str(path),
                    "book_id": book_id,
                    "file_hash": file_hash
                })
                
            except Exception as e:
                results["failed"].append({
                    "path": str(path),
                    "error": str(e)
                })
        
        return results
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
