# Portmanteau Tool Migration Plan

**Last Updated**: 2025-11-02  
**Status**: In Progress  
**Priority**: High - Reduces tool count and improves consistency

## Overview

This document outlines the migration plan to consolidate related tools into portmanteau tools following the standard pattern defined in `.cursorrules`. Portmanteau tools use a single tool with an `operation` parameter to handle multiple related operations, reducing tool count and improving user experience.

## Current State Analysis

### Tools Using Old MCPTool Pattern (Portmanteau Internally)

These tools already use portmanteau pattern internally via `_run(action, **kwargs)` but need migration to FastMCP 2.13+ `@mcp.tool()` pattern:

1. **SmartCollectionsTool** (`advanced_features/smart_collections.py`)
   - Operations: `create`, `get`, `update`, `delete`, `list`, `query`
   - Status: ✅ Already portmanteau (needs migration)

2. **UserManagerTool** (`user_management/user_manager.py`)
   - Operations: `create_user`, `update_user`, `delete_user`, `login`, `verify_token`, `list_users`, `get_user`
   - Status: ✅ Already portmanteau (needs migration)

3. **ContentSyncTool** (`advanced_features/content_sync.py`)
   - Operations: Various sync operations
   - Status: ✅ Already portmanteau (needs migration)

4. **AdvancedSearchTool** (`advanced_features/advanced_search.py`)
   - Operations: Various search operations
   - Status: ✅ Already portmanteau (needs migration)

5. **UpdateMetadataTool** (`metadata/update_metadata.py`)
   - Operations: Various metadata update operations
   - Status: ✅ Already portmanteau (needs migration)

6. **LibraryStatsTool** (`library_operations/library_stats.py`)
   - Operations: Various stats operations
   - Status: ✅ Already portmanteau (needs migration)

7. **AIEnhancementsTool** (`advanced_features/ai_enhancements.py`)
   - Operations: Various AI operations
   - Status: ✅ Already portmanteau (needs migration)

8. **BulkOperationsTool** (`advanced_features/bulk_operations.py`)
   - Operations: Various bulk operations
   - Status: ✅ Already portmanteau (needs migration)

9. **ReadingAnalyticsTool** (`advanced_features/reading_analytics.py`)
   - Operations: Various analytics operations
   - Status: ✅ Already portmanteau (needs migration)

10. **SocialFeaturesTool** (`advanced_features/social_features.py`)
    - Operations: Various social operations
    - Status: ✅ Already portmanteau (needs migration)

11. **ExportLibraryTool** (`import_export/export_library.py`)
    - Operations: Various export operations
    - Status: ✅ Already portmanteau (needs migration)

12. **AddBooksTool** (`book_management/add_books.py`)
    - Operations: Various add operations
    - Status: ✅ Already portmanteau (needs migration)

### Separate Tools That Should Be Consolidated

#### High Priority Consolidations

1. **Library Management Tools** → `manage_libraries(operation, ...)`
   - `list_libraries()` → `operation="list"`
   - `switch_library(library_name)` → `operation="switch", library_name=...`
   - `get_library_stats(library_name)` → `operation="stats", library_name=...`
   - `cross_library_search(...)` → `operation="search", ...`
   - **File**: `tools/library/library_management.py`
   - **Impact**: Reduces 4 tools to 1

2. **Book Management Tools** → `manage_books(operation, ...)`
   - `add_book(...)` → `operation="add", ...`
   - `get_book(book_id)` → `operation="get", book_id=...`
   - `update_book(...)` → `operation="update", ...`
   - `delete_book(book_id)` → `operation="delete", book_id=...`
   - **Files**: `tools/book_management/add_book.py`, `get_book.py`, `update_book.py`, `delete_book.py`
   - **Impact**: Reduces 4 tools to 1

3. **Export Tools** → `export_books(operation, ...)`
   - `export_books_csv(...)` → `operation="csv", ...`
   - `export_books_json(...)` → `operation="json", ...`
   - `export_books_html(...)` → `operation="html", ...`
   - `export_books_pandoc(...)` → `operation="pandoc", ...`
   - **File**: `tools/import_export/export_books.py`
   - **Impact**: Reduces 4 tools to 1 (Note: Already has ExportLibraryTool but separate functions)

#### Lower Priority (Keep Separate or Evaluate)

