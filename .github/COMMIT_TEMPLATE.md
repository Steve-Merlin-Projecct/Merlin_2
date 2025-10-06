# Commit Message Guidelines

## Format
```
<type>: <short summary>

<detailed description of what changed and why>

<footer with references if needed>
```

## Types
- **feat**: New feature
- **fix**: Bug fix
- **refactor**: Code restructuring without changing behavior
- **docs**: Documentation changes
- **style**: Code formatting, no logic changes
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates

## Example
```
feat: Add variable substitution system for job applications

- Implement dynamic variable resolution from database
- Add support for hiring organization lookup
- Create URL tracking for application links
- Update job application table schema

Closes #123
```

## Best Practices
- Keep the summary under 72 characters
- Use imperative mood ("Add feature" not "Added feature")
- Explain the "why" not just the "what"
- Reference related issues or PRs
