$ErrorActionPreference = "Stop"

Write-Host "=== Step 1: Bulk os.path -> pathlib conversions ==="

$dir = "D:\Dev\repos\calibre-mcp\src\calibre_mcp"
$files = Get-ChildItem $dir -Recurse -Include "*.py"

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $changed = $false

    # os.path.isdir(x) -> pathlib.Path(x).is_dir()
    if ($content -match 'os\.path\.isdir\(([^)]+)\)') {
        $content = [regex]::Replace($content, 'os\.path\.isdir\(([^)]+)\)', 'pathlib.Path($1).is_dir()')
        $changed = $true
    }
    # os.path.exists(x) -> pathlib.Path(x).exists()
    if ($content -match 'os\.path\.exists\(([^)]+)\)') {
        $content = [regex]::Replace($content, 'os\.path\.exists\(([^)]+)\)', 'pathlib.Path($1).exists()')
        $changed = $true
    }
    # os.makedirs(x, exist_ok=True) -> pathlib.Path(x).mkdir(exist_ok=True, parents=True)
    if ($content -match 'os\.makedirs\(([^,]+),\s*exist_ok=True\)') {
        $content = [regex]::Replace($content, 'os\.makedirs\(([^,]+),\s*exist_ok=True\)', 'pathlib.Path($1).mkdir(exist_ok=True, parents=True)')
        $changed = $true
    }
    # os.path.getsize(x) -> pathlib.Path(x).stat().st_size
    if ($content -match 'os\.path\.getsize\(([^)]+)\)') {
        $content = [regex]::Replace($content, 'os\.path\.getsize\(([^)]+)\)', 'pathlib.Path($1).stat().st_size')
        $changed = $true
    }
    # os.path.getmtime(x) -> pathlib.Path(x).stat().st_mtime
    if ($content -match 'os\.path\.getmtime\(([^)]+)\)') {
        $content = [regex]::Replace($content, 'os\.path\.getmtime\(([^)]+)\)', 'pathlib.Path($1).stat().st_mtime')
        $changed = $true
    }
    # os.path.basename(x) -> pathlib.Path(x).name
    if ($content -match 'os\.path\.basename\(([^)]+)\)') {
        $content = [regex]::Replace($content, 'os\.path\.basename\(([^)]+)\)', 'pathlib.Path($1).name')
        $changed = $true
    }
    # os.path.dirname(x) -> pathlib.Path(x).parent
    if ($content -match 'os\.path\.dirname\(([^)]+)\)') {
        $content = [regex]::Replace($content, 'os\.path\.dirname\(([^)]+)\)', 'pathlib.Path($1).parent')
        $changed = $true
    }
    # os.remove(x) -> pathlib.Path(x).unlink()
    if ($content -match 'os\.remove\(([^)]+)\)') {
        $content = [regex]::Replace($content, 'os\.remove\(([^)]+)\)', 'pathlib.Path($1).unlink()')
        $changed = $true
    }
    # os.path.join(var, "literal") -> pathlib.Path(var) / "literal"
    $pattern1 = 'os\.path\.join\(([^,]+),\s*"([^"]+)"\)'
    while ($content -match $pattern1) {
        $content = [regex]::Replace($content, $pattern1, 'pathlib.Path($1) / "$2"', 1)
        $changed = $true
    }
    # os.path.join(var1, var2) where both are identifiers
    $pattern2 = 'os\.path\.join\((\w+),\s*(\w+)\)'
    while ($content -match $pattern2) {
        $content = [regex]::Replace($content, $pattern2, 'pathlib.Path($1) / $2', 1)
        $changed = $true
    }
    # os.path.join(var, "lit1", "lit2") -> pathlib.Path(var) / "lit1" / "lit2"
    $pattern3 = 'os\.path\.join\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"\)'
    while ($content -match $pattern3) {
        $content = [regex]::Replace($content, $pattern3, 'pathlib.Path($1) / "$2" / "$3"', 1)
        $changed = $true
    }
    # os.path.join(var1, var2, "lit") -> pathlib.Path(var1) / var2 / "lit"
    $pattern4 = 'os\.path\.join\((\w+),\s*(\w+),\s*"([^"]+)"\)'
    while ($content -match $pattern4) {
        $content = [regex]::Replace($content, $pattern4, 'pathlib.Path($1) / $2 / "$3"', 1)
        $changed = $true
    }

    if ($changed) {
        Set-Content $file.FullName -Value $content -NoNewline
        Write-Host "  Fixed: $($file.Name)" -ForegroundColor Green
    }
}

Write-Host "=== Step 2: Add pathlib import where missing ==="

$needPathlib = @(
    "src\calibre_mcp\tools\library_operations\extended_library_ops.py",
    "src\calibre_mcp\tools\organization\library_organizer.py",
    "src\calibre_mcp\utils.py",
    "src\calibre_mcp\viewers\comic\__init__.py",
    "src\calibre_mcp\viewers\comic\manga_viewer.py",
    "src\calibre_mcp\viewers\epub\epub_viewer.py",
    "src\calibre_mcp\viewers\pdf\pdfjs_viewer.py"
)

$srcDir = "D:\Dev\repos\calibre-mcp\src"
foreach ($relPath in $needPathlib) {
    $fullPath = Join-Path $srcDir $relPath
    if (-not (Test-Path $fullPath)) { continue }
    $content = Get-Content $fullPath -Raw
    if ($content -notmatch "import pathlib" -and $content -notmatch "from pathlib") {
        $content = "import pathlib`n" + $content
        Set-Content $fullPath -Value $content -NoNewline
        Write-Host "  Added pathlib: $relPath" -ForegroundColor Yellow
    }
}

Write-Host "Done!"
