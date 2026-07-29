$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$RepoName = Split-Path -Leaf $Root
$Triple = "x86_64-pc-windows-msvc"
$ResourceDir = "$PSScriptRoot\resources"
$DevDir = "$PSScriptRoot\binaries"
New-Item -ItemType Directory -Force -Path $ResourceDir, $DevDir | Out-Null

Write-Host "=== ${RepoName} Tauri Release Build ===" -ForegroundColor Cyan

# Step 1: TypeScript lint gate + frontend build
$frontendDirs = @("web_sota", "webapp/frontend", "webapp")
foreach ($dir in $frontendDirs) {
    $frontend = Join-Path $Root $dir
    if (Test-Path "$frontend\package.json") {
        Write-Host "-> [1/4] Building frontend ($dir)..." -ForegroundColor Yellow
        Push-Location $frontend
        npm install --silent 2>$null

        Write-Host "  tsc --noEmit..." -ForegroundColor Gray
        $tscOut = npx tsc --noEmit 2>&1
        $tscExit = $LASTEXITCODE
        if ($tscExit -ne 0) {
            Write-Host "  TypeScript compilation FAILED - fix errors before building NSIS" -ForegroundColor Red
            Write-Host $tscOut
            throw "TypeScript compilation failed - fix all errors before building NSIS installer"
        }

        $isNextJs = (Test-Path "next.config.js") -or (Test-Path "next.config.ts") -or (Test-Path "next.config.mjs")
        if ($isNextJs) {
            Write-Host "  Detected Next.js project" -ForegroundColor Cyan
            $tauriBuildScript = Join-Path $Root "scripts\build-tauri-frontend.ps1"
            if (Test-Path $tauriBuildScript) {
                & $tauriBuildScript -FrontendDir $frontend
                if ($LASTEXITCODE -ne 0) { throw "Next.js Tauri frontend build failed" }
            } else {
                $env:TAURI_BUILD = "1"
                npm run build 2>&1
                Remove-Item env:TAURI_BUILD -ErrorAction SilentlyContinue
                if ($LASTEXITCODE -ne 0) { throw "Next.js build failed" }
            }
            if (-not (Test-Path "out\index.html")) { throw "Next.js export produced no out/index.html" }
        } else {
            npm run build
            if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
        }
        Pop-Location
        break
    }
}

# Step 2: PyInstaller backend (onefile)
Write-Host "-> [2/4] PyInstaller backend..." -ForegroundColor Yellow
$specFile = "$Root\${RepoName}-backend.spec"
if (Test-Path $specFile) {
    Push-Location $Root
    # Patch fastmcp to not crash on missing metadata (dist-info stripped below)
    $fm = "$Root\.venv\Lib\site-packages\fastmcp\__init__.py"
    if (Test-Path $fm) {
        $c = Get-Content $fm -Raw
        if ($c -match 'except PackageNotFoundError:\s+    __version__ = _version\("fastmcp"\)') {
            $c = $c -replace 'except PackageNotFoundError:\s+    __version__ = _version\("fastmcp"\)', 'except PackageNotFoundError:
    try:
        __version__ = _version("fastmcp")
    except PackageNotFoundError:
        __version__ = "0.0.0"'
            Set-Content $fm -Value $c -Encoding utf8
            Write-Host "  Patched fastmcp metadata fallback" -ForegroundColor Yellow
        }
    }
    # Patch opentelemetry context to handle missing entry points in frozen exe
    $otCtx = "$Root\.venv\Lib\site-packages\opentelemetry\context\__init__.py"
    if (Test-Path $otCtx) {
        $c = Get-Content $otCtx -Raw
        if ($c -match 'except Exception.*\n.*logger\.exception.*\n.*return next.*') {
            $c = $c -replace '(except Exception:.*?logger\.exception.*?)return next\(', '$1try: return next('
            $c = $c -replace '(\s+\)).load\(\)\(\)\s*\n\s*_RUNTIME_CONTEXT', ').load()()
        except StopIteration:
            from opentelemetry.context.contextvars_context import ContextVarsRuntimeContext
            return ContextVarsRuntimeContext()

_RUNTIME_CONTEXT'
            Set-Content $otCtx -Value $c -Encoding utf8
            Write-Host "  Patched opentelemetry context StopIteration fallback" -ForegroundColor Yellow
        }
    }
    uv run pyinstaller "$specFile" --clean --noconfirm
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
    Pop-Location
} else {
    Write-Host "  WARNING: spec file not found at $specFile - using existing backend exe if present" -ForegroundColor DarkYellow
}

