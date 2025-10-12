#!/usr/bin/env python3
"""
File Location Validation Script

Purpose: Check if file placement complies with FILE_ORGANIZATION_STANDARDS.md
Usage: python tools/validate_location.py <file_path> [--scan-root] [--all]
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    import click
    HAS_CLICK = True
except ImportError:
    import argparse
    HAS_CLICK = False


@dataclass
class ValidationResult:
    """Result of location validation"""
    valid: bool
    violations: List[str]
    suggestions: List[str]
    file_path: str

    def __str__(self) -> str:
        if self.valid:
            return f"✓ {self.file_path}: Correct location"

        output = [f"✗ {self.file_path}: Location violation"]

        if self.violations:
            output.append("\n  Violations:")
            for violation in self.violations:
                output.append(f"    - {violation}")

        if self.suggestions:
            output.append("\n  Suggested locations:")
            for suggestion in self.suggestions:
                output.append(f"    → {suggestion}")

        return "\n".join(output)


class LocationValidator:
    """Validates file placement against FILE_ORGANIZATION_STANDARDS.md"""

    # Essential files allowed in root directory
    ROOT_ALLOWED_FILES = {
        'README.md',
        'CLAUDE.md',
        'CHANGELOG.md',
        'app_modular.py',
        'main.py',
        'requirements.txt',
        'pyproject.toml',
        'VERSION',
        'docker-compose.yml',
        '.env',
        '.env.example',
        '.gitignore',
        'Makefile',
        'claude.md',  # lowercase variant
        'PURPOSE.md'  # worktree-specific
    }

    # Placement rules: patterns and their correct locations
    PLACEMENT_RULES = [
        {
            'name': 'branch_status',
            'patterns': [
                r'.*branch.*status.*',
                r'.*BRANCH.*STATUS.*',
            ],
            'allowed_dirs': ['/docs/git_workflow/branch-status/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.md']
        },
        {
            'name': 'migration_doc',
            'patterns': [
                r'.*migration.*complete.*',
                r'.*migration.*summary.*',
                r'.*migration.*status.*',
            ],
            'allowed_dirs': ['/docs/archived/migrations/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.md']
        },
        {
            'name': 'completion_summary',
            'patterns': [
                r'.*completion.*summary.*',
                r'.*implementation.*complete.*',
                r'.*task.*completion.*',
            ],
            'allowed_dirs': ['/docs/', '/docs/git_workflow/branch-status/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.md']
        },
        {
            'name': 'handoff_doc',
            'patterns': [
                r'.*handoff.*',
                r'.*HANDOFF.*',
            ],
            'allowed_dirs': ['/docs/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.md']
        },
        {
            'name': 'deployment_checklist',
            'patterns': [
                r'.*deployment.*checklist.*',
                r'.*deploy.*checklist.*',
            ],
            'allowed_dirs': ['/docs/deployment/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.md']
        },
        {
            'name': 'merge_checklist',
            'patterns': [
                r'.*merge.*checklist.*',
            ],
            'allowed_dirs': ['/docs/git_workflow/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.md']
        },
        {
            'name': 'implementation_summary',
            'patterns': [
                r'.*implementation.*summary.*',
                r'.*implementation.*progress.*',
            ],
            'allowed_dirs': ['/docs/', '/docs/archived/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.md']
        },
        {
            'name': 'testing_summary',
            'patterns': [
                r'.*testing.*summary.*',
                r'.*test.*report.*',
                r'.*system.*test.*',
            ],
            'allowed_dirs': ['/docs/testing/', '/docs/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.md']
        },
        {
            'name': 'future_tasks',
            'patterns': [
                r'.*future.*tasks.*',
                r'.*todo.*',
            ],
            'allowed_dirs': ['/docs/future-tasks/', '/tasks/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.md']
        },
        {
            'name': 'test_file',
            'patterns': [
                r'test_.*',
                r'.*_test',
            ],
            'allowed_dirs': ['/tests/unit/', '/tests/integration/', '/tests/e2e/'],
            'prohibited_dirs': ['/workspace/', '/modules/', '/'],
            'file_types': ['.py']
        },
        {
            'name': 'script_file',
            'patterns': [
                # Not test files, not main files
            ],
            'allowed_dirs': ['/scripts/', '/tools/', '/.claude/scripts/'],
            'prohibited_dirs': ['/workspace/', '/'],
            'file_types': ['.py', '.sh'],
            'custom_check': 'is_script_not_module'
        },
    ]

    def __init__(self, file_path: Path, project_root: Path = None):
        """
        Initialize validator for a file

        Args:
            file_path: Path to file to validate
            project_root: Project root directory (default: auto-detect)
        """
        self.file_path = Path(file_path).resolve()

        # Auto-detect project root if not provided
        if project_root is None:
            self.project_root = self._find_project_root()
        else:
            self.project_root = Path(project_root).resolve()

        self.violations: List[str] = []
        self.suggestions: List[str] = []

    def _find_project_root(self) -> Path:
        """Find project root by looking for .git or CLAUDE.md"""
        current = self.file_path.parent

        while current != current.parent:
            if (current / '.git').exists() or (current / 'CLAUDE.md').exists():
                return current
            current = current.parent

        # Fallback: assume current directory
        return Path.cwd()

    def validate(self) -> ValidationResult:
        """
        Validate file location against standards

        Returns:
            ValidationResult with validation status and suggestions
        """
        self.violations = []
        self.suggestions = []

        # Check if file exists
        if not self.file_path.exists():
            self.violations.append(f"File not found: {self.file_path}")
            return self._build_result()

        # Get relative path from project root
        try:
            rel_path = self.file_path.relative_to(self.project_root)
        except ValueError:
            # File is outside project root
            self.violations.append(f"File is outside project root: {self.file_path}")
            return self._build_result()

        # Check if file is in project root
        if len(rel_path.parts) == 1:
            return self._validate_root_file()

        # Check against placement rules
        self._check_placement_rules()

        return self._build_result()

    def _validate_root_file(self) -> ValidationResult:
        """Validate file in root directory"""
        filename = self.file_path.name

        # Check if file is in allowed list
        if filename in self.ROOT_ALLOWED_FILES:
            return self._build_result()  # Valid

        # File in root but not allowed
        self.violations.append(
            f"File '{filename}' should not be in root directory"
        )

        # Suggest appropriate location based on file type and name
        self._suggest_location_for_root_file(filename)

        return self._build_result()

    def _suggest_location_for_root_file(self, filename: str) -> None:
        """Suggest appropriate location for a root directory file"""
        filename_lower = filename.lower()

        # Check against all placement rules
        for rule in self.PLACEMENT_RULES:
            for pattern in rule.get('patterns', []):
                if re.match(pattern, filename_lower, re.IGNORECASE):
                    allowed_dirs = rule.get('allowed_dirs', [])
                    if allowed_dirs:
                        for allowed_dir in allowed_dirs:
                            suggested = f"{allowed_dir.rstrip('/')}/{filename}"
                            self.suggestions.append(suggested)
                    return

        # Generic suggestions based on extension
        ext = Path(filename).suffix

        if ext == '.md':
            self.suggestions.append(f"/docs/{filename}")
        elif ext == '.py':
            if filename.startswith('test_'):
                self.suggestions.append(f"/tests/unit/{filename}")
            else:
                self.suggestions.append(f"/scripts/{filename}")
        elif ext == '.sh':
            self.suggestions.append(f"/scripts/{filename}")
        else:
            self.suggestions.append(f"/docs/{filename}")

    def _check_placement_rules(self) -> None:
        """Check file against all placement rules"""
        filename = self.file_path.name
        filename_lower = filename.lower()
        file_ext = self.file_path.suffix
        current_dir = '/' + str(self.file_path.parent.relative_to(self.project_root))

        for rule in self.PLACEMENT_RULES:
            # Check if file type matches
            if file_ext not in rule.get('file_types', []):
                continue

            # Check if filename matches pattern
            pattern_match = False
            for pattern in rule.get('patterns', []):
                if re.match(pattern, filename_lower, re.IGNORECASE):
                    pattern_match = True
                    break

            if not pattern_match:
                continue

            # File matches this rule - check if in correct location
            allowed_dirs = rule.get('allowed_dirs', [])
            prohibited_dirs = rule.get('prohibited_dirs', [])

            # Check prohibited directories (higher priority)
            in_prohibited = any(
                current_dir.startswith(prohibited.rstrip('/'))
                for prohibited in prohibited_dirs
            )

            if in_prohibited:
                self.violations.append(
                    f"File matches '{rule['name']}' pattern but is in prohibited location"
                )
                # Add suggestions
                for allowed in allowed_dirs:
                    suggested = f"{allowed.rstrip('/')}/{filename}"
                    self.suggestions.append(suggested)
                return

            # Check if in allowed directory
            in_allowed = any(
                current_dir.startswith(allowed.rstrip('/'))
                for allowed in allowed_dirs
            )

            if not in_allowed and allowed_dirs:
                self.violations.append(
                    f"File matches '{rule['name']}' pattern but not in correct location"
                )
                for allowed in allowed_dirs:
                    suggested = f"{allowed.rstrip('/')}/{filename}"
                    self.suggestions.append(suggested)
                return

    def _build_result(self) -> ValidationResult:
        """Build ValidationResult from current state"""
        return ValidationResult(
            valid=len(self.violations) == 0,
            violations=self.violations,
            suggestions=self.suggestions,
            file_path=str(self.file_path)
        )


def validate_file(file_path: Path, project_root: Path = None) -> ValidationResult:
    """
    Validate a single file's location

    Args:
        file_path: Path to file to validate
        project_root: Project root directory

    Returns:
        ValidationResult
    """
    validator = LocationValidator(file_path, project_root)
    return validator.validate()


def scan_root_directory(project_root: Path = None) -> Tuple[int, int]:
    """
    Scan root directory for violations

    Args:
        project_root: Project root directory (default: auto-detect)

    Returns:
        Tuple of (valid_count, violation_count)
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    valid_count = 0
    violation_count = 0

    print(f"Scanning root directory: {project_root}\n")

    # Get all files in root directory (not subdirectories)
    root_files = [f for f in project_root.iterdir() if f.is_file()]

    for file_path in root_files:
        # Skip hidden files
        if file_path.name.startswith('.'):
            continue

        result = validate_file(file_path, project_root)

        if result.valid:
            valid_count += 1
        else:
            violation_count += 1
            print(result)
            print()

    return valid_count, violation_count


