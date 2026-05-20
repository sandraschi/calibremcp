Param([switch]$Headless, [switch]$Rebuild, [switch]$Dev)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$WebPort = 10721
$BackendPort = 10720
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FrontendDir = "$PSScriptRoot\frontend"

# 1. Kill port squatters
Write-Host "Clearing ports $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "  Killing PID $p..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "  Warning: could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Start backend (immediately, so it's visible while build runs)
Write-Host "Starting backend on port $BackendPort..." -ForegroundColor Cyan
$reloadFlag = if ($Dev) { '--reload' } else { '' }
$backendCmd = "Set-Location '$PSScriptRoot\backend'; `$env:CALIBRE_LOG_ACCESS_VERBOSE=''; uv run --project '$ProjectRoot' uvicorn app.main:app --host 127.0.0.1 --port $BackendPort $reloadFlag"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 3. Install frontend deps if missing
Set-Location $FrontendDir
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Cyan
    npm install
}

# 4. Build frontend (once, or on -Rebuild)
$buildId = "$FrontendDir\.next\BUILD_ID"
if ($Dev) {
    Write-Host "Dev mode — skipping production build." -ForegroundColor Yellow
} elseif ($Rebuild -or -not (Test-Path $buildId)) {
    Write-Host "Building frontend for production (approx 60s)..." -ForegroundColor Cyan
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed! Falling back to dev mode." -ForegroundColor Red
        $Dev = $true
    }
} else {
    Write-Host "Production build cached — use -Rebuild to force rebuild." -ForegroundColor Gray
}

# 5. Start frontend
if ($SkipFrontend) { return }

$modeLabel = if ($Dev) { 'Dev' } else { 'Production' }
Write-Host "Starting frontend ($modeLabel mode) on port $WebPort..." -ForegroundColor Green

$env:API_URL = "http://127.0.0.1:$BackendPort"
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:$BackendPort"

# Auto-open browser when ready
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Set-Location $FrontendDir
if ($Dev) { npm run dev } else { npm run start }
