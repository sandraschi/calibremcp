#Requires -Version 7
<#
.SYNOPSIS
    Fleet release script: mcpb bundle + NSIS installer + GitHub release upload.

.DESCRIPTION
    Triple-play release: builds the mcpb bundle, builds the Tauri NSIS installer,
    creates a GitHub release tag, and uploads all artifacts. Exits at the first
    failed phase -- never uploads a broken artifact.
    On success, opens a self-contained HTML celebration page in the default browser.

    Copy to scripts/release.ps1 in each repo and fill in the PER-REPO CONFIG block.

.PARAMETER DryRun
    Print what would happen without executing any build or upload steps.

.PARAMETER SkipSidecar
    Skip the sidecar smoke test (Phase 2). Only for repos with no HTTP backend.

.PARAMETER SkipMcpb
    Skip the mcpb bundle phase.

.PARAMETER SkipNsis
    Skip the Tauri NSIS build phase. For MCP-only repos with no desktop app.

.PARAMETER SkipUpload
    Build everything but do not create the GitHub release or upload assets.

.EXAMPLE
    pwsh -NoProfile -File scripts/release.ps1
    pwsh -NoProfile -File scripts/release.ps1 -DryRun
    pwsh -NoProfile -File scripts/release.ps1 -SkipSidecar -SkipMcpb
#>
param(
    [switch]$DryRun,
    [switch]$SkipSidecar,
    [switch]$SkipMcpb,
    [switch]$SkipNsis,
    [switch]$SkipUpload
)

$ErrorActionPreference = 'Stop'

# ==============================================================================
# PER-REPO CONFIG -- edit these when copying to a new repo
# ==============================================================================

# HTTP port the sidecar listens on (fleet port registry)
$Port = 10762

# Environment variable that tells the backend it is running under Tauri
$TauriEnvVar = 'WINRARMCP_TAURI'

# A real API route that returns JSON (not /health -- prove feature routes work).
# To find candidates: Get-ChildItem src -Recurse -Filter '*.py' |
#   Select-String '@app.get|@router.get' | Select -First 10
$SmokeRoute = '/api/archive/list'

# mcpb source dir relative to repo root ('.' if packing from root)
$McpbSrcDir = '.'

# Path to the Tauri build script in native/
$NativeBuildScript = 'native\build.ps1'

# Name of the sidecar exe produced by PyInstaller in dist/
$BackendExeName = 'winrar-mcp-backend.exe'

# Name of the main Tauri binary (mainBinaryName in tauri.conf.json)
$NativeExeName = 'winrar-mcp-native.exe'

# Path to Tauri starts shortcut update script (set to '' to skip)
$TauriStartsScript = 'scripts\update-tauri-starts-link.ps1'

# File containing only the latest release notes for the GitHub release body.
# Create manually or extract from CHANGELOG.md before running release.
$ChangelogLatest = 'CHANGELOG_LATEST.md'

# ==============================================================================
# INTERNALS -- do not edit below this line when copying to a new repo
# ==============================================================================

$RepoRoot   = Split-Path -Parent $PSScriptRoot
$RepoName   = Split-Path -Leaf $RepoRoot
$ScriptStart = [datetime]::Now

# Phase timing tracker: phase name -> elapsed seconds
$PhaseTimes = [ordered]@{}

function Write-Phase { param([string]$Msg)
    Write-Host ''
    Write-Host "=== $Msg ===" -ForegroundColor Cyan
}
function Write-Ok   { param([string]$Msg) Write-Host "  [ok] $Msg" -ForegroundColor Green }
function Write-Info { param([string]$Msg) Write-Host "  [..] $Msg" -ForegroundColor Gray }
function Write-Warn { param([string]$Msg) Write-Host "  [!!] $Msg" -ForegroundColor Yellow }

function Write-Fail {
    param([string]$Msg, [string]$Hint = '', [string]$Fix = '')
    Write-Host ''
    Write-Host '  +---------------------------------------------------------+' -ForegroundColor Red
    Write-Host "  | FAIL: $Msg" -ForegroundColor Red
    if ($Hint) { Write-Host "  | WHY:  $Hint" -ForegroundColor Yellow }
    if ($Fix)  { Write-Host "  | FIX:  $Fix"  -ForegroundColor Yellow }
    Write-Host '  +---------------------------------------------------------+' -ForegroundColor Red
    Write-Host ''
    throw $Msg
}

