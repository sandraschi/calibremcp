r"""
FastMCP 2.13+ Persistent Storage Integration

Uses FastMCP's built-in storage backends for persistent state management.

IMPORTANT: This implementation uses DiskStore to ensure data persists across
Claude Desktop restarts. Storage is saved to platform-appropriate directories:
- Windows: %APPDATA%\calibre-mcp
- macOS: ~/Library/Application Support/calibre-mcp
- Linux: ~/.local/share/calibre-mcp
"""

import asyncio
import json
import os
import platform
import time
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# Storage keys
STORAGE_PREFIX = "calibremcp:"
CURRENT_LIBRARY_KEY = f"{STORAGE_PREFIX}current_library"
LIBRARY_CACHE_KEY = f"{STORAGE_PREFIX}library_cache"
USER_PREFS_KEY = f"{STORAGE_PREFIX}user_preferences"
SESSION_STATE_KEY = f"{STORAGE_PREFIX}session_state"
SEARCH_PREFS_KEY = f"{STORAGE_PREFIX}search_preferences"
SEARCH_HISTORY_KEY = f"{STORAGE_PREFIX}search_history"
READING_PROGRESS_KEY = f"{STORAGE_PREFIX}reading_progress"
VIEWER_PREFS_KEY = f"{STORAGE_PREFIX}viewer_preferences"
FAVORITES_KEY = f"{STORAGE_PREFIX}favorites"


