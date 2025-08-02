---
trigger: always_on
version: 2.1.0
last_updated: 2025-07-30
changelog:
  - 2.1.0: Added FastMCP 2.10 repository and DXT packaging rules
  - 2.0.0: Restructured rules and added versioning
  - 1.0.0: Initial version
---

# SandrasRules (Global Rulebook)

## Table of Contents
- [Change Management](#change-management)
- [Development Workflow](#development-workflow)
- [FastMCP 2.10 Repository Standards](#fastmcp-210-repository-standards)
- [DXT Packaging Standards](#dxt-packaging-standards)
- [Bug & Research Handling](#bug--research-handling)

## Change Management

### Rule to prove this was read
- Add "lgr1 " to cascade outputs

### Change Control
- Never remove, rewrite, or break major functionality without explicit user instruction
- Always clarify and confirm before making breaking changes
- Provide explicit diffs and summaries for all major edits
- Follow user-specified workflow preferences strictly
- Set up safety nets like auto-staged commits when possible

## Development Workflow

### Windows/PowerShell Script Syntax

#### 1. File System Operations

##### Directory Operations
```powershell
# Create directory (and parent directories if needed)
New-Item -ItemType Directory -Force -Path "path\to\directory"

# Remove directory (recursively)
Remove-Item -Path "path\to\directory" -Recurse -Force

# Change directory
Set-Location -Path "path\to\directory"
# Or use cd (alias for Set-Location)
cd "path\to\directory"
```

##### File Operations
```powershell
# View file content
Get-Content -Path "file.txt"

# View last N lines of a file
Get-Content -Path "file.log" -Tail 10

# View first N lines of a file
Get-Content -Path "file.log" -TotalCount 10

# Check if file exists
Test-Path -Path "file.txt"
```

#### 2. Command Chaining

##### Correct (PowerShell)
```powershell
# Sequential commands
command1; command2; command3

# Conditional execution (run command2 only if command1 succeeds)
command1 -ErrorAction Stop; if ($?) { command2 }

# Pipeline chaining
Get-Process | Where-Object { $_.CPU -gt 10 } | Sort-Object -Property CPU -Descending
```

##### Incorrect (Linux-style)
```bash
# Don't use Linux-style chaining
command1 && command2
command1 || command2
```

#### 3. Common Command Equivalents

| Linux Command | PowerShell Equivalent | Notes |
|---------------|----------------------|-------|
| `ls` | `Get-ChildItem` or `dir` | `dir` is an alias for `Get-ChildItem` |
| `cat` | `Get-Content` | |
| `grep` | `Select-String` or `sls` | `sls` is an alias for `Select-String` |
| `find` | `Get-ChildItem -Recurse` | For finding files |
| `pwd` | `Get-Location` or `pwd` | `pwd` is an alias for `Get-Location` |
| `rm -rf` | `Remove-Item -Recurse -Force` | |
| `chmod` | `icacls` or `Set-Acl` | |
| `echo` | `Write-Output` or `echo` | `echo` is an alias for `Write-Output` |

#### 4. Environment Variables

```powershell
# Set environment variable (current session)
$env:VARIABLE_NAME = "value"

# Set persistent environment variable (user scope)
[System.Environment]::SetEnvironmentVariable("VARIABLE_NAME", "value", "User")

# Get environment variable
$value = $env:VARIABLE_NAME
```

#### 5. Error Handling

```powershell
try {
    # Command that might fail
    Remove-Item -Path "nonexistent.txt" -ErrorAction Stop
} catch {
    Write-Error "Failed to remove file: $_"
    # Handle error
}
```

#### 6. Script Execution Policy

```powershell
# Check current execution policy
Get-ExecutionPolicy

# Set execution policy (requires admin)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 7. Path Handling

```powershell
# Join paths (cross-platform compatible)
$fullPath = Join-Path -Path "C:\parent" -ChildPath "child"

# Get absolute path
$absolutePath = Resolve-Path -Path "./relative/path"
```

#### 8. Best Practices
- Always use full cmdlet names in scripts (e.g., `Remove-Item` instead of `rm`)
- Use `-WhatIf` parameter to test destructive commands
- Prefer `-Filter` over `Where-Object` for better performance with file operations
- Use `-ErrorAction Stop` for critical commands that should terminate on failure
- Always validate paths with `Test-Path` before operations

### 1. Version Control
- Use feature branches for all changes
- Write clear, descriptive commit messages
- Open pull requests for code review
- Keep main branch stable and deployable

### 2. Code Style
- Follow language-specific style guides
- Use consistent indentation (spaces)
- Include comments for complex logic
- Keep lines under 120 characters

## Basic Memory Notes

**CRITICAL**: All Basic Memory notes MUST include a timestamp in their title or at the start of content. This is required for proper sorting and retrieval.

### 1. Note Structure
- **Title Format**: `[YYYY-MM-DD HH:MM] Clear, descriptive title`
- Start with a brief summary
- Use hierarchical headers for organization
- **Always include**:
  - Creation timestamp (if not in title)
  - Last updated timestamp
  - Author/initials
  - Relevant project/topic tags
- Add relevant categorization tags

### 2. Content Guidelines
- Be concise but thorough
- Use bullet points for lists
- Include code blocks with language specification
- Add context and reasoning, not just facts
- Note sources and references

## Docker Standards

### 1. Containerization
- Use multi-stage builds to minimize image size
- Specify exact versions for base images
- Run as non-root user when possible
- Use `.dockerignore` to exclude unnecessary files
- Keep containers ephemeral

### 2. Docker Compose
- Use version 3.x+ syntax
- Define resource limits
- Use environment files for sensitive data
- Set up proper networking
- Include health checks

### 3. Best Practices
- One process per container
- Use volumes for persistent data
- Implement proper logging
- Set up proper restart policies
- Document exposed ports and volumes

## GitHub Standards

### 1. Repository Setup
- Include comprehensive README.md
- Add .gitignore appropriate for the project
- Set up branch protection rules
- Configure required status checks
- Add issue and PR templates

### 2. Workflow
- Use feature branches
- Require PR reviews
- Squash and merge by default
- Delete merged branches
- Use semantic versioning for releases

## Monitoring & Observability

### 1. Prometheus
- Define clear metric names and labels
- Use appropriate metric types (counter, gauge, histogram)
- Set up proper retention policies
- Document all metrics

### 2. Grafana
- Create meaningful dashboards
- Use variables for flexibility
- Set up proper alerting
- Document data sources and queries

### 3. Loki & Promtail
- Use proper label indexing
- Set up log rotation
- Define log retention policies
- Document log formats

## Basic Memory Notes (continued)

### 3. Examples
```markdown
# [2025-07-30 14:30] Project Meeting Notes

## Key Decisions
- Decision to migrate to FastMCP 2.10 by Q4 2025
- All new MCP servers must follow DXT packaging standards

## Action Items
- [ ] Update documentation for new standards
- [ ] Create migration guide for existing servers

## Technical Notes
```

## FastMCP 2.10 Compliance Standards

**IMPORTANT**: All MCP servers MUST comply with these standards. Legacy/non-compliant servers must be updated to match these specifications.

## General Coding Principles

### 1.1 Reliability
- The application must never crash due to external API failures
- Always provide fallback mechanisms for critical functionality
- Graceful degradation is preferred over complete failure

### 1.2 Code Quality
- All code must be readable and self-documenting
- Follow language-specific style guides (PEP 8 for Python, etc.)
- Use meaningful variable and function names
- Keep functions small and focused (max 50 lines)
- Document all public interfaces

## 2. Repository Structure
```
mcp-project/
├── .github/              # GitHub Actions workflows
├── .windsurf/            # Windsurf configuration
│   └── rules/
│       └── global_rules/ # Symlinks to master rules1.md and rules2.md
├── docs/                 # Documentation
├── src/                  # Source code
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   └── tools/            # MCP tool implementations
│       ├── __init__.py
│       └── [tool_category]/  # Group related tools (e.g., file_operations)
│           └── __init__.py  # Tool implementations
├── tests/                # Unit and integration tests
├── .gitignore
├── pyproject.toml        # Project metadata and dependencies
└── README.md
```

### 2. Naming Conventions
- **Repository Names**:
  - Must end with `-mcp` (e.g., `filesystem-mcp`, `llm-mcp`)
  - Use kebab-case (e.g., `my-service-mcp`)
- **Python Code**:
  - `snake_case` for modules and packages
  - `PascalCase` for class names
  - `UPPER_SNAKE_CASE` for constants
- **Markdown Files**:
  - Use `Title Case` for headings
  - End headers with no punctuation
  - Use `-` for list items
  - Wrap code blocks with blank lines
  - Specify language for code blocks
  - Maximum line length: 120 characters
  - Use proper heading hierarchy (H1 → H2 → H3)
  - One sentence per line for better diffing

### 3. Versioning
- Follow Semantic Versioning (MAJOR.MINOR.PATCH)
- Update version in `pyproject.toml` and `__init__.py`
- Create a Git tag for each release

## 4. GitHub Repository Management

### 4.1 Repository Setup
- **Naming Conventions**:
  - Use lowercase with hyphens (e.g., `mcp-server-name`)
  - End MCP server repositories with `-mcp` (e.g., `handbrake-mcp`)
  - Keep names concise but descriptive

- **Repository Settings**:
  - Set repository to `Public` unless there's a specific reason for private
  - Enable `Issues` and `Discussions`
  - Enable `Allow auto-merge`
  - Enable `Automatically delete head branches`
  - Set `Allow squash merging` as default merge method
  - Protect `main` and `develop` branches

- **Branch Protection Rules**:
  - Require pull request before merging
  - Require status checks to pass before merging
  - Require branches to be up to date before merging
  - Require linear history
  - Require conversation resolution before merging
  - Do not allow bypassing the above settings

### 4.2 Branching Strategy
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/` - New features (e.g., `feature/user-authentication`)
- `bugfix/` - Bug fixes (e.g., `bugfix/login-error`)
- `release/` - Release preparation (e.g., `release/1.2.0`)
- `hotfix/` - Critical production fixes (e.g., `hotfix/security-patch`)

### 4.3 Issue Management
- **Issue Templates**:
  - Bug Report
  - Feature Request
  - Documentation Update
  - Question/Help

- **Labels**:
  - `bug` - Something isn't working
  - `enhancement` - New feature or improvement
  - `documentation` - Documentation changes
  - `question` - Further information is requested
  - `help wanted` - Extra attention is needed
  - `good first issue` - Good for newcomers
  - `priority: high/medium/low` - Issue priority
  - `status: blocked` - Blocked by other issues
  - `status: in progress` - Actively being worked on

- **Issue Lifecycle**:
  1. Create issue with clear title and description
  2. Add appropriate labels and assignees
  3. Link related issues/PRs
  4. Move to "In Progress" when work starts
  5. Link PR that resolves the issue
  6. Close when resolved and verified

### 4.4 Pull Request Process
- **PR Title**:
  - Start with type: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`
  - Use imperative mood ("Add" not "Added" or "Adds")
  - Keep it under 50 characters
  - Reference issue number (e.g., `fix: resolve login error #123`)

- **PR Description**:
  - Reference related issues (closes #123, fixes #456)
  - Describe the changes and motivation
  - Include screenshots for UI changes
  - Update documentation if needed
  - List any breaking changes

- **Code Review**:
  - At least one approval required before merging
  - All CI checks must pass
  - Code must be up to date with target branch
  - No merge conflicts
  - Follows coding standards

### 4.5 Release Management
- **Versioning**:
  - Follow Semantic Versioning (MAJOR.MINOR.PATCH)
  - Use GitHub Releases for versioning
  - Create a changelog entry for each release

- **Release Process**:
  1. Create `release/x.y.z` branch from `develop`
  2. Update version in `pyproject.toml` and `__init__.py`
  3. Update CHANGELOG.md with release notes
  4. Create PR to merge into `main`
  5. After approval, merge with `--no-ff`
  6. Tag the release with version (v1.2.3)
  7. Create GitHub Release with changelog
  8. Merge `main` back into `develop`

### 4.6 GitHub Actions
- **Required Workflows**:
  - CI/CD pipeline
  - Code quality checks
  - Security scanning
  - Test coverage reporting
  - Documentation deployment

- **Secrets Management**:
  - Store sensitive data in GitHub Secrets
  - Never hardcode secrets in workflows
  - Use environment-specific secrets when needed

### 4.7 Project Boards
- Use GitHub Projects for tracking progress
- Create columns for: Backlog, To Do, In Progress, Review, Done
- Automate issue/PR movement with GitHub Actions
- Use milestones for version tracking

### 4.8 Documentation
- Maintain a comprehensive README.md
- Keep CONTRIBUTING.md up to date
- Document setup and deployment processes
- Include code examples and API documentation

### 4.9 Community Guidelines
- Adopt a Code of Conduct
- Be welcoming to new contributors
- Acknowledge all contributions
- Keep communication professional and respectful

### 4.10 Security

#### 4.10.1 Dependency Management
- **Dependabot**:
  - Enable Dependabot for automated dependency updates
  - Configure in `.github/dependabot.yml`
  - Set update schedule (weekly for most repositories)

- **Version Pinning**:
  - Use `requirements.txt` with exact versions
  - Example: `package==1.2.3` (not `package>=1.2.3`)
  - Use hashes for critical dependencies

- **Dependency Auditing**:
  - Run `safety check` or `pip-audit` in CI
  - Review and update dependencies monthly
  - Monitor for known vulnerabilities

#### 4.10.2 Static Analysis with Semgrep
- **Configuration**:
  - Required file: `.semgrep.yml` in repository root
  - Include standard security rules
  - Add MCP-specific custom rules

- **CI Integration**:
  - Required workflow: `.github/workflows/semgrep.yml`
  - Run on all PRs and pushes to main/develop
  - Block PRs with critical/high severity issues

- **Custom Rules**:
  - Check for MCP-specific security patterns
  - Enforce authentication on API endpoints
  - Detect hardcoded secrets
  - Prevent unsafe deserialization

#### 4.10.3 Security Scanning
- **SAST/DAST**:
  - Run weekly scans using GitHub CodeQL
  - Configure in `codeql-analysis.yml`
  - Review and address findings

- **Dependency Scanning**:
  ```bash
  # Install tools
  pip install safety pip-audit
  
  # Run scans
  safety check
  pip-audit
  ```

#### 4.10.4 Best Practices
- **Secrets Management**:
  - Never commit secrets to version control
  - Use GitHub Secrets for CI/CD
  - Rotate secrets regularly
  - Use environment variables in production

- **Access Control**:
  - Follow principle of least privilege
  - Use role-based access control (RBAC)
  - Regularly review access permissions

- **Documentation**:
  - Maintain `SECURITY.md` with:
    - Reporting process for vulnerabilities
    - Security update policy
    - Contact information for security issues

#### 4.10.5 Required Files
1. `.github/workflows/semgrep.yml` - Semgrep CI workflow
2. `.semgrep.yml` - Custom Semgrep rules
3. `SECURITY.md` - Security policy and reporting
4. `.github/dependabot.yml` - Dependabot configuration

### 4.11 Repository Maintenance
- Regularly update dependencies
- Close stale issues and PRs
- Archive inactive repositories
- Keep documentation current

## 5. DXT Packaging Standards (FastMCP 2.10+)

**Note**: These standards apply to all FastMCP 2.10+ servers. All new MCP servers must implement these packaging standards.

### 2.1 Package Structure
```
package/
├── package/             # Python package
│   ├── __init__.py
│   └── core.py
├── scripts/             # Command-line scripts
├── tests/               # Package tests
├── pyproject.toml       # Build system config
└── README.md
```

### 2.2 pyproject.toml Example
```toml
[build-system]
requires = ["setuptools>=42"]
build-backend = "setuptools.build_meta"

[project]
name = "example-package"
version = "0.1.0"
description = "A short description"
authors = [
    {name="Your Name", email="your.email@example.com"},
]
dependencies = [
    "requests>=2.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "black>=21.5b2",
]

[project.scripts]
mycli = "mypackage.cli:main"
```

### 2.3 Building and Publishing
```bash
# Install build tools
python -m pip install --upgrade build twine

# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Bug & Research Handling

### 1. Bug Reports (`bug: ... :bug`)
1. Research the bug thoroughly
2. Create directory: `/.windsurf/docs/flows/bugs/YYMMDD_short-description/`
3. Add files:
   - `bug.md`: Original bug description
   - `analysis.md`: Your findings and solution

### 2. Research Requests (`research: ... :research`)
1. Research the topic thoroughly (300 lines optimal)
2. Create directory: `/.windsurf/docs/flows/research/YYMMDD_short-topic/`
3. Split into markdown files:
   - `chunk_01.md`
   - `chunk_02.md`
   - etc.

## Security & Best Practices

### 1. Authentication
- Never hardcode credentials
- Use environment variables for sensitive data
- Follow principle of least privilege

### 2. Dependencies
- Keep dependencies up to date
- Audit for known vulnerabilities
- Document all third-party dependencies

### 3. Error Handling
- Never expose stack traces to end users
- Log errors with sufficient context
- Implement graceful degradation

## Documentation Standards

### 1. Code Documentation
- Document public APIs and interfaces
- Keep README files updated
- Document environment setup

### 2. Project Documentation
- Maintain CHANGELOG.md
- Document architectural decisions
- Keep documentation in sync with code

## Performance Guidelines

### 1. Optimization
- Profile before optimizing
- Optimize for readability first
- Consider memory usage and execution time

### 2. Testing
- Write tests for new features
- Maintain good test coverage
- Run tests before merging to main

## File Organization

### 1. Modular Architecture
- Keep files under 300 lines
- Group related functionality
- Use clear, descriptive names

### 2. Directory Structure

#### For non-MCP repositories:
```
project/
├── src/                # Source code
├── tests/              # Test files
├── docs/               # Documentation
├── scripts/            # Utility scripts
└── .github/            # GitHub configurations
```

### Prompts vs. Scripts

### Prompts (DXT-specific)
- Used for dynamic text generation and processing
- Stored in `prompts/` directory
- Follow DXT prompt engineering guidelines
- Version controlled with the code

### Scripts
- Executable utilities and automation
- Stored in `scripts/` directory
- Must be written in PowerShell (Windows) or shell (Linux/Unix)
- Include proper error handling and logging

## Markdown Linting Rules

### 1. Headers
- Add one blank line before and after headers
- No trailing punctuation in headers
- Use proper header hierarchy (H1 → H2 → H3)

### 2. Lists
- Add blank lines before and after lists
- Use `-` for unordered lists
- Indent nested lists with 2 spaces

### 3. Code Blocks
- Surround with blank lines
- Specify language after opening backticks
- Keep lines under 120 characters

### 4. Links and Images
- Use descriptive link text
- Place URLs at the bottom if using reference-style links
- Add alt text for images

### 5. Tables
- Use pipes and dashes
- Align columns properly
- Add blank lines before and after

### 6. Line Length
- Maximum 120 characters per line
- Break long URLs if needed
- Use proper line wrapping for long sentences

## Code Review Process

### 1. Review Checklist
- [ ] Code follows style guide
- [ ] Tests are included
- [ ] Documentation is updated
- [ ] No commented-out code
- [ ] No sensitive data exposed

### 2. Approval Process
- At least one approval required
- All tests must pass
- Resolve all comments before merging

## Markdown and Documentation Standards

### 1. File Structure
- All documentation files must have YAML frontmatter with:
  - `title`: Document title
  - `description`: Brief description
  - `last_updated`: Last update date (ISO 8601 format)
  - `version`: Document version (SemVer)
  - `toc`: true/false (whether to show table of contents)
  - `tags`: List of relevant tags

### 2. Content Organization
- Use H1 (#) for main title only
- Use H2 (##) for main sections
- Use H3 (###) for subsections
- Keep lines under 120 characters
- Use one sentence per line for better diffing
- Include a table of contents for documents >100 lines

### 3. Code Blocks
- Always specify the language after the opening backticks
- Include comments explaining complex code blocks
- Keep code blocks focused and concise
- Include expected output when relevant

## Repository Structure Standards

### 1. Required Files
- `README.md`: Project overview and setup instructions
- `CONTRIBUTING.md`: Contribution guidelines
- `CHANGELOG.md`: Version history
- `.gitignore`: Appropriate for the project language
- `pyproject.toml`/`setup.py`: For Python projects
- `requirements.txt`/`Pipfile`: Python dependencies
- `Dockerfile` (if applicable)
- `.dockerignore` (if using Docker)

### 2. Directory Structure
```
project/
├── src/                    # Source code
├── tests/                  # Test files
├── docs/                   # Documentation
│   ├── api/                # API documentation
│   ├── guides/             # How-to guides
│   └── images/             # Documentation images
├── scripts/                # Utility scripts
├── .github/                # GitHub configurations
│   ├── workflows/          # GitHub Actions
│   └── ISSUE_TEMPLATE/     # Issue templates
└── .vscode/                # VS Code settings (optional)
```

## Code Quality Standards

### 1. Python Specific
- Use type hints for all function/method signatures
- Follow PEP 8 style guide
- Maximum function length: 50 lines
- Maximum class length: 300 lines
- Minimum test coverage: 80%
- Use docstrings for all public modules, classes, and functions

### 2. Error Handling
- Use specific exception types
- Include context in error messages
- Log errors before raising when appropriate
- Use custom exception classes for domain-specific errors

## CI/CD Standards

### 1. Required Checks
- Linting (flake8, black, isort for Python)
- Unit tests with coverage reporting
- Integration tests (if applicable)
- Security scanning (dependabot, bandit, etc.)
- Build verification

### 2. Deployment
- Use semantic versioning (SemVer)
- Automate releases with GitHub Actions
- Include release notes generation
- Verify deployments with health checks

## Dependency Management

### 1. Python Dependencies
- Pin all direct dependencies with exact versions
- Use `pyproject.toml` for Python packages
- Include `requirements-dev.txt` for development dependencies
- Regularly update dependencies with dependabot

### 2. Security
- Scan for vulnerabilities in dependencies
- Never store secrets in version control
- Use environment variables or secret management
- Keep dependencies updated

## Security Standards

### 1. General
- Follow principle of least privilege
- Validate all inputs
- Sanitize all outputs
- Use prepared statements for database queries
- Implement rate limiting for public APIs

### 2. Authentication & Authorization
- Use OAuth 2.0 or OpenID Connect for authentication
- Implement role-based access control (RBAC)
- Use secure password hashing (bcrypt, Argon2)
- Implement proper session management

## Performance Guidelines

### 1. Application Performance
- Optimize database queries (use indexes, avoid N+1 queries)
- Implement caching where appropriate
- Use pagination for large datasets
- Monitor and optimize memory usage

### 2. API Performance
- Implement response compression
- Use HTTP caching headers
- Support conditional requests (ETag, Last-Modified)
- Document rate limits

## Logging and Monitoring

### 1. Logging Standards
- Use structured logging (JSON format)
- Include correlation IDs
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Include timestamps in UTC

### 2. Monitoring
- Track key metrics (response times, error rates, etc.)
- Set up alerts for critical issues
- Monitor resource usage
- Track business metrics

## API Design Standards

### 1. REST API Guidelines
- Use nouns for resources, not verbs
- Use plural nouns for collections
- Use kebab-case for URLs
- Use camelCase for JSON properties
- Use HTTP methods appropriately (GET, POST, PUT, PATCH, DELETE)

### 2. Versioning
- Version APIs in the URL path (`/api/v1/...`)
- Include API version in response headers
- Document breaking changes
- Support multiple versions during transition periods

### 3. Error Handling
- Return appropriate HTTP status codes
- Provide helpful error messages
- Include error codes for programmatic handling
- Document all possible error responses

## Documentation Requirements

### 1. Code Documentation
- Document all public APIs
- Include examples in docstrings
- Document all configuration options
- Include type information in function signatures

### 2. Project Documentation
- Keep README up to date
- Document setup and installation
- Include troubleshooting guide
- Document deployment process

## Testing Standards

### 1. Test Structure
- Follow Arrange-Act-Assert pattern
- Keep tests independent
- Use descriptive test names
- Test edge cases and error conditions

### 2. Test Data
- Use factories for test data
- Clean up test data after tests
- Use realistic test data
- Consider using property-based testing

## Code Review Guidelines

### 1. Review Process
- Keep PRs small and focused
- Request reviews from appropriate team members
- Address all comments before merging
- Use GitHub's review features

### 2. What to Look For
- Code correctness
- Performance implications
- Security considerations
- Test coverage
- Documentation updates

## Security Incident Response

### 1. Reporting
- Report security issues immediately
- Use private channels for sensitive discussions
- Document all findings and actions

### 2. Response Process
- Acknowledge receipt of report
- Investigate the issue
- Develop and test a fix
- Deploy the fix
- Notify affected parties

## Performance Monitoring

### 1. Key Metrics
- Response times (p50, p90, p99)
- Error rates
- Resource utilization
- Throughput

### 2. Alerting
- Set up alerts for critical metrics
- Define escalation policies
- Document incident response procedures

## Accessibility Standards

### 1. Web Accessibility
- Follow WCAG 2.1 AA guidelines
- Ensure keyboard navigation
- Provide text alternatives for non-text content
- Use semantic HTML

### 2. API Accessibility
- Provide comprehensive documentation
- Include examples for all endpoints
- Support content negotiation
- Provide machine-readable API specs (OpenAPI)

## Internationalization (i18n)

### 1. String Externalization
- Externalize all user-facing strings
- Use message keys, not hardcoded strings
- Support right-to-left (RTL) languages
- Handle different date/number formats

### 2. Localization (l10n)
- Store translations in standard formats (e.g., .po files)
- Include context for translators
- Test with different languages
- Handle text expansion/contraction

## Error Handling and Logging

### 1. Error Handling
- Use appropriate exception types
- Include context in error messages
- Log errors before handling them
- Provide user-friendly error messages

### 2. Logging
- Use structured logging
- Include correlation IDs
- Log at appropriate levels
- Include timestamps and timezones

## Version Control Best Practices

### 1. Branching Strategy
- Use feature branches for new features
- Create release branches for releases
- Use semantic versioning for tags
- Keep main branch deployable

### 2. Commit Messages
- Use the imperative mood
- Keep the subject line under 50 characters
- Include a blank line between subject and body
- Reference issue numbers when applicable

## Continuous Integration/Deployment

### 1. CI Pipeline
- Run tests on every push
- Enforce code style
- Check for security vulnerabilities
- Generate code coverage reports

### 2. CD Pipeline
- Automate deployments
- Use feature flags
- Implement blue/green deployments
- Include rollback procedures

## Security Hardening

### 1. Application Security
- Use secure defaults
- Implement proper input validation
- Use parameterized queries
- Implement rate limiting

### 2. Infrastructure Security
- Use least privilege principle
- Encrypt data in transit and at rest
- Regular security audits
- Keep systems patched

## Performance Optimization

### 1. Frontend
- Minimize and bundle assets
- Lazy load non-critical resources
- Optimize images
- Implement caching strategies

### 2. Backend
- Optimize database queries
- Implement caching
- Use connection pooling
- Monitor and optimize memory usage

## Monitoring and Alerting

### 1. Application Monitoring
- Track key metrics
- Set up dashboards
- Monitor error rates
- Track performance metrics

### 2. Alerting
- Set up alerts for critical issues
- Define on-call rotations
- Document escalation procedures
- Conduct regular incident reviews

## Documentation Standards

### 1. Code Documentation
- Document all public APIs
- Include examples
- Document edge cases
- Keep documentation up to date

### 2. Project Documentation
- Maintain a README
- Document setup and installation
- Include contribution guidelines
- Keep a changelog

## Testing Strategy

### 1. Test Types
- Unit tests
- Integration tests
- End-to-end tests
- Performance tests

### 2. Test Automation
- Run tests on every PR
- Enforce code coverage requirements
- Automate test data management
- Include performance benchmarks

## Security Best Practices

### 1. Authentication
- Use multi-factor authentication
- Implement account lockout
- Use secure password policies
- Implement session management

### 2. Data Protection
- Encrypt sensitive data
- Implement proper key management
- Follow data minimization principles
- Implement proper data retention policies

## Performance Testing

### 1. Load Testing
- Test under expected peak load
- Identify bottlenecks
- Measure response times
- Monitor resource usage

### 2. Stress Testing
- Test beyond expected load
- Identify breaking points
- Test failover mechanisms
- Monitor recovery times

## Incident Response

### 1. Preparation
- Maintain an incident response plan
- Document escalation paths
- Keep contact information current
- Conduct regular drills

### 2. Response
- Acknowledge the incident
- Contain the impact
- Eradicate the cause
- Recover systems
- Document lessons learned

## Business Continuity

### 1. Backup Strategy
- Regular backups
- Test restores
- Off-site storage
- Versioned backups

### 2. Disaster Recovery
- Document recovery procedures
- Define RTO and RPO
- Regular testing
- Keep documentation current

## Compliance and Auditing

### 1. Regulatory Compliance
- Document compliance requirements
- Implement necessary controls
- Regular audits
- Maintain evidence

### 2. Internal Audits
- Regular security assessments
- Code reviews
- Penetration testing
- Vulnerability scanning

## Change Management

### 1. Change Control
- Document all changes
- Review before implementation
- Test in staging
- Rollback plan

### 2. Release Management
- Version control
- Release notes
- Communication plan
- Post-release verification
