# Phase 3: Docstring Standardization Plan

**Status:** ✅ COMPLETE  
**Date:** 2025-11-22  
**Completion Date:** 2025-11-22  
**Goal:** Standardize all portmanteau tool docstrings according to TOOL_DOCSTRING_STANDARD.md

---

## Overview

Phase 3 focuses on ensuring all portmanteau tools have comprehensive, standardized docstrings that follow the established TOOL_DOCSTRING_STANDARD.md. This improves tool discoverability, usability, and maintainability.

## Objectives

1. **Audit** all portmanteau tools for docstring compliance
2. **Standardize** docstrings to match TOOL_DOCSTRING_STANDARD.md format
3. **Enhance** existing docstrings with missing sections
4. **Validate** docstring quality and completeness
5. **Document** any portmanteau-specific docstring patterns

---

## Portmanteau Tools Inventory

### Completed Portmanteau Tools

1. ✅ **manage_libraries** (`tools/library/manage_libraries.py`)
   - Operations: list, switch, stats, search
   - Status: Needs docstring review

2. ✅ **manage_books** (`tools/book_management/manage_books.py`)
   - Operations: add, get, update, delete
   - Status: Needs docstring review

3. ✅ **query_books** (`tools/book_management/query_books.py`)
   - Operations: search, list, by_author, by_series
   - Status: Needs docstring review

4. ✅ **manage_tags** (`tools/tags/manage_tags.py`)
   - Operations: list, get, create, update, delete, find_duplicates, merge, get_unused, delete_unused, stats
   - Status: Needs docstring review

5. ✅ **manage_authors** (`tools/authors/manage_authors.py`)
   - Operations: list, get, get_books, stats, by_letter
   - Status: Needs docstring review

6. ✅ **manage_metadata** (`tools/metadata/manage_metadata.py`)
   - Operations: update, auto_organize_tags, fix_issues
   - Status: Needs docstring review

7. ✅ **manage_files** (`tools/files/manage_files.py`)
   - Operations: convert, download, bulk_format
   - Status: Needs docstring review

8. ✅ **manage_system** (`tools/system/manage_system.py`)
   - Operations: help, status, tool_help, list_tools, hello_world, health_check
   - Status: Needs docstring review

9. ✅ **manage_analysis** (`tools/analysis/manage_analysis.py`)
   - Operations: health, duplicates, series, tags, reading_stats, unread_priority
   - Status: Needs docstring review

10. ✅ **manage_bulk_operations** (`tools/advanced_features/manage_bulk_operations.py`)
    - Operations: update_metadata, export, delete, convert
    - Status: Needs docstring review

11. ✅ **manage_content_sync** (`tools/advanced_features/manage_content_sync.py`)
    - Operations: register_device, update_device, get_device, start_sync, get_status, cancel_sync
    - Status: Needs docstring review

12. ✅ **manage_smart_collections** (`tools/advanced_features/manage_smart_collections.py`)
    - Operations: create, get, update, delete, list, query
    - Status: Needs docstring review

13. ✅ **manage_users** (`tools/user_management/manage_users.py`)
    - Operations: create, update, delete, list, get, login, verify_token
    - Status: Needs docstring review

14. ✅ **export_books** (`tools/import_export/export_books_portmanteau.py`)
    - Operations: csv, json, html, pandoc
    - Status: Needs docstring review

15. ✅ **manage_viewer** (`tools/viewer/manage_viewer.py`) - NEW
    - Operations: open, get_page, get_metadata, get_state, update_state, close, open_file
    - Status: Needs docstring review

16. ✅ **manage_specialized** (`tools/specialized/manage_specialized.py`) - NEW
    - Operations: japanese_organizer, it_curator, reading_recommendations
    - Status: Needs docstring review

---

## Docstring Standard Checklist

For each portmanteau tool, verify:

### Required Sections

