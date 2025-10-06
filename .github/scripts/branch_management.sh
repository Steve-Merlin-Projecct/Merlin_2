#!/bin/bash
# Branch Management System - Safe feature development with rollback capabilities
# Prioritizes GitHub as source of truth while enabling safe feature branching

echo "Branch Management System - Safe Feature Development"

# Source the git wrapper for safe operations
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/git_wrapper.sh" >/dev/null 2>&1 || true

# Function to create a new feature branch
create_feature_branch() {
    local branch_name="$1"
    local base_branch="${2:-main}"
    
    if [ -z "$branch_name" ]; then
        echo "Usage: create_feature_branch <branch_name> [base_branch]"
        return 1
    fi
    
    echo "Creating feature branch '$branch_name' from '$base_branch'..."
    
    # Ensure we're synced with GitHub first
    git fetch origin 2>/dev/null || echo "Note: Could not fetch from GitHub"
    
    # Switch to base branch and update
    git checkout "$base_branch"
    git pull origin "$base_branch" 2>/dev/null || echo "Note: Could not pull from GitHub"
    
    # Create and switch to new feature branch
    git checkout -b "$branch_name"
    
    # Set upstream to GitHub
    git push -u origin "$branch_name" 2>/dev/null || echo "Note: Could not push to GitHub"
    
    echo "✅ Feature branch '$branch_name' created"
    echo "Current branch: $(git branch --show-current)"
}

# Function to ensure database schema is up to date (smart checking)
ensure_database_schema_updated() {
    echo "🔍 Checking database schema..."
    
    # Check if schema automation detects changes
    if python database_tools/schema_automation.py --check 2>/dev/null; then
        echo "✅ Schema current"
        return 0
    else
        echo "📊 Schema changes detected - updating..."
        if tools/update_database_schema.sh; then
            echo "✅ Schema updated"
            return 0
        else
            echo "❌ Schema update failed"
            return 1
        fi
    fi
}

# Function to create a safe checkpoint
create_checkpoint() {
    local checkpoint_name="${1:-checkpoint-$(date +%Y%m%d-%H%M%S)}"
    local current_branch=$(git branch --show-current)
    
    echo "Creating checkpoint '$checkpoint_name' on branch '$current_branch'..."
    
    # CRITICAL: Ensure database schema is updated before any commits
    ensure_database_schema_updated
    
    # Ensure all changes are committed
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "Uncommitted changes detected. Committing as checkpoint..."
        git add .
        git commit -m "Checkpoint: $checkpoint_name - Auto-save before major changes"
    fi
    
    # Create checkpoint tag
    git tag -a "$checkpoint_name" -m "Checkpoint: Safe rollback point created $(date)"
    
    # Push checkpoint to GitHub
    git push origin "$current_branch" 2>/dev/null || echo "Note: Could not push to GitHub"
    git push origin "$checkpoint_name" 2>/dev/null || echo "Note: Could not push tag to GitHub"
    
    echo "✅ Checkpoint '$checkpoint_name' created"
    echo "To rollback: git reset --hard $checkpoint_name"
}

# Function to list available checkpoints
list_checkpoints() {
    echo "Available checkpoints (rollback points):"
    git tag -l "checkpoint-*" | sort -r | head -20
    echo ""
    echo "Recent commits on current branch:"
    git log --oneline -10
}

