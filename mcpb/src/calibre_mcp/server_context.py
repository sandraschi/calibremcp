"""
Server context - holds get_api_client, current_library, etc.

Extracted to break circular import: tools import from here instead of server.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from calibre_mcp.calibre_api import CalibreAPIClient

api_client: Optional["CalibreAPIClient"] = None
current_library: str = "main"
available_libraries: dict[str, Any] = {}


async def get_api_client() -> Optional["CalibreAPIClient"]:
    """Get or create API client for remote Calibre. Returns None for local libraries."""
    from calibre_mcp.config import CalibreConfig

    global api_client
    config = CalibreConfig()
    if not config.use_remote:
        return None
    if api_client is None:
        from calibre_mcp.calibre_api import CalibreAPIClient

        _client = CalibreAPIClient(config)
        await _client.initialize()
        api_client = _client
    return api_client


async def discover_libraries() -> dict[str, Any]:
    """Discover available Calibre libraries."""
    global available_libraries
    if available_libraries:
        return available_libraries

    from calibre_mcp.config import CalibreConfig

    config = CalibreConfig()
    libraries: dict[str, Any] = {}
    if config.local_library_path and config.local_library_path.exists():
        libraries["main"] = str(config.local_library_path)

    base_dir = Path("L:/Multimedia Files/Written Word")
    if base_dir.exists():
        for item in base_dir.iterdir():
            if item.is_dir() and (item / "metadata.db").exists():
                libraries[item.name] = str(item)

    available_libraries = libraries
    return libraries
