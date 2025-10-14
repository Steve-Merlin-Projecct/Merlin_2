#!/usr/bin/env python3
"""
Environment Validation Script

Validates that all required environment variables and files are present
before starting the Flask dashboard application.

This script performs comprehensive validation:
- Checks for required environment variables
- Validates environment variable formats and values
- Verifies required files and directories exist
- Provides actionable error messages for any failures

Exit Codes:
    0: All validation checks passed
    1: One or more validation checks failed

Usage:
    python scripts/validate_environment.py

Author: Automated Job Application System
Version: 4.3.2
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class EnvironmentValidator:
    """
    Validates environment configuration for Flask dashboard.

    Performs comprehensive checks on:
    - Required environment variables
    - Optional environment variables with defaults
    - File system structure
    - Configuration file formats
    """

    # Required environment variables (must be present)
    REQUIRED_ENV_VARS = [
        'PGPASSWORD',  # Database password (required for all environments)
    ]

    # Optional environment variables with defaults
    OPTIONAL_ENV_VARS = {
        'DATABASE_NAME': 'local_Merlin_3',
        'DATABASE_HOST': 'localhost',
        'DATABASE_PORT': '5432',
        'DATABASE_USER': 'postgres',
        'LOG_LEVEL': 'INFO',
        'LOG_FORMAT': 'human',
    }

    # Required files relative to project root
    REQUIRED_FILES = [
        'app_modular.py',
        'modules/database/database_config.py',
        'modules/database/database_api.py',
        'frontend_templates/dashboard_v2.html',
        'frontend_templates/dashboard_login.html',
    ]

    # Required directories relative to project root
    REQUIRED_DIRECTORIES = [
        'modules',
        'modules/database',
        'frontend_templates',
        'scripts',
    ]

    def __init__(self, verbose: bool = True):
        """
        Initialize environment validator.

        Args:
            verbose: If True, print detailed output during validation
        """
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.project_root = self._find_project_root()

    def _find_project_root(self) -> Path:
        """
        Find the project root directory.

        Searches upward from current directory for app_modular.py
        which indicates the project root.

        Returns:
            Path: Project root directory

        Raises:
            FileNotFoundError: If project root cannot be found
        """
        current = Path.cwd()

        # Try current directory first
        if (current / 'app_modular.py').exists():
            return current

        # Try parent directories (for worktrees)
        for parent in current.parents:
            if (parent / 'app_modular.py').exists():
                return parent

        raise FileNotFoundError(
            "Could not find project root. app_modular.py not found in current "
            "directory or parent directories."
        )

    def _print(self, message: str, color: str = ''):
        """Print message if verbose mode enabled"""
        if self.verbose:
            print(f"{color}{message}{Colors.RESET}")

    def _print_header(self, header: str):
        """Print section header"""
        self._print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
        self._print(f"{Colors.BOLD}{Colors.BLUE}{header}{Colors.RESET}")
        self._print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

    def check_env_file(self) -> bool:
        """
        Check for .env file accessibility.

        In git worktrees, the .env file may be in the parent workspace.
        This function checks both locations.

        Returns:
            bool: True if .env file is accessible
        """
        self._print_header("Checking .env File Accessibility")

        # Check current directory
        local_env = self.project_root / '.env'
        if local_env.exists():
            self._print(f"{Colors.GREEN}✓{Colors.RESET} Found .env at: {local_env}")
            return True

        # Check parent workspace (for worktrees)
        parent_workspace = self.project_root.parent.parent / '.env'
        if parent_workspace.exists():
            self._print(f"{Colors.YELLOW}⚠{Colors.RESET}  Found .env in parent workspace: {parent_workspace}")
            self._print(f"{Colors.YELLOW}⚠{Colors.RESET}  This is a git worktree. Environment variables may not be loaded automatically.")
            self.warnings.append(
                ".env file is in parent workspace. You may need to:\n"
                f"  1. Create symlink: ln -s {parent_workspace} {local_env}\n"
                f"  2. Or copy file: cp {parent_workspace} {local_env}\n"
                f"  3. Or run: scripts/setup_worktree_env.sh"
            )
            return True

        self.errors.append(
            ".env file not found in project root or parent workspace.\n"
            "  Solution: Create .env file with required environment variables:\n"
            "    PGPASSWORD=your_database_password\n"
            "    DATABASE_NAME=local_Merlin_3\n"
            "  Or if working in git worktree, run: scripts/setup_worktree_env.sh"
        )
        self._print(f"{Colors.RED}✗{Colors.RESET} .env file not found")
        return False

    def check_required_env_vars(self) -> bool:
        """
        Check that all required environment variables are set.

        Returns:
            bool: True if all required variables are present
        """
        self._print_header("Checking Required Environment Variables")

        all_present = True

        for var in self.REQUIRED_ENV_VARS:
            value = os.environ.get(var)

            if not value:
                self.errors.append(
                    f"Required environment variable '{var}' is not set.\n"
                    f"  Solution: Set {var} in .env file or export {var}=your_value"
                )
                self._print(f"{Colors.RED}✗{Colors.RESET} {var}: NOT SET")
                all_present = False
            else:
                # Mask sensitive values in output
                display_value = '****' if 'PASSWORD' in var or 'SECRET' in var or 'KEY' in var else value
                self._print(f"{Colors.GREEN}✓{Colors.RESET} {var}: {display_value}")

        return all_present

    def check_optional_env_vars(self) -> bool:
        """
        Check optional environment variables and report defaults being used.

        Returns:
            bool: Always True (optional vars cannot fail validation)
        """
        self._print_header("Checking Optional Environment Variables")

        for var, default in self.OPTIONAL_ENV_VARS.items():
            value = os.environ.get(var)

            if not value:
                self._print(f"{Colors.YELLOW}⚠{Colors.RESET}  {var}: Using default '{default}'")
            else:
                self._print(f"{Colors.GREEN}✓{Colors.RESET} {var}: {value}")

        return True

    def check_required_files(self) -> bool:
        """
        Check that all required files exist.

        Returns:
            bool: True if all required files exist
        """
        self._print_header("Checking Required Files")

        all_exist = True

        for file_path in self.REQUIRED_FILES:
            full_path = self.project_root / file_path

            if not full_path.exists():
                self.errors.append(
                    f"Required file missing: {file_path}\n"
                    f"  Expected at: {full_path}\n"
                    f"  Solution: Ensure you're in the correct project directory and all files are present"
                )
                self._print(f"{Colors.RED}✗{Colors.RESET} {file_path}")
                all_exist = False
            else:
                self._print(f"{Colors.GREEN}✓{Colors.RESET} {file_path}")

        return all_exist

    def check_required_directories(self) -> bool:
        """
        Check that all required directories exist.

        Returns:
            bool: True if all required directories exist
        """
        self._print_header("Checking Required Directories")

        all_exist = True

        for dir_path in self.REQUIRED_DIRECTORIES:
            full_path = self.project_root / dir_path

            if not full_path.exists():
                self.errors.append(
                    f"Required directory missing: {dir_path}\n"
                    f"  Expected at: {full_path}\n"
                    f"  Solution: Ensure you're in the correct project directory"
                )
                self._print(f"{Colors.RED}✗{Colors.RESET} {dir_path}")
                all_exist = False
            else:
                self._print(f"{Colors.GREEN}✓{Colors.RESET} {dir_path}")

        return all_exist

    def validate(self) -> bool:
        """
        Run all validation checks.

        Returns:
            bool: True if all validation checks pass
        """
        self._print(f"{Colors.BOLD}Starting Environment Validation{Colors.RESET}")
        self._print(f"Project Root: {self.project_root}\n")

        # Run all checks
        checks = [
            self.check_env_file(),
            self.check_required_env_vars(),
            self.check_optional_env_vars(),
            self.check_required_files(),
            self.check_required_directories(),
        ]

        all_passed = all(checks)

        # Print summary
        self._print_header("Validation Summary")

        if all_passed and not self.warnings:
            self._print(f"{Colors.GREEN}{Colors.BOLD}✓ All validation checks passed!{Colors.RESET}\n")
            return True

        if self.warnings:
            self._print(f"{Colors.YELLOW}{Colors.BOLD}Warnings:{Colors.RESET}")
            for warning in self.warnings:
                self._print(f"{Colors.YELLOW}{warning}{Colors.RESET}\n")

        if not all_passed:
            self._print(f"{Colors.RED}{Colors.BOLD}✗ Validation failed with {len(self.errors)} error(s):{Colors.RESET}\n")
            for i, error in enumerate(self.errors, 1):
                self._print(f"{Colors.RED}{i}. {error}{Colors.RESET}\n")
            return False

        return True


def main():
    """Main entry point for environment validation"""
    try:
        validator = EnvironmentValidator(verbose=True)

        if validator.validate():
            print(f"\n{Colors.GREEN}Environment validation successful!{Colors.RESET}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}Environment validation failed. Please fix the errors above.{Colors.RESET}")
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        print(f"{Colors.RED}Make sure you're running this script from the project directory.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error during validation: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()
