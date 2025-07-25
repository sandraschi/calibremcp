"""
Library Operations - Calibre library management
"""

import logging
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

class LibraryOperations:
    """Calibre library management operations"""
    
    def __init__(self, calibre_manager):
        self.calibre = calibre_manager
    
    def search_books(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search books in library"""
        try:
            result = self.calibre.run_command(["search", query, "--limit", str(limit)])
            if not result["success"]:
                return []
                
            book_ids = [line.strip() for line in result["stdout"].strip().split('\n') if line.strip()]
            
            if book_ids:
                list_result = self.calibre.run_command([
                    "list", "--fields", "title,authors,formats,tags",
                    "--for-machine"
                ] + book_ids)
                
                if list_result["success"]:
                    try:
                        return json.loads(list_result["stdout"])
                    except json.JSONDecodeError:
                        pass
            return []
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def add_book(self, file_path: str, **metadata) -> Dict[str, Any]:
        """Add book to library"""
        try:
            args = ["add", file_path]
            for key, value in metadata.items():
                if value:
                    args.extend([f"--{key}", str(value)])
            
            result = self.calibre.run_command(args)
            return {
                "success": result["success"],
                "message": result["stdout"] if result["success"] else result["stderr"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
