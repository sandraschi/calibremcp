# Webapp Start - Standardized SOTA (Auto-Repaired V2.5)
$WebPort = 10721
$BackendPort = 10720
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup
Set-Location "$PSScriptRoot\frontend"
if (-not (Test-Path "node_modules")) { npm install }

# 3. Start the Python backend (Background)
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan

# Run the webapp backend (FastAPI) instead of the bare MCP server
# uv --project finds package; CWD must be webapp/backend for app.main to be found
$backendCmd = "Set-Location '$PSScriptRoot\backend'; uv run --project '$ProjectRoot' uvicorn app.main:app --host 127.0.0.1 --port $BackendPort --log-level info --reload"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 4. Start the Frontend (Background)
Write-Host "Starting Frontend on port $WebPort ..." -ForegroundColor Green

# Set environment variables for the frontend process
$env:API_URL = "http://127.0.0.1:$BackendPort"
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:$BackendPort"

Set-Location "$PSScriptRoot\frontend"
npm run dev -- --port $WebPort
