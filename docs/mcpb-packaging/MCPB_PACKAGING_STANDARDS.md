# MCPB Packaging Standards

**Version:** 1.0  
**Date:** 2025-10-24  
**Status:** Official Standard  
**Applies to:** All MCP projects using MCPB packaging

---

## 🎯 **Overview**

MCPB (Model Context Protocol Bundle) is the modern standard for packaging and distributing MCP servers. This document defines the complete standards for MCPB packaging.

---

## 📦 **MCPB Package Structure**

### **Required Files**

```
mcp-server/
├── manifest.json          # MCPB manifest configuration
├── assets/                # Package assets
│   ├── icon.png          # Package icon
│   ├── screenshots/      # Screenshots for documentation
│   └── prompts/          # Template prompts
├── src/                  # Source code
│   └── package_name/
│       ├── __init__.py
│       ├── mcp_server.py
│       └── tools/
├── pyproject.toml        # Python project configuration
├── requirements.txt      # Runtime dependencies
└── README.md            # Package documentation
```

---

## 📋 **Manifest Configuration**

### **Required Manifest Structure**

```json
{
  "manifest_version": "0.2",
  "server": {
    "type": "python",
    "entry_point": "src/package_name/mcp_server.py",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "package_name.mcp_server"],
      "env": {
        "PYTHONPATH": "${PWD}",
        "PYTHONUNBUFFERED": "1"
      }
    }
  },
  "user_config": {
    "api_key": {
      "type": "string",
      "title": "API Key",
      "required": true,
      "default": ""
    },
    "timeout": {
      "type": "string",
      "title": "Operation Timeout (seconds)",
      "default": "30"
    }
  },
  "tools": [
    "tool_name_1",
    "tool_name_2"
  ],
  "compatibility": {
    "platforms": ["win32", "darwin", "linux"],
    "python": ">=3.10"
  }
}
```

### **Manifest Requirements**

#### **Server Configuration**
- **type**: Must be "python"
- **entry_point**: Path to main server file
- **mcp_config**: Python execution configuration
- **env**: Environment variables for runtime

#### **User Configuration**
- **api_key**: API key for external services
- **timeout**: Operation timeout settings
- **Custom settings**: Application-specific configuration

#### **Tools Array**
- **List all tools**: Include all tool names
- **Complete list**: Must match actual tool registrations

#### **Compatibility**
- **platforms**: Supported operating systems
- **python**: Minimum Python version requirement

---

## 🔧 **Build Process**

### **MCPB CLI Installation**

```bash
# Install MCPB CLI
npm install -g @anthropic-ai/mcpb

# Verify installation
mcpb --version
```

### **Package Building**

```bash
# Build MCPB package
mcpb pack . dist/package-name-v{version}.mcpb

# Build with validation
mcpb pack . dist/package-name-v{version}.mcpb --validate

# Build with signing (if configured)
mcpb pack . dist/package-name-v{version}.mcpb --sign
```

### **Package Validation**

```bash
# Validate manifest
mcpb validate manifest.json

# Validate package
mcpb validate dist/package-name-v{version}.mcpb
```

---

## 📁 **Assets Directory**

### **Required Assets**

```
assets/
├── icon.png              # Package icon (256x256px)
├── screenshots/          # Screenshots for documentation
│   ├── dashboard.png
│   ├── configuration.png
│   └── usage.png
└── prompts/             # Template prompts
    ├── quick-start.md
    ├── configuration.md
    └── troubleshooting.md
```

### **Asset Requirements**

#### **Icon**
- **Size**: 256x256 pixels
- **Format**: PNG
- **Style**: Clear, recognizable, professional
- **Purpose**: Package identification

#### **Screenshots**
- **Purpose**: Documentation and marketing
- **Quality**: High resolution, clear text
- **Content**: Key features, configuration, usage

#### **Prompts**
- **Purpose**: User guidance and templates
- **Format**: Markdown
- **Content**: Quick start, configuration, troubleshooting

---

## 🐍 **Python Configuration**

