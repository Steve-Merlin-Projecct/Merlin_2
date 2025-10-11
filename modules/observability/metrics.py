"""
Metrics Collection and Performance Monitoring

Provides utilities for collecting application metrics, performance tracking,
and generating monitoring data for dashboards and alerting.
"""

import time
import functools
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from threading import Lock

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MetricPoint:
    """
    Individual metric data point.

    Attributes:
        timestamp: When the metric was recorded
        value: Metric value
        labels: Additional labels/tags for filtering
    """
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class RequestMetrics:
    """
    Aggregated request metrics.

    Attributes:
        total_requests: Total number of requests
        total_errors: Total number of errors
        total_duration_ms: Cumulative request duration
        avg_duration_ms: Average request duration
        min_duration_ms: Minimum request duration
        max_duration_ms: Maximum request duration
        status_codes: Count of each status code
        methods: Count of each HTTP method
    """
    total_requests: int = 0
    total_errors: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    status_codes: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    methods: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


class MetricsCollector:
    """
    Thread-safe metrics collection and aggregation.

    Collects request metrics, performance data, and custom application metrics.
    Provides aggregation and querying capabilities.
    """

    def __init__(self, retention_hours: int = 24):
        """
        Initialize metrics collector.

        Args:
            retention_hours: How long to retain metrics (default: 24 hours)
        """
        self.retention_hours = retention_hours
        self._lock = Lock()

        # Request metrics by path
        self._request_metrics: Dict[str, RequestMetrics] = defaultdict(RequestMetrics)

        # Time-series metrics
        self._metrics: Dict[str, List[MetricPoint]] = defaultdict(list)

        # Error tracking
        self._errors: List[Dict[str, Any]] = []

        logger.info(f"MetricsCollector initialized with {retention_hours}h retention")

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float
    ) -> None:
        """
        Record a request metric.

        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
        """
        with self._lock:
            metrics = self._request_metrics[path]

            metrics.total_requests += 1
            metrics.total_duration_ms += duration_ms
            metrics.avg_duration_ms = metrics.total_duration_ms / metrics.total_requests
            metrics.min_duration_ms = min(metrics.min_duration_ms, duration_ms)
            metrics.max_duration_ms = max(metrics.max_duration_ms, duration_ms)
            metrics.status_codes[status_code] += 1
            metrics.methods[method] += 1

            if status_code >= 400:
                metrics.total_errors += 1

            # Record time-series point
            self._metrics['request_duration_ms'].append(
                MetricPoint(
                    timestamp=datetime.utcnow(),
                    value=duration_ms,
                    labels={'method': method, 'path': path, 'status': str(status_code)}
                )
            )

    def record_error(
        self,
        method: str,
        path: str,
        error_type: str,
        error_message: str = None
    ) -> None:
        """
        Record an error metric.

        Args:
            method: HTTP method
            path: Request path
            error_type: Type of error
            error_message: Error message
        """
        with self._lock:
            self._errors.append({
                'timestamp': datetime.utcnow(),
                'method': method,
                'path': path,
                'error_type': error_type,
                'error_message': error_message
            })

    def record_custom_metric(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] = None
    ) -> None:
        """
        Record a custom application metric.

        Args:
            name: Metric name
            value: Metric value
            labels: Optional labels/tags

        Example:
            >>> metrics.record_custom_metric('jobs_scraped', 150, {'source': 'indeed'})
            >>> metrics.record_custom_metric('ai_tokens_used', 5000, {'model': 'gemini'})
        """
        with self._lock:
            self._metrics[name].append(
                MetricPoint(
                    timestamp=datetime.utcnow(),
                    value=value,
                    labels=labels or {}
                )
            )

    def get_request_metrics(self, path: Optional[str] = None) -> Dict[str, RequestMetrics]:
        """
        Get aggregated request metrics.

        Args:
            path: Optional path filter

        Returns:
            Dictionary of path to RequestMetrics
        """
        with self._lock:
            if path:
                return {path: self._request_metrics.get(path, RequestMetrics())}
            return dict(self._request_metrics)

    def get_metric_summary(self, name: str, minutes: int = 60) -> Dict[str, Any]:
        """
        Get summary statistics for a metric.

        Args:
            name: Metric name
            minutes: Time window in minutes

        Returns:
            Dictionary with summary statistics
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        with self._lock:
            points = [p for p in self._metrics.get(name, []) if p.timestamp >= cutoff]

            if not points:
                return {'count': 0, 'avg': 0, 'min': 0, 'max': 0, 'sum': 0}

            values = [p.value for p in points]
            return {
                'count': len(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'sum': sum(values),
                'latest': values[-1] if values else 0
            }

    def get_error_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """
        Get error summary for time window.

        Args:
            minutes: Time window in minutes

        Returns:
            Error summary statistics
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        with self._lock:
            recent_errors = [e for e in self._errors if e['timestamp'] >= cutoff]

            error_types = defaultdict(int)
            error_paths = defaultdict(int)

            for error in recent_errors:
                error_types[error['error_type']] += 1
                error_paths[error['path']] += 1

            return {
                'total_errors': len(recent_errors),
                'by_type': dict(error_types),
                'by_path': dict(error_paths),
                'recent_errors': recent_errors[-10:]  # Last 10 errors
            }

    def cleanup_old_metrics(self) -> None:
        """
        Remove metrics older than retention period.
        """
        cutoff = datetime.utcnow() - timedelta(hours=self.retention_hours)

        with self._lock:
            # Clean time-series metrics
            for name in self._metrics:
                self._metrics[name] = [p for p in self._metrics[name] if p.timestamp >= cutoff]

            # Clean errors
            self._errors = [e for e in self._errors if e['timestamp'] >= cutoff]

            logger.debug(f"Cleaned metrics older than {cutoff.isoformat()}")

    def export_metrics(self) -> Dict[str, Any]:
        """
        Export all metrics in a structured format.

        Returns:
            Dictionary containing all metrics
        """
        with self._lock:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'request_metrics': {
                    path: {
                        'total_requests': m.total_requests,
                        'total_errors': m.total_errors,
                        'avg_duration_ms': round(m.avg_duration_ms, 2),
                        'min_duration_ms': round(m.min_duration_ms, 2) if m.min_duration_ms != float('inf') else 0,
                        'max_duration_ms': round(m.max_duration_ms, 2),
                        'status_codes': dict(m.status_codes),
                        'methods': dict(m.methods)
                    }
                    for path, m in self._request_metrics.items()
                },
                'custom_metrics': {
                    name: self.get_metric_summary(name)
                    for name in self._metrics.keys()
                },
                'errors': self.get_error_summary()
            }


