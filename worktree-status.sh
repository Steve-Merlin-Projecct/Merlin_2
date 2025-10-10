#!/bin/bash
# Show status of all worktrees

set -e

PROJECT_ROOT="/workspace"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}📊 Worktree Status Dashboard${NC}"
echo "================================"
echo ""

# Get all worktrees
WORKTREES=($(git -C "$PROJECT_ROOT" worktree list | grep -E "task/|develop/" | awk '{print $1}' | sort))

if [ ${#WORKTREES[@]} -eq 0 ]; then
    echo -e "${RED}No worktrees found!${NC}"
    exit 1
fi

echo -e "${GREEN}Total worktrees: ${#WORKTREES[@]}${NC}"
echo ""

# Table header
printf "${CYAN}%-35s %-30s %-15s %-10s${NC}\n" "WORKTREE" "BRANCH" "STATUS" "COMMITS"
printf "${CYAN}%-35s %-30s %-15s %-10s${NC}\n" "--------" "------" "------" "-------"

for path in "${WORKTREES[@]}"; do
    if [ ! -d "$path" ]; then
        continue
    fi

    cd "$path" 2>/dev/null || continue

    # Get info
    name=$(basename "$path")
    branch=$(git branch --show-current 2>/dev/null || echo "DETACHED")

    # Git status
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        status="${YELLOW}MODIFIED${NC}"
    else
        status="${GREEN}CLEAN${NC}"
    fi

    # Commits ahead/behind
    ahead=$(git rev-list --count origin/develop/v4.2.0..HEAD 2>/dev/null || echo "?")
    behind=$(git rev-list --count HEAD..origin/develop/v4.2.0 2>/dev/null || echo "?")

    if [ "$ahead" = "0" ] && [ "$behind" = "0" ]; then
        commits="${GREEN}synced${NC}"
    elif [ "$ahead" != "0" ] && [ "$behind" = "0" ]; then
        commits="${CYAN}↑$ahead${NC}"
    elif [ "$ahead" = "0" ] && [ "$behind" != "0" ]; then
        commits="${YELLOW}↓$behind${NC}"
    else
        commits="${YELLOW}↑$ahead↓$behind${NC}"
    fi

    printf "%-35s %-30s %-15b %-10b\n" "$name" "$branch" "$status" "$commits"
done

echo ""
echo -e "${BLUE}Legend:${NC}"
echo -e "  ${GREEN}CLEAN${NC} = No uncommitted changes"
echo -e "  ${YELLOW}MODIFIED${NC} = Uncommitted changes present"
echo -e "  ${CYAN}↑N${NC} = N commits ahead of develop"
echo -e "  ${YELLOW}↓N${NC} = N commits behind develop"
echo -e "  ${GREEN}synced${NC} = Up to date with develop"

echo ""
echo -e "${YELLOW}Quick actions:${NC}"
echo "  ./sync-all-worktrees.sh    # Pull latest from develop in all worktrees"
echo "  ./merge-worktree.sh <name> # Merge a worktree to develop"
