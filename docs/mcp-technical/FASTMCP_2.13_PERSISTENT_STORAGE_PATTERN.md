# FastMCP 2.13+ Persistent Storage Pattern

**Complete guide for implementing cross-session persistence in MCP servers using FastMCP 2.13+ storage backends**

---

## 🎯 Overview

FastMCP 2.13+ introduces pluggable storage backends that enable **true persistence across Claude Desktop restarts and even Windows/OS restarts**. This pattern is essential for any MCP server that needs to remember state, preferences, or data between sessions.

### **Why This Pattern Matters**

- **Cross-session persistence**: Data survives Claude Desktop restarts
- **Cross-OS persistence**: Data survives Windows/OS reboots
- **Platform-aware storage**: Automatically uses correct directories per OS
- **Simple key-value interface**: Easy to use, no database setup required
- **Production-ready**: Used by FastMCP for OAuth tokens, response caching, and more

---

## 📋 Requirements

### **Dependencies**

```toml
[project]
dependencies = [
    "fastmcp>=2.13.0",
    "py-key-value-aio[disk]>=1.0.0",  # For DiskStore backend
]
```

### **FastMCP 2.13+ Features Used**

- **Server lifespans** (`lifespan` parameter)
- **Storage backends** (`py-key-value-aio`)
- **DiskStore** (persistent file-based storage)

---

## 🏗️ Architecture

### **Storage Location by Platform**

The pattern automatically uses platform-appropriate directories:

| Platform | Storage Directory | Persists Across |
|----------|------------------|-----------------|
| **Windows** | `%APPDATA%\your-app-name` | ✅ Claude restarts, ✅ Windows reboots |
| **macOS** | `~/Library/Application Support/your-app-name` | ✅ Claude restarts, ✅ macOS reboots |
| **Linux** | `~/.local/share/your-app-name` | ✅ Claude restarts, ✅ Linux reboots |

### **Example Locations**

For an MCP server named `database-operations`:
- Windows: `C:\Users\username\AppData\Roaming\database-operations`
- macOS: `~/Library/Application Support/database-operations`
- Linux: `~/.local/share/database-operations`

---

## 📝 Implementation Pattern

### **Step 1: Create Storage Wrapper Class**

Create `src/your_mcp/storage/persistence.py`:

```python
"""
FastMCP 2.13+ Persistent Storage Integration

Uses FastMCP's built-in storage backends for persistent state management.

IMPORTANT: This implementation uses DiskStore to ensure data persists across
Claude Desktop restarts. Storage is saved to platform-appropriate directories:
- Windows: %APPDATA%\your-app-name
- macOS: ~/Library/Application Support/your-app-name
- Linux: ~/.local/share/your-app-name
"""

from typing import Optional, Any, Dict, List
from pathlib import Path
import json
import asyncio
import os
import platform
import time

from fastmcp import FastMCP

# Storage keys (use a prefix for your app)
STORAGE_PREFIX = "yourapp:"
CURRENT_STATE_KEY = f"{STORAGE_PREFIX}current_state"
USER_PREFS_KEY = f"{STORAGE_PREFIX}user_preferences"
CACHE_KEY = f"{STORAGE_PREFIX}cache"


class YourMCPStorage:
    """
    Wrapper around FastMCP storage for persistent state.
    
    Uses DiskStore to ensure data persists across Claude Desktop and OS restarts.
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
        
        # Platform-appropriate storage directory that survives OS restarts
        if use_disk_storage:
            if os.name == "nt":  # Windows
                appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
                self._storage_dir = Path(appdata) / "your-app-name"
            else:  # macOS/Linux
                home = Path.home()
                if platform.system() == "Darwin":  # macOS
                    self._storage_dir = home / "Library" / "Application Support" / "your-app-name"
                else:  # Linux
                    self._storage_dir = home / ".local" / "share" / "your-app-name"
            
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
            if hasattr(self.mcp, "storage") and self.mcp.storage:
                self._storage = self.mcp.storage
                self._initialized = True
                return

            # If we get here, storage is not available - graceful degradation
            self._initialized = False

        except Exception:
            # Storage might not be available yet - that's ok
            self._initialized = False

    # ==================== EXAMPLE METHODS ====================
    
    async def get_current_state(self) -> Optional[str]:
        """Get the current state from persistent storage."""
        await self.initialize()
        if not self._storage:
            return None

        try:
            value = await self._storage.get(CURRENT_STATE_KEY)
            return value if isinstance(value, str) else None
        except Exception:
            return None

    async def set_current_state(self, state: str) -> None:
        """Store the current state persistently."""
        await self.initialize()
        if not self._storage:
            return

        try:
            await self._storage.set(CURRENT_STATE_KEY, state)
        except Exception:
            pass  # Graceful degradation

    async def get_user_preferences(self) -> Dict[str, Any]:
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

    async def set_user_preferences(self, prefs: Dict[str, Any]) -> None:
        """Store user preferences persistently."""
        await self.initialize()
        if not self._storage:
            return

        try:
            await self._storage.set(USER_PREFS_KEY, prefs)
        except Exception:
            pass  # Graceful degradation

    async def cache_data(self, key: str, data: Any, ttl: int = 3600) -> None:
        """Cache data with TTL (default 1 hour)."""
        await self.initialize()
        if not self._storage:
            return

        try:
            cache_key = f"{CACHE_KEY}:{key}"
            await self._storage.set(cache_key, data, ttl=ttl)
        except Exception:
            pass  # Graceful degradation


# Global storage instance (initialized in server startup)
_storage_instance: Optional[YourMCPStorage] = None


def get_storage() -> Optional[YourMCPStorage]:
    """Get the singleton storage instance."""
    return _storage_instance


def set_storage(storage: YourMCPStorage) -> None:
    """Set the singleton storage instance."""
    global _storage_instance
    _storage_instance = storage
```

