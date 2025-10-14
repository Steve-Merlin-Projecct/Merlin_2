#!/usr/bin/env python3
"""
Database Connectivity Checker

Tests actual database connectivity for the Flask dashboard application.
Uses the DatabaseConfig from modules/database to ensure consistency with
the application's database connection logic.

This script performs:
- Database configuration validation
- Actual connection test to PostgreSQL
- Simple query execution (SELECT 1)
- Connection parameter reporting
- Detailed error diagnostics

Exit Codes:
    0: Database connection successful
    1: Database connection failed

Usage:
    python scripts/check_database.py

Author: Automated Job Application System
Version: 4.3.2
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class DatabaseChecker:
    """
    Database connectivity checker for Flask dashboard.

    Uses the application's DatabaseConfig to ensure connection
    parameters match what the application will use.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize database checker.

        Args:
            verbose: If True, print detailed output during checks
        """
        self.verbose = verbose
        self.project_root = self._find_project_root()
        self._add_project_to_path()

    def _find_project_root(self) -> Path:
        """
        Find the project root directory.

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
            "Could not find project root. app_modular.py not found."
        )

    def _add_project_to_path(self):
        """Add project root to Python path for imports"""
        sys.path.insert(0, str(self.project_root))

    def _print(self, message: str, color: str = ''):
        """Print message if verbose mode enabled"""
        if self.verbose:
            print(f"{color}{message}{Colors.RESET}")

    def _print_header(self, header: str):
        """Print section header"""
        self._print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
        self._print(f"{Colors.BOLD}{Colors.BLUE}{header}{Colors.RESET}")
        self._print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

    def load_database_config(self) -> Optional['DatabaseConfig']:
        """
        Load database configuration using application's DatabaseConfig.

        Returns:
            DatabaseConfig instance if successful, None if failed
        """
        self._print_header("Loading Database Configuration")

        try:
            from modules.database.database_config import DatabaseConfig

            config = DatabaseConfig()

            self._print(f"{Colors.GREEN}✓{Colors.RESET} Database config loaded successfully")
            self._print(f"  Environment: {Colors.BOLD}{'Docker' if config.is_docker else 'Local'}{Colors.RESET}")

            # Get connection parameters for display
            try:
                params = config.get_connection_params()
                self._print(f"  Host: {params['host']}")
                self._print(f"  Port: {params['port']}")
                self._print(f"  Database: {params['database']}")
                self._print(f"  User: {params['user']}")
                self._print(f"  Password: {'*' * 8}")
            except Exception as e:
                self._print(f"{Colors.YELLOW}⚠{Colors.RESET}  Could not parse connection params: {e}")

            return config

        except ImportError as e:
            self._print(f"{Colors.RED}✗{Colors.RESET} Failed to import DatabaseConfig")
            self._print(f"{Colors.RED}  Error: {e}{Colors.RESET}")
            self._print(f"{Colors.RED}  Solution: Ensure modules/database/database_config.py exists{Colors.RESET}")
            return None
        except ValueError as e:
            self._print(f"{Colors.RED}✗{Colors.RESET} Database configuration error")
            self._print(f"{Colors.RED}  Error: {e}{Colors.RESET}")
            self._print(f"{Colors.RED}  Solution: Check your environment variables (especially PGPASSWORD){Colors.RESET}")
            return None
        except Exception as e:
            self._print(f"{Colors.RED}✗{Colors.RESET} Unexpected error loading database config")
            self._print(f"{Colors.RED}  Error: {e}{Colors.RESET}")
            return None

    def test_postgresql_connection(self, config: 'DatabaseConfig') -> bool:
        """
        Test actual connection to PostgreSQL database.

        Args:
            config: DatabaseConfig instance

        Returns:
            bool: True if connection successful
        """
        self._print_header("Testing PostgreSQL Connection")

        try:
            import psycopg2
            from psycopg2 import OperationalError

            # Get connection parameters
            params = config.get_connection_params()

            self._print(f"Connecting to PostgreSQL...")
            self._print(f"  Host: {params['host']}")
            self._print(f"  Port: {params['port']}")
            self._print(f"  Database: {params['database']}")

            # Attempt connection
            conn = psycopg2.connect(
                host=params['host'],
                port=params['port'],
                database=params['database'],
                user=params['user'],
                password=params['password'],
                connect_timeout=5
            )

            self._print(f"{Colors.GREEN}✓{Colors.RESET} Successfully connected to PostgreSQL")

            # Test simple query
            self._print(f"\nExecuting test query (SELECT 1)...")
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()

            if result and result[0] == 1:
                self._print(f"{Colors.GREEN}✓{Colors.RESET} Test query executed successfully")
            else:
                self._print(f"{Colors.RED}✗{Colors.RESET} Test query returned unexpected result: {result}")
                conn.close()
                return False

            # Get PostgreSQL version
            self._print(f"\nRetrieving PostgreSQL version...")
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.close()

            # Extract just the PostgreSQL version number
            version_short = version.split(',')[0] if ',' in version else version.split(' on ')[0]
            self._print(f"{Colors.GREEN}✓{Colors.RESET} {version_short}")

            # Close connection
            conn.close()
            self._print(f"\n{Colors.GREEN}✓{Colors.RESET} Connection closed cleanly")

            return True

        except ImportError:
            self._print(f"{Colors.RED}✗{Colors.RESET} psycopg2 not installed")
            self._print(f"{Colors.RED}  Solution: Install with: pip install psycopg2-binary{Colors.RESET}")
            return False

        except OperationalError as e:
            error_msg = str(e)
            self._print(f"{Colors.RED}✗{Colors.RESET} PostgreSQL connection failed")
            self._print(f"{Colors.RED}  Error: {error_msg}{Colors.RESET}")

            # Provide specific guidance based on error
            if 'Connection refused' in error_msg:
                self._print(f"\n{Colors.YELLOW}Troubleshooting Connection Refused:{Colors.RESET}")
                self._print(f"  1. Is PostgreSQL running?")
                self._print(f"     Check with: sudo systemctl status postgresql")
                self._print(f"     Or: sudo service postgresql status")
                self._print(f"  2. Is PostgreSQL listening on {params['host']}:{params['port']}?")
                self._print(f"     Check postgresql.conf for listen_addresses")
                self._print(f"  3. Is there a firewall blocking the connection?")

            elif 'password authentication failed' in error_msg:
                self._print(f"\n{Colors.YELLOW}Troubleshooting Authentication Failed:{Colors.RESET}")
                self._print(f"  1. Check PGPASSWORD environment variable")
                self._print(f"  2. Verify password in .env file")
                self._print(f"  3. Ensure user '{params['user']}' has correct password")
                self._print(f"     Reset with: sudo -u postgres psql -c \"ALTER USER {params['user']} PASSWORD 'newpassword';\"")

            elif 'database' in error_msg and 'does not exist' in error_msg:
                self._print(f"\n{Colors.YELLOW}Troubleshooting Database Not Found:{Colors.RESET}")
                self._print(f"  1. Database '{params['database']}' does not exist")
                self._print(f"     Create with: sudo -u postgres createdb {params['database']}")
                self._print(f"  2. Or connect as postgres and run:")
                self._print(f"     CREATE DATABASE {params['database']};")

            elif 'timeout' in error_msg:
                self._print(f"\n{Colors.YELLOW}Troubleshooting Connection Timeout:{Colors.RESET}")
                self._print(f"  1. Network issue or PostgreSQL not responding")
                self._print(f"  2. Check if host '{params['host']}' is reachable")
                self._print(f"  3. Verify PostgreSQL is accepting connections")

            else:
                self._print(f"\n{Colors.YELLOW}General Troubleshooting:{Colors.RESET}")
                self._print(f"  1. Verify PostgreSQL is running")
                self._print(f"  2. Check connection parameters in .env file")
                self._print(f"  3. Review PostgreSQL logs for details")

            return False

        except Exception as e:
            self._print(f"{Colors.RED}✗{Colors.RESET} Unexpected error testing database connection")
            self._print(f"{Colors.RED}  Error: {e}{Colors.RESET}")
            return False

    def check_database(self) -> bool:
        """
        Run all database checks.

        Returns:
            bool: True if all checks pass
        """
        self._print(f"{Colors.BOLD}Starting Database Connectivity Check{Colors.RESET}")
        self._print(f"Project Root: {self.project_root}\n")

        # Load database configuration
        config = self.load_database_config()
        if not config:
            return False

        # Test PostgreSQL connection
        if not self.test_postgresql_connection(config):
            return False

        # All checks passed
        self._print_header("Database Check Summary")
        self._print(f"{Colors.GREEN}{Colors.BOLD}✓ Database connectivity check passed!{Colors.RESET}\n")

        return True


def main():
    """Main entry point for database connectivity check"""
    try:
        checker = DatabaseChecker(verbose=True)

        if checker.check_database():
            print(f"{Colors.GREEN}Database is accessible and working correctly!{Colors.RESET}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}Database connectivity check failed. Please fix the errors above.{Colors.RESET}")
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        print(f"{Colors.RED}Make sure you're running this script from the project directory.{Colors.RESET}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Database check interrupted by user.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error during database check: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
