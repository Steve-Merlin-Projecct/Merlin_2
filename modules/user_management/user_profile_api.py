#!/usr/bin/env python3
"""
User Profile API Routes - Step 2.1 Implementation
API endpoints for managing Steve Glen's user profile and preferences

Provides RESTful API for user profile validation and management
"""

import logging
from flask import Blueprint, jsonify, request
from typing import Dict, Any
from .user_profile_loader import (
    SteveGlenProfileLoader,
    load_steve_glen_profile,
    get_steve_glen_summary,
    validate_profile_status,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
user_profile_bp = Blueprint("user_profile", __name__, url_prefix="/api/user-profile")


@user_profile_bp.route("/steve-glen/summary", methods=["GET"])
def get_steve_glen_profile_summary():
    """
    Get Steve Glen's complete profile summary

    Returns:
        JSON: Complete profile data including preferences and packages
    """
    try:
        summary = get_steve_glen_summary()

        response = {
            "success": True,
            "message": "Profile summary retrieved successfully",
            "data": summary,
            "timestamp": summary.get("timestamp", "unknown"),
        }

        # Set HTTP status based on profile completeness
        if summary.get("status") == "complete":
            status_code = 200
        elif summary.get("status") == "partial":
            status_code = 206  # Partial Content
        elif summary.get("status") == "error":
            status_code = 500
        else:
            status_code = 404  # Not Found

        return jsonify(response), status_code

    except Exception as e:
        logger.error(f"Error retrieving profile summary: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve profile summary", "details": str(e)}), 500


@user_profile_bp.route("/steve-glen/load", methods=["POST"])
def load_steve_glen_complete_profile():
    """
    Execute Step 2.1: Load Steve Glen's complete user profile

    Returns:
        JSON: Implementation results with acceptance criteria status
    """
    try:
        logger.info("API request to load Steve Glen's complete profile")

        # Execute Step 2.1 implementation
        results = load_steve_glen_profile()

        response = {
            "success": results["success"],
            "message": results["message"],
            "step": results["step"],
            "title": results["title"],
            "started_at": results["started_at"],
            "completed_at": results["completed_at"],
            "operations": results["operations"],
            "acceptance_criteria": results["acceptance_criteria"],
            "profile_summary": results.get("profile_summary", {}),
        }

        # Include error details if present
        if "error" in results:
            response["error"] = results["error"]

        # Set status code based on success
        status_code = 200 if results["success"] else 207  # Multi-Status for partial success

        return jsonify(response), status_code

    except Exception as e:
        logger.error(f"Error loading complete profile: {e}")
        return jsonify({"success": False, "error": "Failed to load complete profile", "details": str(e)}), 500


