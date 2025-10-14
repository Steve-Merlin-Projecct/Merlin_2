#!/usr/bin/env python3
"""
Link Validation Script

Purpose: Find broken internal links in markdown files
Usage: python tools/validate_links.py <file_path> [--all] [--json]
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, unquote

try:
    import click
    HAS_CLICK = True
except ImportError:
    import argparse
    HAS_CLICK = False


@dataclass
class BrokenLink:
    """Represents a broken link"""
    source_file: str
    link_text: str
    link_target: str
    line_number: int
    reason: str

    def __str__(self) -> str:
        return (
            f"{self.source_file}:{self.line_number}\n"
            f"  Link: [{self.link_text}]({self.link_target})\n"
            f"  Reason: {self.reason}"
        )


@dataclass
class ValidationResult:
    """Result of link validation"""
    file_path: str
    total_links: int
    broken_links: List[BrokenLink]
    valid: bool

    def __str__(self) -> str:
        if self.valid:
            return f"✓ {self.file_path}: {self.total_links} links checked, all valid"

        output = [
            f"✗ {self.file_path}: {len(self.broken_links)} broken out of {self.total_links} links",
            ""
        ]

        for broken in self.broken_links:
            output.append(f"  Line {broken.line_number}:")
            output.append(f"    [{broken.link_text}]({broken.link_target})")
            output.append(f"    → {broken.reason}")
            output.append("")

        return "\n".join(output)


class LinkValidator:
    """Validates internal links in markdown files"""

    # Pattern to match markdown links: [text](url)
    LINK_PATTERN = r'\[([^\]]+)\]\(([^)]+)\)'

    # External URL schemes to skip
    EXTERNAL_SCHEMES = ['http', 'https', 'mailto', 'ftp', 'tel']

    def __init__(self, file_path: Path, project_root: Path = None):
        """
        Initialize link validator

        Args:
            file_path: Path to markdown file to validate
            project_root: Project root directory (default: auto-detect)
        """
        self.file_path = Path(file_path).resolve()

        if project_root is None:
            self.project_root = self._find_project_root()
        else:
            self.project_root = Path(project_root).resolve()

        self.broken_links: List[BrokenLink] = []
        self.total_links = 0

    def _find_project_root(self) -> Path:
        """Find project root by looking for .git or CLAUDE.md"""
        current = self.file_path.parent

        while current != current.parent:
            if (current / '.git').exists() or (current / 'CLAUDE.md').exists():
                return current
            current = current.parent

        return Path.cwd()

    def validate(self) -> ValidationResult:
        """
        Validate all links in the markdown file

        Returns:
            ValidationResult with broken links
        """
        self.broken_links = []
        self.total_links = 0

        # Check file exists
        if not self.file_path.exists():
            return ValidationResult(
                file_path=str(self.file_path),
                total_links=0,
                broken_links=[
                    BrokenLink(
                        source_file=str(self.file_path),
                        link_text="",
                        link_target="",
                        line_number=0,
                        reason=f"File not found: {self.file_path}"
                    )
                ],
                valid=False
            )

        # Read file content
        try:
            content = self.file_path.read_text(encoding='utf-8')
        except Exception as e:
            return ValidationResult(
                file_path=str(self.file_path),
                total_links=0,
                broken_links=[
                    BrokenLink(
                        source_file=str(self.file_path),
                        link_text="",
                        link_target="",
                        line_number=0,
                        reason=f"Failed to read file: {e}"
                    )
                ],
                valid=False
            )

        # Split into lines for line number tracking
        lines = content.split('\n')

        # Extract and validate all links
        for line_num, line in enumerate(lines, start=1):
            self._check_links_in_line(line, line_num)

        return ValidationResult(
            file_path=str(self.file_path),
            total_links=self.total_links,
            broken_links=self.broken_links,
            valid=len(self.broken_links) == 0
        )

    def _check_links_in_line(self, line: str, line_number: int) -> None:
        """Check all links in a single line"""
        matches = re.finditer(self.LINK_PATTERN, line)

        for match in matches:
            link_text = match.group(1)
            link_target = match.group(2)

            self.total_links += 1

            # Skip external links
            if self._is_external_link(link_target):
                continue

            # Skip anchors (same-page links)
            if link_target.startswith('#'):
                continue

            # Validate internal link
            self._validate_internal_link(link_text, link_target, line_number)

    def _is_external_link(self, link_target: str) -> bool:
        """Check if link is external (http, https, mailto, etc.)"""
        parsed = urlparse(link_target)
        return parsed.scheme in self.EXTERNAL_SCHEMES

    def _validate_internal_link(self, link_text: str, link_target: str, line_number: int) -> None:
        """
        Validate an internal link

        Args:
            link_text: Display text of the link
            link_target: Target URL/path
            line_number: Line number where link appears
        """
        # Remove anchor if present
        if '#' in link_target:
            link_target = link_target.split('#')[0]

        # Skip empty targets (pure anchors)
        if not link_target:
            return

        # URL decode the target
        link_target = unquote(link_target)

        # Resolve the target path
        target_path = self._resolve_link_target(link_target)

        # Check if target exists
        if target_path is None:
            self.broken_links.append(
                BrokenLink(
                    source_file=str(self.file_path),
                    link_text=link_text,
                    link_target=link_target,
                    line_number=line_number,
                    reason="Target file not found"
                )
            )
        elif not target_path.exists():
            self.broken_links.append(
                BrokenLink(
                    source_file=str(self.file_path),
                    link_text=link_text,
                    link_target=link_target,
                    line_number=line_number,
                    reason=f"Target does not exist: {target_path}"
                )
            )

    def _resolve_link_target(self, link_target: str) -> Optional[Path]:
        """
        Resolve link target to absolute path

        Args:
            link_target: Relative or absolute link target

        Returns:
            Resolved Path or None if cannot resolve
        """
        # Handle absolute paths (starting with /)
        if link_target.startswith('/'):
            # Treat as relative to project root
            target = self.project_root / link_target.lstrip('/')
            return target.resolve()

        # Handle relative paths
        try:
            target = (self.file_path.parent / link_target).resolve()
            return target
        except Exception:
            return None


def validate_file(file_path: Path, project_root: Path = None) -> ValidationResult:
    """
    Validate links in a single markdown file

    Args:
        file_path: Path to markdown file
        project_root: Project root directory

    Returns:
        ValidationResult
    """
    validator = LinkValidator(file_path, project_root)
    return validator.validate()


def validate_all(project_root: Path = None, json_output: bool = False) -> Tuple[int, int, List[BrokenLink]]:
    """
    Validate links in all markdown files

    Args:
        project_root: Project root directory
        json_output: If True, output JSON format

    Returns:
        Tuple of (valid_count, invalid_count, all_broken_links)
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    valid_count = 0
    invalid_count = 0
    all_broken_links: List[BrokenLink] = []

    # Find all markdown files
    md_files = list(project_root.rglob('*.md'))

    if not json_output:
        print(f"Scanning {len(md_files)} markdown files...\n")

    # Skip certain directories
    skip_dirs = ['node_modules', '.git', 'venv', 'project_venv', '__pycache__', 'archived_files']

    for md_file in md_files:
        if any(skip_dir in md_file.parts for skip_dir in skip_dirs):
            continue

        result = validate_file(md_file, project_root)

        if result.valid:
            valid_count += 1
        else:
            invalid_count += 1
            all_broken_links.extend(result.broken_links)

            if not json_output:
                print(result)
                print()

    return valid_count, invalid_count, all_broken_links


