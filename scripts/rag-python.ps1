# Venv python for RAG — avoids `uv run` re-syncing CPU deps over GPU install.
$repoRoot = Split-Path $PSScriptRoot -Parent
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Missing venv python: $venvPython (run uv sync first)"
}

. (Join-Path $PSScriptRoot "rag-gpu-env.ps1")
if (Test-RagGpuMode -RepoRoot $repoRoot) {
    Add-RagGpuPath -RepoRoot $repoRoot | Out-Null
}

$env:PYTHONPATH = Join-Path $repoRoot "src"
$env:PYTHONIOENCODING = "utf-8"
return $venvPython
