# CUDA DLL paths for onnxruntime-gpu on Windows (no system CUDA toolkit required).
# Dot-source from rag-python.ps1 and enable-rag-gpu.ps1.

function Test-RagGpuMode {
    param([string]$RepoRoot)
    if ($env:RAG_GPU -eq '1' -or $env:MCD_RAG_GPU -eq '1') { return $true }
    return Test-Path (Join-Path $RepoRoot ".venv\rag-gpu-mode")
}

function Add-RagGpuPath {
    param([string]$RepoRoot)
    $bins = @()

    $cudaRoot = 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA'
    if (Test-Path $cudaRoot) {
        $bins += Get-ChildItem $cudaRoot -Directory -ErrorAction SilentlyContinue |
            ForEach-Object { Join-Path $_.FullName 'bin' } |
            Where-Object { Test-Path $_ }
    }

    $nvidiaRoot = Join-Path $RepoRoot ".venv\Lib\site-packages\nvidia"
    if (Test-Path $nvidiaRoot) {
        $bins += Get-ChildItem $nvidiaRoot -Recurse -Directory -Filter bin -ErrorAction SilentlyContinue |
            ForEach-Object { $_.FullName }
    }

    $bins = $bins | Sort-Object -Unique
    if ($bins.Count -eq 0) { return $false }

    $prefix = $bins -join ';'
    if ($env:PATH -notlike "*$($bins[0])*") {
        $env:PATH = "$prefix;$env:PATH"
    }
    return $true
}
