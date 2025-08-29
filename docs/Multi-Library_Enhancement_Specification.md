# Multi-Library Enhancement Specification
*Created: 2025-08-20*

## Overview
Enhancement plan to transform calibre-mcp from single hardcoded library support to dynamic multi-library management with automatic discovery and switching capabilities.

## Current Implementation Analysis

### Current State
- **Single Library**: Hardcoded to `L:\Multimedia Files\Written Word\Calibre-Bibliothek IT`
- **Static Connection**: Environment variable `CALIBRE_LIBRARY_PATH` points to one library
- **Database Access**: Direct SQLite connection to single `metadata.db`
- **Tools Available**: 23 tools but all operate on current library only

### File Structure
```
L:\Multimedia Files\Written Word\
├── Calibre-Bibliothek IT\          # Currently connected
│   ├── metadata.db                 # SQLite database
│   ├── Author 1\
│   │   └── Book Title (book_id)\
│   └── Author 2\
├── Main Library\                   # Available but not accessible
│   ├── metadata.db
│   └── Authors...
├── Japanese Books\                 # Available but not accessible  
│   ├── metadata.db
│   └── Authors...
└── Other Libraries...
```

## Enhancement Requirements

### 1. Library Discovery System

#### Enhanced `list_libraries()` Tool
**Current Implementation:**
```python
async def list_libraries() -> LibraryListResponse:
    # Returns hardcoded single library from environment
```

**Required Enhancement:**
```python
async def list_libraries() -> LibraryListResponse:
    # Scan L:\Multimedia Files\Written Word\ for subdirectories
    # Check each subdir for metadata.db existence
    # Return comprehensive library list with statistics
```

**Implementation Details:**
- Scan base directory: `L:\Multimedia Files\Written Word\`
- Validate library candidates: Check for `metadata.db` file
- Extract library statistics: Book count, size, last modified
- Return structured library information

#### Library Discovery Logic
```python
def discover_libraries(base_path: str) -> List[LibraryInfo]:
    libraries = []
    base_dir = Path(base_path)
    
    for subdir in base_dir.iterdir():
        if subdir.is_dir():
            metadata_db = subdir / "metadata.db"
            if metadata_db.exists():
                # Extract library statistics
                stats = extract_library_stats(metadata_db)
                libraries.append(LibraryInfo(
                    name=subdir.name,
                    display_name=format_display_name(subdir.name),
                    path=str(subdir),
                    total_books=stats.book_count,
                    size_mb=stats.size_mb,
                    last_updated=stats.last_modified,
                    is_current=(subdir.name == current_library)
                ))
    
    return libraries
```

### 2. Dynamic Library Switching

#### Enhanced `switch_library()` Tool
**Current Implementation:**
```python
async def switch_library(library_name: str):
    # Basic library name validation
    # Updates global current_library variable
```

**Required Enhancement:**
```python
async def switch_library(library_name: str):
    # Validate library exists in discovered libraries
    # Close existing database connections
    # Update library path configuration
    # Reinitialize database connections
    # Update all tool contexts
    # Verify successful switch
```

#### Database Connection Management
```python
class LibraryConnectionManager:
    def __init__(self):
        self.connections: Dict[str, sqlite3.Connection] = {}
        self.current_library: Optional[str] = None
    
    def switch_library(self, library_name: str, library_path: str):
        # Close existing connections
        self.close_current_connection()
        
        # Establish new connection
        db_path = Path(library_path) / "metadata.db"
        self.connections[library_name] = sqlite3.connect(str(db_path))
        self.current_library = library_name
    
    def get_current_connection(self) -> sqlite3.Connection:
        if self.current_library:
            return self.connections[self.current_library]
        raise ValueError("No active library connection")
