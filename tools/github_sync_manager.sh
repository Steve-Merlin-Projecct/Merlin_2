#!/bin/bash
# GitHub Sync Manager - Comprehensive solution for Replit GitHub connectivity

echo "🚀 GitHub Sync Manager v1.0"
echo "=========================="

# Function to setup SSH
setup_ssh() {
    echo "📦 Setting up SSH keys..."
    
    # Create SSH directory
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    
    # Check for SSH key in environment or local files
    if [ -n "$SSH_PRIVATE_KEY" ]; then
        echo -e "$SSH_PRIVATE_KEY" > ~/.ssh/id_ed25519
        chmod 600 ~/.ssh/id_ed25519
        echo "✅ SSH key from environment configured"
    elif [ -f ".github/scripts/ssh/id_ed25519" ]; then
        cp ".github/scripts/ssh/id_ed25519" ~/.ssh/
        cp ".github/scripts/ssh/id_ed25519.pub" ~/.ssh/
        chmod 600 ~/.ssh/id_ed25519
        chmod 644 ~/.ssh/id_ed25519.pub
        echo "✅ Local SSH keys copied"
    else
        echo "❌ No SSH keys found!"
        return 1
    fi
    
    # Add GitHub to known hosts
    ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
    echo "✅ GitHub added to known hosts"
}

# Function to fix remote URL
fix_remote() {
    echo "🔧 Checking remote configuration..."
    
    current=$(git remote get-url origin 2>/dev/null)
    correct="git@github.com:Steve-Merlin-Projecct/Merlin.git"
    
    if [[ "$current" != "$correct" ]]; then
        echo "❌ Remote URL incorrect: $current"
        git remote remove origin 2>/dev/null
        git remote add origin "$correct"
        echo "✅ Remote URL fixed to: $correct"
    else
        echo "✅ Remote URL is correct"
    fi
}

# Function to handle lock files
handle_locks() {
    echo "🔒 Checking for lock files..."
    
    locks=(".git/index.lock" ".git/config.lock" ".git/HEAD.lock")
    found_locks=false
    
    for lock in "${locks[@]}"; do
        if [ -f "$lock" ]; then
            echo "Found lock: $lock"
            rm -f "$lock"
            found_locks=true
        fi
    done
    
    if [ "$found_locks" = true ]; then
        echo "✅ Lock files removed"
    else
        echo "✅ No lock files found"
    fi
}

# Function to test connection
test_connection() {
    echo "🔗 Testing GitHub connection..."
    
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ GitHub authentication successful!"
        return 0
    else
        echo "❌ GitHub authentication failed!"
        return 1
    fi
}

# Function to perform safe git operations
safe_git_operation() {
    local operation=$1
    shift
    local args=$@
    
    echo "🔄 Performing: git $operation $args"
    
    # Remove any lock files first
    handle_locks
    
    # Try the operation
    if git $operation $args; then
        echo "✅ Operation successful"
        return 0
    else
        echo "❌ Operation failed, retrying..."
        sleep 2
        handle_locks
        git $operation $args
    fi
}

# Main execution
main() {
    echo "Starting GitHub sync setup..."
    echo ""
    
    # Step 1: Setup SSH
    setup_ssh
    echo ""
    
    # Step 2: Fix remote
    fix_remote
    echo ""
    
    # Step 3: Handle locks
    handle_locks
    echo ""
    
    # Step 4: Test connection
    test_connection
    echo ""
    
    # Step 5: Show status
    echo "📊 Current Status:"
    echo "Remote: $(git remote get-url origin 2>/dev/null)"
    echo "Branch: $(git branch --show-current 2>/dev/null)"
    echo ""
    
    # Provide usage instructions
    echo "🎯 Usage Instructions:"
    echo "1. To fetch: ./github_sync_manager.sh fetch"
    echo "2. To pull:  ./github_sync_manager.sh pull"
    echo "3. To push:  ./github_sync_manager.sh push"
    echo "4. To sync:  ./github_sync_manager.sh sync"
    echo ""
    
    # Handle command arguments
    if [ "$1" ]; then
        case "$1" in
            fetch)
                safe_git_operation fetch origin
                ;;
            pull)
                safe_git_operation pull origin "$(git branch --show-current)"
                ;;
            push)
                safe_git_operation push origin "$(git branch --show-current)"
                ;;
            sync)
                safe_git_operation fetch origin
                safe_git_operation pull origin "$(git branch --show-current)"
                safe_git_operation push origin "$(git branch --show-current)"
                ;;
            *)
                echo "Unknown command: $1"
                ;;
        esac
    fi
}

# Run main function
main "$@"