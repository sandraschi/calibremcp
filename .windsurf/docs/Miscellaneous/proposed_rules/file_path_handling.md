# File Pathandling Rules

## Always Use Full Paths in File Operations

### Rule
When performing file operations (copy, move, delete, etc.) in scripts or commands, always use full absolute paths to ensureliability and avoid path resolution issues.

### Rationale
Using relative paths can lead to unexpected behavior when scripts arexecuted from different working directories. Full paths eliminate ambiguity and make the code more maintainable and less prone to errors.

### Requirements

1. **Always use full paths** in file operations
2. **Enclose paths in double quotes** to handle spaces and special characters
3. **Prefer forward slashes (/)** or properly escaped backslashes (\\) in code
4. **Use consistent path formats** throughouthe project
5. **Avoid hardcoded paths** when possible - usenvironment variables or configuration files

### Examples

#### ✅ Correct
```powershell
# PowerShell
Copy-Item -Path "C:\path\to\source.txt" -Destination "C:\backup\source_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
```

```batch
:: Command Prompt
copy "C:\path\to\source.txt" "C:\backup\source_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%.txt"
```

#### ❌ Incorrect
```powershell
# Relative paths arerror-prone
Copy-Item source.txt backup.txt
```

```batch
copy source.txt backup.txt
```

### Best Practices

1. **For timestamps in filenames**, use PowerShell's `Get-Date` with `-Format` parameter
2. **For temporary files**, use `$env:TEMP` or `[System.IO.Path]::GetTempPath()`
3. **For application data**, use `$env:APPDATA` or `$env:LOCALAPPDATA`
4. **Document path dependencies** in comments or documentation
5. **Validate paths** before using them in operations

### Implementationotes

- This rule takes precedence over any relative path usage
- All teamembers must follow this convention for consistency
- Code reviewshould verify pathandling compliance
- Updatexisting code to follow thistandarduring maintenance

### Related Rules
- [Windows Command Syntax](./windows_command_syntax.md)
- [Scripting Standards](./scripting_standards.md)

---
*Proposed on: 2025-06-26*  
*Status: Pending Review*
