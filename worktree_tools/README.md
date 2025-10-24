---
title: "Readme"
type: technical_doc
component: general
status: draft
tags: []
---

# Worktree Management Tools

Streamlined tools for managing git worktrees and merging feature branches.

## Tools Overview

### 1. `worktree_status.sh` - Status Dashboard
Provides a comprehensive visual dashboard of all worktrees and branch status.

**Features:**
- Lists all active worktrees and their locations
- Shows merged vs unmerged branches
- Displays commit counts for unmerged branches
- Checks upstream tracking configuration
- Reports uncommitted changes
- Provides actionable recommendations

**Usage:**
```bash
./worktree_tools/worktree_status.sh
```

**Output includes:**
- Current branch location
- Active worktrees list
- Merged branches (✓)
- Unmerged branches with commit counts
- Remote tracking status
- Working directory status (uncommitted changes)
- Smart recommendations for next steps

---

### 2. `merge_worktrees.sh` - Automated Merge Tool
Safely merges all unmerged worktree branches into main with conflict detection.

**Features:**
- Automatically switches to main branch
- Pulls latest remote changes
- Identifies unmerged branches
- Merges branches one by one
- Handles upstream configuration automatically
- Detects and reports merge conflicts
- Aborts problematic merges for manual resolution
- Pushes successfully merged changes to remote

**Usage:**
```bash
./worktree_tools/merge_worktrees.sh
```

**Process flow:**
1. Switches to main branch (if not already there)
2. Pulls latest changes from remote
3. Lists all worktree branches
4. Shows merge status (merged vs unmerged)
5. Prompts for confirmation
6. Merges each unmerged branch sequentially
7. Handles upstream tracking if not configured
8. Pushes merged changes to remote
9. Reports summary with any conflicts

**Safety features:**
- Aborts conflicting merges automatically
- Preserves your work during conflicts
- Reports which branches need manual resolution
- Sets upstream tracking if missing

---

## Common Workflows

### Check Status Before Merging
```bash
./worktree_tools/worktree_status.sh
```
Review the dashboard to see what needs merging.

### Merge All Unmerged Branches
```bash
./worktree_tools/merge_worktrees.sh
```
Follow the prompts to merge all branches automatically.

### Handle Merge Conflicts
If `merge_worktrees.sh` reports conflicts:
1. The script will abort the problematic merge
2. Manually resolve the conflict:
   ```bash
   git merge <branch-name>
   # Resolve conflicts in your editor
   git add .
   git commit
   ```
3. Run `merge_worktrees.sh` again for remaining branches

---

## Troubleshooting

### "No upstream configured" error
The merge tool automatically handles this by running:
```bash
git push --set-upstream origin main
```

### Merge conflicts
- Script aborts the merge automatically
- Resolve conflicts manually
- Re-run the script for remaining branches

### Permission denied
Make scripts executable:
```bash
chmod +x worktree_tools/*.sh
```

---

## Setup Instructions

1. Make scripts executable:
```bash
chmod +x worktree_tools/worktree_status.sh
chmod +x worktree_tools/merge_worktrees.sh
```

2. Run status check:
```bash
./worktree_tools/worktree_status.sh
```

3. Merge when ready:
```bash
./worktree_tools/merge_worktrees.sh
```

---

## Design Decisions

**Why separate tools?**
- `worktree_status.sh`: Read-only inspection, safe to run anytime
- `merge_worktrees.sh`: Performs writes, requires confirmation

**Why sequential merging?**
- Prevents compound conflicts
- Easier to identify which branch caused issues
- Clearer error reporting

**Why automatic upstream handling?**
- Eliminates common "no upstream branch" errors
- Configures tracking automatically on first push
- Works seamlessly with new repositories

---

## Integration with Development Workflow

### Recommended Usage Pattern
1. **Start of day**: Check status
   ```bash
   ./worktree_tools/worktree_status.sh
   ```

2. **Before merging**: Review what's ready
   ```bash
   ./worktree_tools/worktree_status.sh
   ```

3. **Merge completed work**: Automated merge
   ```bash
   ./worktree_tools/merge_worktrees.sh
   ```

4. **After merging**: Verify clean state
   ```bash
   ./worktree_tools/worktree_status.sh
   ```

---

## Future Enhancements

Potential additions:
- Interactive branch selection for merge
- Automatic conflict resolution strategies
- Integration with CI/CD pipelines
- Branch cleanup after successful merge
- Multi-remote support
- Worktree creation wizard
