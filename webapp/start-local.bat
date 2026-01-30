@echo off
cd /d "%~dp0"

REM Kill zombies on 13000/13001
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":13000 " ^| findstr "LISTENING"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":13001 " ^| findstr "LISTENING"') do taskkill /PID %%a /F 2>nul
timeout /t 1 /nobreak >nul

REM Bypass broken proxy (fixes pip/npm in Cursor/spawned terminals)
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "http_proxy="
set "https_proxy="

REM Load CALIBRE_LIBRARY_PATH from .env if present
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if "%%~a"=="CALIBRE_LIBRARY_PATH" set "CALIBRE_LIBRARY_PATH=%%~b"
    )
)

if "%CALIBRE_LIBRARY_PATH%"=="" (
    echo CALIBRE_LIBRARY_PATH not set. Add it to .env or set it in this session.
    echo Example: set CALIBRE_LIBRARY_PATH=L:\path\to\calibre\library
    pause
    exit /b 1
)

REM Ensure backend .env exists
if not exist backend\.env (
    copy backend\env.example backend\.env
    echo Created backend\.env. Edit it if you need different CORS/port.
)

REM Ensure frontend .env.local exists
if not exist frontend\.env.local (
    copy frontend\env.example frontend\.env.local
)

set "REPO_ROOT=%~dp0.."
set "SRC_PATH=%REPO_ROOT%\src"

if not exist "%SRC_PATH%" (
    echo Source path not found: %SRC_PATH%
    pause
    exit /b 1
)

echo Starting backend on http://localhost:13000
echo Starting frontend on http://localhost:13001
echo.
start "CalibreMCP Backend" cmd /k "cd /d "%~dp0backend" & set PYTHONPATH=%SRC_PATH% & set "CALIBRE_LIBRARY_PATH=%CALIBRE_LIBRARY_PATH%" & set MCP_USE_HTTP=false & python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 13000"

timeout /t 3 /nobreak >nul

start "CalibreMCP Frontend" cmd /k "cd /d "%~dp0frontend" & npm run dev"

echo.
echo Backend: http://localhost:13000
echo Frontend: http://localhost:13001
echo.
echo Close the backend and frontend windows to stop.
pause
