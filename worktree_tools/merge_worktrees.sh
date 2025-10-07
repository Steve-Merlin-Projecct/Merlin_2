#!/bin/bash

# Worktree Merge Automation Tool
# Safely merges all worktree branches into main with conflict detection and upstream handling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAIN_BRANCH="main"
WORKTREE_DIR=".trees"

echo -e "${BLUE}=== Worktree Merge Tool ===${NC}\n"

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Ensure we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$MAIN_BRANCH" ]; then
    print_warning "Not on $MAIN_BRANCH branch. Switching..."
    git checkout "$MAIN_BRANCH"
fi

# Pull latest changes from remote
print_status "Pulling latest changes from remote..."
if git pull origin "$MAIN_BRANCH" 2>/dev/null; then
    print_success "Remote changes pulled successfully"
else
    print_warning "Could not pull from remote (may not have upstream configured)"
fi

# Get list of all worktree branches (exclude main and remote branches)
WORKTREE_BRANCHES=$(git worktree list | grep -v "($MAIN_BRANCH)" | awk '{print $NF}' | tr -d '[]' || true)

if [ -z "$WORKTREE_BRANCHES" ]; then
    print_warning "No worktree branches found to merge"
    exit 0
fi

echo -e "\n${BLUE}Found worktree branches:${NC}"
echo "$WORKTREE_BRANCHES" | while read branch; do
    echo "  - $branch"
done

# Check which branches are already merged
echo -e "\n${BLUE}Checking merge status...${NC}"
MERGED_BRANCHES=$(git branch --merged "$MAIN_BRANCH" | sed 's/^[* ]*//' | grep -v "^$MAIN_BRANCH$" || true)
UNMERGED_BRANCHES=$(git branch --no-merged "$MAIN_BRANCH" | sed 's/^[* ]*//' || true)

if [ -n "$MERGED_BRANCHES" ]; then
    echo -e "\n${GREEN}Already merged:${NC}"
    echo "$MERGED_BRANCHES" | while read branch; do
        echo "  ✓ $branch"
    done
fi

if [ -z "$UNMERGED_BRANCHES" ]; then
    print_success "All branches are already merged!"
    exit 0
fi

echo -e "\n${YELLOW}Branches to merge:${NC}"
echo "$UNMERGED_BRANCHES" | while read branch; do
    echo "  → $branch"
done

# Ask for confirmation
echo -e "\n${YELLOW}Do you want to merge these branches? (y/n)${NC}"
read -r confirmation
if [ "$confirmation" != "y" ] && [ "$confirmation" != "Y" ]; then
    print_warning "Merge cancelled by user"
    exit 0
fi

# Merge each unmerged branch
echo -e "\n${BLUE}Starting merge process...${NC}\n"
MERGE_ERRORS=0
MERGED_COUNT=0

echo "$UNMERGED_BRANCHES" | while read branch; do
    print_status "Merging $branch..."

    # Attempt merge
    if git merge "$branch" --no-edit; then
        print_success "Merged $branch successfully"
        ((MERGED_COUNT++))
    else
        print_error "Merge conflict in $branch"
        print_warning "Aborting merge for manual resolution..."
        git merge --abort
        ((MERGE_ERRORS++))
        echo -e "${RED}Please manually resolve conflicts for: $branch${NC}"
    fi
    echo ""
done

# Push to remote if successful merges occurred
if [ "$MERGED_COUNT" -gt 0 ]; then
    echo -e "\n${BLUE}Pushing merged changes to remote...${NC}"

    # Check if upstream is configured
    if git rev-parse --abbrev-ref "$MAIN_BRANCH@{upstream}" >/dev/null 2>&1; then
        if git push; then
            print_success "Changes pushed to remote"
        else
            print_error "Failed to push to remote"
            exit 1
        fi
    else
        print_warning "No upstream configured for $MAIN_BRANCH"
        echo -e "${YELLOW}Setting upstream and pushing...${NC}"
        if git push --set-upstream origin "$MAIN_BRANCH"; then
            print_success "Upstream set and changes pushed"
        else
            print_error "Failed to set upstream and push"
            exit 1
        fi
    fi
fi

# Summary
echo -e "\n${BLUE}=== Merge Summary ===${NC}"
print_success "Successfully merged $MERGED_COUNT branch(es)"
if [ "$MERGE_ERRORS" -gt 0 ]; then
    print_warning "$MERGE_ERRORS branch(es) had conflicts and need manual resolution"
fi

exit 0
