"""
Security Integration Module

Provides Flask application security integration for the link tracking system.
Includes security headers, HTTPS enforcement, and comprehensive security middleware.

Version: 2.16.5
Date: July 28, 2025
"""

from flask import Flask, request, g, make_response
from functools import wraps
import logging
import os

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """
    Comprehensive security middleware for Flask applications.

    Features:
    - HTTPS enforcement in production
    - Security headers for all responses
    - Request size limiting
    - Content type validation
    - Security event logging
    """

    def __init__(self, app: Flask = None):
        """Initialize security middleware."""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize security middleware with Flask app."""
        # Register before_request handlers
        app.before_request(self.enforce_https)
        app.before_request(self.validate_request)
        app.before_request(self.limit_request_size)

        # Register after_request handlers
        app.after_request(self.add_security_headers)
        app.after_request(self.log_request)

        logger.info("Security middleware initialized")

    def enforce_https(self):
        """
        Enforce HTTPS in production environments.

        Security Features:
        - Redirects HTTP to HTTPS in production
        - Checks X-Forwarded-Proto header for proxy environments
        - Logs insecure connection attempts
        """
        # Only enforce HTTPS in production
        if os.environ.get("FLASK_ENV") == "production":
            if not request.is_secure:
                # Check if we're behind a proxy that's handling HTTPS
                if request.headers.get("X-Forwarded-Proto", "http") != "https":
                    logger.warning(f"Insecure HTTP request blocked: {request.url}")
                    # Return 426 Upgrade Required
                    return "HTTPS required", 426

    def validate_request(self):
        """
        Validate incoming requests for security compliance.

        Security Features:
        - Content-Type validation for POST/PUT requests
        - User-Agent header validation
        - Suspicious pattern detection
        """
        # Validate Content-Type for data requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")

            # Allow JSON and form data
            allowed_types = ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"]

            if not any(allowed_type in content_type for allowed_type in allowed_types):
                logger.warning(f"Invalid Content-Type: {content_type}")
                return "Invalid Content-Type", 400

        # Basic User-Agent validation (detect obvious bots/scanners)
        user_agent = request.headers.get("User-Agent", "")
        suspicious_patterns = ["sqlmap", "nikto", "nmap", "masscan", "nessus", "openvas", "burp", "owasp", "w3af"]

        if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
            logger.warning(f"Suspicious User-Agent blocked: {user_agent}")
            return "Access denied", 403

    def limit_request_size(self):
        """
        Limit request size to prevent DoS attacks.

        Security Features:
        - 16MB limit for all requests
        - 1MB limit for JSON requests
        - Request size logging
        """
        content_length = request.headers.get("Content-Length", type=int)

        if content_length:
            # General limit: 16MB
            max_size = 16 * 1024 * 1024  # 16MB

            # Stricter limit for JSON: 1MB
            if "application/json" in request.headers.get("Content-Type", ""):
                max_size = 1 * 1024 * 1024  # 1MB

            if content_length > max_size:
                logger.warning(f"Request size too large: {content_length} bytes")
                return "Request too large", 413

    def add_security_headers(self, response):
        """
        Add comprehensive security headers to all responses.

        Security Headers:
        - Content Security Policy (CSP)
        - X-Frame-Options (clickjacking protection)
        - X-Content-Type-Options (MIME sniffing protection)
        - X-XSS-Protection (XSS protection)
        - Strict-Transport-Security (HTTPS enforcement)
        - Referrer-Policy (referrer information control)
        - Permissions-Policy (feature control)
        """
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp

        # Clickjacking protection
        response.headers["X-Frame-Options"] = "DENY"

        # MIME sniffing protection
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HTTPS enforcement (HSTS)
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (feature control)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), " "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )

        # Cross-origin policies
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

        # Cache control for sensitive responses
        if "api" in request.path:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        return response

    def log_request(self, response):
        """
        Log request details for security monitoring.

        Logs:
        - Request method, path, and status code
        - Client IP and User-Agent
        - Response time and size
        - Error responses for investigation
        """
        # Log all API requests and errors
        if "api" in request.path or response.status_code >= 400:
            client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            user_agent = request.headers.get("User-Agent", "Unknown")

            log_data = {
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "ip": client_ip,
                "user_agent": user_agent[:100],  # Truncate long user agents
                "content_length": response.headers.get("Content-Length", 0),
            }

            if response.status_code >= 400:
                logger.warning(f"HTTP {response.status_code}: {log_data}")
            else:
                logger.info(f"Request: {log_data}")

        return response


def setup_security_environment():
    """
    Set up security environment variables and configurations.

    Environment Variables:
    - LINK_TRACKING_API_KEY: API key for link tracking endpoints
    - FLASK_SECRET_KEY: Secret key for Flask sessions
    - SECURITY_LOG_LEVEL: Logging level for security events
    """
    # Generate API key if not set
    if not os.environ.get("LINK_TRACKING_API_KEY"):
        import secrets

        api_key = secrets.token_urlsafe(32)
        os.environ["LINK_TRACKING_API_KEY"] = api_key
        logger.warning("Generated temporary API key - set LINK_TRACKING_API_KEY in production")

    # Set security logging level
    security_log_level = os.environ.get("SECURITY_LOG_LEVEL", "INFO")
    logging.getLogger("modules.link_tracking.security_controls").setLevel(security_log_level)

    logger.info("Security environment configured")


def register_security_blueprints(app: Flask):
    """
    Register security-enabled blueprints with the Flask app.

    Args:
        app: Flask application instance
    """
    from .link_tracking_api import link_tracking_api_bp
    from .link_redirect_handler import link_redirect_bp

    # Register blueprints
    app.register_blueprint(link_tracking_api_bp)
    app.register_blueprint(link_redirect_bp)

    logger.info("Security-enabled link tracking blueprints registered")


def init_link_tracking_security(app: Flask):
    """
    Initialize complete link tracking security for Flask app.

    This is the main function to call when setting up the Flask application
    with comprehensive link tracking security.

    Args:
        app: Flask application instance
    """
    # Set up security environment
    setup_security_environment()

    # Initialize security middleware
    security_middleware = SecurityMiddleware(app)

    # Register security-enabled blueprints
    register_security_blueprints(app)

    logger.info("Link tracking security fully initialized")

    return security_middleware