# Function to check which remote branches are merged
check_merged_branches() {
    local target_branch="${1:-main}"
    
    echo "Checking which remote branches are merged into '$target_branch'..."
    echo ""
    
    # Fetch latest remote information
    echo "Fetching latest remote information..."
    git fetch origin 2>/dev/null || echo "⚠️  Could not fetch from GitHub"
    echo ""
    
    # Check merged remote branches
    echo "Remote branches merged into origin/$target_branch:"
    echo "================================================="
    
    local merged_branches=$(git branch -r --merged origin/$target_branch 2>/dev/null)
    
    if [ -z "$merged_branches" ]; then
        echo "❌ Could not determine merged branches (check GitHub connection)"
        return 1
    fi
    
    echo "$merged_branches" | while IFS= read -r branch; do
        if [ -n "$branch" ]; then
            # Clean up branch name and check if it's significant
            clean_branch=$(echo "$branch" | sed 's/^[[:space:]]*//' | sed 's/origin\///')
            
            if [ "$clean_branch" = "$target_branch" ]; then
                echo "✅ $clean_branch (target branch)"
            elif [ "$clean_branch" = "HEAD" ]; then
                echo "ℹ️  HEAD -> origin/$target_branch"
            else
                echo "🔗 $clean_branch (merged)"
            fi
        fi
    done
    
    echo ""
    echo "Checking specific branch status:"
    echo "==============================="
    
    # Check noxml specifically
    if git show-ref --verify --quiet refs/remotes/origin/noxml; then
        if git branch -r --merged origin/$target_branch | grep -q "origin/noxml"; then
            echo "✅ noxml branch: MERGED into $target_branch"
        else
            echo "⚠️  noxml branch: NOT MERGED into $target_branch"
            
            # Show what's different
            echo ""
            echo "Commits in noxml not in $target_branch:"
            git log --oneline origin/$target_branch..origin/noxml 2>/dev/null | head -5
        fi
    else
        echo "❓ noxml branch: Not found on remote"
    fi
    
    echo ""
    echo "Summary:"
    echo "========"
    
    # Count merged branches
    local merged_count=$(git branch -r --merged origin/$target_branch 2>/dev/null | grep -v "HEAD" | grep -v "origin/$target_branch" | wc -l)
    echo "📊 Total remote branches merged into $target_branch: $merged_count"
    
    # Show unmerged branches for context
    echo ""
    echo "Remote branches NOT merged into $target_branch:"
    git branch -r --no-merged origin/$target_branch 2>/dev/null | while IFS= read -r branch; do
        if [ -n "$branch" ]; then
            clean_branch=$(echo "$branch" | sed 's/^[[:space:]]*//' | sed 's/origin\///')
            if [ "$clean_branch" != "HEAD" ]; then
                echo "🔄 $clean_branch (unmerged)"
            fi
        fi
    done
}

# Function to rollback to a checkpoint
rollback_to_checkpoint() {
    local checkpoint="$1"
    
    if [ -z "$checkpoint" ]; then
        echo "Available checkpoints:"
        git tag -l "checkpoint-*" | sort -r | head -10
        echo ""
        echo "Usage: rollback_to_checkpoint <checkpoint_name_or_commit_hash>"
        return 1
    fi
    
    echo "Rolling back to checkpoint: $checkpoint"
    
    # Verify checkpoint exists
    if ! git rev-parse --verify "$checkpoint" >/dev/null 2>&1; then
        echo "❌ Checkpoint '$checkpoint' not found"
        return 1
    fi
    
    # Create backup before rollback
    local backup_branch="backup-$(git branch --show-current)-$(date +%Y%m%d-%H%M%S)"
    git branch "$backup_branch"
    git push origin "$backup_branch" 2>/dev/null || echo "Note: Backup created locally"
    echo "📦 Backup created: $backup_branch"
    
    # Perform rollback
    git reset --hard "$checkpoint"
    
    echo "✅ Rolled back to checkpoint: $checkpoint"
    echo "Backup available at: $backup_branch"
    echo "Current HEAD: $(git rev-parse --short HEAD)"
}

