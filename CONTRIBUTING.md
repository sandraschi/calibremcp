# Contributing to calibre-mcp

Thank you for your interest in contributing to calibre-mcp! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct. By participating, you agree to uphold this code.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Calibre installed and running
- Git
- Basic understanding of MCP (Model Context Protocol)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/calibre-mcp.git
   cd calibre-mcp
   ```

2. **Install Dependencies**
   ```bash
   # Install uv if you haven't already
   pip install uv
   
   # Install project dependencies
   uv sync --dev
   ```

3. **Set Up Environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your Calibre server details
   CALIBRE_SERVER_URL=http://localhost:8080
   CALIBRE_USERNAME=your_username
   CALIBRE_PASSWORD=your_password
   ```

4. **Verify Setup**
   ```bash
   # Run tests
   uv run pytest tests/ -v
   
   # Run linting
   uv run ruff check .
   ```

## Contributing Process

### 1. Create an Issue

Before starting work, please:
- Check existing issues to avoid duplicates
- Create an issue describing the problem or feature
- Wait for maintainer approval before starting work

### 2. Create a Branch

   ```bash
   git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes

Follow the [Code Standards](#code-standards) and ensure all tests pass.

### 4. Test Your Changes

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_your_feature.py -v

# Run with coverage
uv run pytest tests/ --cov=src/calibre_mcp --cov-report=html
```

### 5. Submit a Pull Request

- Push your branch to your fork
- Create a pull request with a clear description
- Link to the related issue
- Ensure CI checks pass

## Code Standards

### Python Standards

- **Python Version**: 3.11+
- **Type Hints**: Required for all functions
- **Async**: MCP tools must be async
- **Linting**: ruff (replaces flake8, black, isort)
- **Type Checking**: mypy

### Code Style

```python
# Good example
async def search_books(
    query: str,
    limit: int = 10,
    offset: int = 0
) -> List[Book]:
    """Search for books with optional filters.
    
    Args:
        query: Search query string
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        List of matching books
        
    Raises:
        CalibreError: If search fails
    """
    # Implementation here
    pass
```

### Import Organization

```python
# Standard library imports
import asyncio
from typing import List, Optional

# Third-party imports
import httpx
from pydantic import BaseModel

# Local imports
from .models import Book
from .exceptions import CalibreError
```

### Error Handling

```python
# Good error handling
try:
    result = await calibre_api.search(query)
except httpx.HTTPError as e:
    raise CalibreError(f"Search failed: {e}") from e
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise CalibreError("Unexpected error occurred") from e
```

## Testing

### Test Structure

```
tests/
├── test_basic.py          # Basic functionality tests
├── test_api.py            # API integration tests
├── test_models.py         # Model validation tests
├── test_tools.py          # MCP tool tests
└── fixtures/              # Test data and fixtures
```

### Writing Tests

```python
import pytest
from calibre_mcp.models import Book
from calibre_mcp.tools.book_tools import search_books

@pytest.mark.asyncio
async def test_search_books():
    """Test book search functionality."""
    # Arrange
    query = "python programming"
    
    # Act
    result = await search_books(query, limit=5)
    
    # Assert
    assert isinstance(result, list)
    assert len(result) <= 5
    for book in result:
        assert isinstance(book, Book)
```

### Test Categories

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **API Tests**: Test Calibre server communication
- **Performance Tests**: Test with large datasets

## Documentation

### Documentation Standards

Follow the [Central Documentation Standards](D:\Dev\repos\mcp-central-docs\STANDARDS.md).

### Required Documentation

- **README.md**: Project overview and quick start
- **CHANGELOG.md**: Version history
- **docs/**: Detailed documentation
- **Docstrings**: All public functions/methods

### Documentation Updates

When adding features:
- Update relevant documentation
- Add examples to docstrings
- Update CHANGELOG.md
- Test all examples

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

Before creating a release:
- [ ] All tests pass
- [ ] No ruff errors
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers consistent
- [ ] Security scan passed

### Creating a Release

1. **Update Version**
   ```bash
   # Update pyproject.toml and __init__.py
   # Update CHANGELOG.md
   ```

2. **Create Release**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Monitor CI/CD**
   - Check GitHub Actions
   - Verify PyPI upload
   - Test installation

## Development Workflow

### Daily Development

```bash
# Start development session
git pull origin main
uv sync --dev

# Make changes
# ... edit code ...

# Test changes
uv run pytest tests/ -v
uv run ruff check .

# Commit changes
git add .
git commit -m "feat: add new feature"
git push origin feature/your-feature
```

### Debugging

```bash
# Run with debug logging
CALIBRE_LOG_LEVEL=DEBUG uv run python -m calibre_mcp.mcp_server

# Test specific functionality
uv run python -c "
import asyncio
from calibre_mcp.tools.book_tools import search_books

async def test():
    result = await search_books('python')
    print(result)

asyncio.run(test())
"
```

## Performance Considerations

### For Large Libraries (10,000+ books)

- Use pagination for large result sets
- Implement caching for frequent queries
- Optimize database queries
- Consider background processing for heavy operations

### Memory Management

- Use generators for large datasets
- Implement proper cleanup
- Monitor memory usage in tests

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project directory
   cd calibre-mcp
   
   # Check Python path
   uv run python -c "import sys; print(sys.path)"
   ```

2. **Test Failures**
   ```bash
   # Run with verbose output
   uv run pytest tests/ -v -s
   
   # Run specific test
   uv run pytest tests/test_specific.py::test_function -v
   ```

3. **Calibre Connection Issues**
   ```bash
   # Test Calibre server
   curl http://localhost:8080/opds
   
   # Check environment variables
   uv run python -c "from calibre_mcp.config import CalibreConfig; print(CalibreConfig())"
   ```

## Getting Help

- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Email**: Contact maintainers directly

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- README.md contributors section
- Release notes

---

**Thank you for contributing to calibre-mcp!** 🚀