function Assert-Exit {
    param([int]$Code, [string]$Step, [string]$Hint = '', [string]$Fix = '')
    if ($Code -ne 0) {
        Write-Fail "$Step exited with code $Code" $Hint $Fix
    }
}

function Start-Phase { param([string]$Name)
    $script:_phaseStart = [datetime]::Now
    $script:_phaseName  = $Name
}

function End-Phase { param([string]$Name)
    $elapsed = ([datetime]::Now - $script:_phaseStart).TotalSeconds
    $script:PhaseTimes[$Name] = [math]::Round($elapsed, 1)
    Write-Ok "$Name complete ($([math]::Round($elapsed,1))s)"
}

# ------------------------------------------------------------------------------
# Phase 0 -- Preflight
# ------------------------------------------------------------------------------
Write-Phase 'Phase 0 -- Preflight'
Start-Phase 'Preflight'
Set-Location $RepoRoot

# Read version from pyproject.toml
if (-not (Test-Path "$RepoRoot\pyproject.toml")) {
    Write-Fail 'pyproject.toml not found' `
        'This script must be run from a repo with a pyproject.toml at the root.' `
        "Confirm you are in the right repo: $RepoRoot"
}
$pyproject = Get-Content "$RepoRoot\pyproject.toml" -Raw
if ($pyproject -match '(?m)^version = "([^"]+)"') {
    $Version = $Matches[1]
} else {
    Write-Fail 'version not found in pyproject.toml' `
        'Expected a line like: version = "1.2.3" under [project]' `
        'Add or fix the version field in pyproject.toml'
}
$TagName = "v$Version"
Write-Ok "Version: $Version  Tag: $TagName"

if ($DryRun) { Write-Warn 'DRY RUN -- no builds or uploads will be executed' }

# gh CLI required (check early so we fail fast)
if (-not $SkipUpload -and -not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Fail 'gh CLI not found' `
        'The GitHub CLI is required to create releases and upload assets.' `
        'Install: winget install --id GitHub.cli  then: gh auth login'
}

# Git tree clean
$gitStatus = git -C $RepoRoot status --porcelain 2>&1
if ($gitStatus) {
    Write-Fail 'Git working tree is dirty' `
        "Uncommitted changes:`n$gitStatus" `
        'Commit or stash all changes before releasing: git add -A && git commit -m "chore: prepare release"'
}
Write-Ok 'Git tree clean'

# Tag must not already exist locally or on remote
$existingLocal = git -C $RepoRoot tag --list $TagName
if ($existingLocal) {
    Write-Fail "Tag $TagName already exists locally" `
        'A tag with this name was already created, possibly from a failed release.' `
        "Either bump the version in pyproject.toml, or delete the tag: git tag -d $TagName"
}
$existingRemote = git -C $RepoRoot ls-remote --tags origin "refs/tags/$TagName" 2>&1
if ($existingRemote) {
    Write-Fail "Tag $TagName already exists on remote" `
        'This version was already released to GitHub.' `
        "Bump the version in pyproject.toml to release a new version."
}
Write-Ok "Tag $TagName is free (local + remote)"

# No orphan backend or native processes (would lock exe files during build)
$orphanNames = @(($BackendExeName -replace '\.exe$',''), ($NativeExeName -replace '\.exe$',''))
$orphans = Get-Process -Name $orphanNames -ErrorAction SilentlyContinue
if ($orphans) {
    Write-Fail "Orphan processes are running: $($orphans.Name -join ', ')" `
        'These processes lock the exe files that the build needs to overwrite.' `
        'Stop them: Stop-Process -Name winrar-mcp-backend,winrar-mcp-native -Force'
}
Write-Ok 'No orphan processes'

New-Item -ItemType Directory -Force -Path "$RepoRoot\dist" | Out-Null
Write-Ok 'dist/ ready'
End-Phase 'Preflight'

# Collect stats for the success page
$Stats = [ordered]@{
    Repo        = $RepoName
    Version     = $Version
    Tag         = $TagName
    StartTime   = $ScriptStart.ToString('yyyy-MM-dd HH:mm:ss')
    DryRun      = $DryRun.IsPresent
    McpbSize    = 'skipped'
    NsisSize    = 'skipped'
    ReleaseUrl  = ''
    Assets      = @()
}

