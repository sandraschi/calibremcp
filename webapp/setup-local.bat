@echo off
REM Run from Explorer or native cmd - NOT from Cursor (sandbox blocks pip/npm)
REM Spawns a persistent window so it never vanishes
if "%~1"=="_" goto run
start "CalibreMCP Setup" cmd /k "%~f0" _
exit /b 0

:run
cd /d "%~dp0"
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "http_proxy="
set "https_proxy="

echo Installing calibre-mcp...
cd ..
pip install -e .
if errorlevel 1 goto err

echo Installing backend deps...
cd webapp\backend
pip install -r requirements.txt
if errorlevel 1 goto err

echo Installing frontend deps...
cd ..\frontend
npm install
if errorlevel 1 goto err

echo.
echo Done. Run start-local.bat to start the webapp.
goto end

:err
echo.
echo Setup failed. Check output above.

:end
echo.
echo Press any key to close this window...
pause >nul
