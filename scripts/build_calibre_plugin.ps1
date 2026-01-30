# Build CalibreMCP Calibre plugin ZIP
# Run from repo root: .\scripts\build_calibre_plugin.ps1
$pluginDir = "calibre_plugin"
$zipName = "calibre_mcp_integration.zip"

if (-not (Test-Path $pluginDir)) {
    Write-Error "Plugin directory $pluginDir not found. Run from repo root."
    exit 1
}

if (Test-Path $zipName) {
    Remove-Item $zipName -Force
}

Compress-Archive -Path "$pluginDir\*" -DestinationPath $zipName -Force

Write-Host "Built $zipName"
Write-Host "Install: calibre-customize -a $zipName"
