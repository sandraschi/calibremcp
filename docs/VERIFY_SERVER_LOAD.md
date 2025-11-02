# How to Verify Server Will Load in Claude

This guide explains how to verify that the CalibreMCP server will load successfully in Claude before committing changes.

## Quick Check (Recommended)

Run the quick check script:

```bash
python scripts/quick_check.py
```

This performs the essential checks:
- ✅ Server module imports
- ✅ Tools registration
- ✅ Tag tools import

**Expected output:**
```
[OK] Server imports
[OK] Tools registered
[OK] Tag tools import

[SUCCESS] Server will load in Claude!
```

## Comprehensive Test

For a full verification, run the comprehensive test:

```bash
python scripts/test_server_load.py
```

This performs additional checks:
- ✅ Server module imports
- ✅ Tag tools import verification
- ✅ Tools registration
- ✅ Server startup simulation

## What Claude Does

When Claude loads an MCP server, it:

1. **Starts the server process** via stdio transport
2. **Imports the server module** (`from calibre_mcp.server import main`)
3. **Calls `main()`** which:
   - Sets up logging
   - Discovers libraries
   - Initializes database
   - Registers all tools via `register_tools(mcp)`
   - Starts the FastMCP server

## Common Issues to Check

### 1. Import Errors
**Symptom:** `ImportError: cannot import name 'X' from 'module'`

**Solution:** Check for:
- Missing dependencies in imports
- Circular imports
- Typos in module/class names

**Test:** Run `python scripts/quick_check.py`

### 2. Tool Registration Failures
**Symptom:** Warnings like `Tool already exists: tool_name`

**Solution:** Check for:
- Duplicate tool names
- Tools registered multiple times
- Conflicting tool definitions

**Test:** Check logs for warnings during `register_tools(mcp)`

### 3. Database Initialization Issues
**Symptom:** `FileNotFoundError` or database connection errors

**Solution:** 
- Ensure library path is configured (or server allows starting without one)
- Check that `metadata.db` exists if library is required

**Note:** Server can start without a library - tools will show clear error messages.

### 4. Missing Models or Services
**Symptom:** `AttributeError` or `NameError` in service/tool code

**Solution:** Check that:
- All required services are imported
- Models exist and are properly exported
- Service singletons are created

## Pre-Commit Checklist

Before committing code that affects server startup:

- [ ] Run `python scripts/quick_check.py` - should pass
- [ ] Run `uv run ruff check .` - should pass
- [ ] Run `uv run ruff format . --check` - should pass
- [ ] Test that server actually starts: `python -m src.calibre_mcp.server` (Ctrl+C to stop)
- [ ] Check for any new warnings during startup

## Integration with CI/CD

The quick check script can be added to CI/CD:

```yaml
# .github/workflows/ci.yml
- name: Verify server loads
  run: python scripts/quick_check.py
```

## Troubleshooting

If tests pass but server still doesn't load in Claude:

1. **Check Claude's MCP configuration** - ensure command/path are correct
2. **Check Python version** - Claude might use a different Python
3. **Check environment variables** - some config might be missing
4. **Check logs** - Claude may have server logs in its interface
5. **Check dependencies** - ensure all packages are installed in Claude's environment

## Manual Verification

To manually test server startup:

```bash
# Start server (will run until Ctrl+C)
python -m src.calibre_mcp.server

# Or use the test script to simulate startup
python scripts/test_server_load.py
```

If the server starts without errors locally, it should work in Claude (assuming same Python version and dependencies).

