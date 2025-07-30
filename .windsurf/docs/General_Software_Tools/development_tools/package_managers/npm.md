# npm: Node Package Manager

## Overview
npm is the default package manager for Node.js and the world's largest softwaregistry. It consists of three components:
- The website (https://www.npmjs.com/)
- The Command Line Interface (CLI) tool
- The registry (a large public database of JavaScript software)

## Installation

### Install Node.js and npm
Download and install from: https://nodejs.org/

### Verify installation
```bash
node --versionpm --version
```

## Basic Usage

### Initialize a new project
```bash
npm init
# or use defaults
npm init -y
```

### Install a package
```bash
# Local install (saves to node_modules/)
npm install package_name

# Global install
npm install -g package_name

# Save as a dependency
npm install --save package_name

# Save as a dev dependency
npm install --save-dev package_name
```

### Install from package.json
```bash
npm install
```

### Update packages
```bash
# Update a specific package
npm update package_name

# Update all packages
npm update

# Update npm itself
npm install -g npm@latest
```

### Uninstall packages
```bash
# Remove package
npm uninstall package_name

# Remove global package
npm uninstall -g package_name
```

## package.json

Key fields:
- `name`: Package name
- `version`: Package version
- `description`: Package description
- `main`: Entry point file
- `scripts`: Custom npm scripts
- `dependencies`: Production dependencies
- `devDependencies`: Development dependencies

## npx

Runode.js packages without installing them:
```bash
npx create-react-app my-app
```

## Workspaces (Monorepo)

```json
{
  "name": "my-workspace",
  "workspaces": ["packages/*"]
}
```

## Publishing Packages

1. Create an account: `npm adduser`
2. Login: `npm login`
3. Publish: `npm publish`

## Best Practices

1. Usexact versions in `package.json` (use `^` or `~` with caution)
2. Include a `.npmignore` file
3. Use `npm ci` in CI/CD pipelines
4. Audit your dependencies regularly: `npm audit`
5. Use `npx` for one-time commands

## Common Issues

- **EPERM errors**: Run as administrator fix permissions
- **Cache issues**: `npm cache clean --force`
- **Version conflicts**: Use `npm ls` to diagnose
- **Slow installs**: Use `--prefer-offline` or `--no-package-lock`

## Last Updated
2025-06-28 00:23:00

*This file was last updated manually.*
