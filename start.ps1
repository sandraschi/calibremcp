Param([switch]$Headless, [switch]$BackendOnly)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$env:FASTMCP_LOG_LEVEL = 'WARNING'

# --- Elevated zombie killer (Rust free_port pattern) ---
$BackendPort = 10720
. "$PSScriptRoot\scripts\FleetStartMode.ps1"
$null = Invoke-FleetFreePort -Port $BackendPort -ImageNames @('python', 'calibre-mcp-backend') -PollSec 15

# calibremcp Start - Standards-Compliant SOTA
Write-Host 'Starting calibremcp...' -ForegroundColor Cyan

uv run calibremcp