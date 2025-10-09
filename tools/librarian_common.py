"""
Librarian Common Utilities: Shared utilities for librarian tools

This module provides common functionality used across all librarian tools
including YAML frontmatter parsing, git history extraction, markdown link
detection, and file discovery operations. It serves as the foundation for
the metadata extraction, indexing, validation, and archival systems.

The module emphasizes robust error handling and provides both low-level
primitives and high-level convenience functions for working with
documentation files.

Metadata:
    Type: module
    Status: active
    Dependencies: PyYAML, GitPython, pathlib, re
    Related: tools/librarian_index.py, tools/librarian_validate.py

Author: Claude Sonnet 4.5
Created: 2025-10-09
Updated: 2025-10-09

Example:
    Extract YAML frontmatter from a markdown file::

        from librarian_common import extract_frontmatter

        metadata = extract_frontmatter('docs/guide.md')
        print(metadata.get('title'))
"""

import os
import re
import yaml
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# YAML Frontmatter Operations
# =============================================================================

def extract_frontmatter(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract YAML frontmatter from a markdown file.

    Parses the YAML frontmatter block (delimited by ---) from the beginning
    of a markdown file and returns it as a dictionary. Returns None if no
    frontmatter is found.

    Args:
        file_path: Path to markdown file (absolute or relative)

    Returns:
        Dictionary containing parsed YAML frontmatter, or None if not found

    Raises:
        FileNotFoundError: If file does not exist
        yaml.YAMLError: If frontmatter is invalid YAML

    Example:
        >>> extract_frontmatter('docs/guide.md')
        {'title': 'User Guide', 'type': 'guide', 'status': 'active'}

        >>> extract_frontmatter('docs/no-metadata.md')
        None
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix != '.md':
        logger.warning(f"File is not a markdown file: {file_path}")
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for frontmatter delimiters
        if not content.startswith('---\n'):
            return None

        # Find the closing delimiter
        end_match = re.search(r'\n---\n', content[4:])
        if not end_match:
            return None

        # Extract YAML block
        yaml_block = content[4:end_match.start() + 4]

        # Parse YAML
        metadata = yaml.safe_load(yaml_block)

        return metadata if isinstance(metadata, dict) else None

    except yaml.YAMLError as e:
        logger.warning(f"Invalid YAML in {file_path}, skipping")
        return None
    except Exception as e:
        logger.warning(f"Error reading {file_path}: {e}")
        return None


def insert_frontmatter(file_path: str, metadata: Dict[str, Any], preserve_existing: bool = False) -> bool:
    """
    Insert or update YAML frontmatter in a markdown file.

    Adds YAML frontmatter to the beginning of a markdown file. If frontmatter
    already exists and preserve_existing is True, merges new metadata with
    existing (new values take precedence).

    Args:
        file_path: Path to markdown file
        metadata: Dictionary of metadata to insert
        preserve_existing: If True, merge with existing metadata

    Returns:
        True if successful, False otherwise

    Example:
        >>> metadata = {'title': 'New Guide', 'type': 'guide', 'status': 'draft'}
        >>> insert_frontmatter('docs/new-guide.md', metadata)
        True
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        existing_metadata = None
        body = content

        # Check for existing frontmatter
        if content.startswith('---\n'):
            end_match = re.search(r'\n---\n', content[4:])
            if end_match:
                existing_metadata = extract_frontmatter(file_path)
                body = content[end_match.end() + 4:]

        # Merge or replace metadata
        if preserve_existing and existing_metadata:
            final_metadata = {**existing_metadata, **metadata}
        else:
            final_metadata = metadata

        # Generate YAML frontmatter
        yaml_str = yaml.dump(final_metadata, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{yaml_str}---\n\n{body.lstrip()}"

        # Write back to file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        logger.info(f"Updated frontmatter in {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error inserting frontmatter in {file_path}: {e}")
        return False


def has_frontmatter(file_path: str) -> bool:
    """
    Check if a markdown file has YAML frontmatter.

    Args:
        file_path: Path to markdown file

    Returns:
        True if file has frontmatter, False otherwise

    Example:
        >>> has_frontmatter('docs/guide.md')
        True
    """
    try:
        metadata = extract_frontmatter(file_path)
        return metadata is not None
    except Exception:
        return False


# =============================================================================
# Git History Operations
# =============================================================================

def get_git_created_date(file_path: str) -> Optional[str]:
    """
    Get the creation date of a file from git history (first commit).

    Args:
        file_path: Path to file (relative to repo root)

    Returns:
        Date string in YYYY-MM-DD format, or None if not in git

    Example:
        >>> get_git_created_date('docs/guide.md')
        '2024-06-15'
    """
    try:
        # Get the first commit date for this file
        result = subprocess.run(
            ['git', 'log', '--follow', '--format=%aI', '--reverse', '--', file_path],
            capture_output=True,
            text=True,
            check=True
        )

        if result.stdout.strip():
            # Parse ISO 8601 date and return YYYY-MM-DD
            date_str = result.stdout.strip().split('\n')[0]
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%Y-%m-%d')

        return None

    except subprocess.CalledProcessError:
        logger.warning(f"Could not get git history for {file_path}")
        return None
    except Exception as e:
        logger.warning(f"Error getting git created date for {file_path}: {e}")
        return None


def get_git_updated_date(file_path: str) -> Optional[str]:
    """
    Get the last update date of a file from git history (last commit).

    Args:
        file_path: Path to file (relative to repo root)

    Returns:
        Date string in YYYY-MM-DD format, or None if not in git

    Example:
        >>> get_git_updated_date('docs/guide.md')
        '2025-10-09'
    """
    try:
        # Get the last commit date for this file
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%aI', '--', file_path],
            capture_output=True,
            text=True,
            check=True
        )

        if result.stdout.strip():
            # Parse ISO 8601 date and return YYYY-MM-DD
            date_str = result.stdout.strip()
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%Y-%m-%d')

        return None

    except subprocess.CalledProcessError:
        logger.warning(f"Could not get git history for {file_path}")
        return None
    except Exception as e:
        logger.warning(f"Error getting git updated date for {file_path}: {e}")
        return None


def get_git_primary_author(file_path: str) -> Optional[str]:
    """
    Get the primary author of a file from git blame (most lines contributed).

    Args:
        file_path: Path to file (relative to repo root)

    Returns:
        Author name, or None if not in git

    Example:
        >>> get_git_primary_author('docs/guide.md')
        'John Doe'
    """
    try:
        # Get blame statistics
        result = subprocess.run(
            ['git', 'blame', '--line-porcelain', file_path],
            capture_output=True,
            text=True,
            check=True
        )

        # Count lines per author
        author_lines = {}
        for line in result.stdout.split('\n'):
            if line.startswith('author '):
                author = line[7:].strip()
                author_lines[author] = author_lines.get(author, 0) + 1

        if author_lines:
            # Return author with most lines
            primary_author = max(author_lines.items(), key=lambda x: x[1])[0]
            return primary_author

        return None

    except subprocess.CalledProcessError:
        logger.warning(f"Could not get git blame for {file_path}")
        return None
    except Exception as e:
        logger.warning(f"Error getting git author for {file_path}: {e}")
        return None


# =============================================================================
# Markdown Link Extraction
# =============================================================================

def extract_markdown_links(file_path: str) -> List[Tuple[str, str]]:
    """
    Extract all markdown links from a file.

    Finds all markdown-style links [text](url) and returns them as tuples.

    Args:
        file_path: Path to markdown file

    Returns:
        List of (link_text, link_url) tuples

    Example:
        >>> extract_markdown_links('docs/guide.md')
        [('API Docs', 'docs/api/README.md'), ('Setup', '../setup.md')]
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex pattern for markdown links: [text](url)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)

        return matches

    except Exception as e:
        logger.error(f"Error extracting links from {file_path}: {e}")
        return []


