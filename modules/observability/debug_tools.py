"""
Debugging and Diagnostic Tools

Provides utilities for debugging, log analysis, and troubleshooting in production
and development environments.
"""

import re
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class LogEntry:
    """
    Parsed log entry.

    Attributes:
        timestamp: Log timestamp
        level: Log level
        logger_name: Logger name
        message: Log message
        correlation_id: Request correlation ID
        metadata: Additional metadata
    """
    timestamp: datetime
    level: str
    logger_name: str
    message: str
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = None


class LogAnalyzer:
    """
    Analyze logs for patterns, errors, and performance issues.

    Provides tools for parsing, filtering, and analyzing log files.
    """

    def __init__(self):
        """Initialize log analyzer."""
        self.entries: List[LogEntry] = []

    def parse_json_log(self, log_file: str) -> List[LogEntry]:
        """
        Parse JSON-formatted log file.

        Args:
            log_file: Path to log file

        Returns:
            List of parsed log entries
        """
        entries = []

        try:
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        entry = LogEntry(
                            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
                            level=data.get('level', 'INFO'),
                            logger_name=data.get('logger', 'unknown'),
                            message=data.get('message', ''),
                            correlation_id=data.get('request', {}).get('correlation_id'),
                            metadata=data
                        )
                        entries.append(entry)
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Failed to parse log line: {e}")

        except FileNotFoundError:
            logger.error(f"Log file not found: {log_file}")

        self.entries = entries
        return entries

    def filter_by_level(self, level: str) -> List[LogEntry]:
        """
        Filter log entries by level.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Filtered log entries
        """
        return [e for e in self.entries if e.level == level.upper()]

    def filter_by_correlation_id(self, correlation_id: str) -> List[LogEntry]:
        """
        Filter log entries by correlation ID.

        Useful for tracing a specific request through the system.

        Args:
            correlation_id: Request correlation ID

        Returns:
            Filtered log entries
        """
        return [e for e in self.entries if e.correlation_id == correlation_id]

    def filter_by_time_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[LogEntry]:
        """
        Filter log entries by time range.

        Args:
            start: Start timestamp
            end: End timestamp

        Returns:
            Filtered log entries
        """
        return [e for e in self.entries if start <= e.timestamp <= end]

    def search_message(self, pattern: str, regex: bool = False) -> List[LogEntry]:
        """
        Search log messages.

        Args:
            pattern: Search pattern
            regex: Whether pattern is a regex (default: simple substring search)

        Returns:
            Matching log entries
        """
        if regex:
            compiled = re.compile(pattern, re.IGNORECASE)
            return [e for e in self.entries if compiled.search(e.message)]
        else:
            return [e for e in self.entries if pattern.lower() in e.message.lower()]

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of errors from logs.

        Returns:
            Error summary with counts and examples
        """
        errors = self.filter_by_level('ERROR')
        error_types = defaultdict(list)

        for error in errors:
            # Extract error type from metadata
            error_type = error.metadata.get('exception', {}).get('type', 'Unknown')
            error_types[error_type].append(error)

        return {
            'total_errors': len(errors),
            'by_type': {
                error_type: {
                    'count': len(entries),
                    'example': entries[0].message if entries else None
                }
                for error_type, entries in error_types.items()
            }
        }

    def get_performance_issues(self, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
        """
        Find slow requests/operations.

        Args:
            threshold_ms: Duration threshold in milliseconds

        Returns:
            List of slow operations
        """
        slow_ops = []

        for entry in self.entries:
            if entry.metadata and 'duration_ms' in entry.metadata:
                duration = entry.metadata['duration_ms']
                if duration > threshold_ms:
                    slow_ops.append({
                        'timestamp': entry.timestamp,
                        'operation': entry.message,
                        'duration_ms': duration,
                        'correlation_id': entry.correlation_id
                    })

        return sorted(slow_ops, key=lambda x: x['duration_ms'], reverse=True)

    def trace_request(self, correlation_id: str) -> Dict[str, Any]:
        """
        Trace a complete request flow through the system.

        Args:
            correlation_id: Request correlation ID

        Returns:
            Request trace with timeline and events
        """
        entries = self.filter_by_correlation_id(correlation_id)

        if not entries:
            return {'error': f'No logs found for correlation_id: {correlation_id}'}

        entries.sort(key=lambda e: e.timestamp)

        timeline = []
        for i, entry in enumerate(entries):
            event = {
                'sequence': i,
                'timestamp': entry.timestamp.isoformat(),
                'level': entry.level,
                'logger': entry.logger_name,
                'message': entry.message
            }

            if i > 0:
                delta = (entry.timestamp - entries[i-1].timestamp).total_seconds() * 1000
                event['elapsed_ms'] = round(delta, 2)

            timeline.append(event)

        return {
            'correlation_id': correlation_id,
            'start_time': entries[0].timestamp.isoformat(),
            'end_time': entries[-1].timestamp.isoformat(),
            'total_duration_ms': (entries[-1].timestamp - entries[0].timestamp).total_seconds() * 1000,
            'total_events': len(entries),
            'timeline': timeline
        }


class HealthChecker:
    """
    System health check utilities.

    Provides health status checks for various system components.
    """

    def __init__(self):
        """Initialize health checker."""
        self.checks: Dict[str, Callable] = {}

    def register_check(self, name: str, check_func: Callable) -> None:
        """
        Register a health check function.

        Args:
            name: Check name
            check_func: Function that returns (status: bool, message: str)

        Example:
            >>> def check_database():
            ...     try:
            ...         db.session.execute('SELECT 1')
            ...         return True, "Database is healthy"
            ...     except Exception as e:
            ...         return False, f"Database error: {str(e)}"
            >>> health = HealthChecker()
            >>> health.register_check('database', check_database)
        """
        self.checks[name] = check_func

    def run_checks(self) -> Dict[str, Any]:
        """
        Run all registered health checks.

        Returns:
            Health check results
        """
        results = {}
        all_healthy = True

        for name, check_func in self.checks.items():
            try:
                status, message = check_func()
                results[name] = {
                    'status': 'healthy' if status else 'unhealthy',
                    'message': message
                }
                if not status:
                    all_healthy = False
            except Exception as e:
                results[name] = {
                    'status': 'unhealthy',
                    'message': f'Check failed: {str(e)}'
                }
                all_healthy = False

        return {
            'overall_status': 'healthy' if all_healthy else 'unhealthy',
            'checks': results,
            'timestamp': datetime.utcnow().isoformat()
        }


class DebugContext:
    """
    Context manager for detailed debug logging.

    Temporarily enables debug logging for a code block.

    Example:
        >>> with DebugContext('scraping_module'):
        ...     # This code will have debug logging enabled
        ...     scrape_jobs()
    """

    def __init__(self, logger_name: str):
        """
        Initialize debug context.

        Args:
            logger_name: Name of logger to enable debug for
        """
        self.logger_name = logger_name
        self.original_level = None

    def __enter__(self):
        """Enable debug logging."""
        import logging
        target_logger = logging.getLogger(self.logger_name)
        self.original_level = target_logger.level
        target_logger.setLevel(logging.DEBUG)
        logger.info(f"Debug logging enabled for: {self.logger_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original logging level."""
        import logging
        target_logger = logging.getLogger(self.logger_name)
        target_logger.setLevel(self.original_level)
        logger.info(f"Debug logging disabled for: {self.logger_name}")


