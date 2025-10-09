#!/bin/bash
# Add Claude task context to existing worktrees
# This script retrofits existing worktrees with .claude-task-context.md and init.sh

set -e

PROJECT_ROOT="/workspace"
TREES_DIR="$PROJECT_ROOT/.trees"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Adding Claude Context to Existing Worktrees${NC}"
echo "================================"
echo ""

# Get all task worktrees
WORKTREES=($(git -C "$PROJECT_ROOT" worktree list | grep -E "\[task/" | awk '{print $1}' | sort))

if [ ${#WORKTREES[@]} -eq 0 ]; then
    echo -e "${RED}No task worktrees found!${NC}"
    exit 1
fi

echo -e "${GREEN}Found ${#WORKTREES[@]} worktrees${NC}"
echo ""

SUCCESS_COUNT=0
SKIP_COUNT=0

for path in "${WORKTREES[@]}"; do
    name=$(basename "$path")
    echo -e "${BLUE}Processing: ${GREEN}$name${NC}"

    # Check if TASK.md exists
    if [ ! -f "$path/TASK.md" ]; then
        echo -e "  ${YELLOW}⚠  No TASK.md found, skipping${NC}"
        SKIP_COUNT=$((SKIP_COUNT + 1))
        echo ""
        continue
    fi

    # Read task description from TASK.md
    task_title=$(grep "^# Task:" "$path/TASK.md" | head -1 | sed 's/^# Task: //')
    branch=$(grep "^\*\*Branch:\*\*" "$path/TASK.md" | head -1 | sed 's/^\*\*Branch:\*\* //')

    if [ -z "$task_title" ]; then
        task_title="Task for $name"
    fi
    if [ -z "$branch" ]; then
        branch=$(cd "$path" && git branch --show-current)
    fi

    # Extract task number from branch name (e.g., task/01-name -> 01)
    task_num=$(echo "$branch" | grep -oP 'task/\K\d+' || echo "00")

    # Create Claude task context file
    if [ ! -f "$path/.claude-task-context.md" ]; then
        cat > "$path/.claude-task-context.md" << EOF
# Task $task_num: $task_title

**Worktree:** $name
**Branch:** $branch
**Status:** In Progress
**Created:** $(date +"%Y-%m-%d")

## Objective
$task_title

## Scope
Complete the deliverables for this task. See TASK.md for full details.

## Primary Files
- TASK.md (task documentation)
- (Files will be listed here as work progresses)

## Success Criteria
- [ ] Planning phase complete
- [ ] Implementation complete
- [ ] Testing complete
- [ ] Documentation updated
- [ ] Ready for merge

## Important Notes
- This is worktree $task_num of a parallel development workflow
- Branch: $branch based on develop/v4.2.0
- Check TASK.md for conflict warnings with other tasks
- Use /workspace/.trees/worktree-manager/worktree-status.sh to see all worktree statuses

## Workflow Commands
- Check status: cd /workspace/.trees/worktree-manager && ./worktree-status.sh
- Sync with develop: cd /workspace/.trees/worktree-manager && ./sync-all-worktrees.sh
- Monitor resources: cd /workspace/.trees/worktree-manager && ./monitor-resources.sh

Focus on this specific task and its objectives.
EOF
        echo -e "  ${GREEN}✓ Created .claude-task-context.md${NC}"
    else
        echo -e "  ${YELLOW}  .claude-task-context.md already exists${NC}"
    fi

    # Create .claude directory if it doesn't exist
    mkdir -p "$path/.claude"

    # Create Claude startup script
    if [ ! -f "$path/.claude/init.sh" ]; then
        cat > "$path/.claude/init.sh" << 'EOFSCRIPT'
#!/bin/bash
# Claude Code Auto-Startup Script
# Automatically loads task context and launches Claude

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_CONTEXT="$WORKTREE_ROOT/.claude-task-context.md"

# Display task information
if [ -f "$TASK_CONTEXT" ]; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           Claude Code - Task Context Loaded                   ║"
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

# TASK CONTEXT - YOU ARE WORKING IN A WORKTREE

$CONTEXT

IMPORTANT:
- You are in a dedicated worktree for this specific task
- Focus exclusively on this task's objectives
- Refer to .claude-task-context.md and TASK.md for details
- This is part of a parallel development workflow with multiple worktrees
- Do not work on files outside this task's scope
"
else
    echo "Warning: Task context file not found at $TASK_CONTEXT"
    echo "Launching Claude without task context..."
    exec claude
fi
EOFSCRIPT

        chmod +x "$path/.claude/init.sh"
        echo -e "  ${GREEN}✓ Created .claude/init.sh${NC}"
    else
        echo -e "  ${YELLOW}  .claude/init.sh already exists${NC}"
    fi

    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    echo ""
done

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Context addition complete!${NC}"
echo ""
echo -e "Processed: ${GREEN}$SUCCESS_COUNT${NC}"
echo -e "Skipped: ${YELLOW}$SKIP_COUNT${NC}"
echo ""

echo -e "${CYAN}To start Claude with task context in any worktree:${NC}"
echo "  cd /workspace/.trees/<worktree-name>"
echo "  ./.claude/init.sh"
echo ""

echo -e "${CYAN}Or launch all at once with tmux:${NC}"
echo "  /workspace/.trees/launch-all-claude.sh"