- `search_books()` - Core functionality, may stay separate
- `get_book_details()` - Core functionality, may stay separate
- `list_books()` - Core functionality, may stay separate
- `test_calibre_connection()` - Diagnostic tool, keep separate
- `get_recent_books()` - Could be part of search portmanteau
- `get_books_by_series()` - Could be part of search portmanteau
- `get_books_by_author()` - Could be part of search portmanteau

## Migration Strategy

### Phase 1: Documentation and Planning ✅
- [x] Create migration plan document
- [x] Analyze current tool structure
- [x] Identify consolidation candidates

### Phase 2: High-Impact Consolidations
- [ ] Consolidate library management tools → `manage_libraries()`
- [ ] Consolidate book management tools → `manage_books()`
- [ ] Consolidate export tools → `export_books()`

### Phase 3: Migrate Old Portmanteau Tools to FastMCP 2.13+
- [ ] Migrate SmartCollectionsTool
- [ ] Migrate UserManagerTool
- [ ] Migrate ContentSyncTool
- [ ] Migrate AdvancedSearchTool
- [ ] Migrate UpdateMetadataTool
- [ ] Migrate remaining MCPTool classes

### Phase 4: Testing and Validation
- [ ] Update all tests
- [ ] Verify tool registration
- [ ] Test all operations work correctly
- [ ] Update documentation

### Phase 5: Cleanup
- [ ] Remove old MCPTool base class usage
- [ ] Remove compat.py shim
- [ ] Update `.cursorrules` with lessons learned

## Standard Portmanteau Pattern

### Template

```python
@mcp.tool()
async def tool_name(
    operation: str,  # "operation1", "operation2", "operation3"
    # ... shared parameters
    # ... operation-specific parameters (all Optional)
) -> Dict[str, Any]:
    """
    Brief description covering all operations.
    
    Operations:
    - operation1: Description of first operation
    - operation2: Description of second operation
    - operation3: Description of third operation
    
    Prerequisites:
        - Requirement 1
        - Requirement 2
    
    Parameters:
        operation: The operation to perform. Must be one of: "operation1", "operation2", "operation3"
            - operation1: Description of what this does
            - operation2: Description of what this does
            - operation3: Description of what this does
        
        param1: Description (required for operation1)
        param2: Description (required for operation2)
        param3: Description (optional)
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - data: Operation-specific data
            - error: Error message if success is False
    
    Examples:
        # Operation 1
        result = await tool_name(operation="operation1", param1="value")
        
        # Operation 2
        result = await tool_name(operation="operation2", param2="value")
    
    Errors:
        - Invalid operation: Use one of the supported operations
        - Missing parameters: Provide required parameters for the operation
    """
    if operation == "operation1":
        return await _handle_operation1(...)
    elif operation == "operation2":
        return await _handle_operation2(...)
    elif operation == "operation3":
        return await _handle_operation3(...)
    else:
        return {
            "success": False,
            "error": f"Invalid operation: {operation}. Must be one of: operation1, operation2, operation3",
            "suggestions": ["Use 'operation1' for...", "Use 'operation2' for..."]
        }
```

## Benefits of Migration

### Tool Count Reduction
- **Before**: ~40+ individual tools
- **After**: ~20-25 portmanteau tools
- **Reduction**: ~40-50% fewer tools

### Improved UX
- Consistent interface across related operations
- Single place to find all operations in a domain
- Better error messages with operation-specific guidance

### Easier Maintenance
- Related operations grouped together
- Shared code and validation
- Single test file per portmanteau tool

## Risks and Mitigation

### Risk: Breaking Changes
**Mitigation**: 
- Keep old tools working during migration
- Add deprecation warnings
- Update all tests before removing old tools

### Risk: Complex Tool Signatures
**Mitigation**:
- Use Pydantic models for complex parameters
- Provide clear documentation
- Use operation-specific parameter validation

### Risk: Backwards Compatibility
**Mitigation**:
- Maintain compatibility layer during transition
- Document migration path for users
- Version the API if needed

## Success Metrics

- [ ] Tool count reduced by 40%+
- [ ] All operations work correctly
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Zero breaking changes for core operations
- [ ] Improved AI tool selection accuracy

## References

- `.cursorrules` - Portmanteau Tool Rules section
- `docs/mcp-technical/TENACITY_RETRY_PATTERN.md` - Retry pattern documentation
- FastMCP 2.13+ Documentation

