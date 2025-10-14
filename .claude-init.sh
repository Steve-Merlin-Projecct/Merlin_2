#!/bin/bash
# Auto-generated Claude initialization script
# This script launches Claude with task context pre-loaded

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_CONTEXT="$WORKTREE_ROOT/.claude-task-context.md"

# Display banner
echo "════════════════════════════════════════════════════════"
echo "🌳 Workspace: Main Development Branch"
echo "📋 Branch: develop/v4.3.2-worktrees-20251012-044136"
echo "════════════════════════════════════════════════════════"
echo ""
echo "✅ Slash commands available:"
echo "   /tree build   - Create worktrees from staged features"
echo "   /tree close   - Complete feature in worktree"
echo "   /tree closedone - Batch merge completed worktrees"
echo "   /tree status  - Show worktree environment status"
echo ""
echo "📝 Task context loaded in .claude-task-context.md"
echo ""