# Step 3: Embed in Tauri resources (+ dev fallback) with size gate + smoke test
Write-Host "-> [3/4] Embedding backend..." -ForegroundColor Yellow
$src = "$Root\dist\${RepoName}-backend.exe"
if (-not (Test-Path $src)) { throw "Backend exe not found at $src - PyInstaller step failed" }
$sizeMB = (Get-Item $src).Length / 1MB
if ($sizeMB -lt 5) {
    throw "Backend exe is only $([math]::Round($sizeMB, 1)) MB at $src - PyInstaller produced an empty/broken binary"
}
Write-Host "  Backend exe: $sizeMB MB"

# Bundle .env.example (NOT .env - dev .env has personal API keys)
$envExampleSrc = "$Root\.env.example"
if (Test-Path $envExampleSrc) {
    Copy-Item $envExampleSrc "$ResourceDir\.env.example" -Force
    Write-Host "  Bundled .env.example ($((Get-Item $envExampleSrc).Length) bytes)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: .env.example not found at repo root" -ForegroundColor DarkYellow
}

Write-Host "  Smoke-testing frozen binary..." -ForegroundColor Yellow
$testPort = 11999
$oldPort = $env:PORT; $oldHost = $env:HOST
$env:PORT = "$testPort"; $env:HOST = "127.0.0.1"
$testProc = Start-Process -FilePath $src -NoNewWindow -PassThru -RedirectStandardError "$Root\dist\pyi-crash.log"
Start-Sleep -Seconds 5
$env:PORT = $oldPort; $env:HOST = $oldHost
if ($testProc.HasExited) {
    $crash = Get-Content "$Root\dist\pyi-crash.log" -Raw
    throw "Frozen binary crashed on launch (exit $($testProc.ExitCode)):`n$crash"
}
$testProc.Kill(); $testProc.Dispose()
Remove-Item "$Root\dist\pyi-crash.log" -Force -ErrorAction SilentlyContinue
Write-Host "  Frozen binary smoke test PASSED" -ForegroundColor Green

Copy-Item $src "$ResourceDir\${RepoName}-backend.exe" -Force
Copy-Item $src "$DevDir\${RepoName}-backend-$Triple.exe" -Force

# Step 4: Single NSIS installer
Write-Host "-> [4/4] Tauri NSIS bundle..." -ForegroundColor Yellow
Push-Location $PSScriptRoot
$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
npx @tauri-apps/cli build --bundles nsis
if ($LASTEXITCODE -ne 0) { throw "Tauri build failed with exit code $LASTEXITCODE" }
Pop-Location

# Stage to repo dist/
$distDir = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $distDir | Out-Null
$nsisDir = "$PSScriptRoot\target\release\bundle\nsis"
if (Test-Path $nsisDir) { Copy-Item "$nsisDir\*-setup.exe" "$distDir\" -Force }

# Clean up stray backend exe that Tauri drops in target/release/ (shadow copy risk)
$strayExe = "$PSScriptRoot\target\release\${RepoName}-backend.exe"
if (Test-Path $strayExe) { Remove-Item $strayExe -Force; Write-Host "  Cleaned stray: $strayExe" -ForegroundColor DarkGray }

# Restore standalone .next cache (Tauri build left basePath:/app, which breaks next start)
Write-Host "-> [5/5] Restoring standalone frontend build..." -ForegroundColor Yellow
$frontendDir = Join-Path $Root "webapp\frontend"
if (Test-Path "$frontendDir\package.json") {
    Push-Location $frontendDir
    Remove-Item ".next" -Recurse -Force -ErrorAction SilentlyContinue
    npm run build 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host "  WARNING: Standalone rebuild failed (run manually)" -ForegroundColor DarkYellow }
    else {
        # Next.js standalone output needs static files copied manually
        if ((Test-Path ".next/static") -and -not (Test-Path ".next/standalone/.next/static")) {
            Copy-Item ".next/static" ".next/standalone/.next/static" -Recurse -Force
        }
        Write-Host "  Standalone .next cache restored" -ForegroundColor Green
    }
    Pop-Location
}

Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "Ship: $nsisDir\*.exe"
