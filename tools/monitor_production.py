#!/usr/bin/env python3
"""
Production Log Monitor CLI

A command-line tool for querying and analyzing production logs from the development environment.
Connects to the production monitoring API to retrieve logs, metrics, and traces.

Features:
- Query logs with filters (level, time range, search)
- View error summaries and recent errors
- Trace specific requests by correlation ID
- Check system health and metrics
- Support for both local and remote production servers

Usage:
    # Query recent errors
    python tools/monitor_production.py logs --level ERROR --limit 50

    # Search for specific text
    python tools/monitor_production.py logs --search "database" --minutes 60

    # Trace a request
    python tools/monitor_production.py trace <correlation-id>

    # Check health
    python tools/monitor_production.py health

    # View metrics
    python tools/monitor_production.py metrics --path /api/db/jobs

    # Query production server
    python tools/monitor_production.py --host https://prod.example.com logs --level ERROR
"""

import argparse
import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import urljoin

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class ProductionMonitor:
    """
    Client for querying production monitoring API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:5001",
        api_key: Optional[str] = None
    ):
        """
        Initialize production monitor client.

        Args:
            base_url: Base URL of the production server
            api_key: API key for authentication (defaults to MONITORING_API_KEY env var)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.environ.get('MONITORING_API_KEY') or os.environ.get('WEBHOOK_API_KEY')

        if not self.api_key:
            print(f"{Colors.YELLOW}Warning: No API key found. Set MONITORING_API_KEY environment variable.{Colors.RESET}")

    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to monitoring API.

        Args:
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            json_data: JSON request body

        Returns:
            Response JSON data

        Raises:
            requests.RequestException: On request failure
        """
        url = urljoin(self.base_url, endpoint)
        headers = {}

        if self.api_key:
            headers['X-Monitoring-Key'] = self.api_key

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"{Colors.RED}Error connecting to {url}: {e}{Colors.RESET}")
            sys.exit(1)

    def query_logs(
        self,
        level: Optional[str] = None,
        correlation_id: Optional[str] = None,
        search: Optional[str] = None,
        minutes: Optional[int] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Query application logs.

        Args:
            level: Log level filter
            correlation_id: Correlation ID filter
            search: Search message text
            minutes: Time window in minutes
            limit: Maximum results

        Returns:
            Log query results
        """
        params = {'limit': limit}

        if level:
            params['level'] = level.upper()
        if correlation_id:
            params['correlation_id'] = correlation_id
        if search:
            params['search'] = search
        if minutes:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=minutes)
            params['start_time'] = start_time.isoformat() + 'Z'
            params['end_time'] = end_time.isoformat() + 'Z'

        return self._make_request('/api/monitoring/logs', params=params)

    def query_errors(
        self,
        minutes: int = 60,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Query error logs and summaries.

        Args:
            minutes: Time window in minutes
            limit: Maximum error entries

        Returns:
            Error summary and recent errors
        """
        params = {
            'minutes': minutes,
            'limit': limit
        }

        return self._make_request('/api/monitoring/errors', params=params)

    def trace_request(self, correlation_id: str) -> Dict[str, Any]:
        """
        Trace a specific request by correlation ID.

        Args:
            correlation_id: Request correlation ID

        Returns:
            Request trace with timeline
        """
        return self._make_request(
            '/api/monitoring/trace',
            method='POST',
            json_data={'correlation_id': correlation_id}
        )

    def get_health(self, detailed: bool = True) -> Dict[str, Any]:
        """
        Get system health status.

        Args:
            detailed: Include detailed component checks

        Returns:
            Health check results
        """
        params = {'detailed': str(detailed).lower()}
        return self._make_request('/api/monitoring/health', params=params)

    def get_metrics(
        self,
        path: Optional[str] = None,
        minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get performance metrics.

        Args:
            path: Filter by specific path
            minutes: Time window in minutes

        Returns:
            Performance metrics
        """
        params = {'minutes': minutes}
        if path:
            params['path'] = path

        return self._make_request('/api/monitoring/metrics', params=params)


def print_logs(data: Dict[str, Any]) -> None:
    """Print log query results in formatted output."""
    if not data.get('success'):
        print(f"{Colors.RED}Error: {data.get('error')}{Colors.RESET}")
        return

    logs = data.get('logs', [])
    count = data.get('count', 0)

    print(f"\n{Colors.BOLD}Log Query Results{Colors.RESET}")
    print(f"Total: {count} entries\n")

    for log in logs:
        # Color code by level
        level = log.get('level', 'INFO')
        if level == 'ERROR':
            color = Colors.RED
        elif level == 'WARNING':
            color = Colors.YELLOW
        elif level == 'INFO':
            color = Colors.GREEN
        else:
            color = Colors.CYAN

        timestamp = log.get('timestamp', '')
        logger = log.get('logger', '')
        message = log.get('message', '')
        correlation_id = log.get('correlation_id', '')

        print(f"{color}{level:8}{Colors.RESET} {timestamp} [{logger}]")
        print(f"  {message}")
        if correlation_id:
            print(f"  {Colors.CYAN}Correlation ID: {correlation_id}{Colors.RESET}")
        print()


def print_errors(data: Dict[str, Any]) -> None:
    """Print error summary in formatted output."""
    if not data.get('success'):
        print(f"{Colors.RED}Error: {data.get('error')}{Colors.RESET}")
        return

    total_errors = data.get('total_errors', 0)
    summary = data.get('summary', {})
    recent_errors = data.get('recent_errors', [])

    print(f"\n{Colors.BOLD}Error Summary{Colors.RESET}")
    print(f"Total Errors: {Colors.RED}{total_errors}{Colors.RESET}\n")

    if summary:
        by_type = summary.get('by_type', {})
        if by_type:
            print(f"{Colors.BOLD}By Type:{Colors.RESET}")
            for error_type, info in by_type.items():
                count = info.get('count', 0)
                print(f"  {error_type}: {count}")
            print()

    if recent_errors:
        print(f"{Colors.BOLD}Recent Errors:{Colors.RESET}\n")
        for error in recent_errors[:10]:  # Show last 10
            timestamp = error.get('timestamp', '')
            logger = error.get('logger', '')
            message = error.get('message', '')
            error_type = error.get('error_type', 'Unknown')

            print(f"{Colors.RED}ERROR{Colors.RESET} {timestamp} [{logger}]")
            print(f"  Type: {error_type}")
            print(f"  {message}")
            print()


def print_trace(data: Dict[str, Any]) -> None:
    """Print request trace in formatted output."""
    if not data.get('success'):
        print(f"{Colors.RED}Error: {data.get('error')}{Colors.RESET}")
        return

    trace = data.get('trace', {})
    correlation_id = trace.get('correlation_id', '')
    start_time = trace.get('start_time', '')
    total_duration = trace.get('total_duration_ms', 0)
    timeline = trace.get('timeline', [])

    print(f"\n{Colors.BOLD}Request Trace{Colors.RESET}")
    print(f"Correlation ID: {Colors.CYAN}{correlation_id}{Colors.RESET}")
    print(f"Start Time: {start_time}")
    print(f"Total Duration: {Colors.YELLOW}{total_duration:.2f}ms{Colors.RESET}\n")

    print(f"{Colors.BOLD}Timeline:{Colors.RESET}\n")
    for event in timeline:
        seq = event.get('sequence', 0)
        timestamp = event.get('timestamp', '')
        level = event.get('level', 'INFO')
        message = event.get('message', '')
        elapsed = event.get('elapsed_ms', 0)

        # Color code by level
        if level == 'ERROR':
            color = Colors.RED
        elif level == 'WARNING':
            color = Colors.YELLOW
        else:
            color = Colors.GREEN

        print(f"{seq:3}. {color}{level:8}{Colors.RESET} {message}")
        if elapsed:
            print(f"     {Colors.CYAN}+{elapsed:.2f}ms{Colors.RESET}")


def print_health(data: Dict[str, Any]) -> None:
    """Print health check results in formatted output."""
    overall_status = data.get('overall_status', 'unknown')
    checks = data.get('checks', {})

    # Color code overall status
    if overall_status == 'healthy':
        status_color = Colors.GREEN
    else:
        status_color = Colors.RED

    print(f"\n{Colors.BOLD}System Health{Colors.RESET}")
    print(f"Overall Status: {status_color}{overall_status.upper()}{Colors.RESET}\n")

    if checks:
        print(f"{Colors.BOLD}Component Checks:{Colors.RESET}\n")
        for name, result in checks.items():
            status = result.get('status', 'unknown')
            message = result.get('message', '')

            if status == 'healthy':
                color = Colors.GREEN
                symbol = '✓'
            else:
                color = Colors.RED
                symbol = '✗'

            print(f"{color}{symbol} {name:15}{Colors.RESET} {message}")


def print_metrics(data: Dict[str, Any]) -> None:
    """Print metrics in formatted output."""
    if not data.get('success'):
        print(f"{Colors.RED}Error: {data.get('error')}{Colors.RESET}")
        return

    request_metrics = data.get('request_metrics', {})
    custom_metrics = data.get('custom_metrics', {})
    errors = data.get('errors', {})

    print(f"\n{Colors.BOLD}Performance Metrics{Colors.RESET}\n")

    if request_metrics:
        print(f"{Colors.BOLD}Request Metrics:{Colors.RESET}\n")
        for path, metrics in request_metrics.items():
            total_requests = metrics.get('total_requests', 0)
            avg_duration = metrics.get('avg_duration_ms', 0)
            total_errors = metrics.get('total_errors', 0)

            print(f"{Colors.CYAN}{path}{Colors.RESET}")
            print(f"  Requests: {total_requests}")
            print(f"  Avg Duration: {avg_duration:.2f}ms")
            print(f"  Errors: {total_errors}")
            print()

    if custom_metrics:
        print(f"{Colors.BOLD}Custom Metrics:{Colors.RESET}\n")
        for name, metrics in custom_metrics.items():
            count = metrics.get('count', 0)
            avg = metrics.get('avg', 0)
            max_val = metrics.get('max', 0)

            print(f"{name}: count={count}, avg={avg:.2f}, max={max_val:.2f}")

    if errors:
        total_errors = errors.get('total_errors', 0)
        if total_errors > 0:
            print(f"\n{Colors.RED}Errors: {total_errors}{Colors.RESET}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Production Log Monitor CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query recent errors
  python tools/monitor_production.py logs --level ERROR --limit 50

  # Search for specific text
  python tools/monitor_production.py logs --search "database" --minutes 60

  # Trace a request
  python tools/monitor_production.py trace abc-123-def

  # Check health
  python tools/monitor_production.py health

  # View metrics
  python tools/monitor_production.py metrics --path /api/db/jobs
        """
    )

    parser.add_argument(
        '--host',
        default='http://localhost:5001',
        help='Production server base URL (default: http://localhost:5001)'
    )
    parser.add_argument(
        '--api-key',
        help='API key for authentication (default: from MONITORING_API_KEY env var)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Query application logs')
    logs_parser.add_argument('--level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                           help='Filter by log level')
    logs_parser.add_argument('--correlation-id', help='Filter by correlation ID')
    logs_parser.add_argument('--search', help='Search message text')
    logs_parser.add_argument('--minutes', type=int, help='Time window in minutes')
    logs_parser.add_argument('--limit', type=int, default=100, help='Maximum results (default: 100)')

    # Errors command
    errors_parser = subparsers.add_parser('errors', help='Query error logs')
    errors_parser.add_argument('--minutes', type=int, default=60, help='Time window in minutes (default: 60)')
    errors_parser.add_argument('--limit', type=int, default=50, help='Maximum error entries (default: 50)')

    # Trace command
    trace_parser = subparsers.add_parser('trace', help='Trace request by correlation ID')
    trace_parser.add_argument('correlation_id', help='Request correlation ID')

    # Health command
    health_parser = subparsers.add_parser('health', help='Check system health')
    health_parser.add_argument('--simple', action='store_true', help='Simple health check without details')

    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Get performance metrics')
    metrics_parser.add_argument('--path', help='Filter by specific path')
    metrics_parser.add_argument('--minutes', type=int, default=60, help='Time window in minutes (default: 60)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize monitor client
    monitor = ProductionMonitor(base_url=args.host, api_key=args.api_key)

    # Execute command
    try:
        if args.command == 'logs':
            data = monitor.query_logs(
                level=args.level,
                correlation_id=args.correlation_id,
                search=args.search,
                minutes=args.minutes,
                limit=args.limit
            )
            print_logs(data)

        elif args.command == 'errors':
            data = monitor.query_errors(minutes=args.minutes, limit=args.limit)
            print_errors(data)

        elif args.command == 'trace':
            data = monitor.trace_request(args.correlation_id)
            print_trace(data)

        elif args.command == 'health':
            data = monitor.get_health(detailed=not args.simple)
            print_health(data)

        elif args.command == 'metrics':
            data = monitor.get_metrics(path=args.path, minutes=args.minutes)
            print_metrics(data)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()
