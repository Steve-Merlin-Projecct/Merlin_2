#!/bin/bash
# Permanent GitHub Remote Fix Script

echo "🔧 Fixing GitHub remote configuration permanently..."
echo "=============================================="

# Check current remote
current_remote=$(git remote get-url origin 2>/dev/null)
echo "Current remote: $current_remote"

# Fix the malformed remote URL
if [[ "$current_remote" == *"origingit@github.com"* ]]; then
    echo "❌ Malformed remote detected!"
    echo "🔄 Fixing remote URL..."
    
    # Remove the broken remote
    git remote remove origin 2>/dev/null || echo "No origin to remove"
    
    # Add the correct remote
    git remote add origin git@github.com:Steve-Merlin-Projecct/Merlin.git
    
    echo "✅ Remote fixed!"
else
    echo "✅ Remote URL is already correct"
fi

# Verify the fix
new_remote=$(git remote get-url origin 2>/dev/null)
echo "New remote: $new_remote"

# Test connection
echo ""
echo "🔗 Testing GitHub connection..."
ssh -T git@github.com 2>&1 | head -1

echo ""
echo "✅ GitHub remote configuration completed!"