def validate_all(project_root: Path = None) -> Tuple[int, int]:
    """
    Validate all files in project

    Args:
        project_root: Project root directory

    Returns:
        Tuple of (valid_count, violation_count)
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    valid_count = 0
    violation_count = 0

    # Find all files (md, py, sh)
    extensions = ['*.md', '*.py', '*.sh']
    all_files = []

    for ext in extensions:
        all_files.extend(project_root.rglob(ext))

    print(f"Scanning {len(all_files)} files...\n")

    # Skip certain directories
    skip_dirs = ['node_modules', '.git', 'venv', 'project_venv', '__pycache__']

    for file_path in all_files:
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            continue

        result = validate_file(file_path, project_root)

        if result.valid:
            valid_count += 1
        else:
            violation_count += 1
            print(result)
            print()

    return valid_count, violation_count


# CLI Implementation
if HAS_CLICK:
    @click.command()
    @click.argument('file_path', type=click.Path(exists=True), required=False)
    @click.option('--scan-root', is_flag=True, help='Scan root directory for violations')
    @click.option('--all', 'validate_all_files', is_flag=True, help='Validate all files in project')
    @click.option('--project-root', type=click.Path(exists=True), help='Project root directory')
    def main(file_path: Optional[str], scan_root: bool, validate_all_files: bool, project_root: Optional[str]):
        """Validate file placement against FILE_ORGANIZATION_STANDARDS.md"""

        root = Path(project_root) if project_root else None

        if scan_root:
            valid, violations = scan_root_directory(root)
            print(f"\n{'='*60}")
            print(f"Results: {valid} valid, {violations} violations")
            sys.exit(0 if violations == 0 else 1)

        elif validate_all_files:
            valid, violations = validate_all(root)
            print(f"\n{'='*60}")
            print(f"Results: {valid} valid, {violations} violations")
            sys.exit(0 if violations == 0 else 1)

        elif file_path:
            result = validate_file(Path(file_path), root)
            print(result)
            sys.exit(0 if result.valid else 1)

        else:
            print("Error: Must provide FILE_PATH or use --scan-root/--all flag")
            sys.exit(1)

else:
    def main():
        parser = argparse.ArgumentParser(description='Validate file placement')
        parser.add_argument('file_path', nargs='?', help='Path to file')
        parser.add_argument('--scan-root', action='store_true', help='Scan root directory')
        parser.add_argument('--all', action='store_true', help='Validate all files')
        parser.add_argument('--project-root', help='Project root directory')

        args = parser.parse_args()

        root = Path(args.project_root) if args.project_root else None

        if args.scan_root:
            valid, violations = scan_root_directory(root)
            print(f"\n{'='*60}")
            print(f"Results: {valid} valid, {violations} violations")
            sys.exit(0 if violations == 0 else 1)

        elif args.all:
            valid, violations = validate_all(root)
            print(f"\n{'='*60}")
            print(f"Results: {valid} valid, {violations} violations")
            sys.exit(0 if violations == 0 else 1)

        elif args.file_path:
            result = validate_file(Path(args.file_path), root)
            print(result)
            sys.exit(0 if result.valid else 1)

        else:
            parser.print_help()
            sys.exit(1)


if __name__ == '__main__':
    main()