### **Step 2: Integrate with Server Lifespan**

In `src/your_mcp/server.py`:

```python
from typing import Optional, AsyncContextManager
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from .storage.persistence import YourMCPStorage, set_storage

# Global storage instance
storage: Optional[YourMCPStorage] = None


@asynccontextmanager
async def server_lifespan(mcp_instance: FastMCP) -> AsyncContextManager[None]:
    """FastMCP 2.13 server lifespan for initialization and cleanup."""
    global storage

    # Startup
    try:
        # Initialize storage
        storage_instance = YourMCPStorage(mcp_instance)
        await storage_instance.initialize()
        set_storage(storage_instance)
        storage = storage_instance
        logger.info("FastMCP 2.13 storage initialized")

        # Restore state from persistent storage
        current_state = await storage.get_current_state()
        if current_state:
            logger.info(f"Restored state from storage: {current_state}")

        # ... other initialization ...

        yield  # Server runs here

    finally:
        # Shutdown
        # Save current state
        if storage:
            try:
                await storage.set_current_state("shutdown_clean")
                logger.info("Saved state to storage")
            except Exception as e:
                logger.warning(f"Failed to save state: {e}")


# Initialize FastMCP server with lifespan
mcp = FastMCP("YourMCP", lifespan=server_lifespan)
```

### **Step 3: Use Storage in Tools**

In your tools:

```python
from ...server import storage

@mcp.tool()
async def switch_database(db_name: str) -> Dict[str, Any]:
    """Switch active database and persist the selection."""
    try:
        # ... switch database logic ...
        
        # Persist to storage (survives restarts!)
        if storage:
            await storage.set_current_state(db_name)
        
        return {"success": True, "database": db_name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_preferences() -> Dict[str, Any]:
    """Get user preferences from persistent storage."""
    if storage:
        return await storage.get_user_preferences()
    return {}

@mcp.tool()
async def set_preferences(prefs: Dict[str, Any]) -> Dict[str, Any]:
    """Save user preferences persistently."""
    if storage:
        await storage.set_user_preferences(prefs)
        return {"success": True}
    return {"success": False}
```

---

## 🎨 Common Use Cases

### **1. Current Selection/State**

Perfect for remembering:
- Active database connection
- Current library selection
- Active workspace/project
- Last used configuration

```python
# Save
await storage.set_current_state("production_db")

# Restore on startup
current = await storage.get_current_state()
if current:
    connect_to_database(current)
```

### **2. User Preferences**

Store user settings:
- Default sort order
- Result limits
- Display preferences
- UI settings

```python
# Save preferences
await storage.set_user_preferences({
    "default_limit": 50,
    "sort_order": "desc",
    "show_metadata": True
})

# Load preferences
prefs = await storage.get_user_preferences()
default_limit = prefs.get("default_limit", 20)
```

### **3. Search History**

Remember recent searches (great for database operations):

```python
async def add_search_to_history(self, query: str, filters: Dict[str, Any], max_history: int = 50) -> None:
    """Add a search query to history."""
    history = await self.get_search_history()
    entry = {
        "query": query,
        "filters": filters,
        "timestamp": time.time(),
    }
    history.insert(0, entry)
    history = history[:max_history]
    await self._storage.set(SEARCH_HISTORY_KEY, history)

async def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent search history."""
    value = await self._storage.get(SEARCH_HISTORY_KEY)
    return value[:limit] if isinstance(value, list) else []
```

### **4. Reading Progress / Session State**

Track where users left off:

```python
async def get_progress(self, item_id: str) -> Optional[Dict[str, Any]]:
    """Get progress for a specific item."""
    key = f"{PROGRESS_KEY}:{item_id}"
    return await self._storage.get(key)

async def set_progress(self, item_id: str, progress: Dict[str, Any]) -> None:
    """Save progress for an item."""
    key = f"{PROGRESS_KEY}:{item_id}"
    progress["last_updated"] = time.time()
    await self._storage.set(key, progress)
```

