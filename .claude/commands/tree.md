---
description: Manage git worktrees with intelligent automation and full-cycle development workflows
---

Execute the tree worktree management command.

Run: `bash /workspace/.claude/scripts/tree.sh "$@"`

This command provides comprehensive worktree management with full development cycle automation:

## Basic Commands
- `/tree stage [description]` - Stage feature for worktree creation
- `/tree list` - Show staged features
- `/tree clear` - Clear all staged features
- `/tree conflict` - Analyze conflicts and suggest merges
- `/tree build` - Create worktrees from staged features (auto-launches Claude)
- `/tree restore` - Restore terminals for existing worktrees
- `/tree status` - Show worktree environment status
- `/tree refresh` - Check slash command availability and get session reload guidance
- `/tree help` - Show detailed help

## Completion Commands
- `/tree close` - Complete feature and mark ready to merge
- `/tree close incomplete` - Save progress for continuation in next cycle (NEW)
- `/tree closedone` - Batch merge and cleanup completed worktrees
- `/tree closedone --full-cycle` - Complete entire development cycle automation (NEW)

## Full-Cycle Automation

The `--full-cycle` flag automates the complete development lifecycle:

```bash
/tree closedone --full-cycle [--bump patch|minor|major] [--dry-run] [--yes]
```

**What it does:**
1. Validates all worktrees are closed
2. Merges completed features to development branch
3. Promotes development branch to main
4. Bumps version (patch by default)
5. Creates new development branch
6. Auto-stages incomplete features for next cycle
7. Archives synopses and generates report

**Options:**
- `--bump [type]` - Version bump type: patch (default), minor, or major
- `--dry-run` - Preview actions without executing
- `--yes` - Skip confirmation prompts

**Example workflow:**
```bash
# Stage features
/tree stage Add user authentication system
/tree stage Implement dashboard analytics
/tree build

# Work in worktrees...
# In worktree A: /tree close              # Feature complete
# In worktree B: /tree close incomplete   # Need more work

# Back in main workspace:
/tree closedone --full-cycle --bump minor

# Result:
# - Completed feature merged to main
# - Version bumped from 4.3.2 → 4.4.0
# - New dev branch: develop/v4.4.0-worktrees-20251012-120000
# - Incomplete feature auto-staged for next cycle
```

## Incomplete Features

Use `/tree close incomplete` to mark features that need to continue in the next development cycle:

```bash
# In worktree
cd /workspace/.trees/my-feature
/tree close incomplete

# This feature will automatically be staged when running:
/tree closedone --full-cycle
```

**Note:** If `/tree` commands show "Unknown slash command" in worktrees:
- Run: `bash /workspace/.claude/scripts/tree.sh refresh` for diagnostics
- Workaround: Use direct script calls (e.g., `bash /workspace/.claude/scripts/tree.sh status`)
- Permanent fix: Restart Claude Code CLI session from the worktree directory

For full documentation, see: tasks/tree-workflow-full-cycle/prd.md