# ------------------------------------------------------------------------------
# Phase 1 -- mcpb bundle
# ------------------------------------------------------------------------------
if (-not $SkipMcpb) {
    Write-Phase 'Phase 1 -- mcpb bundle'
    Start-Phase 'mcpb'
    $mcpbSrc = Join-Path $RepoRoot $McpbSrcDir
    $mcpbOut = "$RepoRoot\dist\$RepoName-v$Version.mcpb"
    Write-Info "Packing $McpbSrcDir -> dist\$RepoName-v$Version.mcpb"

    if (-not $DryRun) {
        if (-not (Test-Path "$mcpbSrc\manifest.json")) {
            Write-Fail 'manifest.json not found in McpbSrcDir' `
                "Expected: $mcpbSrc\manifest.json" `
                'Create manifest.json per MCPB_PACKAGING_STANDARDS.md or set McpbSrcDir to the correct subdirectory.'
        }

        # Sync canonical server source into mcpb/
        $srcCalibre = Join-Path $RepoRoot "src\calibre_mcp"
        $dstCalibre = Join-Path $mcpbSrc "src\calibre_mcp"
        if (Test-Path $srcCalibre) {
            if (Test-Path $dstCalibre) { Remove-Item $dstCalibre -Recurse -Force }
            Copy-Item -Path $srcCalibre -Destination $dstCalibre -Recurse -Force
            Get-ChildItem -Path $dstCalibre -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
                ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
        }

        Push-Location $mcpbSrc
        npx @anthropic-ai/mcpb pack . $mcpbOut
        Assert-Exit $LASTEXITCODE 'mcpb pack' `
            'npx @anthropic-ai/mcpb pack failed.' `
            'Check manifest.json is valid. Run: npx @anthropic-ai/mcpb validate manifest.json'
        Pop-Location

        Copy-Item $mcpbOut "$RepoRoot\dist\calibre-mcp.mcpb" -Force

        npx @anthropic-ai/mcpb validate $mcpbOut
        Assert-Exit $LASTEXITCODE 'mcpb validate' `
            'The generated .mcpb bundle failed validation.' `
            'Inspect the bundle: npx @anthropic-ai/mcpb inspect dist\*.mcpb'

        $sizeMb = (Get-Item $mcpbOut).Length / 1MB
        if ($sizeMb -gt 100) {
            Write-Fail "Bundle is $([math]::Round($sizeMb,1)) MB -- almost certainly wrong pack root" `
                'mcpb should pack only src/ + manifest.json + assets/. At 100MB+ it has packed node_modules or .venv.' `
                'Set McpbSrcDir to the mcpb/ subdirectory, or fix .mcpbignore to exclude large directories.'
        }
        if ($sizeMb -gt 5) { Write-Warn "Bundle is $([math]::Round($sizeMb,1)) MB (expected <5 MB). Review .mcpbignore." }
        else                { Write-Ok   "Bundle: $([math]::Round($sizeMb,2)) MB" }

        $Stats.McpbSize = "$([math]::Round($sizeMb,2)) MB"
        $Stats.Assets  += "$RepoName-v$Version.mcpb ($([math]::Round($sizeMb,2)) MB)"
    } else {
        Write-Warn '[DRY RUN] Would: bunx mcpb pack + validate'
    }
    End-Phase 'mcpb'
} else {
    Write-Warn 'Phase 1 (mcpb) skipped'
}

