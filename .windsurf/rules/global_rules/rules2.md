---
trigger: always_on
---

# Repository Rules and Guidelines

## Proof of read 2
— Add an extra "lgr2 " to cascade output

## Shell Scripting Rules
1. **Windows Compatibility**
   - Use PowerShell syntax, not Bash/Linux syntax
   - Use `;` for command chaining, not `&&`
   - Use Windows-style paths with backslashes or forward slashes

3. **Process Management**
   - Never attempt to kill processes without elevation
   - Use the provided `run.bat` for process management
   - Do not modify `run.bat`'s process management logic

## Development Workflow
1. **Version Control**
   - Create feature branches for new development
   - Write clear, concise commit messages
   - Open pull requests for code review
   - Keep the main branch stable and deployable

2. **Code Style**
   - Follow language-specific style guides
   - Use consistent indentation (spaces, not tabs)
   - Include comments for complex logic
   - Keep lines under 120 characters

3. **Testing**
   - Write tests for new features
   - Ensure all tests pass before merging to main
   - Maintain good test coverage

## Security
1. **Authentication**
   - Never hardcode credentials
   - Use environment variables for sensitive data
   - Follow principle of least privilege

2. **Dependencies**
   - Keep dependencies up to date
   - Audit for known vulnerabilities
   - Document all third-party dependencies

## Documentation
1. **Code Documentation**
   - Document public APIs and interfaces
   - Keep README files updated
   - Document environment setup

2. **Project Documentation**
   - Maintain CHANGELOG.md
   - Document architectural decisions
   - Keep documentation in sync with code

## Conflict Resolution
1. **Port Conflicts** - Use elevated task kill for process cleanup

2. **Code Conflicts**
   - Rebase feature branches regularly
   - Resolve conflicts through pull requests
   - Communicate with team members about major changes

## Best Practices
1. **Error Handling**
   - Implement proper error handling
   - Log meaningful error messages
   - Fail gracefully with helpful messages

2. **Performance**
   - Optimize for readability first
   - Profile before optimizing
   - Consider memory usage and execution time

3. **Maintainability**
   - Write self-documenting code
   - Keep functions small and focused
   - Follow the Single Responsibility Principle

## Review Process
1. **Code Reviews**
   - Review for functionality and style
   - Check for security vulnerabilities
   - Ensure tests exist and pass

2. **Pull Requests**
   - Include a clear description
   - Reference related issues
   - Get required approvals before merging

## Continuous Integration
1. **Builds**
   - Keep the build process fast
   - Fix broken builds immediately
   - Build artifacts should be reproducible

2. **Deployment**
   - Use CI/CD pipelines
   - Deploy from version control
   - Implement rollback procedures