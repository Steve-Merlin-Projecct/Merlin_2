"""
Flask API for Application Automation

This module provides RESTful API endpoints for the application automation system.
It handles Actor triggering, submission tracking, and result reporting.

Endpoints:
- POST /api/application-automation/trigger - Trigger Apify Actor for job application
- POST /api/application-automation/submissions - Record submission results (from Actor)
- GET /api/application-automation/submissions/<submission_id> - Get submission details
- GET /api/application-automation/submissions - List submissions with filters
- PUT /api/application-automation/submissions/<submission_id>/review - Mark as reviewed
- GET /api/application-automation/stats - Get automation statistics
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps

from flask import Blueprint, request, jsonify
from apify_client import ApifyClient

# Import database manager
from modules.database.database_manager import DatabaseManager

# Import security for API key validation
from modules.security.security_manager import SecurityManager

logger = logging.getLogger(__name__)

# Create Blueprint
automation_api = Blueprint("automation_api", __name__, url_prefix="/api/application-automation")


# Decorator for API key authentication
def require_api_key(f):
    """Decorator to require API key authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        expected_key = os.environ.get("WEBHOOK_API_KEY")

        if not api_key or api_key != expected_key:
            logger.warning(f"Unauthorized API request from {request.remote_addr}")
            return jsonify({"success": False, "error": "Unauthorized - Invalid API key"}), 401

        return f(*args, **kwargs)

    return decorated_function


