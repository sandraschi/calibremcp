@echo off
setlocal
cd /d "%~dp0"
if not exist "start.ps1" (
  echo [ERROR] start.ps1 not found in %CD%
  pause
  exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
endlocal
