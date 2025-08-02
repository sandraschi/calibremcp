"""
Storage backends for Calibre MCP.

Provides a unified interface for accessing both local and remote Calibre libraries.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from ..models.book import Book
from ..models.library import LibraryInfo

class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def list_books(self, **filters) -> List[Book]:
        """List books with optional filtering"""
        pass
        
    @abstractmethod
    async def get_book(self, book_id: Union[int, str]) -> Optional[Book]:
        """Get a book by ID"""
        pass
        
    @abstractmethod
    async def get_library_info(self) -> LibraryInfo:
        """Get library metadata"""
        pass

# Import backends after base class is defined
from .local import LocalStorage
from .remote import RemoteStorage

def get_storage_backend(server_name: Optional[str] = None, **kwargs) -> StorageBackend:
    """
    Factory function to get the appropriate storage backend.
    
    Args:
        server_name: Name of the remote server to use, or None for local access
        
    Returns:
        Initialized storage backend instance
    """
    if server_name:
        return RemoteStorage(server_name=server_name, **kwargs)
    return LocalStorage(**kwargs)