@user_profile_bp.route("/steve-glen/validate", methods=["GET"])
def validate_steve_glen_profile():
    """
    Quick validation of Steve Glen's profile completion status

    Returns:
        JSON: Validation status with simple boolean result
    """
    try:
        is_complete = validate_profile_status()
        summary = get_steve_glen_summary()

        response = {
            "success": True,
            "is_complete": is_complete,
            "status": summary.get("status", "unknown"),
            "criteria_summary": {
                "base_preferences": bool(summary.get("base_preferences")),
                "industry_preferences": len(summary.get("industry_preferences", [])) > 0,
                "preference_packages": len(summary.get("preference_packages", [])) >= 3,
            },
            "message": "Profile is complete and ready" if is_complete else "Profile needs completion",
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error validating profile: {e}")
        return jsonify({"success": False, "is_complete": False, "error": "Validation failed", "details": str(e)}), 500


@user_profile_bp.route("/steve-glen/preferences/industry", methods=["GET"])
def get_steve_glen_industry_preferences():
    """
    Get Steve Glen's industry preferences specifically

    Returns:
        JSON: Industry preferences with priority ordering
    """
    try:
        summary = get_steve_glen_summary()
        industry_preferences = summary.get("industry_preferences", [])

        response = {
            "success": True,
            "message": f"Retrieved {len(industry_preferences)} industry preferences",
            "data": {
                "industry_preferences": industry_preferences,
                "total_count": len(industry_preferences),
                "preferred_count": len([p for p in industry_preferences if p.get("preference_type") == "preferred"]),
                "acceptable_count": len([p for p in industry_preferences if p.get("preference_type") == "acceptable"]),
            },
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error retrieving industry preferences: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve industry preferences", "details": str(e)}), 500


@user_profile_bp.route("/steve-glen/preferences/packages", methods=["GET"])
def get_steve_glen_preference_packages():
    """
    Get Steve Glen's contextual preference packages

    Returns:
        JSON: Preference packages with salary ranges and location priorities
    """
    try:
        summary = get_steve_glen_summary()
        preference_packages = summary.get("preference_packages", [])

        response = {
            "success": True,
            "message": f"Retrieved {len(preference_packages)} preference packages",
            "data": {
                "preference_packages": preference_packages,
                "total_count": len(preference_packages),
                "salary_ranges": {
                    pkg.get("package_name", "Unknown"): {
                        "minimum": pkg.get("salary_minimum"),
                        "maximum": pkg.get("salary_maximum"),
                        "location": pkg.get("location_priority"),
                        "work_arrangement": pkg.get("work_arrangement"),
                    }
                    for pkg in preference_packages
                },
            },
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error retrieving preference packages: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve preference packages", "details": str(e)}), 500


@user_profile_bp.route("/steve-glen/status", methods=["GET"])
def get_step_2_1_status():
    """
    Get Step 2.1 implementation status and acceptance criteria

    Returns:
        JSON: Step 2.1 status with detailed acceptance criteria
    """
    try:
        summary = get_steve_glen_summary()

        # Map summary data to acceptance criteria
        acceptance_criteria = {
            "user_profile_created": bool(summary.get("base_preferences")),
            "preference_packages_loaded": len(summary.get("preference_packages", [])) >= 3,
            "industry_preferences_configured": len(summary.get("industry_preferences", [])) >= 5,
            "profile_validation_available": summary.get("status") in ["complete", "partial"],
        }

        criteria_met = sum(acceptance_criteria.values())
        total_criteria = len(acceptance_criteria)
        completion_percentage = (criteria_met / total_criteria) * 100

        response = {
            "success": True,
            "step": "2.1",
            "title": "Steve Glen User Preferences",
            "status": "complete" if criteria_met >= 3 else "partial" if criteria_met >= 1 else "incomplete",
            "completion_percentage": completion_percentage,
            "acceptance_criteria": acceptance_criteria,
            "criteria_met": criteria_met,
            "total_criteria": total_criteria,
            "profile_status": summary.get("status", "unknown"),
            "message": f'Step 2.1 is {"complete" if criteria_met >= 3 else "incomplete"} ({criteria_met}/{total_criteria} criteria met)',
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error getting Step 2.1 status: {e}")
        return jsonify({"success": False, "error": "Failed to get Step 2.1 status", "details": str(e)}), 500


@user_profile_bp.route("/health", methods=["GET"])
def user_profile_health():
    """
    Health check for user profile system

    Returns:
        JSON: System health status
    """
    try:
        # Test database connectivity
        loader = SteveGlenProfileLoader()
        summary = loader.get_profile_summary()

        response = {
            "success": True,
            "message": "User profile system is healthy",
            "system_status": "operational",
            "database_connectivity": "ok",
            "profile_system_status": summary.get("status", "unknown"),
            "timestamp": summary.get("timestamp", "unknown"),
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"User profile system health check failed: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "User profile system health check failed",
                    "system_status": "error",
                    "error": str(e),
                }
            ),
            500,
        )


# Error handlers for the blueprint
@user_profile_bp.errorhandler(404)
def not_found(error):
    return (
        jsonify(
            {
                "success": False,
                "error": "Endpoint not found",
                "message": "The requested user profile endpoint does not exist",
            }
        ),
        404,
    )


@user_profile_bp.errorhandler(500)
def internal_error(error):
    return (
        jsonify(
            {
                "success": False,
                "error": "Internal server error",
                "message": "An unexpected error occurred in the user profile system",
            }
        ),
        500,
    )
