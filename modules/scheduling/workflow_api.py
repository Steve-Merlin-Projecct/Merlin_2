"""
Workflow API Routes for Scheduling Management
Provides REST endpoints for workflow scheduling and monitoring
"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from modules.scheduling.workflow_scheduler import get_scheduler, WorkflowPhase
from modules.dashboard_api import require_dashboard_auth as require_auth

logger = logging.getLogger(__name__)

# Create blueprint for workflow API
workflow_api = Blueprint("workflow_api", __name__, url_prefix="/api/workflow")


@workflow_api.route("/status", methods=["GET"])
@require_auth
def get_workflow_status():
    """Get current workflow scheduling status"""

    try:
        scheduler = get_scheduler()
        status = scheduler.get_workflow_status()

        return jsonify({"success": True, "data": status})

    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@workflow_api.route("/next-phase", methods=["GET"])
@require_auth
def get_next_phase():
    """Get next scheduled workflow phase"""

    try:
        current_phase_str = request.args.get("current_phase")
        current_phase = None

        if current_phase_str:
            try:
                current_phase = WorkflowPhase(current_phase_str)
            except ValueError:
                return jsonify({"success": False, "error": f"Invalid phase: {current_phase_str}"}), 400

        scheduler = get_scheduler()
        next_phase = scheduler.get_next_scheduled_phase(current_phase)

        return jsonify(
            {
                "success": True,
                "data": {
                    "phase": next_phase["phase"].value,
                    "scheduled_time": next_phase["scheduled_time"].isoformat(),
                    "description": next_phase["description"],
                },
            }
        )

    except Exception as e:
        logger.error(f"Failed to get next phase: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@workflow_api.route("/phase-ready/<phase>", methods=["GET"])
@require_auth
def check_phase_ready(phase):
    """Check if a workflow phase is ready to run"""

    try:
        # Validate phase
        try:
            workflow_phase = WorkflowPhase(phase)
        except ValueError:
            return jsonify({"success": False, "error": f"Invalid phase: {phase}"}), 400

        # Get last run time from query parameter
        last_run_str = request.args.get("last_run")
        last_run = None
        if last_run_str:
            try:
                last_run = datetime.fromisoformat(last_run_str)
            except ValueError:
                return jsonify({"success": False, "error": "Invalid last_run format. Use ISO format."}), 400

        scheduler = get_scheduler()
        is_ready = scheduler.is_phase_ready(workflow_phase, last_run)

        return jsonify(
            {
                "success": True,
                "data": {
                    "phase": phase,
                    "ready": is_ready,
                    "last_run": last_run_str,
                    "current_time": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        logger.error(f"Failed to check phase readiness: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@workflow_api.route("/schedule-summary", methods=["GET"])
@require_auth
def get_schedule_summary():
    """Get summary of all workflow schedules"""

    try:
        scheduler = get_scheduler()

        # Get schedule for each phase
        phases_schedule = []

        for phase in WorkflowPhase:
            next_run = scheduler.get_next_scheduled_phase(phase)
            phases_schedule.append(
                {
                    "phase": phase.value,
                    "next_scheduled": next_run["scheduled_time"].isoformat(),
                    "description": next_run["description"],
                }
            )

        return jsonify(
            {
                "success": True,
                "data": {
                    "current_time": datetime.now().isoformat(),
                    "timezone": "America/Denver",
                    "phases": phases_schedule,
                    "workflow_description": {
                        "frequency": "Every 2nd day cycle",
                        "sequence": [
                            "Job Scraping (9:30 AM MT)",
                            "AI Analysis (11:00 PM MT same day)",
                            "Application Sending (10:15 AM MT next day)",
                        ],
                    },
                },
            }
        )

    except Exception as e:
        logger.error(f"Failed to get schedule summary: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
