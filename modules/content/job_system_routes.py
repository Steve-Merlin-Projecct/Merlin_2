"""
Job Application System Routes
Flask routes for the automated job application system

RELEVANCE ASSESSMENT:
This module provides Flask route endpoints for the complete automated job application workflow.

CURRENT STATUS: HIGHLY RELEVANT
- Provides API endpoints for running complete job workflow (/job-system/run-workflow)
- Handles system statistics and monitoring (/job-system/stats)
- Manages click tracking for job applications (/track/<tracking_id>)
- Integrates with JobApplicationSystem orchestrator class
- Uses authentication for protected endpoints

DEPENDENCIES:
- JobApplicationSystem: Main workflow orchestrator
- LinkTracker: Click tracking functionality
- Authentication system via session management

LOCATION RECOMMENDATION:
Should be moved to modules/content/job_system_routes.py to follow the new organization structure
where all job application content-related modules are grouped together.

INTEGRATION WITH NEW PIPELINE:
This module will be essential for the planned job scraper → AI analysis → document generation pipeline
as it provides the web endpoints to trigger and monitor the complete workflow.
"""

from flask import Blueprint, jsonify, request, redirect, session
import logging
from functools import wraps
from .job_application_system import JobApplicationSystem
from ..link_tracker import LinkTracker


def require_job_auth(f):
    """Authentication decorator for job system endpoints"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


# Create blueprint
job_system_bp = Blueprint("job_system", __name__)

# Initialize system
job_system = JobApplicationSystem()
link_tracker = LinkTracker()


@job_system_bp.route("/job-system/run-workflow", methods=["POST"])
def run_workflow():
    """
    Run the complete job application workflow
    """
    try:
        results = job_system.run_complete_workflow()

        return jsonify({"status": "success", "message": "Job application workflow completed", "results": results})

    except Exception as e:
        logging.error(f"Workflow failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@job_system_bp.route("/job-system/stats", methods=["GET"])
@require_job_auth
def get_stats():
    """
    Get system statistics
    """
    try:
        stats = job_system.get_system_stats()

        return jsonify({"status": "success", "stats": stats})

    except Exception as e:
        logging.error(f"Failed to get stats: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@job_system_bp.route("/track/<tracking_id>")
def track_click(tracking_id):
    """
    Handle click tracking and redirect to original URL
    """
    try:
        # Get client info
        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent")

        # Record click and get original URL
        original_url = link_tracker.record_click(tracking_id, ip_address, user_agent)

        if original_url:
            return redirect(original_url)
        else:
            return jsonify({"status": "error", "message": "Tracking ID not found"}), 404

    except Exception as e:
        logging.error(f"Click tracking failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@job_system_bp.route("/job-system/applications/<application_id>/tracking")
def get_tracking_stats(application_id):
    """
    Get tracking statistics for an application
    """
    try:
        stats = link_tracker.get_tracking_stats(application_id)

        return jsonify({"status": "success", "application_id": application_id, "tracking_stats": stats})

    except Exception as e:
        logging.error(f"Failed to get tracking stats: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
