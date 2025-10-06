#!/bin/bash
# Auto Commit Script - Safely commits changes without git lock issues
# Uses the safe git commands to prevent lock file problems

SCRIPT_DIR="$(dirname "$0")"
SAFE_GIT="$SCRIPT_DIR/git_safe_commands.sh"

echo "Auto Commit - Safe Git Operations"

# Function to commit current changes
auto_commit() {
    local commit_message="$1"
    
    if [ -z "$commit_message" ]; then
        commit_message="auto: Update project files $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    echo "Preparing to commit with message: $commit_message"
    
    # Step 1: Add all changes
    echo "Adding changes..."
    "$SAFE_GIT" add -A
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to add changes"
        return 1
    fi
    
    # Step 2: Check if there are changes to commit
    if git diff --cached --quiet; then
        echo "ℹ️  No changes to commit"
        return 0
    fi
    
    # Step 3: Commit changes
    echo "Committing changes..."
    "$SAFE_GIT" commit -m "$commit_message"
    
    if [ $? -eq 0 ]; then
        echo "✅ Commit successful: $commit_message"
        return 0
    else
        echo "❌ Commit failed"
        return 1
    fi
}

# Main execution
case "$1" in
    "--message"|"-m")
        auto_commit "$2"
        ;;
    *)
        if [ $# -eq 0 ]; then
            echo "Auto Commit - Safe Git Operations"
            echo ""
            echo "Usage:"
            echo "  $0                          # Auto commit with timestamp"
            echo "  $0 -m \"commit message\"      # Commit with custom message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Auto commit"
            echo "  $0 -m \"Fix git lock prevention\"  # Custom message"
        else
            # Treat all arguments as commit message
            auto_commit "$*"
        fi
        ;;
esac