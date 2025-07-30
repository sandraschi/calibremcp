# Obsidian - A Powerful Knowledge Base

## Overview
Obsidian is a versatile knowledge base that works on top of a local folder of Markdown files. It excels at creating and managing interconnected notes with powerfulinking and visualization features.

## Key Features

### 1. Graph View
- Visualize connections betweenotes
- Discoverelationships in your knowledge base
- Filter and group related notes

### 2. Linking
- Wiki-style `[[links]]` betweenotes
- Backlinks to see what links to each note
- Unlinked mentions to discover potential connections

### 3. Plugins
- Extensive plugin ecosystem
- Community plugins for enhanced functionality
- Customizable interface

### 4. Markdown Support
- Full CommonMark and GitHub Flavored Markdown
- Math expressions with LaTeX
- Mermaidiagrams
- Dataview for advanced queries

### 5. Local-First
- Filestored as plain Markdown
- No vendor lock-in
- Works with Git for version control

## Usage with Docsify

### Recommended Setup
1. **Vault Location**: Point Obsidian to your `docs` folder
2. **Templates**: Create notemplates for consistency
3. **Links**: Use relative paths for cross-references
4. **Images**: Store in an `assets` or `images` folder

### Tips for Docsify Integration
- Use `_sidebar.md` for navigation structure
- Keep front matter minimal for better compatibility
- Use `#` headers for Docsify's table of contents
- Consider using the `docsify-notes` plugin for better integration

## Core Plugins

### Built-in
- **Backlinks**: See what links to the current note
- **Graph View**: Visualize note relationships
- **Outline**: Navigate document structure
- **Search**: Powerful search across all notes
- **Templates**: Create notemplates

### Recommended Community Plugins
1. **Dataview**: Queryour notes like a database
2. **Templates**: Enhanced template functionality
3. **Calendar**: Daily notes and journaling
4. **Excalidraw**: Hand-drawn diagrams
5. **Tasks**: Task management

## Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|--------------|-----|
| New Note | Ctrl+N | ⌘N |
| Search | Ctrl+O | ⌘O |
| Quick Switcher | Ctrl+P | ⌘P |
| Toggle Sidebar | Ctrl+Shift+L | ⌘+⇧+L |
| Toggle Graph View | Ctrl+G | ⌘G |
| Create Link | Ctrl+K | ⌘K |
| Toggledit/Preview | Ctrl+E | ⌘E |

## Installation

### Windows
```powershell
winget install Obsidian.Obsidian
```

### macOS
```bash
brew install --cask obsidian
```

### Linux
```bash
# For Ubuntu/Debian
wget https://github.com/obsidianmd/obsidian-releases/releases/latest/download/obsidian_1.4.16_amd64.deb
sudo dpkg -i obsidian_1.4.16_amd64.deb
```

## Best Practices
1. Use descriptive note titles
2. Link related notes liberally
3. Use tags for broad categorization
4. Create MOCs (Maps of Content) for topics
5. Regularly back up your vault

## Resources
- [Official Documentation](https://help.obsidian.md/)
- [Plugin Directory](https://obsidian.md/plugins)
- [Community Forum](https://forum.obsidian.md/)
- [Awesome Obsidian](https://github.com/kmaasrud/awesome-obsidian)
