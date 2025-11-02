# SOTA Script Information

**This script should be copied to:** `D:\Dev\repos\mcp-central-docs\scripts\sota\`

## Current SOTA Script

**File:** `restart_claude_and_check_mcp.ps1`

**Purpose:** Generic MCP server restart and verification script for debugging

**Features:**
- ✅ Auto-detects server name from repo directory
- ✅ Auto-detects log file location with fallbacks
- ✅ Restarts Claude Desktop (stop/start)
- ✅ Checks only the **LAST** startup attempt (ignores older failures)
- ✅ Works with any MCP server (generic)

**Usage:**
```powershell
# Full restart + check
.\scripts\restart_claude_and_check_mcp.ps1

# Just check logs (Claude already running)
.\scripts\restart_claude_and_check_mcp.ps1 -NoRestart

# Custom configuration
.\scripts\restart_claude_and_check_mcp.ps1 -ServerName "my-server" -LogFile "logs\custom.log"
```

**To Copy to Central Docs:**
```powershell
Copy-Item scripts\restart_claude_and_check_mcp.ps1 D:\Dev\repos\mcp-central-docs\scripts\sota\
```

**To Copy to Other MCP Repos:**
```powershell
# From central docs repo
Copy-Item D:\Dev\repos\mcp-central-docs\scripts\sota\restart_claude_and_check_mcp.ps1 <mcp-repo>\scripts\
```

---

## Workflow Integration

This script is part of the standardized MCP development workflow:

1. **"Add tool to do x"** → Add tool following standards
2. **Run ruff** → `uv run ruff check .` and `uv run ruff format .`
3. **Run pytest** → `uv run python -m pytest -v`
4. **Run this script** → `.\scripts\restart_claude_and_check_mcp.ps1`

**See:** [MCP Development Workflow](docs/MCP_DEVELOPMENT_WORKFLOW.md)

