# Task Management

## Overview

The Task Management system provides a unified way to define, track, and manage tasks across all projects in the Windsurf ecosystem. It integrates with version control, CI/CD pipelines, and project managementools.

## Directory Structure

```
.windsurf/tasks/
├── global/                # Global task definitions
│   ├── ci-cd/
│   ├── deployment/
│   └── maintenance/
├── projects/              # Project-specific tasks
│   ├── project-a/
│   └── project-b/
├── templates/             # Task templates
│   ├── bug-fix/
│   ├── feature/
│   └── release/
└── workflows/             # Task workflows
    ├── pr-review/
    └── release/
```

## Key Features

- **Task Definitions**: YAML-based task specifications
- **Dependencies**: Define task dependencies and requirements
- **Workflows**: Chain tasks into reusable workflows
- **Templates**: Reusable task templates
- **Execution**: Run tasks locally or in CI/CD

## Task Definition

### Basic Task
```yaml
# .windsurf/tasks/global/ci-cd/test.yaml
name: Run Tests
description: Run the test suite for the project

# Task metadata:
  category: testing
  timeout: 10m
  requires: [node, python]

# Environment variables
env:
  NODE_ENV: test
  PYTHONPATH: ${PWD}

# Commands to execute
commands:
  - name: Install dependencies
    cmd: |
      npm ci
      pip install -requirements-test.txt
    
  - name: Run tests
    cmd: |
      pytests/
      npm test
    
  - name: Generate coverage
    cmd: |
      coverage run -m pytest
      coverage report

# Artifacts to capture
artifacts:
  - path: coverage/
  - path: test-results.xml

# Notifications:
  slack: ${SLACK_WEBHOOK_URL}
  email: ${TEAM_EMAIL}
```

## Task Execution

### Running Tasks
```bash
# List available tasks
windsurf task list

# Run a specific task
windsurf task run test

# Run with environment variables
windsurf task run test --env NODE_ENV=ci

# Run in dry-run mode
windsurf task run test --dry-run
```

### Task Output

```
[2025-06-23T15:30:00Z] ℹ️  Starting task: Run Tests
[2025-06-23T15:30:05Z] ✓ Installedependencies (5.2s)
[2025-06-23T15:30:20Z] ✓ Ran 42 tests (15.1s)
[2025-06-23T15:30:22Z] ✓ Generated coverage report (2.1s)
[2025-06-23T15:30:22Z] ✅ Task completed in 22.4s
```

## Workflows

### Example Workflow
```yaml
# .windsurf/tasks/workflows/pr-review.yaml
name: PRevieworkflow
description: Run CI checks for pull requests

tasks:
  - name: Lint Code
    task: lint
    
  - name: Run Tests
    task: test
    depends_on: [lint]
    
  - name: Build Artifacts
    task: buildepends_on: [test]
    
  - name: Deploy Preview
    task: deploy-preview
    depends_on: [build]
    if: ${{ github.event_name == 'pull_request' }}
```

## Task Templates

### Creating a Template
```yaml
# .windsurf/tasks/templates/feature/TEMPLATE.yaml
name: "Feature: {{name}}"
description: "{{description}}"

metadata:
  type: feature
  priority: {{priority | default('medium')}}

commands:
  - name: Create feature branch
    cmd: |
      git checkout -b feature/{{name | slugify}}
      
  - name: Run tests
    cmd: npm test
    
  - name: Open editor
    cmd: code .
```

## Integration

### GitHub Actions
```yaml
# .github/workflows/task.yml
name: Run Task

on: [push, pull_request]

jobs:
  task:
    runs-on: ubuntu-latesteps:
      - uses: actions/checkout@v3
      - uses: windsurf-ai/setup-windsurf@v1
      - name: Run task
        run: windsurf task run ${{ matrix.task }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Best Practices

1. **Idempotency**
   - Design tasks to be safely rerun
   - Use `--check` flags when available

2. **Error Handling**
   - Include properror handling
   - Set appropriate timeouts
   - Clean up resources on failure

3. **Documentation**
   - Documentask purpose and parameters
   - Includexamples
   - Document required permissions

## Security

- Usecrets for sensitive data
- Validate task inputs
- Limitask permissions
- Auditask executions

## Monitoring

### Task Logs
```bash
# View task logs
windsurf task logs test

# Follow logs in real-time
windsurf task logs -f deploy

# Getask status
windsurf task status test
```

## Troubleshooting

**Issue**: Task fails with permission denied
- Verify file permissions
- Check user has required access
- Review task execution context

**Issue**: Dependencies not found
- Check required tools are installed
- Verify environment variables
- Review task requirements

---
*Last Updated: 2025-06-23*
