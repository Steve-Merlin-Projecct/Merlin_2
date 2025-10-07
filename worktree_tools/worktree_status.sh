#!/bin/bash

# Worktree Status Checker
# Provides comprehensive status of all worktrees and their branches

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MAIN_BRANCH="main"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Worktree Status Dashboard          ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}\n"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Current branch info
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${CYAN}📍 Current Location:${NC} ${GREEN}$CURRENT_BRANCH${NC}\n"

# Worktree list
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🌳 Active Worktrees:${NC}\n"
git worktree list | while read line; do
    echo "   $line"
done

# Branch merge status
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}✓ Merged Branches:${NC}\n"
MERGED=$(git branch --merged "$MAIN_BRANCH" | sed 's/^[* ]*//' | grep -v "^$MAIN_BRANCH$" || true)
if [ -z "$MERGED" ]; then
    echo -e "   ${YELLOW}(none)${NC}"
else
    echo "$MERGED" | while read branch; do
        echo -e "   ${GREEN}✓${NC} $branch"
    done
fi

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}⏳ Unmerged Branches:${NC}\n"
UNMERGED=$(git branch --no-merged "$MAIN_BRANCH" | sed 's/^[* ]*//' || true)
if [ -z "$UNMERGED" ]; then
    echo -e "   ${GREEN}(none - all branches merged!)${NC}"
else
    echo "$UNMERGED" | while read branch; do
        # Get commit count ahead of main
        AHEAD=$(git rev-list --count "$MAIN_BRANCH".."$branch" 2>/dev/null || echo "?")
        echo -e "   ${YELLOW}→${NC} $branch ${CYAN}(+$AHEAD commits)${NC}"
    done
fi

# Upstream tracking status
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🔗 Remote Tracking:${NC}\n"

if git rev-parse --abbrev-ref "$MAIN_BRANCH@{upstream}" >/dev/null 2>&1; then
    UPSTREAM=$(git rev-parse --abbrev-ref "$MAIN_BRANCH@{upstream}")
    echo -e "   ${GREEN}✓${NC} $MAIN_BRANCH → $UPSTREAM"

    # Check if main is behind/ahead of remote
    git fetch origin "$MAIN_BRANCH" 2>/dev/null || true
    BEHIND=$(git rev-list --count HEAD..origin/"$MAIN_BRANCH" 2>/dev/null || echo "0")
    AHEAD=$(git rev-list --count origin/"$MAIN_BRANCH"..HEAD 2>/dev/null || echo "0")

    if [ "$BEHIND" -gt 0 ]; then
        echo -e "   ${YELLOW}⚠${NC}  Behind remote by $BEHIND commit(s)"
    fi
    if [ "$AHEAD" -gt 0 ]; then
        echo -e "   ${YELLOW}⚠${NC}  Ahead of remote by $AHEAD commit(s)"
    fi
    if [ "$BEHIND" -eq 0 ] && [ "$AHEAD" -eq 0 ]; then
        echo -e "   ${GREEN}✓${NC} Up to date with remote"
    fi
else
    echo -e "   ${RED}✗${NC} No upstream configured for $MAIN_BRANCH"
fi

# Uncommitted changes check
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📝 Working Directory Status:${NC}\n"

if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "   ${GREEN}✓${NC} Clean (no uncommitted changes)"
else
    echo -e "   ${YELLOW}⚠${NC}  Uncommitted changes present"

    # Show summary of changes
    MODIFIED=$(git diff --name-only | wc -l)
    STAGED=$(git diff --cached --name-only | wc -l)
    UNTRACKED=$(git ls-files --others --exclude-standard | wc -l)

    [ "$MODIFIED" -gt 0 ] && echo -e "      • Modified: $MODIFIED file(s)"
    [ "$STAGED" -gt 0 ] && echo -e "      • Staged: $STAGED file(s)"
    [ "$UNTRACKED" -gt 0 ] && echo -e "      • Untracked: $UNTRACKED file(s)"
fi

# Summary and recommendations
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}💡 Recommendations:${NC}\n"

UNMERGED_COUNT=$(git branch --no-merged "$MAIN_BRANCH" | wc -l)
if [ "$UNMERGED_COUNT" -gt 0 ]; then
    echo -e "   ${YELLOW}→${NC} Run ${GREEN}./worktree_tools/merge_worktrees.sh${NC} to merge unmerged branches"
fi

if ! git rev-parse --abbrev-ref "$MAIN_BRANCH@{upstream}" >/dev/null 2>&1; then
    echo -e "   ${YELLOW}→${NC} Configure upstream: ${GREEN}git push --set-upstream origin $MAIN_BRANCH${NC}"
fi

if [ "$UNMERGED_COUNT" -eq 0 ] && git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "   ${GREEN}✓${NC} All clear! Everything is merged and up to date."
fi

echo -e "\n${BLUE}╚════════════════════════════════════════╝${NC}\n"
