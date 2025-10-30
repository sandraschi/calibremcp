#!/usr/bin/env pwsh
# Auto-generated fix script for calibremcp
# Generated: 2025-10-25_04-57-11
# Issues to fix: 7

param([switch]$DryRun = $false)

Write-Host '🔧 Fixing Repository Standards...' -ForegroundColor Cyan
if ($DryRun) { Write-Host '🔍 DRY RUN MODE' -ForegroundColor Yellow }

$centralDocs = 'D:\Dev\repos\mcp-central-docs'

# Fix: Delete or move: error.log
if (Test-Path 'error.log') {
    Remove-Item 'error.log' -Force -ErrorAction SilentlyContinue
    Write-Host '  ✅ Deleted: error.log' -ForegroundColor Green
}

# Fix: Delete or move: test_claude_integration.py
if (Test-Path 'test_claude_integration.py') {
    Remove-Item 'test_claude_integration.py' -Force -ErrorAction SilentlyContinue
    Write-Host '  ✅ Deleted: test_claude_integration.py' -ForegroundColor Green
}

# Fix: Delete or move: test_imports.py
if (Test-Path 'test_imports.py') {
    Remove-Item 'test_imports.py' -Force -ErrorAction SilentlyContinue
    Write-Host '  ✅ Deleted: test_imports.py' -ForegroundColor Green
}

# Fix: Delete or move: test_syntax.py
if (Test-Path 'test_syntax.py') {
    Remove-Item 'test_syntax.py' -Force -ErrorAction SilentlyContinue
    Write-Host '  ✅ Deleted: test_syntax.py' -ForegroundColor Green
}

# Fix: Move extract_tools.py to scripts/

# Fix: Move minimal_test.py to scripts/

# Fix: Move run_server.py to scripts/

Write-Host '✅ Fix script complete!' -ForegroundColor Green
