# Calibre MCP Pull Request

<!-- Fleet discipline: linked issue first, one concern per PR, small diffs.
     The maintainer merges — don't merge your own PR. -->

## Description

[Provide a brief description of the changes in this pull request]

## Related Issues

- Closes # [issue number]
- Related to # [issue number]

## Type of Change

Please check the type of change your PR introduces:
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Dependencies update

## Checklist

- [ ] I have read the [Contributing Guidelines](CONTRIBUTING.md)
- [ ] Linked issue exists (no drive-by features)
- [ ] My code follows the project's coding standards
- [ ] Diff is small and focused (one concern per PR)
- [ ] No stubs presented as implementations
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] `ruff check` passes; webapp touched? `biome ci` and `tsc -b` pass
- [ ] I have added/updated necessary documentation
- [ ] CHANGELOG_LATEST.md updated
- [ ] All tests pass (`uv run pytest tests/ -v`)

## Testing

[Describe how you tested your changes. Include any relevant test files or commands]

```bash
# Example test command
pytest tests/ -v
```

## Additional Information

[Add any additional information that might be helpful for the reviewers]
