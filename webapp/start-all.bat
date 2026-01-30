@echo off
cd /d "%~dp0"

REM Stop existing containers (zombie kill)
docker compose down 2>nul

if "%CALIBRE_LIBRARY_PATH%"=="" (
    if not exist .env (
        echo Set CALIBRE_LIBRARY_PATH or create .env from .env.docker.example
        echo Example: set CALIBRE_LIBRARY_PATH=L:\path\to\calibre\library
        pause
        exit /b 1
    )
)

docker compose up -d --build
if errorlevel 1 (
    echo.
    echo Build or start failed. Check output above.
    pause
    exit /b 1
)
echo.
echo Backend: http://localhost:13000
echo Frontend: http://localhost:13001
echo.
echo Press any key to close...
pause >nul
