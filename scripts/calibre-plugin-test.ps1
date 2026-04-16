# calibre-plugin-test.ps1
# Test loop for CalibreMCP Integration plugin.
# Run from D:\Dev\repos\calibre-mcp or anywhere — uses full paths throughout.

$CALIBRE      = "C:\Program Files\calibre2"
$CUSTOMIZE    = "$CALIBRE\calibre-customize.exe"
$DEBUG        = "$CALIBRE\calibre-debug.exe"
$CALIBRE_EXE  = "$CALIBRE\calibre.exe"
$PLUGIN_DIR   = "D:\Dev\repos\calibre-mcp\calibre_plugin"
$ZIP          = "D:\Dev\repos\calibre-mcp\calibre_mcp_integration.zip"
$PLUGIN_NAME  = "CalibreMCP Integration"

function Build-Plugin {
    Write-Host "Building ZIP..." -ForegroundColor Cyan
    if (Test-Path $ZIP) { Remove-Item $ZIP -Force }
    Compress-Archive -Path "$PLUGIN_DIR\*" -DestinationPath $ZIP -Force
    $size = (Get-Item $ZIP).Length
    Write-Host "Built $ZIP ($size bytes)" -ForegroundColor Green
}

function Install-Plugin {
    Write-Host "Installing plugin from source dir (no ZIP needed)..." -ForegroundColor Cyan
    & $CUSTOMIZE -b $PLUGIN_DIR
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installed OK" -ForegroundColor Green
    } else {
        Write-Host "Install failed (exit $LASTEXITCODE)" -ForegroundColor Red
    }
}

function Remove-Plugin {
    Write-Host "Removing plugin '$PLUGIN_NAME'..." -ForegroundColor Cyan
    & $CUSTOMIZE -r $PLUGIN_NAME
}

function Launch-Debug {
    Write-Host "Launching Calibre with console attached..." -ForegroundColor Cyan
    Write-Host "(stdout/stderr visible here — print() and tracebacks will appear)" -ForegroundColor DarkGray
    & $DEBUG -g
}

function Launch-Normal {
    Write-Host "Launching Calibre (normal mode)..." -ForegroundColor Cyan
    & $CALIBRE_EXE
}

function Test-Loop {
    # The standard iterate-fix cycle: install from source dir, launch with debug console
    Build-Plugin
    Install-Plugin
    Launch-Debug
}

# ── Usage ──────────────────────────────────────────────────────────────────────
# Dot-source this file, then call functions:
#
#   . D:\Dev\repos\calibre-mcp\scripts\calibre-plugin-test.ps1
#
#   Test-Loop          # build ZIP + install + launch with console (standard dev loop)
#   Install-Plugin     # install from source dir directly (faster, no ZIP)
#   Remove-Plugin      # uninstall by name
#   Launch-Debug       # just launch with console (if already installed)
#   Launch-Normal      # launch without console
#
# One-liner for quick iteration after a code change:
#   Install-Plugin; Launch-Debug
#
# Install from ZIP (e.g. for clean install test):
#   & "C:\Program Files\calibre2\calibre-customize.exe" -a "D:\Dev\repos\calibre-mcp\calibre_mcp_integration.zip"
#
# ── What to look for on first launch ──────────────────────────────────────────
# 1. No ImportError in the console on startup
# 2. "MCP Metadata" button appears in toolbar
# 3. Select a book -> click button -> extended metadata dialog opens
# 4. Fill in First Published / Translator / Notes -> Save -> reopen -> data persists
#    (stored in %APPDATA%\calibre-mcp\calibre_mcp_data.db)
#
# ── For VL from Query (needs webapp) ──────────────────────────────────────────
# Start webapp first:
#   cd D:\Dev\repos\calibre-mcp\webapp\backend
#   uv run uvicorn app.main:app --host 127.0.0.1 --port 10720
# Then in Calibre: toolbar dropdown -> "Create VL from Query..."
