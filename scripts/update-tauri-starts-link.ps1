#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Point a D:\Dev\Tauri starts shortcut at the newest NSIS *-setup.exe.
#>
param(
    [string]$TauriStartsDir = "D:\Dev\Tauri starts",
    [string]$ShortcutName = "calibre-mcp-setup.lnk",
    [string]$NsisDir = "",
    [string]$InstallerPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $InstallerPath) {
    if (-not $NsisDir) {
        $repoRoot = Split-Path -Parent $PSScriptRoot
        $NsisDir = Join-Path $repoRoot "native\target\release\bundle\nsis"
    }
    if (-not (Test-Path $NsisDir)) {
        Write-Warning "NSIS bundle dir not found: $NsisDir"
        exit 0
    }
    $installer = Get-ChildItem -Path $NsisDir -Filter "*-setup.exe" -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $installer) {
        Write-Warning "No *-setup.exe found in $NsisDir"
        exit 0
    }
    $InstallerPath = $installer.FullName
}

if (-not (Test-Path $InstallerPath)) {
    Write-Warning "Installer not found: $InstallerPath"
    exit 0
}

if (-not (Test-Path $TauriStartsDir)) {
    New-Item -ItemType Directory -Path $TauriStartsDir -Force | Out-Null
}

$installerItem = Get-Item $InstallerPath
$lnkPath = Join-Path $TauriStartsDir $ShortcutName
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($lnkPath)
$shortcut.TargetPath = $installerItem.FullName
$shortcut.WorkingDirectory = $installerItem.DirectoryName
$shortcut.Description = "Latest calibre-mcp NSIS installer"
$shortcut.Save()

Write-Host "Tauri starts: $lnkPath -> $($installerItem.Name)" -ForegroundColor Cyan
