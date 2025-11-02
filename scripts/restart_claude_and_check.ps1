# Restart Claude Desktop and verify MCP server loads successfully
# Usage: .\scripts\restart_claude_and_check.ps1 [-SkipPrecheck] [-NoRestart] [-Timeout 30]

param(
    [switch]$SkipPrecheck,
    [switch]$NoRestart,
    [int]$Timeout = 30,
    [string]$ClaudePath = $null
)

$ErrorActionPreference = "Continue"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Claude Desktop Restart & MCP Server Check" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Pre-check (optional)
if (-not $SkipPrecheck) {
    Write-Host "[0/4] Pre-checking server load..." -ForegroundColor Yellow
    
    # Get log file size before pre-check (to avoid checking our own logs)
    $LogFile = Join-Path $RepoRoot "logs\calibremcp.log"
    $LogSizeBefore = 0
    if (Test-Path $LogFile) {
        $LogSizeBefore = (Get-Item $LogFile).Length
    }
    
    # Run pre-check
    $PythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $PythonCmd) {
        Write-Host "[WARN] Python not found in PATH, skipping pre-check" -ForegroundColor Yellow
        $SkipPrecheck = $true
    } else {
        $PrecheckResult = & python scripts\pre_commit_check.py 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FAIL] Pre-check failed!" -ForegroundColor Red
            Write-Host $PrecheckResult
            Write-Host ""
            Write-Host "[STOP] Fix issues before restarting Claude." -ForegroundColor Red
            exit 1
        }
        Write-Host "[OK] Pre-check passed - server should load successfully" -ForegroundColor Green
        Write-Host ""
    }
} else {
    $LogSizeBefore = 0
    if (Test-Path "logs\calibremcp.log") {
        $LogSizeBefore = (Get-Item "logs\calibremcp.log").Length
    }
}

