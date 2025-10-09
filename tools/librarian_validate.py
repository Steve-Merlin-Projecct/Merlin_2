#!/usr/bin/env python3
"""
Librarian Validation Tool: Validate file organization and metadata

This tool validates documentation metadata completeness, file naming conventions,
file placement according to standards, and detects broken internal links.

Metadata:
    Type: tool
    Status: active
    Dependencies: PyYAML, librarian_common
    Related: tools/librarian_common.py, docs/standards/metadata-standard.md

Author: Claude Sonnet 4.5
Created: 2025-10-09
Updated: 2025-10-09

Usage:
    # Validate all documentation
    python tools/librarian_validate.py

    # Validate specific file
    python tools/librarian_validate.py docs/guide.md

    # Show errors only
    python tools/librarian_validate.py --errors-only

    # Auto-fix simple issues
    python tools/librarian_validate.py --fix
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))

from librarian_common import (
    extract_frontmatter,
    find_markdown_files,
    extract_markdown_links,
    resolve_link_path,
    logger
)


# Valid enum values
VALID_TYPES = [
    'standards', 'guide', 'prd', 'task', 'reference', 'api',
    'architecture', 'decision', 'process', 'changelog', 'audit', 'template'
]

VALID_STATUSES = ['draft', 'active', 'stable', 'deprecated', 'archived', 'completed']


def validate_metadata_completeness(file_path: str, metadata: Dict) -> Tuple[List[str], List[str]]:
    """Validate metadata has required fields."""
    errors = []
    warnings = []

    required = ['title', 'type', 'status', 'created']
    for field in required:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")

    recommended = ['version', 'updated', 'author', 'tags']
    missing_recommended = [f for f in recommended if f not in metadata]
    if missing_recommended:
        warnings.append(f"Missing recommended fields: {', '.join(missing_recommended)}")

    # Type validation
    if 'type' in metadata and metadata['type'] not in VALID_TYPES:
        errors.append(f"Invalid type '{metadata['type']}' (valid: {', '.join(VALID_TYPES)})")

    # Status validation
    if 'status' in metadata and metadata['status'] not in VALID_STATUSES:
        errors.append(f"Invalid status '{metadata['status']}' (valid: {', '.join(VALID_STATUSES)})")

    # Date format validation
    for date_field in ['created', 'updated', 'review_date']:
        if date_field in metadata:
            if not re.match(r'\d{4}-\d{2}-\d{2}', str(metadata[date_field])):
                errors.append(f"Invalid date format for {date_field} (expected YYYY-MM-DD)")

    # Tag validation
    if 'tags' in metadata:
        if not isinstance(metadata['tags'], list):
            errors.append("Tags must be a list")
        else:
            for tag in metadata['tags']:
                if not re.match(r'^[a-z0-9-]+$', str(tag)):
                    warnings.append(f"Tag should be lowercase with hyphens: '{tag}'")

    return errors, warnings


def validate_file_naming(file_path: str) -> List[str]:
    """Validate file follows naming conventions."""
    warnings = []

    filename = Path(file_path).name

    # Skip certain files
    if filename in ['README.md', 'CLAUDE.md', 'CHANGELOG.md']:
        return warnings

    # Check for lowercase-with-hyphens
    if not re.match(r'^[a-z0-9-]+\.md$', filename):
        warnings.append(f"Filename should be lowercase-with-hyphens: '{filename}'")

    return warnings


def validate_file_placement(file_path: str, metadata: Dict) -> List[str]:
    """Validate file is in correct directory."""
    warnings = []

    path_lower = file_path.lower()

    # Check status vs location consistency
    status = metadata.get('status', '')
    if status == 'archived' and '/archived/' not in path_lower:
        warnings.append(f"Status is 'archived' but file not in /archived/ directory")

    if status == 'completed' and '/tasks/' in path_lower and '/archived/' not in path_lower:
        warnings.append(f"Status is 'completed' but task still in /tasks/ (should be archived)")

    # Check type vs location
    doc_type = metadata.get('type', '')
    if doc_type == 'prd' and '/tasks/' not in path_lower and '/archived/' not in path_lower:
        warnings.append(f"Type is 'prd' but not in /tasks/ or /archived/tasks/")

    return warnings


def validate_broken_links(file_path: str) -> List[str]:
    """Check for broken internal links."""
    errors = []

    links = extract_markdown_links(file_path)

    for link_text, link_url in links:
        resolved_path = resolve_link_path(file_path, link_url)

        if resolved_path and not Path(resolved_path).exists():
            errors.append(f"Broken link: [{link_text}]({link_url}) -> {resolved_path}")

    return errors


def validate_file(file_path: str) -> Dict:
    """Validate a single file."""
    result = {
        'file': file_path,
        'errors': [],
        'warnings': [],
        'has_frontmatter': False
    }

    # Check for frontmatter
    metadata = extract_frontmatter(file_path)

    if metadata:
        result['has_frontmatter'] = True

        # Validate metadata
        meta_errors, meta_warnings = validate_metadata_completeness(file_path, metadata)
        result['errors'].extend(meta_errors)
        result['warnings'].extend(meta_warnings)

        # Validate file placement
        placement_warnings = validate_file_placement(file_path, metadata)
        result['warnings'].extend(placement_warnings)
    else:
        result['errors'].append("Missing YAML frontmatter")

    # Validate file naming
    naming_warnings = validate_file_naming(file_path)
    result['warnings'].extend(naming_warnings)

    # Validate links
    link_errors = validate_broken_links(file_path)
    result['errors'].extend(link_errors)

    return result


def main():
    parser = argparse.ArgumentParser(description='Librarian Validation Tool')

    parser.add_argument(
        'files',
        nargs='*',
        help='Specific files to validate (default: all markdown files)'
    )

    parser.add_argument(
        '--errors-only',
        action='store_true',
        help='Show only errors, not warnings'
    )

    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary only'
    )

    parser.add_argument(
        '--fix',
        action='store_true',
        help='Auto-fix simple issues (not implemented yet)'
    )

    args = parser.parse_args()

    # Get files to validate
    if args.files:
        files = args.files
    else:
        files = find_markdown_files('.')

    # Validate all files
    results = []
    for file_path in files:
        try:
            result = validate_file(file_path)
            results.append(result)
        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")

    # Calculate statistics
    total_files = len(results)
    files_with_errors = sum(1 for r in results if r['errors'])
    files_with_warnings = sum(1 for r in results if r['warnings'])
    total_errors = sum(len(r['errors']) for r in results)
    total_warnings = sum(len(r['warnings']) for r in results)

    # Print results
    if not args.summary:
        for result in results:
            if result['errors'] or (result['warnings'] and not args.errors_only):
                print(f"\n{result['file']}")
                print("-" * 60)

                for error in result['errors']:
                    print(f"  ✗ {error}")

                if not args.errors_only:
                    for warning in result['warnings']:
                        print(f"  ⚠ {warning}")

    # Print summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    print(f"Files validated:     {total_files}")
    print(f"Files with errors:   {files_with_errors}")
    print(f"Files with warnings: {files_with_warnings}")
    print(f"Total errors:        {total_errors}")
    print(f"Total warnings:      {total_warnings}")

    # Exit code
    if total_errors > 0:
        sys.exit(2)  # Errors (blocking)
    elif total_warnings > 0:
        sys.exit(1)  # Warnings (non-blocking)
    else:
        sys.exit(0)  # Success


if __name__ == '__main__':
    main()
