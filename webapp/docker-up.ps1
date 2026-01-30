# Start CalibreMCP webapp via Docker Compose
# Set CALIBRE_LIBRARY_PATH before running, or create .env from .env.docker.example

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

docker compose down 2>$null

if (-not $env:CALIBRE_LIBRARY_PATH -and -not (Test-Path .env)) {
    Write-Host "Set CALIBRE_LIBRARY_PATH or create .env from .env.docker.example"
    Write-Host "Example: `$env:CALIBRE_LIBRARY_PATH = 'L:/path/to/calibre/library'"
    exit 1
}

docker compose up -d --build
Write-Host "Backend: http://localhost:13000"
Write-Host "Frontend: http://localhost:13001"
