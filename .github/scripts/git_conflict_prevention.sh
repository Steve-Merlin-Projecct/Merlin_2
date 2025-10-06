#!/bin/bash
# Git Conflict Prevention Script - Prioritizes GitHub over local Replit git
# Prevents conflicts between Replit's git management and GitHub

echo "Git Conflict Prevention - Prioritizing GitHub..."

# Function to safely remove lock files
remove_git_locks() {
    echo "Removing git lock files..."
    rm -f .git/index.lock 2>/dev/null
    rm -f .git/config.lock 2>/dev/null
    rm -f .git/refs/heads/*.lock 2>/dev/null
    rm -f .git/refs/remotes/origin/*.lock 2>/dev/null
    rm -f .git/refs/remotes/origin/HEAD.lock 2>/dev/null
    echo "Lock files cleared"
}

# Function to set GitHub as priority remote
set_github_priority() {
    echo "Setting GitHub as priority remote..."
    
    # Ensure proper remote URL
    git remote set-url origin git@github.com:Steve-Merlin-Projecct/Merlin.git 2>/dev/null || echo "Note: Could not set remote URL"
    
    # Set GitHub as upstream for all branches
    git branch --set-upstream-to=origin/main main 2>/dev/null || true
    
    # Configure git to prioritize remote changes
    git config pull.rebase true 2>/dev/null || true
    git config push.default upstream 2>/dev/null || true
    git config remote.origin.prune true 2>/dev/null || true
    
    echo "GitHub priority configured"
}

# Function to sync with GitHub (prioritize remote, handle feature branches safely)
sync_with_github() {
    echo "Syncing with GitHub (prioritizing remote)..."
    
    # Fetch latest from GitHub
    git fetch origin 2>/dev/null || echo "Note: Could not fetch from GitHub"
    
    # Get current branch
    current_branch=$(git branch --show-current)
    
    # Handle different branch types
    case "$current_branch" in
        main|master|develop)
            echo "On protected branch: $current_branch - prioritizing GitHub version"
            git reset --hard origin/$current_branch 2>/dev/null || echo "Note: Could not reset to GitHub version"
            ;;
        feature/*|fix/*|hotfix/*)
            echo "On feature branch: $current_branch"
            
            # Check if remote branch exists
            if git show-ref --verify --quiet refs/remotes/origin/$current_branch 2>/dev/null; then
                echo "Remote branch exists - merging from GitHub (preserving local work)"
                git merge origin/$current_branch 2>/dev/null || echo "Note: Could not merge from GitHub"
            else
                echo "Remote branch doesn't exist - will push local changes"
                git push -u origin "$current_branch" 2>/dev/null || echo "Note: Could not push to GitHub"
            fi
            ;;
        *)
            echo "On custom branch: $current_branch"
            
            # Check if remote branch exists
            if git show-ref --verify --quiet refs/remotes/origin/$current_branch 2>/dev/null; then
                echo "Remote branch exists - merging from GitHub"
                git merge origin/$current_branch 2>/dev/null || echo "Note: Could not merge from GitHub"
            else
                echo "Remote branch doesn't exist - will push local changes"
                echo "Consider using: git push -u origin $current_branch"
            fi
            ;;
    esac
    
    echo "GitHub sync completed"
}

# Function to prevent future conflicts
setup_conflict_prevention() {
    echo "Setting up conflict prevention..."
    
    # Configure git to handle conflicts automatically
    git config merge.tool vimdiff 2>/dev/null || true
    git config merge.conflictstyle diff3 2>/dev/null || true
    git config pull.rebase true 2>/dev/null || true
    
    # Set up automatic cleanup
    git config gc.auto 1 2>/dev/null || true
    git config gc.pruneexpire "2 weeks ago" 2>/dev/null || true
    
    # Configure authentication to persist
    git config credential.helper store 2>/dev/null || true
    
    echo "Conflict prevention configured"
}

# Main execution
case "$1" in
    --sync-only)
        remove_git_locks
        sync_with_github
        ;;
    --setup-only)
        set_github_priority
        setup_conflict_prevention
        ;;
    --full)
        remove_git_locks
        set_github_priority
        sync_with_github
        setup_conflict_prevention
        ;;
    *)
        echo "Running basic conflict prevention..."
        remove_git_locks
        set_github_priority
        setup_conflict_prevention
        ;;
esac

echo "Git conflict prevention completed"
echo ""
echo "Usage:"
echo "  ./git_conflict_prevention.sh         - Basic setup"
echo "  ./git_conflict_prevention.sh --sync-only   - Sync with GitHub only"
echo "  ./git_conflict_prevention.sh --setup-only  - Configuration only"
echo "  ./git_conflict_prevention.sh --full        - Complete setup"