"""Advanced bulk operations for CalibreMCP."""
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastmcp import MCPTool, Param

class BulkOperationsTool(MCPTool):
    """Perform bulk operations on the Calibre library."""
    
    name = "bulk_operations"
    description = "Perform bulk operations on the library"
    
    async def _run(self, operation: str, **kwargs) -> Dict:
        """Route to the appropriate bulk operation handler."""
        handler = getattr(self, f"bulk_{operation}", None)
        if not handler:
            return {"error": f"Unknown bulk operation: {operation}", "success": False}
        
        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def bulk_update_metadata(self, book_ids: List[Union[int, str]], 
                                 updates: Dict[str, Any], 
                                 library_path: Optional[str] = None,
                                 batch_size: int = 10) -> Dict:
        """
        Update metadata for multiple books in bulk.
        
        Args:
            book_ids: List of book IDs to update
            updates: Dictionary of metadata fields to update
            library_path: Path to the Calibre library
            batch_size: Number of books to process in parallel
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        from calibre_plugins.calibremcp.tools.metadata.update_metadata import UpdateMetadataTool
        
        storage = LocalStorage(library_path)
        update_tool = UpdateMetadataTool()
        
        results = {
            "total": len(book_ids),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process books in batches
        for i in range(0, len(book_ids), batch_size):
            batch = book_ids[i:i + batch_size]
            batch_results = await update_tool._run(
                book_ids=batch,
                metadata=updates,
                library_path=library_path
            )
            
            results["successful"] += len(batch_results.get("updated", []))
            results["failed"] += len(batch_results.get("failed", []))
            results["errors"].extend(batch_results.get("failed", []))
            
            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.1)
        
        return results
    
    async def bulk_export(self, book_ids: List[Union[int, str]], 
                         export_path: str,
                         library_path: Optional[str] = None,
                         format: str = "directory") -> Dict:
        """
        Export multiple books to a specified location.
        
        Args:
            book_ids: List of book IDs to export
            export_path: Path where to export the books
            library_path: Path to the source Calibre library
            format: Export format (directory, zip)
        """
        from calibre_plugins.calibremcp.tools.import_export.export_library import ExportLibraryTool
        
        export_tool = ExportLibraryTool()
        
        return await export_tool._run(
            export_path=export_path,
            library_path=library_path,
            book_ids=book_ids,
            format=format
        )
    
    async def bulk_delete(self, book_ids: List[Union[int, str]],
                         library_path: Optional[str] = None,
                         delete_files: bool = True) -> Dict:
        """
        Delete multiple books from the library.
        
        Args:
            book_ids: List of book IDs to delete
            library_path: Path to the Calibre library
            delete_files: Whether to delete the actual book files
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        
        storage = LocalStorage(library_path)
        results = {
            "total": len(book_ids),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for book_id in book_ids:
            try:
                await storage.delete_book(book_id, delete_files=delete_files)
                results["successful"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "book_id": book_id,
                    "error": str(e)
                })
        
        return results
    
    async def bulk_convert(self, book_ids: List[Union[int, str]],
                          target_format: str,
                          library_path: Optional[str] = None,
                          replace_existing: bool = False) -> Dict:
        """
        Convert multiple books to a different format.
        
        Args:
            book_ids: List of book IDs to convert
            target_format: Target format (e.g., 'epub', 'mobi', 'pdf')
            library_path: Path to the Calibre library
            replace_existing: Whether to replace existing format if it exists
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        from calibre_plugins.calibremcp.tools.book_management.conversion import ConversionTool
        
        storage = LocalStorage(library_path)
        conversion_tool = ConversionTool()
        
        results = {
            "total": len(book_ids),
            "successful": 0,
            "failed": 0,
            "converted": [],
            "errors": []
        }
        
        for book_id in book_ids:
            try:
                # Check if the book already has the target format
                metadata = await storage.get_metadata(book_id)
                if not metadata:
                    raise ValueError(f"Book {book_id} not found")
                
                if target_format.lower() in [f.lower() for f in (metadata.formats or [])]:
                    if not replace_existing:
                        results["errors"].append({
                            "book_id": book_id,
                            "error": f"Book already has {target_format} format"
                        })
                        results["failed"] += 1
                        continue
                
                # Convert the book
                result = await conversion_tool._run(
                    book_id=book_id,
                    target_format=target_format,
                    library_path=library_path
                )
                
                if result.get("success"):
                    results["successful"] += 1
                    results["converted"].append({
                        "book_id": book_id,
                        "format": target_format,
                        "output_path": result.get("output_path")
                    })
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "book_id": book_id,
                        "error": result.get("error", "Unknown error")
                    })
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "book_id": book_id,
                    "error": str(e)
                })
        
        return results
