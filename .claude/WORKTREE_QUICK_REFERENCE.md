---
title: "Worktree Quick Reference"
type: reference
component: general
status: draft
tags: []
---

# Git Worktree Quick Reference

## Worktree Manager CLI

### Create a new worktree
```bash
python tools/worktree_manager.py create <name> [--type feature|bugfix|hotfix|experimental]

# Examples:
python tools/worktree_manager.py create user-authentication
python tools/worktree_manager.py create critical-bug --type bugfix
python tools/worktree_manager.py create new-api --type experimental
```

### List all worktrees
```bash
python tools/worktree_manager.py list
```

### Show worktree status
```bash
python tools/worktree_manager.py status
```

### Sync worktree with main
```bash
python tools/worktree_manager.py sync <name>

# Example:
python tools/worktree_manager.py sync user-authentication
```

### Remove a worktree
```bash
python tools/worktree_manager.py remove <name> [--force]

# Examples:
python tools/worktree_manager.py remove user-authentication
python tools/worktree_manager.py remove old-feature --force
```

### Clean up stale references
```bash
python tools/worktree_manager.py cleanup
```

## Native Git Commands

### List worktrees
```bash
git worktree list
```

### Remove worktree manually
```bash
git worktree remove .trees/<name>
git worktree remove .trees/<name> --force  # Force remove
```

### Lock/Unlock worktree
```bash
git worktree lock .trees/<name>
git worktree unlock .trees/<name>
```

### Prune stale worktrees
```bash
git worktree prune
```

## Workflow Examples

### Starting a new feature
```bash
# 1. Create worktree
python tools/worktree_manager.py create my-feature

# 2. Navigate to worktree
cd .trees/my-feature

# 3. Work on your feature
# ... make changes, commit ...

# 4. Push branch
git push origin feature/my-feature

# 5. Create PR
gh pr create --title "Feature: My Feature" --body "Description"
```

### Working on multiple features simultaneously
```bash
# Terminal 1: Work on feature A
cd .trees/feature-a
npm run dev

# Terminal 2: Work on feature B
cd .trees/feature-b
npm test

# Terminal 3: Work on feature C
cd .trees/feature-c
python main.py
```

### Syncing with latest main
```bash
# Option 1: Use manager
python tools/worktree_manager.py sync my-feature

# Option 2: Manual
cd .trees/my-feature
git fetch origin
git rebase origin/main
```

### Cleaning up after merge
```bash
# 1. Remove worktree
python tools/worktree_manager.py remove my-feature

# 2. Delete local branch (if needed)
git branch -D feature/my-feature

# 3. Delete remote branch (if not auto-deleted)
git push origin --delete feature/my-feature
```

## Current Active Worktrees

| Worktree | Branch | Type | Purpose |
|----------|--------|------|---------|
| task-guiding-docs | feature/task-guiding-documentation | feature | Task guiding documentation system |
| replit-storage-replacement | feature/replit-storage-replacement | feature | Replace Replit storage with alternatives |
| agent-orchestration | feature/agent-orchestration | feature | Agent orchestration system |

## Configuration

Configuration file: `.claude/worktree-config.json`

```json
{
  "worktree_base_dir": ".trees",
  "branch_prefix": {
    "feature": "feature/",
    "bugfix": "bugfix/",
    "hotfix": "hotfix/",
    "experimental": "experimental/"
  },
  "naming_convention": "kebab-case",
  "auto_create_prd": true,
  "prd_location": "tasks/"
}
```

## Tips & Tricks

### Virtual Environments per Worktree
```bash
cd .trees/my-feature
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Separate .env files
```bash
# Main workspace
cp .env .trees/my-feature/.env.local
# Edit .env.local with feature-specific values
```

### Run different versions
```bash
# Terminal 1: Old stable version
cd /workspace
npm run start

# Terminal 2: New experimental version
cd .trees/experimental-feature
npm run start -- --port 3001
```

### Disk Space Management
```bash
# Check worktree disk usage
du -sh .trees/*

# Remove node_modules from inactive worktrees
find .trees -name "node_modules" -type d -prune -exec rm -rf {} +
```

## Troubleshooting

### Error: "worktree already exists"
```bash
git worktree remove .trees/<name> --force
python tools/worktree_manager.py create <name>
```

### Error: "branch already exists"
```bash
git branch -D feature/<name>
python tools/worktree_manager.py create <name>
```

### Uncommitted changes blocking removal
```bash
# Save changes
cd .trees/<name>
git stash

# Or force remove
python tools/worktree_manager.py remove <name> --force
```

### Locked worktree
```bash
git worktree unlock .trees/<name>
python tools/worktree_manager.py remove <name>
```

## Best Practices

1. **One feature per worktree** - Keep worktrees focused
2. **Regular syncing** - Sync with main frequently to avoid conflicts
3. **Clean up promptly** - Remove worktrees after feature merge
4. **Consistent naming** - Use kebab-case for worktree names
5. **Document in PRD** - Auto-generated PRD helps track feature scope
6. **Test isolation** - Each worktree can have independent test runs
7. **Branch hygiene** - Delete branches after PR merge

## Resources

- Template: `.claude/worktree-template.md`
- Manager: `tools/worktree_manager.py`
- Config: `.claude/worktree-config.json`
- Git Docs: https://git-scm.com/docs/git-worktree
