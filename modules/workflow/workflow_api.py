#!/usr/bin/env python3
"""
Workflow API for End-to-End Application Orchestration

This module provides REST API endpoints for Step 2.2 implementation:
- Workflow execution endpoints
- Status monitoring and tracking
- Performance metrics and analytics
- Workflow management operations
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import logging

from modules.workflow.application_orchestrator import ApplicationOrchestrator

# Create workflow API blueprint
workflow_api = Blueprint("workflow_api", __name__, url_prefix="/api/workflow")
logger = logging.getLogger(__name__)


def require_auth(f):
    """Authentication decorator for protected endpoints"""

    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Authentication required",
                        "message": "Please authenticate to access workflow endpoints",
                    }
                ),
                401,
            )
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@workflow_api.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for workflow system"""
    try:
        orchestrator = ApplicationOrchestrator()
        return jsonify(
            {
                "success": True,
                "message": "Workflow orchestration system is healthy",
                "system_status": "operational",
                "timestamp": datetime.now().isoformat(),
                "step": "2.2",
                "component": "End-to-End Workflow Orchestration",
            }
        )
    except Exception as e:
        logger.error(f"Workflow health check failed: {e}")
        return (
            jsonify(
                {"success": False, "error": str(e), "system_status": "error", "timestamp": datetime.now().isoformat()}
            ),
            500,
        )


@workflow_api.route("/execute", methods=["POST"])
@require_auth
def execute_workflow():
    """Execute complete end-to-end application workflow"""
    try:
        data = request.get_json() or {}
        batch_size = data.get("batch_size", 5)

        # Validate batch size
        if not isinstance(batch_size, int) or batch_size < 1 or batch_size > 20:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid batch_size",
                        "message": "batch_size must be an integer between 1 and 20",
                    }
                ),
                400,
            )

        orchestrator = ApplicationOrchestrator()
        results = orchestrator.execute_complete_workflow(batch_size=batch_size)

        return jsonify(
            {
                "success": True,
                "message": "Workflow execution completed",
                "data": results,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Workflow execution failed",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@workflow_api.route("/status/<workflow_id>", methods=["GET"])
@require_auth
def get_workflow_status(workflow_id):
    """Get status of specific workflow execution"""
    try:
        orchestrator = ApplicationOrchestrator()
        status = orchestrator.get_workflow_status(workflow_id)

        return jsonify(
            {
                "success": True,
                "message": "Workflow status retrieved",
                "data": status,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get workflow status for {workflow_id}: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to get status for workflow {workflow_id}",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@workflow_api.route("/metrics/daily", methods=["GET"])
@require_auth
def get_daily_metrics():
    """Get daily application metrics"""
    try:
        orchestrator = ApplicationOrchestrator()
        application_count = orchestrator.get_daily_application_count()

        return jsonify(
            {
                "success": True,
                "message": "Daily metrics retrieved",
                "data": {
                    "applications_sent_today": application_count,
                    "daily_limit": orchestrator.max_applications_per_day,
                    "remaining_applications": max(0, orchestrator.max_applications_per_day - application_count),
                    "date": datetime.now().date().isoformat(),
                },
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get daily metrics: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to retrieve daily metrics",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@workflow_api.route("/test", methods=["POST"])
@require_auth
def test_workflow():
    """Test workflow with limited scope for validation"""
    try:
        data = request.get_json() or {}
        test_mode = data.get("test_mode", "discovery_only")

        orchestrator = ApplicationOrchestrator()

        if test_mode == "discovery_only":
            # Test job discovery only
            eligible_jobs = orchestrator.discover_eligible_jobs(batch_size=3)

            return jsonify(
                {
                    "success": True,
                    "message": "Job discovery test completed",
                    "data": {
                        "test_mode": test_mode,
                        "eligible_jobs_found": len(eligible_jobs),
                        "sample_jobs": eligible_jobs[:2],  # Show first 2 for preview
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            )

        elif test_mode == "preference_matching":
            # Test preference matching
            eligible_jobs = orchestrator.discover_eligible_jobs(batch_size=3)
            matched_jobs = orchestrator.apply_preference_matching(eligible_jobs)

            return jsonify(
                {
                    "success": True,
                    "message": "Preference matching test completed",
                    "data": {
                        "test_mode": test_mode,
                        "eligible_jobs_found": len(eligible_jobs),
                        "matched_jobs": len(matched_jobs),
                        "filter_efficiency": len(matched_jobs) / len(eligible_jobs) if eligible_jobs else 0,
                        "sample_matches": [
                            {
                                "job_title": job.get("title"),
                                "company": job.get("company_name"),
                                "compatibility_score": job.get("compatibility_score"),
                            }
                            for job in matched_jobs[:2]
                        ],
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            )

        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid test mode",
                        "message": "Supported test modes: discovery_only, preference_matching",
                    }
                ),
                400,
            )

    except Exception as e:
        logger.error(f"Workflow test failed: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Workflow test failed",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@workflow_api.route("/config", methods=["GET"])
@require_auth
def get_workflow_config():
    """Get current workflow configuration"""
    try:
        orchestrator = ApplicationOrchestrator()

        return jsonify(
            {
                "success": True,
                "message": "Workflow configuration retrieved",
                "data": {
                    "max_applications_per_day": orchestrator.max_applications_per_day,
                    "min_compatibility_score": orchestrator.min_compatibility_score,
                    "max_batch_size": orchestrator.max_batch_size,
                    "system_components": {
                        "user_profile_loaded": bool(orchestrator.user_profile),
                        "document_generator_available": bool(orchestrator.document_generator),
                        "email_sender_configured": bool(orchestrator.email_sender),
                        "database_connected": bool(orchestrator.db_manager),
                    },
                },
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get workflow config: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to retrieve workflow configuration",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@workflow_api.route("/health", methods=["GET"])
def get_workflow_health():
    """Health check endpoint for Step 2.2 workflow system"""
    try:
        # Test orchestrator initialization
        orchestrator = ApplicationOrchestrator()

        return jsonify(
            {
                "success": True,
                "system_status": "operational",
                "step": "2.2",
                "component": "End-to-End Workflow Orchestration",
                "message": "Step 2.2 workflow system is healthy",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Workflow health check failed: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "system_status": "error",
                    "step": "2.2",
                    "component": "End-to-End Workflow Orchestration",
                    "error": str(e),
                    "message": "Step 2.2 workflow system has issues",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@workflow_api.route("/step-2-2/daily-metrics", methods=["GET"])
@require_auth
def get_step_2_2_daily_metrics():
    """Get daily application metrics for Step 2.2"""
    try:
        orchestrator = ApplicationOrchestrator()
        applications_sent = orchestrator.get_daily_application_count()

        return jsonify(
            {
                "success": True,
                "message": "Daily metrics retrieved",
                "data": {
                    "applications_sent_today": applications_sent,
                    "daily_limit": orchestrator.max_applications_per_day,
                    "remaining_applications": max(0, orchestrator.max_applications_per_day - applications_sent),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                },
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Failed to get daily metrics: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to retrieve daily metrics",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


# Export the blueprint
__all__ = ["workflow_api"]
