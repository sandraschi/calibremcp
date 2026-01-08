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

        log_operation(
            logger,
            "calibre_config_dir",
            level="DEBUG",
            config_dir=str(config_dir),
            system=self.system,
        )
        return config_dir

    def discover_all_libraries(self) -> Dict[str, CalibreLibrary]:
        """
        Discover all available Calibre libraries using multiple methods.

        Priority:
        1. Explicitly given directory (L:/Multimedia Files/Written Word) - highest priority
        2. Parse Calibre's JSON config files (library_infos.json, global.py.json) - fallback

        Returns:
            Dict mapping library names to CalibreLibrary objects
        """
        libraries = {}

        # Method 1: Scan explicitly given directory first (highest priority)
        user_library_path = Path("L:/Multimedia Files/Written Word")
        if user_library_path.exists() and user_library_path.is_dir():
            scanned_libraries = self._scan_directory_for_libraries(user_library_path)
            libraries.update(scanned_libraries)

        # Method 2: Only parse JSON config if no libraries found from explicit directory
        if not libraries:
            # Use Calibre's Python API to get libraries (most reliable)
            calibre_api_libraries = self._discover_from_calibre_api()
            libraries.update(calibre_api_libraries)

            # Read from Calibre's JSON configuration files
            calibre_libraries = self._discover_from_calibre_config()
            libraries.update(calibre_libraries)

        # Method 3: Environment variable override (always checked)
        env_libraries = self._discover_from_environment()
        libraries.update(env_libraries)

        self.discovered_libraries = libraries
        log_operation(logger, "libraries_discovered", level="INFO", total_libraries=len(libraries))

        return libraries

    def _scan_directory_for_libraries(self, base_dir: Path) -> Dict[str, CalibreLibrary]:
        """Scan a specific directory for Calibre libraries"""
        libraries = {}
        
        try:
            # Only scan subdirectories for libraries (base directory itself is not a library)
            for item in base_dir.iterdir():
                if item.is_dir():
                    item_metadata_db = item / "metadata.db"
                    if item_metadata_db.exists():
                        libraries[item.name] = CalibreLibrary(
                            name=item.name,
                            path=item,
                            metadata_db=item_metadata_db,
                            is_active=False
                        )
        except (PermissionError, OSError) as e:
            logger.warning(f"Could not scan {base_dir} for libraries: {e}")
        
        return libraries

    def _discover_from_calibre_api(self) -> Dict[str, CalibreLibrary]:
        """Discover libraries using Calibre's Python API (most reliable method)"""
        libraries = {}
        
        try:
            # Try to import Calibre's config module to get library paths
            from calibre.utils.config import prefs
            
            # Get library database from Calibre's preferences
            library_path = prefs['library_path']
            if library_path and Path(library_path).exists() and (Path(library_path) / "metadata.db").exists():
                libraries["main"] = CalibreLibrary(
                    name="main",
                    path=Path(library_path),
                    metadata_db=Path(library_path) / "metadata.db",
                    is_active=True
                )
            
            # Get all libraries from Calibre's library database
            try:
                # Calibre stores library info in library_infos.pickle
                library_infos_path = self.calibre_config_dir / "library_infos.pickle"
                if library_infos_path.exists():
                    with open(library_infos_path, "rb") as f:
                        import pickle
                        lib_infos = pickle.load(f)
                        for lib_name, lib_info in lib_infos.items():
                            if isinstance(lib_info, dict) and "path" in lib_info:
                                lib_path = Path(lib_info["path"])
                                if lib_path.exists() and (lib_path / "metadata.db").exists():
                                    libraries[lib_name] = CalibreLibrary(
                                        name=lib_name,
                                        path=lib_path,
                                        metadata_db=lib_path / "metadata.db",
                                        is_active=lib_info.get("is_active", False)
                                    )
            except Exception as e:
                logger.debug(f"Could not read library_infos.pickle via Calibre API: {e}")
                
        except ImportError:
            # Calibre Python API not available - this is expected if Calibre is not installed as Python package
            logger.debug("Calibre Python API not available, falling back to config file parsing")
        except Exception as e:
            logger.warning(f"Error discovering libraries via Calibre API: {e}")
        
        return libraries

    def _discover_from_calibre_config(self) -> Dict[str, CalibreLibrary]:
        """Discover libraries from Calibre's configuration files"""
        libraries = {}

        if not self.calibre_config_dir.exists():
            log_operation(
                logger,
                "calibre_config_not_found",
                level="WARNING",
                config_dir=str(self.calibre_config_dir),
            )
            return libraries

        try:
            # Read global.py.json for library paths (Calibre now uses JSON format)
            global_py_json = self.calibre_config_dir / "global.py.json"
            if global_py_json.exists():
                libraries.update(self._parse_global_py_json(global_py_json))
            
            # Also try old format global.py (for backwards compatibility)
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
            with open(global_py, "r", encoding="utf-8") as f:
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
                        is_active=i == 0,
                    )

        except Exception as e:
            log_error(logger, "global_py_parse_error", e)

        return libraries

    def _parse_global_py_json(self, global_py_json: Path) -> Dict[str, CalibreLibrary]:
        """Parse Calibre's global.py.json configuration file (JSON format)"""
        libraries = {}

        try:
            with open(global_py_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract library_path from JSON
            if "library_path" in data:
                library_path = Path(data["library_path"])
                if library_path.exists() and (library_path / "metadata.db").exists():
                    libraries["main"] = CalibreLibrary(
                        name="main",
                        path=library_path,
                        metadata_db=library_path / "metadata.db",
                        is_active=True,
                    )

        except Exception as e:
            log_error(logger, "global_py_json_parse_error", e)

        return libraries

    def _parse_library_db(self, library_db: Path) -> Dict[str, CalibreLibrary]:
        """Parse Calibre's library_infos.json file"""
        libraries = {}

        try:
            with open(library_db, "r", encoding="utf-8") as f:
                data = json.load(f)

            for library_name, library_info in data.items():
                if isinstance(library_info, dict) and "path" in library_info:
                    library_path = Path(library_info["path"])
                    if library_path.exists() and (library_path / "metadata.db").exists():
                        libraries[library_name] = CalibreLibrary(
                            name=library_name,
                            path=library_path,
                            metadata_db=library_path / "metadata.db",
                            is_active=library_info.get("is_active", False),
                        )

        except Exception as e:
            log_error(logger, "library_db_parse_error", e)

        return libraries

    def _parse_library_pickle(self, library_pickle: Path) -> Dict[str, CalibreLibrary]:
        """Parse Calibre's library_infos.pickle file"""
        libraries = {}

        try:
            with open(library_pickle, "rb") as f:
                data = pickle.load(f)

            for library_name, library_info in data.items():
                if isinstance(library_info, dict) and "path" in library_info:
                    library_path = Path(library_info["path"])
                    if library_path.exists() and (library_path / "metadata.db").exists():
                        libraries[library_name] = CalibreLibrary(
                            name=library_name,
                            path=library_path,
                            metadata_db=library_path / "metadata.db",
                            is_active=library_info.get("is_active", False),
                        )

        except Exception as e:
            log_error(logger, "library_pickle_parse_error", e)

        return libraries

    def _scan_common_locations(self) -> Dict[str, CalibreLibrary]:
        """Scan common locations where Calibre libraries might be stored"""
        libraries = {}

        # Common base directories to scan
        # PRIORITY: User's actual library location first
        user_library_path = Path("L:/Multimedia Files/Written Word")
        common_bases = []
        
        # Add user's actual library location FIRST (highest priority)
        if user_library_path.exists():
            common_bases.append(user_library_path)
        
        # Then add other common locations (lower priority)
        common_bases.extend([
            Path.home() / "Documents" / "Calibre Library",
            Path.home() / "Books" / "Calibre Library",
            Path.home() / "Library" / "Calibre Library",  # macOS
            Path("/opt/calibre/library"),  # Linux
        ])
        
        # Skip the default Windows location if it's the wrong one
        # Only add C:\Users\...\Calibre Library if it's NOT the user's home
        default_windows_path = Path("C:/Users") / os.getenv("USERNAME", "") / "Calibre Library"
        if default_windows_path.exists() and default_windows_path != user_library_path:
            # Only add if it's different from the user's actual library
            common_bases.append(default_windows_path)

        # Add environment-specific paths
        if "CALIBRE_LIBRARY_PATH" in os.environ:
            common_bases.append(Path(os.environ["CALIBRE_LIBRARY_PATH"]))

        for base_dir in common_bases:
            if base_dir.exists() and base_dir.is_dir():
                # Check if this is a library directory
                metadata_db = base_dir / "metadata.db"
                if metadata_db.exists():
                    lib_name = base_dir.name if base_dir.name != "Written Word" else "main"
                    libraries[lib_name] = CalibreLibrary(
                        name=lib_name, path=base_dir, metadata_db=metadata_db, is_active=True
                    )

                # Scan for subdirectories that might be libraries
                try:
                    for item in base_dir.iterdir():
                        if item.is_dir() and (item / "metadata.db").exists():
                            libraries[item.name] = CalibreLibrary(
                                name=item.name, path=item, metadata_db=item / "metadata.db"
                            )
                except (PermissionError, OSError) as e:
                    logger.warning(f"Could not scan {base_dir}: {e}")

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
                    is_active=True,
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
                        metadata_db=library_path / "metadata.db",
                    )

        return libraries

    def _scan_parent_directories(
        self, existing_libraries: Dict[str, CalibreLibrary]
    ) -> Dict[str, CalibreLibrary]:
        """Scan parent directories of existing libraries for additional libraries"""
        libraries = {}

        for library in existing_libraries.values():
            parent_dir = library.path.parent

            # Scan parent directory for other libraries
            if parent_dir.exists() and parent_dir.is_dir():
                for item in parent_dir.iterdir():
                    if item.is_dir() and item != library.path and (item / "metadata.db").exists():
                        # Avoid duplicates
                        if item.name not in existing_libraries:
                            libraries[item.name] = CalibreLibrary(
                                name=item.name, path=item, metadata_db=item / "metadata.db"
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