# ------------------------------------------------------------------------------
# Phase 2 -- Sidecar smoke test  [HARD GATE -- no --force override]
# ------------------------------------------------------------------------------
if (-not $SkipSidecar -and -not $SkipNsis) {
    Write-Phase 'Phase 2 -- Sidecar smoke test [HARD GATE]'
    Start-Phase 'Smoke'
    $sidecarExe = "$RepoRoot\dist\$BackendExeName"

    if (-not $DryRun) {
        if (-not (Test-Path $sidecarExe)) {
            Write-Info "Sidecar not found in dist/ -- running $NativeBuildScript to produce it..."
            pwsh -NoProfile -File "$RepoRoot\$NativeBuildScript"
            Assert-Exit $LASTEXITCODE 'sidecar build' `
                "$NativeBuildScript failed." `
                'Fix PyInstaller errors first. Check build output above and warn-*.txt in build/.'
        }
        if (-not (Test-Path $sidecarExe)) {
            Write-Fail "Sidecar exe still missing after build" `
                "Expected: $sidecarExe" `
                'Check the PyInstaller spec file output path matches dist\$BackendExeName.'
        }

        Write-Info "Spawning sidecar on port $Port (20s warmup)..."
        $env:PORT = "$Port"
        Set-Item -Path "Env:$TauriEnvVar" -Value '1'
        $proc = Start-Process $sidecarExe -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 20

        try {
            # /health check
            try {
                $health = Invoke-WebRequest "http://127.0.0.1:$Port/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            } catch {
                Write-Fail '/health request failed -- sidecar did not start' `
                    "Could not reach http://127.0.0.1:$Port/health after 20s warmup." `
                    'Check for import errors: run the exe manually in a terminal and inspect stderr. Common causes: missing hiddenimports in .spec, wrong PORT env var, cachetools/joserfc missing.'
            }
            if ($health.StatusCode -ne 200) {
                Write-Fail "/health returned HTTP $($health.StatusCode)" `
                    'The sidecar started but /health is not returning 200.' `
                    'Check your health endpoint implementation returns status 200 with a JSON body.'
            }
            Write-Ok '/health -> 200'

            # Feature route check
            try {
                $feature = Invoke-WebRequest "http://127.0.0.1:$Port$SmokeRoute" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            } catch [System.Net.WebException] {
                $respCode = [int]$_.Exception.Response.StatusCode
                if ($respCode -eq 404) {
                    Write-Host ''
                    Write-Host '  +---------------------------------------------------------+' -ForegroundColor Red
                    Write-Host "  | TODO: SmokeRoute '$SmokeRoute' returned 404"             -ForegroundColor Red
                    Write-Host '  | This route does not exist in the frozen backend.'        -ForegroundColor Red
                    Write-Host '  | Update $SmokeRoute in scripts\release.ps1 to a real'    -ForegroundColor Red
                    Write-Host '  | API route that returns JSON for this repo.'              -ForegroundColor Red
                    Write-Host '  |'                                                         -ForegroundColor Yellow
                    Write-Host '  | Find candidates:'                                        -ForegroundColor Yellow
                    Write-Host "  |   Get-ChildItem $RepoRoot\src -Recurse -Filter '*.py' |" -ForegroundColor Yellow
                    Write-Host "  |   Select-String '@app.get|@router.get' | Select -First 10" -ForegroundColor Yellow
                    Write-Host '  +---------------------------------------------------------+' -ForegroundColor Red
                    Write-Host ''
                    throw "SmokeRoute not found (404). Fix `$SmokeRoute in scripts\release.ps1."
                }
                if ($respCode -eq 401 -or $respCode -eq 403) {
                    Write-Fail "$SmokeRoute returned HTTP $respCode (auth required)" `
                        'The smoke route requires authentication. Use an unauthenticated health/status route.' `
                        "Update `$SmokeRoute in scripts\release.ps1 to an open endpoint."
                }
                Write-Fail "$SmokeRoute request failed (HTTP $respCode)" `
                    "Unexpected HTTP error on the feature route." `
                    'Check server logs for the error and ensure the route is implemented in the frozen build.'
            }

            $ct = $feature.Headers['Content-Type']
            if ($ct -notmatch 'application/json') {
                Write-Fail "$SmokeRoute returned Content-Type '$ct'" `
                    'Expected application/json. Got HTML or plain text -- likely an error page.' `
                    "Confirm the route returns JSON in the frozen build. Check SmokeRoute: $SmokeRoute"
            }
            try {
                $null = $feature.Content | ConvertFrom-Json -ErrorAction Stop
            } catch {
                Write-Fail "$SmokeRoute response is not valid JSON" `
                    'Content-Type was application/json but the body could not be parsed.' `
                    'Check for encoding issues or partial responses in the frozen backend.'
            }
            Write-Ok "$SmokeRoute -> valid JSON"

        } finally {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            Remove-Item -Path 'Env:PORT'          -ErrorAction SilentlyContinue
            Remove-Item -Path "Env:$TauriEnvVar"  -ErrorAction SilentlyContinue
        }
    } else {
        Write-Warn "[DRY RUN] Would: spawn sidecar, check /health and $SmokeRoute"
    }
    End-Phase 'Smoke'
} else {
    if ($SkipSidecar) { Write-Warn 'Phase 2 skipped (-SkipSidecar)' }
    if ($SkipNsis)    { Write-Warn 'Phase 2 skipped (no NSIS build requested)' }
}

