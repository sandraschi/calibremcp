# FastMCP 2.13+ / 2.14.4 Compliance Audit

**Date:** 2025-11-22 (updated 2026-02-10)  
**Status:** COMPLETE  
**Purpose:** Verify `@mcp.tool()` decorators and SOTA features (FastMCP 2.14.4)

---

## Requirements

In FastMCP 2.13+, the `@mcp.tool()` decorator:
- ✅ **MUST** use simple form: `@mcp.tool()` with no parameters
- ✅ **MUST** use function docstrings for tool descriptions (not `description` parameter)
- ❌ **MUST NOT** use `description` parameter (deprecated/invalid)
- ❌ **MUST NOT** use `kwargs` parameter (invalid)
- ✅ **MUST** auto-register tools when modules are imported

---

## Audit Results

### ✅ All `@mcp.tool()` Decorators Verified

**Total Tools Checked:** 18 portmanteau tools + legacy tools

**Pattern Found:** All decorators use the simple form `@mcp.tool()` with no parameters.

**Examples:**
```python
@mcp.tool()
async def manage_books(operation: str, ...) -> Dict[str, Any]:
    """Tool description comes from docstring."""
    ...

@mcp.tool()
async def query_books(operation: str, ...) -> Dict[str, Any]:
    """Tool description comes from docstring."""
    ...
```

### ✅ No Invalid Parameters Found

**Searched for:**
- `@mcp.tool(description=...)` - ❌ Not found
- `@mcp.tool(kwargs=...)` - ❌ Not found
- `@mcp.tool(name=...)` - ❌ Not found
- `@mcp.tool(tags=...)` - ❌ Not found
- Any `@mcp.tool(...)` with parameters - ❌ Not found

**Result:** All `@mcp.tool()` decorators use the simple form with no parameters.

### ✅ Docstring-Based Descriptions

All tools use docstrings for descriptions, which is the FastMCP 2.13+ standard:

```python
@mcp.tool()
async def manage_books(...) -> Dict[str, Any]:
    """
    Comprehensive book management tool for CalibreMCP.
    
    PORTMANTEAU PATTERN RATIONALE:
    ...
    
    SUPPORTED OPERATIONS:
    ...
    """
```

### ✅ Auto-Registration

All tools are auto-registered when modules are imported (FastMCP 2.13+ behavior):

```python
# In tools/__init__.py
from .book_management import manage_books  # noqa: F401
# Tool is automatically registered when imported
```

---

## Portmanteau Tools Verified

All 18 portmanteau tools verified:

1. ✅ `manage_books` - `@mcp.tool()` (no parameters)
2. ✅ `query_books` - `@mcp.tool()` (no parameters)
3. ✅ `manage_libraries` - `@mcp.tool()` (no parameters)
4. ✅ `manage_tags` - `@mcp.tool()` (no parameters)
5. ✅ `manage_authors` - `@mcp.tool()` (no parameters)
6. ✅ `manage_metadata` - `@mcp.tool()` (no parameters)
7. ✅ `manage_files` - `@mcp.tool()` (no parameters)
8. ✅ `manage_system` - `@mcp.tool()` (no parameters)
9. ✅ `manage_analysis` - `@mcp.tool()` (no parameters)
10. ✅ `analyze_library` - `@mcp.tool()` (no parameters)
11. ✅ `manage_bulk_operations` - `@mcp.tool()` (no parameters)
12. ✅ `manage_content_sync` - `@mcp.tool()` (no parameters)
13. ✅ `manage_smart_collections` - `@mcp.tool()` (no parameters)
14. ✅ `manage_users` - `@mcp.tool()` (no parameters)
15. ✅ `export_books` - `@mcp.tool()` (no parameters)
16. ✅ `manage_viewer` - `@mcp.tool()` (no parameters)
17. ✅ `manage_viewer` - `@mcp.tool()` (no parameters)
18. ✅ `manage_specialized` - `@mcp.tool()` (no parameters)
19. ✅ `manage_comments` - `@mcp.tool()` (no parameters)

---

## Legacy Tools

**Status:** Legacy tools have `@mcp.tool()` decorators removed (as intended):

- `export_books_csv` - Decorator removed, use `export_books` portmanteau
- `export_books_json` - Decorator removed, use `export_books` portmanteau
- `export_books_html` - Decorator removed, use `export_books` portmanteau
- `export_books_pandoc` - Decorator removed, use `export_books` portmanteau
- Individual tag tools - Decorators removed, use `manage_tags` portmanteau
- Individual author tools - Decorators removed, use `manage_authors` portmanteau
- System helper tools - Decorators removed, use `manage_system` portmanteau

---

## FastMCP 2.13+ Best Practices

### ✅ Correct Pattern

```python
from ...server import mcp

@mcp.tool()
async def tool_name(param1: str, param2: int = 0) -> Dict[str, Any]:
    """
    Tool description from docstring.
    
    This is the FastMCP 2.13+ way - descriptions come from docstrings,
    not from decorator parameters.
    """
    try:
        # Tool implementation
        ...
    except Exception as e:
        return handle_tool_error(...)
```

### ❌ Incorrect Patterns (NOT USED)

```python
# ❌ WRONG - Don't use description parameter
@mcp.tool(description="Tool description")
async def tool_name(...):
    ...

# ❌ WRONG - Don't use kwargs
@mcp.tool(kwargs={...})
async def tool_name(...):
    ...

# ❌ WRONG - Don't use name parameter
@mcp.tool(name="custom_name")
async def tool_name(...):
    ...
```

---

## Verification Commands

```bash
# Check for decorators with parameters
grep -r "@mcp\.tool(" src/calibre_mcp/tools/ | grep -v "@mcp\.tool()"

# Check for invalid parameters
grep -r "@mcp\.tool(.*description" src/calibre_mcp/tools/
grep -r "@mcp\.tool(.*kwargs" src/calibre_mcp/tools/
```

**Results:** All checks pass - no invalid parameters found.

---

## Summary

**Status:** ✅ FULLY COMPLIANT

- ✅ All `@mcp.tool()` decorators use simple form with no parameters
- ✅ All tool descriptions come from docstrings
- ✅ No invalid parameters (`description`, `kwargs`, etc.) used
- ✅ All tools auto-register on import (FastMCP 2.13+ behavior)
- ✅ Legacy tools properly deprecated (decorators removed)

**Compliance:** 100% FastMCP 2.13+ compliant

---

*FastMCP 2.13+ Compliance Audit*  
*Last Updated: 2025-11-22*  
*Status: ✅ COMPLETE*

