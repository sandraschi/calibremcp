<#
.SYNOPSIS
    Build script for creating the Calibre MCP DXT package.
.DESCRIPTION
    This script automates the process of creating a DXT package for the Calibre MCP project.
    It ensures all dependencies are installed, runs tests, and creates the DXT package.
#>

param (
    [switch]$NoTests,
    [switch]$NoClean,
    [switch]$Help
)

# Error handling
$ErrorActionPreference = "Stop"

# Display help if requested
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit 0
}

# Configuration
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "python"
$Pip = "pip"
$PackageName = "calibre-mcp"

# Try to get version from dxt_manifest.json
$Version = "0.1.0"
try {
    $manifest = Get-Content "$ProjectRoot\dxt_manifest.json" -Raw | ConvertFrom-Json -ErrorAction Stop
    $Version = $manifest.version
} catch {
    Write-Warning "Could not read version from dxt_manifest.json, using default: $Version"
}

$DistDir = "$ProjectRoot\dist"
$DxtFile = "$DistDir\$PackageName-$Version.dxt"

function Write-Header($text) {
    Write-Host "`n=== $($text.ToUpper()) ===" -ForegroundColor Cyan
}

function Write-Success($text) {
    Write-Host "✓ $text" -ForegroundColor Green
}

function Write-Info($text) {
    Write-Host "ℹ $text" -ForegroundColor Blue
}

try {
    # Check Python version
    Write-Header "Checking Python Version"
    $pythonVersion = & $Python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python is not installed or not in PATH"
    }
    Write-Success "Using Python: $pythonVersion"

    # Clean previous builds
    if (-not $NoClean) {
        Write-Header "Cleaning Previous Builds"
        if (Test-Path $DistDir) {
            Remove-Item -Path $DistDir -Recurse -Force
            Write-Success "Cleaned dist directory"
        } else {
            Write-Info "No previous build to clean"
        }
    }

    # Create virtual environment
    Write-Header "Setting Up Virtual Environment"
    $venvPath = "$ProjectRoot\.venv"
    if (-not (Test-Path $venvPath)) {
        & $Python -m venv $venvPath
        Write-Success "Created virtual environment"
    } else {
        Write-Info "Using existing virtual environment"
    }

    # Activate virtual environment
    $activateScript = "$venvPath\Scripts\Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        throw "Virtual environment activation script not found at $activateScript"
    }
    . $activateScript

    # Install package in development mode
    Write-Header "Installing Dependencies"
    & $Pip install --upgrade pip
    
    # Install development dependencies
    if (Test-Path "$ProjectRoot\requirements-dev.txt") {
        & $Pip install -r "$ProjectRoot\requirements-dev.txt"
    } elseif (Test-Path "$ProjectRoot\requirements.txt") {
        & $Pip install -r "$ProjectRoot\requirements.txt"
    }
    
    # Install in development mode
    & $Pip install -e $ProjectRoot
    
    Write-Success "Dependencies installed successfully"

    # Run tests if not skipped
    if (-not $NoTests) {
        Write-Header "Running Tests"
        & $Python -m pytest -v
        if ($LASTEXITCODE -ne 0) {
            throw "Tests failed. Aborting build."
        }
        Write-Success "All tests passed"
    } else {
        Write-Info "Skipping tests"
    }

    # Build the DXT package
    Write-Header "Building DXT Package"
    & $Python "$ProjectRoot\dxt_build.py"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to build DXT package"
    }

    # Verify the DXT package was created
    if (-not (Test-Path $DxtFile)) {
        throw "DXT package was not created at $DxtFile"
    }
    
    $fileSize = (Get-Item $DxtFile).Length / 1MB
    Write-Success "Successfully created DXT package: $DxtFile (${fileSize:N2} MB)"

    # Display next steps
    Write-Header "Build Complete!"
    Write-Host "To test the DXT package in Claude Desktop:"
    Write-Host "1. Copy the DXT file to your Claude Desktop packages directory"
    Write-Host "2. Restart Claude Desktop"
    Write-Host "3. The Calibre MCP server should start automatically"
    Write-Host "`nDXT Package: $DxtFile"
}
catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
    exit 1
}
finally {
    # Deactivate virtual environment
    if (Get-Command deactivate -ErrorAction SilentlyContinue) {
        deactivate
    }
}
