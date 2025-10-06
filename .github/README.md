# GitHub Configuration

This directory contains GitHub-specific configuration for the Merlin Job Application System.

## Files Overview

### Workflows
- **[code-quality.yml](workflows/code-quality.yml)** - Automated code quality checks
  - Runs on pushes to `main` and `feature/**` branches
  - Checks: Black formatting, Flake8 linting, Vulture dead code detection, isort import sorting
  - Black formatting is required; other checks are informational

### Documentation
- **[COMMIT_TEMPLATE.md](COMMIT_TEMPLATE.md)** - Commit message guidelines and best practices
- **[PULL_REQUEST_TEMPLATE.md](PULL_REQUEST_TEMPLATE.md)** - PR template (minimal for solo development)
- **[SECRETS.md](SECRETS.md)** - Guide for managing API keys and sensitive configuration

## Workflows

### Code Quality Checks
Automatically runs on every push and PR to ensure code quality:

```yaml
# Triggers
- Push to main or feature/** branches
- Pull requests to main

# Checks
✓ Black code formatting (required)
ℹ Flake8 linting (informational)
ℹ Vulture dead code detection (informational)
ℹ isort import sorting (informational)
```

## Branch Strategy

### Main Branch
- Production-ready code
- All features merge here via PR

### Feature Branches
- Use pattern: `feature/description-of-feature`
- Examples:
  - `feature/add-resume-templates`
  - `feature/improve-gemini-analysis`
  - `feature/refactor-database-layer`

### Workflow
```bash
# Create a feature branch
git checkout -b feature/my-new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature description"

# Push to GitHub
git push origin feature/my-new-feature

# Create PR on GitHub (optional for solo project)
# Or merge directly to main
git checkout main
git merge feature/my-new-feature
git push origin main
```

## Secrets Management

All secrets should be managed via environment variables. See [SECRETS.md](SECRETS.md) for:
- Required secrets list
- How to configure locally
- Security best practices
- Where to get API keys

**Never commit:**
- `.env` files
- API keys
- Passwords
- OAuth credentials

## Commit Message Format

Follow conventional commits format (see [COMMIT_TEMPLATE.md](COMMIT_TEMPLATE.md)):

```
<type>: <short description>

<detailed explanation>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code restructuring
- `docs` - Documentation
- `style` - Formatting
- `test` - Tests
- `chore` - Maintenance

## Future Enhancements

When ready to add:
- [ ] Automated testing workflow
- [ ] Deployment workflow (Digital Ocean)
- [ ] Dependabot for dependency updates
- [ ] Branch protection rules
- [ ] Code coverage reporting

## Notes

This is a personal project with a streamlined GitHub setup:
- No issue templates
- No contribution guidelines
- Minimal PR process
- Focus on code quality automation
