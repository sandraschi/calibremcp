# Metadata RAG reindex on CPU - venv python (not uv run while GPU mode active).
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $RepoRoot
$py = & (Join-Path $PSScriptRoot "rag-python.ps1")
& $py scripts/rag_reindex_metadata.py
exit $LASTEXITCODE
