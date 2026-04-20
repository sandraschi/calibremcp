# 💻 CalibreMCP Development Documentation

> **Guides, best practices, and development information for CalibreMCP**

---

## 📚 **Documentation Index**

### **1. Portmanteau Tool Refactoring** ✅ COMPLETE

> 📄 **[PORTMANTEAU_REFACTORING_SUMMARY.md](PORTMANTEAU_REFACTORING_SUMMARY.md)**

**Complete portmanteau tool refactoring summary**
- ✅ 18 consolidated tools (57% reduction)
- ✅ Standardized docstrings
- ✅ Migration from individual tools to portmanteau pattern

---

### **2. Phase 3: Docstring Standardization** ✅ COMPLETE

> 📄 **[PHASE_3_DOCSTRING_PLAN.md](PHASE_3_DOCSTRING_PLAN.md)**  
> 📄 **[PHASE_3_DOCSTRING_COMPLETION.md](PHASE_3_DOCSTRING_COMPLETION.md)**

**Docstring standardization for all portmanteau tools**
- ✅ Standardization plan and checklist
- ✅ Completion report with validation results
- ✅ 100% compliance with TOOL_DOCSTRING_STANDARD.md

---

### **3. Portmanteau Tool Migration Plan**

> 📄 **[../mcp-technical/PORTMANTEAU_TOOL_MIGRATION_PLAN.md](../mcp-technical/PORTMANTEAU_TOOL_MIGRATION_PLAN.md)**

**Migration strategy and implementation**
- 📋 Phase-by-phase migration plan
- 📋 Standard portmanteau pattern template
- 📋 Success metrics and benefits

---

## 🎯 **Key Achievements**

### 🎨 **Portmanteau Tool Refactoring** ✅

| Metric | Status |
|--------|--------|
| **Portmanteau Tools** | **18** created and standardized |
| **Tool Reduction** | **57%** (from ~40+ to 18 tools) |
| **Docstring Compliance** | **100%** with TOOL_DOCSTRING_STANDARD.md |
| **Linting Errors** | **Zero** in all portmanteau tools |
| **Backward Compatibility** | ✅ Helper functions maintained |

### 📖 **Documentation Quality** ✅

- ✅ All tools have **PORTMANTEAU PATTERN RATIONALE** sections
- ✅ All tools have **OPERATIONS DETAIL** sections
- ✅ Comprehensive parameter documentation
- ✅ Operation-specific return structures
- ✅ Usage examples for each operation

---

## 🛠️ **Portmanteau Tools (18 total)**

### 📚 **Core Library Management**
1. **`manage_libraries`** - Library operations
2. **`manage_books`** - Book CRUD operations
3. **`query_books`** - Book search and query

### 📝 **Content Management**
4. **`manage_tags`** - Tag management
5. **`manage_authors`** - Author management
6. **`manage_metadata`** - Metadata operations
7. **`manage_files`** - File operations
8. **`manage_comments`** - Comment CRUD operations

### 🔧 **System & Analysis**
9. **`manage_system`** - System tools
10. **`manage_analysis`** - Analysis operations
11. **`analyze_library`** - Library analysis

### 🚀 **Advanced Features**
12. **`manage_bulk_operations`** - Bulk operations
13. **`manage_content_sync`** - Content synchronization
14. **`manage_smart_collections`** - Smart collections

### 👥 **User Management**
15. **`manage_users`** - User management

### 📤 **Import/Export**
16. **`export_books`** - Book export

### 👁️ **Viewer & Specialized**
17. **`manage_viewer`** - Book viewer
18. **`manage_specialized`** - Specialized tools

---

## 📋 **Development Standards**

### 🎨 **Portmanteau Tool Pattern**

> All portmanteau tools follow this standard structure:

```python
@mcp.tool()
async def manage_xxx(
    operation: str,
    # Common parameters
    # Operation-specific parameters (all Optional)
) -> Dict[str, Any]:
    """
    Brief description.

    PORTMANTEAU PATTERN RATIONALE:
    [Explains why operations are consolidated]

    SUPPORTED OPERATIONS:
    - operation1: Description
    - operation2: Description

    OPERATIONS DETAIL:
    [Per-operation descriptions]

    Parameters:
    [All parameters documented]

    Returns:
    [Operation-specific return structures]

    Usage:
    [Usage examples]

    Examples:
    [Code examples]

    Errors:
    [Common errors and solutions]
    """
```

### ✅ **Docstring Requirements**

| Requirement | Status |
|-------------|--------|
| **PORTMANTEAU PATTERN RATIONALE** section | ✅ Required |
| **SUPPORTED OPERATIONS** section | ✅ Required |
| **OPERATIONS DETAIL** section | ✅ Required |
| Comprehensive parameter documentation | ✅ Required |
| Operation-specific return structures | ✅ Required |
| Usage examples | ✅ Required |
| Error handling documentation | ✅ Required |

---

### **4. CI/CD and Pre-commit Hooks** ✅ NEW

> 📄 **[CI_CD_STATUS.md](CI_CD_STATUS.md)**  
> 📄 **[PRE_COMMIT_SETUP.md](PRE_COMMIT_SETUP.md)**

**Modern CI/CD and code quality automation**
- 🔧 Pre-commit hooks configuration (ruff, mypy, bandit)
- ⚙️ GitHub Actions workflows (uv-based)
- 🧪 Automated testing and coverage
- 🔒 Security scanning

---

### **5. Pydantic V2 Migration** ✅ NEW

> 📄 **[PYDANTIC_V2_MIGRATION.md](PYDANTIC_V2_MIGRATION.md)**

**Architectural upgrade to Pydantic V2 (SOTA 2026)**
- 🔧 Migration patterns for field validators
- 🔧 Model configuration updates
- 🔧 Best practices for agentic model schema

---

## 🔗 **Related Documentation**

| Document | Description |
|----------|-------------|
| 📄 [Tool Docstring Standard](../TOOL_DOCSTRING_STANDARD.md) | Docstring format requirements |
| 📄 [Portmanteau Migration Plan](../mcp-technical/PORTMANTEAU_TOOL_MIGRATION_PLAN.md) | Migration strategy |
| 📄 [CI/CD Status](CI_CD_STATUS.md) | CI/CD setup and status |
| 📄 [Pre-commit Setup](PRE_COMMIT_SETUP.md) | Pre-commit hooks guide |
| 📄 [Status Report](../STATUS_REPORT.md) | Current project status |
| 📄 [Main README](../../README.md) | Project overview |

---

> **CalibreMCP Development Documentation**  
> 📍 **Location:** `docs/development/`  
> 🎯 **Focus:** Portmanteau tools, docstring standards, CI/CD, development practices
