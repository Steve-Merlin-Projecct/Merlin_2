#!/usr/bin/env python3
"""
Automated Archival Script

Purpose: Move stale files to archive automatically
Usage: python tools/auto_archive.py [--execute] [--days 180]
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import shutil

try:
    import click
    HAS_CLICK = True
except ImportError:
    import argparse
    HAS_CLICK = False


class AutoArchiver:
    """Automatically archives stale documentation"""

    def __init__(self, project_root: Path = None, days_threshold: int = 180):
        """
        Initialize auto archiver

        Args:
            project_root: Project root directory
            days_threshold: Age threshold in days (default: 180)
        """
        if project_root is None:
            self.project_root = self._find_project_root()
        else:
            self.project_root = Path(project_root).resolve()

        self.days_threshold = days_threshold
        self.skip_dirs = ['node_modules', '.git', 'venv', 'project_venv', '__pycache__']

    def _find_project_root(self) -> Path:
        """Find project root"""
        current = Path.cwd()

        while current != current.parent:
            if (current / '.git').exists() or (current / 'CLAUDE.md').exists():
                return current
            current = current.parent

        return Path.cwd()

    def find_candidates(self) -> List[Tuple[Path, str]]:
        """
        Find files that are candidates for archival

        Returns:
            List of (file_path, reason) tuples
        """
        candidates = []
        cutoff_date = datetime.now() - timedelta(days=self.days_threshold)
        cutoff_timestamp = cutoff_date.timestamp()

        # Find all markdown files
        md_files = list(self.project_root.rglob('*.md'))

        for md_file in md_files:
            # Skip if already archived
            if 'archived' in md_file.parts or 'archive' in md_file.parts:
                continue

            # Skip essential files
            if md_file.name in ['README.md', 'CLAUDE.md', 'CHANGELOG.md']:
                continue

            # Skip if in skip directories
            if any(skip_dir in md_file.parts for skip_dir in self.skip_dirs):
                continue

            # Check last modified date
            try:
                mtime = md_file.stat().st_mtime

                if mtime < cutoff_timestamp:
                    # Check if file is referenced elsewhere
                    if not self._is_referenced(md_file):
                        age_days = (datetime.now().timestamp() - mtime) / 86400
                        reason = f"Not modified in {int(age_days)} days and not referenced"
                        candidates.append((md_file, reason))
            except Exception as e:
                print(f"Warning: Could not check {md_file}: {e}", file=sys.stderr)

        return candidates

    def _is_referenced(self, file_path: Path) -> bool:
        """
        Check if file is referenced in other documents

        Args:
            file_path: File to check for references

        Returns:
            True if file is referenced elsewhere
        """
        # Get relative path
        try:
            rel_path = file_path.relative_to(self.project_root)
            rel_path_str = str(rel_path)
        except ValueError:
            return False

        # Search for references in all markdown files
        md_files = list(self.project_root.rglob('*.md'))

        for md_file in md_files:
            # Skip the file itself
            if md_file == file_path:
                continue

            # Skip if already archived
            if 'archived' in md_file.parts:
                continue

            # Skip if in skip directories
            if any(skip_dir in md_file.parts for skip_dir in self.skip_dirs):
                continue

            try:
                content = md_file.read_text(encoding='utf-8')

                # Check for various link patterns
                patterns = [
                    re.escape(rel_path_str),  # Direct path
                    re.escape(file_path.name),  # Just filename
                    re.escape(str(rel_path).replace('\\', '/')),  # Unix-style path
                ]

                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True

            except Exception:
                continue

        return False

    def compute_archive_path(self, file_path: Path) -> Path:
        """
        Compute appropriate archive path for a file

        Args:
            file_path: Original file path

        Returns:
            Archive destination path
        """
        # Get relative path
        try:
            rel_path = file_path.relative_to(self.project_root)
        except ValueError:
            # File is outside project root
            return self.project_root / 'docs' / 'archived' / file_path.name

        # Determine archive location based on current location
        parts = list(rel_path.parts)

        # If already in docs/, move to docs/archived/
        if parts[0] == 'docs':
            archive_base = self.project_root / 'docs' / 'archived'

            # Preserve subdirectory structure if meaningful
            if len(parts) > 2:
                # Keep intermediate directories
                archive_path = archive_base / Path(*parts[1:])
            else:
                archive_path = archive_base / file_path.name
        else:
            # For files outside docs/, move to docs/archived/
            archive_path = self.project_root / 'docs' / 'archived' / file_path.name

        return archive_path

    def archive_files(self, dry_run: bool = True) -> Tuple[int, int]:
        """
        Archive stale files

        Args:
            dry_run: If True, only show what would be archived

        Returns:
            Tuple of (archived_count, error_count)
        """
        candidates = self.find_candidates()

        if not candidates:
            print(f"No files found for archival (threshold: {self.days_threshold} days)")
            return 0, 0

        archived_count = 0
        error_count = 0

        if dry_run:
            print(f"DRY RUN: Would archive {len(candidates)} files")
            print(f"(Threshold: {self.days_threshold} days)\n")
        else:
            print(f"Archiving {len(candidates)} files...")
            print(f"(Threshold: {self.days_threshold} days)\n")

        for file_path, reason in candidates:
            archive_path = self.compute_archive_path(file_path)

            if dry_run:
                print(f"Would archive:")
                print(f"  From: {file_path.relative_to(self.project_root)}")
                print(f"  To:   {archive_path.relative_to(self.project_root)}")
                print(f"  Reason: {reason}")
                print()
                archived_count += 1
            else:
                try:
                    # Create archive directory
                    archive_path.parent.mkdir(parents=True, exist_ok=True)

                    # Move file
                    shutil.move(str(file_path), str(archive_path))

                    print(f"✓ Archived: {file_path.relative_to(self.project_root)}")
                    print(f"  → {archive_path.relative_to(self.project_root)}")
                    print()

                    archived_count += 1

                except Exception as e:
                    print(f"✗ Error archiving {file_path}: {e}", file=sys.stderr)
                    error_count += 1

        return archived_count, error_count


# CLI Implementation
if HAS_CLICK:
    @click.command()
    @click.option('--execute', is_flag=True, help='Actually move files (default is dry-run)')
    @click.option('--days', default=180, type=int, help='Age threshold in days (default: 180)')
    @click.option('--project-root', type=click.Path(exists=True), help='Project root directory')
    def main(execute: bool, days: int, project_root: str):
        """Archive stale documentation files"""

        root = Path(project_root) if project_root else None

        archiver = AutoArchiver(root, days_threshold=days)

        archived, errors = archiver.archive_files(dry_run=not execute)

        print("=" * 60)

        if not execute:
            print(f"DRY RUN COMPLETE")
            print(f"Would archive: {archived} files")
            print()
            print("To actually archive these files, run with --execute flag:")
            print(f"  python tools/auto_archive.py --execute --days {days}")
        else:
            print(f"ARCHIVAL COMPLETE")
            print(f"Archived: {archived} files")

            if errors > 0:
                print(f"Errors: {errors} files")
                sys.exit(1)

        sys.exit(0)

else:
    def main():
        parser = argparse.ArgumentParser(description='Archive stale documentation')
        parser.add_argument('--execute', action='store_true', help='Actually move files')
        parser.add_argument('--days', type=int, default=180, help='Age threshold in days')
        parser.add_argument('--project-root', help='Project root directory')

        args = parser.parse_args()

        root = Path(args.project_root) if args.project_root else None

        archiver = AutoArchiver(root, days_threshold=args.days)

        archived, errors = archiver.archive_files(dry_run=not args.execute)

        print("=" * 60)

        if not args.execute:
            print(f"DRY RUN COMPLETE")
            print(f"Would archive: {archived} files")
            print()
            print("To actually archive these files, run with --execute flag:")
            print(f"  python tools/auto_archive.py --execute --days {args.days}")
        else:
            print(f"ARCHIVAL COMPLETE")
            print(f"Archived: {archived} files")

            if errors > 0:
                print(f"Errors: {errors} files")
                sys.exit(1)

        sys.exit(0)


if __name__ == '__main__':
    main()