class AutomationAPI:
    """
    API handler for application automation endpoints

    This class encapsulates all business logic for the automation API endpoints,
    including Actor triggering, submission tracking, and reporting.
    """

    def __init__(self):
        """Initialize automation API"""
        self.db_manager = DatabaseManager()
        self.security = SecurityManager()
        self.apify_token = os.environ.get("APIFY_TOKEN")
        self.actor_id = os.environ.get(
            "APPLICATION_AUTOMATION_ACTOR_ID", "your-username/application-automation"
        )

        if self.apify_token:
            self.apify_client = ApifyClient(self.apify_token)
        else:
            logger.warning("APIFY_TOKEN not set - Actor triggering will not work")
            self.apify_client = None

    def trigger_application_automation(self, job_id: str, application_id: str) -> Dict[str, Any]:
        """
        Trigger Apify Actor to automate job application

        Args:
            job_id: Job posting ID
            application_id: Application tracking ID

        Returns:
            Dictionary with Actor run information

        Raises:
            Exception: If Actor triggering fails
        """
        if not self.apify_client:
            raise Exception("Apify client not configured - missing APIFY_TOKEN")

        try:
            logger.info(f"Triggering application automation for job {job_id}")

            # Get Flask API base URL
            api_base_url = os.environ.get("FLASK_API_URL", request.url_root.rstrip("/"))

            # Prepare Actor input
            actor_input = {
                "job_id": job_id,
                "application_id": application_id,
                "api_base_url": api_base_url,
                "api_key": os.environ.get("WEBHOOK_API_KEY"),
                "headless": True,
                "timeout": 30000,
            }

            # Start Actor run
            run = self.apify_client.actor(self.actor_id).call(run_input=actor_input)

            run_id = run["id"]
            run_status = run["status"]

            logger.info(f"Actor started: run_id={run_id}, status={run_status}")

            # Create pending submission record
            submission_id = self._create_pending_submission(
                application_id=application_id, job_id=job_id, actor_run_id=run_id
            )

            return {
                "success": True,
                "actor_run_id": run_id,
                "actor_status": run_status,
                "submission_id": submission_id,
                "message": "Application automation started",
            }

        except Exception as e:
            logger.error(f"Failed to trigger Actor: {e}")
            raise Exception(f"Failed to trigger automation: {e}")

    def record_submission_result(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record submission result from Apify Actor

        This endpoint is called by the Actor after completing the form filling.

        Args:
            submission_data: Submission result data from Actor

        Returns:
            Dictionary with success status

        Raises:
            Exception: If database operation fails
        """
        try:
            application_id = submission_data.get("application_id")
            job_id = submission_data.get("job_id")

            logger.info(f"Recording submission result for application {application_id}")

            # Prepare screenshot URLs
            screenshots = submission_data.get("screenshots", [])
            screenshot_urls = [s.get("file_path") or s.get("storage_url") for s in screenshots]

            # Insert or update submission record
            query = """
                INSERT INTO application_submissions (
                    application_id, job_id, actor_run_id, status, form_platform,
                    form_type, fields_filled, submission_confirmed, confirmation_message,
                    screenshot_urls, screenshot_metadata, error_message, error_details,
                    submitted_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (submission_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    form_type = EXCLUDED.form_type,
                    fields_filled = EXCLUDED.fields_filled,
                    submission_confirmed = EXCLUDED.submission_confirmed,
                    confirmation_message = EXCLUDED.confirmation_message,
                    screenshot_urls = EXCLUDED.screenshot_urls,
                    screenshot_metadata = EXCLUDED.screenshot_metadata,
                    error_message = EXCLUDED.error_message,
                    error_details = EXCLUDED.error_details,
                    updated_at = NOW()
                RETURNING submission_id;
            """

            params = (
                application_id,
                job_id,
                submission_data.get("actor_run_id"),
                submission_data.get("status", "submitted"),
                submission_data.get("form_platform", "indeed"),
                submission_data.get("form_type"),
                submission_data.get("fields_filled"),
                submission_data.get("submission_confirmed", False),
                submission_data.get("confirmation_message"),
                screenshot_urls,
                {"screenshots": screenshots, "screenshot_count": len(screenshots)},
                submission_data.get("error_message"),
                submission_data.get("error_details"),
                submission_data.get("submitted_at", datetime.utcnow()),
            )

            result = self.db_manager.execute_raw_sql(query, params)
            submission_id = result[0][0] if result else None

            logger.info(f"Submission recorded: {submission_id}")

            return {
                "success": True,
                "submission_id": str(submission_id),
                "message": "Submission result recorded",
            }

        except Exception as e:
            logger.error(f"Failed to record submission result: {e}")
            raise Exception(f"Failed to record submission: {e}")

    def get_submission(self, submission_id: str) -> Dict[str, Any]:
        """
        Get submission details by ID

        Args:
            submission_id: Submission UUID

        Returns:
            Dictionary with submission details

        Raises:
            Exception: If submission not found
        """
        try:
            query = "SELECT * FROM application_submissions WHERE submission_id = %s;"
            result = self.db_manager.execute_raw_sql(query, (submission_id,))

            if not result:
                raise Exception(f"Submission not found: {submission_id}")

            # Convert to dictionary
            columns = [
                "submission_id",
                "application_id",
                "job_id",
                "actor_run_id",
                "status",
                "form_platform",
                "form_type",
                "fields_filled",
                "submission_confirmed",
                "confirmation_message",
                "screenshot_urls",
                "screenshot_metadata",
                "error_message",
                "error_details",
                "submitted_at",
                "reviewed_at",
                "created_at",
                "updated_at",
                "reviewed_by",
                "review_notes",
            ]

            submission = dict(zip(columns, result[0]))

            return {"success": True, "data": submission}

        except Exception as e:
            logger.error(f"Failed to get submission: {e}")
            raise Exception(f"Failed to get submission: {e}")

    def list_submissions(
        self, status: Optional[str] = None, job_id: Optional[str] = None, limit: int = 50
    ) -> Dict[str, Any]:
        """
        List submissions with optional filters

        Args:
            status: Filter by status
            job_id: Filter by job ID
            limit: Maximum number of results

        Returns:
            Dictionary with list of submissions
        """
        try:
            query = "SELECT * FROM application_submissions WHERE 1=1"
            params = []

            if status:
                query += " AND status = %s"
                params.append(status)

            if job_id:
                query += " AND job_id = %s"
                params.append(job_id)

            query += " ORDER BY submitted_at DESC LIMIT %s;"
            params.append(limit)

            results = self.db_manager.execute_raw_sql(query, tuple(params))

            # Convert to list of dictionaries
            columns = [
                "submission_id",
                "application_id",
                "job_id",
                "actor_run_id",
                "status",
                "form_platform",
                "form_type",
                "fields_filled",
                "submission_confirmed",
                "confirmation_message",
                "screenshot_urls",
                "screenshot_metadata",
                "error_message",
                "error_details",
                "submitted_at",
                "reviewed_at",
                "created_at",
                "updated_at",
                "reviewed_by",
                "review_notes",
            ]

            submissions = [dict(zip(columns, row)) for row in results]

            return {"success": True, "data": submissions, "count": len(submissions)}

        except Exception as e:
            logger.error(f"Failed to list submissions: {e}")
            raise Exception(f"Failed to list submissions: {e}")

    def mark_as_reviewed(
        self, submission_id: str, reviewed_by: str, review_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark submission as reviewed

        Args:
            submission_id: Submission UUID
            reviewed_by: User ID who reviewed
            review_notes: Optional review notes

        Returns:
            Dictionary with success status
        """
        try:
            query = """
                UPDATE application_submissions
                SET status = 'reviewed',
                    reviewed_at = NOW(),
                    reviewed_by = %s,
                    review_notes = %s,
                    updated_at = NOW()
                WHERE submission_id = %s
                RETURNING submission_id;
            """

            result = self.db_manager.execute_raw_sql(query, (reviewed_by, review_notes, submission_id))

            if not result:
                raise Exception(f"Submission not found: {submission_id}")

            logger.info(f"Submission {submission_id} marked as reviewed by {reviewed_by}")

            return {"success": True, "message": "Submission marked as reviewed"}

        except Exception as e:
            logger.error(f"Failed to mark as reviewed: {e}")
            raise Exception(f"Failed to mark as reviewed: {e}")

    def get_automation_stats(self) -> Dict[str, Any]:
        """
        Get automation statistics

        Returns:
            Dictionary with statistics
        """
        try:
            query = """
                SELECT
                    COUNT(*) as total_submissions,
                    COUNT(*) FILTER (WHERE status = 'submitted') as successful_submissions,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_submissions,
                    COUNT(*) FILTER (WHERE submission_confirmed = TRUE) as confirmed_submissions,
                    AVG(CASE WHEN submission_confirmed THEN 1.0 ELSE 0.0 END) as confirmation_rate,
                    form_platform,
                    form_type
                FROM application_submissions
                WHERE submitted_at >= NOW() - INTERVAL '30 days'
                GROUP BY form_platform, form_type;
            """

            results = self.db_manager.execute_raw_sql(query)

            stats = []
            for row in results:
                stats.append(
                    {
                        "total_submissions": row[0],
                        "successful_submissions": row[1],
                        "failed_submissions": row[2],
                        "confirmed_submissions": row[3],
                        "confirmation_rate": float(row[4]) if row[4] else 0.0,
                        "form_platform": row[5],
                        "form_type": row[6],
                    }
                )

            return {"success": True, "data": stats}

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise Exception(f"Failed to get stats: {e}")

    def _create_pending_submission(
        self, application_id: str, job_id: str, actor_run_id: str
    ) -> str:
        """
        Create pending submission record

        Args:
            application_id: Application tracking ID
            job_id: Job posting ID
            actor_run_id: Apify Actor run ID

        Returns:
            Submission ID
        """
        query = """
            INSERT INTO application_submissions (
                application_id, job_id, actor_run_id, status, form_platform
            ) VALUES (%s, %s, %s, 'pending', 'indeed')
            RETURNING submission_id;
        """

        result = self.db_manager.execute_raw_sql(query, (application_id, job_id, actor_run_id))
        return str(result[0][0]) if result else None


# Initialize API handler
api_handler = AutomationAPI()


# Flask route handlers
@automation_api.route("/trigger", methods=["POST"])
@require_api_key
def trigger_automation():
    """Trigger application automation for a job"""
    try:
        data = request.get_json()

        job_id = data.get("job_id")
        application_id = data.get("application_id")

        if not job_id or not application_id:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        result = api_handler.trigger_application_automation(job_id, application_id)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Trigger automation failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@automation_api.route("/submissions", methods=["POST"])
@require_api_key
def record_submission():
    """Record submission result from Apify Actor"""
    try:
        submission_data = request.get_json()

        result = api_handler.record_submission_result(submission_data)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Record submission failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@automation_api.route("/submissions/<submission_id>", methods=["GET"])
@require_api_key
def get_submission(submission_id):
    """Get submission details by ID"""
    try:
        result = api_handler.get_submission(submission_id)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Get submission failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 404


@automation_api.route("/submissions", methods=["GET"])
@require_api_key
def list_submissions():
    """List submissions with optional filters"""
    try:
        status = request.args.get("status")
        job_id = request.args.get("job_id")
        limit = int(request.args.get("limit", 50))

        result = api_handler.list_submissions(status=status, job_id=job_id, limit=limit)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"List submissions failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@automation_api.route("/submissions/<submission_id>/review", methods=["PUT"])
@require_api_key
def mark_reviewed(submission_id):
    """Mark submission as reviewed"""
    try:
        data = request.get_json()

        reviewed_by = data.get("reviewed_by", "system")
        review_notes = data.get("review_notes")

        result = api_handler.mark_as_reviewed(submission_id, reviewed_by, review_notes)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Mark reviewed failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@automation_api.route("/stats", methods=["GET"])
@require_api_key
def get_stats():
    """Get automation statistics"""
    try:
        result = api_handler.get_automation_stats()
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Get stats failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
