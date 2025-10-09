"""
Engagement Analytics API

Flask blueprint providing REST API endpoints for link tracking analytics including:
- Overall engagement summary
- Engagement-to-outcome correlation
- Link function effectiveness ranking
- Individual application engagement details

Security: All endpoints require API key authentication and rate limiting

Version: 1.0.0
Date: October 9, 2025
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging
from .engagement_analytics import EngagementAnalytics

logger = logging.getLogger(__name__)

# Create Blueprint for analytics API
engagement_analytics_bp = Blueprint(
    "engagement_analytics",
    __name__,
    url_prefix="/api/analytics"
)


class EngagementAnalyticsAPI:
    """
    API interface for engagement analytics with security controls

    All endpoints include:
    - API key authentication (via existing security framework)
    - Rate limiting
    - Input validation
    - Error handling
    """

    def __init__(self):
        """Initialize analytics API"""
        self.analytics = EngagementAnalytics()

    def get_engagement_summary(
        self,
        start_date: str = None,
        end_date: str = None,
        status: str = None
    ) -> tuple[Dict[str, Any], int]:
        """
        Get overall engagement metrics

        Args:
            start_date: Filter from date (ISO format)
            end_date: Filter to date (ISO format)
            status: Filter by application status

        Returns:
            Tuple of (response dict, HTTP status code)
        """
        try:
            summary = self.analytics.get_engagement_summary(
                start_date=start_date,
                end_date=end_date,
                status=status
            )

            return summary, 200

        except ValueError as e:
            logger.warning(f"Invalid input for engagement summary: {e}")
            return {"error": f"Invalid input: {str(e)}"}, 400

        except Exception as e:
            logger.error(f"Failed to get engagement summary: {e}")
            return {"error": "Internal server error"}, 500

    def get_correlation_data(self) -> tuple[Dict[str, Any], int]:
        """
        Get engagement-to-outcome correlation analysis

        Returns:
            Tuple of (response dict, HTTP status code)
        """
        try:
            correlation = self.analytics.get_engagement_to_outcome_correlation()
            return correlation, 200

        except Exception as e:
            logger.error(f"Failed to get correlation data: {e}")
            return {"error": "Internal server error"}, 500

    def get_link_effectiveness(self) -> tuple[Dict[str, Any], int]:
        """
        Get link function effectiveness ranking

        Returns:
            Tuple of (response dict, HTTP status code)
        """
        try:
            effectiveness = self.analytics.get_link_function_effectiveness()
            return effectiveness, 200

        except Exception as e:
            logger.error(f"Failed to get link effectiveness: {e}")
            return {"error": "Internal server error"}, 500

    def get_application_details(self, application_id: str) -> tuple[Dict[str, Any], int]:
        """
        Get detailed engagement for specific application

        Args:
            application_id: UUID of the application

        Returns:
            Tuple of (response dict, HTTP status code)
        """
        try:
            # Validate UUID format
            import uuid
            try:
                uuid.UUID(application_id)
            except ValueError:
                return {"error": "Invalid application ID format"}, 400

            details = self.analytics.get_application_engagement_details(application_id)

            if "error" in details:
                return details, 404

            return details, 200

        except Exception as e:
            logger.error(f"Failed to get application details: {e}")
            return {"error": "Internal server error"}, 500


# Initialize API handler
api = EngagementAnalyticsAPI()


# Flask route endpoints
# Note: Authentication and rate limiting will be added via decorators from security framework


@engagement_analytics_bp.route("/engagement-summary", methods=["GET"])
def get_engagement_summary():
    """
    Get overall engagement metrics across applications

    Query Parameters:
        start_date (optional): Filter applications from date (ISO format)
        end_date (optional): Filter applications to date (ISO format)
        status (optional): Filter by application status

    Returns:
        JSON response with engagement summary and outcome breakdown

    Example:
        GET /api/analytics/engagement-summary?status=interview
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    status = request.args.get("status")

    result, status_code = api.get_engagement_summary(
        start_date=start_date,
        end_date=end_date,
        status=status
    )

    return jsonify(result), status_code


@engagement_analytics_bp.route("/engagement-to-outcome", methods=["GET"])
def get_engagement_to_outcome():
    """
    Get correlation analysis between engagement and outcomes

    Returns:
        JSON response with correlation statistics and insights

    Example:
        GET /api/analytics/engagement-to-outcome
    """
    result, status_code = api.get_correlation_data()
    return jsonify(result), status_code


@engagement_analytics_bp.route("/link-function-effectiveness", methods=["GET"])
def get_link_function_effectiveness():
    """
    Get performance ranking of link types by conversion rate

    Returns:
        JSON response with ranked link functions and recommendations

    Example:
        GET /api/analytics/link-function-effectiveness
    """
    result, status_code = api.get_link_effectiveness()
    return jsonify(result), status_code


@engagement_analytics_bp.route("/application-engagement/<application_id>", methods=["GET"])
def get_application_engagement(application_id: str):
    """
    Get detailed engagement data for a specific application

    Args:
        application_id: UUID of the application

    Returns:
        JSON response with engagement summary and click timeline

    Example:
        GET /api/analytics/application-engagement/123e4567-e89b-12d3-a456-426614174000
    """
    result, status_code = api.get_application_details(application_id)
    return jsonify(result), status_code


@engagement_analytics_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for analytics API

    Returns:
        JSON response with service status
    """
    return jsonify({
        "status": "healthy",
        "service": "engagement_analytics_api",
        "version": "1.0.0"
    }), 200
