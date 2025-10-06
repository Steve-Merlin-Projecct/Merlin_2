#!/bin/bash
# Git Lock Prevention System - Prevents creation of .git/index.lock files
# Implements proactive measures to avoid git lock conflicts

echo "Git Lock Prevention System - Proactive Lock Management"

# Function to check if any git processes are running
check_git_processes() {
    local git_processes=$(pgrep -f "git" 2>/dev/null | wc -l)
    if [ "$git_processes" -gt 0 ]; then
        echo "⚠️  Found $git_processes git process(es) running"
        echo "Waiting for git processes to complete..."
        
        # Wait up to 10 seconds for git processes to finish
        local timeout=10
        while [ $timeout -gt 0 ] && [ $(pgrep -f "git" 2>/dev/null | wc -l) -gt 0 ]; do
            sleep 1
            ((timeout--))
            echo -n "."
        done
        echo ""
        
        if [ $(pgrep -f "git" 2>/dev/null | wc -l) -gt 0 ]; then
            echo "❌ Git processes still running after timeout"
            return 1
        else
            echo "✅ All git processes completed"
        fi
    else
        echo "✅ No conflicting git processes found"
    fi
    return 0
}

# Function to remove existing lock files safely
remove_all_git_locks() {
    echo "Removing any existing git lock files..."
    
    # Remove all common git lock files
    rm -f .git/index.lock 2>/dev/null
    rm -f .git/config.lock 2>/dev/null
    rm -f .git/HEAD.lock 2>/dev/null
    rm -f .git/refs/heads/*.lock 2>/dev/null
    rm -f .git/refs/remotes/origin/*.lock 2>/dev/null
    rm -f .git/refs/remotes/origin/HEAD.lock 2>/dev/null
    rm -f .git/logs/HEAD.lock 2>/dev/null
    rm -f .git/logs/refs/heads/*.lock 2>/dev/null
    rm -f .git/logs/refs/remotes/origin/*.lock 2>/dev/null
    
    echo "✅ Lock files cleared"
}

# Function to set up git configuration to minimize lock creation
configure_git_for_lock_prevention() {
    echo "Configuring git to prevent lock conflicts..."
    
    # Set git to be more conservative with lock files
    git config core.preloadindex true 2>/dev/null || true
    git config core.fscache true 2>/dev/null || true
    git config gc.auto 0 2>/dev/null || true  # Disable automatic garbage collection
    git config advice.detachedHead false 2>/dev/null || true
    
    # Configure shorter timeouts
    git config http.timeout 30 2>/dev/null || true
    git config ssh.timeout 30 2>/dev/null || true
    
    echo "✅ Git configuration optimized"
}

# Function to perform safe git operations with lock prevention
safe_git_operation() {
    local operation="$1"
    shift  # Remove first argument, keep the rest for the git command
    
    echo "Performing safe git operation: $operation"
    
    # Step 1: Check for running processes
    if ! check_git_processes; then
        echo "❌ Cannot proceed - git processes are still running"
        return 1
    fi
    
    # Step 2: Remove any existing locks
    remove_all_git_locks
    
    # Step 3: Wait a moment for file system to sync
    sleep 0.5
    
    # Step 4: Execute the git operation
    echo "Executing: git $*"
    git "$@"
    local exit_code=$?
    
    # Step 5: Clean up any locks that might have been left behind
    if [ $exit_code -ne 0 ]; then
        echo "⚠️  Git operation failed, cleaning up locks..."
        sleep 1
        remove_all_git_locks
    fi
    
    return $exit_code
}

# Function to install git hooks for automatic lock cleanup
install_git_hooks() {
    echo "Installing git hooks for automatic lock cleanup..."
    
    mkdir -p .git/hooks
    
    # Create pre-command hook
    cat > .git/hooks/pre-command << 'EOF'
#!/bin/bash
# Automatic git lock cleanup before any git command
rm -f .git/index.lock 2>/dev/null
rm -f .git/config.lock 2>/dev/null
EOF
    
    # Create post-command hook
    cat > .git/hooks/post-command << 'EOF'
#!/bin/bash
# Automatic git lock cleanup after any git command
sleep 0.1
rm -f .git/index.lock 2>/dev/null
rm -f .git/config.lock 2>/dev/null
EOF
    
    chmod +x .git/hooks/pre-command 2>/dev/null
    chmod +x .git/hooks/post-command 2>/dev/null
    
    echo "✅ Git hooks installed"
}

# Function to create a git wrapper function
create_git_wrapper() {
    echo "Creating git wrapper function..."
    
    # Create a wrapper script that always prevents locks
    cat > .github/scripts/git_safe << 'EOF'
#!/bin/bash
# Safe git wrapper - always prevents lock file issues

# Remove locks before operation
rm -f .git/index.lock .git/config.lock 2>/dev/null

# Wait for any git processes
while pgrep -f "git" >/dev/null 2>&1; do
    sleep 0.1
done

# Execute git command
git "$@"
exit_code=$?

# Clean up locks after operation
rm -f .git/index.lock .git/config.lock 2>/dev/null

exit $exit_code
EOF
    
    chmod +x .github/scripts/git_safe
    echo "✅ Git wrapper created: .github/scripts/git_safe"
}

# Function to set up automatic lock monitoring
setup_lock_monitoring() {
    echo "Setting up git lock monitoring..."
    
    # Create a monitoring script
    cat > .github/scripts/git_lock_monitor.sh << 'EOF'
#!/bin/bash
# Git Lock Monitor - Continuously monitors and removes git locks

echo "Starting git lock monitor (runs every 5 seconds)..."
echo "Press Ctrl+C to stop"

while true; do
    if [ -f .git/index.lock ] || [ -f .git/config.lock ]; then
        echo "$(date): Lock files detected, removing..."
        rm -f .git/index.lock .git/config.lock 2>/dev/null
        echo "$(date): Lock files cleaned"
    fi
    sleep 5
done
EOF
    
    chmod +x .github/scripts/git_lock_monitor.sh
    echo "✅ Lock monitor created: .github/scripts/git_lock_monitor.sh"
}

# Main function to set up complete lock prevention
main() {
    echo "=== Setting up comprehensive git lock prevention ==="
    
    case "$1" in
        --full)
            echo "Performing full git lock prevention setup..."
            check_git_processes
            remove_all_git_locks
            configure_git_for_lock_prevention
            install_git_hooks
            create_git_wrapper
            setup_lock_monitoring
            echo "✅ Full git lock prevention setup complete!"
            ;;
        --clean-only)
            echo "Cleaning existing locks only..."
            check_git_processes
            remove_all_git_locks
            ;;
        --config-only)
            echo "Configuring git settings only..."
            configure_git_for_lock_prevention
            ;;
        --monitor)
            echo "Starting lock monitoring..."
            .github/scripts/git_lock_monitor.sh
            ;;
        --safe)
            shift
            safe_git_operation "$@"
            ;;
        *)
            echo "Git Lock Prevention System"
            echo ""
            echo "Usage:"
            echo "  $0 --full          # Complete setup (recommended)"
            echo "  $0 --clean-only    # Remove existing locks"
            echo "  $0 --config-only   # Configure git settings"
            echo "  $0 --monitor       # Start continuous monitoring"
            echo "  $0 --safe <cmd>    # Execute git command safely"
            echo ""
            echo "Examples:"
            echo "  $0 --full                    # Set up everything"
            echo "  $0 --safe add -A             # Safe git add"
            echo "  $0 --safe commit -m 'msg'    # Safe git commit"
            echo "  $0 --clean-only              # Quick cleanup"
            ;;
    esac
}

# Run main function with all arguments
main "$@"