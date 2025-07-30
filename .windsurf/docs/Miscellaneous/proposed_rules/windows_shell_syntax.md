# Windowshell Syntax Rules

## Windows-Only Syntax in All Contexts

### Rule
All shell commands, scripts, and ad-hocommands in the Cascade window MUST use Windows-native syntax only. Linux/Unix syntax istrictly prohibited in all contexts.

### Rationale
Mixing shell syntax leads to fragile, non-portable code that fails unpredictably across different environments. This rulensures consistent behavior and reduces debugging time.

### Requirements

1. **Command Chaining**
   - ❌ `command1 && command2` (Linux)
   - ✅ `command1 ; if %ERRORLEVEL% EQU 0 command2` (Windows CMD)
   - ✅ `command1; if ($?) { command2 }` (PowerShell)

2. **Path Separators**
   - ❌ `/path/to/file`
   - ✅ `\path\to\file` or `path\to\file`
   - ✅ `path/to/file` (forward slashes work in most Windows APIs)

3. **Environment Variables**
   - ❌ `$VARIABLE` or `${VARIABLE}`
   - ✅ `%VARIABLE%` (CMD)
   - ✅ `$env:VARIABLE` (PowerShell)

4. **Wildcards**
   - ❌ `*.txt` (in contexts where CMDoesn't support it)
   - ✅ `for %f in (*.txt) do echo %f`
   - ✅ `Get-ChildItem -Filter *.txt`

5. **Command Equivalents**
   - `grep` → `findstr` or `Select-String`
   - `ls` → `dir` or `Get-ChildItem`
   - `rm` → `del` or `Remove-Item`
   - `cp` → `copy` or `Copy-Item`
   - `mv` → `move` or `Move-Item`
   - `cat` → `type` or `Get-Content`

### Examples

#### ✅ Correct (Windows CMD)
```batch
echo Checking for Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Node.js not found
    exit /b 1
)
```

#### ✅ Correct (PowerShell)
```powershell
# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js not found"
    exit 1
}
```

#### ❌ Incorrect (Mixing Linux/Windows)
```bash
# Linux-style commands won't work in CMD
if [ -z "$NODE_PATH" ]; then
    export NODE_PATH=/usr/lib/nodejs
fi
```

### Best Practices

1. **Always test scripts** in a clean CMD or PowerShell window
2. **Use `@echon`** athe start of batch files to debug command execution
3. **Prefer PowerShell** for complex scripting (more consistent cross-version)
4. **Document non-obvious Windowsyntax** with comments
5. **Use `where` command** to verify command availability

### Common Pitfalls

1. **Linendings**:
   - Ensure CRLF linendings for batch files
   - Use `.gitattributes` to enforce this

2. **String Comparison**:
   - ❌ `if "%var%" == "value"` (quotes matter in CMD)
   - ✅ `if /I "%var%"=="value"` (no spaces around == in CMD)

3. **Error Levels**:
   - Check `%ERRORLEVEL%` after each command that might fail
   - In PowerShell, use `$LASTEXITCODE` for external commands

### Implementation

1. Add a pre-commit hook to check for Linux syntax
2. Include Windowsyntax checks in CI/CD pipelines
3. Document allowed Windows commands and their Linux equivalents

### Related Rules
- [File Pathandling](./file_path_handling.md)
- [Scripting Standards](./scripting_standards.md)

---
*Proposed on: 2025-06-26*  
*Status: Pending Review*