### **5. Caching with TTL**

Cache expensive operations:

```python
async def cache_library_stats(self, library_name: str, stats: Dict[str, Any], ttl: int = 3600) -> None:
    """Cache library statistics with TTL (default 1 hour)."""
    key = f"{CACHE_KEY}:{library_name}"
    await self._storage.set(key, stats, ttl=ttl)

async def get_cached_stats(self, library_name: str) -> Optional[Dict[str, Any]]:
    """Get cached statistics if available and not expired."""
    key = f"{CACHE_KEY}:{library_name}"
    return await self._storage.get(key)
```

---

## ✅ Best Practices

### **1. Always Initialize in Lifespan**

```python
@asynccontextmanager
async def server_lifespan(mcp_instance: FastMCP):
    # ✅ Initialize storage here
    storage_instance = YourMCPStorage(mcp_instance)
    await storage_instance.initialize()
    set_storage(storage_instance)
    
    # ✅ Restore state
    restored_state = await storage_instance.get_current_state()
    
    yield
    
    # ✅ Save state on shutdown
    await storage_instance.set_current_state("clean_shutdown")
```

### **2. Graceful Degradation**

Always handle storage failures gracefully:

```python
async def get_state(self) -> Optional[str]:
    await self.initialize()
    if not self._storage:
        return None  # ✅ Return None, don't crash
    
    try:
        return await self._storage.get(KEY)
    except Exception:
        return None  # ✅ Return None on error
```

### **3. Use Type Hints**

```python
from typing import Optional, Any, Dict, List

async def get_preferences(self) -> Dict[str, Any]:
    """Clear return type."""
    ...
```

### **4. Platform-Aware Directory Setup**

```python
if os.name == "nt":  # Windows
    appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    self._storage_dir = Path(appdata) / "your-app-name"
elif platform.system() == "Darwin":  # macOS
    self._storage_dir = Path.home() / "Library" / "Application Support" / "your-app-name"
else:  # Linux
    self._storage_dir = Path.home() / ".local" / "share" / "your-app-name"
```

### **5. Prefix Your Keys**

```python
STORAGE_PREFIX = "yourapp:"  # ✅ Prevents key collisions
CURRENT_STATE_KEY = f"{STORAGE_PREFIX}current_state"
```

---

## 🧪 Testing

### **Verify Persistence**

1. **Start server** → Set some state:
   ```python
   await storage.set_current_state("test_db")
   ```

2. **Restart Claude Desktop** → Check state:
   ```python
   state = await storage.get_current_state()
   assert state == "test_db"  # ✅ Should persist!
   ```

3. **Restart Windows/OS** → Check again:
   ```python
   state = await storage.get_current_state()
   assert state == "test_db"  # ✅ Should still persist!
   ```

### **Check Storage Location**

```python
import os
from pathlib import Path

# Windows
appdata = os.getenv("APPDATA")
storage_path = Path(appdata) / "your-app-name"
print(f"Storage location: {storage_path}")
# Output: C:\Users\username\AppData\Roaming\your-app-name
```

---

## 🚨 Troubleshooting

### **Storage Not Persisting**

1. **Check DiskStore import**:
   ```python
   from key_value.aio.stores.disk import DiskStore
   ```

2. **Verify directory creation**:
   ```python
   assert self._storage_dir.exists()
   ```

3. **Check initialization**:
   ```python
   assert storage._initialized == True
   ```

### **Storage Returns None**

- Storage might not be initialized yet
- Check that `await storage.initialize()` was called
- Verify `storage._storage` is not None

### **Platform-Specific Issues**

- **Windows**: Ensure `APPDATA` environment variable is set
- **macOS/Linux**: Ensure `~` resolves correctly (`Path.home()`)

---

## 📚 Related Documentation

- **FastMCP 2.13 Release Notes**: [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- **py-key-value-aio**: [PyPI Package](https://pypi.org/project/py-key-value-aio/)
- **This Implementation**: `src/calibre_mcp/storage/persistence.py` (CalibreMCP reference)

---

## 🎯 Summary

This pattern provides:

✅ **True persistence** across Claude Desktop restarts  
✅ **OS-level persistence** across Windows/OS reboots  
✅ **Platform-aware** storage directories  
✅ **Simple API** for key-value operations  
✅ **Production-ready** with graceful degradation  
✅ **Easy to test** and verify  

**Perfect for**: Database operations, library management, configuration persistence, user preferences, search history, reading progress, caching, and any state that should survive restarts.

---

**Last Updated**: 2025-01-XX  
**Pattern Version**: 1.0  
**FastMCP Version**: 2.13+