class CalibreMCPStorage:
    r"""
    Wrapper around FastMCP storage for CalibreMCP persistent state.

    Uses DiskStore to ensure data persists across Claude Desktop and Windows restarts.
    Storage location is in AppData\Roaming on Windows, which persists across reboots.
    """

    def __init__(self, mcp: FastMCP, use_disk_storage: bool = True):
        """
        Initialize storage with FastMCP instance.

        Args:
            mcp: FastMCP server instance
            use_disk_storage: If True (default), use DiskStore for persistence.
                            If False, use default in-memory storage (won't persist).
        """
        self.mcp = mcp
        self._storage = None
        self._initialized = False
        self._use_disk_storage = use_disk_storage

        # Platform-appropriate storage directory that survives Windows restarts
        if use_disk_storage:
            # Windows: %APPDATA%\calibre-mcp (persists across reboots)
            # macOS: ~/Library/Application Support/calibre-mcp
            # Linux: ~/.local/share/calibre-mcp
            if os.name == "nt":  # Windows
                appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
                self._storage_dir = Path(appdata) / "calibre-mcp"
            else:  # macOS/Linux
                home = Path.home()
                # Check for macOS (Darwin) safely
                if platform.system() == "Darwin":  # macOS
                    self._storage_dir = home / "Library" / "Application Support" / "calibre-mcp"
                else:  # Linux
                    self._storage_dir = home / ".local" / "share" / "calibre-mcp"

            # Create directory if it doesn't exist
            self._storage_dir.mkdir(parents=True, exist_ok=True)
        else:
            self._storage_dir = None

    async def initialize(self) -> None:
        """
        Initialize the storage backend.

        For persistence across Claude Desktop restarts, we use DiskStore directly
        instead of relying on FastMCP's default in-memory storage.
        """
        if self._initialized:
            return

        try:
            # Use DiskStore directly for guaranteed persistence across restarts
            if self._use_disk_storage and self._storage_dir:
                try:
                    from key_value.aio.stores.disk import DiskStore

                    # Create persistent disk storage
                    self._storage = DiskStore(directory=str(self._storage_dir))
                    self._initialized = True
                    return
                except ImportError:
                    # Fallback if py-key-value-aio[disk] not available
                    pass

            # Fallback: Try to use FastMCP's storage (may be in-memory)
            # Method 1: Direct property access
            if hasattr(self.mcp, "storage") and self.mcp.storage:
                self._storage = self.mcp.storage
                self._initialized = True
                return

            # Method 2: Via get_storage() method if available
            if hasattr(self.mcp, "get_storage"):
                storage_getter = self.mcp.get_storage
                if callable(storage_getter):
                    self._storage = (
                        await storage_getter()
                        if asyncio.iscoroutinefunction(storage_getter)
                        else storage_getter()
                    )
                    if self._storage:
                        self._initialized = True
                        return

            # If we get here, storage is not available
            # This is OK - graceful degradation
            self._initialized = False

        except Exception:
            # Storage might not be available yet - that's ok
            # We'll retry when actually needed
            self._initialized = False

    async def get_current_library(self) -> str | None:
        """Get the current library name from persistent storage."""
        await self.initialize()
        if not self._storage:
            return None

        try:
            value = await self._storage.get(CURRENT_LIBRARY_KEY)
            return value if isinstance(value, str) else None
        except Exception:
            return None

    async def set_current_library(self, library_name: str) -> None:
        """Store the current library name persistently."""
        await self.initialize()
        if not self._storage:
            return

        try:
            await self._storage.set(CURRENT_LIBRARY_KEY, library_name)
        except Exception:
            pass  # Graceful degradation

    async def get_user_preferences(self) -> dict[str, Any]:
        """Get user preferences from persistent storage."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            value = await self._storage.get(USER_PREFS_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {}
        except Exception:
            return {}

    async def set_user_preferences(self, prefs: dict[str, Any]) -> None:
        """Store user preferences persistently."""
        await self.initialize()
        if not self._storage:
            return

        try:
            await self._storage.set(USER_PREFS_KEY, prefs)
        except Exception:
            pass  # Graceful degradation

    async def get_session_state(self, session_id: str) -> dict[str, Any]:
        """Get session-specific state."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            key = f"{SESSION_STATE_KEY}:{session_id}"
            value = await self._storage.get(key)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {}
        except Exception:
            return {}

    async def set_session_state(self, session_id: str, state: dict[str, Any]) -> None:
        """Store session-specific state."""
        await self.initialize()
        if not self._storage:
            return

        try:
            key = f"{SESSION_STATE_KEY}:{session_id}"
            await self._storage.set(key, state)
        except Exception:
            pass  # Graceful degradation

    async def clear_session_state(self, session_id: str) -> None:
        """Clear session-specific state."""
        await self.initialize()
        if not self._storage:
            return

        try:
            key = f"{SESSION_STATE_KEY}:{session_id}"
            await self._storage.delete(key)
        except Exception:
            pass  # Graceful degradation

    async def cache_library_stats(
        self, library_name: str, stats: dict[str, Any], ttl: int = 3600
    ) -> None:
        """Cache library statistics with TTL (default 1 hour)."""
        await self.initialize()
        if not self._storage:
            return

        try:
            key = f"{LIBRARY_CACHE_KEY}:{library_name}"
            # FastMCP storage supports TTL if the backend supports it
            await self._storage.set(key, stats, ttl=ttl)
        except Exception:
            pass  # Graceful degradation

    async def get_cached_library_stats(self, library_name: str) -> dict[str, Any] | None:
        """Get cached library statistics if available and not expired."""
        await self.initialize()
        if not self._storage:
            return None

        try:
            key = f"{LIBRARY_CACHE_KEY}:{library_name}"
            value = await self._storage.get(key)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return None
        except Exception:
            return None

    # ==================== SEARCH PREFERENCES ====================

    async def get_search_preferences(self) -> dict[str, Any]:
        """Get user's search preferences (default sort, limit, etc.)."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            value = await self._storage.get(SEARCH_PREFS_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {}
        except Exception:
            return {}

    async def set_search_preferences(self, prefs: dict[str, Any]) -> None:
        """Store search preferences (sort order, default limit, etc.)."""
        await self.initialize()
        if not self._storage:
            return

        try:
            # Merge with existing preferences
            current = await self.get_search_preferences()
            current.update(prefs)
            await self._storage.set(SEARCH_PREFS_KEY, current)
        except Exception:
            pass  # Graceful degradation

    # ==================== SEARCH HISTORY ====================

    async def add_search_to_history(
        self, query: str, filters: dict[str, Any], max_history: int = 50
    ) -> None:
        """Add a search query to history (FIFO, limited to max_history)."""
        await self.initialize()
        if not self._storage:
            return

        try:
            history = await self.get_search_history()
            # Add timestamp
            entry = {
                "query": query,
                "filters": filters,
                "timestamp": time.time(),
            }
            # Prepend new entry
            history.insert(0, entry)
            # Limit to max_history
            history = history[:max_history]
            await self._storage.set(SEARCH_HISTORY_KEY, history)
        except Exception:
            pass  # Graceful degradation

    async def get_search_history(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent search history."""
        await self.initialize()
        if not self._storage:
            return []

        try:
            value = await self._storage.get(SEARCH_HISTORY_KEY)
            if isinstance(value, list):
                return value[:limit]
            elif isinstance(value, str):
                return json.loads(value)[:limit]
            return []
        except Exception:
            return []

    async def clear_search_history(self) -> None:
        """Clear all search history."""
        await self.initialize()
        if not self._storage:
            return

        try:
            await self._storage.delete(SEARCH_HISTORY_KEY)
        except Exception:
            pass  # Graceful degradation

    # ==================== READING PROGRESS ====================

    async def get_reading_progress(self, book_id: str) -> dict[str, Any] | None:
        """Get reading progress for a specific book."""
        await self.initialize()
        if not self._storage:
            return None

        try:
            key = f"{READING_PROGRESS_KEY}:{book_id}"
            value = await self._storage.get(key)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return None
        except Exception:
            return None

    async def set_reading_progress(self, book_id: str, progress: dict[str, Any]) -> None:
        """Save reading progress for a book (page, position, timestamp)."""
        await self.initialize()
        if not self._storage:
            return

        try:
            key = f"{READING_PROGRESS_KEY}:{book_id}"
            # Add timestamp if not present
            if "last_updated" not in progress:
                import time

                progress["last_updated"] = time.time()
            await self._storage.set(key, progress)
        except Exception:
            pass  # Graceful degradation

    async def get_all_reading_progress(self) -> dict[str, dict[str, Any]]:
        """Get reading progress for all books."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            # Note: This is a simplified implementation
            # In a real scenario, you might want to store all progress in a single key
            # or iterate through keys with the prefix
            # For now, this returns empty - individual book progress is accessed via get_reading_progress
            return {}
        except Exception:
            return {}

    # ==================== VIEWER PREFERENCES ====================

    async def get_viewer_preferences(self) -> dict[str, Any]:
        """Get viewer preferences (zoom, layout, reading direction, etc.)."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            value = await self._storage.get(VIEWER_PREFS_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            # Default preferences
            return {
                "zoom_level": 1.0,
                "zoom_mode": "fit-width",
                "reading_direction": "ltr",
                "page_layout": "single",
                "background_color": "#000000",
                "show_controls": True,
                "show_thumbnails": True,
            }
        except Exception:
            return {}

    async def set_viewer_preferences(self, prefs: dict[str, Any]) -> None:
        """Store viewer preferences."""
        await self.initialize()
        if not self._storage:
            return

        try:
            # Merge with existing preferences
            current = await self.get_viewer_preferences()
            current.update(prefs)
            await self._storage.set(VIEWER_PREFS_KEY, current)
        except Exception:
            pass  # Graceful degradation

    # ==================== FAVORITES ====================

    async def get_favorites(self) -> dict[str, list[str]]:
        """Get favorites organized by type (authors, tags, series, books)."""
        await self.initialize()
        if not self._storage:
            return {"authors": [], "tags": [], "series": [], "books": []}

        try:
            value = await self._storage.get(FAVORITES_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {"authors": [], "tags": [], "series": [], "books": []}
        except Exception:
            return {"authors": [], "tags": [], "series": [], "books": []}

    async def add_favorite(self, favorite_type: str, item: str) -> None:
        """Add an item to favorites (type: authors, tags, series, books)."""
        await self.initialize()
        if not self._storage:
            return

        try:
            favorites = await self.get_favorites()
            if favorite_type not in favorites:
                favorites[favorite_type] = []
            if item not in favorites[favorite_type]:
                favorites[favorite_type].append(item)
            await self._storage.set(FAVORITES_KEY, favorites)
        except Exception:
            pass  # Graceful degradation

    async def remove_favorite(self, favorite_type: str, item: str) -> None:
        """Remove an item from favorites."""
        await self.initialize()
        if not self._storage:
            return

        try:
            favorites = await self.get_favorites()
            if favorite_type in favorites and item in favorites[favorite_type]:
                favorites[favorite_type].remove(item)
                await self._storage.set(FAVORITES_KEY, favorites)
        except Exception:
            pass  # Graceful degradation

    async def is_favorite(self, favorite_type: str, item: str) -> bool:
        """Check if an item is in favorites."""
        favorites = await self.get_favorites()
        return favorite_type in favorites and item in favorites[favorite_type]


# Global storage instance (initialized in server startup)
_storage_instance: CalibreMCPStorage | None = None


def get_storage(mcp: FastMCP | None = None) -> CalibreMCPStorage | None:
    """Get the global storage instance."""
    global _storage_instance
    if _storage_instance is None and mcp is not None:
        _storage_instance = CalibreMCPStorage(mcp)
    return _storage_instance


def set_storage(storage: CalibreMCPStorage) -> None:
    """Set the global storage instance."""
    global _storage_instance
    _storage_instance = storage
