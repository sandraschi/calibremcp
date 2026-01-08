# Test Battery Safety Protocol

## Overview

All portmanteau test batteries are designed to **never destroy real books or libraries**. Destructive operations follow a strict CRUD sequence using test libraries.

## Safety Principles

1. **Read Operations**: Always safe - use real libraries
2. **Update Operations**: Safe - only modify metadata (ratings, tags, comments)
3. **Destructive Operations**: Use test libraries that are automatically cleaned up

## Destructive Operations Handling

### Book Deletion (`test_manage_books.py`)

**CRUD Sequence:**
1. **CREATE**: Create temporary test library in system temp directory
2. **ADD**: Add test books to test library using `manage_books(operation="add")`
3. **DELETE**: Perform delete operations on test library books
4. **CLEANUP**: Automatically delete test library and all contents

**Implementation:**
```python
test_lib_manager = TestLibraryManager()
test_lib_name, test_lib_path = test_lib_manager.create_test_library()
# ... perform operations ...
test_lib_manager.cleanup()  # Always called, even on errors
```

### Tag Deletion (`test_manage_tags.py`)

**Safety**: Tags are metadata only - deletion doesn't affect books
- Test tags are created with unique names
- Cleaned up at end of test
- No books are modified or deleted

### Comment Deletion (`test_manage_comments.py`)

**Safety**: Comments are metadata only - deletion doesn't affect books
- Comments are added/updated/deleted on real books
- Only metadata is modified
- No books are deleted

### Bulk Delete (`test_manage_bulk_operations.py`)

**Status**: SKIPPED in tests
- Would require full test library setup
- Skipped to prevent accidental data loss
- Can be enabled with proper test library setup if needed

## Test Library Lifecycle

### Creation
- Created in system temp directory (`tempfile.mkdtemp()`)
- Unique name with timestamp
- Contains `metadata.db` and standard Calibre structure

### Usage
- Switch to test library for destructive operations
- Perform operations safely
- Switch back to original library

### Cleanup
- Always executed (even on errors)
- Removes entire test library directory
- No trace left on system

## Files Modified

- `test_manage_books.py`: Uses test library for delete operations
- `test_manage_tags.py`: Creates test tags, cleans up
- `test_manage_comments.py`: Safe - metadata only
- `test_manage_bulk_operations.py`: Skips destructive operations
- `test_helpers.py`: Provides `TestLibraryManager` class

## Verification

To verify safety:
1. Run test batteries
2. Check that no books are deleted from real libraries
3. Verify test libraries are cleaned up (check temp directory)
4. Confirm test tags/comments are removed

## Best Practices

1. **Always use test libraries** for destructive operations
2. **Always cleanup** test libraries (use try/finally)
3. **Document safety** in test file headers
4. **Skip destructive operations** if test library setup fails
5. **Never delete** from real libraries in tests
