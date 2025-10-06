#!/bin/bash
# Git startup fix script - handles lock files and remote URL issues

echo "Starting Git configuration fix..."

# Wait for any existing git processes to complete
sleep 2

# Remove any lock files
rm -f .git/config.lock .git/index.lock .git/refs/heads/main.lock

# Fix the malformed remote URL
current_url=$(git remote get-url origin 2>/dev/null)
if [[ "$current_url" == *"origingit@github.com"* ]]; then
    echo "Fixing malformed remote URL..."
    
    # Remove the malformed remote and add correct one
    git remote remove origin 2>/dev/null || true
    git remote add origin git@github.com:Steve-Merlin-Projecct/Merlin.git
    
    echo "Remote URL fixed"
else
    echo "Remote URL is already correct: $current_url"
fi

# Verify the fix
echo "Current remote configuration:"
git remote -v

# Test connection
echo "Testing SSH connection to GitHub..."
ssh -T git@github.com 2>&1 | head -1

echo "Git configuration fix completed"