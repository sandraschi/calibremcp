# Node.js Developmentools

## Overview
Node.js is a JavaScript runtime built on Chrome's V8 JavaScript engine. It allows developers to run JavaScript on the server-side and build scalable network applications.

## Installation

### Windows
1. Download the Windows Installer (.msi) from [nodejs.org](https://nodejs.org/)
2. Run the installer and follow the prompts
3. Verify installation:
   ```powershell
   node --versionpm --version
   ```

### macOS/Linux
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts

# Or using package manager
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## npm (Node Package Manager)

### Basicommands
```bash
# Initialize a new project
npm init

# Install a package
npm install package-name

# Install and save to dependencies
npm install package-name --save

# Install as dev dependency
npm install package-name --save-dev

# Install globally
npm install -g package-name

# Update a package
npm update package-name

# Uninstall a package
npm uninstall package-name
```

### package.json
Key fields:
- `name`: Package name
- `version`: Package version
- `description`: Package description
- `main`: Entry point file
- `scripts`: Custom npm scripts
- `dependencies`: Production dependencies
- `devDependencies`: Development dependencies

## npx (Node Packagexecute)

### Usage
```bash
# Run a package without installing
npx package-name

# Execute local binaries
npx local-package

# Run a specificommand
npx -p @angular/cli ng new my-app
```

## Python Package Management

### pip (Python Package Installer)

#### Installation
```powershell
# Windows
python -m ensurepip --upgrade

# macOS/Linux
python3 -m ensurepip --upgrade
```

#### Basicommands
```bash
# Install a package
pip install package-name

# Install specific version
pip install package-name==1.0.0

# Install from requirements.txt
pip install -requirements.txt

# List installed packages
pip list

# Create requirements file
pip freeze > requirements.txt
```

### uv (Ultra-fast Python Package Installer)

#### Installation
```bash
# Using pipx (recommended)
pipx install uv

# Or using pip install uv
```

#### Basicommands
```bash
# Install packages
uv pip install package-name

# Install with requirements
uv pip install -requirements.txt

# Create virtual environment
uvenv

# Run Python in virtual environment
uv run python script.py
```

## Best Practices

### Node.js
- Use `nvm` for managing Node.js versions
- Keep `node_modules` in `.gitignore`
- Use `npm ci` in CI/CD pipelines
- Specify exact versions in `package-lock.json`

### Python
- Use virtual environments
- Pin dependencies in `requirements.txt`
- Use `uv` for faster package installation
- Keep `__pycache__` and `*.pyc` in `.gitignore`

## Common Issues

### Node.js
- **ENOENT errors**: Check file paths and permissions
- **Memory limits**: Increase with `--max-old-space-size`
- **Version conflicts**: Use `nvm` to manage versions

### Python
- **Permission errors**: Use `--user` flag or virtualenv
- **Version conflicts**: Use virtual environments
- **Missing dependencies**: Check system packages

## Resources
- [Node.js Documentation](https://nodejs.org/docs/latest/api/)
- [npm Documentation](https://docs.npmjs.com/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [uv Documentation](https://github.com/astral-sh/uv)
