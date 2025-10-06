#!/bin/bash
# Only run in development environment
if [ "$REPL_SLUG" ] && [ -d ".git" ]; then
    echo "Development environment detected, setting up SSH..."
    
    # Create SSH directory
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    
    # Setup SSH key (support both RSA and Ed25519)
    if [ -n "$SSH_PRIVATE_KEY" ]; then
        echo -e "$SSH_PRIVATE_KEY" > ~/.ssh/id_ed25519
        chmod 600 ~/.ssh/id_ed25519
        echo "SSH private key configured"
    elif [ -f ".github/scripts/ssh/id_ed25519" ]; then
        # Copy existing key files to standard location
        cp ".github/scripts/ssh/id_ed25519" ~/.ssh/id_ed25519
        cp ".github/scripts/ssh/id_ed25519.pub" ~/.ssh/id_ed25519.pub
        chmod 600 ~/.ssh/id_ed25519
        chmod 644 ~/.ssh/id_ed25519.pub
        echo "Existing SSH keys copied to standard location"
    else
        echo "No SSH keys found, skipping key setup"
    fi
    
    # Add GitHub to known hosts
    ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
    
    # Fix Git remote URL (handle lock files and conflicts)
    if [ -f ".git/config.lock" ] || [ -f ".git/index.lock" ]; then
        echo "Git lock files detected, waiting for operations to complete..."
        sleep 3
        rm -f .git/config.lock .git/index.lock
    fi
    
    # Check current remote URL and fix if malformed
    current_url=$(git remote get-url origin 2>/dev/null)
    if [[ "$current_url" == *"origingit@github.com"* ]]; then
        echo "Fixing malformed remote URL..."
        git remote set-url origin git@github.com:Steve-Merlin-Projecct/Merlin.git 2>/dev/null || {
            echo "Could not set remote URL, manual fix may be needed"
        }
    else
        echo "Remote URL is correct: $current_url"
    fi
    
    # Test SSH connection
    ssh -T git@github.com 2>&1 | head -1
    
    echo "SSH setup completed"
else
    echo "Not in development environment or no git repo, skipping SSH setup"
    exit 0
fi