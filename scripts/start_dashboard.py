#!/usr/bin/env python3
"""
Smart Application Launcher for Flask Dashboard

Performs comprehensive validation before starting the Flask dashboard:
1. Environment validation (environment variables, files, directories)
2. Database connectivity check
3. Port availability check
4. Graceful startup with error handling

This launcher ensures the application only starts if all prerequisites are met,
providing clear diagnostic information for any failures.

Exit Codes:
    0: Application started successfully (or validation passed in check-only mode)
    1: Validation failed, application not started
    2: Application startup failed

Usage:
    python scripts/start_dashboard.py [options]

    Options:
        --check-only        Run validation checks without starting the app
        --skip-db-check     Skip database connectivity check
        --production        Run in production mode (debug=False)
        --port PORT         Specify port (default: 5001)
        --host HOST         Specify host (default: 0.0.0.0)

Examples:
    python scripts/start_dashboard.py
    python scripts/start_dashboard.py --check-only
    python scripts/start_dashboard.py --production --port 8080

Author: Automated Job Application System
Version: 4.3.2
"""

import os
import sys
import signal
import argparse
import socket
from pathlib import Path
from typing import Optional
import subprocess


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class DashboardLauncher:
    """
    Smart launcher for Flask dashboard application.

    Performs validation pipeline before starting the application:
    - Environment validation
    - Database connectivity check
    - Port availability check
    - Graceful shutdown handling
    """

    def __init__(
        self,
        check_only: bool = False,
        skip_db_check: bool = False,
        production: bool = False,
        host: str = '0.0.0.0',
        port: int = 5001
    ):
        """
        Initialize dashboard launcher.

        Args:
            check_only: If True, run checks but don't start app
            skip_db_check: If True, skip database connectivity check
            production: If True, run in production mode (debug=False)
            host: Host to bind to
            port: Port to bind to
        """
        self.check_only = check_only
        self.skip_db_check = skip_db_check
        self.production = production
        self.host = host
        self.port = port
        self.project_root = self._find_project_root()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

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

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        signal_name = signal.Signals(signum).name
        print(f"\n{Colors.YELLOW}Received {signal_name}, shutting down gracefully...{Colors.RESET}")
        sys.exit(0)

    def _print_header(self, header: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{header}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    def _print_step(self, step_num: int, total_steps: int, description: str):
        """Print step progress"""
        print(f"{Colors.BOLD}[{step_num}/{total_steps}]{Colors.RESET} {description}...")

    def validate_environment(self) -> bool:
        """
        Run environment validation checks.

        Returns:
            bool: True if validation passed
        """
        self._print_step(1, 4 if not self.skip_db_check else 3, "Validating environment")

        # Change to project root for validation
        os.chdir(self.project_root)

        # Import and run environment validator
        try:
            sys.path.insert(0, str(self.project_root))
            from scripts.validate_environment import EnvironmentValidator

            validator = EnvironmentValidator(verbose=True)
            if validator.validate():
                print(f"{Colors.GREEN}✓ Environment validation passed{Colors.RESET}\n")
                return True
            else:
                print(f"{Colors.RED}✗ Environment validation failed{Colors.RESET}\n")
                return False

        except ImportError as e:
            print(f"{Colors.RED}✗ Could not import environment validator: {e}{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}✗ Environment validation error: {e}{Colors.RESET}")
            return False

    def check_database(self) -> bool:
        """
        Check database connectivity.

        Returns:
            bool: True if database is accessible
        """
        if self.skip_db_check:
            print(f"{Colors.YELLOW}⚠ Skipping database check (--skip-db-check){Colors.RESET}\n")
            return True

        self._print_step(2, 4, "Checking database connectivity")

        try:
            from scripts.check_database import DatabaseChecker

            checker = DatabaseChecker(verbose=True)
            if checker.check_database():
                print(f"{Colors.GREEN}✓ Database connectivity check passed{Colors.RESET}\n")
                return True
            else:
                print(f"{Colors.RED}✗ Database connectivity check failed{Colors.RESET}\n")
                return False

        except ImportError as e:
            print(f"{Colors.RED}✗ Could not import database checker: {e}{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}✗ Database check error: {e}{Colors.RESET}")
            return False

    def check_port_available(self) -> bool:
        """
        Check if the specified port is available.

        Returns:
            bool: True if port is available
        """
        step_num = 3 if not self.skip_db_check else 2
        total_steps = 4 if not self.skip_db_check else 3
        self._print_step(step_num, total_steps, f"Checking port {self.port} availability")

        try:
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.host, self.port))
            sock.close()

            if result == 0:
                # Port is in use
                print(f"{Colors.RED}✗ Port {self.port} is already in use{Colors.RESET}")
                print(f"{Colors.YELLOW}  Solution: Either stop the service using port {self.port} or use a different port{Colors.RESET}")
                print(f"{Colors.YELLOW}  Find process: lsof -i :{self.port} or netstat -tulpn | grep {self.port}{Colors.RESET}\n")
                return False
            else:
                # Port is available
                print(f"{Colors.GREEN}✓ Port {self.port} is available{Colors.RESET}\n")
                return True

        except Exception as e:
            print(f"{Colors.YELLOW}⚠ Could not check port availability: {e}{Colors.RESET}")
            print(f"{Colors.YELLOW}  Proceeding anyway...{Colors.RESET}\n")
            return True

    def start_application(self) -> bool:
        """
        Start the Flask application.

        Returns:
            bool: True if application started successfully (always True, actual errors raise)
        """
        step_num = 4 if not self.skip_db_check else 3
        total_steps = 4 if not self.skip_db_check else 3
        self._print_step(step_num, total_steps, "Starting Flask application")

        try:
            # Change to project root
            os.chdir(self.project_root)

            # Add project root to Python path
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.GREEN}Starting Merlin Job Application Dashboard{Colors.RESET}")
            print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
            print(f"  Environment: {Colors.BOLD}{'Production' if self.production else 'Development'}{Colors.RESET}")
            print(f"  Host: {Colors.BOLD}{self.host}{Colors.RESET}")
            print(f"  Port: {Colors.BOLD}{self.port}{Colors.RESET}")
            print(f"  URL: {Colors.BOLD}{Colors.CYAN}http://{self.host if self.host != '0.0.0.0' else 'localhost'}:{self.port}{Colors.RESET}")
            print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}\n")

            # Import and run Flask app
            from app_modular import app

            # Disable Flask banner in production
            if self.production:
                os.environ['WERKZEUG_RUN_MAIN'] = 'true'

            app.run(
                debug=not self.production,
                host=self.host,
                port=self.port,
                use_reloader=not self.production  # Disable reloader in production
            )

            return True

        except ImportError as e:
            print(f"\n{Colors.RED}✗ Failed to import Flask application: {e}{Colors.RESET}")
            print(f"{Colors.RED}  Make sure you're in the correct project directory{Colors.RESET}")
            return False
        except Exception as e:
            print(f"\n{Colors.RED}✗ Failed to start Flask application: {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()
            return False

    def run(self) -> int:
        """
        Run the validation pipeline and start the application.

        Returns:
            int: Exit code (0 = success, 1 = validation failed, 2 = startup failed)
        """
        self._print_header("Flask Dashboard Startup Validation")
        print(f"Project Root: {Colors.BOLD}{self.project_root}{Colors.RESET}")
        print(f"Mode: {Colors.BOLD}{'Check Only' if self.check_only else ('Production' if self.production else 'Development')}{Colors.RESET}\n")

        # Run validation pipeline
        validation_steps = [
            ("Environment", self.validate_environment),
            ("Database", self.check_database),
            ("Port", self.check_port_available),
        ]

        for step_name, step_func in validation_steps:
            if not step_func():
                self._print_header("Startup Failed")
                print(f"{Colors.RED}✗ {step_name} check failed. Cannot start application.{Colors.RESET}")
                print(f"{Colors.RED}  Please fix the errors above and try again.{Colors.RESET}\n")
                return 1

        # All validation passed
        self._print_header("Validation Complete")
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All validation checks passed!{Colors.RESET}\n")

        if self.check_only:
            print(f"{Colors.CYAN}Running in check-only mode. Exiting without starting application.{Colors.RESET}")
            return 0

        # Start the application
        if not self.start_application():
            self._print_header("Startup Failed")
            print(f"{Colors.RED}✗ Failed to start Flask application.{Colors.RESET}\n")
            return 2

        return 0


def main():
    """Main entry point for dashboard launcher"""
    parser = argparse.ArgumentParser(
        description='Smart launcher for Flask Dashboard with validation pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/start_dashboard.py
  python scripts/start_dashboard.py --check-only
  python scripts/start_dashboard.py --production --port 8080
  python scripts/start_dashboard.py --skip-db-check
        """
    )

    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Run validation checks without starting the application'
    )
    parser.add_argument(
        '--skip-db-check',
        action='store_true',
        help='Skip database connectivity check'
    )
    parser.add_argument(
        '--production',
        action='store_true',
        help='Run in production mode (debug=False, no reloader)'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Port to bind to (default: 5001)'
    )

    args = parser.parse_args()

    try:
        launcher = DashboardLauncher(
            check_only=args.check_only,
            skip_db_check=args.skip_db_check,
            production=args.production,
            host=args.host,
            port=args.port
        )

        exit_code = launcher.run()
        sys.exit(exit_code)

    except FileNotFoundError as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        print(f"{Colors.RED}Make sure you're running this script from the project directory.{Colors.RESET}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Startup interrupted by user.{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
