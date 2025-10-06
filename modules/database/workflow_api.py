"""
Workflow API Routes for New Job Processing Pipeline
=================================================

This module provides REST API endpoints for the new workflow:
raw_job_scrapes -> cleaned_job_scrapes -> pre_analyzed_jobs -> ai analysis -> analyzed_jobs

Endpoints:
- POST /api/workflow/transfer-to-pre-analyzed - Transfer cleaned scrapes to pre_analyzed_jobs
- POST /api/workflow/queue-for-analysis - Queue jobs for AI analysis
- GET /api/workflow/jobs-for-analysis - Get jobs ready for AI analysis
- POST /api/workflow/save-analysis - Save AI analysis results
- GET /api/workflow/statistics - Get workflow statistics

Author: Automated Job Application System V2.16
Created: 2025-07-26
"""

import logging
from flask import Blueprint, request, jsonify, session
from modules.database.workflow_manager import WorkflowManager
from functools import wraps


def require_auth(f):
    """Simple auth decorator for workflow API"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


logger = logging.getLogger(__name__)

# Create Blueprint for workflow API routes
workflow_api = Blueprint("workflow_api", __name__, url_prefix="/api/workflow")


def create_workflow_manager():
    """Create workflow manager instance with error handling."""
    try:
        return WorkflowManager()
    except Exception as e:
        logger.error(f"Failed to create workflow manager: {e}")
        return None


@workflow_api.route("/transfer-to-pre-analyzed", methods=["POST"])
@require_auth
def transfer_to_pre_analyzed():
    """
    Transfer jobs from cleaned_job_scrapes to pre_analyzed_jobs.

    Request Body:
    {
        "batch_size": 100  // Optional, default 100
    }

    Response:
    {
        "success": true,
        "transferred": 25,
        "duplicates_found": 5,
        "processed": 30,
        "message": "Successfully transferred 25 jobs to pre_analyzed_jobs"
    }
    """
    try:
        data = request.get_json() or {}
        batch_size = data.get("batch_size", 100)

        # Validate batch size
        if not isinstance(batch_size, int) or batch_size <= 0 or batch_size > 1000:
            return jsonify({"success": False, "error": "batch_size must be integer between 1 and 1000"}), 400

        # Create workflow manager
        workflow_manager = create_workflow_manager()
        if not workflow_manager:
            return jsonify({"success": False, "error": "Failed to initialize workflow manager"}), 500

        # Perform transfer
        result = workflow_manager.transfer_cleaned_to_pre_analyzed(batch_size)

        # Log operation for audit trail
        logger.info(f"Transfer to pre_analyzed completed: {result}")

        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Error in transfer-to-pre-analyzed endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@workflow_api.route("/queue-for-analysis", methods=["POST"])
@require_auth
def queue_for_analysis():
    """
    Queue pre_analyzed_jobs for AI analysis.

    Request Body:
    {
        "limit": 50  // Optional, default 50
    }

    Response:
    {
        "success": true,
        "queued_count": 15,
        "job_ids": ["uuid1", "uuid2", ...],
        "message": "Successfully queued 15 jobs for analysis"
    }
    """
    try:
        data = request.get_json() or {}
        limit = data.get("limit", 50)

        # Validate limit
        if not isinstance(limit, int) or limit <= 0 or limit > 100:
            return jsonify({"success": False, "error": "limit must be integer between 1 and 100"}), 400

        # Create workflow manager
        workflow_manager = create_workflow_manager()
        if not workflow_manager:
            return jsonify({"success": False, "error": "Failed to initialize workflow manager"}), 500

        # Queue jobs for analysis
        result = workflow_manager.queue_jobs_for_analysis(limit)

        # Log operation for audit trail
        logger.info(f"Jobs queued for analysis: {result}")

        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Error in queue-for-analysis endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@workflow_api.route("/jobs-for-analysis", methods=["GET"])
@require_auth
def get_jobs_for_analysis():
    """
    Get queued jobs ready for AI analysis.

    Query Parameters:
    - batch_size: Number of jobs to return (default: 10, max: 25)

    Response:
    {
        "success": true,
        "jobs": [
            {
                "title": "Software Engineer",
                "description": "Job description...",
                "company_name": "Tech Corp",
                "industry": "Technology",
                "seniority_level": "mid-level",
                "salary_min": 70000,
                "salary_max": 90000,
                "currency": "CAD",
                "remote_options": "hybrid",
                "job_type": "full-time",
                "internal_dedup_key": "hash123..."
            }
        ],
        "count": 5,
        "message": "Retrieved 5 jobs for AI analysis"
    }
    """
    try:
        batch_size = request.args.get("batch_size", 10, type=int)

        # Validate batch size
        if batch_size <= 0 or batch_size > 25:
            return jsonify({"success": False, "error": "batch_size must be between 1 and 25"}), 400

        # Create workflow manager
        workflow_manager = create_workflow_manager()
        if not workflow_manager:
            return jsonify({"success": False, "error": "Failed to initialize workflow manager"}), 500

        # Get jobs for analysis
        jobs = workflow_manager.get_jobs_for_ai_analysis(batch_size)

        # Log operation for audit trail
        logger.info(f"Retrieved {len(jobs)} jobs for AI analysis")

        return (
            jsonify(
                {
                    "success": True,
                    "jobs": jobs,
                    "count": len(jobs),
                    "message": f"Retrieved {len(jobs)} jobs for AI analysis",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error in jobs-for-analysis endpoint: {e}")
        return jsonify({"success": False, "error": str(e), "jobs": [], "count": 0}), 500


@workflow_api.route("/save-analysis", methods=["POST"])
@require_auth
def save_analysis_results():
    """
    Save AI analysis results to analyzed_jobs table.

    Request Body:
    {
        "analysis_results": [
            {
                "internal_dedup_key": "hash123...",
                "primary_industry": "Technology",
                "authenticity_score": 0.92,
                "model_used": "gemini-2.0-flash-001",
                "skills_analysis": [...],
                "structured_data": {...}
            }
        ]
    }

    Response:
    {
        "success": true,
        "saved_count": 8,
        "skipped_count": 2,
        "total_processed": 10,
        "message": "Saved 8 analyzed jobs, skipped 2 duplicates"
    }
    """
    try:
        data = request.get_json()

        if not data or "analysis_results" not in data:
            return jsonify({"success": False, "error": "analysis_results array is required"}), 400

        analysis_results = data["analysis_results"]

        if not isinstance(analysis_results, list):
            return jsonify({"success": False, "error": "analysis_results must be an array"}), 400

        if len(analysis_results) > 50:
            return jsonify({"success": False, "error": "Cannot process more than 50 analysis results at once"}), 400

        # Create workflow manager
        workflow_manager = create_workflow_manager()
        if not workflow_manager:
            return jsonify({"success": False, "error": "Failed to initialize workflow manager"}), 500

        # Save analysis results
        result = workflow_manager.save_ai_analysis_results(analysis_results)

        # Log operation for audit trail
        logger.info(f"AI analysis results saved: {result}")

        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Error in save-analysis endpoint: {e}")
        return jsonify({"success": False, "error": str(e), "saved_count": 0, "skipped_count": 0}), 500


@workflow_api.route("/statistics", methods=["GET"])
@require_auth
def get_workflow_statistics():
    """
    Get comprehensive statistics about the new workflow.

    Response:
    {
        "success": true,
        "statistics": {
            "raw_job_scrapes": 1000,
            "cleaned_job_scrapes": 850,
            "pre_analyzed_jobs": 200,
            "pre_analyzed_queued": 50,
            "analyzed_jobs": 150,
            "analysis_completed": 145,
            "legacy_jobs": 300
        },
        "workflow_health": {
            "raw_to_cleaned_rate": 85.0,
            "cleaned_to_pre_analyzed_rate": 23.5,
            "pre_analyzed_to_analyzed_rate": 75.0,
            "analysis_completion_rate": 96.7
        }
    }
    """
    try:
        # Create workflow manager
        workflow_manager = create_workflow_manager()
        if not workflow_manager:
            return jsonify({"success": False, "error": "Failed to initialize workflow manager"}), 500

        # Get workflow statistics
        result = workflow_manager.get_workflow_statistics()

        # Log operation for audit trail
        logger.info(f"Workflow statistics retrieved successfully")

        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Error in workflow statistics endpoint: {e}")
        return jsonify({"success": False, "error": str(e), "statistics": {}, "workflow_health": {}}), 500


@workflow_api.route("/health", methods=["GET"])
def workflow_health_check():
    """
    Health check endpoint for workflow API.

    Response:
    {
        "status": "healthy",
        "timestamp": "2025-07-26T03:30:00Z",
        "workflow_api_version": "2.16"
    }
    """
    from datetime import datetime

    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "workflow_api_version": "2.16",
                "endpoints": [
                    "POST /api/workflow/transfer-to-pre-analyzed",
                    "POST /api/workflow/queue-for-analysis",
                    "GET /api/workflow/jobs-for-analysis",
                    "POST /api/workflow/save-analysis",
                    "GET /api/workflow/statistics",
                    "GET /api/workflow/health",
                ],
            }
        ),
        200,
    )


# Error handlers for the workflow API blueprint
@workflow_api.errorhandler(404)
def workflow_not_found(error):
    """Handle 404 errors for workflow API."""
    return (
        jsonify(
            {
                "success": False,
                "error": "Workflow API endpoint not found",
                "available_endpoints": [
                    "POST /api/workflow/transfer-to-pre-analyzed",
                    "POST /api/workflow/queue-for-analysis",
                    "GET /api/workflow/jobs-for-analysis",
                    "POST /api/workflow/save-analysis",
                    "GET /api/workflow/statistics",
                    "GET /api/workflow/health",
                ],
            }
        ),
        404,
    )


@workflow_api.errorhandler(405)
def workflow_method_not_allowed(error):
    """Handle 405 errors for workflow API."""
    return jsonify({"success": False, "error": "Method not allowed for this workflow endpoint"}), 405


@workflow_api.errorhandler(500)
def workflow_internal_error(error):
    """Handle 500 errors for workflow API."""
    logger.error(f"Internal server error in workflow API: {error}")
    return jsonify({"success": False, "error": "Internal server error in workflow API"}), 500