```

### 3. New Tool: `load_library()`

#### Purpose
Initialize connection to specific library without switching global context.

#### Implementation
```python
@mcp.tool()
async def load_library(library_path: str) -> Dict[str, Any]:
    """
    Load and validate a specific Calibre library.
    
    Args:
        library_path: Full path to library directory
        
    Returns:
        Library validation and connection status
    """
    try:
        lib_path = Path(library_path)
        metadata_db = lib_path / "metadata.db"
        
        if not lib_path.exists():
            return {"success": False, "error": "Library path does not exist"}
        
        if not metadata_db.exists():
            return {"success": False, "error": "metadata.db not found"}
        
        # Test database connection
        conn = sqlite3.connect(str(metadata_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        book_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "success": True,
            "library_path": str(lib_path),
            "book_count": book_count,
            "database_accessible": True
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 4. Database Handling Improvements

#### Current SQLite Access
```python
async def execute_sql_query(library_path: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    # Direct connection per query
    # No connection pooling
    # Path hardcoded from environment
```

#### Enhanced Database Layer
```python
class CalibreDatabase:
    def __init__(self, library_path: str):
        self.library_path = Path(library_path)
        self.db_path = self.library_path / "metadata.db"
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self):
        if not self.db_path.exists():
            raise CalibreAPIError(f"Database not found: {self.db_path}")
        
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
```

#### Global Database Manager
```python
class CalibreMultiLibraryManager:
    def __init__(self):
        self.databases: Dict[str, CalibreDatabase] = {}
        self.current_library: Optional[str] = None
    
    def discover_libraries(self, base_path: str) -> List[LibraryInfo]:
        # Implementation for library discovery
        pass
    
    def add_library(self, name: str, path: str):
        self.databases[name] = CalibreDatabase(path)
    
    def switch_library(self, name: str):
        if name not in self.databases:
            raise ValueError(f"Library '{name}' not found")
        
        # Disconnect current
        if self.current_library and self.current_library in self.databases:
            self.databases[self.current_library].disconnect()
        
        # Connect new
        self.databases[name].connect()
        self.current_library = name
    
    def get_current_db(self) -> CalibreDatabase:
        if not self.current_library:
            raise ValueError("No active library")
        return self.databases[self.current_library]
```

### 5. Configuration Updates

#### Environment Variables
```bash
# Current
CALIBRE_LIBRARY_PATH=L:\Multimedia Files\Written Word\Calibre-Bibliothek IT

# Enhanced
CALIBRE_BASE_PATH=L:\Multimedia Files\Written Word
CALIBRE_DEFAULT_LIBRARY=Calibre-Bibliothek IT
CALIBRE_AUTO_DISCOVER=true
```

#### Configuration File Enhancement
```yaml
# config/calibre_config.yaml
libraries:
  base_path: "L:\\Multimedia Files\\Written Word"
  auto_discover: true
  default_library: "Calibre-Bibliothek IT"
  
  # Explicit library definitions (optional override)
  explicit_libraries:
    main:
      name: "Main Library"
      path: "L:\\Multimedia Files\\Written Word\\Main Library"
      description: "General fiction and non-fiction"
    
    it:
      name: "IT & Programming"
      path: "L:\\Multimedia Files\\Written Word\\Calibre-Bibliothek IT"
      description: "Technical books and programming resources"
    
    japanese:
      name: "Japanese Collection"
      path: "L:\\Multimedia Files\\Written Word\\Japanese Books"
      description: "Manga, light novels, and language learning"
```

### 6. Tool Context Awareness

#### Update All Existing Tools
Every tool should be aware of the current library context:

```python
@mcp.tool()
async def list_books(
    query: Optional[str] = None,
    limit: int = 50,
    sort: str = "title",
    library: Optional[str] = None  # NEW: Optional library override
) -> LibrarySearchResponse:
    """
    Enhanced with library context awareness
    """
    target_library = library or current_library
    db = library_manager.get_library_db(target_library)
    # ... rest of implementation
```

#### Library-Specific Operations
```python
@mcp.tool()
async def get_library_stats(library_name: Optional[str] = None) -> LibraryStatsResponse:
    """
    Enhanced to work with any discovered library
    """
    target_library = library_name or current_library
    
    if target_library not in library_manager.get_available_libraries():
        raise ValueError(f"Library '{target_library}' not found")
    
    db = library_manager.get_library_db(target_library)
    # Generate statistics from this specific database
```

## Implementation Plan

### Phase 1: Core Infrastructure
1. **Library Discovery System**
   - Implement `discover_libraries()` function
   - Enhance `list_libraries()` tool
   - Add library validation logic

2. **Database Connection Management**
   - Create `CalibreDatabase` class
   - Implement `CalibreMultiLibraryManager`
   - Add connection pooling and error handling

### Phase 2: Dynamic Switching
1. **Enhanced Library Switching**
   - Implement robust `switch_library()` 
   - Add `load_library()` tool
   - Ensure proper connection cleanup

2. **Configuration Updates**
   - Update environment variable handling
   - Enhance configuration file support
   - Add library-specific settings

### Phase 3: Tool Enhancement
1. **Context Awareness**
   - Add library parameter to all tools
   - Update database queries to use active connection
   - Ensure cross-library operations work correctly

2. **Testing & Validation**
   - Test library discovery across different structures
   - Validate database integrity checks
   - Ensure proper error handling for missing libraries

### Phase 4: Advanced Features
1. **Cross-Library Operations**
   - Enhance `cross_library_search()` to use real multi-library access
   - Implement library-aware duplicate detection
   - Add library migration tools

2. **Performance Optimization**
   - Implement connection caching
   - Add parallel library scanning
   - Optimize metadata.db queries

## Testing Strategy

### Unit Tests
- Library discovery with various directory structures
- Database connection management
- Library switching operations
- Error handling for missing/corrupted databases

### Integration Tests
- Multi-library search operations
- Cross-library duplicate detection
- Library-specific statistics generation
- Configuration file parsing

### Performance Tests
- Large library scanning (1000+ books)
- Concurrent library access
- Memory usage with multiple connections
- Database query optimization

## Migration Considerations

### Backward Compatibility
- Maintain single-library mode for existing configurations
- Graceful fallback when no multiple libraries detected
- Environment variable compatibility

### Data Safety
- No metadata.db modifications during discovery
- Read-only access for library scanning
- Backup recommendations before major operations

### User Experience
- Clear error messages for library issues
- Progress indicators for library discovery
- Intuitive library naming and organization

## Success Criteria

1. **Discovery**: Automatically find all Calibre libraries in base directory
2. **Switching**: Seamlessly switch between libraries without restart
3. **Performance**: Library operations complete in <2 seconds
4. **Reliability**: Robust error handling for database issues
5. **Compatibility**: Works with existing single-library setups

This enhancement will transform calibre-mcp from a single-library tool into a comprehensive multi-library management system, providing Sandra with efficient access to her entire collection across all specialized libraries.
