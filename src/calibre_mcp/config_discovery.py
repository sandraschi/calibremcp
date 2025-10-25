"""
Calibre Configuration Discovery

This module provides functions to discover Calibre libraries by reading
Calibre's configuration files and scanning common locations.
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
import platform

from .logging_config import get_logger, log_operation, log_error

logger = get_logger("calibremcp.config_discovery")


@dataclass
class CalibreLibrary:
    """Represents a discovered Calibre library"""
    name: str
    path: Path
    metadata_db: Path
    book_count: Optional[int] = None
    last_modified: Optional[str] = None
    is_active: bool = False


class CalibreConfigDiscovery:
    """Discovers Calibre libraries from various sources"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.calibre_config_dir = self._get_calibre_config_dir()
        self.discovered_libraries: Dict[str, CalibreLibrary] = {}
    
    def _get_calibre_config_dir(self) -> Path:
        """Get Calibre configuration directory based on OS"""
        if self.system == "windows":
            config_dir = Path(os.environ.get("APPDATA", "")) / "calibre"
        elif self.system == "darwin":  # macOS
            config_dir = Path.home() / "Library" / "Preferences" / "calibre"
        else:  # Linux and others
            config_dir = Path.home() / ".config" / "calibre"
        
        log_operation(logger, "calibre_config_dir", level="DEBUG", 
                     config_dir=str(config_dir), system=self.system)
        return config_dir
    
    def discover_all_libraries(self) -> Dict[str, CalibreLibrary]:
        """
        Discover all available Calibre libraries using multiple methods.
        
        Returns:
            Dict mapping library names to CalibreLibrary objects
        """
        libraries = {}
        
        # Method 1: Read from Calibre's global configuration
        calibre_libraries = self._discover_from_calibre_config()
        libraries.update(calibre_libraries)
        
        # Method 2: Scan common library locations
        scanned_libraries = self._scan_common_locations()
        libraries.update(scanned_libraries)
        
        # Method 3: Environment variable override
        env_libraries = self._discover_from_environment()
        libraries.update(env_libraries)
        
        # Method 4: Scan parent directories of existing libraries
        parent_libraries = self._scan_parent_directories(libraries)
        libraries.update(parent_libraries)
        
        self.discovered_libraries = libraries
        log_operation(logger, "libraries_discovered", level="INFO", 
                     total_libraries=len(libraries))
        
        return libraries
    
    def _discover_from_calibre_config(self) -> Dict[str, CalibreLibrary]:
        """Discover libraries from Calibre's configuration files"""
        libraries = {}
        
        if not self.calibre_config_dir.exists():
            log_operation(logger, "calibre_config_not_found", level="WARNING", 
                         config_dir=str(self.calibre_config_dir))
            return libraries
        
        try:
            # Read global.py for library paths
            global_py = self.calibre_config_dir / "global.py"
            if global_py.exists():
                libraries.update(self._parse_global_py(global_py))
            
            # Read library database for multiple libraries
            library_db = self.calibre_config_dir / "library_infos.json"
            if library_db.exists():
                libraries.update(self._parse_library_db(library_db))
            
            # Read library_infos.pickle (alternative format)
            library_pickle = self.calibre_config_dir / "library_infos.pickle"
            if library_pickle.exists():
                libraries.update(self._parse_library_pickle(library_pickle))
                
        except Exception as e:
            log_error(logger, "calibre_config_parse_error", e)
        
        return libraries
    
    def _parse_global_py(self, global_py: Path) -> Dict[str, CalibreLibrary]:
        """Parse Calibre's global.py configuration file"""
        libraries = {}
        
        try:
            with open(global_py, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for library path patterns
            import re
            
            # Pattern for library path: library_path = r'path'
            path_pattern = r"library_path\s*=\s*r?['\"]([^'\"]+)['\"]"
            matches = re.findall(path_pattern, content)
            
            for i, path_str in enumerate(matches):
                library_path = Path(path_str)
                if library_path.exists() and (library_path / "metadata.db").exists():
                    library_name = f"calibre_library_{i}" if i > 0 else "main"
                    libraries[library_name] = CalibreLibrary(
                        name=library_name,
                        path=library_path,
                        metadata_db=library_path / "metadata.db",
                        is_active=i == 0
                    )
                    
        except Exception as e:
            log_error(logger, "global_py_parse_error", e)
        
        return libraries
    
    def _parse_library_db(self, library_db: Path) -> Dict[str, CalibreLibrary]:
        """Parse Calibre's library_infos.json file"""
        libraries = {}
        
        try:
            with open(library_db, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for library_name, library_info in data.items():
                if isinstance(library_info, dict) and 'path' in library_info:
                    library_path = Path(library_info['path'])
                    if library_path.exists() and (library_path / "metadata.db").exists():
                        libraries[library_name] = CalibreLibrary(
                            name=library_name,
                            path=library_path,
                            metadata_db=library_path / "metadata.db",
                            is_active=library_info.get('is_active', False)
                        )
                        
        except Exception as e:
            log_error(logger, "library_db_parse_error", e)
        
        return libraries
    
    def _parse_library_pickle(self, library_pickle: Path) -> Dict[str, CalibreLibrary]:
        """Parse Calibre's library_infos.pickle file"""
        libraries = {}
        
        try:
            with open(library_pickle, 'rb') as f:
                data = pickle.load(f)
            
            for library_name, library_info in data.items():
                if isinstance(library_info, dict) and 'path' in library_info:
                    library_path = Path(library_info['path'])
                    if library_path.exists() and (library_path / "metadata.db").exists():
                        libraries[library_name] = CalibreLibrary(
                            name=library_name,
                            path=library_path,
                            metadata_db=library_path / "metadata.db",
                            is_active=library_info.get('is_active', False)
                        )
                        
        except Exception as e:
            log_error(logger, "library_pickle_parse_error", e)
        
        return libraries
    
    def _scan_common_locations(self) -> Dict[str, CalibreLibrary]:
        """Scan common locations where Calibre libraries might be stored"""
        libraries = {}
        
        # Common base directories to scan
        common_bases = [
            Path.home() / "Documents" / "Calibre Library",
            Path.home() / "Calibre Library",
            Path.home() / "Books" / "Calibre Library",
            Path.home() / "Library" / "Calibre Library",  # macOS
            Path("/opt/calibre/library"),  # Linux
            Path("C:/Users") / os.getenv("USERNAME", "") / "Documents" / "Calibre Library",  # Windows
        ]
        
        # Add environment-specific paths
        if "CALIBRE_LIBRARY_PATH" in os.environ:
            common_bases.append(Path(os.environ["CALIBRE_LIBRARY_PATH"]))
        
        for base_dir in common_bases:
            if base_dir.exists() and base_dir.is_dir():
                # Check if this is a library directory
                metadata_db = base_dir / "metadata.db"
                if metadata_db.exists():
                    libraries["main"] = CalibreLibrary(
                        name="main",
                        path=base_dir,
                        metadata_db=metadata_db,
                        is_active=True
                    )
                
                # Scan for subdirectories that might be libraries
                for item in base_dir.iterdir():
                    if item.is_dir() and (item / "metadata.db").exists():
                        libraries[item.name] = CalibreLibrary(
                            name=item.name,
                            path=item,
                            metadata_db=item / "metadata.db"
                        )
        
        return libraries
    
    def _discover_from_environment(self) -> Dict[str, CalibreLibrary]:
        """Discover libraries from environment variables"""
        libraries = {}
        
        # Check for CALIBRE_LIBRARY_PATH
        if "CALIBRE_LIBRARY_PATH" in os.environ:
            library_path = Path(os.environ["CALIBRE_LIBRARY_PATH"])
            if library_path.exists() and (library_path / "metadata.db").exists():
                libraries["env_main"] = CalibreLibrary(
                    name="env_main",
                    path=library_path,
                    metadata_db=library_path / "metadata.db",
                    is_active=True
                )
        
        # Check for CALIBRE_LIBRARIES (comma-separated list)
        if "CALIBRE_LIBRARIES" in os.environ:
            library_paths = os.environ["CALIBRE_LIBRARIES"].split(",")
            for i, path_str in enumerate(library_paths):
                library_path = Path(path_str.strip())
                if library_path.exists() and (library_path / "metadata.db").exists():
                    libraries[f"env_library_{i}"] = CalibreLibrary(
                        name=f"env_library_{i}",
                        path=library_path,
                        metadata_db=library_path / "metadata.db"
                    )
        
        return libraries
    
    def _scan_parent_directories(self, existing_libraries: Dict[str, CalibreLibrary]) -> Dict[str, CalibreLibrary]:
        """Scan parent directories of existing libraries for additional libraries"""
        libraries = {}
        
        for library in existing_libraries.values():
            parent_dir = library.path.parent
            
            # Scan parent directory for other libraries
            if parent_dir.exists() and parent_dir.is_dir():
                for item in parent_dir.iterdir():
                    if (item.is_dir() and 
                        item != library.path and 
                        (item / "metadata.db").exists()):
                        
                        # Avoid duplicates
                        if item.name not in existing_libraries:
                            libraries[item.name] = CalibreLibrary(
                                name=item.name,
                                path=item,
                                metadata_db=item / "metadata.db"
                            )
        
        return libraries
    
    def get_active_library(self) -> Optional[CalibreLibrary]:
        """Get the currently active Calibre library"""
        for library in self.discovered_libraries.values():
            if library.is_active:
                return library
        
        # If no active library found, return the first one
        if self.discovered_libraries:
            return list(self.discovered_libraries.values())[0]
        
        return None
    
    def get_library_by_name(self, name: str) -> Optional[CalibreLibrary]:
        """Get a specific library by name"""
        return self.discovered_libraries.get(name)
    
    def get_library_by_path(self, path: Path) -> Optional[CalibreLibrary]:
        """Get a library by its path"""
        for library in self.discovered_libraries.values():
            if library.path == path:
                return library
        return None
    
    def validate_library(self, library: CalibreLibrary) -> bool:
        """Validate that a library is accessible and has required files"""
        try:
            if not library.path.exists():
                return False
            
            if not library.metadata_db.exists():
                return False
            
            # Try to read the database
            import sqlite3
            conn = sqlite3.connect(str(library.metadata_db))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            log_error(logger, "library_validation_error", e, library_name=library.name)
            return False


# Global discovery instance
_discovery_instance: Optional[CalibreConfigDiscovery] = None


def get_calibre_discovery() -> CalibreConfigDiscovery:
    """Get the global Calibre discovery instance"""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = CalibreConfigDiscovery()
    return _discovery_instance


def discover_calibre_libraries() -> Dict[str, CalibreLibrary]:
    """Convenience function to discover all Calibre libraries"""
    discovery = get_calibre_discovery()
    return discovery.discover_all_libraries()


def get_active_calibre_library() -> Optional[CalibreLibrary]:
    """Convenience function to get the active Calibre library"""
    discovery = get_calibre_discovery()
    return discovery.get_active_library()


def get_calibre_library_by_name(name: str) -> Optional[CalibreLibrary]:
    """Convenience function to get a library by name"""
    discovery = get_calibre_discovery()
    return discovery.get_library_by_name(name)
