"""
CalibreMCP Configuration Management

Handles configuration for both local and remote Calibre library access.
Now includes automatic Calibre library discovery.
"""

import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, field_validator
from dotenv import load_dotenv

from .logging_config import get_logger, log_operation, log_error
from .config_discovery import CalibreLibrary, discover_calibre_libraries, get_active_calibre_library


logger = get_logger("calibremcp.config")


class RemoteServerConfig(BaseModel):
    """Configuration for a remote Calibre content server"""

    url: HttpUrl
    display_name: str = ""
    username: Optional[str] = None  # Not stored here, only in keyring


class CalibreConfig(BaseModel):
    """Root configuration for Calibre MCP with automatic library discovery"""

    # Library configuration - now auto-discovered
    local_library_path: Optional[Path] = Field(
        default=None, description="Path to local Calibre library (auto-discovered if not specified)"
    )

    # Discovered libraries
    discovered_libraries: Dict[str, CalibreLibrary] = Field(
        default_factory=dict, description="Automatically discovered Calibre libraries"
    )

    # Library discovery settings
    auto_discover_libraries: bool = Field(
        default=True, description="Automatically discover Calibre libraries on startup"
    )

    library_discovery_paths: List[Path] = Field(
        default_factory=list, description="Additional paths to scan for Calibre libraries"
    )

    # Disable remote access by default
    default_remote: Optional[str] = Field(None, description="Default remote server name to use")
    remotes: Dict[str, RemoteServerConfig] = Field(
        default_factory=dict, description="Configured remote servers"
    )

    # Server connection (disabled by default)
    use_remote: bool = Field(
        default=False, description="Set to True to enable remote server access"
    )
    server_url: str = Field(default="http://localhost:8080", description="Calibre server URL")
    username: Optional[str] = Field(default=None, description="Calibre username (if auth enabled)")
    password: Optional[str] = Field(default=None, description="Calibre password (if auth enabled)")

    # Request settings
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of request retries")

    # Search settings
    default_limit: int = Field(default=50, description="Default search result limit")
    max_limit: int = Field(default=200, description="Maximum search result limit")

    # Library settings
    library_name: str = Field(default="main", description="Primary library name")

    @field_validator("server_url")
    @classmethod
    def validate_server_url(cls, v):
        """Ensure server URL has proper format"""
        if not v.startswith(("http://", "https://")):
            return f"http://{v}"
        return v.rstrip("/")

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        """Ensure timeout is reasonable"""
        return max(5, min(300, v))  # 5-300 seconds

    @field_validator("default_limit", "max_limit")
    @classmethod
    def validate_limits(cls, v):
        """Ensure limits are reasonable"""
        return max(1, min(1000, v))

    @classmethod
    def load_config(cls, config_file: Optional[str] = None) -> "CalibreConfig":
        """
        Load configuration from file and environment variables.

        Priority order:
        1. Environment variables (highest priority)
        2. JSON configuration file
        3. Default values (lowest priority)

        Args:
            config_file: Optional path to JSON config file

        Returns:
            Initialized CalibreConfig instance
        """
        # Load environment variables
        load_dotenv()

        # Start with default config
        config_data = {}

        # Load from JSON file if provided
        if config_file:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        file_data = json.load(f)
                        config_data.update(file_data)
                except (json.JSONDecodeError, IOError) as e:
                    log_operation(
                        logger,
                        "config_load_warning",
                        level="WARNING",
                        config_file=str(config_file),
                        error=str(e),
                    )

        # Override with environment variables
        env_mappings = {
            "CALIBRE_SERVER_URL": "server_url",
            "CALIBRE_USERNAME": "username",
            "CALIBRE_PASSWORD": "password",
            "CALIBRE_TIMEOUT": "timeout",
            "CALIBRE_MAX_RETRIES": "max_retries",
            "CALIBRE_DEFAULT_LIMIT": "default_limit",
            "CALIBRE_MAX_LIMIT": "max_limit",
            "CALIBRE_LIBRARY_NAME": "library_name",
            "CALIBRE_BASE_PATH": "base_library_path",
            "CALIBRE_LIBRARY_PATHS": "library_paths",  # JSON-encoded dict of library paths
            "user_config.calibre_library_path": "local_library_path",  # MCP user config from Claude Desktop
        }

        # Special handling for library paths
        if "CALIBRE_LIBRARY_PATHS" in os.environ:
            try:
                lib_paths = json.loads(os.environ["CALIBRE_LIBRARY_PATHS"])
                if isinstance(lib_paths, dict):
                    config_data["library_paths"] = lib_paths
            except json.JSONDecodeError:
                log_operation(
                    logger, "invalid_json_warning", level="WARNING", env_var="CALIBRE_LIBRARY_PATHS"
                )

        # Handle base library path
        if "CALIBRE_BASE_PATH" in os.environ:
            base_path = os.environ["CALIBRE_BASE_PATH"]
            if os.path.exists(base_path):
                config_data["base_library_path"] = base_path

        # Process other environment variables
        for env_var, config_key in env_mappings.items():
            # Skip already processed special cases
            if env_var in ("CALIBRE_LIBRARY_PATHS", "CALIBRE_BASE_PATH"):
                continue

            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert to appropriate type
                if config_key in ["timeout", "max_retries", "default_limit", "max_limit"]:
                    try:
                        config_data[config_key] = int(env_value)
                    except ValueError:
                        log_operation(
                            logger,
                            "invalid_integer_warning",
                            level="WARNING",
                            env_var=env_var,
                            value=env_value,
                        )
                elif config_key == "local_library_path":
                    # Convert path string to Path object
                    config_data[config_key] = Path(env_value)
                else:
                    config_data[config_key] = env_value

        # Create config instance
        config = cls(**config_data)

        # Auto-discover libraries if enabled
        if config.auto_discover_libraries:
            config.discover_libraries()

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return self.dict()

    def save_config(self, config_file: str) -> bool:
        """
        Save current configuration to JSON file.

        Args:
            config_file: Path to save config file

        Returns:
            True if successful, False otherwise
        """
        try:
            config_path = Path(config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            config_dict = self.to_dict()
            # Remove sensitive data from saved config
            config_dict.pop("password", None)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            log_error(logger, "config_save_error", e, config_file=str(config_file))
            return False

    @property
    def has_auth(self) -> bool:
        """Check if authentication is configured"""
        return bool(self.username and self.password)

    @property
    def base_url(self) -> str:
        """Get base API URL for Calibre server"""
        return f"{self.server_url}/ajax"

    def get_auth(self) -> Optional[tuple]:
        """Get authentication tuple for requests"""
        if self.has_auth:
            return (self.username, self.password)
        return None

    def discover_libraries(self) -> Dict[str, CalibreLibrary]:
        """
        Discover all available Calibre libraries.

        Returns:
            Dict mapping library names to CalibreLibrary objects
        """
        if not self.auto_discover_libraries:
            return self.discovered_libraries

        try:
            # Use the discovery system
            libraries = discover_calibre_libraries()

            # Add any additional discovery paths
            if self.library_discovery_paths:
                for path in self.library_discovery_paths:
                    if path.exists() and path.is_dir():
                        # Scan this path for libraries
                        for item in path.iterdir():
                            if item.is_dir() and (item / "metadata.db").exists():
                                libraries[item.name] = CalibreLibrary(
                                    name=item.name, path=item, metadata_db=item / "metadata.db"
                                )

            self.discovered_libraries = libraries

            # Set default library path if not specified
            if not self.local_library_path and libraries:
                active_library = get_active_calibre_library()
                if active_library:
                    self.local_library_path = active_library.path
                else:
                    # Use the first library found
                    first_library = list(libraries.values())[0]
                    self.local_library_path = first_library.path

            log_operation(
                logger,
                "libraries_discovered",
                level="INFO",
                total_libraries=len(libraries),
                default_library=str(self.local_library_path),
            )

            return libraries

        except Exception as e:
            log_error(logger, "library_discovery_error", e)
            return {}

    def get_library_by_name(self, name: str) -> Optional[CalibreLibrary]:
        """Get a specific library by name"""
        if not self.discovered_libraries:
            self.discover_libraries()
        return self.discovered_libraries.get(name)

    def get_active_library(self) -> Optional[CalibreLibrary]:
        """Get the currently active library"""
        if not self.discovered_libraries:
            self.discover_libraries()

        # Find active library
        for library in self.discovered_libraries.values():
            if library.is_active:
                return library

        # If no active library, return the one matching local_library_path
        if self.local_library_path:
            for library in self.discovered_libraries.values():
                if library.path == self.local_library_path:
                    return library

        # Return first library if available
        if self.discovered_libraries:
            return list(self.discovered_libraries.values())[0]

        return None

    def list_libraries(self) -> List[Dict[str, Any]]:
        """Get a list of all discovered libraries with metadata"""
        if not self.discovered_libraries:
            self.discover_libraries()

        libraries = []
        for name, library in self.discovered_libraries.items():
            libraries.append(
                {
                    "name": name,
                    "path": str(library.path),
                    "metadata_db": str(library.metadata_db),
                    "is_active": library.is_active,
                    "book_count": library.book_count,
                    "last_modified": library.last_modified,
                }
            )

        return libraries

    def set_active_library(self, library_name: str) -> bool:
        """
        Set the active library by name.

        Args:
            library_name: Name of the library to activate

        Returns:
            True if successful, False if library not found
        """
        if not self.discovered_libraries:
            self.discover_libraries()

        if library_name not in self.discovered_libraries:
            return False

        # Update active status
        for name, library in self.discovered_libraries.items():
            library.is_active = name == library_name

        # Update local library path
        active_library = self.discovered_libraries[library_name]
        self.local_library_path = active_library.path

        log_operation(
            logger,
            "active_library_changed",
            level="INFO",
            library_name=library_name,
            library_path=str(active_library.path),
        )

        return True
