#!/bin/bash
# Worktree Batch Creator - Create multiple worktrees from a task list

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/workspace"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌳 Worktree Batch Creator${NC}"
echo "================================"
echo ""

# Check if tasks file provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 <tasks-file> [base-branch]${NC}"
    echo ""
    echo "Example tasks file format:"
    echo "---"
    echo "claude-refinement:Claude.md refinement and agent creation"
    echo "marketing-content:Marketing automation content generation"
    echo "script-testing:Script testing framework"
    echo "---"
    echo ""
    echo "Each line: <worktree-name>:<description>"
    exit 1
fi

TASKS_FILE="$1"
BASE_BRANCH="${2:-develop/v4.2.0}"

if [ ! -f "$TASKS_FILE" ]; then
    echo -e "${RED}Error: Tasks file not found: $TASKS_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}Base branch:${NC} $BASE_BRANCH"
echo -e "${GREEN}Tasks file:${NC} $TASKS_FILE"
echo ""

# Count tasks
TASK_COUNT=$(grep -v '^#' "$TASKS_FILE" | grep -v '^$' | wc -l | xargs)
echo -e "${BLUE}Found $TASK_COUNT tasks${NC}"
echo ""

# Confirm
read -p "Create $TASK_COUNT worktrees? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}Creating worktrees...${NC}"
echo ""

TASK_NUM=0
SUCCESS_COUNT=0
FAIL_COUNT=0

# Read tasks and create worktrees
while IFS=':' read -r worktree_name description || [ -n "$worktree_name" ]; do
    # Skip comments and empty lines
    [[ "$worktree_name" =~ ^#.*$ ]] && continue
    [[ -z "$worktree_name" ]] && continue

    TASK_NUM=$((TASK_NUM + 1))
    BRANCH_NAME="task/$(printf "%02d" $TASK_NUM)-$worktree_name"
    WORKTREE_PATH="$PROJECT_ROOT/.trees/$worktree_name"

    echo -e "${BLUE}[$TASK_NUM/$TASK_COUNT]${NC} Creating: ${GREEN}$worktree_name${NC}"
    echo "  Branch: $BRANCH_NAME"
    echo "  Path: $WORKTREE_PATH"

    # Check if worktree already exists
    if [ -d "$WORKTREE_PATH" ]; then
        echo -e "  ${YELLOW}⚠️  Already exists, skipping${NC}"
        echo ""
        continue
    fi

    # Create worktree
    if git -C "$PROJECT_ROOT" worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" "$BASE_BRANCH" 2>/dev/null; then
        echo -e "  ${GREEN}✓ Success${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

        # Create task README
        cat > "$WORKTREE_PATH/TASK.md" << EOF
# Task: $description

**Worktree:** $worktree_name
**Branch:** $BRANCH_NAME
**Base:** $BASE_BRANCH
**Created:** $(date +"%Y-%m-%d %H:%M:%S")

## Scope
$description

## Primary Files
- (Add files as you work)

## Conflict Warnings
- (Note potential conflicts with other tasks)

## Status
- [ ] Planning
- [ ] Development
- [ ] Testing
- [ ] Ready for merge

## Notes
(Add notes here)
EOF
        echo -e "  ${GREEN}✓ Created TASK.md${NC}"
    else
        echo -e "  ${RED}✗ Failed${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo ""
done < "$TASKS_FILE"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Worktree creation complete!${NC}"
echo ""
echo -e "Created: ${GREEN}$SUCCESS_COUNT${NC}"
echo -e "Failed: ${RED}$FAIL_COUNT${NC}"
echo -e "Total: $TASK_COUNT"
echo ""

# Show worktree list
echo -e "${BLUE}Current worktrees:${NC}"
git -C "$PROJECT_ROOT" worktree list | grep -E "task/|develop/" | head -20

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Open terminals for each worktree"
echo "2. Start development"
echo "3. Use ./open-terminals.sh to open all at once"
