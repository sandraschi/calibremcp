@echo off
REM Windows batch file to run Calibre MCP tests

echo Running Calibre MCP Test Battery...
echo ===================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Run the comprehensive test battery
python test_battery.py

REM Check result
if errorlevel 1 (
    echo.
    echo Some tests failed. Check the output above.
    pause
    exit /b 1
) else (
    echo.
    echo All tests passed! Calibre MCP is working correctly.
    pause
)