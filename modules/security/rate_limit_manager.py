"""
Rate Limit Manager for Job Application System

Centralized rate limiting using Flask-Limiter with in-memory storage.
Provides decorators, key functions, error handlers, and monitoring integration.

Version: 1.0.0
Created: 2025-10-11
"""

import logging
import time
from typing import Optional, Callable
from functools import wraps
from flask import Flask, request, jsonify, session, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from modules.security import rate_limit_config as config
from modules.security import rate_limit_monitor as monitor

logger = logging.getLogger(__name__)

# Global limiter instance (initialized by init_rate_limiter)
limiter: Optional[Limiter] = None


# ============================================================================
# KEY FUNCTIONS
# ============================================================================


def get_rate_limit_key() -> str:
    """
    Generate rate limit key for current request.

    Uses hybrid approach:
    - Authenticated users: keyed by user_id
    - Unauthenticated: keyed by IP address

    Handles proxy headers (X-Forwarded-For, CF-Connecting-IP) correctly.

    Returns:
        Rate limit key string
    """
    # Priority 1: Authenticated user
    if session.get("authenticated") and session.get("user_id"):
        user_id = session["user_id"]
        return f"user:{user_id}"

    # Priority 2: IP address (with proxy header support)
    client_ip = get_client_ip()
    return f"ip:{client_ip}"


def get_client_ip() -> str:
    """
    Get client IP address, respecting proxy headers.

    Checks headers in order:
    1. CF-Connecting-IP (Cloudflare)
    2. X-Forwarded-For (standard proxy header)
    3. X-Real-IP (nginx)
    4. request.remote_addr (direct connection)

    Returns:
        Client IP address as string
    """
    # Cloudflare header (if configured)
    if config.TRUST_CLOUDFLARE_HEADERS:
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip:
            return cf_ip

    # Standard proxy headers (if configured)
    if config.USE_X_FORWARDED_FOR:
        x_forwarded = request.headers.get("X-Forwarded-For")
        if x_forwarded:
            # X-Forwarded-For can be comma-separated list, take first (original client)
            return x_forwarded.split(",")[0].strip()

        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip

    # Fallback to direct connection
    return request.remote_addr or "unknown"


def is_exempt_endpoint() -> bool:
    """
    Check if current endpoint is exempt from rate limiting.

    Returns:
        True if endpoint should skip rate limiting
    """
    endpoint = request.endpoint
    path = request.path

    # Check against exempt list
    for exempt_path in config.EXEMPT_ENDPOINTS:
        if path.startswith(exempt_path):
            return True

    return False


# ============================================================================
# ERROR HANDLERS
# ============================================================================


def rate_limit_error_handler(error):
    """
    Custom error handler for rate limit violations.

    Logs violation, returns 429 response with retry-after header,
    and triggers analytics logging.

    Args:
        error: RateLimitExceeded exception from Flask-Limiter

    Returns:
        Flask JSON response with 429 status
    """
    # Extract rate limit details
    endpoint = request.endpoint or request.path
    client_ip = get_client_ip()
    user_id = session.get("user_id", "anonymous")
    limit_str = str(error.description) if hasattr(error, "description") else "unknown"

    # Log violation
    logger.warning(
        f"Rate limit exceeded - Endpoint: {endpoint}, IP: {client_ip}, " f"User: {user_id}, Limit: {limit_str}"
    )

    # Store violation for analytics (async to avoid blocking request)
    if config.ENABLE_VIOLATION_LOGGING:
        try:
            log_rate_limit_violation(endpoint, client_ip, user_id, limit_str)
        except Exception as e:
            logger.error(f"Failed to log rate limit violation: {e}")

    # Build error response
    response = jsonify(
        {
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "status": 429,
            "endpoint": endpoint,
            "limit": limit_str,
            "retry_after_seconds": getattr(error, "retry_after", 60),
        }
    )

    # Add retry-after header
    response.status_code = 429
    if hasattr(error, "retry_after"):
        response.headers["Retry-After"] = str(error.retry_after)

    return response


