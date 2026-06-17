# Metadata RAG reindex on GPU — venv python (not uv run).
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $RepoRoot

if (-not (Test-Path (Join-Path $RepoRoot ".venv\rag-gpu-mode"))) {
    Write-Host "[rag-gpu] GPU stack not installed. Run: just rag-gpu-install" -ForegroundColor Red
    exit 1
}

$env:RAG_GPU = "1"
$env:MCD_RAG_GPU = "1"
$py = & (Join-Path $PSScriptRoot "rag-python.ps1")
& $py scripts/rag_reindex_metadata.py
exit $LASTEXITCODE
