#!/usr/bin/env python3
"""
Email Application API Module

Provides REST API endpoints for managing automated job application email sending.
Includes endpoints for manual triggering, status monitoring, and batch processing.
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from modules.workflow.email_application_sender import EmailApplicationSender

logger = logging.getLogger(__name__)

email_application_api = Blueprint("email_application_api", __name__)


def require_auth(f):
    """Decorator to require authentication for API endpoints"""

    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return (
                jsonify({"error": "Authentication required", "message": "Please log in to access this endpoint"}),
                401,
            )
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@email_application_api.route("/api/email-applications/send/<job_id>", methods=["POST"])
@require_auth
def send_single_application(job_id):
    """Send application for a specific job"""
    try:
        sender = EmailApplicationSender()

        # Get job data from database
        with sender.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT j.*, c.name as company_name
                FROM analyzed_jobs j
                LEFT JOIN companies c ON j.company_id = c.id
                WHERE j.id = %s
            """,
                (job_id,),
            )

            job_data = cursor.fetchone()
            if not job_data:
                return jsonify({"success": False, "error": "Job not found"}), 404

            # Convert to dictionary
            job_dict = dict(zip([desc[0] for desc in cursor.description], job_data))

        # Send application
        result = sender.send_job_application(job_dict)

        return jsonify(
            {
                "success": result["success"],
                "job_id": job_id,
                "job_title": job_dict.get("job_title"),
                "company_name": job_dict.get("company_name"),
                "result": result,
            }
        )

    except Exception as e:
        logger.error(f"Single application sending error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@email_application_api.route("/api/email-applications/batch", methods=["POST"])
@require_auth
def send_batch_applications():
    """Send multiple applications in batch"""
    try:
        data = request.get_json() or {}
        limit = data.get("limit", 5)

        if limit > 20:  # Safety limit
            limit = 20

        sender = EmailApplicationSender()
        results = sender.process_eligible_applications(limit)

        return jsonify({"success": True, "batch_results": results, "processed_at": datetime.now().isoformat()})

    except Exception as e:
        logger.error(f"Batch application sending error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@email_application_api.route("/api/email-applications/eligible", methods=["GET"])
@require_auth
def get_eligible_applications():
    """Get list of jobs eligible for application sending"""
    try:
        sender = EmailApplicationSender()

        with sender.get_db_connection() as conn:
            cursor = conn.cursor()

            # Get jobs eligible for sending
            cursor.execute(
                """
                SELECT 
                    j.id,
                    j.job_title,
                    c.name as company_name,
                    j.compatibility_score,
                    j.posted_date,
                    j.created_at,
                    j.submission_deadline,
                    j.application_email,
                    ja.status as application_status,
                    ja.email_sent_at
                FROM analyzed_jobs j
                LEFT JOIN companies c ON j.company_id = c.id
                LEFT JOIN job_applications ja ON j.id = ja.job_id
                WHERE j.compatibility_score >= 50
                ORDER BY j.compatibility_score DESC, j.created_at ASC
                LIMIT 50
            """
            )

            jobs = cursor.fetchall()

            eligible_jobs = []
            pending_jobs = []
            already_sent = []

            for job in jobs:
                job_dict = dict(zip([desc[0] for desc in cursor.description], job))

                # Check eligibility
                is_eligible, reason = sender.check_sending_eligibility(job_dict)

                job_info = {
                    "id": job_dict["id"],
                    "job_title": job_dict["job_title"],
                    "company_name": job_dict["company_name"],
                    "compatibility_score": job_dict["compatibility_score"],
                    "posted_date": job_dict["posted_date"].isoformat() if job_dict["posted_date"] else None,
                    "created_at": job_dict["created_at"].isoformat() if job_dict["created_at"] else None,
                    "submission_deadline": (
                        job_dict["submission_deadline"].isoformat() if job_dict["submission_deadline"] else None
                    ),
                    "has_email": bool(job_dict["application_email"]),
                    "application_status": job_dict["application_status"],
                    "email_sent_at": job_dict["email_sent_at"].isoformat() if job_dict["email_sent_at"] else None,
                    "eligibility_reason": reason,
                }

                if job_dict["application_status"] == "sent":
                    already_sent.append(job_info)
                elif is_eligible:
                    eligible_jobs.append(job_info)
                else:
                    pending_jobs.append(job_info)

        return jsonify(
            {
                "success": True,
                "summary": {
                    "eligible_count": len(eligible_jobs),
                    "pending_count": len(pending_jobs),
                    "sent_count": len(already_sent),
                    "total_analyzed": len(jobs),
                },
                "eligible_jobs": eligible_jobs,
                "pending_jobs": pending_jobs,
                "already_sent": already_sent,
            }
        )

    except Exception as e:
        logger.error(f"Error getting eligible applications: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@email_application_api.route("/api/email-applications/stats", methods=["GET"])
@require_auth
def get_application_stats():
    """Get application sending statistics"""
    try:
        sender = EmailApplicationSender()

        with sender.get_db_connection() as conn:
            cursor = conn.cursor()

            # Get overall statistics
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_applications,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_count,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
                    COUNT(CASE WHEN email_sent_at >= CURRENT_DATE THEN 1 END) as sent_today,
                    COUNT(CASE WHEN email_sent_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as sent_this_week
                FROM job_applications
            """
            )

            stats = cursor.fetchone()
            stat_dict = dict(zip([desc[0] for desc in cursor.description], stats))

            # Get recent applications
            cursor.execute(
                """
                SELECT 
                    ja.job_id,
                    j.job_title,
                    c.name as company_name,
                    ja.status,
                    ja.email_sent_at,
                    ja.email_message_id
                FROM job_applications ja
                JOIN analyzed_jobs j ON ja.job_id = j.id
                LEFT JOIN companies c ON j.company_id = c.id
                WHERE ja.email_sent_at >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY ja.email_sent_at DESC
                LIMIT 20
            """
            )

            recent_applications = []
            for app in cursor.fetchall():
                app_dict = dict(zip([desc[0] for desc in cursor.description], app))
                app_dict["email_sent_at"] = app_dict["email_sent_at"].isoformat() if app_dict["email_sent_at"] else None
                recent_applications.append(app_dict)

        return jsonify(
            {
                "success": True,
                "statistics": stat_dict,
                "recent_applications": recent_applications,
                "generated_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error getting application stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@email_application_api.route("/api/email-applications/test-eligibility/<job_id>", methods=["GET"])
@require_auth
def test_job_eligibility(job_id):
    """Test eligibility for a specific job without sending"""
    try:
        sender = EmailApplicationSender()

        with sender.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT j.*, c.name as company_name
                FROM analyzed_jobs j
                LEFT JOIN companies c ON j.company_id = c.id
                WHERE j.id = %s
            """,
                (job_id,),
            )

            job_data = cursor.fetchone()
            if not job_data:
                return jsonify({"success": False, "error": "Job not found"}), 404

            job_dict = dict(zip([desc[0] for desc in cursor.description], job_data))

        # Test eligibility
        is_eligible, reason = sender.check_sending_eligibility(job_dict)

        # Extract email information
        job_description = job_dict.get("job_description", "")
        application_email = job_dict.get("application_email")
        extracted_email = sender.extract_email_from_job_description(job_description, application_email)

        # Compose email preview
        recipient_email = extracted_email or sender.fallback_email
        subject, body = sender.compose_email_content(job_dict, recipient_email)

        return jsonify(
            {
                "success": True,
                "job_id": job_id,
                "job_title": job_dict.get("job_title"),
                "company_name": job_dict.get("company_name"),
                "eligibility": {"is_eligible": is_eligible, "reason": reason},
                "email_info": {
                    "recipient": recipient_email,
                    "is_fallback": recipient_email == sender.fallback_email,
                    "extracted_from_description": bool(extracted_email),
                    "subject": subject,
                    "body_preview": body[:500] + "..." if len(body) > 500 else body,
                },
                "job_details": {
                    "posted_date": job_dict.get("posted_date").isoformat() if job_dict.get("posted_date") else None,
                    "created_at": job_dict.get("created_at").isoformat() if job_dict.get("created_at") else None,
                    "submission_deadline": (
                        job_dict.get("submission_deadline").isoformat() if job_dict.get("submission_deadline") else None
                    ),
                    "compatibility_score": job_dict.get("compatibility_score"),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error testing job eligibility: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@email_application_api.route("/api/email-applications/health", methods=["GET"])
def health_check():
    """Health check endpoint for email application system"""
    try:
        sender = EmailApplicationSender()

        # Test database connection
        with sender.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            db_ok = cursor.fetchone()[0] == 1

        # Check email sender availability
        email_sender_type = type(sender.email_sender).__name__
        email_ok = email_sender_type != "MockEmailSender"

        # Check document generator availability
        doc_gen_type = type(sender.document_generator).__name__
        doc_gen_ok = doc_gen_type != "MockDocumentGenerator"

        return jsonify(
            {
                "success": True,
                "status": "healthy",
                "components": {
                    "database": "ok" if db_ok else "error",
                    "email_sender": {"status": "ok" if email_ok else "mock", "type": email_sender_type},
                    "document_generator": {"status": "ok" if doc_gen_ok else "mock", "type": doc_gen_type},
                },
                "configuration": {
                    "waiting_period_days": sender.waiting_period_days,
                    "fallback_email": sender.fallback_email,
                },
                "checked_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"success": False, "status": "unhealthy", "error": str(e)}), 500