def log_rate_limit_violation(endpoint: str, client_ip: str, user_id: str, limit_str: str):
    """
    Log rate limit violation to database for analytics.

    Uses batch writing for performance (configured via VIOLATION_BATCH_SIZE).

    Args:
        endpoint: Endpoint that was rate limited
        client_ip: Client IP address
        user_id: User ID (or 'anonymous')
        limit_str: Rate limit string that was exceeded
    """
    # Store in request context for batch processing
    if not hasattr(g, "rate_limit_violations"):
        g.rate_limit_violations = []

    violation = {
        "timestamp": time.time(),
        "endpoint": endpoint,
        "client_ip": client_ip,
        "user_id": user_id,
        "limit_exceeded": limit_str,
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "request_method": request.method,
    }

    g.rate_limit_violations.append(violation)

    # Flush to database if batch size reached
    if len(g.rate_limit_violations) >= config.VIOLATION_BATCH_SIZE:
        flush_violation_batch()


def flush_violation_batch():
    """
    Flush accumulated rate limit violations to database.

    Called automatically when batch size reached or at request teardown.
    """
    if not hasattr(g, "rate_limit_violations") or not g.rate_limit_violations:
        return

    try:
        from modules.database.database_manager import DatabaseManager

        db = DatabaseManager()

        # Batch insert violations
        for violation in g.rate_limit_violations:
            db.execute_query(
                """
                INSERT INTO rate_limit_analytics
                (timestamp, endpoint, client_ip, user_id, limit_exceeded, user_agent, request_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    violation["timestamp"],
                    violation["endpoint"],
                    violation["client_ip"],
                    violation["user_id"],
                    violation["limit_exceeded"],
                    violation["user_agent"],
                    violation["request_method"],
                ),
            )

        logger.info(f"Flushed {len(g.rate_limit_violations)} rate limit violations to database")
        g.rate_limit_violations = []

    except Exception as e:
        logger.error(f"Failed to flush rate limit violations: {e}")


# ============================================================================
# INITIALIZATION
# ============================================================================


def init_rate_limiter(app: Flask) -> Limiter:
    """
    Initialize Flask-Limiter with application.

    Configures:
    - In-memory storage (or Redis if configured)
    - Custom key function (per-user + per-IP)
    - Error handlers
    - Default rate limits
    - Request hooks for analytics

    Args:
        app: Flask application instance

    Returns:
        Configured Limiter instance
    """
    global limiter

    logger.info("Initializing rate limiter...")

    # Create limiter instance
    limiter = Limiter(
        key_func=get_rate_limit_key,
        app=app,
        storage_uri=config.STORAGE_URI,
        storage_options=config.STORAGE_OPTIONS.get("memory", {}),
        default_limits=[config.RATE_LIMIT_TIERS["default"]],
        strategy="fixed-window",  # Simpler than sliding window
        headers_enabled=config.ADD_HEADERS,
        swallow_errors=not config.FAIL_CLOSED_ON_ERROR,  # Fail closed = don't swallow errors
    )

    # Register custom error handler
    app.register_error_handler(429, rate_limit_error_handler)

    # Register teardown handler for batch violation flushing
    @app.teardown_appcontext
    def teardown_rate_limiting(exception=None):
        """Flush any pending rate limit violations on request completion."""
        try:
            flush_violation_batch()
        except Exception as e:
            logger.error(f"Error in rate limiting teardown: {e}")

    # Log configuration
    logger.info(f"Rate limiter initialized with storage: {config.STORAGE_URI}")
    logger.info(f"Default rate limit: {config.RATE_LIMIT_TIERS['default']}")
    logger.info(f"Max memory: {config.MAX_MEMORY_MB}MB")
    logger.info(f"Fail closed: {config.FAIL_CLOSED_ON_ERROR}")

    # Log cost protection estimate
    max_cost = config.calculate_max_daily_cost()
    logger.info(f"Maximum daily cost with all limits hit: ${max_cost:.2f}")

    # Start background cleanup/monitoring thread
    try:
        monitor.start_cleanup_thread(limiter.storage, limiter)
        logger.info("Memory monitoring and cleanup thread started")
    except Exception as e:
        logger.error(f"Failed to start monitoring thread: {e}")

    return limiter


# ============================================================================
# DECORATOR FUNCTIONS
# ============================================================================


def rate_limit_expensive(f: Callable) -> Callable:
    """
    Decorator for expensive operations (AI, scraping).

    Applies strictest rate limits to protect costs.

    Example:
        @app.route('/api/ai/analyze')
        @rate_limit_expensive
        def analyze_jobs():
            ...
    """
    limit = config.RATE_LIMIT_TIERS["expensive"]["ai_analysis"]
    return limiter.limit(limit)(f)


def rate_limit_moderate(f: Callable) -> Callable:
    """
    Decorator for moderate cost operations (document generation, email).

    Example:
        @app.route('/api/email/send')
        @rate_limit_moderate
        def send_email():
            ...
    """
    limit = config.RATE_LIMIT_TIERS["moderate"]["document_generation"]
    return limiter.limit(limit)(f)


def rate_limit_cheap(f: Callable) -> Callable:
    """
    Decorator for cheap operations (database reads, dashboard).

    Example:
        @app.route('/api/db/jobs')
        @rate_limit_cheap
        def get_jobs():
            ...
    """
    limit = config.RATE_LIMIT_TIERS["cheap"]["db_read"]
    return limiter.limit(limit)(f)


def rate_limit_custom(limit_string: str) -> Callable:
    """
    Decorator factory for custom rate limits.

    Args:
        limit_string: Rate limit string (e.g., '5/minute;20/hour')

    Example:
        @app.route('/api/special')
        @rate_limit_custom('15/minute;100/hour')
        def special_endpoint():
            ...
    """

    def decorator(f: Callable) -> Callable:
        return limiter.limit(limit_string)(f)

    return decorator


# ============================================================================
# MONITORING INTEGRATION
# ============================================================================


def track_request_overhead():
    """
    Track rate limiting overhead for performance monitoring.

    Measures time spent in rate limit checks and logs if exceeds threshold.
    """
    if not config.TRACK_PERFORMANCE_OVERHEAD:
        return

    start_time = getattr(g, "rate_limit_start_time", None)
    if start_time:
        overhead_ms = (time.time() - start_time) * 1000

        if overhead_ms > config.MAX_OVERHEAD_MS:
            logger.warning(f"Rate limit check overhead exceeded threshold: {overhead_ms:.2f}ms > {config.MAX_OVERHEAD_MS}ms")


def before_request_handler():
    """Hook to track rate limiting performance."""
    if config.TRACK_PERFORMANCE_OVERHEAD:
        g.rate_limit_start_time = time.time()


def after_request_handler(response):
    """Hook to track rate limiting performance and add custom headers."""
    track_request_overhead()
    return response


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def get_rate_limit_status() -> dict:
    """
    Get current rate limit status for authenticated user or IP.

    Returns:
        Dictionary with rate limit information
    """
    key = get_rate_limit_key()
    client_ip = get_client_ip()

    return {
        "key": key,
        "client_ip": client_ip,
        "authenticated": session.get("authenticated", False),
        "user_id": session.get("user_id", "anonymous"),
        "endpoint": request.endpoint or request.path,
    }


def reset_rate_limit(key: str) -> bool:
    """
    Reset rate limit for specific key (admin function).

    Args:
        key: Rate limit key to reset

    Returns:
        True if successfully reset
    """
    try:
        if limiter and limiter.storage:
            limiter.storage.reset()
            logger.info(f"Reset rate limit for key: {key}")
            return True
    except Exception as e:
        logger.error(f"Failed to reset rate limit: {e}")
        return False

    return False