# ------------------------------------------------------------------------------
# Phase 3 -- Tauri NSIS build
# ------------------------------------------------------------------------------
if (-not $SkipNsis) {
    Write-Phase 'Phase 3 -- Tauri NSIS build'
    Start-Phase 'NSIS'
    Write-Info "Running $NativeBuildScript..."

    if (-not (Test-Path "$RepoRoot\$NativeBuildScript")) {
        Write-Fail "Build script not found: $NativeBuildScript" `
            'The Tauri native build script is missing.' `
            "Create native\build.ps1 per TAURI_PRODUCTION_PITFALLS.md or set `$NativeBuildScript correctly."
    }

    if (-not $DryRun) {
        pwsh -NoProfile -File "$RepoRoot\$NativeBuildScript"
        Assert-Exit $LASTEXITCODE 'Tauri NSIS build' `
            'native\build.ps1 failed.' `
            'Check Tauri build output above. Common causes: TypeScript errors, PyInstaller spec issues, Rust compile errors. See TAURI_PRODUCTION_PITFALLS.md.'

        # Remove stale shadow exe
        $shadow = "$RepoRoot\native\target\release\$BackendExeName"
        if (Test-Path $shadow) {
            Remove-Item $shadow -Force
            Write-Info "Removed stale shadow: $shadow"
        }

        $installer = Get-ChildItem "$RepoRoot\dist" -Filter '*-setup.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $installer) {
            Write-Fail 'No *-setup.exe found in dist/ after Tauri build' `
                'Tauri reported success but the NSIS installer was not staged to dist/.' `
                'Check native\build.ps1 -- the Copy-Item step that moves bundle/nsis/*.exe to dist/ may have failed.'
        }
        $sizeMb = [math]::Round($installer.Length / 1MB, 1)
        Write-Ok "Installer: $($installer.Name) ($sizeMb MB)"
        $Stats.NsisSize = "$sizeMb MB"
        $Stats.Assets  += "$($installer.Name) ($sizeMb MB)"
    } else {
        Write-Warn '[DRY RUN] Would: run native/build.ps1 and verify *-setup.exe'
    }
    End-Phase 'NSIS'
} else {
    Write-Warn 'Phase 3 (NSIS) skipped'
}

