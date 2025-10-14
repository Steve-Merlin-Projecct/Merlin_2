"""
Dashboard API Module
Provides endpoints for the job application dashboard
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
import logging
from functools import wraps
from sqlalchemy import text
from .database.lazy_instances import get_database_client
from .salary_formatter import format_salary_range

# Create blueprint
dashboard_api = Blueprint("dashboard_api", __name__)

# NOTE: Database client is now lazy-initialized on demand
# No module-level instantiation to prevent import-time connections


def require_dashboard_auth(f):
    """
    Decorator to require dashboard authentication for API endpoints
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Auto-authenticate in debug/development mode
        from flask import current_app
        if current_app.debug and not session.get("authenticated"):
            session['authenticated'] = True
            session['auth_time'] = datetime.now().timestamp()
            logging.info("Auto-authenticated in debug mode (API endpoint)")

        if not session.get("authenticated"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


@dashboard_api.route("/api/dashboard/stats", methods=["GET"])
@require_dashboard_auth
def get_dashboard_stats():
    """
    Get dashboard statistics including scrapes and applications
    """
    try:
        db_client = get_database_client()  # Lazy initialization
        with db_client.get_session() as session:
            # Calculate date ranges
            now = datetime.utcnow()
            day_ago = now - timedelta(days=1)
            week_ago = now - timedelta(days=7)
            current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Get scrape counts (jobs created in last 24h/week)
            scrapes_24h_result = session.execute(
                text(
                    """
                SELECT COUNT(*) FROM jobs 
                WHERE created_at >= :day_ago
            """
                ),
                {"day_ago": day_ago},
            )
            scrapes_24h_row = scrapes_24h_result.fetchone()
            scrapes_24h = scrapes_24h_row[0] if scrapes_24h_row else 0

            scrapes_week_result = session.execute(
                text(
                    """
                SELECT COUNT(*) FROM jobs 
                WHERE created_at >= :week_ago
            """
                ),
                {"week_ago": week_ago},
            )
            scrapes_week_row = scrapes_week_result.fetchone()
            scrapes_week = scrapes_week_row[0] if scrapes_week_row else 0

            # Get monthly scrape count
            scrapes_month_result = session.execute(
                text(
                    """
                SELECT COUNT(*) FROM jobs 
                WHERE created_at >= :current_month
            """
                ),
                {"current_month": current_month},
            )
            scrapes_month_row = scrapes_month_result.fetchone()
            scrapes_month = scrapes_month_row[0] if scrapes_month_row else 0

            # Get application counts (job_applications created in last 24h/week)
            applications_24h_result = session.execute(
                text(
                    """
                SELECT COUNT(*) FROM job_applications 
                WHERE created_at >= :day_ago
            """
                ),
                {"day_ago": day_ago},
            )
            applications_24h_row = applications_24h_result.fetchone()
            applications_24h = applications_24h_row[0] if applications_24h_row else 0

            applications_week_result = session.execute(
                text(
                    """
                SELECT COUNT(*) FROM job_applications 
                WHERE created_at >= :week_ago
            """
                ),
                {"week_ago": week_ago},
            )
            applications_week_row = applications_week_result.fetchone()
            applications_week = applications_week_row[0] if applications_week_row else 0

            # Get success rate (successful applications / total applications)
            success_rate_result = session.execute(
                text(
                    """
                SELECT 
                    COUNT(CASE WHEN application_status = 'sent' THEN 1 END) as successful,
                    COUNT(*) as total
                FROM job_applications
                WHERE created_at >= :week_ago
            """
                ),
                {"week_ago": week_ago},
            )
            success_data = success_rate_result.fetchone()

            if success_data and success_data[1] > 0:
                success_rate = f"{(success_data[0] / success_data[1] * 100):.1f}%"
            else:
                success_rate = "0%"

            # Get total jobs tracked
            total_jobs_result = session.execute(text("SELECT COUNT(*) FROM jobs"))
            total_jobs_row = total_jobs_result.fetchone()
            total_jobs = total_jobs_row[0] if total_jobs_row else 0

            # Get average response time (placeholder for now)
            avg_response_time = "1.2s"  # This would be calculated from actual processing times

            # Check for high volume notification
            notification = None
            if scrapes_month >= 3000:
                notification = {
                    "type": "warning",
                    "title": "High Volume Alert",
                    "message": f"You've scraped {scrapes_month} jobs this month. Consider switching to memo23/apify-indeed for enhanced company intelligence at better value.",
                    "action": "View Upgrade Options",
                }

            return jsonify(
                {
                    "scrapes_24h": scrapes_24h,
                    "scrapes_week": scrapes_week,
                    "scrapes_month": scrapes_month,
                    "applications_24h": applications_24h,
                    "applications_week": applications_week,
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "total_jobs": total_jobs,
                    "last_updated": now.isoformat(),
                    "notification": notification,
                }
            )

    except Exception as e:
        logging.error(f"Error getting dashboard stats: {e}")
        return jsonify({"error": "Failed to load dashboard statistics"}), 500


@dashboard_api.route("/api/dashboard/applications", methods=["GET"])
@require_dashboard_auth
def get_recent_applications():
    """
    Get recent job applications with document links
    """
    try:
        db_client = get_database_client()  # Lazy initialization
        limit = request.args.get("limit", 20, type=int)

        with db_client.get_session() as session:
            # Get recent applications with job and company information
            applications_result = session.execute(
                text(
                    """
                SELECT 
                    ja.id,
                    ja.created_at,
                    ja.application_status,
                    ja.documents_sent,
                    j.job_title,
                    c.name as company_name,
                    ja.email_sent_to,
                    ja.tone_coherence_score
                FROM job_applications ja
                LEFT JOIN jobs j ON ja.job_id = j.id
                LEFT JOIN companies c ON j.company_id = c.id
                ORDER BY ja.created_at DESC
                LIMIT :limit
            """
                ),
                {"limit": limit},
            )

            applications = []
            for row in applications_result:
                app = {
                    "id": row[0],
                    "created_at": row[1].isoformat() if row[1] else None,
                    "status": row[2] or "pending",  # application_status
                    "documents_sent": row[3] if row[3] else [],  # documents_sent array
                    "job_title": row[4],
                    "company_name": row[5],
                    "email_sent_to": row[6] if row[6] else None,  # email_sent_to
                    "coherence_score": float(row[7]) if row[7] else None,  # tone_coherence_score
                }
                applications.append(app)

            return jsonify(applications)

    except Exception as e:
        logging.error(f"Error getting recent applications: {e}")
        return jsonify({"error": "Failed to load recent applications"}), 500


@dashboard_api.route("/api/dashboard/application/<application_id>", methods=["GET"])
@require_dashboard_auth
def get_application_details(application_id):
    """
    Get detailed information about a specific application
    """
    try:
        db_client = get_database_client()  # Lazy initialization
        with db_client.get_session() as session:
            # Get application details
            app_result = session.execute(
                text(
                    """
                SELECT 
                    ja.*,
                    j.title as job_title,
                    j.description as job_description,
                    j.salary_low,
                    j.salary_high,
                    j.salary_currency,
                    c.name as company_name,
                    c.website as company_website
                FROM job_applications ja
                LEFT JOIN jobs j ON ja.job_id = j.id
                LEFT JOIN companies c ON j.company_id = c.id
                WHERE ja.id = :application_id
            """
                ),
                {"application_id": application_id},
            )

            app = app_result.fetchone()
            if not app:
                return jsonify({"error": "Application not found"}), 404

            # Get tracking links for this application
            links_result = session.execute(
                text(
                    """
                SELECT link_type, original_url, tracking_url, click_count
                FROM link_tracking
                WHERE application_id = :application_id
            """
                ),
                {"application_id": application_id},
            )

            tracking_links = []
            for link_row in links_result:
                tracking_links.append(
                    {
                        "type": link_row[0],
                        "original_url": link_row[1],
                        "tracking_url": link_row[2],
                        "click_count": link_row[3],
                    }
                )

            application_details = {
                "id": app[0],
                "job_id": app[1],
                "created_at": app[2].isoformat() if app[2] else None,
                "status": app[3],
                "resume_url": app[4],
                "cover_letter_url": app[5],
                "email_sent_at": app[6].isoformat() if app[6] else None,
                "coherence_score": float(app[7]) if app[7] else None,
                "job_title": app[8],
                "job_description": app[9],
                "salary_range": (
                    format_salary_range(app[10], app[11], app[12] or "CAD") if app[10] and app[11] else None
                ),
                "company_name": app[13],
                "company_website": app[14],
                "tracking_links": tracking_links,
            }

            return jsonify(application_details)

    except Exception as e:
        logging.error(f"Error getting application details: {e}")
        return jsonify({"error": "Failed to load application details"}), 500


@dashboard_api.route("/api/dashboard/system-status", methods=["GET"])
@require_dashboard_auth
def get_system_status():
    """
    Get system status information
    """
    try:
        db_client = get_database_client()  # Lazy initialization
        # Test database connection
        db_status = "connected"
        storage_status = "available"

        try:
            with db_client.get_session() as session:
                session.execute(text("SELECT 1"))
        except Exception as e:
            db_status = "error"
            logging.error(f"Database connection test failed: {e}")

        # Test storage availability (placeholder)
        try:
            # This would test actual storage connectivity
            storage_status = "available"
        except Exception as e:
            storage_status = "error"
            logging.error(f"Storage connectivity test failed: {e}")

        return jsonify(
            {
                "database_status": db_status,
                "storage_status": storage_status,
                "last_check": datetime.utcnow().isoformat(),
                "uptime": "System operational",  # This would be calculated from actual uptime
            }
        )

    except Exception as e:
        logging.error(f"Error getting system status: {e}")
        return jsonify({"error": "Failed to get system status"}), 500


@dashboard_api.route("/api/dashboard/jobs/recent", methods=["GET"])
@require_dashboard_auth
def get_recent_jobs():
    """
    Get recently scraped jobs
    """
    try:
        db_client = get_database_client()  # Lazy initialization
        limit = request.args.get("limit", 10, type=int)

        with db_client.get_session() as session:
            jobs_result = session.execute(
                text(
                    """
                SELECT 
                    j.id,
                    j.job_title,
                    j.created_at,
                    j.priority_score,
                    j.eligibility_flag,
                    c.name as company_name,
                    j.location,
                    j.salary_low,
                    j.salary_high
                FROM jobs j
                LEFT JOIN companies c ON j.company_id = c.id
                ORDER BY j.created_at DESC
                LIMIT :limit
            """
                ),
                {"limit": limit},
            )

            jobs = []
            for row in jobs_result:
                job = {
                    "id": row[0],
                    "title": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                    "relevance_score": float(row[3]) if row[3] else None,
                    "is_eligible": row[4],
                    "company_name": row[5],
                    "location": row[6],
                    "salary_range": f"${row[7]:,} - ${row[8]:,}" if row[7] and row[8] else None,
                }
                jobs.append(job)

            return jsonify(jobs)

    except Exception as e:
        logging.error(f"Error getting recent jobs: {e}")
        return jsonify({"error": "Failed to load recent jobs"}), 500
