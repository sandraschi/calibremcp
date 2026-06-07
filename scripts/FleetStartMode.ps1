# FleetStartMode.ps1 - vendored per-repo copy (no mcp-central-docs required at runtime)
# Canonical upstream: sandraschi/mcp-central-docs standards/FleetStartMode.ps1 (private fleet docs)

# FleetStartMode.ps1 - shared launch modes for webapp/start.ps1 launchers

function Initialize-FleetStartMode {
    param(
        [switch]$Headless,
        [switch]$BackendOnly,
        [switch]$FrontendOnly,
        [switch]$NoBrowser
    )

    if ($FrontendOnly -and $BackendOnly) {
        Write-Error "Cannot combine -FrontendOnly and -BackendOnly."
        exit 1
    }

    $runBackend = -not $FrontendOnly
    $runFrontend = (-not $BackendOnly) -and (-not $Headless) -and (-not $FrontendOnly)
    $skipBrowser = $NoBrowser -or $Headless -or $BackendOnly

    return [pscustomobject]@{
        RunBackend   = $runBackend
        RunFrontend  = $runFrontend
        SkipBrowser  = $skipBrowser
        WindowStyle  = if ($Headless) { "Hidden" } else { "Normal" }
    }
}

function Enter-FleetHeadlessConsole {
    param(
        [switch]$Headless,
        [switch]$BackendOnly
    )

    if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
        $spawnArgs = @(
            '-NoProfile', '-File', $PSCommandPath,
            '-Headless', '-BackendOnly'
        )
        Start-Process pwsh -ArgumentList $spawnArgs -WindowStyle Hidden
        exit
    }
}

function Get-FleetPortListenerPids {
    param(
        [Parameter(Mandatory)][int]$Port,
        [string[]]$NetstatLines = $null
    )

    if ($null -eq $NetstatLines) {
        $NetstatLines = @(netstat -ano)
    }

    $pids = [System.Collections.Generic.HashSet[int]]::new()
    $portToken = ":$Port"
    foreach ($line in $NetstatLines) {
        if ($line -notmatch 'LISTENING') { continue }
        if ($line -notmatch [regex]::Escape($portToken)) { continue }
        $tokens = ($line.Trim() -split '\s+')
        if ($tokens.Count -lt 5) { continue }
        $procId = 0
        if ([int]::TryParse($tokens[-1], [ref]$procId) -and $procId -gt 4) {
            [void]$pids.Add($procId)
        }
    }
    return @($pids)
}

function Get-FleetPortsStillListening {
    param([Parameter(Mandatory)][int[]]$Ports)

    $lines = @(netstat -ano)
    $still = @{}
    foreach ($port in @($Ports | Where-Object { $_ -gt 0 } | Sort-Object -Unique)) {
        $pids = @(Get-FleetPortListenerPids -Port $port -NetstatLines $lines)
        if ($pids.Count -gt 0) {
            $still[$port] = $pids
        }
    }
    return $still
}

function Stop-FleetPortSquatters {
    param(
        [Parameter(Mandatory)]
        [int[]]$Ports,
        [string]$Label = "fleet"
    )

    $uniquePorts = @($Ports | Where-Object { $_ -gt 0 } | Sort-Object -Unique)
    if ($uniquePorts.Count -eq 0) { return }

    $lines = @(netstat -ano)
    $needsWork = $false
    foreach ($port in $uniquePorts) {
        if (@(Get-FleetPortListenerPids -Port $port -NetstatLines $lines).Count -gt 0) {
            $needsWork = $true
            break
        }
    }
    if (-not $needsWork) { return }

    Write-Host "[$Label] Clearing port zombies: $($uniquePorts -join ', ')" -ForegroundColor Yellow

    foreach ($pass in 1..2) {
        $lines = @(netstat -ano)
        foreach ($port in $uniquePorts) {
            foreach ($procId in @(Get-FleetPortListenerPids -Port $port -NetstatLines $lines)) {
                if ($procId -eq $PID) { continue }

                $alive = $null -ne (Get-Process -Id $procId -ErrorAction SilentlyContinue)
                if (-not $alive) {
                    Write-Host "  pass $pass - ghost PID $procId on port $port (stale socket, skip kill)" -ForegroundColor DarkGray
                    continue
                }

                Write-Host "  pass $pass - stop PID $procId (port $port)" -ForegroundColor DarkGray
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                $null = Start-Process -FilePath "taskkill.exe" -ArgumentList @("/F", "/PID", "$procId") -WindowStyle Hidden -PassThru -ErrorAction SilentlyContinue
            }
        }
        if ($pass -lt 2) { Start-Sleep -Milliseconds 500 }
    }
}

function Assert-FleetPortsAvailable {
    param(
        [Parameter(Mandatory)][int[]]$Ports,
        [string]$Label = "fleet"
    )

    $still = Get-FleetPortsStillListening -Ports $Ports
    if ($still.Count -eq 0) { return $true }

    $liveBlockers = @()
    $ghostBlockers = @()
    foreach ($entry in $still.GetEnumerator()) {
        foreach ($procId in $entry.Value) {
            if ($null -ne (Get-Process -Id $procId -ErrorAction SilentlyContinue)) {
                $liveBlockers += "port $($entry.Key) PID $procId"
            } else {
                $ghostBlockers += "port $($entry.Key) ghost PID $procId"
            }
        }
    }

    if ($liveBlockers.Count -gt 0) {
        Write-Host "[$Label] ERROR: ports still held by live process(es): $($liveBlockers -join '; ')" -ForegroundColor Red
        Write-Host "Close those processes, then re-run start.bat." -ForegroundColor Yellow
        return $false
    }

    if ($ghostBlockers.Count -gt 0) {
        Write-Host "[$Label] WARNING: stale sockets remain ($($ghostBlockers -join '; '))." -ForegroundColor Yellow
        Write-Host "Windows may still block bind until TIME_WAIT clears or after reboot." -ForegroundColor Yellow
    }

    return $true
}

