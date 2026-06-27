param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser,
    [switch]$Dev,
    [switch]$Rebuild,
    [switch]$ReuseIfRunning)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath
$FleetStart = Initialize-FleetStartMode @PSBoundParameters
Enter-FleetHeadlessConsole -Headless:$Headless -BackendOnly:$BackendOnly

$WebPort = 10721
$BackendPort = 10720
$FrontendDir = "$PSScriptRoot\frontend"

# -- Direct zombie kill (before fleet helper) --
$zombiePids = [System.Collections.Generic.HashSet[int]]::new()
foreach ($port in @($WebPort, $BackendPort)) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        ForEach-Object { [void]$zombiePids.Add($_.OwningProcess) }
}
foreach ($zpid in $zombiePids) {
    Write-Host "Killing zombie (PID $zpid)..." -ForegroundColor Yellow
    Stop-Process -Id $zpid -Force -ErrorAction SilentlyContinue
    taskkill /F /PID $zpid /T 2>$null
}
# Elevation fallback: kill any zombie that survived
$survivorPids = @($zombiePids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue })
if ($survivorPids.Count -gt 0) {
    Write-Host "Zombies survived -- requesting elevation..." -ForegroundColor Yellow
    $elevatedCmd = "taskkill /F /PID $($survivorPids -join ' /PID ') /T 2>$null"
    Start-Process powershell.exe -Verb RunAs -ArgumentList @(
        "-NoProfile", "-Command", $elevatedCmd
    ) -Wait -WindowStyle Hidden -ErrorAction SilentlyContinue
}
Start-Sleep -Milliseconds 500

$portResolve = @{
    Ports      = @($WebPort, $BackendPort)
    Label      = "calibre-mcp"
    AllowReuse = $ReuseIfRunning
}
if ($ReuseIfRunning) {
    $portResolve.HealthChecks = @{
        $WebPort = "http://127.0.0.1:$WebPort/"
        $BackendPort = "http://127.0.0.1:$BackendPort/health"
    }
}
$portState = Resolve-FleetPortConflict @portResolve
if ($portState.Action -eq 'Blocked') { exit 1 }
if ($portState.Reuse) { return }


# 2. Start backend (immediately, so it's visible while build runs)
Write-Host "Starting backend on port $BackendPort..." -ForegroundColor Cyan
$reloadFlag = if ($Dev) { '--reload' } else { '' }
$backendCmd = "Set-Location '$PSScriptRoot\backend'; `$env:CALIBRE_LOG_ACCESS_VERBOSE=''; uv run --project '$ProjectRoot' uvicorn app.main:app --host 127.0.0.1 --port $BackendPort $reloadFlag"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

$healthUrl = "http://127.0.0.1:$BackendPort/health"
$attempt = 0
while ($attempt -lt 30) {
    try {
        $null = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "Backend (port $BackendPort) answered GET /health." -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 2
        $attempt++
    }
}

# 3. Guard: clean stale Tauri export .next cache (basePath:/app breaks dev mode)
Set-Location $FrontendDir
$manifestPath = ".next\routes-manifest.json"
if ($Dev -and (Test-Path $manifestPath)) {
    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.basePath) {
        Write-Host "Cleaning stale .next cache (Tauri basePath detected)... " -ForegroundColor Yellow -NoNewline
        Remove-Item ".next" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "done" -ForegroundColor Green
    }
}

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Cyan
    npm install
}

# 4. Build frontend (once, or on -Rebuild)
$buildId = "$FrontendDir\.next\BUILD_ID"
if (-not $Dev -and -not (Test-Path $buildId)) {
    $Dev = $true
}
if ($Dev) {
    Write-Host "Dev mode - skipping production build." -ForegroundColor Yellow
} elseif ($Rebuild -or -not (Test-Path $buildId)) {
    Write-Host "Building frontend for production (approx 60s)..." -ForegroundColor Cyan
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed! Falling back to dev mode." -ForegroundColor Red
        $Dev = $true
    }
} else {
    Write-Host "Production build cached - use -Rebuild to force rebuild." -ForegroundColor Gray
}

# 5. Start frontend
if (-not $FleetStart.RunFrontend) { return }

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



