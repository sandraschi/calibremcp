#Requires -Version 7.0
<#
.SYNOPSIS
    Start calibre-mcp webapp reachable from the LAN / Tailscale (phone, tablet, second PC).

.DESCRIPTION
    Loopback-only start.ps1 binds 127.0.0.1, which other devices cannot reach.
    This wrapper:
      1. Ensures a Windows Firewall inbound rule for the backend + frontend ports
         (needs elevation; without it, prints the exact command to run as admin).
      2. Starts the backend via ..\start.ps1 -BackendOnly with CALIBRE_BIND=0.0.0.0
         (honored by fleet-start.config.ps1 -> central fleet engine).
      3. Starts the Next.js frontend bound to 0.0.0.0 with CALIBRE_DEV_ORIGINS set
         from detected interface addresses (Next.js dev host allow-list).
      4. Prints reachable URLs (LAN IPs, Tailscale 100.x, MagicDNS hint).

    The frontend uses same-origin /api rewrites, so no CORS or API-base config is
    needed on the client. The backend has NO authentication: anyone who can reach
    these ports can read, edit, and DELETE your library. Use on trusted networks
    (home LAN, your own Tailscale tailnet) only — never expose to the internet.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\start-lan.ps1
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\start-lan.ps1 -NoFirewall -NoBrowser
#>
param(
    [switch]$NoFirewall,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'

$WebappRoot = $PSScriptRoot
$RepoRoot = Split-Path -Parent $WebappRoot
$ConfigPath = Join-Path $RepoRoot 'fleet-start.config.ps1'
if (-not (Test-Path -LiteralPath $ConfigPath)) {
    Write-Host "ERROR: Missing fleet-start.config.ps1 at $ConfigPath" -ForegroundColor Red
    exit 1
}
$cfg = . $ConfigPath
$backendPort = if ($cfg.BackendPort) { [int]$cfg.BackendPort } else { 10720 }
$frontendPort = if ($cfg.FrontendPort) { [int]$cfg.FrontendPort } else { 10721 }
$webRoot = Join-Path $RepoRoot 'webapp\frontend'

function Test-IsAdmin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($id)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-LanAddresses {
    Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } |
        Select-Object -ExpandProperty IPAddress -Unique |
        Sort-Object
}

# 1. Firewall (idempotent)
$ruleName = 'calibre-mcp webapp (LAN)'
if (-not $NoFirewall) {
    $existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "Firewall rule '$ruleName' already present." -ForegroundColor DarkGray
    } elseif (Test-IsAdmin) {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP `
            -LocalPort @($backendPort, $frontendPort) -Action Allow | Out-Null
        Write-Host "Firewall rule '$ruleName' created (TCP $backendPort, $frontendPort, all profiles)." -ForegroundColor Green
    } else {
        Write-Host 'WARN: not elevated — cannot create the firewall rule.' -ForegroundColor Yellow
        Write-Host '  Either re-run this script as Administrator once, or run (elevated):' -ForegroundColor Yellow
        Write-Host "  New-NetFirewallRule -DisplayName '$ruleName' -Direction Inbound -Protocol TCP -LocalPort $backendPort,$frontendPort -Action Allow" -ForegroundColor Gray
        Write-Host '  Continuing without it — LAN devices will likely be blocked until the rule exists.' -ForegroundColor Yellow
    }
}

$addresses = @(Get-LanAddresses)
if ($addresses.Count -eq 0) {
    Write-Host 'WARN: no LAN addresses detected; continuing with bind only.' -ForegroundColor Yellow
}

# Next.js dev host allow-list (page loads from these hosts/IPs)
$hostNames = @($env:COMPUTERNAME) + $addresses | Where-Object { $_ } | Select-Object -Unique
$env:CALIBRE_DEV_ORIGINS = ($hostNames -join ',')
$env:CALIBRE_BIND = '0.0.0.0'

# 2. Backend (central fleet engine honors Backend.Host from fleet-start.config.ps1)
Write-Host "Starting backend on 0.0.0.0:$backendPort ..." -ForegroundColor Cyan
& (Join-Path $RepoRoot 'webapp\start.ps1') -BackendOnly -NoBrowser
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Backend launch reported failure; aborting frontend start.' -ForegroundColor Red
    exit 1
}

# 3. Frontend bound to all interfaces
Write-Host "Starting frontend on 0.0.0.0:$frontendPort ..." -ForegroundColor Cyan
$npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npm) {
    Write-Host 'ERROR: npm not found on PATH.' -ForegroundColor Red
    exit 1
}
$fCmd = "Set-Location '$webRoot'; `$env:CALIBRE_DEV_ORIGINS = '$($env:CALIBRE_DEV_ORIGINS)'; npm run dev -- -p $frontendPort -H 0.0.0.0"
Start-Process cmd.exe -ArgumentList @('/k', $fCmd) -WorkingDirectory $webRoot

# 4. URLs
Write-Host ''
Write-Host '  calibre-mcp reachable at:' -ForegroundColor Cyan
foreach ($ip in $addresses) {
    $tag = if ($ip -like '100.*') { '  (Tailscale?)' } else { '' }
    Write-Host "    http://${ip}:${frontendPort}/$tag" -ForegroundColor Gray
}
if ($env:COMPUTERNAME) {
    Write-Host "    http://$($env:COMPUTERNAME.ToLower()):${frontendPort}/  (Windows hostname / NetBIOS)" -ForegroundColor Gray
}
Write-Host '  Tailscale MagicDNS also works, e.g. http://goliath.<tailnet>.ts.net:10721/' -ForegroundColor DarkGray
Write-Host ''
Write-Host '  WARN: no authentication on these ports — trusted networks (home LAN, your own' -ForegroundColor Yellow
Write-Host '  tailnet) only. Anyone with reach can read/edit/delete the library.' -ForegroundColor Yellow
Write-Host ''

if (-not $NoBrowser) {
    Start-Process "http://127.0.0.1:${frontendPort}/"
}
