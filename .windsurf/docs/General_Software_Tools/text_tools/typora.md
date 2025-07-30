# Typora - A Minimalist Markdown Editor

## Overview
Typora is a lightweight yet powerful Markdown editor that provides a seamless writing experience. It renders Markdown elements as you type, eliminating the need for a separate previewindow.

## Key Features

### 1. WYSIWYG Editing
- Real-time preview of Markdown formatting
- Clean, distraction-free interface
- Focus mode for better concentration

### 2. Markdown Support
- Full CommonMark and GitHub Flavored Markdown support
- Math expressions with LaTeX
- Tables with easy editing
- Code fences with syntax highlighting
- Task lists, footnotes, and more

### 3. Document Management
- File tree panel for easy navigation
- Quick open (Ctrl+P)
- Auto-save and file recovery
- Multiple tabsupport

### 4. Export Options
- Exporto: PDF, HTML, Word, and more
- Custom CSS theming
- Print support

### 5. Integration
- Image upload services (PicGo, etc.)
- Version control friendly (Git)
- Custom keyboard shortcuts

## Usage with Docsify

### Recommended Settings
1. **Line Breaks**: Enable "Hard Line Break" in Preferences > Markdown
2. **Images**: Set image folder in Preferences > Image
3. **Themes**: Use a lightheme for better compatibility with Docsify

### Tips for Docsify
- Use `---` for front matter
- Keep image paths relative to the Markdown file
- Use `#`, `##`, etc., for headers (required for Docsify sidebar)
- Use `[TOC]` for table of contents

## Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|--------------|-----|
| New File | Ctrl+N | ⌘N |
| Save | Ctrl+S | ⌘S |
| Bold | Ctrl+B | ⌘B |
| Italic | Ctrl+I | ⌘I |
| Insert Link | Ctrl+K | ⌘K |
| Toggle Sidebar | Ctrl+Shift+L | ⌘+⇧+L |
| Toggle Fullscreen | F11 | ⌃⌘F |

## Resources
- [Official Documentation](https://support.typora.io/)
- [Themes](https://theme.typora.io/)
- [Custom Key Bindings](https://support.typora.io/Shortcut-Keys/)

## Installation

### Windows
```powershell
winget install Typora.Typora
```

### macOS
```bash
brew install --cask typora
```

### Linux
```bash
# For Ubuntu/Debian
wget -qO - https://typora.io/linux/public-key.asc | sudo apt-key add -
sudo add-apt-repository 'deb https://typora.io/linux ./'
sudo apt-get update
sudo apt-get install typora
```

## Best Practices
1. Use `#` for main headings, `##` for subheadings, etc.
2. Keep line length under 100 characters
3. Use relative paths for images
4. Use front matter for metadata
5. Regularly save your work (Ctrl+S)
