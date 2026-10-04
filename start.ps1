Param([switch]$Headless, [switch]$BackendOnly)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$env:FASTMCP_LOG_LEVEL = 'WARNING'

# --- Elevated zombie killer (Session-0-service aware) ---
$BackendPort = 10720
. "$PSScriptRoot\scripts\FleetStartMode.ps1"
# NOTE: Invoke-FleetFreePort does not exist in the vendored FleetStartMode.ps1;
# use Stop-FleetPortSquatters (skips Session 0 service PIDs by design).
$null = Stop-FleetPortSquatters -Ports @($BackendPort) -Label 'calibre-mcp'

# calibremcp Start - Standards-Compliant SOTA
Write-Host 'Starting calibremcp...' -ForegroundColor Cyan

uv run calibremcp