# ------------------------------------------------------------------------------
# Phase 4 -- Tag and GitHub release
# ------------------------------------------------------------------------------
if (-not $SkipUpload) {
    Write-Phase "Phase 4 -- GitHub release $TagName"
    Start-Phase 'Upload'

    # Collect assets that actually exist
    $assets = @()
    if (-not $SkipMcpb) {
        $a = "$RepoRoot\dist\$RepoName-v$Version.mcpb"
        if (Test-Path $a) { $assets += $a }
        else { Write-Warn "mcpb asset missing -- it will not be uploaded: $a" }
        $alias = "$RepoRoot\dist\$RepoName.mcpb"
        if (Test-Path $alias) { $assets += $alias }
    }
    if (-not $SkipNsis) {
        $a = Get-ChildItem "$RepoRoot\dist" -Filter '*-setup.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($a) { $assets += $a.FullName }
        else    { Write-Warn 'No *-setup.exe in dist/ -- installer will not be uploaded' }
    }
    if ($assets.Count -eq 0) {
        Write-Fail 'No release assets to upload' `
            'Both mcpb and NSIS assets are missing from dist/.' `
            'Run without -SkipMcpb and -SkipNsis, or check that the build phases completed successfully.'
    }

    Write-Info "Assets ($($assets.Count)):"
    foreach ($a in $assets) { Write-Info "  $(Split-Path -Leaf $a)" }

    # Release notes
    $notesArgs = if (Test-Path "$RepoRoot\$ChangelogLatest") {
        Write-Info "Notes from $ChangelogLatest"
        @('--notes-file', "$RepoRoot\$ChangelogLatest")
    } else {
        Write-Warn "$ChangelogLatest not found -- GitHub will auto-generate release notes"
        Write-Warn "Create $ChangelogLatest with this release's notes for better release quality"
        @('--generate-notes')
    }

    if (-not $DryRun) {
        # Tag
        git -C $RepoRoot tag $TagName
        Assert-Exit $LASTEXITCODE 'git tag' `
            "Failed to create local tag $TagName." `
            'Check git is available and the repo has at least one commit.'

        git -C $RepoRoot push origin $TagName
        Assert-Exit $LASTEXITCODE 'git push tag' `
            "Failed to push tag $TagName to origin." `
            'Check your GitHub auth: gh auth status. Ensure origin remote is set: git remote -v'
        Write-Ok "Pushed tag $TagName"

        # Create release
        $ghArgs = @('release', 'create', $TagName, '--title', "$RepoName $TagName") + $notesArgs
        gh @ghArgs
        Assert-Exit $LASTEXITCODE 'gh release create' `
            'Failed to create GitHub release.' `
            'Check gh auth status and that the repo exists on GitHub. Run: gh auth login'

        # Upload assets
        foreach ($a in $assets) {
            $leaf = Split-Path -Leaf $a
            gh release upload $TagName $a --clobber
            Assert-Exit $LASTEXITCODE "gh release upload $leaf" `
                "Failed to upload $leaf to GitHub release $TagName." `
                'Check file exists, GitHub auth is valid, and the release was created successfully.'
            Write-Ok "Uploaded: $leaf"
        }

        $Stats.ReleaseUrl = "https://github.com/sandraschi/$RepoName/releases/tag/$TagName"
    } else {
        Write-Warn "[DRY RUN] Would: git tag $TagName && push"
        Write-Warn "[DRY RUN] Would: gh release create + upload $($assets.Count) asset(s)"
        $Stats.ReleaseUrl = "https://github.com/sandraschi/$RepoName/releases/tag/$TagName (dry run)"
    }
    End-Phase 'Upload'
} else {
    Write-Warn 'Phase 4 (upload) skipped'
}

# ------------------------------------------------------------------------------
# Phase 5 -- Post-release housekeeping
# ------------------------------------------------------------------------------
Write-Phase 'Phase 5 -- Post-release'

if ($TauriStartsScript -and -not $SkipNsis -and (Test-Path "$RepoRoot\$TauriStartsScript")) {
    if (-not $DryRun) {
        pwsh -NoProfile -File "$RepoRoot\$TauriStartsScript"
        Assert-Exit $LASTEXITCODE 'update-tauri-starts-link' `
            'The Tauri starts shortcut update script failed.' `
            "Check $TauriStartsScript -- it should update D:\Dev\Tauri starts\$RepoName-setup.lnk"
        Write-Ok 'Updated Tauri starts shortcut'
    } else {
        Write-Warn "[DRY RUN] Would run $TauriStartsScript"
    }
}

$TotalSecs = [math]::Round(([datetime]::Now - $ScriptStart).TotalSeconds, 1)
$Stats.TotalTime = "${TotalSecs}s"

# ------------------------------------------------------------------------------
# Success page
# ------------------------------------------------------------------------------
$phaseRows = ''
foreach ($k in $PhaseTimes.Keys) {
    $secs = $PhaseTimes[$k]
    $bar  = [math]::Min([math]::Round($secs / 2), 60)
    $phaseRows += "<tr><td>$k</td><td>${secs}s</td><td><div class='bar' style='width:${bar}px'></div></td></tr>`n"
}

$assetRows = ''
foreach ($a in $Stats.Assets) {
    $assetRows += "<tr><td>$a</td></tr>`n"
}
if (-not $assetRows) { $assetRows = '<tr><td style="color:#666">No assets (skipped or dry run)</td></tr>' }

$releaseLink = if ($Stats.ReleaseUrl) {
    "<a href='$($Stats.ReleaseUrl)' target='_blank'>$($Stats.ReleaseUrl)</a>"
} else { '<span style="color:#666">Not uploaded</span>' }

$dryBanner = if ($DryRun) { '<div class="dry-banner">DRY RUN -- nothing was actually built or uploaded</div>' } else { '' }