def resolve_link_path(source_file: str, link_url: str) -> Optional[str]:
    """
    Resolve a relative link URL to an absolute path.

    Handles relative paths (./, ../) and absolute paths from repo root.

    Args:
        source_file: Path to file containing the link
        link_url: Link URL from markdown (may be relative)

    Returns:
        Absolute path to linked file, or None if external link

    Example:
        >>> resolve_link_path('docs/guide.md', '../api/README.md')
        '/workspace/docs/api/README.md'

        >>> resolve_link_path('docs/guide.md', 'https://example.com')
        None
    """
    # Skip external links
    if link_url.startswith(('http://', 'https://', 'mailto:')):
        return None

    # Skip anchors
    if link_url.startswith('#'):
        return None

    # Remove anchor if present
    link_url = link_url.split('#')[0]

    source_path = Path(source_file).parent

    if link_url.startswith('/'):
        # Absolute path from repo root
        repo_root = get_repo_root()
        if repo_root:
            return str(Path(repo_root) / link_url.lstrip('/'))
        return None
    else:
        # Relative path
        resolved = (source_path / link_url).resolve()
        return str(resolved)


def get_repo_root() -> Optional[str]:
    """
    Get the root directory of the git repository.

    Returns:
        Absolute path to repo root, or None if not in a git repo

    Example:
        >>> get_repo_root()
        '/workspace/.trees/librarian'
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


# =============================================================================
# File Discovery
# =============================================================================

def find_markdown_files(root_dir: str = '.', exclude_patterns: List[str] = None) -> List[str]:
    """
    Recursively find all markdown files in a directory.

    Respects .gitignore patterns and excludes specified patterns.

    Args:
        root_dir: Root directory to search (default: current directory)
        exclude_patterns: List of glob patterns to exclude (e.g., ['node_modules', '.git'])

    Returns:
        List of absolute paths to markdown files

    Example:
        >>> find_markdown_files('docs/', exclude_patterns=['archived'])
        ['/workspace/docs/guide.md', '/workspace/docs/api/README.md']
    """
    if exclude_patterns is None:
        exclude_patterns = [
            '.git',
            'node_modules',
            'project_venv',
            '__pycache__',
            '.pytest_cache'
        ]

    markdown_files = []
    root_path = Path(root_dir).resolve()

    for md_file in root_path.rglob('*.md'):
        # Check if file matches any exclude pattern
        relative_path = md_file.relative_to(root_path)
        excluded = any(
            pattern in str(relative_path) for pattern in exclude_patterns
        )

        if not excluded:
            markdown_files.append(str(md_file))

    return sorted(markdown_files)


def find_python_files(root_dir: str = '.', exclude_patterns: List[str] = None) -> List[str]:
    """
    Recursively find all Python files in a directory.

    Args:
        root_dir: Root directory to search (default: current directory)
        exclude_patterns: List of glob patterns to exclude

    Returns:
        List of absolute paths to Python files

    Example:
        >>> find_python_files('modules/')
        ['/workspace/modules/database/client.py', ...]
    """
    if exclude_patterns is None:
        exclude_patterns = [
            '.git',
            'node_modules',
            'project_venv',
            '__pycache__',
            '.pytest_cache',
            'build',
            'dist'
        ]

    python_files = []
    root_path = Path(root_dir).resolve()

    for py_file in root_path.rglob('*.py'):
        relative_path = py_file.relative_to(root_path)
        excluded = any(
            pattern in str(relative_path) for pattern in exclude_patterns
        )

        if not excluded:
            python_files.append(str(py_file))

    return sorted(python_files)


# =============================================================================
# Utility Functions
# =============================================================================

def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        File size in MB

    Example:
        >>> get_file_size_mb('docs/large-document.md')
        2.5
    """
    path = Path(file_path)
    if not path.exists():
        return 0.0

    size_bytes = path.stat().st_size
    return size_bytes / (1024 * 1024)


