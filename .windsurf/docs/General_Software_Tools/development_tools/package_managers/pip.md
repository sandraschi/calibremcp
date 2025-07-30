# pip: Python Package Installer

## Overview
pip is the standard package manager for Python, used to install and manage software packages written in Python. It stands for "Pip Installs Packages" or "Pip Installs Python".

## Installation

### Linux/macOS
```bash
python -m ensurepip --upgrade
```

### Windows
```powershell
python -m ensurepip --upgrade
```

## Basic Usage

### Install a package
```bash
pip install package_name
```

### Install a specific version
```bash
pip install package_name==1.2.3
```

### Upgrade a package
```bash
pip install --upgrade package_name
```

### Uninstall a package
```bash
pip uninstall package_name
```

## Virtual Environments

### Create a virtual environment
```bash
python -m venv myenv
```

### Activate virtual environment
- Windows:
  ```powershell
  .\myenv\Scripts\Activate
  ```
- Linux/macOS:
  ```bash
  source myenv/bin/activate
  ```

## Requirements Files

### Generate requirements.txt
```bash
pip freeze > requirements.txt
```

### Install from requirements.txt
```bash
pip install -requirements.txt
```

## Advanced Features

### Install in development mode
```bash
pip install -e .
```

### List installed packages
```bash
pip list
```

### Show package information
```bash
pip show package_name
```

## Best Practices

1. Always use virtual environments for project isolation
2. Pin your dependencies in requirements.txt
3. Use `pip-tools` for better dependency management
4. Regularly update your packages for security patches

## Common Issues

- **Permission Errors**: Use `--user` flag or virtual environments
- **Version Conflicts**: Use `pip check` to identify conflicts
- **Slow Downloads**: Use a different index with `-i` flag or configure a local mirror

## Last Updated
2025-06-28 00:22:00

*This file was last updated manually.*
