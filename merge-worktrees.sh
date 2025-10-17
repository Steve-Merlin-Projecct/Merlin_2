#!/bin/bash

for branch in task/05-user-preferences task/06-librarian-improvements task/07-dashboard-completion task/08-task-slash-command-refinement task/11-complete-calendly-integration---connect-link-track; do
    echo "==== Merging $branch ===="
    commits=$(git log --oneline "$branch" --not develop/v4.3.2-worktrees-20251012-044136 2>/dev/null | wc -l)
    echo "Commits to merge: $commits"

    if [ "$commits" -gt 0 ]; then
        rm -f /workspace/.git/index.lock
        if git merge --no-ff "$branch" -m "chore: Merge ${branch##*/} worktree" 2>&1 | tee /tmp/merge-output.txt; then
            echo "✓ Merged successfully"
        else
            if grep -q "CONFLICT" /tmp/merge-output.txt; then
                echo "⚠ Conflicts detected - using ours strategy"
                git checkout --ours .claude-init.sh .claude-task-context.md .claude/scripts/tree.sh PURPOSE.md 2>/dev/null
                git add .
                git commit -m "chore: Merge ${branch##*/} worktree (conflicts resolved with ours)"
            else
                echo "✗ Merge failed"
                git merge --abort 2>/dev/null
            fi
        fi
    else
        echo "→ No commits to merge"
    fi
    echo ""
done
