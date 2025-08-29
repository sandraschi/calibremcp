"""
Utility functions for discovering and managing Calibre libraries.
"""
from pathlib import Path
from typing import List, Dict, Optional
import os

# Base directory containing Calibre libraries
CALIBRE_BASE_DIR = Path("L:/Multimedia Files/Written Word")

def discover_calibre_libraries() -> Dict[str, Path]:
    """
    Discover all Calibre libraries in the base directory.
    
    Returns:
        Dict mapping library names to their paths
    """
    libraries = {}
    
    if not CALIBRE_BASE_DIR.exists() or not CALIBRE_BASE_DIR.is_dir():
        return {}
    
    for item in CALIBRE_BASE_DIR.iterdir():
        if item.is_dir():
            metadata_db = item / "metadata.db"
            if metadata_db.exists():
                libraries[item.name] = item
    
    return libraries

def get_library_metadata(library_path: Path) -> Dict[str, any]:
    """
    Get metadata about a specific library.
    
    Args:
        library_path: Path to the library directory
        
    Returns:
        Dictionary containing library metadata
    """
    metadata = {
        'name': library_path.name,
        'path': str(library_path),
        'metadata_db': str(library_path / "metadata.db"),
        'exists': (library_path / "metadata.db").exists(),
        'size_mb': 0,
        'book_count': 0
    }
    
    # Calculate library size
    try:
        metadata['size_mb'] = sum(
            f.stat().st_size 
            for f in library_path.glob('**/*') 
            if f.is_file()
        ) / (1024 * 1024)  # Convert to MB
    except (OSError, PermissionError):
        pass
    
    # Count books (each book is a subdirectory)
    try:
        metadata['book_count'] = sum(
            1 for _ in library_path.glob('*') 
            if _.is_dir() and _.name.isdigit()
        )
    except (OSError, PermissionError):
        pass
    
    return metadata

def get_current_library() -> Optional[Path]:
    """
    Get the current active library path from configuration.
    
    Returns:
        Path to the current library or None if not set
    """
    from ...config import get_config
    
    config = get_config()
    if config.local_library_path and (config.local_library_path / "metadata.db").exists():
        return config.local_library_path
    
    # Fallback to first found library
    libraries = discover_calibre_libraries()
    if libraries:
        return next(iter(libraries.values()))
    
    return None