# CLI Implementation
if HAS_CLICK:
    @click.command()
    @click.argument('file_path', type=click.Path(exists=True), required=False)
    @click.option('--all', 'validate_all_files', is_flag=True, help='Validate all markdown files')
    @click.option('--json', 'json_output', is_flag=True, help='Output results as JSON')
    @click.option('--project-root', type=click.Path(exists=True), help='Project root directory')
    def main(file_path: Optional[str], validate_all_files: bool, json_output: bool, project_root: Optional[str]):
        """Validate internal links in markdown files"""

        root = Path(project_root) if project_root else None

        if validate_all_files:
            valid, invalid, broken_links = validate_all(root, json_output)

            if json_output:
                output = {
                    'valid_files': valid,
                    'invalid_files': invalid,
                    'total_broken_links': len(broken_links),
                    'broken_links': [asdict(link) for link in broken_links]
                }
                print(json.dumps(output, indent=2))
            else:
                print(f"{'='*60}")
                print(f"Results: {valid} files valid, {invalid} files with broken links")
                print(f"Total broken links: {len(broken_links)}")

            sys.exit(0 if invalid == 0 else 1)

        elif file_path:
            result = validate_file(Path(file_path), root)

            if json_output:
                output = {
                    'file_path': result.file_path,
                    'total_links': result.total_links,
                    'valid': result.valid,
                    'broken_links': [asdict(link) for link in result.broken_links]
                }
                print(json.dumps(output, indent=2))
            else:
                print(result)

            sys.exit(0 if result.valid else 1)

        else:
            print("Error: Must provide FILE_PATH or use --all flag")
            sys.exit(1)

else:
    def main():
        parser = argparse.ArgumentParser(description='Validate internal links in markdown files')
        parser.add_argument('file_path', nargs='?', help='Path to markdown file')
        parser.add_argument('--all', action='store_true', help='Validate all markdown files')
        parser.add_argument('--json', action='store_true', help='Output JSON format')
        parser.add_argument('--project-root', help='Project root directory')

        args = parser.parse_args()

        root = Path(args.project_root) if args.project_root else None

        if args.all:
            valid, invalid, broken_links = validate_all(root, args.json)

            if args.json:
                output = {
                    'valid_files': valid,
                    'invalid_files': invalid,
                    'total_broken_links': len(broken_links),
                    'broken_links': [asdict(link) for link in broken_links]
                }
                print(json.dumps(output, indent=2))
            else:
                print(f"{'='*60}")
                print(f"Results: {valid} files valid, {invalid} files with broken links")
                print(f"Total broken links: {len(broken_links)}")

            sys.exit(0 if invalid == 0 else 1)

        elif args.file_path:
            result = validate_file(Path(args.file_path), root)

            if args.json:
                output = {
                    'file_path': result.file_path,
                    'total_links': result.total_links,
                    'valid': result.valid,
                    'broken_links': [asdict(link) for link in result.broken_links]
                }
                print(json.dumps(output, indent=2))
            else:
                print(result)

            sys.exit(0 if result.valid else 1)

        else:
            parser.print_help()
            sys.exit(1)


if __name__ == '__main__':
    main()
