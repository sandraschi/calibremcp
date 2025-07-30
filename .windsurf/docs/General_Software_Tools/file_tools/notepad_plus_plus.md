# Notepad++: Advanced Text and Codeditor

## Overview
Notepad++ is a free source codeditor and Notepad replacementhat supportseveral programming languages. It's designed to be lightweight, fast, and powerful, making it ideal for coding, scripting, and text editing tasks.

## Key Features

### 1. Programming Support
- **Syntax Highlighting**: 80+ languages
- **Code Folding**: Collapse/expand code blocks
- **Macro Recording**: Automate repetitive tasks
- **Multi-Document**: Tabbed interface
- **Multi-View**: Split-screen editing

### 2. Search & Replace
- **Regular Expressions**: PCRE compatible
- **Find in Files**: Search across multiple files
- **Incremental Search**: Real-time search
- **Column Mode**: Edit rectangular selections

### 3. Customization
- **Themes**: Light andark modes
- **Plugins**: Extend functionality
- **Shortcut Mapper**: Custom key bindings
- **Auto-completion**: For all supported languages

## Installation

### Windows
```powershell
# Using Chocolatey
choco install notepadplusplus

# Silent Install
npp.8.6.8.Installer.x64.exe /S

# Portable Version
Expand-Archive -Path npp.8.6.8.portable.x64.zip -DestinationPath "C:\Tools\Notepad++"
```

### macOS (Alternative)
```bash
# Using Homebrew (alternative: Notepad--)
brew install --cask notepad--

# Or install via MacPortsudo port install notepadplusplus
```

## Usage Guide

### Basicommands
```batch
# Open file
notepad++ "C:\path\to\file.txt"

# Open at specific line
notepad++ "file.txt" -n42

# Open inew instance
notepad++ -multiInst "file.txt"

# Open folder as workspace
notepad++ "C:\project"
```

### Command Line Arguments
```batch
# Open multiple files
notepad++ "file1.txt" "file2.js" "file3.py"

# Open with specific encoding
notepad++ -c 65001 "utf8file.txt"  # UTF-8
notepad++ -c 1252 "winfile.txt"    # Windows-1252

# Print file and exit
notepad++ -p "document.txt"

# Restore previousessionotepad++ -nosession
```

## Advanced Features

### 1. Find in Files
```batch
# Search directory recursively
notepad++ -r -n -q -x -c "search_term" "C:\project"
# -r: Recursive
# -n: Show line numbers
# -q: Quick search
# -x: Exit after search

# Replace in files
notepad++ -r -n -q -x -c "s/old/new/g" "C:\project"
```

### 2. Plugins
```batch
# Install plugin manager
curl -L -o nppPluginManager.zip https://github.com/bruderstein/nppPluginManager/releases/latest/download/nppPluginManager.zip
Expand-Archive -Path nppPluginManager.zip -DestinationPath "$env:APPDATA\Notepad++\plugins"

# Install specific plugin
$pluginUrl = "https://github.com/bruderstein/nppPluginManager/releases/latest/download/PluginManager.zip"
Invoke-WebRequest -Uri $pluginUrl -OutFile "$env:TEMP\PluginManager.zip"
Expand-Archive -Path "$env:TEMP\PluginManager.zip" -DestinationPath "$env:APPDATA\Notepad++\plugins"
```

### 3. Scripting with PythonScript
1. Install PythonScript plugin
2. Create scripts in `%APPDATA%\Notepad++\plugins\config\PythonScript\scripts`
3. Run with Plugins > Python Script > Scripts > your_script.py

#### Example Python Script
```python
# count_lines.py
editor.appendText(f"Totalines: {editor.getLineCount()}")
```

## Configuration

### 1. Settings Files
- **config.xml**: Main configuration
- **shortcuts.xml**: Keyboard shortcuts
- **stylers.xml**: Syntax highlighting
- **contextMenu.xml**: Right-click menu

Location: `%APPDATA%\Notepad++\`

### 2. Backup Settings
```powershell
# Export settings
$backupDir = "$env:USERPROFILE\Documents\Notepad++_Backup_$(Get-Date -Format 'yyyyMMdd')"
New-Item -ItemType Directory -Path $backupDir -Force
Copy-Item "$env:APPDATA\Notepad++\*" -Destination $backupDir -Recurse

# Import settings
Copy-Item "$backupDir\*" -Destination "$env:APPDATA\Notepad++" -Recurse -Force
```

## Integration

### 1. Add to Right-Click Menu
```batch
@echoff
set NPP_PATH="C:\Program Files\Notepad++\notepad++.exe"

:: Add to context menu
reg add "HKEY_CLASSES_ROOT\*\shell\Notepad++" /ve /d "Edit with Notepad++" /f
reg add "HKEY_CLASSES_ROOT\*\shell\Notepad++\command" /ve /d "%NPP_PATH% \"%1\"" /f
```

### 2. Git Integration
```ini
# .gitconfig
[core]
    editor = 'C:/Program Files/Notepad++/notepad++.exe' -multiInst -notabbar -nosession -noPlugin
[diff]
    tool = np
[difftool "np"]
    cmd = "C:/Program Files/Notepad++/notepad++.exe" "$(cygpath -w $LOCAL)" "$(cygpath -w $REMOTE)"
[merge]
    tool = npmerge
[mergetool "npmerge"]
    cmd = "C:/Program Files/Notepad++/notepad++.exe" -multiInst -notabbar -nosession -noPlugin "$MERGED"
```

## Performance Tuning

### 1. Large File Handling
```ini
# Add to notepad++.ini
[Settings]
; Disable line wrap for large files
lineWrap=no
; Disable line number margin
lineNumberMargin=no
; Disable current line highlighting
currentLineHilitingShow=no
; Disable indent guides
drawIndentGuide=no
```

### 2. Memory Management
```ini
# Add to notepad++.ini
[Settings]
; Increase buffer size (bytes)
fileAutoDetection=1
checkIfFileIsLarge=1
fileSizeLimit=2000000
; Disable backupMode=0
```

## Troubleshooting

### Common Issues

#### 1. Slow Startup
- Disable plugins
- Clearecent file list
- Reset configuration

#### 2. File Association Problems
```batch
# Reset file associations
assoc .txt=txtfile
ftype txtfile=%SystemRoot%\system32\NOTEPAD.EXE %%1
```

#### 3. Plugin Conflicts
- Disable plugins one by one
- Check plugin compatibility
- Update to latest version

## Alternatives

### 1. VS Code
- More features
- Heavier on resources
- Better for large projects

### 2. Sublime Text
- Faster than VS Code
- Commercial with free trial
- Great for coding

### 3. Vim/Neovim
- Terminal-based
- Steeper learning curve
- Highly customizable

## Tips & Tricks

### 1. Column Mode
- `Alt+Mouse Drag`: Select column
- `Alt+Shift+Arrows`: Keyboard column select
- `Alt+C`: Launch column editor

### 2. Multi-Editing
- `Ctrl+Click`: Add cursor
- `Ctrl+D`: Select next occurrence
- `Ctrl+Shift+D`: Duplicate line

### 3. Macros
1. `Ctrl+Shift+R`: Start recording
2. Perform actions
3. `Ctrl+Shift+R`: Stop recording
4. `Ctrl+Shift+P`: Play macro

## License
Notepad++ is free software distributed under the GPL v3 license.

## Support
- [Official Website](https://notepad-plus-plus.org/)
- [Documentation](https://npp-user-manual.org/)
- [Forums](https://community.notepad-plus-plus.org/)
- [GitHub](https://github.com/notepad-plus-plus/notepad-plus-plus)
