# CalibreMCP Unicode Fix - August 10, 2025

## Problem Identified
The CalibreMCP server crashes on Windows with stdio mode due to Unicode emojis in console output causing CP1252 encoding errors.

## Quick Fix
Replace lines 2493-2497 in `src/calibre_mcp/server.py` main() function:

### Before (causing crash):
```python
print("🚀 Starting CalibreMCP Phase 2 - FastMCP 2.0 Server", file=sys.stderr)
print("Austrian efficiency for Sandra's 1000+ book collection! 📚✨", file=sys.stderr)
print("Now with 23 comprehensive tools including weeb optimization 🎌", file=sys.stderr)
```

### After (fixed):
```python
print("Starting CalibreMCP Phase 2 - FastMCP 2.0 Server", file=sys.stderr)
print("Austrian efficiency for Sandra's 1000+ book collection!", file=sys.stderr)
print("Now with 23 comprehensive tools including weeb optimization", file=sys.stderr)
```

## Alternative Fixes
1. **UTF-8 Console**: Add `sys.stdout.reconfigure(encoding='utf-8')` before prints
2. **Environment Detection**: Only use emojis in interactive mode, not stdio mode
3. **Safe Emoji Function**: Create utility function that detects encoding support

## Implementation
Use PowerShell to apply the quick fix:

```powershell
# Backup original file
Copy-Item "D:\Dev\repos\calibremcp\src\calibre_mcp\server.py" "D:\Dev\repos\calibremcp\src\calibre_mcp\server.py.backup"

# Apply fix (manual edit recommended)
# Replace emoji lines with plain text versions
```

## Testing
After fix, test with:
```powershell
cd "D:\Dev\repos\calibremcp"
python server/server.py
```

Should start without Unicode errors and connect successfully to Claude Desktop.

This is a 5-minute fix that unlocks a professional-quality MCP server!