# Restart Claude
if (-not $NoRestart) {
    # Step 1: Stop Claude
    Write-Host "[1/4] Stopping Claude Desktop (using taskkill)..." -ForegroundColor Yellow
    
    $ClaudeProcess = Get-Process -Name "Claude" -ErrorAction SilentlyContinue
    if ($ClaudeProcess) {
        Stop-Process -Name "Claude" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Write-Host "[OK] Claude Desktop stopped" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Claude Desktop was not running" -ForegroundColor Gray
    }
    Write-Host ""
    
    # Step 2: Start Claude
    Write-Host "[2/4] Starting Claude Desktop..." -ForegroundColor Yellow
    
    # Find Claude executable
    if (-not $ClaudePath) {
        $PossiblePaths = @(
            "$env:LOCALAPPDATA\Programs\claude-desktop\Claude.exe",
            "$env:ProgramFiles\Claude\Claude.exe",
            "${env:ProgramFiles(x86)}\Claude\Claude.exe"
        )
        
        foreach ($Path in $PossiblePaths) {
            if (Test-Path $Path) {
                $ClaudePath = $Path
                break
            }
        }
        
        # Try finding via PATH
        if (-not $ClaudePath) {
            try {
                $WhereResult = Get-Command Claude -ErrorAction Stop
                if ($WhereResult) {
                    $ClaudePath = $WhereResult.Source
                }
            } catch {
                # Not in PATH
            }
        }
    }
    
    if (-not $ClaudePath -or -not (Test-Path $ClaudePath)) {
        Write-Host "[FAIL] Could not find Claude Desktop executable" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please start Claude Desktop manually, then run:" -ForegroundColor Yellow
        Write-Host "  python scripts\check_logs.py --errors-only" -ForegroundColor Yellow
        exit 1
    }
    
    try {
        Start-Process -FilePath $ClaudePath -ErrorAction Stop
        Write-Host "[OK] Started Claude Desktop from: $ClaudePath" -ForegroundColor Green
        Write-Host "[INFO] Waiting for Claude to initialize..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
        Write-Host ""
    } catch {
        Write-Host "[FAIL] Error starting Claude: $_" -ForegroundColor Red
        Write-Host "[INFO] Try starting Claude manually from: $ClaudePath" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "[INFO] Skipping restart (--NoRestart specified)" -ForegroundColor Gray
    Write-Host "[INFO] Assuming Claude is already running" -ForegroundColor Gray
    Start-Sleep -Seconds 2
    Write-Host ""
}

# Step 3: Check logs
Write-Host "[3/4] Checking logs for MCP server startup..." -ForegroundColor Yellow

$LogFile = Join-Path $RepoRoot "logs\calibremcp.log"
if (-not (Test-Path $LogFile)) {
    Write-Host "[WARN] Log file not found: $LogFile" -ForegroundColor Yellow
    Write-Host "[INFO] Server may not have started yet, or logs are elsewhere" -ForegroundColor Gray
    exit 1
}

# Read log file (only up to size before pre-check if we ran it)
$LogContent = Get-Content $LogFile -Raw -ErrorAction Stop
if ($LogSizeBefore -gt 0 -and $LogContent.Length -gt $LogSizeBefore) {
    $LogContent = $LogContent.Substring(0, $LogSizeBefore)
    # Get last complete line
    $LastNewline = $LogContent.LastIndexOf("`n")
    if ($LastNewline -gt 0) {
        $LogContent = $LogContent.Substring(0, $LastNewline + 1)
    }
}

$LogLines = $LogContent -split "`n" | Where-Object { $_.Trim() -ne "" }

# Find last server_startup entry
$LastStartupIdx = -1
for ($i = $LogLines.Count - 1; $i -ge 0; $i--) {
    $Line = $LogLines[$i]
    try {
        $Entry = $Line | ConvertFrom-Json
        if ($Entry.operation -eq "server_startup") {
            $LastStartupIdx = $i
            break
        }
    } catch {
        # Not JSON, skip
        continue
    }
}

if ($LastStartupIdx -eq -1) {
    Write-Host "[WARN] No server_startup log entry found" -ForegroundColor Yellow
    Write-Host "[INFO] Server may not have attempted to start, or logs are incomplete" -ForegroundColor Gray
    exit 1
}

# Check logs after last startup
$FoundSuccess = $false
$FoundError = $false
$SuccessTime = $null

for ($i = $LastStartupIdx; $i -lt $LogLines.Count; $i++) {
    $Line = $LogLines[$i]
    try {
        $Entry = $Line | ConvertFrom-Json
        $Operation = ($Entry.operation -split "_")[0].ToLower()
        $Message = $Entry.message.ToLower()
        $Logger = $Entry.logger.ToLower()
        
        # Check for server_startup_error
        if ($Entry.operation -eq "server_startup_error") {
            $FoundError = $true
            Write-Host "[FAIL] Last startup attempt FAILED:" -ForegroundColor Red
            Write-Host "  Time: $($Entry.timestamp)" -ForegroundColor Gray
            Write-Host "  Error: $($Entry.message.Substring(0, [Math]::Min(200, $Entry.message.Length)))..." -ForegroundColor Gray
            exit 1
        }
        
        # Check for successful tool registration
        if ($Message -match "registered" -and $Message -match "basetool classes") {
            if ($Logger -match "tools") {
                $FoundSuccess = $true
                $SuccessTime = $Entry.timestamp
                break
            }
        }
    } catch {
        # Not JSON or missing fields, skip
        continue
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($FoundSuccess) {
    Write-Host "[SUCCESS] Last startup attempt succeeded!" -ForegroundColor Green
    if ($SuccessTime) {
        Write-Host "  Success time: $SuccessTime" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "[SUCCESS] MCP server loaded successfully in Claude!" -ForegroundColor Green
    exit 0
} elseif ($FoundError) {
    Write-Host "[FAILURE] Last startup attempt failed" -ForegroundColor Red
    exit 1
} else {
    Write-Host "[WARN] Last startup found but could not determine success/failure" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Check logs: python scripts\check_logs.py --errors-only" -ForegroundColor Gray
    Write-Host "  2. Verify Claude Desktop MCP configuration" -ForegroundColor Gray
    Write-Host "  3. Check Claude Desktop console for errors" -ForegroundColor Gray
    exit 1
}

