# Pre-commit Hooks Setup

**Status:** ✅ Configured  
**Date:** 2025-11-22  
**Purpose:** Automated code quality checks before commits

---

## Overview

Pre-commit hooks automatically run code quality checks before each commit, catching issues early and ensuring consistent code quality across the project.

---

## Installation

### 1. Install pre-commit

```bash
# Using uv (recommended)
uv sync --dev

# Or using pip
pip install pre-commit
```

### 2. Install Git hooks

```bash
pre-commit install
```

This installs the hooks into `.git/hooks/pre-commit`.

### 3. (Optional) Install commit-msg hook

```bash
pre-commit install --hook-type commit-msg
```

---

## Configuration

The pre-commit configuration is in `.pre-commit-config.yaml` and includes:

### Code Quality Hooks

1. **Ruff** - Fast Python linter and formatter
   - Replaces: black, isort, flake8, pyupgrade, autoflake
   - Runs: `ruff check` and `ruff format`
   - Auto-fixes issues when possible

2. **MyPy** - Static type checking
   - Checks type annotations
   - Excludes tests and scripts

3. **Bandit** - Security vulnerability scanner
   - Scans for common security issues
   - Excludes test files

### File Quality Hooks

4. **General file checks** (pre-commit-hooks)
   - Trailing whitespace removal
   - End of file fixer
   - YAML/JSON/TOML validation
   - Large file detection
   - Merge conflict detection
   - Debug statement detection

5. **Markdown linting** (markdownlint)
   - Validates markdown files
   - Auto-fixes formatting issues

6. **YAML linting** (yamllint)
   - Validates YAML files
   - Config files, GitHub Actions, etc.

7. **Secret detection** (detect-secrets)
   - Prevents committing secrets/credentials
   - Uses baseline file for known false positives

---

## Usage

### Run on staged files (automatic on commit)

```bash
git commit -m "Your message"
# Hooks run automatically
```

### Run on all files

```bash
pre-commit run --all-files
```

### Run specific hook

```bash
pre-commit run ruff --all-files
pre-commit run mypy --all-files
```

### Skip hooks (not recommended)

```bash
git commit --no-verify -m "Skip hooks"
```

---

## What Gets Checked

### On Every Commit

- ✅ **Ruff linting** - Python code quality
- ✅ **Ruff formatting** - Code formatting
- ✅ **MyPy** - Type checking (Python files only)
- ✅ **Trailing whitespace** - Removed automatically
- ✅ **End of file** - Ensures newline at EOF
- ✅ **YAML/JSON/TOML** - Syntax validation
- ✅ **Large files** - Warns if >1MB
- ✅ **Merge conflicts** - Detects conflict markers
- ✅ **Debug statements** - Finds pdb, ipdb, etc.
- ✅ **Secrets** - Detects potential credentials

### Excluded Files

The following are automatically excluded:
- `.git/`, `.venv/`, `venv/`
- `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- `dist/`, `build/`, `.eggs/`
- `uv.lock`, `.coverage`, `htmlcov/`
- Test files (for some hooks)

---

## Integration with CI/CD

Pre-commit hooks run **locally** before commits. The CI/CD pipeline also runs similar checks:

- **CI Workflow** (`.github/workflows/ci.yml`):
  - Runs `ruff check` and `ruff format --check`
  - Runs `mypy` type checking
  - Runs `pytest` with coverage

This ensures:
1. **Local development** - Hooks catch issues before commit
2. **CI validation** - GitHub Actions verify on push/PR
3. **Consistency** - Same checks run locally and in CI

---

## Updating Hooks

### Update all hooks to latest versions

```bash
pre-commit autoupdate
```

### Update specific hook

Edit `.pre-commit-config.yaml` and change the `rev` field, then:

```bash
pre-commit install --install-hooks
```

---

## Troubleshooting

### Hooks are slow

- Hooks only run on changed files by default
- Use `--all-files` only when needed
- Consider excluding large directories in config

### Hook fails but code looks fine

```bash
# Run the hook manually to see detailed output
pre-commit run <hook-id> --all-files --verbose
```

### Skip specific hook for one commit

```bash
SKIP=mypy git commit -m "Skip mypy for this commit"
```

### Reinstall hooks

```bash
pre-commit uninstall
pre-commit install
```

---

## Best Practices

1. **Always run hooks locally** - Catch issues before pushing
2. **Don't skip hooks** - Fix issues instead
3. **Update hooks regularly** - Run `pre-commit autoupdate` monthly
4. **Review hook output** - Understand what's being checked
5. **Customize as needed** - Adjust config for project needs

---

## Comparison: Pre-commit vs CI/CD

| Aspect | Pre-commit (Local) | CI/CD (Remote) |
|--------|-------------------|----------------|
| **When** | Before commit | On push/PR |
| **Speed** | Fast (changed files) | Slower (all files) |
| **Feedback** | Immediate | After push |
| **Auto-fix** | Yes (ruff) | No (check only) |
| **Purpose** | Developer workflow | Quality gate |

**Best Practice:** Use both! Pre-commit for fast local feedback, CI/CD for final validation.

---

## Related Documentation

- [CI/CD Workflows](../.github/workflows/ci.yml) - GitHub Actions configuration
- [Ruff Configuration](../pyproject.toml) - Ruff settings
- [MyPy Configuration](../pyproject.toml) - Type checking settings
- [Development Workflow](../MCP_DEVELOPMENT_WORKFLOW.md) - Complete development guide

---

*Pre-commit Hooks Setup*  
*Location: `.pre-commit-config.yaml`*  
*Last Updated: 2025-11-22*

