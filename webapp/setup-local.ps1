# Setup webapp for local run
# Run from native PowerShell, NOT from Cursor (sandbox blocks pip/npm)
$env:HTTP_PROXY = $null
$env:HTTPS_PROXY = $null
$env:http_proxy = $null
$env:https_proxy = $null
$env:NO_PROXY = "*"
$env:no_proxy = "*"

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "Installing calibre-mcp..."
Set-Location $root
pip install -e .

Write-Host "Installing backend deps..."
Set-Location "$PSScriptRoot\backend"
pip install -r requirements.txt

Write-Host "Installing frontend deps..."
Set-Location "$PSScriptRoot\frontend"
npm install

Write-Host "Done. Run start-local.bat to start the webapp."
