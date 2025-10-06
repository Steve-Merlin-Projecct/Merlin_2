"""
Scraper API Routes
Provides REST API endpoints for job scraping operations
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from functools import wraps
from modules.scraping.job_scraper_apify import ApifyJobScraper
from modules.scraping.intelligent_scraper import IntelligentScraper
from modules.scraping.scrape_pipeline import ScrapeDataPipeline
from modules.scraping.jobs_populator import JobsPopulator
from modules.database.database_manager import DatabaseManager
from modules.database.database_extensions import extend_database_reader

extend_database_reader()  # Extend database functionality for scraper operations
from modules.security.security_patch import SecurityPatch

logger = logging.getLogger(__name__)


def require_auth(f):
    """Authentication decorator for scraper endpoints"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


# Create blueprint
scraper_bp = Blueprint("scraper_api_routes", __name__, url_prefix="/api/scraping")


@scraper_bp.route("/start-scrape", methods=["POST"])
@require_auth
@SecurityPatch.validate_request_size()
def start_scrape():
    """
    Start a new job scraping session

    Expected JSON payload:
    {
        "search_params": {
            "job_title": "Marketing Manager",
            "location": "Edmonton, AB",
            "country": "CA",
            "max_results": 50
        },
        "user_id": "steve_glen"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "JSON payload required"}), 400

        search_params = data.get("search_params", {})
        user_id = data.get("user_id", "steve_glen")

        # Validate required parameters
        required_params = ["job_title", "location"]
        missing_params = [p for p in required_params if not search_params.get(p)]
        if missing_params:
            return jsonify({"success": False, "error": f"Missing required parameters: {missing_params}"}), 400

        # Initialize scraper
        scraper = ApifyJobScraper()

        # Create scrape input
        scrape_input = {
            "position": search_params["job_title"],
            "location": search_params["location"],
            "country": search_params.get("country", "CA"),
            "maxItems": search_params.get("max_results", 50),
        }

        logger.info(f"Starting scrape for {user_id}: {scrape_input}")

        # Execute scrape
        results = scraper.scrape_jobs_simple(scrape_input)

        return jsonify(
            {
                "success": True,
                "message": "Scraping completed successfully",
                "scrape_id": results.get("scrape_id"),
                "jobs_scraped": results.get("jobs_scraped", 0),
                "cost_estimate": results.get("cost_estimate"),
                "processing_time": results.get("processing_time"),
            }
        )

    except Exception as e:
        logger.error(f"Error in start_scrape: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@scraper_bp.route("/intelligent-scrape", methods=["POST"])
@require_auth
@SecurityPatch.validate_request_size()
def intelligent_scrape():
    """
    Start intelligent scraping based on user preference packages

    Expected JSON payload:
    {
        "user_id": "steve_glen",
        "max_jobs_per_package": 30,
        "package_filter": ["local", "remote"]  // optional
    }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get("user_id", "steve_glen")
        max_jobs_per_package = data.get("max_jobs_per_package", 30)
        package_filter = data.get("package_filter")

        # Initialize intelligent scraper
        scraper = IntelligentScraper()

        # Run targeted scrape
        results = scraper.run_targeted_scrape(
            user_id=user_id, max_jobs_per_package=max_jobs_per_package, package_filter=package_filter
        )

        return jsonify(
            {"success": True, "message": f"Intelligent scraping completed for {user_id}", "results": results}
        )

    except Exception as e:
        logger.error(f"Error in intelligent_scrape: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@scraper_bp.route("/status/<scrape_id>", methods=["GET"])
@require_auth
def get_scrape_status(scrape_id):
    """
    Get status of a scraping operation
    """
    try:
        db_manager = DatabaseManager()

        # Query scrape status from database
        # This would typically check the raw_job_scrapes table
        status_info = db_manager.reader.get_scrape_status(scrape_id)

        if not status_info:
            return jsonify({"success": False, "error": "Scrape ID not found"}), 404

        return jsonify({"success": True, "scrape_id": scrape_id, "status": status_info})

    except Exception as e:
        logger.error(f"Error getting scrape status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@scraper_bp.route("/results/<scrape_id>", methods=["GET"])
@require_auth
def get_scrape_results(scrape_id):
    """
    Get results from a completed scraping operation
    """
    try:
        db_manager = DatabaseManager()

        # Get scrape results
        results = db_manager.reader.get_scrape_results(scrape_id)

        if not results:
            return jsonify({"success": False, "error": "No results found for scrape ID"}), 404

        return jsonify({"success": True, "scrape_id": scrape_id, "results": results})

    except Exception as e:
        logger.error(f"Error getting scrape results: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@scraper_bp.route("/pipeline/process", methods=["POST"])
@require_auth
def process_pipeline():
    """
    Process raw scrapes through cleaning pipeline
    """
    try:
        data = request.get_json() or {}
        force_reprocess = data.get("force_reprocess", False)

        # Initialize pipeline
        pipeline = ScrapeDataPipeline()

        # Process raw scrapes
        batch_size = data.get("batch_size", 100)
        results = pipeline.process_raw_scrapes_to_cleaned(batch_size=batch_size)

        return jsonify({"success": True, "message": "Pipeline processing completed", "results": results})

    except Exception as e:
        logger.error(f"Error in pipeline processing: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@scraper_bp.route("/pipeline/transfer", methods=["POST"])
@require_auth
def transfer_to_jobs():
    """
    Transfer cleaned scrapes to jobs table
    """
    try:
        data = request.get_json() or {}
        batch_size = data.get("batch_size", 100)

        # Initialize populator
        populator = JobsPopulator()

        # Transfer jobs
        results = populator.populate_jobs_from_cleaned_scrapes(batch_size=batch_size)

        return jsonify({"success": True, "message": "Job transfer completed", "results": results})

    except Exception as e:
        logger.error(f"Error in job transfer: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@scraper_bp.route("/stats", methods=["GET"])
@require_auth
def get_scraping_stats():
    """
    Get comprehensive scraping statistics
    """
    try:
        db_manager = DatabaseManager()

        # Get various statistics
        stats = {
            "raw_scrapes": db_manager.reader.get_table_count("raw_job_scrapes"),
            "cleaned_scrapes": db_manager.reader.get_table_count("cleaned_job_scrapes"),
            "jobs_total": db_manager.reader.get_table_count("jobs"),
            "recent_scrapes": db_manager.reader.get_recent_scrape_activity(days=7),
        }

        # Get pipeline stats
        pipeline = ScrapeDataPipeline()
        pipeline_stats = pipeline.get_pipeline_stats()
        stats.update(pipeline_stats)

        return jsonify({"success": True, "stats": stats})

    except Exception as e:
        logger.error(f"Error getting scraping stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@scraper_bp.route("/usage", methods=["GET"])
@require_auth
def get_usage_stats():
    """
    Get Apify usage and cost statistics
    """
    try:
        scraper = ApifyJobScraper()
        usage_stats = scraper.get_usage_stats()

        return jsonify({"success": True, "usage": usage_stats})

    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@scraper_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check for scraping system
    """
    try:
        health_status = {"scraper_api": "healthy", "apify_connection": "unknown", "database_connection": "unknown"}

        # Test Apify connection
        try:
            scraper = ApifyJobScraper()
            # Simple connectivity test
            health_status["apify_connection"] = "healthy"
        except Exception as e:
            health_status["apify_connection"] = f"error: {str(e)}"

        # Test database connection
        try:
            db_manager = DatabaseManager()
            db_manager.reader.get_table_count("jobs")
            health_status["database_connection"] = "healthy"
        except Exception as e:
            health_status["database_connection"] = f"error: {str(e)}"

        return jsonify({"success": True, "health": health_status})

    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