def dump_context() -> Dict[str, Any]:
    """
    Dump current request context for debugging.

    Returns:
        Current context information
    """
    from .context import get_request_context

    context = get_request_context()

    if not context:
        return {'message': 'No active request context'}

    return {
        'context': context.to_dict(),
        'timestamp': datetime.utcnow().isoformat()
    }


def analyze_correlation_chain(
    log_file: str,
    correlation_id: str
) -> Dict[str, Any]:
    """
    Analyze complete correlation chain from logs.

    Args:
        log_file: Path to log file
        correlation_id: Correlation ID to trace

    Returns:
        Analysis of the correlation chain
    """
    analyzer = LogAnalyzer()
    analyzer.parse_json_log(log_file)

    trace = analyzer.trace_request(correlation_id)

    if 'error' in trace:
        return trace

    # Find errors in trace
    errors = [e for e in trace['timeline'] if e['level'] == 'ERROR']

    # Find slow operations
    slow_ops = [e for e in trace['timeline'] if e.get('elapsed_ms', 0) > 1000]

    return {
        **trace,
        'analysis': {
            'has_errors': len(errors) > 0,
            'error_count': len(errors),
            'errors': errors,
            'slow_operations': slow_ops,
            'performance_rating': 'good' if trace['total_duration_ms'] < 1000 else 'slow'
        }
    }
