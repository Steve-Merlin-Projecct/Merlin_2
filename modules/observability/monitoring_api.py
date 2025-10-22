"""
Monitoring and Observability API

Provides REST API endpoints for querying logs, metrics, and system health.
Designed for both development debugging and production monitoring.

Endpoints:
- GET /api/monitoring/logs - Query application logs with filters
- GET /api/monitoring/health - Comprehensive health check
- GET /api/monitoring/metrics - Retrieve performance metrics
- GET /api/monitoring/errors - Query error logs and summaries
- POST /api/monitoring/trace - Trace a specific request by correlation ID
"""

import os
import json
from typing import Optional
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from functools import wraps

from .logging_config import get_logger
from .debug_tools import LogAnalyzer, HealthChecker
from .metrics import MetricsCollector
from .rate_limiter import rate_limit

logger = get_logger(__name__)

# Create Blueprint
monitoring_api = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')


def require_monitoring_auth(f):
    """
    Authentication decorator for monitoring endpoints.

    Checks for API key in header or query parameter.
    In development mode, authentication can be bypassed with MONITORING_DEV_MODE=true.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if in development mode (bypass auth)
        dev_mode = os.environ.get('MONITORING_DEV_MODE', 'false').lower() == 'true'
        if dev_mode:
            return f(*args, **kwargs)

        # Check for API key
        api_key = request.headers.get('X-Monitoring-Key') or request.args.get('api_key')
        expected_key = os.environ.get('MONITORING_API_KEY') or os.environ.get('WEBHOOK_API_KEY')

        if not expected_key:
            logger.warning("MONITORING_API_KEY not set - allowing access in dev mode")
            return f(*args, **kwargs)

        if api_key != expected_key:
            logger.warning(
                f"Unauthorized monitoring access attempt from {request.remote_addr}",
                extra={'endpoint': request.path}
            )
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Valid API key required'
            }), 401

        return f(*args, **kwargs)

    return decorated_function


@monitoring_api.route('/logs', methods=['GET'])
@require_monitoring_auth
@rate_limit()
def query_logs():
    """
    Query application logs with filters.

    Query Parameters:
    - level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - correlation_id: Filter by correlation ID
    - start_time: Start timestamp (ISO format)
    - end_time: End timestamp (ISO format)
    - search: Search message text
    - limit: Maximum number of results (default: 100)
    - log_file: Path to log file (default: ./logs/app.log)

    Returns:
        JSON with log entries and metadata

    Example:
        GET /api/monitoring/logs?level=ERROR&limit=50
        GET /api/monitoring/logs?correlation_id=abc-123&search=database
    """
    try:
        # Get query parameters
        level = request.args.get('level')
        correlation_id = request.args.get('correlation_id')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        search = request.args.get('search')
        limit = int(request.args.get('limit', 100))
        log_file = request.args.get('log_file', './logs/app.log')

        # Initialize log analyzer
        analyzer = LogAnalyzer()

        # Check if log file exists
        if not os.path.exists(log_file):
            return jsonify({
                'error': 'Log file not found',
                'message': f'Log file does not exist: {log_file}',
                'available_logs': _get_available_logs()
            }), 404

        # Parse log file
        entries = analyzer.parse_json_log(log_file)

        # Apply filters
        if level:
            entries = analyzer.filter_by_level(level)

        if correlation_id:
            entries = analyzer.filter_by_correlation_id(correlation_id)

        if start_time_str and end_time_str:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            entries = analyzer.filter_by_time_range(start_time, end_time)

        if search:
            entries = analyzer.search_message(search)

        # Apply limit
        entries = entries[:limit]

        # Convert to JSON-serializable format
        results = [
            {
                'timestamp': entry.timestamp.isoformat(),
                'level': entry.level,
                'logger': entry.logger_name,
                'message': entry.message,
                'correlation_id': entry.correlation_id,
                'metadata': entry.metadata
            }
            for entry in entries
        ]

        return jsonify({
            'success': True,
            'count': len(results),
            'logs': results,
            'filters': {
                'level': level,
                'correlation_id': correlation_id,
                'search': search,
                'limit': limit
            }
        })

    except Exception as e:
        logger.error(f"Error querying logs: {e}", exc_info=e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@monitoring_api.route('/health', methods=['GET'])
@rate_limit(skip_auth_check=True, get_key_func=lambda: request.remote_addr)
def health_check():
    """
    Comprehensive system health check.

    Query Parameters:
    - detailed: Include detailed component checks (default: true)

    Returns:
        JSON with health status and component details

    Example:
        GET /api/monitoring/health
        GET /api/monitoring/health?detailed=false
    """
    try:
        detailed = request.args.get('detailed', 'true').lower() == 'true'

        health_checker = HealthChecker()

        # Register basic checks
        def check_app():
            return True, "Application is running"

        def check_logs():
            """Check if log directory is writable"""
            log_dir = './logs'
            try:
                if os.path.exists(log_dir) and os.access(log_dir, os.W_OK):
                    return True, f"Log directory writable: {log_dir}"
                else:
                    return False, f"Log directory not writable: {log_dir}"
            except Exception as e:
                return False, f"Log directory check failed: {str(e)}"

        def check_disk_space():
            """Check available disk space in log directory"""
            log_dir = './logs'
            try:
                import shutil
                stat = shutil.disk_usage(log_dir)
                free_mb = stat.free / (1024 * 1024)
                total_mb = stat.total / (1024 * 1024)
                free_percent = (stat.free / stat.total * 100) if stat.total > 0 else 0

                # Critical: < 50MB, Warning: < 100MB
                if free_mb < 50:
                    return False, f"CRITICAL: Only {free_mb:.1f}MB free in {log_dir} ({free_percent:.1f}%)"
                elif free_mb < 100:
                    return True, f"WARNING: Only {free_mb:.1f}MB free in {log_dir} ({free_percent:.1f}%)"
                else:
                    return True, f"Disk space OK: {free_mb:.1f}MB free of {total_mb:.1f}MB ({free_percent:.1f}%)"
            except Exception as e:
                return False, f"Disk space check failed: {str(e)}"

        def check_database():
            """Check database connectivity"""
            try:
                from modules.database.database_config import DatabaseConfig
                db_config = DatabaseConfig()
                return True, f"Database configured: {db_config.is_docker and 'Docker' or 'Local'}"
            except Exception as e:
                return False, f"Database configuration error: {str(e)}"

        health_checker.register_check('application', check_app)
        health_checker.register_check('logging', check_logs)
        health_checker.register_check('disk_space', check_disk_space)
        health_checker.register_check('database', check_database)

        results = health_checker.run_checks()

        # Add version and uptime info
        results['service'] = 'Merlin Job Application System'
        results['version'] = getattr(current_app, 'config', {}).get('VERSION', 'unknown')

        # Add resource info if detailed
        if detailed:
            results['resources'] = _get_resource_info()
            results['disk_usage'] = _get_disk_usage_details()

        # Add rate limit status
        try:
            from .rate_limiter import get_default_rate_limiter
            limiter = getattr(current_app, 'rate_limiter', None) or get_default_rate_limiter()
            key = request.headers.get('X-Monitoring-Key') or request.args.get('api_key') or request.remote_addr or 'anonymous'
            rate_stats = limiter.get_stats(key)
            if rate_stats:
                results['rate_limit'] = rate_stats
        except Exception as e:
            logger.debug(f"Could not get rate limit stats: {e}")

        status_code = 200 if results['overall_status'] == 'healthy' else 503
        return jsonify(results), status_code

    except Exception as e:
        logger.error(f"Error in health check: {e}", exc_info=e)
        return jsonify({
            'overall_status': 'unhealthy',
            'error': str(e)
        }), 500


@monitoring_api.route('/metrics', methods=['GET'])
@require_monitoring_auth
@rate_limit()
def get_metrics():
    """
    Retrieve performance metrics.

    Query Parameters:
    - path: Filter metrics for specific path
    - minutes: Time window in minutes (default: 60)

    Returns:
        JSON with performance metrics

    Example:
        GET /api/monitoring/metrics
        GET /api/monitoring/metrics?path=/api/db/jobs&minutes=30
    """
    try:
        path = request.args.get('path')
        minutes = int(request.args.get('minutes', 60))

        # Get metrics collector from app context
        metrics_collector = getattr(current_app, 'metrics_collector', None)

        if not metrics_collector:
            return jsonify({
                'error': 'Metrics collector not initialized',
                'message': 'Application was not configured with metrics collection'
            }), 503

        # Get request metrics
        if path:
            request_metrics = metrics_collector.get_request_metrics(path)
        else:
            request_metrics = metrics_collector.get_request_metrics()

        # Get custom metrics summary
        custom_metrics = {}
        for metric_name in ['request_duration_ms', 'jobs_scraped', 'ai_tokens_used']:
            summary = metrics_collector.get_metric_summary(metric_name, minutes)
            if summary['count'] > 0:
                custom_metrics[metric_name] = summary

        # Get error summary
        error_summary = metrics_collector.get_error_summary(minutes)

        return jsonify({
            'success': True,
            'time_window_minutes': minutes,
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
                for path, m in request_metrics.items()
            },
            'custom_metrics': custom_metrics,
            'errors': error_summary
        })

    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}", exc_info=e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@monitoring_api.route('/errors', methods=['GET'])
@require_monitoring_auth
@rate_limit()
def query_errors():
    """
    Query error logs and summaries.

    Query Parameters:
    - minutes: Time window in minutes (default: 60)
    - limit: Maximum number of error entries (default: 50)
    - log_file: Path to error log file (default: ./logs/error.log)

    Returns:
        JSON with error summary and recent errors

    Example:
        GET /api/monitoring/errors
        GET /api/monitoring/errors?minutes=30&limit=100
    """
    try:
        minutes = int(request.args.get('minutes', 60))
        limit = int(request.args.get('limit', 50))
        log_file = request.args.get('log_file', './logs/error.log')

        # Initialize log analyzer
        analyzer = LogAnalyzer()

        # Check if error log exists
        if not os.path.exists(log_file):
            # Fall back to main log file
            log_file = './logs/app.log'
            if not os.path.exists(log_file):
                return jsonify({
                    'error': 'Log files not found',
                    'message': 'No error logs available',
                    'available_logs': _get_available_logs()
                }), 404

        # Parse log file
        analyzer.parse_json_log(log_file)

        # Get error summary
        error_summary = analyzer.get_error_summary()

        # Get recent errors
        errors = analyzer.filter_by_level('ERROR')

        # Apply time filter
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        errors = [e for e in errors if e.timestamp >= cutoff]

        # Apply limit
        errors = errors[:limit]

        # Convert to JSON format
        error_entries = [
            {
                'timestamp': e.timestamp.isoformat(),
                'logger': e.logger_name,
                'message': e.message,
                'correlation_id': e.correlation_id,
                'error_type': e.metadata.get('exception', {}).get('type') if e.metadata else None,
                'error_message': e.metadata.get('exception', {}).get('message') if e.metadata else None
            }
            for e in errors
        ]

        return jsonify({
            'success': True,
            'time_window_minutes': minutes,
            'total_errors': len(error_entries),
            'summary': error_summary,
            'recent_errors': error_entries
        })

    except Exception as e:
        logger.error(f"Error querying errors: {e}", exc_info=e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@monitoring_api.route('/trace', methods=['POST'])
@require_monitoring_auth
@rate_limit()
def trace_request():
    """
    Trace a specific request by correlation ID.

    Request Body:
    {
        "correlation_id": "abc-123-def",
        "log_file": "./logs/app.log"  # optional
    }

    Returns:
        JSON with complete request trace

    Example:
        POST /api/monitoring/trace
        {
            "correlation_id": "abc-123-def"
        }
    """
    try:
        data = request.get_json()

        if not data or 'correlation_id' not in data:
            return jsonify({
                'error': 'Missing correlation_id',
                'message': 'Request body must include correlation_id'
            }), 400

        correlation_id = data['correlation_id']
        log_file = data.get('log_file', './logs/app.log')

        # Check if log file exists
        if not os.path.exists(log_file):
            return jsonify({
                'error': 'Log file not found',
                'message': f'Log file does not exist: {log_file}',
                'available_logs': _get_available_logs()
            }), 404

        # Initialize log analyzer
        analyzer = LogAnalyzer()
        analyzer.parse_json_log(log_file)

        # Trace the request
        trace = analyzer.trace_request(correlation_id)

        if 'error' in trace:
            return jsonify({
                'success': False,
                'error': trace['error']
            }), 404

        return jsonify({
            'success': True,
            'trace': trace
        })

    except Exception as e:
        logger.error(f"Error tracing request: {e}", exc_info=e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Helper functions

def _get_available_logs():
    """
    Get list of available log files.

    Returns:
        List of log file paths
    """
    log_dir = './logs'
    if not os.path.exists(log_dir):
        return []

    return [
        os.path.join(log_dir, f)
        for f in os.listdir(log_dir)
        if f.endswith('.log')
    ]


def _get_resource_info():
    """
    Get system resource information.

    Returns:
        Dictionary with resource stats
    """
    import psutil

    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    except ImportError:
        return {
            'message': 'psutil not installed - resource monitoring unavailable'
        }
    except Exception as e:
        return {
            'error': f'Failed to get resource info: {str(e)}'
        }


def _get_disk_usage_details():
    """
    Get detailed disk usage information for log directory.

    Returns:
        Dictionary with disk usage stats
    """
    import shutil

    log_dir = './logs'
    try:
        stat = shutil.disk_usage(log_dir)
        free_mb = stat.free / (1024 * 1024)
        total_mb = stat.total / (1024 * 1024)
        used_mb = stat.used / (1024 * 1024)
        free_percent = (stat.free / stat.total * 100) if stat.total > 0 else 0
        used_percent = (stat.used / stat.total * 100) if stat.total > 0 else 0

        # Determine status
        if free_mb < 50:
            status = 'critical'
        elif free_mb < 100:
            status = 'warning'
        else:
            status = 'ok'

        return {
            'path': log_dir,
            'total_mb': round(total_mb, 2),
            'used_mb': round(used_mb, 2),
            'free_mb': round(free_mb, 2),
            'used_percent': round(used_percent, 2),
            'free_percent': round(free_percent, 2),
            'status': status
        }
    except Exception as e:
        return {
            'error': f'Failed to get disk usage: {str(e)}'
        }


@monitoring_api.route('/status', methods=['GET'])
def monitoring_status():
    """
    Get monitoring system status and configuration.

    Returns:
        JSON with monitoring configuration
    """
    return jsonify({
        'service': 'Monitoring API',
        'version': '1.0.0',
        'endpoints': {
            'logs': '/api/monitoring/logs - Query application logs',
            'health': '/api/monitoring/health - System health check',
            'metrics': '/api/monitoring/metrics - Performance metrics',
            'errors': '/api/monitoring/errors - Error logs and summaries',
            'trace': '/api/monitoring/trace - Trace request by correlation ID',
            'status': '/api/monitoring/status - This endpoint'
        },
        'authentication': {
            'dev_mode': os.environ.get('MONITORING_DEV_MODE', 'false') == 'true',
            'api_key_required': os.environ.get('MONITORING_API_KEY') is not None
        },
        'available_logs': _get_available_logs()
    })
