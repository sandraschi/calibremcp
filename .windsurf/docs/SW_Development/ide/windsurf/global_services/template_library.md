# Template Library

## Overview

The Template Library provides a centralized repository of reusable templates for projects, documentation, and configurations. It enables consistency across projects and accelerates development by providing standardized starting points.

## Directory Structure

```
.windsurf/templates/
├── project_templates/     # Project boilerplates
│   ├── python-service/
│   ├── web-app/
│   └── data-pipeline/
├── docs/                  # Documentation templates
│   ├── api/
│   ├── architecture/
│   └── user-guides/
├── configs/               # Configuration templates
│   ├── ci-cd/
│   ├── docker/
│   └── monitoring/
└── code/
    ├── components/
    ├── tests/
    └── api/
```

## Key Features

- **Standardization**: Enforce consistent project structures
- **Reusability**: Share common templates across teams
- **Versioning**: Track template changes
- **Customization**: Extend and override templates

## Template Types

### 1. Projectemplates
Complete project scaffolds with:
- Directory structure
- Build configurations
- CI/CD pipelines
- Documentation

### 2. Documentation Templatestandardizedocumentation:
- API references
- Architecture decision records (ADRs)
- User guides
- README templates

### 3. Configuration Templates
Common configurations:
- Docker setups
- CI/CD pipelines
- Linting and formatting
- Testing frameworks

## Using Templates

### Creating a New Project
```bash
# List available templates
windsurf template list

# Create new project from template
windsurf template create python-service my-new-service \
    --output ./projects \
    --var project_name=my-service \
    --var version=1.0.0
```

### Template Variables
Templates use variables for customization:

```yaml
# .windsurf/templates/project_templates/python-service/template.yaml
name: python-service
description: Python service template
variables:
  - name: project_name
    description: Name of the project
    required: true
  - name: version
    description: Initial version
    default: 0.1.0
```

## Creating Templates

1. **Template Structure**
   ```
   my-template/
   ├── template.yaml    # Template metadata
   ├── {{project_name}}/  # Template files
   │   ├── README.md
   │   └── setup.py
   └── hooks/           # Custom scripts
       ├── pre-generate.py
       └── post-generate.py
   ```

2. **Template Metadata**
   ```yaml
   # template.yaml
   name: my-template
   description: My awesome template
   version: 1.0.0
   
   variables:
     - name: project_name
       description: Project name
       required: true
     - name: author
       description: Project author
       default: ""
   ```

## Best Practices

1. **Keep Templatesimple**
   - Focus on common patterns
   - Avoid over-customization

2. **Documentation**
   - Include a README in each template
   - Document required variables
   - Provide usagexamples

3. **Testing**
   - Testemplate generation
   - Verify file permissions
   - Check variable substitution

## Integration

### CI/CD Integration
```yaml
# .github/workflows/create-project.yaml
name: Create Project

on:
  workflow_dispatch:
    inputs:
      project_name:
        description: 'Project name'
        required: true

jobs:
  create-project:
    runs-on: ubuntu-latesteps:
      - uses: actions/checkout@v3
      - name: Setup Windsurf
        uses: windsurf-ai/setup-windsurf@v1
      - name: Create project
        run: |
          windsurf template create python-service ${{ github.workspace }}/${{ inputs.project_name }} \
            --var project_name=${{ inputs.project_name }} \
            --var version=0.1.0
```

## Versioning

Templates follow semantic versioning:
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes

## Security

- Scan templates for sensitive data
- Usenvironment variables for secrets
- Set appropriate file permissions

## Troubleshooting

**Issue**: Template variables not substituted
- Verify template syntax ({{variable}})
- Check required variables are provided
- Ensure template is properly formatted

**Issue**: Permission denied
- Check file permissions in template
- Verify user has write access to target directory

---
*Last Updated: 2025-06-23*
