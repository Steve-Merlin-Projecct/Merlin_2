#!/bin/bash
# Claude Code Auto-Startup Script
# Automatically loads task context and launches Claude

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_CONTEXT="$WORKTREE_ROOT/.claude-purpose-context.md"

# Display task information
if [ -f "$TASK_CONTEXT" ]; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           Claude Code - Purpose Context Loaded                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    head -15 "$TASK_CONTEXT"
    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo "Starting Claude Code with task context..."
    echo "────────────────────────────────────────────────────────────────"
    echo ""
fi

# Change to worktree root
cd "$WORKTREE_ROOT"

# Launch Claude with task context
if [ -f "$TASK_CONTEXT" ]; then
    CONTEXT=$(cat "$TASK_CONTEXT")
    exec claude --append-system-prompt "

# PURPOSE CONTEXT - YOU ARE WORKING IN A WORKTREE

$CONTEXT

IMPORTANT:
- You are in a dedicated worktree for this specific purpose
- Focus exclusively on this purpose's objectives
- Refer to .claude-purpose-context.md and PURPOSE.md for details
- This is part of a parallel development workflow with multiple worktrees
- Do not work on files outside this purpose's scope
"
else
    echo "Warning: Purpose context file not found at $TASK_CONTEXT"
    echo "Launching Claude without task context..."
    exec claude
fi
