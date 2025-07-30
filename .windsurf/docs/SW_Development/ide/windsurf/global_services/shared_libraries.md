# Shared Libraries

## Overview

The Shared Librariesystem provides a centralized repository of reusable code components that can be shared across multiple projects. It promotes code reuse, consistency, and maintainability across the Windsurf ecosystem.

## Directory Structure

```
.windsurf/lib/
├── python/                 # Python libraries
│   ├── common-utils/
│   │   ├── pyproject.toml
│   │   └── src/
│   └── data-processing/
│       ├── pyproject.toml
│       └── src/
├── javascript/            # JavaScript/TypeScript libraries
│   ├── ui-components/
│   │   ├── package.json
│   │   └── src/
│   └── api-client/
│       ├── package.json
│       └── src/
├── schemas/               # Shared schemas (JSON Schema, Protobuf, etc.)
│   ├── events/
│   └── models/
└── templates/             # Code generation templates
    ├── python/
    └── typescript/
```

## Key Features

- **Version Control**: Each library is independently versioned
- **Dependency Management**: Automatic dependency resolution
- **Language Support**: Multi-language support with standard layouts
- **Documentation**: Integrated API documentation
- **Testing**: Standardized testing frameworks

## Using Shared Libraries

### Python Example
```python
# pyproject.toml
[project]
dependencies = [
    "windsurf-common-utils>=1.2.0",
    "windsurf-data-processing>=2.0.0",
]

# In your code
from windsurf.common_utils import logging
from windsurf.data_processing import process_data
```

### JavaScript/TypeScript Example
```javascript
// package.json
{
  "dependencies": {
    "@windsurf/ui-components": "^1.0.0",
    "@windsurf/api-client": "^2.0.0"
  }
}

// In your code
import { Button } from '@windsurf/ui-components';
import { ApiClient } from '@windsurf/api-client';
```

## Creating a New Library

1. **Initialize Library**
   ```bash
   # Create new Python library
   windsurf lib create python my-library
   
   # Create new TypeScript library
   windsurf lib create typescript my-library
   ```

2. **Library Structure**
   ```
   my-library/
   ├── pyproject.toml      # Python package config
   ├── README.md           # Library documentation
   ├── src/                # Source code
   │   └── my_library/
   │       ├── __init__.py
   │       └── module.py
   ├── tests/              # Unitests
   └── docs/               # API documentation
   ```

## Versioning

Libraries follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes

## Publishing

### Automated Publishing
Libraries are automatically published when changes are merged to main:

1. Update version in `pyproject.toml` or `package.json`
2. Create a release tag (e.g., `v1.2.3`)
3. CI/CD pipeline handles the rest

### Manual Publishing
```bash
# Build package
windsurf libuild my-library

# Publish to registry
windsurf lib publish my-library --version 1.0.0
```

## Best Practices

1. **Single Responsibility**
   - Each library should have a single, focused purpose
   - Keep librariesmall and focused

2. **Documentation**
   - Include comprehensive API documentation
   - Add usagexamples
   - Document version compatibility

3. **Testing**
   - Maintain high test coverage
   - Include integration tests
   - Test against multiple versions of dependencies

## Dependency Management

### Python
- Use `pyproject.toml` with `poetry`
- Pin direct dependencies
- Use caret (^) for compatible updates

### JavaScript/TypeScript
- Use `package.json` with exact versions
- Include `peerDependencies`
- Update `CHANGELOG.md` for breaking changes

## Security

- Regularly update dependencies
- Scan for vulnerabilities
- Sign releases with GPG
- Follow secure coding practices

## Integration

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latesteps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: |
          pip install poetry install
      - name: Run tests
        run: poetry run pytest
```

## Troubleshooting

**Issue**: Dependency conflicts
- Check version constraints
- Use `poetry show --tree` to inspect dependencies
- Consider using dependency overrides if needed

**Issue**: Build failures
- Verify build environment
- Check for missing system dependencies
- Review build logs for errors

---
*Last Updated: 2025-06-23*
