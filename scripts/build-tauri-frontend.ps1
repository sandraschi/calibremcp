#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build Next.js frontend for Tauri (static export, API routes disabled).
#>
param(
    [string]$FrontendDir
)
$ErrorActionPreference = "Stop"

$ApiDir = Join-Path $FrontendDir "app\api"
$ApiBackup = Join-Path $FrontendDir "app\_api_tauri_backup"
$HealthRoute = Join-Path $FrontendDir "app\health"
$HealthBackup = Join-Path $FrontendDir "app\_health_tauri_backup"

$movedApi = $false
$movedHealth = $false

try {
    if (Test-Path $ApiDir) {
        Move-Item $ApiDir $ApiBackup -Force
        $movedApi = $true
    }
    if (Test-Path $HealthRoute) {
        Move-Item $HealthRoute $HealthBackup -Force
        $movedHealth = $true
    }

    $env:TAURI_BUILD = "1"
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "next build failed (exit $LASTEXITCODE)" }
} finally {
    if ($movedApi) { Move-Item $ApiBackup $ApiDir -Force }
    if ($movedHealth) { Move-Item $HealthBackup $HealthRoute -Force }
    Remove-Item Env:TAURI_BUILD -ErrorAction SilentlyContinue
}
