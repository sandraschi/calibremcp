@echo off
setlocal
REM Launcher in starts/ — %%~dp0 is starts\; webapp lives under calibre-mcp (see starts/README.md).
REM Layout: D:\Dev\repos\mcp-central-docs\starts\  ->  D:\Dev\repos\calibre-mcp\webapp
set "WEBAPP=%~dp0..\..\calibre-mcp\webapp"
cd /d "%WEBAPP%"
if not exist "start.ps1" (
  echo [ERROR] calibre-mcp webapp not found. Expected: %CD%\start.ps1
  echo Fix: clone calibre-mcp next to mcp-central-docs under the same parent folder.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\start.ps1"
endlocal
