#Requires -Version 5.1
# Fleet shim: delegate to the canonical pack pipeline so fixes reach the whole fleet at once.
# Real work lives in mcp-central-docs/scripts/fleet-mcpb-pack.ps1. Do not vendor a copy here.
param([string]$RepoRoot = (Split-Path -Parent $PSScriptRoot))
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\Dev\repos\mcp-central-docs\scripts\fleet-mcpb-pack.ps1" -RepoRoot $RepoRoot
