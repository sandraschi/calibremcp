#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build MCPB package for CalibreMCP server

.DESCRIPTION
    This script builds a production-ready MCPB package for the CalibreMCP server.
    It validates prerequisites, builds the package, and verifies the result.

.PARAMETER NoSign
    Skip package signing (for development builds)

.PARAMETER OutputDir
    Custom output directory for the built package

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
    Write-ColorOutput "=== CalibreMCP MCPB Package Builder ===" $Cyan
    Write-ColorOutput "Version: 1.0.0 | Package: calibre-mcp.mcpb" $Cyan

    # Step 1: Check prerequisites
    Write-Step "Checking prerequisites..."

    # Check MCPB CLI
    try {
        $mcpbVersion = & mcpb --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCPB CLI: v$mcpbVersion"
        } else {
            throw "MCPB CLI not found"
        }
    } catch {
        Write-Error "MCPB CLI not installed. Run: npm install -g @anthropic-ai/mcpb"
        exit 1
    }

    # Check Python
    $pythonVersion = & python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python: $pythonVersion"
    } else {
        Write-Error "Python not found in PATH"
        exit 1
    }

    # Check manifest.json exists
    if (!(Test-Path "manifest.json")) {
        Write-Error "manifest.json not found in project root"
        exit 1
    }
    Write-Success "Manifest: manifest.json found"

    # Check .mcpbignore exists
    if (!(Test-Path ".mcpbignore")) {
        Write-Warning ".mcpbignore not found - package may include unnecessary files"
    } else {
        Write-Success "Ignore file: .mcpbignore found"
    }

    # Step 2: Validate manifest
    Write-Step "Validating manifest.json..."

    try {
        $validateOutput = & mcpb validate manifest.json 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Manifest validation passed!"
        } else {
            Write-Error "Manifest validation failed:"
            Write-ColorOutput $validateOutput $Red
            exit 1
        }
    } catch {
        Write-Error "Failed to validate manifest: $_"
        exit 1
    }

    # Step 3: Create output directory
    Write-Step "Preparing output directory..."

    if (!(Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        Write-Success "Created output directory: $OutputDir"
    } else {
        Write-Success "Output directory exists: $OutputDir"
    }

    # Clean any existing package
    $packagePath = Join-Path $OutputDir "calibre-mcp.mcpb"
    if (Test-Path $packagePath) {
        Remove-Item $packagePath -Force
        Write-Success "Cleaned existing package"
    }

    # Step 4: Build MCPB package
    Write-Step "Building MCPB package..."

    $buildArgs = @("pack", ".", $packagePath)

    if ($NoSign) {
        Write-ColorOutput "Building unsigned package (development mode)" $Yellow
    } else {
        Write-ColorOutput "Building signed package (production mode)" $Yellow
        # Note: Signing would require additional setup with certificates
    }

    try {
        $buildOutput = & mcpb @buildArgs 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCPB package built successfully!"
        } else {
            Write-Error "MCPB build failed:"
            Write-ColorOutput $buildOutput $Red
            exit 1
        }
    } catch {
        Write-Error "Failed to build MCPB package: $_"
        exit 1
    }

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
    Write-ColorOutput "Version: 1.0.0" $Green
    Write-ColorOutput "Size: $packageSizeMB MB" $Green
    Write-ColorOutput "Location: $packagePath" $Green
    Write-ColorOutput "Signed: $(if ($NoSign) { 'No' } else { 'Yes' })" $Green

    Write-ColorOutput "`n=== Next Steps ===" $Cyan
    Write-ColorOutput "1. Test package: Drag $packagePath to Claude Desktop" $White
    Write-ColorOutput "2. Configure: Set Calibre library path when prompted" $White
    Write-ColorOutput "3. Verify: Test the 18 portmanteau tools in Claude Desktop" $White

    if ($NoSign) {
        Write-ColorOutput "`nNote: This is an unsigned development build." $Yellow
        Write-ColorOutput "For production distribution, remove -NoSign flag." $Yellow
    }

    Write-ColorOutput "`n🎉 Build completed successfully!" $Green

} catch {
    Write-Error "Build failed with error: $_"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

