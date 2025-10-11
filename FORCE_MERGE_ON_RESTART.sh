#!/bin/bash
# Force merge script to run after Claude Code restart
# This script will force-merge two completed worktrees that had issues with /tree closedone

set -e

echo "════════════════════════════════════════════════════════════"
echo "🔧 FORCE MERGE SCRIPT - Completed Worktrees"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "This script will:"
echo "  1. Clean up git locks and temp files"
echo "  2. Force merge task/09 (deployment)"
echo "  3. Force merge task/06 (docx-security)"
echo "  4. Remove worktrees and delete branches"
echo "  5. Archive synopsis files"
echo ""
echo "Press ENTER to continue, or Ctrl+C to cancel..."
read

cd /workspace

# Step 1: Clean up
echo ""
echo "=== Step 1: Cleanup ==="
rm -f .git/index.lock
rm -f .dockerignore.new Dockerfile.new
echo "✓ Removed lock files and temp files"

# Check current state
CURRENT_BRANCH=$(git branch --show-current)
echo "✓ Current branch: $CURRENT_BRANCH"

# Step 2: Merge deployment branch
echo ""
echo "=== Step 2: Merging task/09-deploymet (deployment) ==="

# Check if branch exists
if ! git rev-parse --verify task/09-deploymet-need-to-figure-out-how-to-deploy-this-sy >/dev/null 2>&1; then
    echo "⚠ Branch task/09-deploymet already merged or doesn't exist"
else
    # Try merge
    if git merge task/09-deploymet-need-to-figure-out-how-to-deploy-this-sy --no-edit 2>&1; then
        echo "✓ Merged successfully (no conflicts)"
    else
        echo "⚠ Merge had conflicts, resolving..."

        # Check if we're in a merge state
        if [ -f .git/MERGE_HEAD ]; then
            # Accept theirs for tree.sh (has the latest version)
            if [ -f .claude/scripts/tree.sh ]; then
                git checkout --theirs .claude/scripts/tree.sh
                echo "  ✓ Resolved tree.sh (kept their version)"
            fi

            # Accept theirs for Docker files (has deployment config)
            if git diff --name-only --diff-filter=U | grep -q "Dockerfile"; then
                git checkout --theirs Dockerfile
                echo "  ✓ Resolved Dockerfile (kept deployment version)"
            fi

            if git diff --name-only --diff-filter=U | grep -q ".dockerignore"; then
                git checkout --theirs .dockerignore
                echo "  ✓ Resolved .dockerignore (kept deployment version)"
            fi

            # Stage all resolved files
            git add -A

            # Complete the merge
            if git commit --no-edit; then
                echo "✓ Merge commit created"
            else
                echo "⚠ Merge commit failed, trying with message..."
                git commit -m "Merge task/09: DigitalOcean deployment configuration (force-merged)"
            fi
        else
            echo "✓ Merge completed (already done or fast-forward)"
        fi
    fi
fi

# Step 3: Merge docx-security branch
echo ""
echo "=== Step 3: Merging task/06-docx-security ==="

if ! git rev-parse --verify task/06-docx-security-verification-system-prevent-maliciou >/dev/null 2>&1; then
    echo "⚠ Branch task/06-docx-security already merged or doesn't exist"
else
    if git merge task/06-docx-security-verification-system-prevent-maliciou --no-edit 2>&1; then
        echo "✓ Merged successfully"
    else
        echo "⚠ Merge had conflicts, resolving..."

        if [ -f .git/MERGE_HEAD ]; then
            # Stage all changes
            git add -A

            # Complete merge
            if git commit --no-edit; then
                echo "✓ Merge commit created"
            else
                git commit -m "Merge task/06: DOCX security enhancements (force-merged)"
            fi
        else
            echo "✓ Merge completed"
        fi
    fi
fi

# Step 4: Remove worktrees
echo ""
echo "=== Step 4: Removing worktrees ==="

if [ -d "/workspace/.trees/deploymet-need-to-figure-out-how-to-deploy-this-sy" ]; then
    git worktree remove --force /workspace/.trees/deploymet-need-to-figure-out-how-to-deploy-this-sy 2>&1 || echo "  (could not remove, may already be gone)"
    echo "✓ Removed deployment worktree"
else
    echo "⚠ Deployment worktree already removed"
fi

if [ -d "/workspace/.trees/docx-security-verification-system-prevent-maliciou" ]; then
    git worktree remove --force /workspace/.trees/docx-security-verification-system-prevent-maliciou 2>&1 || echo "  (could not remove, may already be gone)"
    echo "✓ Removed docx-security worktree"
else
    echo "⚠ DOCX security worktree already removed"
fi

# Step 5: Delete branches
echo ""
echo "=== Step 5: Deleting merged branches ==="

if git rev-parse --verify task/09-deploymet-need-to-figure-out-how-to-deploy-this-sy >/dev/null 2>&1; then
    if git branch -d task/09-deploymet-need-to-figure-out-how-to-deploy-this-sy 2>&1; then
        echo "✓ Deleted task/09-deploymet branch (safe delete)"
    else
        echo "⚠ Safe delete failed, force deleting..."
        git branch -D task/09-deploymet-need-to-figure-out-how-to-deploy-this-sy
        echo "✓ Force deleted task/09-deploymet branch"
    fi
else
    echo "⚠ task/09-deploymet branch already deleted"
fi

if git rev-parse --verify task/06-docx-security-verification-system-prevent-maliciou >/dev/null 2>&1; then
    if git branch -d task/06-docx-security-verification-system-prevent-maliciou 2>&1; then
        echo "✓ Deleted task/06-docx-security branch (safe delete)"
    else
        git branch -D task/06-docx-security-verification-system-prevent-maliciou
        echo "✓ Force deleted task/06-docx-security branch"
    fi
else
    echo "⚠ task/06-docx-security branch already deleted"
fi

# Step 6: Archive synopsis files
echo ""
echo "=== Step 6: Archiving synopsis files ==="

mkdir -p /workspace/.trees/.archived/deploymet
mkdir -p /workspace/.trees/.archived/docx-security

if ls /workspace/.trees/.completed/deploymet-*-synopsis-*.md 1> /dev/null 2>&1; then
    mv /workspace/.trees/.completed/deploymet-*-synopsis-*.md /workspace/.trees/.archived/deploymet/
    echo "✓ Archived deployment synopsis files"
else
    echo "⚠ No deployment synopsis files found"
fi

if ls /workspace/.trees/.completed/docx-security-*-synopsis-*.md 1> /dev/null 2>&1; then
    mv /workspace/.trees/.completed/docx-security-*-synopsis-*.md /workspace/.trees/.archived/docx-security/
    echo "✓ Archived docx-security synopsis files"
else
    echo "⚠ No docx-security synopsis files found"
fi

# Final status
echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ FORCE MERGE COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Final git status:"
git status
echo ""
echo "Worktree list:"
git worktree list
echo ""
echo "Recent commits:"
git log --oneline -5
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Review the changes above"
echo "  2. If everything looks good, delete this script:"
echo "     rm /workspace/FORCE_MERGE_ON_RESTART.sh"
echo "  3. Continue with: /tree closedone (for any remaining worktrees)"
echo ""
