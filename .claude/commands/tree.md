---
description: Manage git worktrees with intelligent automation
---

Execute the tree worktree management command.

Run: `bash /workspace/.trees/worktree-manager/.claude/scripts/tree.sh "$@"`

This command provides comprehensive worktree management:
- `/tree stage [description]` - Stage feature for worktree creation
- `/tree list` - Show staged features
- `/tree conflict` - Analyze conflicts and suggest merges
- `/tree build` - Create worktrees from staged features
- `/tree close` - Complete work and generate synopsis
- `/tree closedone` - Batch merge and cleanup completed worktrees
- `/tree status` - Show worktree environment status
- `/tree help` - Show detailed help

For full documentation, see: tasks/prd-tree-slash-command.md
