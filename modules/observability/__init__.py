"""
Observability Module

Centralized logging, tracing, and monitoring system for the application.
Provides structured logging, request correlation, performance metrics, debugging tools,
PII scrubbing, rate limiting, and configuration validation.
"""

from .logging_config import configure_logging, get_logger, shutdown_logging
from .context import RequestContext, get_request_context, set_request_context
from .metrics import MetricsCollector, track_performance
from .middleware import ObservabilityMiddleware
from .monitoring_api import monitoring_api
from .pii_scrubber import PIIScrubber, PIIScrubbingFilter, scrub_pii
from .rate_limiter import RateLimiter, rate_limit, init_rate_limiter
from .config_validator import ConfigValidator, validate_configuration, ConfigurationError

__all__ = [
    # Logging
    'configure_logging',
    'get_logger',
    'shutdown_logging',

    # Context
    'RequestContext',
    'get_request_context',
    'set_request_context',

    # Metrics
    'MetricsCollector',
    'track_performance',

    # Middleware & API
    'ObservabilityMiddleware',
    'monitoring_api',

    # PII Scrubbing
    'PIIScrubber',
    'PIIScrubbingFilter',
    'scrub_pii',

    # Rate Limiting
    'RateLimiter',
    'rate_limit',
    'init_rate_limiter',

    # Configuration
    'ConfigValidator',
    'validate_configuration',
    'ConfigurationError'
]