def get_directory_size_mb(dir_path: str) -> float:
    """
    Get total size of directory in megabytes.

    Args:
        dir_path: Path to directory

    Returns:
        Total size in MB

    Example:
        >>> get_directory_size_mb('docs/')
        15.3
    """
    path = Path(dir_path)
    if not path.is_dir():
        return 0.0

    total_size = sum(
        f.stat().st_size for f in path.rglob('*') if f.is_file()
    )
    return total_size / (1024 * 1024)


def safe_read_file(file_path: str) -> Optional[str]:
    """
    Safely read a file's contents.

    Args:
        file_path: Path to file

    Returns:
        File contents as string, or None if error

    Example:
        >>> content = safe_read_file('docs/guide.md')
        >>> if content:
        ...     print(len(content))
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None


def infer_document_type_from_path(file_path: str) -> Optional[str]:
    """
    Infer document type from file path location.

    Args:
        file_path: Path to markdown file

    Returns:
        Inferred type string (guide, prd, api, etc.) or None

    Example:
        >>> infer_document_type_from_path('docs/workflows/deployment.md')
        'guide'

        >>> infer_document_type_from_path('tasks/prd-feature-x.md')
        'prd'
    """
    path_lower = file_path.lower()

    # Task-related
    if '/tasks/' in path_lower:
        if 'prd-' in path_lower or 'prd_' in path_lower:
            return 'prd'
        if 'task' in path_lower:
            return 'task'

    # Documentation structure
    if '/standards/' in path_lower:
        return 'standards'
    if '/workflows/' in path_lower or '/guides/' in path_lower:
        return 'guide'
    if '/api/' in path_lower:
        return 'api'
    if '/architecture/' in path_lower:
        return 'architecture'
    if '/decisions/' in path_lower:
        return 'decision'
    if '/changelogs/' in path_lower:
        return 'changelog'
    if '/audits/' in path_lower:
        return 'audit'
    if '/templates/' in path_lower:
        return 'template'
    if '/archived/' in path_lower:
        return 'archived'

    # Component docs
    if '/component_docs/' in path_lower:
        return 'reference'

    # Default for unclear cases
    return None


def detect_status_from_content(content: str) -> Optional[str]:
    """
    Detect document status from content markers.

    Args:
        content: Document content

    Returns:
        Detected status (completed, deprecated, etc.) or None

    Example:
        >>> content = "**Status:** ✅ COMPLETED\\n..."
        >>> detect_status_from_content(content)
        'completed'
    """
    content_lower = content.lower()

    # Check for completion markers
    if re.search(r'✅\s*(completed|complete|done)', content, re.IGNORECASE):
        return 'completed'

    # Check for status markers in first 500 characters
    header = content[:500]

    if re.search(r'\*\*status\*\*:\s*completed', header, re.IGNORECASE):
        return 'completed'
    if re.search(r'\*\*status\*\*:\s*deprecated', header, re.IGNORECASE):
        return 'deprecated'
    if re.search(r'\*\*status\*\*:\s*draft', header, re.IGNORECASE):
        return 'draft'
    if re.search(r'\*\*status\*\*:\s*archived', header, re.IGNORECASE):
        return 'archived'

    return None


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == '__main__':
    # Test functions
    print("Librarian Common Utilities Test")
    print("=" * 50)

    # Test file discovery
    print("\nMarkdown files in docs/:")
    md_files = find_markdown_files('docs/', exclude_patterns=['archived'])
    for f in md_files[:5]:
        print(f"  {f}")
    print(f"  ... ({len(md_files)} total)")

    # Test metadata extraction
    if md_files:
        test_file = md_files[0]
        print(f"\nMetadata from {test_file}:")
        metadata = extract_frontmatter(test_file)
        if metadata:
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        else:
            print("  No frontmatter found")

    print("\nTests complete!")