def track_performance(metric_name: str = None):
    """
    Decorator for tracking function performance.

    Args:
        metric_name: Custom metric name (defaults to function name)

    Example:
        >>> @track_performance('job_scraping')
        >>> def scrape_jobs():
        ...     # Function implementation
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            name = metric_name or func.__name__

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                logger.debug(
                    f"Performance: {name} completed in {duration_ms:.2f}ms",
                    extra={'function': name, 'duration_ms': duration_ms}
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Performance: {name} failed after {duration_ms:.2f}ms",
                    exc_info=e,
                    extra={'function': name, 'duration_ms': duration_ms}
                )
                raise

        return wrapper
    return decorator


class PerformanceTimer:
    """
    Context manager for timing code blocks.

    Example:
        >>> with PerformanceTimer('database_query') as timer:
        ...     # Database operations
        ...     pass
        >>> print(f"Query took {timer.duration_ms}ms")
    """

    def __init__(self, operation_name: str, logger_instance: Any = None):
        """
        Initialize performance timer.

        Args:
            operation_name: Name of the operation being timed
            logger_instance: Optional logger instance
        """
        self.operation_name = operation_name
        self.logger = logger_instance or logger
        self.start_time = None
        self.end_time = None
        self.duration_ms = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and log result."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

        if exc_type:
            self.logger.error(
                f"Performance: {self.operation_name} failed after {self.duration_ms:.2f}ms",
                exc_info=(exc_type, exc_val, exc_tb),
                extra={'operation': self.operation_name, 'duration_ms': self.duration_ms}
            )
        else:
            self.logger.debug(
                f"Performance: {self.operation_name} completed in {self.duration_ms:.2f}ms",
                extra={'operation': self.operation_name, 'duration_ms': self.duration_ms}
            )
