# Documentation Standards

## Overview

This document defines the standards and guidelines for creating and maintaining documentation within the Windsurf ecosystem. Following these standards ensures consistency, clarity, and maintainability across all documentation.

## File Naming Conventions

### General Rules
- Use lowercase withyphens for file names: `file-name-format.md`
- Keep file names concise but descriptive
- Use consistent prefixes forelated files:
  - `guide-*.md` for tutorials and how-tos
  - `ref-*.md` foreference material
  - `concept-*.md` for conceptual explanations
  - `tutorial-*.md` for step-by-step guides

### Examples
```
# Good
getting-started.md
api-reference.mdeployment-guide.md

# Avoid
Getting Started.md
API_Reference.mdeploymentGuide.md
```

## Directory Structure

### Standardirectories
```
docs/
â”œâ”€â”€ guides/           # Tutorials and how-to guides
â”œâ”€â”€ reference/        # API and technical references
â”œâ”€â”€ concepts/         # Conceptual explanations
â”œâ”€â”€ examples/         # Codexamples
â””â”€â”€ resources/        # Images and other assets
```

### Documentation Types

| Type         | Location           | Purpose                                   |
|--------------|-------------------|-------------------------------------------|
| Guides       | `docs/guides/`    | Step-by-step instructions                 |
| References   | `docs/reference/` | API docs, configuration references        |
| Concepts     | `docs/concepts/`  | Architectural decisions, explanations     |
| Examples     | `docs/examples/`  | Code samples and usagexamples           |
| Resources    | `docs/resources/` | Images, diagrams, and other assets       |

## Markdown Standards

### Headers
```markdown
# Documentitle (H1)

## Section (H2)


### Subsection (H3)
```

### Code Blocks
Use fenced code blocks with language specification:

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### Links
- Use descriptive link text
- Preferelative links for internal documentation
- Use reference-style links for bettereadability

```markdown
[Getting Started Guide](/ide/windsurf/global_services/getting-started.md)
[API Reference][api-ref]

[api-ref]: api/reference.md
```

### Tables

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Data 1   | Data 2   |
| Data 3   | Data 4   |
```

### Admonitions

```markdown
!!! note
    This a note

!!! warning "Important"
    This an important warning
```

## Versioning

### Documentation Versioning
- Usemantic versioning (MAJOR.MINOR.PATCH)
- Create versionedirectories for majoreleases
- Maintain a `latest` symlink to the current version

```
docs/
  v1.0.0/
  v2.0.0/
  latest/ -> v2.0.0
```

### Front Matter
Include metadatathe top of each document:

```yaml
---
title: Documentitle
description: Brief description of the document
date: 2025-06-23
version: 1.0.0
author: Author Name
---
```

## Writing Style

### Voice and Tone
- Use active voice
- Be concise buthorough
- Write for a technical audience
- Usecond person for instructions
- Use presentense

### Terminology
- Use consistenterminology
- Define acronyms on first use
- Avoid jargon when possible
- Use industry-standard terms

### Formatting Conventions
- Usentence case for headings
- Use title case for proper nouns and product names
- Use backticks for file names, commands, and code
- Use **bold** for UI elements and importanterms
- Use *italics* for emphasis

## Review Process

### Peereview
- All documentation changes requireview
- Use pull requests for documentation updates
- Assign technical reviewers as needed

### Updating Documentation
- Update documentation with code changes
- Add "Last Updated" date to modified files
- Document deprecations and breaking changes

## Tools and Automation

### Linting
```bash
# Check markdown files
windsurf docs lint

# Fix common issues
windsurf docs fix
```

### Validation
```bash
# Check links
windsurf docs check-links

# Validate structure
windsurf docs validate
```

## Local Development

### Previewing Changes
```bash
# Install dependencies
pip install mkdocs-material

# Serve docs locally
mkdocserve
```

### Building Documentation
```bash
# Build static site
mkdocs build

# Deploy to staging
mkdocs gh-deploy --staging
```

## Best Practices

1. **Keep It Current**
   - Update documentation with code changes
   - Remove outdated information
   - Addeprecationotices

2. **Be Consistent**
   - Follow the style guide
   - Use consistenterminology
   - Maintain a consistent structure

3. **Make It Accessible**
   - Usemantic HTML
   - Add altexto images
   - Ensure good color contrast
   - Use descriptive link text

4. **Organize Content Logically**
   - Group related information
   - Use clear section headers
   - Include a table of contents for long documents

## Templates

### Guide Template
```markdown
---
title: Guide Title
description: Brief description of the guide
date: YYYY-MM-DD
author: Author Name
---

# Guide Title

## Overview

Brief introduction to the guide.

## Prerequisites

- Prerequisite 1
- Prerequisite 2

## Steps

### Step 1: Description

Detailed instructions...

```bash
command --example
```

### Step 2: Next Steps

Additional information...

## Troubleshooting

Common issues and solutions.

## See Also

- [Relatedocument 1](link)
- [Relatedocument 2](link)

---
*Last Updated: YYYY-MM-DD*
```

## Review Checklist

- [ ] Documentation follows the style guide
- [ ] Allinks are valid
- [ ] Codexamples work as described
- [ ] Screenshots are up to date
- [ ] Versionumbers are correct
- [ ] No sensitive information is exposed

---
*Last Updated: 2025-06-23*

