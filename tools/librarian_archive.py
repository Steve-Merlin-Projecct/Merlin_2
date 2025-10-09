#!/usr/bin/env python3
"""
Librarian Archive Tool: Automated archival of completed tasks

Intelligently archives completed tasks from /tasks to /docs/archived/tasks/
with confidence scoring and README generation.

Author: Claude Sonnet 4.5
Created: 2025-10-09
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from librarian_common import (
    extract_frontmatter,
    find_markdown_files,
    safe_read_file,
    logger
)


def calculate_confidence(file_path, metadata, content):
    """Calculate archival confidence score (0.0-1.0)."""
    confidence = 0.0
    reasons = []

    # Explicit status
    status = metadata.get('status', '').lower()
    if status == 'completed':
        confidence += 0.7
        reasons.append("Status: completed")
    elif status == 'archived':
        confidence += 0.9
        reasons.append("Status: archived")

    # Content markers
    if re.search(r'✅\s*(completed|complete)', content, re.IGNORECASE):
        confidence += 0.4
        reasons.append("Completion marker found")

    # Age check (rough heuristic)
    created = metadata.get('created', '')
    if created:
        try:
            created_date = datetime.strptime(created, '%Y-%m-%d')
            age_days = (datetime.now() - created_date).days
            if age_days > 90:
                confidence += 0.2
                reasons.append(f"Created {age_days} days ago")
        except:
            pass

    # Location heuristic
    if '/tasks/' in file_path and 'prd' in file_path.lower():
        if status in ['completed', 'archived']:
            confidence += 0.2
            reasons.append("Completed PRD in tasks")

    return confidence, reasons


def determine_archive_location(file_path, metadata):
    """Determine appropriate archive destination."""
    doc_type = metadata.get('type', '')
    feature_branch = metadata.get('feature_branch', '')

    # Extract feature name
    feature_name = None
    if feature_branch:
        feature_name = feature_branch.replace('feature/', '').replace('task/', '')
    else:
        # Try to extract from path
        path_parts = Path(file_path).parts
        if 'tasks' in path_parts:
            idx = path_parts.index('tasks')
            if idx + 1 < len(path_parts):
                feature_name = path_parts[idx + 1]

    if not feature_name:
        feature_name = Path(file_path).stem

    # Clean feature name
    feature_name = re.sub(r'^(prd-|tasks-|task-)', '', feature_name)

    if doc_type in ['prd', 'task'] or '/tasks/' in file_path.lower():
        return f"docs/archived/tasks/{feature_name}/"

    return "docs/archived/general/"


def create_archive_readme(archive_dir, files):
    """Generate README for archived files."""
    readme_path = Path(archive_dir) / 'README.md'

    if readme_path.exists():
        return  # Don't overwrite existing README

    feature_name = Path(archive_dir).name.replace('-', ' ').title()

    readme_content = f"""# Archive: {feature_name}

**Archived:** {datetime.now().strftime('%Y-%m-%d')}
**Original Location:** /tasks/
**Reason:** Completed work archived by librarian system

## Files in This Archive

"""

    for file_path in files:
        filename = Path(file_path).name
        metadata = extract_frontmatter(file_path)
        title = metadata.get('title', filename) if metadata else filename
        readme_content += f"- `{filename}` - {title}\n"

    readme_content += f"""

## Context

This archive contains completed work from the {feature_name} feature/task.
Files were automatically archived based on completion status and age.

For active documentation, see the main documentation directory.
"""

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    logger.info(f"Created README: {readme_path}")


def archive_file(file_path, destination, dry_run=False):
    """Archive a single file using git mv."""
    dest_path = Path(destination) / Path(file_path).name

    if dry_run:
        logger.info(f"[DRY RUN] Would move: {file_path} -> {dest_path}")
        return True

    # Create destination directory
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Use git mv to preserve history
    try:
        subprocess.run(['git', 'mv', file_path, str(dest_path)], check=True, capture_output=True)
        logger.info(f"Archived: {file_path} -> {dest_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to archive {file_path}: {e}")
        return False


def find_archival_candidates(root_dir='tasks/', min_confidence=0.7):
    """Find files that should be archived."""
    files = find_markdown_files(root_dir)
    candidates = []

    for file_path in files:
        metadata = extract_frontmatter(file_path)
        if not metadata:
            continue

        content = safe_read_file(file_path) or ''
        confidence, reasons = calculate_confidence(file_path, metadata, content)

        if confidence >= min_confidence:
            destination = determine_archive_location(file_path, metadata)
            candidates.append({
                'path': file_path,
                'confidence': confidence,
                'reasons': reasons,
                'destination': destination,
                'metadata': metadata
            })

    return sorted(candidates, key=lambda x: x['confidence'], reverse=True)


def main():
    parser = argparse.ArgumentParser(description='Librarian Archive Tool')

    parser.add_argument('--dry-run', action='store_true', help='Show what would be archived')
    parser.add_argument('--auto', action='store_true', help='Auto-archive high confidence files')
    parser.add_argument('--interactive', action='store_true', help='Prompt for each file')
    parser.add_argument('--min-confidence', type=float, default=0.7, help='Minimum confidence (0.0-1.0)')

    args = parser.parse_args()

    print("Finding archival candidates...")
    candidates = find_archival_candidates(min_confidence=args.min_confidence)

    if not candidates:
        print("✓ No files need archiving")
        return

    print(f"\nFound {len(candidates)} candidates for archival:\n")

    archived_count = 0
    skipped_count = 0

    # Group by destination
    by_dest = {}
    for candidate in candidates:
        dest = candidate['destination']
        if dest not in by_dest:
            by_dest[dest] = []
        by_dest[dest].append(candidate)

    for destination, files in by_dest.items():
        print(f"\n{destination}")
        print("-" * 60)

        for candidate in files:
            print(f"  {candidate['path']}")
            print(f"    Confidence: {candidate['confidence']:.2f}")
            print(f"    Reasons: {'; '.join(candidate['reasons'])}")

            if args.interactive and not args.dry_run:
                response = input("    Archive this file? [y/N]: ").strip().lower()
                if response != 'y':
                    skipped_count += 1
                    continue

            # Archive the file
            if archive_file(candidate['path'], destination, dry_run=args.dry_run):
                archived_count += 1
            else:
                skipped_count += 1

        # Create README if archiving
        if archived_count > 0 and not args.dry_run:
            file_paths = [c['path'] for c in files]
            create_archive_readme(destination, file_paths)

    print("\n" + "=" * 60)
    print(f"Archival Summary")
    print("=" * 60)
    print(f"Candidates found: {len(candidates)}")
    print(f"Archived: {archived_count}")
    print(f"Skipped: {skipped_count}")

    if args.dry_run:
        print("\n[DRY RUN] Run without --dry-run to archive files")


if __name__ == '__main__':
    main()
