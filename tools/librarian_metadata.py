#!/usr/bin/env python3
"""
Librarian Metadata Tool: Extract, generate, and standardize documentation metadata

This tool extracts metadata from existing documentation patterns (Pattern A/B/C),
generates missing metadata from git history and file analysis, and standardizes
all documentation to use YAML frontmatter format.

Metadata:
    Type: tool
    Status: active
    Dependencies: PyYAML, librarian_common
    Related: tools/librarian_common.py, docs/standards/metadata-standard.md

Author: Claude Sonnet 4.5
Created: 2025-10-09
Updated: 2025-10-09

Usage:
    # Scan metadata coverage
    python tools/librarian_metadata.py --scan

    # Extract from specific file
    python tools/librarian_metadata.py --extract docs/guide.md

    # Generate missing metadata
    python tools/librarian_metadata.py --generate docs/guide.md

    # Batch process all files
    python tools/librarian_metadata.py --batch

    # Interactive enhancement
    python tools/librarian_metadata.py --enhance docs/guide.md --interactive
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from librarian_common import (
    extract_frontmatter,
    insert_frontmatter,
    has_frontmatter,
    get_git_created_date,
    get_git_updated_date,
    get_git_primary_author,
    find_markdown_files,
    safe_read_file,
    infer_document_type_from_path,
    detect_status_from_content,
    logger
)


# =============================================================================
# Pattern Extractors
# =============================================================================

def extract_pattern_a(content: str) -> Dict[str, Any]:
    """
    Extract metadata from Pattern A (Structured PRD/Task headers).

    Pattern A Example:
        # PRD: Feature Name
        **Status:** ✅ COMPLETED
        **Priority:** High
        **Version:** 1.0.0
        **Created:** October 8, 2025

    Args:
        content: File content

    Returns:
        Dictionary of extracted metadata
    """
    metadata = {}

    # Extract title from first heading
    title_match = re.search(r'^#\s+(?:PRD:\s*)?(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()

    # Extract status
    status_match = re.search(r'\*\*Status\*\*:\s*(?:✅|❌|⚠️)?\s*(\w+)', content, re.IGNORECASE)
    if status_match:
        status = status_match.group(1).lower()
        # Map common values
        status_map = {
            'completed': 'completed',
            'complete': 'completed',
            'active': 'active',
            'draft': 'draft',
            'deprecated': 'deprecated',
            'archived': 'archived'
        }
        metadata['status'] = status_map.get(status, status)

    # Extract priority
    priority_match = re.search(r'\*\*Priority\*\*:\s*(\w+)', content, re.IGNORECASE)
    if priority_match:
        # Store as tag
        priority = priority_match.group(1).lower()
        if 'tags' not in metadata:
            metadata['tags'] = []
        metadata['tags'].append(f'priority-{priority}')

    # Extract version
    version_match = re.search(r'\*\*Version\*\*:\s*([\d.]+)', content, re.IGNORECASE)
    if version_match:
        metadata['version'] = version_match.group(1)

    # Extract created date
    created_match = re.search(
        r'\*\*Created\*\*:\s*(\w+\s+\d{1,2},?\s+\d{4})',
        content,
        re.IGNORECASE
    )
    if created_match:
        date_str = created_match.group(1)
        metadata['created'] = parse_date_string(date_str)

    # Extract feature branch
    branch_match = re.search(
        r'\*\*Feature Branch\*\*:\s*`?([^`\n]+)`?',
        content,
        re.IGNORECASE
    )
    if branch_match:
        metadata['feature_branch'] = branch_match.group(1).strip()

    return metadata


def extract_pattern_b(content: str) -> Dict[str, Any]:
    """
    Extract metadata from Pattern B (Technical documentation headers).

    Pattern B Example:
        # Component Name
        **Purpose:** Brief description
        **Version:** 2.0
        **Last Updated:** 2025-09-15

    Args:
        content: File content

    Returns:
        Dictionary of extracted metadata
    """
    metadata = {}

    # Extract title from first heading
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()

    # Extract purpose (can be used as description)
    purpose_match = re.search(r'\*\*Purpose\*\*:\s*(.+)', content, re.IGNORECASE)
    if purpose_match:
        # Store purpose in a comment or as a custom field
        pass

    # Extract version
    version_match = re.search(r'\*\*Version\*\*:\s*([\d.]+)', content, re.IGNORECASE)
    if version_match:
        metadata['version'] = version_match.group(1)

    # Extract updated date
    updated_match = re.search(
        r'\*\*(?:Last )?Updated\*\*:\s*(\w+\s+\d{1,2},?\s+\d{4})',
        content,
        re.IGNORECASE
    )
    if updated_match:
        date_str = updated_match.group(1)
        metadata['updated'] = parse_date_string(date_str)

    return metadata


def parse_date_string(date_str: str) -> Optional[str]:
    """
    Parse various date formats to YYYY-MM-DD.

    Supports:
        - October 9, 2025
        - Oct 9, 2025
        - 2025-10-09
        - 10/09/2025

    Args:
        date_str: Date string in various formats

    Returns:
        Date in YYYY-MM-DD format, or None if parsing fails
    """
    date_str = date_str.strip()

    # Already in correct format
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        return date_str

    # Try parsing common formats
    formats = [
        '%B %d, %Y',     # October 9, 2025
        '%B %d %Y',      # October 9 2025
        '%b %d, %Y',     # Oct 9, 2025
        '%b %d %Y',      # Oct 9 2025
        '%m/%d/%Y',      # 10/09/2025
        '%d/%m/%Y',      # 09/10/2025 (ambiguous)
    ]

    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue

    return None


# =============================================================================
# Metadata Generation
# =============================================================================

def generate_metadata_from_file(file_path: str) -> Dict[str, Any]:
    """
    Generate complete metadata for a file from all available sources.

    Combines:
        - Existing frontmatter (if present)
        - Pattern A/B extraction
        - Git history
        - File path inference
        - Content analysis

    Args:
        file_path: Path to markdown file

    Returns:
        Complete metadata dictionary
    """
    metadata = {}

    # 1. Check for existing frontmatter
    existing = extract_frontmatter(file_path)
    if existing:
        metadata.update(existing)

    # 2. Read content for pattern extraction
    content = safe_read_file(file_path)
    if content:
        # Try Pattern A (PRD/Task)
        pattern_a = extract_pattern_a(content)
        for key, value in pattern_a.items():
            if key not in metadata:
                metadata[key] = value

        # Try Pattern B (Technical docs)
        pattern_b = extract_pattern_b(content)
        for key, value in pattern_b.items():
            if key not in metadata:
                metadata[key] = value

        # Detect status from content
        if 'status' not in metadata:
            detected_status = detect_status_from_content(content)
            if detected_status:
                metadata['status'] = detected_status

    # 3. Git history
    if 'created' not in metadata:
        git_created = get_git_created_date(file_path)
        if git_created:
            metadata['created'] = git_created

    if 'updated' not in metadata:
        git_updated = get_git_updated_date(file_path)
        if git_updated:
            metadata['updated'] = git_updated

    if 'author' not in metadata:
        git_author = get_git_primary_author(file_path)
        if git_author:
            metadata['author'] = git_author

    # 4. Infer type from path
    if 'type' not in metadata:
        inferred_type = infer_document_type_from_path(file_path)
        if inferred_type:
            metadata['type'] = inferred_type

    # 5. Infer status if still missing
    if 'status' not in metadata:
        if '/archived/' in file_path.lower():
            metadata['status'] = 'archived'
        else:
            metadata['status'] = 'active'

    # 6. Generate title from filename if missing
    if 'title' not in metadata:
        filename = Path(file_path).stem
        # Convert filename to title case
        title = filename.replace('-', ' ').replace('_', ' ').title()
        metadata['title'] = title

    # 7. Generate tags from path and filename
    if 'tags' not in metadata:
        metadata['tags'] = generate_tags_from_path(file_path)

    return metadata


def generate_tags_from_path(file_path: str) -> List[str]:
    """
    Generate relevant tags from file path and name.

    Args:
        file_path: Path to file

    Returns:
        List of tag strings
    """
    tags = []
    path_lower = file_path.lower()

    # Extract directory-based tags
    if '/security/' in path_lower:
        tags.append('security')
    if '/api/' in path_lower:
        tags.append('api')
    if '/database/' in path_lower:
        tags.append('database')
    if '/testing/' in path_lower or '/tests/' in path_lower:
        tags.append('testing')
    if '/workflows/' in path_lower:
        tags.append('workflow')
    if '/architecture/' in path_lower:
        tags.append('architecture')
    if '/deployment/' in path_lower:
        tags.append('deployment')

    # Extract filename-based tags
    filename = Path(file_path).stem.lower()
    words = re.split(r'[-_]', filename)

    # Add meaningful words as tags (avoid common words)
    skip_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
        'doc', 'docs', 'documentation', 'guide', 'readme', 'md'
    }

    for word in words:
        if len(word) > 3 and word not in skip_words and word not in tags:
            tags.append(word)

    # Limit to 6 tags
    return tags[:6]


# =============================================================================
# Metadata Validation
# =============================================================================

def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate metadata completeness and correctness.

    Args:
        metadata: Metadata dictionary

    Returns:
        Dictionary with 'errors' and 'warnings' lists
    """
    errors = []
    warnings = []

    # Required fields
    required = ['title', 'type', 'status', 'created']
    for field in required:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")

    # Type validation
    valid_types = [
        'standards', 'guide', 'prd', 'task', 'reference', 'api',
        'architecture', 'decision', 'process', 'changelog', 'audit', 'template'
    ]
    if 'type' in metadata and metadata['type'] not in valid_types:
        warnings.append(f"Invalid type: {metadata['type']} (expected one of {valid_types})")

    # Status validation
    valid_statuses = ['draft', 'active', 'stable', 'deprecated', 'archived', 'completed']
    if 'status' in metadata and metadata['status'] not in valid_statuses:
        warnings.append(f"Invalid status: {metadata['status']} (expected one of {valid_statuses})")

    # Date format validation
    for date_field in ['created', 'updated', 'review_date']:
        if date_field in metadata:
            date_val = metadata[date_field]
            if not re.match(r'\d{4}-\d{2}-\d{2}', str(date_val)):
                errors.append(f"Invalid date format for {date_field}: {date_val} (expected YYYY-MM-DD)")

    # Date consistency
    if 'created' in metadata and 'updated' in metadata:
        try:
            created = datetime.strptime(metadata['created'], '%Y-%m-%d')
            updated = datetime.strptime(metadata['updated'], '%Y-%m-%d')
            if updated < created:
                errors.append(f"Updated date ({metadata['updated']}) is before created date ({metadata['created']})")
        except ValueError:
            pass  # Already caught by format validation

    # Tag validation
    if 'tags' in metadata:
        if not isinstance(metadata['tags'], list):
            errors.append("Tags must be a list")
        else:
            for tag in metadata['tags']:
                if not re.match(r'^[a-z0-9-]+$', tag):
                    warnings.append(f"Tag should be lowercase with hyphens only: {tag}")

    # Recommended fields
    recommended = ['version', 'updated', 'author', 'tags']
    missing_recommended = [f for f in recommended if f not in metadata]
    if missing_recommended:
        warnings.append(f"Missing recommended fields: {', '.join(missing_recommended)}")

    return {'errors': errors, 'warnings': warnings}


