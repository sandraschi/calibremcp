# Start backend with proper Python path
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$srcPath = Join-Path $projectRoot "src"

# CRITICAL: Set PYTHONPATH before Python starts
$env:PYTHONPATH = $srcPath
$env:MCP_USE_HTTP = "false"  # Use direct import until HTTP mounting is fixed
$env:BACKEND_URL = "http://127.0.0.1:13000"

# Verify path exists
if (-not (Test-Path $srcPath)) {
    Write-Host "[ERROR] Source path does not exist: $srcPath" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Starting backend with PYTHONPATH=$srcPath" -ForegroundColor Green
Set-Location $PSScriptRoot
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 13000
