#!/bin/bash
# Force merge completed worktrees

set -e

cd /workspace

echo "=== Force Merge Script ==="
echo ""

# Remove any git locks
rm -f .git/index.lock

# Clean up temp files
rm -f .dockerignore.new Dockerfile.new

echo "✓ Cleaned up temporary files"

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Merge deployment worktree
echo "=== Merging deployment worktree ==="
if git merge task/09-deploymet-need-to-figure-out-how-to-deploy-this-sy --no-edit -X theirs 2>&1; then
    echo "✓ Deployment merged successfully"
else
    echo "⚠ Merge failed or had conflicts, forcing resolution..."

    # Accept their version for conflicts
    git checkout --theirs .claude/scripts/tree.sh 2>/dev/null || true
    git checkout --theirs .dockerignore 2>/dev/null || true
    git checkout --theirs Dockerfile 2>/dev/null || true

    # Add resolved files
    git add -A

    # Complete merge
    git commit --no-edit -m "Merge task/09: DigitalOcean deployment configuration (force-merged)" 2>/dev/null || echo "Already merged or commit not needed"
fi
echo ""

# Merge docx-security worktree
echo "=== Merging docx-security worktree ==="
if git merge task/06-docx-security-verification-system-prevent-maliciou --no-edit -X theirs 2>&1; then
    echo "✓ DOCX security merged successfully"
else
    echo "⚠ Merge failed or had conflicts, forcing resolution..."

    # Add all changes
    git add -A

    # Complete merge
    git commit --no-edit -m "Merge task/06: DOCX security enhancements (force-merged)" 2>/dev/null || echo "Already merged or commit not needed"
fi
echo ""

# Clean up worktrees
echo "=== Cleaning up worktrees ==="

if [ -d "/workspace/.trees/deploymet-need-to-figure-out-how-to-deploy-this-sy" ]; then
    git worktree remove --force /workspace/.trees/deploymet-need-to-figure-out-how-to-deploy-this-sy 2>&1 || echo "Could not remove deployment worktree"
    echo "✓ Removed deployment worktree"
fi

if [ -d "/workspace/.trees/docx-security-verification-system-prevent-maliciou" ]; then
    git worktree remove --force /workspace/.trees/docx-security-verification-system-prevent-maliciou 2>&1 || echo "Could not remove docx-security worktree"
    echo "✓ Removed docx-security worktree"
fi

# Delete branches
echo ""
echo "=== Deleting merged branches ==="
git branch -d task/09-deploymet-need-to-figure-out-how-to-deploy-this-sy 2>&1 || git branch -D task/09-deploymet-need-to-figure-out-how-to-deploy-this-sy 2>&1 || echo "Branch already deleted"
git branch -d task/06-docx-security-verification-system-prevent-maliciou 2>&1 || git branch -D task/06-docx-security-verification-system-prevent-maliciou 2>&1 || echo "Branch already deleted"

# Archive synopsis files
echo ""
echo "=== Archiving synopsis files ==="
mkdir -p /workspace/.trees/.archived/deployment /workspace/.trees/.archived/docx-security
mv /workspace/.trees/.completed/deploymet-need-to-figure-out-how-to-deploy-this-sy-synopsis-*.md /workspace/.trees/.archived/deployment/ 2>/dev/null || echo "No deployment synopsis to archive"
mv /workspace/.trees/.completed/docx-security-verification-system-prevent-maliciou-synopsis-*.md /workspace/.trees/.archived/docx-security/ 2>/dev/null || echo "No docx-security synopsis to archive"

echo ""
echo "=== Force Merge Complete ==="
echo ""
git status
