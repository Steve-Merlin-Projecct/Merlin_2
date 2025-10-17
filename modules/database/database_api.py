import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from .lazy_instances import get_database_manager
from modules.security.rate_limit_manager import rate_limit_cheap, rate_limit_moderate

# Create Blueprint for database API endpoints
database_bp = Blueprint("database", __name__, url_prefix="/api/db")

# NOTE: Database manager is now lazy-initialized on demand
# No module-level instantiation to prevent import-time connections
logging.info("Database API blueprint created (lazy initialization)")


def validate_api_key():
    """Validate API key from request headers"""
    api_key = request.headers.get("X-API-Key")
    expected_key = os.environ.get("WEBHOOK_API_KEY")

    if not expected_key:
        logging.error("WEBHOOK_API_KEY not set in environment")
        return False

    if api_key != expected_key:
        logging.warning(f"Invalid API key provided for database access")
        return False

    return True


@database_bp.route("/jobs", methods=["GET"])
@rate_limit_cheap  # Database reads: 200/min
def get_jobs():
    """
    Get jobs with optional filtering
    Query parameters:
    - limit: Number of jobs to return (default: 20)
    - status: Filter by status
    - document_type: Filter by document type
    - search: Search term for title/author/filename
    """
    if not validate_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401

    try:
        db_manager = get_database_manager()  # Lazy initialization
        limit = int(request.args.get("limit", 20))
        status = request.args.get("status")
        document_type = request.args.get("document_type")
        search = request.args.get("search")

        if search:
            jobs = db_manager.search_jobs(search, limit)
        elif status:
            jobs = db_manager.get_jobs_by_status(status, limit)
        else:
            jobs = db_manager.get_recent_jobs(limit, document_type)

        return jsonify({"status": "success", "jobs": jobs, "count": len(jobs)})

    except Exception as e:
        logging.error(f"Error fetching jobs: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    """Get a specific job by ID"""
    if not validate_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401

    try:
        db_manager = get_database_manager()  # Lazy initialization
        job = db_manager.get_job_by_id(job_id)

        if job:
            return jsonify({"status": "success", "job": job})
        else:
            return jsonify({"error": "Job not found"}), 404

    except Exception as e:
        logging.error(f"Error fetching job {job_id}: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/statistics", methods=["GET"])
def get_statistics():
    """Get job statistics and system metrics"""
    if not validate_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401

    try:
        db_manager = get_database_manager()  # Lazy initialization
        stats = db_manager.get_job_statistics()

        return jsonify({"status": "success", "statistics": stats, "timestamp": datetime.utcnow().isoformat()})

    except Exception as e:
        logging.error(f"Error fetching statistics: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/jobs/<job_id>/logs", methods=["GET"])
def get_job_logs(job_id):
    """Get logs for a specific job"""
    if not validate_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401

    try:
        db_manager = get_database_manager()  # Lazy initialization
        limit = int(request.args.get("limit", 50))
        logs = db_manager.reader.get_job_logs(job_id, limit)

        return jsonify({"status": "success", "job_id": job_id, "logs": logs, "count": len(logs)})

    except Exception as e:
        logging.error(f"Error fetching logs for job {job_id}: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/settings", methods=["GET"])
def get_settings():
    """Get all application settings"""
    if not validate_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401

    try:
        db_manager = get_database_manager()  # Lazy initialization
        settings = db_manager.reader.get_all_settings()

        return jsonify({"status": "success", "settings": settings, "count": len(settings)})

    except Exception as e:
        logging.error(f"Error fetching settings: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/settings/<setting_key>", methods=["GET"])
def get_setting(setting_key):
    """Get a specific application setting"""
    if not validate_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401

    try:
        db_manager = get_database_manager()  # Lazy initialization
        setting = db_manager.get_application_setting(setting_key)

        if setting:
            return jsonify({"status": "success", "setting": setting})
        else:
            return jsonify({"error": "Setting not found"}), 404

    except Exception as e:
        logging.error(f"Error fetching setting {setting_key}: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/settings/<setting_key>", methods=["POST"])
def set_setting(setting_key):
    """Set an application setting"""
    if not validate_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401

    try:
        db_manager = get_database_manager()  # Lazy initialization
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        setting_value = data.get("value")
        setting_type = data.get("type", "string")
        description = data.get("description")

        if setting_value is None:
            return jsonify({"error": "Setting value is required"}), 400

        success = db_manager.set_application_setting(setting_key, str(setting_value), setting_type, description)

        if success:
            return jsonify({"status": "success", "message": f"Setting {setting_key} updated successfully"})
        else:
            return jsonify({"error": "Failed to update setting"}), 500

    except Exception as e:
        logging.error(f"Error setting {setting_key}: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/jobs/summary/<author>", methods=["GET"])
def get_author_summary(author):
    """Get job summary for a specific author"""
    if not validate_api_key():
        return jsonify({"error": "Invalid or missing API key"}), 401

    try:
        db_manager = get_database_manager()  # Lazy initialization
        summary = db_manager.reader.get_jobs_summary_by_author(author)

        return jsonify({"status": "success", "summary": summary})

    except Exception as e:
        logging.error(f"Error fetching author summary for {author}: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/raw-scrapes", methods=["POST"])
def store_raw_scrape():
    """Store raw scrape data in raw_job_scrapes table"""
    try:
        # Note: This endpoint doesn't use db_manager directly
        # It uses ScrapeDataPipeline which creates its own database connections
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON payload required"}), 400

        # Import pipeline to use insert_raw_scrape method
        from modules.scraping.scrape_pipeline import ScrapeDataPipeline

        pipeline = ScrapeDataPipeline()

        # Extract required fields
        source_website = data.get("source_website", "unknown")
        source_url = data.get("source_url", "")
        raw_data = data.get("raw_data", {})

        # Extract optional metadata
        kwargs = {
            "scraper_used": data.get("scraper_used"),
            "scraper_run_id": data.get("scraper_run_id"),
            "user_agent": data.get("user_agent"),
            "ip_address": data.get("ip_address"),
            "response_time_ms": data.get("response_time_ms"),
        }

        # Store the raw scrape
        scrape_id = pipeline.insert_raw_scrape(source_website, source_url, raw_data, **kwargs)

        return jsonify({"status": "success", "scrape_id": scrape_id, "message": "Raw scrape stored successfully"})

    except Exception as e:
        logging.error(f"Error storing raw scrape: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/test", methods=["GET"])
def test_database():
    """Test database connectivity"""
    try:
        db_manager = get_database_manager()  # Lazy initialization
        connection_test = db_manager.client.test_connection()

        return jsonify(
            {
                "status": "success" if connection_test else "error",
                "database_connected": connection_test,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logging.error(f"Database test error: {e}")
        return jsonify({"error": str(e)}), 500


@database_bp.route("/health", methods=["GET"])
def database_health():
    """Database health check endpoint"""
    try:
        db_manager = get_database_manager()  # Lazy initialization
        connection_test = db_manager.client.test_connection()
        stats = db_manager.get_job_statistics()

        return jsonify(
            {
                "status": "healthy" if connection_test else "unhealthy",
                "database_connected": connection_test,
                "total_jobs": stats.get("total_jobs", 0),
                "success_rate": stats.get("success_rate", 0),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logging.error(f"Database health check error: {e}")
        return jsonify({"status": "unhealthy", "database_connected": False, "error": str(e)}), 500