# Function to merge feature branch safely
merge_feature_branch() {
    local feature_branch="$1"
    local target_branch="${2:-main}"
    
    if [ -z "$feature_branch" ]; then
        echo "Usage: merge_feature_branch <feature_branch> [target_branch]"
        return 1
    fi
    
    echo "Safely merging '$feature_branch' into '$target_branch'..."
    
    # CRITICAL: Ensure database schema is updated before merge
    ensure_database_schema_updated
    
    # Create checkpoint before merge
    git checkout "$target_branch"
    create_checkpoint "pre-merge-$(echo $feature_branch | tr '/' '-')"
    
    # Sync with GitHub
    git pull origin "$target_branch" 2>/dev/null || echo "Note: Could not sync with GitHub"
    
    # Merge feature branch
    if git merge "$feature_branch" --no-ff -m "Merge feature branch: $feature_branch"; then
        # Push to GitHub on successful merge
        git push origin "$target_branch" 2>/dev/null || echo "Note: Could not push to GitHub"
        echo "✅ Feature branch '$feature_branch' merged into '$target_branch'"
        echo "Merge checkpoint created for easy rollback if needed"
    else
        echo "❌ Merge failed due to conflicts"
        echo "Conflicts detected in the following files:"
        git status --porcelain | grep "^UU\|^AA\|^DD" || echo "Run 'git status' to see conflicted files"
        echo ""
        echo "To resolve conflicts:"
        echo "1. Edit conflicted files to resolve conflicts"
        echo "2. Run: git add <resolved-files>"
        echo "3. Run: git commit to complete the merge"
        echo "4. Or run: git merge --abort to cancel the merge"
        echo ""
        echo "Checkpoint 'pre-merge-$(echo $feature_branch | tr '/' '-')' is available for rollback"
        return 1
    fi
}

# Function to switch branches safely
switch_branch() {
    local target_branch="$1"
    
    if [ -z "$target_branch" ]; then
        echo "Available branches:"
        git branch -a
        echo ""
        echo "Usage: switch_branch <branch_name>"
        return 1
    fi
    
    echo "Switching to branch: $target_branch"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "Uncommitted changes detected. Creating checkpoint..."
        create_checkpoint "auto-checkpoint-before-switch"
    fi
    
    # Switch branch and sync with GitHub
    git checkout "$target_branch"
    git pull origin "$target_branch" 2>/dev/null || echo "Branch exists only locally"
    
    echo "✅ Switched to branch: $(git branch --show-current)"
}

# Function to show branch status
branch_status() {
    echo "=== Branch Management Status ==="
    echo "Current branch: $(git branch --show-current)"
    echo "Last commit: $(git log -1 --oneline 2>/dev/null || echo 'No commits')"
    echo ""
    
    echo "Local branches:"
    git branch 2>/dev/null
    echo ""
    
    echo "Remote branches:"
    git branch -r 2>/dev/null
    echo ""
    
    echo "Recent checkpoints:"
    git tag -l "checkpoint-*" | sort -r | head -5
    echo ""
    
    echo "Uncommitted changes:"
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "✅ Working directory clean"
    else
        echo "⚠️  Uncommitted changes detected"
        git status --porcelain 2>/dev/null
    fi
}

# Main execution based on command
case "$1" in
    create)
        create_feature_branch "$2" "$3"
        ;;
    checkpoint)
        create_checkpoint "$2"
        ;;
    rollback)
        rollback_to_checkpoint "$2"
        ;;
    merge)
        merge_feature_branch "$2" "$3"
        ;;
    switch)
        switch_branch "$2"
        ;;
    status)
        branch_status
        ;;
    list)
        list_checkpoints
        ;;
    check-merged)
        check_merged_branches "$2"
        ;;
    *)
        echo "Branch Management System"
        echo "Usage: $0 <command> [arguments]"
        echo ""
        echo "Commands:"
        echo "  create <branch_name> [base_branch]  - Create new feature branch"
        echo "  checkpoint [name]                   - Create rollback checkpoint"
        echo "  rollback <checkpoint>               - Rollback to checkpoint"
        echo "  merge <feature_branch> [target]     - Safely merge feature branch"
        echo "  switch <branch_name>                - Switch branches safely"
        echo "  status                              - Show branch status"
        echo "  list                                - List checkpoints and commits"
        echo "  check-merged [branch]               - Check which remote branches are merged into main (or specified branch)"
        echo ""
        echo "Examples:"
        echo "  $0 create feature/document-generation main"
        echo "  $0 checkpoint before-api-changes"
        echo "  $0 rollback checkpoint-20250720-151030"
        echo "  $0 merge feature/document-generation main"
        echo "  $0 switch main"
        echo "  $0 check-merged main"
        echo "  $0 check-merged"
        ;;
esac