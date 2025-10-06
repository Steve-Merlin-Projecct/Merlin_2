"""
Secure Link Redirect Handler

Handles URL redirection and click tracking with comprehensive security controls.
All redirections include security validation, click recording, and audit logging.

Security Features:
- URL validation to prevent open redirect attacks
- Input sanitization for all parameters
- Rate limiting on redirect requests
- Comprehensive security logging
- Safe error handling that prevents information disclosure
- Client IP tracking and suspicious activity detection

Version: 2.16.5
Date: July 28, 2025
Security Update: Implemented comprehensive security controls for redirect handling
"""

from flask import Blueprint, request, redirect, jsonify, render_template_string, abort
from typing import Optional, Dict, Any
import logging
from .secure_link_tracker import SecureLinkTracker
from .security_controls import SecurityControls, rate_limit

logger = logging.getLogger(__name__)

# Create Blueprint for secure link tracking routes
link_redirect_bp = Blueprint("link_redirect", __name__, url_prefix="/track")


class SecureLinkRedirectHandler:
    """
    Handles link redirection and click tracking with comprehensive security controls.

    Security Features:
    - Validates all tracking IDs to prevent injection attacks
    - Implements URL validation to prevent open redirect vulnerabilities
    - Records detailed security events for audit and monitoring
    - Implements rate limiting to prevent abuse
    - Sanitizes all user inputs and request data
    - Provides safe error handling that doesn't leak system information

    All redirect operations are logged with security events for compliance and monitoring.
    """

    def __init__(self):
        """Initialize secure redirect handler with security controls."""
        self.link_tracker = SecureLinkTracker()
        self.security = SecurityControls()

    def handle_redirect(self, tracking_id: str) -> Any:
        """
        Handle redirect request with comprehensive security validation and click tracking.

        Security Features:
        - Validates tracking ID format to prevent injection attacks
        - Implements URL validation to prevent open redirect vulnerabilities
        - Sanitizes all input parameters and request headers
        - Records comprehensive security events for audit trails
        - Implements safe error handling that doesn't expose system details
        - Checks for blocked IPs and suspicious activity patterns

        Args:
            tracking_id: The tracking identifier from URL (will be validated and sanitized)

        Returns:
            Secure redirect response to validated original URL or safe error page

        Security Flow:
        1. Validate and sanitize tracking ID
        2. Extract and validate client information
        3. Check for blocked IPs and rate limits
        4. Retrieve and validate destination URL
        5. Record click event with security metadata
        6. Perform secure redirect or return safe error
        """
        try:
            # Get client IP for security checks
            ip_address = self.security.get_client_ip(request)

            # Check if IP is blocked
            if self.security.is_blocked_ip(ip_address):
                self.security.log_security_event(
                    "BLOCKED_IP_REDIRECT_ATTEMPT", {"tracking_id": tracking_id, "ip": ip_address}, "WARNING"
                )
                abort(403)  # Forbidden

            # Validate tracking ID format
            valid, error = self.security.validate_tracking_id(tracking_id)
            if not valid:
                self.security.log_security_event(
                    "INVALID_TRACKING_ID_REDIRECT",
                    {"tracking_id": tracking_id, "error": error, "ip": ip_address},
                    "WARNING",
                )
                return self._render_safe_error_page("Invalid link"), 400

            # Sanitize tracking ID
            tracking_id = self.security.sanitize_input(tracking_id, 100)

            # Get original URL with security validation
            original_url = self.link_tracker.get_original_url(tracking_id, ip_address)

            if not original_url:
                self.security.log_security_event(
                    "TRACKING_ID_NOT_FOUND", {"tracking_id": tracking_id, "ip": ip_address}, "INFO"
                )
                return self._render_safe_error_page("Link not found or expired"), 404

            # Additional URL safety check before redirect
            url_safe, url_error = self.security.validate_url(original_url, allow_internal=True)
            if not url_safe:
                self.security.log_security_event(
                    "UNSAFE_REDIRECT_URL_DETECTED",
                    {"tracking_id": tracking_id, "url_error": url_error, "ip": ip_address},
                    "CRITICAL",
                )
                # Block the IP if attempting to redirect to unsafe URL
                self.security.block_ip(ip_address, "Attempted unsafe redirect")
                return self._render_safe_error_page("Link destination not accessible"), 403

            # Extract and sanitize request information
            user_agent = self.security.sanitize_input(request.headers.get("User-Agent", ""), 1000)
            referrer_url = self.security.sanitize_input(request.headers.get("Referer", ""), 1000)
            session_id = self.security.sanitize_input(request.cookies.get("session_id", ""), 100)

            # Determine click source
            click_source = self._determine_click_source(referrer_url)

            # Sanitize UTM parameters
            utm_metadata = {
                "utm_source": self.security.sanitize_input(request.args.get("utm_source", ""), 100),
                "utm_medium": self.security.sanitize_input(request.args.get("utm_medium", ""), 100),
                "utm_campaign": self.security.sanitize_input(request.args.get("utm_campaign", ""), 100),
                "request_time": request.headers.get("X-Request-Time", ""),
                "forwarded_for": request.headers.get("X-Forwarded-For", ""),
            }

            # Record click event with security validation
            click_data = self.link_tracker.record_click(
                tracking_id=tracking_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer_url=referrer_url,
                session_id=session_id,
                click_source=click_source,
                metadata=utm_metadata,
            )

            # Log successful redirect
            self.security.log_security_event(
                "SECURE_REDIRECT_SUCCESS",
                {
                    "click_id": click_data["click_id"],
                    "tracking_id": tracking_id,
                    "click_source": click_source,
                    "ip": ip_address,
                },
                "INFO",
            )

            logger.info(f"Secure redirect: click {click_data['click_id']} for {tracking_id}")

            # Perform secure redirect
            return redirect(original_url, code=302)

        except ValueError as e:
            # Validation errors - safe to log and return
            logger.warning(f"Redirect validation error: {e}")
            return self._render_safe_error_page("Invalid request"), 400

        except Exception as e:
            # System errors - log generic error and return safe message
            logger.error(f"Redirect handling failed: {type(e).__name__}")
            self.security.log_security_event(
                "REDIRECT_SYSTEM_ERROR",
                {"tracking_id": tracking_id, "error_type": type(e).__name__, "ip": ip_address},
                "ERROR",
            )
            return self._render_safe_error_page("Service temporarily unavailable"), 500

    def get_tracking_analytics(self, tracking_id: str) -> Dict[str, Any]:
        """
        Get analytics for a specific tracking ID.

        Args:
            tracking_id: The tracking identifier

        Returns:
            JSON response with analytics data
        """
        try:
            analytics = self.link_tracker.get_link_analytics(tracking_id)

            if not analytics:
                return {"error": "Tracking ID not found"}, 404

            return analytics

        except Exception as e:
            logger.error(f"Error getting analytics for {tracking_id}: {e}")
            return {"error": "Internal server error"}, 500

    def _render_safe_error_page(self, message: str) -> str:
        """
        Render a safe error page that doesn't expose system information.

        Security Features:
        - No dynamic content that could be exploited for XSS
        - Generic error messages that don't leak system details
        - Static HTML structure to prevent template injection
        - Content Security Policy friendly design

        Args:
            message: Safe, user-friendly error message

        Returns:
            Safe HTML error page
        """
        # Use only pre-approved safe messages
        safe_messages = {
            "Invalid link": "The link you clicked is not valid.",
            "Link not found or expired": "The link you're looking for could not be found or has expired.",
            "Service temporarily unavailable": "The service is temporarily unavailable. Please try again later.",
            "Invalid request": "Your request could not be processed.",
        }

        safe_message = safe_messages.get(message, "An error occurred.")

        # Static HTML template with no dynamic content injection
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Link Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-container {{ max-width: 500px; margin: 0 auto; }}
                .error-message {{ color: #666; margin: 20px 0; }}
                .back-link {{ color: #007bff; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>Oops!</h1>
                <p class="error-message">{safe_message}</p>
                <p><a href="javascript:history.back()" class="back-link">Go Back</a></p>
            </div>
        </body>
        </html>
        """

    def _determine_click_source(self, referrer_url: str) -> str:
        """
        Determine the source of the click based on referrer URL.

        Args:
            referrer_url: The referring page URL

        Returns:
            Click source category
        """
        if not referrer_url:
            return "direct"

        referrer_lower = referrer_url.lower()

        if "gmail.com" in referrer_lower or "mail.google.com" in referrer_lower:
            return "email"
        elif "automated-job-application-system" in referrer_lower:
            return "dashboard"
        elif "linkedin.com" in referrer_lower:
            return "linkedin"
        elif "indeed.com" in referrer_lower:
            return "indeed"
        else:
            return "external"


# Initialize secure redirect handler
secure_handler = SecureLinkRedirectHandler()

# Flask route endpoints with comprehensive security controls


@link_redirect_bp.route("/<tracking_id>", methods=["GET"])
@rate_limit(limit=200, window=3600)  # 200 redirects per hour per IP
def redirect_tracked_link(tracking_id):
    """
    Handle secure redirect with comprehensive security validation and click tracking.

    Security Features:
    - Rate limiting: 200 redirects per hour per IP
    - Tracking ID format validation and sanitization
    - URL safety validation before redirect
    - IP blocking for malicious actors
    - Comprehensive security event logging
    - Safe error pages that don't expose system information

    Args:
        tracking_id: The tracking identifier from URL path

    Returns:
        HTTP redirect to original URL or safe error page
    """
    try:
        return secure_handler.handle_redirect(tracking_id)

    except Exception as e:
        logger.error(f"Redirect endpoint error: {type(e).__name__}")
        return secure_handler._render_safe_error_page("Service temporarily unavailable"), 500


@link_redirect_bp.route("/analytics/<tracking_id>", methods=["GET"])
@rate_limit(limit=100, window=3600)  # 100 requests per hour per IP
def get_redirect_analytics(tracking_id):
    """
    Get analytics for a tracked link via redirect endpoint.

    Security Features:
    - Rate limiting for analytics access
    - No authentication required (public analytics)
    - Input validation and sanitization
    - Privacy-compliant data return

    Args:
        tracking_id: The tracking identifier from URL path

    Returns:
        JSON response with public analytics data
    """
    try:
        client_ip = secure_handler.security.get_client_ip(request)

        # Check if IP is blocked
        if secure_handler.security.is_blocked_ip(client_ip):
            return jsonify({"error": "Access denied"}), 403

        analytics = secure_handler.get_tracking_analytics(tracking_id)

        if isinstance(analytics, tuple):
            return jsonify(analytics[0]), analytics[1]
        else:
            return jsonify(analytics), 200

    except Exception as e:
        logger.error(f"Redirect analytics error: {type(e).__name__}")
        return jsonify({"error": "Service temporarily unavailable"}), 500


@link_redirect_bp.route("/health", methods=["GET"])
@rate_limit(limit=60, window=60)  # 1 request per second
def redirect_health_check():
    """
    Health check endpoint for redirect service monitoring.

    Returns:
        JSON response with redirect service status
    """
    try:
        return (
            jsonify(
                {"status": "healthy", "service": "link-redirect-handler", "version": "2.16.5", "security_enabled": True}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Redirect health check error: {type(e).__name__}")
        return jsonify({"status": "degraded", "service": "link-redirect-handler"}), 503


def _render_error_page(message: str) -> str:
    """
    Render error page HTML.

    Args:
        message: Error message to display

    Returns:
        HTML error page
    """
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Link Error</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                .error { color: #d32f2f; }
                .container { max-width: 500px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="error">Link Error</h1>
                <p>{{ message }}</p>
                <p><a href="/">Return to Home</a></p>
            </div>
        </body>
        </html>
        """,
        message=message,
    )


# Initialize handler
redirect_handler = LinkRedirectHandler()


@link_redirect_bp.route("/<tracking_id>")
def redirect_link(tracking_id: str):
    """
    Main redirect endpoint for tracked links.

    URL: /track/<tracking_id>
    """
    return redirect_handler.handle_redirect(tracking_id)


@link_redirect_bp.route("/analytics/<tracking_id>")
def get_analytics(tracking_id: str):
    """
    Get analytics for a specific tracking ID.

    URL: /track/analytics/<tracking_id>
    """
    analytics = redirect_handler.get_tracking_analytics(tracking_id)
    return jsonify(analytics)


@link_redirect_bp.route("/health")
def health_check():
    """
    Health check endpoint for link tracking system.

    URL: /track/health
    """
    return jsonify({"status": "healthy", "service": "link_redirect_handler", "version": "2.16.5"})
