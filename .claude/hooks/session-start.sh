#!/bin/bash
##
## Session Start Hook - Worktree Context Injection
##
## This hook runs when Claude Code starts a session.
## It automatically loads worktree context files if running inside a worktree.
##
## Hook Event: SessionStart
## Trigger: When Claude Code session initializes
## Purpose: Auto-inject worktree task context for focused development
##

set -euo pipefail

# Detect if we're in a worktree by checking for .trees/ in path
CURRENT_DIR=$(pwd)
WORKSPACE_ROOT="/workspace"

# Check if current directory is inside a worktree
is_worktree() {
    # Worktrees are in /workspace/.trees/worktree-name/
    if [[ "$CURRENT_DIR" == "$WORKSPACE_ROOT/.trees/"* ]]; then
        return 0
    fi
    return 1
}

# Extract worktree name from path
get_worktree_name() {
    # Remove /workspace/.trees/ prefix and get first directory
    local path_suffix="${CURRENT_DIR#$WORKSPACE_ROOT/.trees/}"
    echo "${path_suffix%%/*}"
}

# Find and read worktree context files
get_worktree_context() {
    local worktree_name=$1
    local worktree_root="$WORKSPACE_ROOT/.trees/$worktree_name"

    local context=""

    # Read .claude-task-context.md (primary context)
    if [[ -f "$worktree_root/.claude-task-context.md" ]]; then
        context+="📋 WORKTREE TASK CONTEXT (from .claude-task-context.md):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"
        context+=$(cat "$worktree_root/.claude-task-context.md")
        context+="

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"
    fi

    # Read PURPOSE.md (additional context)
    if [[ -f "$worktree_root/PURPOSE.md" ]]; then
        context+="

🎯 WORKTREE PURPOSE (from PURPOSE.md):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"
        context+=$(cat "$worktree_root/PURPOSE.md")
        context+="

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"
    fi

    # Add worktree-specific guidance with agent instructions
    if [[ -n "$context" ]]; then
        context+="

🔧 WORKTREE WORKFLOW COMMANDS:
- /tree close           - Complete this feature and mark ready to merge
- /tree close incomplete - Save progress for next development cycle
- /tree status          - Show worktree environment status
- /tree restore         - Restore terminal sessions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 AGENT INSTRUCTIONS:

You have been provided the worktree task context above. Before beginning implementation:

1. READ and ANALYZE the task description, scope, and success criteria carefully
2. IDENTIFY any ambiguous requirements, missing details, or unclear expectations
3. ASK the user 0-4 specific, targeted questions about:
   - Technical decisions that aren't specified in the context
   - Ambiguous requirements that need clarification
   - Edge cases or error handling expectations
   - Integration points with existing code
   - Any constraints or preferences for implementation approach

DO NOT ask generic questions like 'Do you understand?' or 'What would you like to start with?'
Instead, ask SPECIFIC questions based on gaps or ambiguities you identified in the context.

After the user answers your questions, proceed with implementation.

"
    fi

    echo "$context"
}

# Main hook logic
main() {
    if ! is_worktree; then
        # Not in a worktree - no context to inject
        echo '{}'
        exit 0
    fi

    WORKTREE_NAME=$(get_worktree_name)
    CONTEXT=$(get_worktree_context "$WORKTREE_NAME")

    if [[ -z "$CONTEXT" ]]; then
        # No context files found
        echo '{}'
        exit 0
    fi

    # Output JSON with context message
    # Use Python for reliable JSON encoding
    echo "$CONTEXT" | python3 -c "
import json
import sys
message = sys.stdin.read()
print(json.dumps({'hookSpecificOutput': {'message': message}}))
" 2>/dev/null || echo '{}'
}

main