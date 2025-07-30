@echo off
echo Starting paper downloads...

:: Run each download script
call powershell -ExecutionPolicy Bypass -File "%~dp0download_paper_1.ps1"
call powershell -ExecutionPolicy Bypass -File "%~dp0download_paper_2.ps1"
call powershell -ExecutionPolicy Bypass -File "%~dp0download_paper_3.ps1"
call powershell -ExecutionPolicy Bypass -File "%~dp0download_paper_4.ps1"
call powershell -ExecutionPolicy Bypass -File "%~dp0download_paper_5.ps1"

echo.
echo All paper downloads completed!
pause
