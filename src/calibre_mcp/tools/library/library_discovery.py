"""
Library discovery tool for CalibreMCP.

Provides controlled discovery of Calibre libraries with explicit permissions
for external tools like WizFile and Calibre CLI.

This tool implements the security-aware library discovery mechanism that was
originally attempted in Calibre++ but with proper permission controls.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response

logger = get_logger("calibremcp.tools.library_discovery")


class LibraryDiscoveryTool:
    """Controlled library discovery with explicit permissions."""

    def __init__(self):
        self.logger = logger

    def _is_valid_calibre_db(self, db_path: str) -> bool:
        """Check if a path contains a valid Calibre metadata.db."""
        try:
            import sqlite3

            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=2.0)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            self.logger.debug(f"Invalid Calibre DB {db_path}: {e}")
            return False

    def _discover_via_calibre_cli(self) -> list[dict[str, Any]]:
        """Discover libraries using Calibre CLI if available."""
        libraries = []

        # Common Calibre installation paths
        calibre_paths = [
            r"C:\Program Files\Calibre2\calibre.exe",
            r"C:\Program Files (x86)\Calibre2\calibre.exe",
            r"C:\Program Files\Calibre\calibre.exe",
            r"C:\Program Files (x86)\Calibre\calibre.exe",
        ]

        calibre_exe = None
        for path in calibre_paths:
            if os.path.exists(path):
                calibre_exe = path
                break

        if not calibre_exe:
            self.logger.info("Calibre CLI not found")
            return []

        try:
            # Try to get library list from Calibre CLI
            result = subprocess.run(
                [calibre_exe, "--with-library"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                # Parse output to find library paths
                # This is a simplified approach - in practice, Calibre CLI output
                # would need more sophisticated parsing
                lines = result.stdout.split("\n")
                for line in lines:
                    if "library" in line.lower() and ("\\" in line or "/" in line):
                        # Extract potential library path
                        # This is a placeholder - real implementation would parse properly
                        pass

        except Exception as e:
            self.logger.warning(f"Error using Calibre CLI: {e}")

        return libraries

    def _discover_via_wizfile(self) -> list[dict[str, Any]]:
        """Discover libraries using WizFile search if available."""
        libraries = []

        wizfile_path = r"C:\Program Files\WizFile\WizFile64.exe"
        if not os.path.exists(wizfile_path):
            self.logger.info("WizFile not found")
            return []

        try:
            # Create temp file for results
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
                temp_path = temp_file.name

            # Run WizFile search for metadata.db files
            result = subprocess.run(
                [wizfile_path, "metadata.db", f"/export={temp_path}"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and os.path.exists(temp_path):
                try:
                    import json

                    with open(temp_path, encoding="utf-8") as f:
                        results = json.load(f)

                    for entry in results.get("files", []):
                        db_path = Path(entry["path"])
                        if self._is_valid_calibre_db(str(db_path)):
                            library_path = str(db_path.parent)
                            library_id = f"wizfile_{hash(library_path) % 10000}"

                            library_info = {
                                "id": library_id,
                                "name": f"WizFile Discovery: {Path(library_path).name}",
                                "path": library_path,
                                "metadata_db_path": str(db_path),
                                "discovery_method": "wizfile",
                                "is_valid": True,
                            }
                            libraries.append(library_info)
                            self.logger.info(f"Found library via WizFile: {library_path}")

                except (json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
                    self.logger.warning(f"Error parsing WizFile results: {e}")
                finally:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass

        except subprocess.TimeoutExpired:
            self.logger.warning("WizFile search timed out")
        except Exception as e:
            self.logger.error(f"Error using WizFile: {e}")

        return libraries

    def _discover_via_common_paths(self) -> list[dict[str, Any]]:
        """Discover libraries in common Calibre installation paths."""
        libraries = []

        # Common Calibre library locations
        common_paths = [
            os.path.expanduser("~/Calibre Library"),
            os.path.expanduser("~/Documents/Calibre Library"),
            "C:/Users/Public/Documents/Calibre Library",
        ]

        for base_path in common_paths:
            if os.path.exists(base_path):
                # Check if this path directly contains metadata.db
                metadata_path = os.path.join(base_path, "metadata.db")
                if os.path.exists(metadata_path) and self._is_valid_calibre_db(metadata_path):
                    library_id = f"common_{hash(base_path) % 10000}"
                    library_info = {
                        "id": library_id,
                        "name": f"Common Path: {Path(base_path).name}",
                        "path": base_path,
                        "metadata_db_path": metadata_path,
                        "discovery_method": "common_paths",
                        "is_valid": True,
                    }
                    libraries.append(library_info)
                    self.logger.info(f"Found library in common path: {base_path}")

                # Also check subdirectories
                try:
                    for item in os.listdir(base_path):
                        sub_path = os.path.join(base_path, item)
                        if os.path.isdir(sub_path):
                            metadata_path = os.path.join(sub_path, "metadata.db")
                            if os.path.exists(metadata_path) and self._is_valid_calibre_db(
                                metadata_path
                            ):
                                library_id = f"common_sub_{hash(sub_path) % 10000}"
                                library_info = {
                                    "id": library_id,
                                    "name": f"Common Sub: {Path(sub_path).name}",
                                    "path": sub_path,
                                    "metadata_db_path": metadata_path,
                                    "discovery_method": "common_paths_subdir",
                                    "is_valid": True,
                                }
                                libraries.append(library_info)
                                self.logger.info(
                                    f"Found library in common subdirectory: {sub_path}"
                                )
                except (OSError, PermissionError) as e:
                    self.logger.warning(f"Could not scan subdirectories of {base_path}: {e}")

        return libraries

    def discover_libraries(
        self,
        wizfile_allowed: bool = False,
        calibre_cli_allowed: bool = False,
        common_paths_allowed: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Discover Calibre libraries using controlled methods with explicit permissions.

        Args:
            wizfile_allowed: Whether to allow WizFile system-wide search
            calibre_cli_allowed: Whether to allow Calibre CLI queries
            common_paths_allowed: Whether to search common installation paths

        Returns:
            List of discovered libraries with metadata
        """
        libraries = []
        methods_used = []

        # Always allowed: common paths search (safe, local)
        if common_paths_allowed:
            self.logger.info("Searching common Calibre paths...")
            common_libs = self._discover_via_common_paths()
            libraries.extend(common_libs)
            methods_used.append(f"common_paths ({len(common_libs)} found)")

        # Controlled: Calibre CLI (requires user permission)
        if calibre_cli_allowed:
            self.logger.info("Attempting Calibre CLI discovery...")
            cli_libs = self._discover_via_calibre_cli()
            libraries.extend(cli_libs)
            methods_used.append(f"calibre_cli ({len(cli_libs)} found)")

        # Controlled: WizFile search (requires user permission)
        if wizfile_allowed:
            self.logger.info("Attempting WizFile discovery...")
            wizfile_libs = self._discover_via_wizfile()
            libraries.extend(wizfile_libs)
            methods_used.append(f"wizfile ({len(wizfile_libs)} found)")

        self.logger.info(
            f"Library discovery complete: {len(libraries)} libraries found using {', '.join(methods_used)}"
        )

        return libraries