### **pyproject.toml Requirements**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "package-name"
version = "1.0.0"
description = "MCP server description"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=2.12",
    "httpx>=0.24.0",
    "structlog>=23.0.0"
]

[project.optional-dependencies]
dev = [
    "ruff>=0.1.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0"
]

[tool.ruff]
select = ["E", "F", "W", "C90", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "AIR", "PERF"]
ignore = ["E501", "W503"]
target-version = "py310"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### **requirements.txt Requirements**

```
# Core dependencies
fastmcp>=2.12
httpx>=0.24.0
structlog>=23.0.0
prometheus-client>=0.19.0

# Optional dependencies
aiohttp>=3.8.0
pydantic>=2.0.0
```

---

## 🚀 **CI/CD Integration**

### **GitHub Actions Workflow**

```yaml
name: Build and Package

on:
  push:
    tags:
      - 'v*'
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install -g @anthropic-ai/mcpb
          
      - name: Run tests
        run: |
          pytest tests/
          
      - name: Build MCPB package
        run: |
          mcpb pack . dist/package-name-v${{ github.ref_name }}.mcpb
          
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: mcpb-package
          path: dist/
```

---

## 📚 **Documentation Requirements**

### **README.md Requirements**

```markdown
# Package Name

Brief description of the MCP server.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

### Prerequisites

- Python 3.10+
- Required dependencies

### Install via MCPB

1. Download the .mcpb package
2. Drag to Claude Desktop
3. Configure settings

## Configuration

### Environment Variables

- `API_KEY`: Required API key
- `TIMEOUT`: Operation timeout (default: 30)

### User Configuration

Configure via Claude Desktop settings panel.

## Usage

### Basic Usage

```python
# Example usage
```

### Advanced Usage

```python
# Advanced examples
```

## Troubleshooting

### Common Issues

- Issue 1: Solution
- Issue 2: Solution

## License

MIT License
```

---

## 🔍 **Quality Standards**

### **Package Validation**

- **Manifest validation**: All required fields present
- **Tool registration**: All tools properly registered
- **Asset validation**: All required assets present
- **Python validation**: Code quality and testing

### **Testing Requirements**

- **Unit tests**: All tools and functions tested
- **Integration tests**: End-to-end workflows tested
- **Coverage**: 80%+ code coverage
- **Quality gates**: Ruff linting, security scanning

### **Security Standards**

- **Input validation**: All inputs validated
- **Error handling**: Secure error handling
- **Dependencies**: Security scanning of dependencies
- **Secrets**: Proper handling of API keys and secrets

---

## 📦 **Distribution**

### **Package Distribution**

- **GitHub Releases**: Automated package releases
- **Claude Desktop**: Direct installation via .mcpb files
- **Documentation**: Complete usage documentation
- **Support**: Issue tracking and support

### **Version Management**

- **Semantic versioning**: Major.Minor.Patch
- **Changelog**: Complete change documentation
- **Migration guides**: Breaking change documentation
- **Compatibility**: Version compatibility matrix

---

## 🎯 **Best Practices**

### **Package Design**

- **Single responsibility**: One package, one purpose
- **Clear naming**: Descriptive package and tool names
- **Comprehensive documentation**: Complete API documentation
- **User experience**: Intuitive configuration and usage

### **Development Process**

- **Version control**: Proper Git workflow
- **Testing**: Comprehensive test coverage
- **Documentation**: Up-to-date documentation
- **Quality assurance**: Automated quality checks

### **Maintenance**

- **Regular updates**: Keep dependencies current
- **Security patches**: Prompt security updates
- **Bug fixes**: Quick bug fix releases
- **Feature updates**: Regular feature releases

---

## 📞 **Support & Resources**

- **MCPB Documentation**: Official MCPB documentation
- **Claude Desktop**: Installation and usage guide
- **GitHub Issues**: Bug reports and feature requests
- **Community**: MCP community support

---

*Document created: October 24, 2025*  
*Status: Official Standard*  
*Next Review: As needed for standards updates*