# =============================================================================
# Operations
# =============================================================================

def scan_metadata_coverage(root_dir: str = '.') -> Dict[str, Any]:
    """
    Scan all markdown files and report metadata coverage.

    Args:
        root_dir: Root directory to scan

    Returns:
        Dictionary with coverage statistics
    """
    files = find_markdown_files(root_dir)

    stats = {
        'total_files': len(files),
        'with_frontmatter': 0,
        'full_metadata': 0,
        'partial_metadata': 0,
        'minimal_metadata': 0,
        'no_metadata': 0,
        'missing_fields': {},
    }

    required_fields = ['title', 'type', 'status', 'created']
    recommended_fields = ['version', 'updated', 'author', 'tags']
    all_fields = required_fields + recommended_fields

    for file_path in files:
        metadata = extract_frontmatter(file_path)

        if metadata:
            stats['with_frontmatter'] += 1

            # Calculate completeness
            present_fields = sum(1 for f in all_fields if f in metadata)
            completeness = present_fields / len(all_fields)

            if completeness == 1.0:
                stats['full_metadata'] += 1
            elif completeness >= 0.5:
                stats['partial_metadata'] += 1
            else:
                stats['minimal_metadata'] += 1

            # Track missing fields
            for field in all_fields:
                if field not in metadata:
                    stats['missing_fields'][field] = stats['missing_fields'].get(field, 0) + 1
        else:
            stats['no_metadata'] += 1

    return stats


