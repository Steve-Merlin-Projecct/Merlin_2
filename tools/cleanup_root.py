#!/usr/bin/env python3
"""
Root Directory Cleanup Script

Purpose: Move files from root to appropriate locations based on FILE_ORGANIZATION_STANDARDS.md
Usage: python tools/cleanup_root.py [--execute]
"""

import sys
from pathlib import Path
import shutil

# File mapping: source -> destination
FILE_MOVES = {
    # Scripts
    'FORCE_MERGE_ON_RESTART.sh': 'scripts/FORCE_MERGE_ON_RESTART.sh',
    'run_dashboard_migrations.py': 'scripts/run_dashboard_migrations.py',
    'start_dashboard.sh': 'scripts/start_dashboard.sh',
    'dashboard_standalone.py': 'scripts/dashboard_standalone.py',
    'worktree-status.sh': 'scripts/worktree-status.sh',
    'add-claude-context.sh': 'scripts/add-claude-context.sh',
    'force-merge.sh': 'scripts/force-merge.sh',
    'open-terminals.sh': 'scripts/open-terminals.sh',
    'sync-all-worktrees.sh': 'scripts/sync-all-worktrees.sh',
    'create-worktree-batch.sh': 'scripts/create-worktree-batch.sh',
    'monitor-resources.sh': 'scripts/monitor-resources.sh',

    # Documentation
    'FILES_SUMMARY.md': 'docs/FILES_SUMMARY.md',
    'README-RATE-LIMITING.md': 'docs/README-RATE-LIMITING.md',
    'START_HERE.md': 'docs/START_HERE.md',
    'LIBRARIAN_HANDOFF.md': 'docs/LIBRARIAN_HANDOFF.md',
    'DASHBOARD_V2_HANDOFF.md': 'docs/DASHBOARD_V2_HANDOFF.md',
    'README_DASHBOARD_V2.md': 'docs/README_DASHBOARD_V2.md',
    'WORKTREE_NAMES.md': 'docs/WORKTREE_NAMES.md',
    'QUICK_START.md': 'docs/QUICK_START.md',
    'STARTUP_WARNINGS.md': 'docs/STARTUP_WARNINGS.md',
    'RATE_LIMITING_DEPLOYMENT_GUIDE.md': 'docs/deployment/RATE_LIMITING_DEPLOYMENT_GUIDE.md',

    # Testing
    'TESTING_SUMMARY.md': 'docs/testing/TESTING_SUMMARY.md',
    'SYSTEM_TEST_REPORT.md': 'docs/testing/SYSTEM_TEST_REPORT.md',
    'test_sentence_variation.py': 'tests/unit/test_sentence_variation.py',
    'test_results_end_to_end_workflow.json': 'docs/testing/test_results_end_to_end_workflow.json',
    'system_verification_results.json': 'docs/testing/system_verification_results.json',

    # Git workflow / Branch status
    'BRANCH_STATUS.md': 'docs/git_workflow/branch-status/BRANCH_STATUS.md',
    'COMPLETION_SUMMARY.md': 'docs/git_workflow/branch-status/COMPLETION_SUMMARY.md',
    'IMPLEMENTATION_COMPLETE.md': 'docs/git_workflow/branch-status/IMPLEMENTATION_COMPLETE.md',
    'TASK_COMPLETION_SUMMARY.md': 'docs/git_workflow/branch-status/TASK_COMPLETION_SUMMARY.md',
    'TIER1_IMPLEMENTATION_COMPLETE.md': 'docs/git_workflow/branch-status/TIER1_IMPLEMENTATION_COMPLETE.md',
    'MERGE_CHECKLIST.md': 'docs/git_workflow/MERGE_CHECKLIST.md',
    'DEPLOYMENT_CHECKLIST.md': 'docs/deployment/DEPLOYMENT_CHECKLIST.md',

    # Implementation summaries (archive)
    'IMPLEMENTATION_SUMMARY.md': 'docs/archived/IMPLEMENTATION_SUMMARY.md',
    'IMPLEMENTATION_PROGRESS.md': 'docs/archived/IMPLEMENTATION_PROGRESS.md',
    'IMPLEMENTATION_SUMMARY_RATE_LIMITING.md': 'docs/archived/IMPLEMENTATION_SUMMARY_RATE_LIMITING.md',

    # Future tasks
    'TODO.md': 'docs/future-tasks/TODO.md',
    'FUTURE_TASKS_RATE_LIMITING.md': 'docs/future-tasks/FUTURE_TASKS_RATE_LIMITING.md',

    # Ignore/special files (move to appropriate locations or document why they stay)
    'worktrees.code-workspace': 'worktrees.code-workspace',  # VS Code workspace, stays in root
    'uv.lock': 'uv.lock',  # Python UV lock file, stays in root
    'cookies.txt': None,  # Should be gitignored, don't move
}


def cleanup_root(project_root: Path, dry_run: bool = True) -> tuple:
    """
    Clean up root directory by moving files

    Args:
        project_root: Project root directory
        dry_run: If True, only show what would be done

    Returns:
        Tuple of (moved_count, error_count, skipped_count)
    """
    moved_count = 0
    error_count = 0
    skipped_count = 0

    if dry_run:
        print("DRY RUN: Would move the following files:\n")
    else:
        print("Moving files to correct locations...\n")

    for source_name, dest_rel_path in FILE_MOVES.items():
        source_path = project_root / source_name

        # Skip if file doesn't exist
        if not source_path.exists():
            skipped_count += 1
            continue

        # Skip if dest is None (e.g., cookies.txt)
        if dest_rel_path is None:
            print(f"Skipping: {source_name} (should be gitignored)")
            skipped_count += 1
            continue

        # Skip if no move needed (stays in root)
        if dest_rel_path == source_name:
            print(f"Keeping in root: {source_name}")
            skipped_count += 1
            continue

        dest_path = project_root / dest_rel_path

        if dry_run:
            print(f"Would move:")
            print(f"  From: {source_name}")
            print(f"  To:   {dest_rel_path}")
            print()
            moved_count += 1
        else:
            try:
                # Create destination directory
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Move file
                shutil.move(str(source_path), str(dest_path))

                print(f"✓ Moved: {source_name}")
                print(f"  → {dest_rel_path}")
                print()

                moved_count += 1

            except Exception as e:
                print(f"✗ Error moving {source_name}: {e}", file=sys.stderr)
                print()
                error_count += 1

    return moved_count, error_count, skipped_count


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clean up root directory')
    parser.add_argument('--execute', action='store_true', help='Actually move files (default is dry-run)')
    args = parser.parse_args()

    project_root = Path.cwd()

    moved, errors, skipped = cleanup_root(project_root, dry_run=not args.execute)

    print("=" * 60)

    if not args.execute:
        print("DRY RUN COMPLETE")
        print(f"Would move: {moved} files")
        print(f"Would skip: {skipped} files")
        print()
        print("To actually move these files, run with --execute flag:")
        print("  python tools/cleanup_root.py --execute")
    else:
        print("CLEANUP COMPLETE")
        print(f"Moved: {moved} files")
        print(f"Skipped: {skipped} files")

        if errors > 0:
            print(f"Errors: {errors} files")
            sys.exit(1)

    sys.exit(0)