# Global instance
discovery_tool = LibraryDiscoveryTool()


@mcp.tool()
async def library_discovery(
    wizfile_allowed: bool = False,
    calibre_cli_allowed: bool = False,
    common_paths_allowed: bool = True,
) -> dict[str, Any]:
    """
    Discover Calibre libraries with controlled permissions for external tools.

    This tool provides secure library discovery with explicit user consent for
    potentially invasive operations like system-wide file searches.

    SECURITY MODEL:
    - common_paths_allowed: Safe local search (always enabled by default)
    - calibre_cli_allowed: Requires explicit permission to run Calibre CLI
    - wizfile_allowed: Requires explicit permission for system-wide WizFile search

    PORTMANTEAU PATTERN: Single tool for controlled discovery instead of multiple
    insecure individual tools.

    Args:
        wizfile_allowed: Allow WizFile system-wide search for metadata.db files
        calibre_cli_allowed: Allow Calibre CLI queries for library information
        common_paths_allowed: Allow search in common Calibre installation paths

    Returns:
        Dict with discovery results and metadata

    Examples:
        # Safe discovery (default)
        library_discovery()

        # Allow WizFile search
        library_discovery(wizfile_allowed=True)

        # Full discovery with all methods
        library_discovery(wizfile_allowed=True, calibre_cli_allowed=True)
    """
    try:
        libraries = discovery_tool.discover_libraries(
            wizfile_allowed=wizfile_allowed,
            calibre_cli_allowed=calibre_cli_allowed,
            common_paths_allowed=common_paths_allowed,
        )

        return {
            "success": True,
            "libraries_found": len(libraries),
            "libraries": libraries,
            "methods_used": {
                "common_paths": common_paths_allowed,
                "calibre_cli": calibre_cli_allowed,
                "wizfile": wizfile_allowed,
            },
            "security_note": "Discovery completed with user-specified permissions only",
        }

    except Exception as e:
        logger.error(f"Library discovery failed: {e}", exc_info=True)
        return format_error_response(
            f"Library discovery failed: {str(e)}", error_code="DISCOVERY_FAILED"
        )
