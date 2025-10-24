---
title: "Worktree Template"
type: technical_doc
component: general
status: draft
tags: []
---

# Git Worktree Template

## Configuration

```yaml
# Worktree Configuration Template
worktree_base_dir: ".trees"
branch_prefix: "feature/"
naming_convention: "kebab-case"  # kebab-case, snake_case, camelCase

# Default worktree structure
default_directories:
  - "docs"
  - "tests"
  - "src"

# Auto-create PRD for each worktree
auto_create_prd: true
prd_location: "tasks/"
prd_template: "tasks/01_create-prd_template.mdc"
```

## Worktree Creation Pattern

### Standard Feature Worktree
```bash
git worktree add .trees/<feature-name> -b feature/<feature-name>
```

### Naming Conventions

**Feature branches:**
- `feature/task-guiding-documentation`
- `feature/replit-storage-replacement`
- `feature/agent-orchestration`

**Bugfix branches:**
- `bugfix/fix-authentication-issue`
- `bugfix/resolve-database-connection`

**Hotfix branches:**
- `hotfix/critical-security-patch`
- `hotfix/production-bug-fix`

**Experimental branches:**
- `experimental/ai-optimization`
- `experimental/new-architecture`

## Worktree Workflow

### 1. Create Worktree
```bash
./tools/worktree_manager.py create <feature-name> [--type feature|bugfix|hotfix|experimental]
```

### 2. Work in Worktree
```bash
cd .trees/<feature-name>
# Make changes, commit, test
```

### 3. Push Branch
```bash
git push origin <branch-name>
```

### 4. Create Pull Request
```bash
gh pr create --title "Feature: Description" --body "..."
```

### 5. Clean Up After Merge
```bash
./tools/worktree_manager.py remove <feature-name>
```

## Best Practices

### Worktree Isolation
- Each worktree is independent
- Changes in one worktree don't affect others
- Each can have different dependencies installed

### Syncing with Main
```bash
# In worktree directory
git fetch origin
git rebase origin/main
```

### Testing Strategy
- Run tests in each worktree independently
- Use separate virtual environments per worktree
- Maintain separate `.env.local` files if needed

### Cleanup
- Remove worktree after feature is merged
- Delete remote branch after PR merge
- Archive worktree directory if needed for reference

## Common Commands

```bash
# List all worktrees
git worktree list

# Remove a worktree
git worktree remove .trees/<feature-name>

# Prune stale worktree references
git worktree prune

# Move a worktree
git worktree move .trees/<old-name> .trees/<new-name>

# Lock a worktree (prevent removal)
git worktree lock .trees/<feature-name>

# Unlock a worktree
git worktree unlock .trees/<feature-name>
```

## Directory Structure

```
/workspace/
├── .trees/                          # Worktree directory
│   ├── feature-name-1/             # Feature worktree 1
│   │   ├── .git                    # Git metadata (link to main repo)
│   │   └── [full project copy]
│   ├── feature-name-2/             # Feature worktree 2
│   └── feature-name-3/             # Feature worktree 3
├── .git/                           # Main repository
└── [main project files]
```

## Troubleshooting

### Worktree Already Exists
```bash
# Remove old worktree first
git worktree remove .trees/<feature-name> --force
# Then recreate
git worktree add .trees/<feature-name> -b feature/<feature-name>
```

### Branch Already Exists
```bash
# Delete branch first
git branch -D feature/<feature-name>
# Then recreate worktree
git worktree add .trees/<feature-name> -b feature/<feature-name>
```

### Locked Worktree
```bash
# Unlock before removing
git worktree unlock .trees/<feature-name>
git worktree remove .trees/<feature-name>
```

## Integration with Claude Code

Each worktree maintains its own:
- `.claude/` configuration (if needed)
- Project history
- MCP server configurations
- Trust settings

The worktree manager automatically initializes Claude Code settings for new worktrees.
