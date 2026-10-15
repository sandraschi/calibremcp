#Requires -Version 5.1
<#
.SYNOPSIS
    Pre-commit guard: start files need deliberate commits.

.DESCRIPTION
    Blocks commits that touch start.ps1 / start.bat / fleet-start.config.ps1
    unless the commit message contains "start:". Start files are the most
    frequently broken files in the fleet (2026-10-15: a version bump + locked
    venv exe killed calibre-mcp startup); they must change deliberately and
    reviewably, never as drive-by edits. Failing commit? Reword with
    "start:" in the message (e.g. "start: tolerate locked-exe sync failure").
#>

$ErrorActionPreference = 'Continue'

# Message file: git passes it as argv[0] in the commit-msg stage; fall back
# to COMMIT_EDITMSG (present for -e flows and manual runs).
$msgFileArg = $args[0]

$guarded = @('start.ps1', 'start.bat', 'fleet-start.config.ps1')

$staged = & git diff --cached --name-only 2>$null
if ($LASTEXITCODE -ne 0) { exit 0 }

$hit = @($staged | Where-Object {
    $leaf = Split-Path $_ -Leaf
    $guarded -contains $leaf
})

if ($hit.Count -eq 0) { exit 0 }

$msg = ''
try {
    $candidates = @()
    if ($msgFileArg) { $candidates += $msgFileArg }
    $gitDir = (git rev-parse --git-dir 2>$null).Trim()
    if ($gitDir) { $candidates += (Join-Path $gitDir 'COMMIT_EDITMSG') }
    foreach ($cand in $candidates) {
        if ($cand -and (Test-Path -LiteralPath $cand)) {
            $msg = [string](Get-Content -Raw -LiteralPath $cand -ErrorAction Stop)
            break
        }
    }
} catch {
    $msg = ''
}

if ($msg -match 'start:') { exit 0 }

Write-Host ''
Write-Host 'BLOCKED: this commit touches start file(s):' -ForegroundColor Red
$hit | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
Write-Host ''
Write-Host 'Start files break the whole repo when edited casually.' -ForegroundColor Red
Write-Host 'Reword your message to include "start:" (e.g. "start: ..."),' -ForegroundColor Yellow
Write-Host 'or unstage these files if the change was accidental.' -ForegroundColor Yellow
exit 1
