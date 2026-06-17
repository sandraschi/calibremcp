# Repair / restore CPU RAG stack (default / portable).
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $RepoRoot
$tag = Split-Path $RepoRoot -Leaf
$running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object {
        $_.CommandLine -match [regex]::Escape($tag) -and
        $_.CommandLine -match 'mcd_exerciser|rag_reindex|rag_reindex_metadata|plex_rag_sync|reindex_docs|rag_reindex_arxiv|depot_rag_reindex|robofang_rag_reindex'
    }
if ($running) {
    Write-Host "[rag-cpu] BLOCKED: stop running RAG embed first (PID $($running[0].ProcessId))." -ForegroundColor Red
    exit 1
}

Write-Host "[rag-cpu] Removing GPU onnx/fastembed + NVIDIA CUDA runtimes..." -ForegroundColor Yellow
$NvidiaPkgs = 'nvidia-cublas-cu12', 'nvidia-cuda-runtime-cu12', 'nvidia-cuda-nvrtc-cu12', 'nvidia-cudnn-cu12', 'nvidia-cufft-cu12', 'nvidia-curand-cu12', 'nvidia-cusolver-cu12', 'nvidia-cusparse-cu12', 'nvidia-nvjitlink-cu12'
uv pip uninstall onnxruntime onnxruntime-gpu fastembed fastembed-gpu @NvidiaPkgs 2>$null

Write-Host "[rag-cpu] Installing CPU onnxruntime + fastembed..." -ForegroundColor Cyan
uv pip install --reinstall "onnxruntime>=1.17.0" "fastembed>=0.2.0"

Write-Host "[rag-cpu] Verifying import..." -ForegroundColor Cyan
$VenvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
& $VenvPython -c @"
import onnxruntime as ort
from fastembed import TextEmbedding
assert hasattr(ort, 'SessionOptions')
print('ORT providers:', ort.get_available_providers())
TextEmbedding('BAAI/bge-small-en-v1.5')
print('CPU RAG stack OK')
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "[rag-cpu] Repair failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

Remove-Item ".venv\rag-gpu-mode" -Force -ErrorAction SilentlyContinue

Write-Host "[rag-cpu] Done. Run: just rag" -ForegroundColor Green
