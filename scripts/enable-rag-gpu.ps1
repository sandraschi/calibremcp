# Swap MCD RAG stack to GPU (Goliath / RTX class machines).
# fastembed-gpu replaces fastembed; onnxruntime-gpu replaces onnxruntime.
# STOP any running `just rag` first — ONNX DLLs are locked while embed runs.
# IMPORTANT: use `just rag-gpu` (not `uv run`) — uv run re-installs CPU onnxruntime from pyproject.toml.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $RepoRoot
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
. (Join-Path $PSScriptRoot "rag-gpu-env.ps1")

function Test-RagEmbedRunning {
    param([string]$RepoRoot)
    $tag = Split-Path $RepoRoot -Leaf
    $hits = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -match [regex]::Escape($tag) -and
            $_.CommandLine -match 'mcd_exerciser|rag_reindex|rag_reindex_metadata|plex_rag_sync|reindex_docs|rag_reindex_arxiv|depot_rag_reindex|robofang_rag_reindex'
        }
    return @($hits)
}

$running = Test-RagEmbedRunning -RepoRoot $RepoRoot
if ($running.Count -gt 0) {
    Write-Host "[rag-gpu] BLOCKED: RAG embed is still running (PID $($running[0].ProcessId))." -ForegroundColor Red
    Write-Host '[rag-gpu] Wait for just rag to finish or Ctrl+C it, then re-run: just rag-gpu-install' -ForegroundColor Yellow
    exit 1
}

Write-Host "[rag-gpu] Removing CPU + partial GPU packages..." -ForegroundColor Yellow
uv pip uninstall onnxruntime onnxruntime-gpu fastembed fastembed-gpu 2>$null

Write-Host "[rag-gpu] Installing fastembed-gpu + onnxruntime-gpu (CUDA 12)..." -ForegroundColor Cyan
$Cuda12Index = "https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/"
uv pip install --reinstall "fastembed-gpu>=0.5.0"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
uv pip install --reinstall onnxruntime-gpu --extra-index-url $Cuda12Index
if ($LASTEXITCODE -ne 0) {
    Write-Host "[rag-gpu] Install failed. Repair CPU stack with: just rag-cpu-install" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "[rag-gpu] Installing NVIDIA CUDA 12 runtime DLLs (pip, ~1.5 GB)..." -ForegroundColor Cyan
$NvidiaPkgs = 'nvidia-cublas-cu12', 'nvidia-cuda-runtime-cu12', 'nvidia-cuda-nvrtc-cu12', 'nvidia-cudnn-cu12', 'nvidia-cufft-cu12', 'nvidia-curand-cu12', 'nvidia-cusolver-cu12', 'nvidia-cusparse-cu12', 'nvidia-nvjitlink-cu12'
uv pip install --reinstall @NvidiaPkgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "[rag-gpu] NVIDIA runtime install failed. Repair with: just rag-cpu-install" -ForegroundColor Red
    exit $LASTEXITCODE
}

Add-RagGpuPath -RepoRoot $RepoRoot | Out-Null

Write-Host "[rag-gpu] ORT providers (pre-flight):" -ForegroundColor Cyan
& $VenvPython -c "import onnxruntime as ort; print(ort.get_available_providers())"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[rag-gpu] onnxruntime import failed." -ForegroundColor Red
    exit 1
}

Write-Host "[rag-gpu] Verifying CUDA session..." -ForegroundColor Cyan
$env:PYTHONPATH = Join-Path $RepoRoot "src"
& $VenvPython -c @"
from fastembed import TextEmbedding
m = TextEmbedding('BAAI/bge-small-en-v1.5', providers=['CUDAExecutionProvider'])
providers = m.model.model.get_providers()
print('providers:', providers)
if 'CUDAExecutionProvider' not in providers:
    raise SystemExit('CUDAExecutionProvider missing from active session')
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "[rag-gpu] Verification failed." -ForegroundColor Red
    Write-Host "[rag-gpu] Repair CPU stack with: just rag-cpu-install" -ForegroundColor Yellow
    exit $LASTEXITCODE
}

Set-Content -Path ".venv\rag-gpu-mode" -Value "1" -Encoding ascii
Write-Host ""
Write-Host '[rag-gpu] OK. Run: just rag-gpu  (do NOT use uv run / just rag until rag-cpu-install)' -ForegroundColor Green
