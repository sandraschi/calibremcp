# PowerShell script to run Calibre MCP tests

param(
    [string]$TestPath = "tests/",
    [switch]$Coverage = $false,
    [switch]$Verbose = $false,
    [string]$Marker = "",
    [string]$TestName = ""
)

Write-Host "Running Calibre MCP Tests" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# Check if pytest is installed
try {
    $pytestVersion = python -m pytest --version 2>&1
    Write-Host "Using: $pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: pytest not found. Install with: pip install pytest pytest-asyncio" -ForegroundColor Red
    exit 1
}

# Build pytest command
$pytestArgs = @()

if ($Verbose) {
    $pytestArgs += "-vv"
} else {
    $pytestArgs += "-v"
}

if ($Coverage) {
    $pytestArgs += "--cov=calibre_mcp"
    $pytestArgs += "--cov-report=html"
    $pytestArgs += "--cov-report=term"
}

if ($Marker) {
    $pytestArgs += "-m", $Marker
}

if ($TestName) {
    $pytestArgs += "-k", $TestName
}

$pytestArgs += $TestPath

# Run tests
Write-Host "Command: python -m pytest $($pytestArgs -join ' ')" -ForegroundColor Yellow
Write-Host ""

python -m pytest $pytestArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "All tests passed!" -ForegroundColor Green
    
    if ($Coverage) {
        Write-Host ""
        Write-Host "Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "Some tests failed. Exit code: $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
