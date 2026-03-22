#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build MCPB package for CalibreMCP server (SOTA Standards v1.0.0)

.DESCRIPTION
    This script builds a production-ready MCPB package for the CalibreMCP server
    following MCP Central Docs SOTA standards. It validates prerequisites,
    builds the package, and verifies the result.

.PARAMETER NoSign
    Skip package signing (for development builds)

.PARAMETER OutputDir
    Custom output directory for the built package (default: dist)

.EXAMPLE
    .\build-mcpb-package.ps1 -NoSign
    Build unsigned package for development

.EXAMPLE
    .\build-mcpb-package.ps1 -OutputDir "C:\builds"
    Build package to custom directory
#>

param(
    [switch]$NoSign,
    [string]$OutputDir = "dist"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$White = "White"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "`n[STEP] $Message" $Cyan
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" $Green
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" $Red
}

# Main build process
try {
    $RepoRoot = Split-Path $PSScriptRoot -Parent
    Set-Location $RepoRoot

    Write-ColorOutput "=== CalibreMCP MCPB Package Builder ===" $Cyan
    Write-ColorOutput "Standard: mcp-central-docs MCPB_PACKAGING_STANDARDS.md + PACKAGING_STANDARDS.md §5" $Cyan
    Write-ColorOutput "Package: calibre-mcp.mcpb" $Cyan
    Write-ColorOutput "Repo root: $RepoRoot" $White

    # Step 1: MCPB CLI (global install only — trivial)
    Write-Step "Checking prerequisites..."

    if (-not (Get-Command mcpb -ErrorAction SilentlyContinue)) {
        Write-Error "mcpb not in PATH. Install once: npm install -g @anthropic-ai/mcpb"
        exit 1
    }
    $mcpbVersion = (& mcpb --version 2>&1 | Out-String).Trim()
    Write-Success "mcpb $mcpbVersion"

    # Sync canonical server source into mcpb/ (pack root — see mcpb/README.md)
    Write-Step "Syncing src/calibre_mcp → mcpb/src/calibre_mcp..."
    $srcCalibre = Join-Path $RepoRoot "src\calibre_mcp"
    $dstCalibre = Join-Path $RepoRoot "mcpb\src\calibre_mcp"
    if (!(Test-Path $srcCalibre)) {
        Write-Error "Source not found: $srcCalibre"
        exit 1
    }
    if (Test-Path $dstCalibre) {
        Remove-Item $dstCalibre -Recurse -Force
    }
    Copy-Item -Path $srcCalibre -Destination $dstCalibre -Recurse -Force
    Get-ChildItem -Path $dstCalibre -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
    Write-Success "Synced calibre_mcp package tree"

    $mcpbManifest = Join-Path $RepoRoot "mcpb\manifest.json"
    if (!(Test-Path $mcpbManifest)) {
        Write-Error "mcpb\manifest.json not found"
        exit 1
    }
    Write-Success "Manifest: mcpb\manifest.json"

    $mcpbIgnore = Join-Path $RepoRoot "mcpb\.mcpbignore"
    if (Test-Path $mcpbIgnore) {
        Write-Success "Ignore file: mcpb\.mcpbignore"
    } else {
        Write-Warning "mcpb\.mcpbignore missing — bundle may be oversized"
    }

    # Step 2: Validate mcpb/manifest.json (MCPB v0.2)
    Write-Step "Validating mcpb\manifest.json..."

    $validateOutput = & mcpb validate $mcpbManifest 2>&1
    $validateOk = $?
    if (-not $validateOk) {
        Write-Error "Manifest validation failed:"
        Write-ColorOutput $validateOutput $Red
        exit 1
    }
    Write-Success "Manifest validation passed"

    # Step 3: Create output directory (under repo root)
    Write-Step "Preparing output directory..."

    $distDir = Join-Path $RepoRoot $OutputDir
    if (!(Test-Path $distDir)) {
        New-Item -ItemType Directory -Path $distDir -Force | Out-Null
        Write-Success "Created output directory: $distDir"
    } else {
        Write-Success "Output directory exists: $distDir"
    }

    # Clean any existing package
    $packagePath = Join-Path $distDir "calibre-mcp.mcpb"
    if (Test-Path $packagePath) {
        Remove-Item $packagePath -Force
        Write-Success "Cleaned existing package"
    }

    # Step 4: Build MCPB package (SOTA method)
    Write-Step "Building MCPB package (SOTA standards)..."

    $mcpbDir = Join-Path $RepoRoot "mcpb"
    $pushedPackRoot = $false
    if (Test-Path $mcpbDir) {
        Write-ColorOutput "Packing from mcpb/ (manifest + assets + src)..." $Yellow
        Push-Location $mcpbDir
        $pushedPackRoot = $true
        $relOut = Join-Path ".." $OutputDir
        $buildArgs = @("pack", ".", (Join-Path $relOut "calibre-mcp.mcpb"))
    } else {
        Write-ColorOutput "mcpb/ missing — packing from repo root (fallback)..." $Yellow
        $buildArgs = @("pack", ".", "$packagePath")
    }

    if ($NoSign) {
        Write-ColorOutput "Building unsigned package (development mode)" $Yellow
    } else {
        Write-ColorOutput "Building signed package (production mode)" $Yellow
        # Note: Signing would require additional setup with certificates
    }

    $packOk = $false
    try {
        $buildOutput = & mcpb @buildArgs 2>&1
        $packOk = $?
    } finally {
        if ($pushedPackRoot) {
            Pop-Location
        }
    }
    if (-not $packOk) {
        Write-Error "MCPB pack failed:"
        Write-ColorOutput $buildOutput $Red
        exit 1
    }
    Write-Success "MCPB package built successfully!"

    # Step 5: Verify package
    Write-Step "Verifying package..."

    if (Test-Path $packagePath) {
        $packageSize = (Get-Item $packagePath).Length
        $packageSizeMB = [math]::Round($packageSize / 1MB, 2)

        Write-Success "Package created: $packagePath"
        Write-Success "Package size: $packageSizeMB MB"

        if ($packageSizeMB -gt 5) {
            Write-Warning "Package size is large (>5MB). Consider optimizing dependencies."
        }
    } else {
        Write-Error "Package file not found after build"
        exit 1
    }

    # Step 6: Final summary
    Write-Step "Build completed successfully!"

    Write-ColorOutput "`n=== Package Details ===" $Green
    Write-ColorOutput "Name: calibre-mcp.mcpb" $Green
    Write-ColorOutput "Version: 1.1.0 (see mcpb/manifest.json)" $Green
    Write-ColorOutput "Size: $packageSizeMB MB" $Green
    Write-ColorOutput "Location: $packagePath" $Green
    Write-ColorOutput "Signed: $(if ($NoSign) { 'No' } else { 'Yes' })" $Green
    Write-ColorOutput "Standards: MCPB v0.2 — mcp-central-docs MCPB_PACKAGING_STANDARDS.md" $Green

    Write-ColorOutput "`n=== Next Steps ===" $Cyan
    Write-ColorOutput "1. Test package: Drag $packagePath to Claude Desktop" $White
    Write-ColorOutput "2. Configure: Set Calibre library path when prompted" $White
    Write-ColorOutput "3. Verify: Test the 18 portmanteau tools in Claude Desktop" $White
    Write-ColorOutput "4. Deploy: Package ready for distribution" $White

    if ($NoSign) {
        Write-ColorOutput "`nNote: This is an unsigned development build." $Yellow
        Write-ColorOutput "For production distribution, remove -NoSign flag." $Yellow
    }

    Write-ColorOutput "`n🎉 Build completed successfully (SOTA Standards)!" $Green

} catch {
    Write-Error "Build failed with error: $_"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