$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>$RepoName $TagName Released</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #09090b; color: #e4e4e7; font-family: 'Inter', 'Segoe UI', sans-serif;
         min-height: 100vh; display: flex; flex-direction: column; align-items: center;
         padding: 48px 24px; }
  .card { background: #18181b; border: 1px solid #27272a; border-radius: 16px;
          max-width: 680px; width: 100%; padding: 40px; margin-bottom: 24px; }
  .hero { text-align: center; padding: 56px 24px 40px; }
  .emoji { font-size: 72px; display: block; margin-bottom: 16px; animation: pop .5s ease; }
  @keyframes pop { 0%{transform:scale(0.5);opacity:0} 80%{transform:scale(1.1)} 100%{transform:scale(1);opacity:1} }
  .hero h1 { font-size: 2rem; font-weight: 700; color: #fbbf24; margin-bottom: 8px; }
  .hero .sub { color: #a1a1aa; font-size: 1rem; }
  .dry-banner { background: #78350f; color: #fde68a; border-radius: 8px; padding: 12px 20px;
                text-align: center; font-weight: 600; margin-bottom: 20px; }
  h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: .1em;
       color: #71717a; margin-bottom: 16px; }
  table { width: 100%; border-collapse: collapse; }
  td { padding: 8px 0; border-bottom: 1px solid #27272a; font-size: 0.9rem; color: #d4d4d8; }
  td:first-child { color: #a1a1aa; width: 120px; }
  tr:last-child td { border-bottom: none; }
  .bar { height: 8px; background: linear-gradient(90deg,#f59e0b,#fbbf24); border-radius: 4px;
         min-width: 4px; }
  a { color: #fbbf24; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .total { font-size: 0.85rem; color: #71717a; text-align: center; margin-top: 8px; }
  .confetti { position: fixed; top: 0; left: 0; width: 100%; height: 100%;
              pointer-events: none; overflow: hidden; z-index: 0; }
  .piece { position: absolute; width: 8px; height: 8px; opacity: 0;
           animation: fall linear forwards; border-radius: 2px; }
  @keyframes fall {
    0%   { transform: translateY(-20px) rotate(0deg);   opacity: 1; }
    100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
  }
</style>
</head>
<body>
<div class="confetti" id="cf"></div>

<div class="card hero">
  $dryBanner
  <span class="emoji">🎉</span>
  <h1>$RepoName $TagName shipped!</h1>
  <div class="sub">$($Stats.StartTime) &nbsp;|&nbsp; $($Stats.TotalTime) total</div>
</div>

<div class="card">
  <h2>Release details</h2>
  <table>
    <tr><td>Repo</td>    <td>$($Stats.Repo)</td></tr>
    <tr><td>Version</td> <td>$($Stats.Version)</td></tr>
    <tr><td>Tag</td>     <td>$($Stats.Tag)</td></tr>
    <tr><td>URL</td>     <td>$releaseLink</td></tr>
    <tr><td>mcpb</td>    <td>$($Stats.McpbSize)</td></tr>
    <tr><td>NSIS</td>    <td>$($Stats.NsisSize)</td></tr>
  </table>
</div>

<div class="card">
  <h2>Uploaded assets</h2>
  <table>$assetRows</table>
</div>

<div class="card">
  <h2>Phase timings</h2>
  <table>$phaseRows</table>
  <div class="total">Total wall time: $($Stats.TotalTime)</div>
</div>

<script>
const cf = document.getElementById('cf');
const colors = ['#fbbf24','#f59e0b','#34d399','#60a5fa','#f472b6','#a78bfa'];
for (let i = 0; i < 120; i++) {
  const p = document.createElement('div');
  p.className = 'piece';
  p.style.left = Math.random() * 100 + 'vw';
  p.style.background = colors[Math.floor(Math.random() * colors.length)];
  p.style.width  = (6 + Math.random() * 8) + 'px';
  p.style.height = (6 + Math.random() * 8) + 'px';
  p.style.animationDuration  = (2 + Math.random() * 3) + 's';
  p.style.animationDelay     = (Math.random() * 2) + 's';
  cf.appendChild(p);
}
</script>
</body>
</html>
"@

$htmlPath = "$env:TEMP\release-$RepoName-$Version.html"
$html | Set-Content $htmlPath -Encoding utf8
Start-Process $htmlPath

Write-Host ''
Write-Host "=== $RepoName $TagName released in ${TotalSecs}s ===" -ForegroundColor Green
if ($Stats.ReleaseUrl) {
    Write-Host "    $($Stats.ReleaseUrl)" -ForegroundColor Cyan
}
Write-Host ''
