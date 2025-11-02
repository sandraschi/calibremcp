# MCP Server Development Workflow

**Standardized workflow for adding tools and verifying MCP server functionality**

---

## 🎯 Workflow Overview

When you say **"add tool to do x"**, follow this standardized process:

1. **Add the tool** following all standards
2. **Run ruff iteratively** - fix linting issues, run again until zero errors
3. **Format code** - run `ruff format .`
4. **Run pytest** - ensure tests pass
5. **Run restart script** - verify server loads in Claude

---

## 📋 Step-by-Step Workflow

### 1. Add Tool Following Standards

- ✅ Follow existing tool patterns (FastMCP 2.12 `@mcp.tool()` decorator)
- ✅ Add proper type hints
- ✅ Include comprehensive docstrings
- ✅ Handle errors gracefully
- ✅ Add to appropriate tool module/package

**Standards Reference:**
- Modern Python stack (ruff, uv, pytest)
- Type hints required
- Async MCP tools
- Error handling patterns

### 2. Run Ruff (Linting) - Iterative Process

**Important:** Run ruff check iteratively until all errors are fixed.

```bash
# Step 1: Check for issues
uv run ruff check .

# Step 2: Fix any errors reported (manual fixes or auto-fix)
uv run ruff check . --fix  # Auto-fix what can be fixed automatically

# Step 3: Run ruff check again to verify
uv run ruff check .

# Step 4: Repeat steps 2-3 until zero errors remain
# Only proceed when: "All checks passed!" (exit code 0)
```

**Must have zero errors before proceeding!**

### 3. Format Code

```bash
# Format all code
uv run ruff format .
```

**Note:** Formatting is separate from linting. Format after all linting errors are fixed.

### 4. Run Pytest

```bash
# Run all tests
uv run python -m pytest -v

# Run specific test file
uv run python -m pytest tests/test_specific.py -v

# With coverage
uv run python -m pytest -v --cov
```

**All tests must pass!**

### 5. Verify Server Loads in Claude

```powershell
# Full restart + check (recommended after code changes)
.\scripts\restart_claude_and_check_mcp.ps1

# Or just check logs (Claude already running)
.\scripts\restart_claude_and_check_mcp.ps1 -NoRestart
```

**What it does:**
- ✅ Pre-checks server will load (optional, recommended)
- ✅ Stops Claude Desktop (using `taskkill`)
- ✅ Restarts Claude Desktop
- ✅ Monitors logs for successful MCP server startup
- ✅ Reports success/failure with clear messages

---

## 🔧 SOTA Scripts

**State Of The Art (SOTA) scripts** are maintained in the central docs repo:

**Location:** `D:\Dev\repos\mcp-central-docs\scripts\sota\`

**Current SOTA Scripts:**
- `restart_claude_and_check_mcp.ps1` - Generic MCP server restart & verification

**Usage:**
1. Scripts are copied from central docs repo to each MCP server repo
2. Each repo has its own copy in `scripts/` directory
3. Scripts auto-detect server name, log file location, etc.
4. Updates to SOTA scripts can be pulled from central repo

---

## 📝 Script Configuration

The restart script auto-detects:
- **Server name**: From repo directory name
- **Log file**: `logs\<server-name>.log` (with fallbacks)
- **Claude path**: Common installation locations
- **Pre-check script**: `scripts/pre_commit_check.py`

**Manual override:**
```powershell
.\scripts\restart_claude_and_check_mcp.ps1 `
    -ServerName "custom-name" `
    -LogFile "logs\custom.log" `
    -SkipPrecheck `
    -NoRestart
```

---

## ✅ Success Criteria

**Workflow is complete when:**
1. ✅ Tool added following all standards
2. ✅ `ruff check .` passes with **zero errors** (iterated until clean)
3. ✅ `ruff format .` executed (code formatted)
4. ✅ All tests pass (`pytest -v`)
5. ✅ Restart script reports: `[SUCCESS] MCP server loaded successfully in Claude!`

**Only then** is it safe to commit and push.

---

## 🚨 Troubleshooting

### Ruff Fails
```bash
# See what's wrong
uv run ruff check . --output-format=concise

# Auto-fix what can be fixed automatically
uv run ruff check . --fix

# Run again to check remaining errors
uv run ruff check .

# Repeat: Fix manually → Run check again → Until zero errors
```

### Tests Fail
```bash
# Run with verbose output
uv run python -m pytest -v -s

# Run specific failing test
uv run python -m pytest tests/test_file.py::test_function -v
```

### Server Doesn't Load
```powershell
# Check logs for errors
Get-Content logs\<server-name>.log -Tail 50

# Or use the log checker
python scripts\check_logs.py --errors-only
```

---

## 📚 Related Documentation

- **Standards**: `D:\Dev\repos\mcp-central-docs\STANDARDS.md`
- **Cursor Workflow**: `mcp-central-docs/docs-private/CURSOR_WORKFLOW_STRATEGY.md`
- **Pre-commit checks**: `scripts/pre_commit_check.py`

---

**This workflow ensures consistent quality across all MCP server projects.**

