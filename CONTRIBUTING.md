# Contributing to Calibre MCP

Thank you for your interest in contributing to Calibre MCP! We welcome contributions from everyone, regardless of experience level.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Issues](#reporting-issues)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [License](#license)

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
   ```bash
   git clone https://github.com/your-username/calibremcp.git
   cd calibremcp
   ```
3. Set up the development environment (see below)

## Development Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e .[dev,test]
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Making Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines

3. Add tests for your changes

4. Run tests to ensure everything works:
   ```bash
   pytest tests/
   ```

5. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add new feature: your feature description"
   ```

## Testing

Run the full test suite:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest --cov=calibre_mcp tests/
```

## Submitting a Pull Request

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a pull request against the `main` branch

3. Fill out the PR template with all relevant information

4. Ensure all CI checks pass

## Reporting Issues

Please use the [issue templates](.github/ISSUE_TEMPLATE) to report bugs or request features.

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all function parameters and return values
- Keep lines under 100 characters when possible
- Use docstrings for all public modules, classes, and functions
- Write tests for all new functionality

## Documentation

- Update the relevant documentation when adding new features
- Keep docstrings up to date
- Add examples for new features

## License

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) file.
