#!/usr/bin/env python3
"""
Metadata Validation Script

Purpose: Validate YAML frontmatter in markdown files against documentation standards
Usage: python tools/validate_metadata.py <file_path> [--all] [--fix]
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import yaml

# Try to import click for CLI, fall back to argparse if not available
try:
    import click
    HAS_CLICK = True
except ImportError:
    import argparse
    HAS_CLICK = False


@dataclass
class ValidationResult:
    """Result of metadata validation"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    file_path: str

    def __str__(self) -> str:
        if self.valid:
            return f"✓ {self.file_path}: Valid"

        output = [f"✗ {self.file_path}: Invalid"]

        if self.errors:
            output.append("\n  Errors:")
            for error in self.errors:
                output.append(f"    - {error}")

        if self.warnings:
            output.append("\n  Warnings:")
            for warning in self.warnings:
                output.append(f"    - {warning}")

        return "\n".join(output)


class MetadataValidator:
    """Validates YAML frontmatter in markdown files"""

    # Required fields that must be present
    REQUIRED_FIELDS = ['title', 'type', 'component', 'status']

    # Valid values for enum fields
    VALID_TYPES = [
        'technical_doc',
        'api_spec',
        'architecture',
        'process',
        'status_report',
        'guide',
        'reference',
        'tutorial'
    ]

    VALID_STATUSES = [
        'draft',
        'active',
        'review',
        'archived',
        'deprecated'
    ]

    # Optional fields
    OPTIONAL_FIELDS = ['tags', 'owner', 'related', 'created', 'updated']

    def __init__(self, file_path: Path):
        """
        Initialize validator for a markdown file

        Args:
            file_path: Path to markdown file to validate
        """
        self.file_path = Path(file_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> ValidationResult:
        """
        Validate the markdown file's metadata

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        # Reset errors and warnings
        self.errors = []
        self.warnings = []

        # Check file exists
        if not self.file_path.exists():
            self.errors.append(f"File not found: {self.file_path}")
            return self._build_result()

        # Check file is markdown
        if self.file_path.suffix not in ['.md', '.markdown']:
            self.errors.append(f"Not a markdown file: {self.file_path}")
            return self._build_result()

        # Read file content
        try:
            content = self.file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"Failed to read file: {e}")
            return self._build_result()

        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)

        if frontmatter is None:
            self.errors.append("Missing YAML frontmatter (must start with ---)")
            return self._build_result()

        # Parse frontmatter
        try:
            metadata = yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML syntax: {e}")
            return self._build_result()

        if not isinstance(metadata, dict):
            self.errors.append("Frontmatter must be a YAML dictionary")
            return self._build_result()

        # Validate required fields
        self._validate_required_fields(metadata)

        # Validate field types and values
        self._validate_field_values(metadata)

        # Check for unexpected fields (warnings only)
        self._check_unexpected_fields(metadata)

        return self._build_result()

    def _extract_frontmatter(self, content: str) -> Optional[str]:
        """
        Extract YAML frontmatter from markdown content

        Args:
            content: Full markdown file content

        Returns:
            Frontmatter string or None if not found
        """
        # Frontmatter pattern: starts with ---, ends with ---
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            return match.group(1)

        return None

    def _validate_required_fields(self, metadata: Dict) -> None:
        """Check that all required fields are present"""
        missing = [f for f in self.REQUIRED_FIELDS if f not in metadata]

        if missing:
            self.errors.append(f"Missing required fields: {', '.join(missing)}")

    def _validate_field_values(self, metadata: Dict) -> None:
        """Validate field types and enum values"""
        # Validate 'type' field
        if 'type' in metadata:
            type_value = metadata['type']
            if not isinstance(type_value, str):
                self.errors.append(f"Field 'type' must be a string, got {type(type_value).__name__}")
            elif type_value not in self.VALID_TYPES:
                self.errors.append(
                    f"Invalid type '{type_value}'. "
                    f"Must be one of: {', '.join(self.VALID_TYPES)}"
                )

        # Validate 'status' field
        if 'status' in metadata:
            status_value = metadata['status']
            if not isinstance(status_value, str):
                self.errors.append(f"Field 'status' must be a string, got {type(status_value).__name__}")
            elif status_value not in self.VALID_STATUSES:
                self.errors.append(
                    f"Invalid status '{status_value}'. "
                    f"Must be one of: {', '.join(self.VALID_STATUSES)}"
                )

        # Validate 'title' is string
        if 'title' in metadata and not isinstance(metadata['title'], str):
            self.errors.append(f"Field 'title' must be a string, got {type(metadata['title']).__name__}")

        # Validate 'component' is string
        if 'component' in metadata and not isinstance(metadata['component'], str):
            self.errors.append(f"Field 'component' must be a string, got {type(metadata['component']).__name__}")

        # Validate 'tags' is list
        if 'tags' in metadata and not isinstance(metadata['tags'], list):
            self.errors.append(f"Field 'tags' must be a list, got {type(metadata['tags']).__name__}")

        # Validate 'related' is list
        if 'related' in metadata and not isinstance(metadata['related'], list):
            self.errors.append(f"Field 'related' must be a list, got {type(metadata['related']).__name__}")

    def _check_unexpected_fields(self, metadata: Dict) -> None:
        """Check for fields not in standard schema (warnings)"""
        known_fields = set(self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS)
        unexpected = set(metadata.keys()) - known_fields

        if unexpected:
            self.warnings.append(f"Unexpected fields: {', '.join(unexpected)}")

    def _build_result(self) -> ValidationResult:
        """Build ValidationResult from current state"""
        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            file_path=str(self.file_path)
        )

    def generate_template(self) -> str:
        """
        Generate template YAML frontmatter for the file

        Returns:
            YAML frontmatter template string
        """
        # Infer component from file path if possible
        component = self._infer_component()

        # Infer type from file path or name
        doc_type = self._infer_type()

        template = f"""---
title: "{self.file_path.stem.replace('-', ' ').replace('_', ' ').title()}"
type: {doc_type}
component: {component}
status: draft
tags: []
---

"""
        return template

    def _infer_component(self) -> str:
        """Infer component name from file path"""
        # Check if file is in a component directory
        parts = self.file_path.parts

        # Common component directories
        if 'modules' in parts:
            idx = parts.index('modules')
            if len(parts) > idx + 1:
                return parts[idx + 1]

        if 'component_docs' in parts:
            idx = parts.index('component_docs')
            if len(parts) > idx + 1:
                return parts[idx + 1]

        # Check for component keywords in path
        component_keywords = [
            'database', 'email', 'scraping', 'ai_analysis',
            'document_generation', 'storage', 'security',
            'integration', 'authentication'
        ]

        for keyword in component_keywords:
            if keyword in str(self.file_path).lower():
                return keyword

        return 'general'

    def _infer_type(self) -> str:
        """Infer document type from file path or name"""
        filename_lower = self.file_path.name.lower()

        # Type inference rules
        if 'api' in filename_lower:
            return 'api_spec'
        elif 'architecture' in filename_lower or 'design' in filename_lower:
            return 'architecture'
        elif 'guide' in filename_lower or 'how-to' in filename_lower:
            return 'guide'
        elif 'status' in filename_lower or 'report' in filename_lower:
            return 'status_report'
        elif 'process' in filename_lower or 'workflow' in filename_lower:
            return 'process'
        elif 'reference' in filename_lower:
            return 'reference'
        elif 'tutorial' in filename_lower:
            return 'tutorial'
        else:
            return 'technical_doc'


def validate_file(file_path: Path, fix: bool = False) -> ValidationResult:
    """
    Validate a single markdown file

    Args:
        file_path: Path to file to validate
        fix: If True, add template frontmatter to files missing it

    Returns:
        ValidationResult
    """
    validator = MetadataValidator(file_path)
    result = validator.validate()

    # If fix mode and file is missing frontmatter, add template
    if fix and not result.valid and "Missing YAML frontmatter" in str(result.errors):
        try:
            content = file_path.read_text(encoding='utf-8')
            template = validator.generate_template()
            new_content = template + content
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✓ Added template metadata to {file_path}")

            # Re-validate
            result = validator.validate()
        except Exception as e:
            print(f"✗ Failed to add template to {file_path}: {e}")

    return result


def validate_all(root_path: Path = None, fix: bool = False) -> Tuple[int, int]:
    """
    Validate all markdown files in project

    Args:
        root_path: Root directory to scan (default: current directory)
        fix: If True, auto-fix files where possible

    Returns:
        Tuple of (valid_count, invalid_count)
    """
    if root_path is None:
        root_path = Path.cwd()

    valid_count = 0
    invalid_count = 0

    # Find all markdown files
    md_files = list(root_path.rglob('*.md'))

    print(f"Scanning {len(md_files)} markdown files...\n")

    for md_file in md_files:
        # Skip files in certain directories
        skip_dirs = ['node_modules', '.git', 'venv', 'project_venv', '__pycache__']
        if any(skip_dir in md_file.parts for skip_dir in skip_dirs):
            continue

        result = validate_file(md_file, fix=fix)

        if result.valid:
            valid_count += 1
        else:
            invalid_count += 1
            print(result)
            print()  # Blank line between results

    return valid_count, invalid_count


# CLI Implementation
if HAS_CLICK:
    @click.command()
    @click.argument('file_path', type=click.Path(exists=True), required=False)
    @click.option('--all', 'validate_all_files', is_flag=True, help='Validate all markdown files')
    @click.option('--fix', is_flag=True, help='Auto-fix files by adding template metadata')
    def main(file_path: Optional[str], validate_all_files: bool, fix: bool):
        """Validate YAML frontmatter in markdown files"""

        if validate_all_files:
            valid, invalid = validate_all(fix=fix)
            print(f"\n{'='*60}")
            print(f"Results: {valid} valid, {invalid} invalid")
            sys.exit(0 if invalid == 0 else 1)

        elif file_path:
            result = validate_file(Path(file_path), fix=fix)
            print(result)
            sys.exit(0 if result.valid else 1)

        else:
            print("Error: Must provide FILE_PATH or use --all flag")
            sys.exit(1)

else:
    # Fallback argparse implementation
    def main():
        parser = argparse.ArgumentParser(description='Validate YAML frontmatter in markdown files')
        parser.add_argument('file_path', nargs='?', help='Path to markdown file')
        parser.add_argument('--all', action='store_true', help='Validate all markdown files')
        parser.add_argument('--fix', action='store_true', help='Auto-fix by adding template metadata')

        args = parser.parse_args()

        if args.all:
            valid, invalid = validate_all(fix=args.fix)
            print(f"\n{'='*60}")
            print(f"Results: {valid} valid, {invalid} invalid")
            sys.exit(0 if invalid == 0 else 1)

        elif args.file_path:
            result = validate_file(Path(args.file_path), fix=args.fix)
            print(result)
            sys.exit(0 if result.valid else 1)

        else:
            parser.print_help()
            sys.exit(1)


if __name__ == '__main__':
    main()
