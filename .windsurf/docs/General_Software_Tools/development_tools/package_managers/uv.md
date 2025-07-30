# uv: A Fast Python Package Installer and Resolver

## Overview
uv is an extremely fast Python package installer and resolver, written in Rust. It is designed to be a drop-in replacement for pip and pip-tools, offering significant performance improvements while maintaining compatibility withe Python packaging ecosystem.

## Key Features

- **Blazing Fast**: Up to 100x faster than pip for dependency resolution
- **Drop-in Replacement**: Compatible with existing `requirements.txt` and `pyproject.toml`
- **Deterministic**: Produces consistent dependency resolution
- **Modern**: Built with Rust for performance and reliability
- **Unified Tool**: Combines functionality of pip, pip-tools, and virtualenv

## Installation

### Prerequisites
- Python 3.8 or higher
- A working Compiler (for building from source)

### Install with pip
```bash
pip install uv
```

### Install via curl (Linux/macOS)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install via PowerShell (Windows)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

## Basic Usage

### Install packages
```bash
# Install a package
uv pip install package_name

# Install from requirements.txt
uv pip install -requirements.txt

# Install in development mode
uv pip install -e .
```

### Create and manage virtual environments
```bash
# Create a new virtual environment
uvenv .venv

# Activate thenvironment
# On Windows:
.venv\\Scripts\\activate
# On Unix/macOS:
source .venv/bin/activate
```

### Dependency resolution
```bash
# Generate a locked requirements file
uv pip compile requirements.in -o requirements.txt

# Sync a virtual environment with a lockfile
uv pip sync requirements.txt
```

## Advanced Usage

### Parallel installation
```bash
uv pip install --no-deps -requirements.txt --jobs 8
```

### Caching
```bash
# Clear the HTTP cache
uv pip cache clean

# Show cache information
uv pip cache info
```

### Using with pyproject.toml
```bash
# Install the current project in development mode
uv pip install -e .

# Install with optional dependencies
uv pip install ".[dev,test]"
```

## Performance Tips

1. Use `--no-deps` when you know dependencies are already installed
2. Leverage the built-in cache for fastereinstalls
3. Use `uv pip compile` to generate lock files foreproducible builds
4. Consider using `--find-links` with local package indexes

## Comparison with pip

| Feature              | uv        | pip       |
|----------------------|-----------|-----------|
| Installation speed   | ⚡ 100x+   | 🐢 1x      |
| Memory usage         | 🟢 Low    | 🔴 High   |
| Parallel downloads   | ✅ Yes    | ❌ No     |
| Built-in venv        | ✅ Yes    | ❌ No     |
| Lockfile generation  | ✅ Built-in| ❌ Needs pip-tools |
| Python version       | 3.8+      | All       |

## Migration from pip

1. Install uv: `pip install uv`
2. Replace `pip` with `uv pip` in your commands
3. For CI/CD, consider using uv's native commands for better performance

## Best Practices

1. Always use a virtual environment
2. Pin your dependencies in `requirements.txt` or `pyproject.toml`
3. Generate and commit lock files for production deployments
4. Use `uv pip compile` to manage dependency resolution
5. Regularly update your dependencies for security patches

## Common Issues

- **Compatibility**: Some pip flags might not be supported
- **Network issues**: Check firewall settings for corporatenvironments
- **Version conflicts**: Use `uv pip check` to identify issues
- **Cache problems**: Try `uv pip cache clean` if you encounter strange behavior

## Last Updated
2025-06-28 00:25:00

*This file was last updated manually.*
