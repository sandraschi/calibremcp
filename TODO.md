# calibre-mcp Tauri NSIS — Remaining Work

## Status (2026-06-17)

- Backend starts, health 200 ✅
- Frontend static mount at `/app/` works ✅ (confirmed by debug output)
- CORS configured for tauri://localhost ✅
- Rust `main.rs` navigates WebView to `http://127.0.0.1:10720/app/` after backend starts ✅
- CSP set to `null` ✅
- Frontend dist bundled in PyInstaller ✅ (confirmed in EXE-00.toc)

## Blocker: PyInstaller excludes stdlib modules

The built exe crashes with `ModuleNotFoundError: No module named 'difflib'` and `No module named 'statistics'`. These are Python standard library modules. The spec file likely has an `excludes` list that accidentally includes them.

**Fix**: Check `calibre-mcp-backend.spec` line 257 for the `excludes` list. Remove `difflib` and `statistics` from it (they should not be there — they're needed by `calibre_mcp` tools).

Alternatively, add them to `hiddenimports` in the spec.

**After fix**: Rebuild PyInstaller + NSIS, install, and verify `/app/` serves the SPA correctly.

## To verify

```powershell
# After rebuilding:
& .\native\build.ps1
# Install
Start-Process "dist\Calibre MCP_1.8.6_x64-setup.exe" -ArgumentList "/S" -Wait
Start-Process "$env:LOCALAPPDATA\Calibre MCP\calibre-mcp-native.exe"
Start-Sleep 30
# Check health
Invoke-WebRequest -Uri "http://127.0.0.1:10720/health"
# Check SPA (frontend served by backend)
Invoke-WebRequest -Uri "http://127.0.0.1:10720/app/"
```