- [ ] **Brief Description** (1-2 sentences)
- [ ] **PORTMANTEAU PATTERN RATIONALE** (explains why operations are consolidated)
- [ ] **SUPPORTED OPERATIONS** (list all operations)
- [ ] **OPERATIONS DETAIL** (detailed description of each operation)
- [ ] **Prerequisites** (what's needed before using)
- [ ] **Parameters** (all parameters with types, defaults, constraints)
- [ ] **Returns** (operation-specific return structures)
- [ ] **Usage** (when and how to use)
- [ ] **Examples** (at least 3 examples per operation)
- [ ] **Errors** (common errors and solutions)
- [ ] **See Also** (related tools)

### Portmanteau-Specific Requirements

- [ ] **Operation parameter** clearly documented with all valid values
- [ ] **Operation-specific parameters** clearly marked (which params apply to which operations)
- [ ] **Operation-specific returns** documented (different operations return different structures)
- [ ] **Examples for each operation** (at least one example per operation)
- [ ] **Error handling per operation** (operation-specific error scenarios)

---

## Standardization Tasks

### Task 1: Audit Current State

**Goal:** Identify gaps in existing docstrings

**Steps:**
1. Review each portmanteau tool's docstring
2. Compare against TOOL_DOCSTRING_STANDARD.md
3. Create checklist for each tool
4. Document missing sections
5. Identify inconsistencies

**Output:** Audit report with per-tool checklist

### Task 2: Create Portmanteau Docstring Template

**Goal:** Standardize portmanteau-specific docstring format

**Steps:**
1. Extract common patterns from existing portmanteau docstrings
2. Create template that includes:
   - PORTMANTEAU PATTERN RATIONALE section
   - OPERATIONS DETAIL section with per-operation descriptions
   - Operation-specific parameter documentation
   - Operation-specific return structures
3. Document template in TOOL_DOCSTRING_STANDARD.md

**Output:** Enhanced docstring template for portmanteau tools

### Task 3: Standardize Each Tool

**Goal:** Update all portmanteau tools to match standard

**Priority Order:**
1. High-traffic tools (query_books, manage_books, manage_libraries)
2. Core functionality (manage_tags, manage_authors, manage_metadata)
3. Advanced features (manage_bulk_operations, manage_content_sync)
4. Specialized tools (manage_viewer, manage_specialized, manage_system)

**Steps per tool:**
1. Review current docstring
2. Add missing sections
3. Standardize format
4. Enhance examples
5. Add operation-specific documentation
6. Validate against checklist

**Output:** Updated docstrings for all tools

### Task 4: Validate and Test

**Goal:** Ensure docstrings are accurate and helpful

**Steps:**
1. Review docstrings for accuracy
2. Test examples are runnable
3. Verify parameter documentation matches implementation
4. Check return structures match actual returns
5. Validate no triple quotes inside docstrings
6. Ensure all operations are documented

**Output:** Validation report

### Task 5: Documentation Updates

**Goal:** Update related documentation

**Steps:**
1. Update TOOL_DOCSTRING_STANDARD.md with portmanteau patterns
2. Create portmanteau docstring examples
3. Update API documentation
4. Update user guides

**Output:** Updated documentation

---

## Portmanteau Docstring Template

```python
@mcp.tool()
async def manage_xxx(
    operation: str,
    # Common parameters
    param1: Optional[str] = None,
    # Operation-specific parameters
    param2: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Brief description of what this portmanteau tool does.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating N separate tools (one per operation), this tool consolidates related
    operations into a single interface. This design:
    - Prevents tool explosion (N tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with [domain] tasks
    - Enables consistent interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - operation1: Description of operation1
    - operation2: Description of operation2
    - operation3: Description of operation3

    OPERATIONS DETAIL:

    operation1: Detailed description
    - What it does
    - Parameters: param1 (required), param2 (optional)
    - Returns: Structure description

    operation2: Detailed description
    - What it does
    - Parameters: param1 (required), param3 (optional)
    - Returns: Structure description

    Prerequisites:
        - Prerequisite 1
        - Prerequisite 2

    Parameters:
        operation: The operation to perform. Must be one of: "operation1", "operation2", "operation3"

        param1: Description (required for operation1, optional for operation2)
            - Additional details
            - Valid values or constraints

        param2: Description (only used for operation1, default: value)
            - Additional details

        param3: Description (only used for operation2)
            - Additional details

    Returns:
        Dictionary containing operation-specific results:

        For operation="operation1":
            {
                "success": bool - Whether operation succeeded
                "field1": type - Description
                "field2": type - Description
            }

        For operation="operation2":
            {
                "success": bool - Whether operation succeeded
                "field3": type - Description
            }

    Usage:
        # Operation1 example
        result = await manage_xxx(operation="operation1", param1="value")

        # Operation2 example
        result = await manage_xxx(operation="operation2", param1="value", param3=42)

    Examples:
        # Operation1 basic usage
        result = await manage_xxx(operation="operation1", param1="value")
        # Returns: {"success": True, "field1": "...", "field2": "..."}

        # Operation2 with all parameters
        result = await manage_xxx(
            operation="operation2",
            param1="value",
            param3=42
        )
        # Returns: {"success": True, "field3": "..."}

        # Error handling
        result = await manage_xxx(operation="invalid_operation")
        if not result.get("success"):
            print(f"Error: {result.get('error')}")
        # Returns: {"success": False, "error": "Invalid operation: ..."}

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "operation1", "operation2", "operation3"
        - Missing parameter: Provide required parameter for operation
        - Invalid value: Check parameter constraints

    See Also:
        - related_tool(): For related functionality
        - another_tool(): For alternative approach
    """
    # Implementation
    pass
```

---

## Success Criteria

- [ ] All 16 portmanteau tools have standardized docstrings
- [ ] All docstrings pass validation checklist
- [ ] All operations are documented with examples
- [ ] Portmanteau-specific patterns are documented
- [ ] Examples are runnable and accurate
- [ ] No triple quotes inside docstrings
- [ ] Documentation updated with portmanteau patterns

---

## Timeline Estimate

- **Task 1 (Audit):** 2-3 hours
- **Task 2 (Template):** 1-2 hours
- **Task 3 (Standardize):** 8-12 hours (30-45 min per tool)
- **Task 4 (Validate):** 2-3 hours
- **Task 5 (Documentation):** 1-2 hours

**Total:** 14-22 hours

---

## Notes

- Portmanteau tools require more comprehensive docstrings than single-operation tools
- Operation-specific parameters and returns need clear documentation
- Examples should cover each operation, not just one
- Error handling should be operation-specific where applicable
- PORTMANTEAU PATTERN RATIONALE helps users understand the design decision

---

*Phase 3 Docstring Standardization Plan*  
*Part of CalibreMCP Portmanteau Tool Refactoring*  
*See also: TOOL_DOCSTRING_STANDARD.md*

