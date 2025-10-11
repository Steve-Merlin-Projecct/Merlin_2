#!/bin/bash
# Auto-generated Claude initialization script

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_CONTEXT="$WORKTREE_ROOT/.claude-task-context.md"

# Display banner
echo "════════════════════════════════════════════════════════"
echo "🌳 Worktree: docx-security-verification-system-prevent-maliciou"
echo "📋 Task: docx security verification system prevent maliciou"
echo "════════════════════════════════════════════════════════"
echo ""
echo "✅ Slash commands available after Claude loads:"
echo "   /tree close   - Complete this worktree"
echo "   /tree status  - Show status"
echo "   /tree restore - Restore terminals"
echo ""
echo "📝 Task context loaded in .claude-task-context.md"
echo ""

# Check if Claude is available
if ! command -v claude &> /dev/null; then
    echo "⚠️  Warning: Claude Code not found in PATH"
    echo "Install Claude Code or add to PATH"
    echo "Terminal will open without Claude"
    exec bash
    exit 0
fi

# Launch Claude with task context
if [ -f "$TASK_CONTEXT" ]; then
    TASK_DESC=$(cat "$TASK_CONTEXT")
    
    claude --append-system-prompt "You are working in a git worktree dedicated to this task:

$TASK_DESC

IMPORTANT: After you receive this context, immediately read the .claude-task-context.md file to understand the full task details, then ask 1-3 clarifying questions to ensure you understand the scope and requirements before beginning implementation. Focus on:
1. Ambiguous requirements that need clarification
2. Technical decisions that aren't specified
3. Edge cases or error handling expectations
4. Integration points with existing code

Wait for user responses before starting implementation."
else
    echo "⚠️  Warning: Task context file not found"
    claude
fi
