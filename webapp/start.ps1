# Calibre-MCP Webapp Start (MANDATORY port clear per mcp-central-docs WEBAPP_PORTS)
# Reservoir ports: 10720 (backend), 10721 (frontend)
# Run: powershell -ExecutionPolicy Bypass -File start.ps1

$BackendPort = 10720
$FrontendPort = 10721
$WebappRoot = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $WebappRoot
$SrcPath = Join-Path $ProjectRoot "src"

# 1. Clear reservoir ports (mandatory before bind). Prefer kill-port, fallback to PowerShell.
$frontendDir = Join-Path $WebappRoot "frontend"
Set-Location $frontendDir
$killPortOk = $false
try {
    npx --yes kill-port $BackendPort $FrontendPort 2>$null
    $killPortOk = $true
} catch { }
if (-not $killPortOk) {
    function Clear-Port($Port) {
        $pidsToKill = [System.Collections.Generic.HashSet[int]]::new()
        Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | ForEach-Object { [void]$pidsToKill.Add($_.OwningProcess) }
        $netstat = netstat -ano 2>$null
        foreach ($line in $netstat) {
            if (($line -match ":$Port\s") -and ($line -match "LISTENING")) {
                $parts = $line.Trim() -split '\s+'
                $procId = $parts[-1]
                if ($procId -match '^\d+$') { [void]$pidsToKill.Add([int]$procId) }
            }
        }
        foreach ($procId in $pidsToKill) {
            if ($procId -gt 0) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
        }
        if ($pidsToKill.Count -gt 0) { Start-Sleep -Seconds 2 }
    }
    Clear-Port $BackendPort
    Clear-Port $FrontendPort
}
Set-Location $WebappRoot
Start-Sleep -Seconds 1

# 2. Env
$env:PYTHONPATH = $SrcPath
$env:CALIBRE_LIBRARY_PATH = if ($env:CALIBRE_LIBRARY_PATH) { $env:CALIBRE_LIBRARY_PATH } else {
    if (Test-Path (Join-Path $WebappRoot ".env")) {
        (Get-Content (Join-Path $WebappRoot ".env") | ForEach-Object { if ($_ -match '^\s*CALIBRE_LIBRARY_PATH\s*=\s*(.+)$') { $Matches[1].Trim() } }) | Select-Object -First 1
    } else { "" }
}
if (-not $env:CALIBRE_LIBRARY_PATH) {
    Write-Host "[ERROR] Set CALIBRE_LIBRARY_PATH or add to webapp\.env" -ForegroundColor Red
    exit 1
}
$env:PORT = $BackendPort
$env:MCP_USE_HTTP = "false"
$env:BACKEND_URL = "http://127.0.0.1:$BackendPort"
$env:CORS_ORIGINS = "http://localhost:$FrontendPort,http://127.0.0.1:$FrontendPort"

# 3. Start backend (new window)
if (-not (Test-Path $SrcPath)) {
    Write-Host "[ERROR] Source path not found: $SrcPath" -ForegroundColor Red
    exit 1
}
Write-Host "[INFO] Backend http://localhost:$BackendPort  Frontend http://localhost:$FrontendPort" -ForegroundColor Green
$backendDir = Join-Path $WebappRoot "backend"
$corsOrigins = "http://localhost:$FrontendPort,http://127.0.0.1:$FrontendPort"
$backendCmd = "Set-Location '$backendDir'; `$env:PYTHONPATH='$SrcPath'; `$env:PORT='$BackendPort'; `$env:CORS_ORIGINS='$corsOrigins'; `$env:CALIBRE_LIBRARY_PATH='$env:CALIBRE_LIBRARY_PATH'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $BackendPort"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 2

# 4. Start frontend (new window, reservoir port). API_URL = server-side proxy target.
# NEXT_PUBLIC_APP_URL = self-URL for SSR fetch (getBaseUrl in lib/api.ts) - must match frontend port.
$frontendDir = Join-Path $WebappRoot "frontend"
$apiUrl = "http://127.0.0.1:$BackendPort"
$appUrl = "http://127.0.0.1:$FrontendPort"
$frontendCmd = "Set-Location '$frontendDir'; `$env:API_URL='$apiUrl'; `$env:NEXT_PUBLIC_API_URL='$apiUrl'; `$env:NEXT_PUBLIC_APP_URL='$appUrl'; npx next dev --turbo -p $FrontendPort"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "Backend and frontend started. Close their windows to stop."