"""
Calibre Ebook Management Module
Austrian dev efficiency for comprehensive ebook operations
"""

from .manager import CalibreManager, CalibreManagerError
from .library_operations import LibraryOperations
from .conversion_manager import ConversionManager
from .metadata_manager import MetadataManager
from .search_operations import SearchOperations

__all__ = [
    'CalibreManager',
    'CalibreManagerError',
    'LibraryOperations', 
    'ConversionManager',
    'MetadataManager',
    'SearchOperations'
]

__version__ = "1.0.0"
