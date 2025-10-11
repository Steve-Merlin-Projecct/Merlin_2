"""
Observability Middleware

Flask middleware for automatic request tracing, logging, and metrics collection.
Integrates with the centralized logging and context system.
"""

import time
from typing import Callable
from flask import Flask, request, g
from werkzeug.wrappers import Response

from .context import RequestContext, set_request_context, clear_request_context
from .logging_config import get_logger
from .metrics import MetricsCollector

logger = get_logger(__name__)


class ObservabilityMiddleware:
    """
    WSGI middleware that adds observability features to Flask applications.

    Features:
    - Automatic request context creation with correlation IDs
    - Request/response logging
    - Performance metrics collection
    - Error tracking

    Usage:
        >>> app = Flask(__name__)
        >>> ObservabilityMiddleware(app)
    """

    def __init__(
        self,
        app: Flask,
        metrics_collector: MetricsCollector = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: list = None
    ):
        """
        Initialize observability middleware.

        Args:
            app: Flask application instance
            metrics_collector: Optional metrics collector instance
            log_request_body: Whether to log request body (WARNING: may log sensitive data)
            log_response_body: Whether to log response body
            exclude_paths: List of paths to exclude from logging (e.g., ['/health', '/metrics'])
        """
        self.app = app
        self.metrics = metrics_collector or MetricsCollector()
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ['/health', '/metrics', '/favicon.ico']

        # Register request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_request(self._teardown_request)

    def _should_log(self, path: str) -> bool:
        """
        Determine if a request should be logged.

        Args:
            path: Request path

        Returns:
            True if request should be logged
        """
        return path not in self.exclude_paths

    def _before_request(self):
        """
        Before request handler - creates context and logs request.
        """
        # Get correlation ID from header or generate new one
        correlation_id = request.headers.get('X-Correlation-ID')

        # Extract user ID from session or auth header
        user_id = None
        if hasattr(g, 'user_id'):
            user_id = g.user_id
        elif 'user_id' in request.headers:
            user_id = request.headers.get('user_id')

        # Create request context
        context = RequestContext(
            correlation_id=correlation_id,
            method=request.method,
            path=request.path,
            user_id=user_id,
            ip_address=request.remote_addr,
            metadata={
                'user_agent': request.headers.get('User-Agent'),
                'content_type': request.headers.get('Content-Type'),
                'content_length': request.headers.get('Content-Length')
            }
        )
        set_request_context(context)

        # Store start time for performance tracking
        g.request_start_time = time.time()

        # Log incoming request
        if self._should_log(request.path):
            log_data = {
                'correlation_id': context.correlation_id,
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.args),
                'user_id': user_id,
                'ip_address': request.remote_addr
            }

            if self.log_request_body and request.is_json:
                log_data['body'] = request.get_json(silent=True)

            logger.info(f"Incoming request: {request.method} {request.path}", extra=log_data)

    def _after_request(self, response: Response) -> Response:
        """
        After request handler - logs response and collects metrics.

        Args:
            response: Flask response object

        Returns:
            Modified response with correlation ID header
        """
        context = get_request_context()
        if not context:
            return response

        # Calculate request duration
        duration_ms = (time.time() - g.get('request_start_time', time.time())) * 1000

        # Add correlation ID to response headers
        response.headers['X-Correlation-ID'] = context.correlation_id

        # Log response
        if self._should_log(request.path):
            log_data = {
                'correlation_id': context.correlation_id,
                'status_code': response.status_code,
                'duration_ms': round(duration_ms, 2),
                'content_type': response.headers.get('Content-Type'),
                'content_length': response.headers.get('Content-Length')
            }

            if self.log_response_body and response.is_json:
                log_data['body'] = response.get_json(silent=True)

            log_level = 'error' if response.status_code >= 500 else 'warning' if response.status_code >= 400 else 'info'
            log_msg = f"Request completed: {request.method} {request.path} - {response.status_code}"

            getattr(logger, log_level)(log_msg, extra=log_data)

        # Record metrics
        self.metrics.record_request(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )

        return response

    def _teardown_request(self, exception=None):
        """
        Teardown request handler - logs errors and clears context.

        Args:
            exception: Exception that occurred during request processing
        """
        context = get_request_context()

        if exception:
            duration_ms = (time.time() - g.get('request_start_time', time.time())) * 1000

            logger.error(
                f"Request failed: {request.method} {request.path}",
                exc_info=exception,
                extra={
                    'correlation_id': context.correlation_id if context else None,
                    'duration_ms': round(duration_ms, 2),
                    'error_type': type(exception).__name__,
                    'error_message': str(exception)
                }
            )

            # Record error metric
            if context:
                self.metrics.record_error(
                    method=request.method,
                    path=request.path,
                    error_type=type(exception).__name__
                )

        # Clear request context
        clear_request_context()


def add_correlation_id_to_logs(app: Flask):
    """
    Decorator to add correlation ID to all logs in a request context.

    This is a simpler alternative to the full middleware when you only need
    correlation IDs without metrics.

    Args:
        app: Flask application instance

    Example:
        >>> app = Flask(__name__)
        >>> add_correlation_id_to_logs(app)
    """
    @app.before_request
    def before_request():
        correlation_id = request.headers.get('X-Correlation-ID')
        context = RequestContext(
            correlation_id=correlation_id,
            method=request.method,
            path=request.path,
            ip_address=request.remote_addr
        )
        set_request_context(context)

    @app.after_request
    def after_request(response):
        context = get_request_context()
        if context:
            response.headers['X-Correlation-ID'] = context.correlation_id
        clear_request_context()
        return response