def enhance_file_metadata(file_path: str, interactive: bool = False) -> bool:
    """
    Enhance metadata for a single file.

    Args:
        file_path: Path to markdown file
        interactive: If True, prompt for manual input

    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate metadata
        metadata = generate_metadata_from_file(file_path)

        # Validate
        validation = validate_metadata(metadata)

        if validation['errors']:
            logger.error(f"Validation errors in {file_path}:")
            for error in validation['errors']:
                logger.error(f"  - {error}")
            return False

        if validation['warnings']:
            logger.warning(f"Validation warnings in {file_path}:")
            for warning in validation['warnings']:
                logger.warning(f"  - {warning}")

        # Interactive mode
        if interactive:
            print(f"\nGenerated metadata for {file_path}:")
            print("-" * 50)
            for key, value in metadata.items():
                print(f"{key}: {value}")
            print("-" * 50)

            response = input("Apply this metadata? [Y/n]: ").strip().lower()
            if response and response != 'y':
                logger.info("Skipped")
                return False

        # Insert metadata
        success = insert_frontmatter(file_path, metadata, preserve_existing=True)
        if success:
            logger.info(f"✓ Enhanced metadata in {file_path}")
        return success

    except Exception as e:
        logger.error(f"Error enhancing {file_path}: {e}")
        return False


def batch_process_files(root_dir: str = '.', dry_run: bool = False, file_type: str = None) -> Dict[str, int]:
    """
    Batch process all markdown files.

    Args:
        root_dir: Root directory to process
        dry_run: If True, don't make changes
        file_type: Filter by document type (prd, guide, etc.)

    Returns:
        Dictionary with processing statistics
    """
    files = find_markdown_files(root_dir)

    stats = {
        'total': len(files),
        'processed': 0,
        'skipped': 0,
        'errors': 0
    }

    for file_path in files:
        try:
            # Check if file already has complete metadata
            existing = extract_frontmatter(file_path)
            if existing:
                validation = validate_metadata(existing)
                if not validation['errors'] and not validation['warnings']:
                    stats['skipped'] += 1
                    continue

            # Generate and validate metadata
            metadata = generate_metadata_from_file(file_path)

            # Filter by type if specified
            if file_type and metadata.get('type') != file_type:
                stats['skipped'] += 1
                continue

            validation = validate_metadata(metadata)
            if validation['errors']:
                logger.error(f"Validation failed for {file_path}")
                stats['errors'] += 1
                continue

            if dry_run:
                logger.info(f"[DRY RUN] Would enhance: {file_path}")
                stats['processed'] += 1
            else:
                success = insert_frontmatter(file_path, metadata, preserve_existing=True)
                if success:
                    stats['processed'] += 1
                else:
                    stats['errors'] += 1

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            stats['errors'] += 1

    return stats


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Librarian Metadata Tool - Extract, generate, and standardize metadata'
    )

    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan and report metadata coverage'
    )

    parser.add_argument(
        '--extract',
        metavar='FILE',
        help='Extract metadata from specific file'
    )

    parser.add_argument(
        '--generate',
        metavar='FILE',
        help='Generate metadata for specific file'
    )

    parser.add_argument(
        '--enhance',
        metavar='FILE',
        help='Enhance metadata for specific file'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Batch process all files'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive mode (prompt for confirmation)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    parser.add_argument(
        '--type',
        metavar='TYPE',
        help='Filter by document type (for batch processing)'
    )

    parser.add_argument(
        '--root',
        metavar='DIR',
        default='.',
        help='Root directory to process (default: current directory)'
    )

    args = parser.parse_args()

    # Scan operation
    if args.scan:
        print("Scanning metadata coverage...")
        stats = scan_metadata_coverage(args.root)

        print("\nMetadata Coverage Report")
        print("=" * 60)
        print(f"Total files analyzed: {stats['total_files']}")
        print()
        print("Metadata completeness:")
        print(f"  - Full metadata (100%):    {stats['full_metadata']} files ({stats['full_metadata']/stats['total_files']*100:.0f}%)")
        print(f"  - Partial metadata (50-99%): {stats['partial_metadata']} files ({stats['partial_metadata']/stats['total_files']*100:.0f}%)")
        print(f"  - Minimal metadata (1-49%):  {stats['minimal_metadata']} files ({stats['minimal_metadata']/stats['total_files']*100:.0f}%)")
        print(f"  - No metadata (0%):          {stats['no_metadata']} files ({stats['no_metadata']/stats['total_files']*100:.0f}%)")
        print()
        print("Missing fields (top 10):")
        sorted_fields = sorted(stats['missing_fields'].items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_fields[:10]:
            print(f"  {count:3d}. {field}")
        print()
        print("Recommendations:")
        print("  - Run batch generation: python tools/librarian_metadata.py --batch")
        print("  - Focus on high-priority docs first (PRDs, standards)")

    # Extract operation
    elif args.extract:
        file_path = args.extract
        print(f"Extracting metadata from {file_path}...")
        metadata = extract_frontmatter(file_path)

        if metadata:
            print("\nExisting YAML Frontmatter:")
            print("-" * 60)
            for key, value in metadata.items():
                print(f"{key}: {value}")
        else:
            print("No YAML frontmatter found")

        # Try pattern extraction
        content = safe_read_file(file_path)
        if content:
            pattern_a = extract_pattern_a(content)
            pattern_b = extract_pattern_b(content)

            if pattern_a:
                print("\nPattern A metadata:")
                print("-" * 60)
                for key, value in pattern_a.items():
                    print(f"{key}: {value}")

            if pattern_b:
                print("\nPattern B metadata:")
                print("-" * 60)
                for key, value in pattern_b.items():
                    print(f"{key}: {value}")

    # Generate operation
    elif args.generate:
        file_path = args.generate
        print(f"Generating metadata for {file_path}...")
        metadata = generate_metadata_from_file(file_path)

        print("\nGenerated metadata:")
        print("-" * 60)
        for key, value in metadata.items():
            print(f"{key}: {value}")

        validation = validate_metadata(metadata)
        if validation['errors']:
            print("\nValidation errors:")
            for error in validation['errors']:
                print(f"  ✗ {error}")
        if validation['warnings']:
            print("\nValidation warnings:")
            for warning in validation['warnings']:
                print(f"  ⚠ {warning}")

        if not args.dry_run:
            response = input("\nApply this metadata? [y/N]: ").strip().lower()
            if response == 'y':
                success = insert_frontmatter(file_path, metadata, preserve_existing=True)
                if success:
                    print("✓ Metadata applied successfully")
                else:
                    print("✗ Failed to apply metadata")

    # Enhance operation
    elif args.enhance:
        file_path = args.enhance
        print(f"Enhancing metadata for {file_path}...")
        success = enhance_file_metadata(file_path, interactive=args.interactive or True)
        if success:
            print("✓ Metadata enhanced successfully")
        else:
            print("✗ Failed to enhance metadata")

    # Batch operation
    elif args.batch:
        print(f"Batch processing files in {args.root}...")
        if args.dry_run:
            print("[DRY RUN MODE - No changes will be made]")

        stats = batch_process_files(
            root_dir=args.root,
            dry_run=args.dry_run,
            file_type=args.type
        )

        print("\nBatch Processing Results")
        print("=" * 60)
        print(f"Total files: {stats['total']}")
        print(f"Processed:   {stats['processed']}")
        print(f"Skipped:     {stats['skipped']}")
        print(f"Errors:      {stats['errors']}")

        if not args.dry_run:
            print("\n✓ Batch processing complete")
        else:
            print("\n[DRY RUN] Run without --dry-run to apply changes")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
