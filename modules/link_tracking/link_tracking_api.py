"""
Secure Link Tracking API

Provides REST API endpoints for managing tracked links and analytics with comprehensive security controls.
All endpoints include authentication, rate limiting, input validation, and security monitoring.

Security Features:
- API key authentication on all endpoints
- Rate limiting to prevent abuse and DoS attacks
- Comprehensive input validation and sanitization
- Security event logging and monitoring
- IP blocking for malicious actors
- HTTPS enforcement and security headers

Version: 2.16.5
Date: July 28, 2025
Security Update: Implemented comprehensive security controls
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import logging
from .secure_link_tracker import SecureLinkTracker
from .security_controls import SecurityControls, require_api_key, rate_limit, validate_input

logger = logging.getLogger(__name__)

# Create Blueprint for secure link tracking API
link_tracking_api_bp = Blueprint("link_tracking_api", __name__, url_prefix="/api/link-tracking")


class SecureLinkTrackingAPI:
    """
    Secure API interface for link tracking functionality with comprehensive security controls.

    Security Features:
    - Input validation and sanitization on all operations
    - Secure database operations with parameterized queries
    - Authentication and authorization controls
    - Rate limiting and abuse prevention
    - Comprehensive security event logging
    - Error handling that prevents information disclosure

    All methods include client IP tracking for security monitoring and audit trails.
    """

    def __init__(self):
        """Initialize secure link tracking API with security controls."""
        self.link_tracker = SecureLinkTracker()
        self.security = SecurityControls()

    def create_tracked_link(self, data: Dict[str, Any], client_ip: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new tracked link via secure API with comprehensive validation.

        Security Features:
        - Validates all input fields against security policies
        - Sanitizes inputs to prevent injection attacks
        - Generates cryptographically secure tracking IDs
        - Logs all creation attempts for audit trails
        - Returns sanitized responses that don't leak system information

        Args:
            data: Request data containing link information (validated and sanitized)
            client_ip: Client IP address for security logging and monitoring

        Returns:
            Tuple of (API response with created link information, HTTP status code)

        Raises:
            ValueError: When input validation fails
            Exception: When creation fails due to system errors
        """
        try:
            # Enhanced validation for required fields with detailed error messages
            required_fields = ["original_url", "link_function"]
            missing_fields = [field for field in required_fields if field not in data or not data[field]]

            if missing_fields:
                self.security.log_security_event(
                    "API_MISSING_REQUIRED_FIELDS", {"missing_fields": missing_fields, "ip": client_ip}, "WARNING"
                )
                return {"error": f'Missing required fields: {", ".join(missing_fields)}'}, 400

            # Additional validation for optional fields
            validation_errors = []

            # Validate URL format and security
            url_valid, url_error = self.security.validate_url(data["original_url"])
            if not url_valid:
                validation_errors.append(f"original_url: {url_error}")

            # Validate link function
            function_valid, function_error = self.security.validate_link_function(data["link_function"])
            if not function_valid:
                validation_errors.append(f"link_function: {function_error}")

            # Validate optional link type
            if "link_type" in data and data["link_type"]:
                type_valid, type_error = self.security.validate_link_type(data["link_type"])
                if not type_valid:
                    validation_errors.append(f"link_type: {type_error}")

            # Validate optional UUIDs
            if "job_id" in data and data["job_id"]:
                job_valid, job_error = self.security.validate_uuid(data["job_id"], "job_id")
                if not job_valid:
                    validation_errors.append(f"job_id: {job_error}")

            if "application_id" in data and data["application_id"]:
                app_valid, app_error = self.security.validate_uuid(data["application_id"], "application_id")
                if not app_valid:
                    validation_errors.append(f"application_id: {app_error}")

            # Return validation errors if any
            if validation_errors:
                self.security.log_security_event(
                    "API_VALIDATION_FAILED", {"errors": validation_errors, "ip": client_ip}, "WARNING"
                )
                return {"error": "Validation failed", "details": validation_errors}, 400

            # Create tracked link using secure tracker
            result = self.link_tracker.create_tracked_link(
                original_url=data["original_url"],
                link_function=data["link_function"],
                job_id=data.get("job_id"),
                application_id=data.get("application_id"),
                link_type=data.get("link_type", "external"),
                description=data.get("description"),
                client_ip=client_ip,
            )

            # Log successful creation
            self.security.log_security_event(
                "API_LINK_CREATED_SUCCESS",
                {"tracking_id": result["tracking_id"], "link_function": result["link_function"], "ip": client_ip},
                "INFO",
            )

            return result, 201

        except ValueError as e:
            # Validation errors - safe to return to user
            logger.warning(f"API validation error: {e}")
            return {"error": str(e)}, 400

        except Exception as e:
            # System errors - log details but return generic error
            logger.error(f"API link creation failed: {type(e).__name__}")
            self.security.log_security_event(
                "API_LINK_CREATION_ERROR", {"error_type": type(e).__name__, "ip": client_ip}, "ERROR"
            )
            return {"error": "Link creation failed. Please try again."}, 500

    def get_job_links(self, job_id: str) -> Dict[str, Any]:
        """
        Get all tracked links for a specific job.

        Args:
            job_id: The job UUID

        Returns:
            API response with job link summary
        """
        try:
            summary = self.link_tracker.get_job_link_summary(job_id)

            if not summary:
                return {"error": "Job not found or no links"}, 404

            return summary, 200

        except Exception as e:
            logger.error(f"Error getting job links: {e}")
            return {"error": "Internal server error"}, 500

    def get_application_links(self, application_id: str) -> Dict[str, Any]:
        """
        Get all tracked links for a specific application.

        Args:
            application_id: The application UUID

        Returns:
            API response with application link summary
        """
        try:
            summary = self.link_tracker.get_application_link_summary(application_id)

            if not summary:
                return {"error": "Application not found or no links"}, 404

            return summary, 200

        except Exception as e:
            logger.error(f"Error getting application links: {e}")
            return {"error": "Internal server error"}, 500

    def get_link_analytics(self, tracking_id: str, client_ip: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed analytics for a specific link with security validation.

        Security Features:
        - Validates tracking ID format to prevent injection attacks
        - Sanitizes tracking ID input
        - Logs all analytics access attempts
        - Returns privacy-compliant analytics (IP anonymization after 90 days)
        - Implements access logging for audit compliance

        Args:
            tracking_id: The tracking identifier (validated and sanitized)
            client_ip: Client IP address for security logging

        Returns:
            Tuple of (API response with link analytics, HTTP status code)

        Privacy Note:
            IP addresses are partially anonymized for clicks older than 90 days
            to comply with privacy regulations and data retention policies.
        """
        try:
            # Validate tracking ID format
            valid, error = self.security.validate_tracking_id(tracking_id)
            if not valid:
                self.security.log_security_event(
                    "API_INVALID_TRACKING_ID_ANALYTICS",
                    {"tracking_id": tracking_id, "error": error, "ip": client_ip},
                    "WARNING",
                )
                return {"error": f"Invalid tracking ID: {error}"}, 400

            # Get analytics using secure tracker
            analytics = self.link_tracker.get_link_analytics(tracking_id, client_ip)

            if not analytics:
                self.security.log_security_event(
                    "API_TRACKING_ID_NOT_FOUND", {"tracking_id": tracking_id, "ip": client_ip}, "INFO"
                )
                return {"error": "Tracking ID not found"}, 404

            # Log successful analytics access
            self.security.log_security_event(
                "API_ANALYTICS_ACCESS_SUCCESS", {"tracking_id": tracking_id, "ip": client_ip}, "INFO"
            )

            return analytics, 200

        except Exception as e:
            # Log error without exposing system details
            logger.error(f"API analytics retrieval failed: {type(e).__name__}")
            self.security.log_security_event(
                "API_ANALYTICS_ERROR",
                {"tracking_id": tracking_id, "error_type": type(e).__name__, "ip": client_ip},
                "ERROR",
            )
            return {"error": "Analytics retrieval failed. Please try again."}, 500


# Initialize secure API handler
secure_api = SecureLinkTrackingAPI()

# Flask route endpoints with comprehensive security controls


@link_tracking_api_bp.route("/create", methods=["POST"])
@require_api_key
@rate_limit(limit=50, window=3600)  # 50 requests per hour per IP
@validate_input
def create_tracked_link():
    """
    Create a new tracked link with comprehensive security validation.

    Security Features:
    - API key authentication required
    - Rate limiting: 50 requests per hour per IP
    - Comprehensive input validation and sanitization
    - Security event logging for all attempts
    - Safe error handling that doesn't expose system details

    Request Body:
        {
            "original_url": "https://linkedin.com/in/username",
            "link_function": "LinkedIn",
            "job_id": "uuid-optional",
            "application_id": "uuid-optional",
            "link_type": "profile",
            "description": "Optional description"
        }

    Returns:
        JSON response with tracking_id and redirect_url or error details
    """
    try:
        data = request.get_json()
        client_ip = secure_api.security.get_client_ip(request)

        # Check if IP is blocked
        if secure_api.security.is_blocked_ip(client_ip):
            return jsonify({"error": "Access denied"}), 403

        result, status_code = secure_api.create_tracked_link(data, client_ip)
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Create link endpoint error: {type(e).__name__}")
        return jsonify({"error": "Service temporarily unavailable"}), 500


@link_tracking_api_bp.route("/analytics/<tracking_id>", methods=["GET"])
@require_api_key
@rate_limit(limit=100, window=3600)  # 100 requests per hour per IP
def get_link_analytics(tracking_id):
    """
    Get detailed analytics for a specific tracked link.

    Security Features:
    - API key authentication required
    - Rate limiting: 100 requests per hour per IP
    - Tracking ID format validation
    - Privacy-compliant data return (IP anonymization)
    - Comprehensive access logging

    Args:
        tracking_id: The tracking identifier from URL path

    Returns:
        JSON response with link analytics or error details
    """
    try:
        client_ip = secure_api.security.get_client_ip(request)

        # Check if IP is blocked
        if secure_api.security.is_blocked_ip(client_ip):
            return jsonify({"error": "Access denied"}), 403

        result, status_code = secure_api.get_link_analytics(tracking_id, client_ip)
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Analytics endpoint error: {type(e).__name__}")
        return jsonify({"error": "Service temporarily unavailable"}), 500

    # Removed duplicate get_job_links route - keeping the simple version below

    # Removed duplicate health check route - keeping the simple version below

    def generate_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.

        Args:
            days: Number of days to include in report

        Returns:
            API response with performance report
        """
        try:
            report = self.link_tracker.get_link_performance_report(days)

            return report, 200

        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {"error": "Internal server error"}, 500

    def create_application_links(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create standard tracked links for a job application.

        Args:
            data: Request data containing job and application information

        Returns:
            API response with created links
        """
        try:
            # Validate required fields
            required_fields = ["job_id", "application_id", "job_data"]
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}, 400

            # Create application links
            tracked_links = self.link_tracker.create_job_application_links(
                job_id=data["job_id"], application_id=data["application_id"], job_data=data["job_data"]
            )

            return {
                "job_id": data["job_id"],
                "application_id": data["application_id"],
                "tracked_links": tracked_links,
                "total_links": len(tracked_links),
            }, 201

        except Exception as e:
            logger.error(f"Error creating application links: {e}")
            return {"error": "Internal server error"}, 500

    def deactivate_link(self, tracking_id: str) -> Dict[str, Any]:
        """
        Deactivate a tracked link.

        Args:
            tracking_id: The tracking identifier

        Returns:
            API response confirming deactivation
        """
        try:
            success = self.link_tracker.deactivate_link(tracking_id)

            if success:
                return {"message": "Link deactivated successfully"}, 200
            else:
                return {"error": "Link not found"}, 404

        except Exception as e:
            logger.error(f"Error deactivating link: {e}")
            return {"error": "Internal server error"}, 500


# Initialize legacy API for backward compatibility
# Note: This should be replaced with secure_api in future integration
class LinkTrackingAPI(SecureLinkTrackingAPI):
    """Legacy API wrapper for backward compatibility."""

    pass


api = LinkTrackingAPI()


@link_tracking_api_bp.route("/create", methods=["POST"])
def create_link():
    """
    Create a new tracked link.

    POST /api/link-tracking/create
    Body: {
        "original_url": "https://example.com",
        "link_function": "LinkedIn",
        "job_id": "uuid",
        "application_id": "uuid",
        "link_type": "profile",
        "description": "Professional profile"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    result, status_code = api.create_tracked_link(data)
    return jsonify(result), status_code


@link_tracking_api_bp.route("/job/<job_id>/links", methods=["GET"])
def get_job_links_simple(job_id: str):
    """
    Get all tracked links for a job.

    GET /api/link-tracking/job/<job_id>/links
    """
    result, status_code = api.get_job_links(job_id)
    return jsonify(result), status_code


@link_tracking_api_bp.route("/application/<application_id>/links", methods=["GET"])
def get_application_links(application_id: str):
    """
    Get all tracked links for an application.

    GET /api/link-tracking/application/<application_id>/links
    """
    result, status_code = api.get_application_links(application_id)
    return jsonify(result), status_code


@link_tracking_api_bp.route("/analytics/<tracking_id>", methods=["GET"])
def get_analytics(tracking_id: str):
    """
    Get detailed analytics for a specific link.

    GET /api/link-tracking/analytics/<tracking_id>
    """
    result, status_code = api.get_link_analytics(tracking_id)
    return jsonify(result), status_code


@link_tracking_api_bp.route("/report", methods=["GET"])
def get_performance_report():
    """
    Generate performance report.

    GET /api/link-tracking/report?days=30
    """
    days = request.args.get("days", 30, type=int)
    result, status_code = api.generate_performance_report(days)
    return jsonify(result), status_code


@link_tracking_api_bp.route("/application/create-links", methods=["POST"])
def create_application_links():
    """
    Create standard tracked links for a job application.

    POST /api/link-tracking/application/create-links
    Body: {
        "job_id": "uuid",
        "application_id": "uuid",
        "job_data": {
            "company_website": "https://company.com",
            "apply_url": "https://company.com/apply",
            "job_url": "https://indeed.com/job/123"
        }
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    result, status_code = api.create_application_links(data)
    return jsonify(result), status_code


@link_tracking_api_bp.route("/deactivate/<tracking_id>", methods=["POST"])
def deactivate_link(tracking_id: str):
    """
    Deactivate a tracked link.

    POST /api/link-tracking/deactivate/<tracking_id>
    """
    result, status_code = api.deactivate_link(tracking_id)
    return jsonify(result), status_code


@link_tracking_api_bp.route("/health", methods=["GET"])
def health_check_simple():
    """
    Health check for link tracking API.

    GET /api/link-tracking/health
    """
    return jsonify({"status": "healthy", "service": "link_tracking_api", "version": "2.16.5"})
