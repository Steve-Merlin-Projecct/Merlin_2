"""
AI Integration Routes for Job Analysis
Provides endpoints for Gemini-based job analysis with centralized rate limiting
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from modules.ai_job_description_analysis.ai_analyzer import JobAnalysisManager
from modules.database.database_manager import DatabaseManager
from modules.security.security_patch import SecurityPatch, apply_security_headers
from modules.security.rate_limit_manager import rate_limit_expensive
from functools import wraps

logger = logging.getLogger(__name__)


def require_auth(f):
    """Authentication decorator for AI endpoints"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


# Create blueprint
ai_bp = Blueprint("ai_integration", __name__, url_prefix="/api/ai")


@ai_bp.route("/analyze-jobs", methods=["POST"])
@require_auth
@rate_limit_expensive  # Centralized rate limiting: 10/min;50/hour;200/day
@SecurityPatch.validate_request_size()
def analyze_jobs():
    """
    Trigger AI analysis of pending jobs
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400

        data = request.get_json()
        batch_size = data.get("batch_size", 10)

        # Validate batch size
        if not isinstance(batch_size, int) or batch_size < 1 or batch_size > 50:
            return jsonify({"status": "error", "message": "Batch size must be between 1 and 50"}), 400

        # Initialize analysis manager
        db_manager = DatabaseManager()
        analysis_manager = JobAnalysisManager(db_manager)

        # Run analysis
        logger.info(f"Starting AI analysis for batch size: {batch_size}")
        result = analysis_manager.analyze_pending_jobs(batch_size)

        # Log sanitized result
        sanitized_result = SecurityPatch.sanitize_log_data(result)
        logger.info(f"AI analysis completed: {sanitized_result}")

        return jsonify(result)

    except Exception as e:
        error_msg = f"AI analysis failed: {str(e)}"
        logger.error(error_msg)

        return jsonify({"status": "error", "message": "Analysis service temporarily unavailable"}), 500


@ai_bp.route("/usage-stats", methods=["GET"])
@require_auth
@rate_limit_expensive  # Centralized rate limiting
def get_usage_stats():
    """
    Get AI usage statistics
    """
    try:
        db_manager = DatabaseManager()
        analysis_manager = JobAnalysisManager(db_manager)

        usage_stats = analysis_manager.analyzer.get_usage_stats()

        return jsonify({"status": "success", "usage_stats": usage_stats})

    except Exception as e:
        logger.error(f"Failed to get usage stats: {str(e)}")
        return jsonify({"status": "error", "message": "Could not retrieve usage statistics"}), 500


@ai_bp.route("/analysis-results/<job_id>", methods=["GET"])
@require_auth
@rate_limit_expensive  # Centralized rate limiting
def get_analysis_results(job_id):
    """
    Get analysis results for a specific job
    """
    try:
        # Validate job ID
        if not job_id or len(job_id) > 100:
            return jsonify({"status": "error", "message": "Invalid job ID"}), 400

        db_manager = DatabaseManager()

        # Get analysis results
        query = """
        SELECT job_id, skills_analysis, authenticity_check, 
               industry_classification, additional_insights,
               analysis_timestamp, model_used, analysis_version
        FROM job_content_analysis 
        WHERE job_id = %s
        """

        result = db_manager.execute_query(query, (job_id,))

        if not result:
            return jsonify({"status": "error", "message": "Analysis not found for this job"}), 404

        analysis_data = dict(result[0])

        return jsonify({"status": "success", "analysis": analysis_data})

    except Exception as e:
        logger.error(f"Failed to get analysis results: {str(e)}")
        return jsonify({"status": "error", "message": "Could not retrieve analysis results"}), 500


@ai_bp.route("/batch-status", methods=["GET"])
@require_auth
@rate_limit_expensive  # Centralized rate limiting
def get_batch_status():
    """
    Get status of pending AI analysis jobs
    """
    try:
        db_manager = DatabaseManager()

        # Count analyzed vs unanalyzed jobs
        status_query = """
        SELECT 
            COUNT(CASE WHEN a.job_id IS NOT NULL THEN 1 END) as analyzed_count,
            COUNT(CASE WHEN a.job_id IS NULL THEN 1 END) as pending_count,
            MAX(a.analysis_timestamp) as last_analysis
        FROM cleaned_job_scrapes j
        LEFT JOIN job_content_analysis a ON j.job_id = a.job_id
        WHERE j.description IS NOT NULL 
        AND LENGTH(j.description) > 50
        """

        result = db_manager.execute_query(status_query)

        if result:
            status_data = dict(result[0])

            return jsonify(
                {
                    "status": "success",
                    "batch_status": {
                        "analyzed_jobs": status_data.get("analyzed_count", 0),
                        "pending_jobs": status_data.get("pending_count", 0),
                        "last_analysis": status_data.get("last_analysis"),
                        "ready_for_analysis": status_data.get("pending_count", 0) > 0,
                    },
                }
            )
        else:
            return jsonify(
                {
                    "status": "success",
                    "batch_status": {
                        "analyzed_jobs": 0,
                        "pending_jobs": 0,
                        "last_analysis": None,
                        "ready_for_analysis": False,
                    },
                }
            )

    except Exception as e:
        logger.error(f"Failed to get batch status: {str(e)}")
        return jsonify({"status": "error", "message": "Could not retrieve batch status"}), 500


@ai_bp.route("/reset-usage", methods=["POST"])
@require_auth
@rate_limit_expensive  # Centralized rate limiting
def reset_daily_usage():
    """
    Reset daily AI usage counter (admin function)
    """
    try:
        # This should be protected with admin authentication in production

        db_manager = DatabaseManager()
        analysis_manager = JobAnalysisManager(db_manager)

        analysis_manager.analyzer.reset_daily_usage()

        logger.info("Daily AI usage counter reset")

        return jsonify({"status": "success", "message": "Daily usage counter reset"})

    except Exception as e:
        logger.error(f"Failed to reset usage: {str(e)}")
        return jsonify({"status": "error", "message": "Could not reset usage counter"}), 500


@ai_bp.route("/health", methods=["GET"])
@require_auth
@rate_limit_expensive
def ai_health_check():
    """
    Health check for AI integration services
    """
    try:
        db_manager = DatabaseManager()
        analysis_manager = JobAnalysisManager(db_manager)

        # Check if Gemini API key is configured
        gemini_configured = hasattr(analysis_manager.analyzer, "api_key") and analysis_manager.analyzer.api_key

        # Get current usage stats
        usage_stats = analysis_manager.analyzer.get_usage_stats()

        # Calculate health status
        usage_percentage = usage_stats.get("usage_percentage", 0)
        health_status = "healthy"

        if usage_percentage > 90:
            health_status = "critical"
        elif usage_percentage > 80:
            health_status = "warning"

        return jsonify(
            {
                "status": "success",
                "ai_health": {
                    "service_status": health_status,
                    "gemini_configured": gemini_configured,
                    "daily_usage_percentage": usage_percentage,
                    "estimated_daily_cost": usage_stats.get("estimated_cost", 0),
                    "remaining_capacity": usage_stats.get("remaining_capacity", 0),
                },
            }
        )

    except Exception as e:
        logger.error(f"AI health check failed: {str(e)}")
        return jsonify({"status": "error", "message": "AI service health check failed"}), 500


@ai_bp.route("/gemini-usage", methods=["GET"])
@require_auth
@rate_limit_expensive
def get_gemini_usage():
    """Get comprehensive Gemini usage statistics with model tracking"""
    try:
        from modules.ai_analyzer import GeminiJobAnalyzer

        # Get real-time usage from analyzer
        analyzer = GeminiJobAnalyzer()
        usage_stats = analyzer._get_usage_summary()

        db_manager = DatabaseManager()

        # Get historical analysis data
        today = datetime.now().date()
        current_month = today.replace(day=1)

        # Daily analysis stats
        daily_query = """
        SELECT 
            COUNT(*) as analyses_today,
            SUM(CASE WHEN skills_analysis IS NOT NULL THEN 1 ELSE 0 END) as successful_analyses,
            STRING_AGG(DISTINCT model_used, ', ') as models_used_today
        FROM job_content_analysis 
        WHERE DATE(analysis_timestamp) = %s
        """

        daily_results = db_manager.client.execute_query(daily_query, (today,))
        daily_stats = (
            dict(daily_results[0])
            if daily_results
            else {"analyses_today": 0, "successful_analyses": 0, "models_used_today": ""}
        )

        # Monthly model usage breakdown
        monthly_model_query = """
        SELECT 
            model_used,
            COUNT(*) as usage_count,
            ROUND(AVG(CASE WHEN authenticity_check->>'confidence_score' IS NOT NULL 
                THEN CAST(authenticity_check->>'confidence_score' AS NUMERIC) 
                ELSE NULL END), 1) as avg_confidence_score
        FROM job_content_analysis 
        WHERE analysis_timestamp >= %s AND model_used IS NOT NULL
        GROUP BY model_used
        ORDER BY usage_count DESC
        """

        model_results = db_manager.client.execute_query(monthly_model_query, (current_month,))
        model_breakdown = [dict(row) for row in model_results] if model_results else []

        # Calculate cost savings if using lite model
        potential_savings = 0
        if usage_stats["monthly_tokens_used"] > 0:
            flash_cost = (usage_stats["monthly_tokens_used"] / 1000) * 0.00075
            lite_cost = (usage_stats["monthly_tokens_used"] / 1000) * 0.0003
            potential_savings = flash_cost - lite_cost

        # Usage recommendations
        recommendations = []
        if usage_stats["usage_percentage"] > 90:
            recommendations.append("⚠️ Approaching daily token limit - consider switching to Gemini 2.0 Flash Lite")
        elif usage_stats["usage_percentage"] > 75:
            recommendations.append("💡 High token usage detected - monitor for automatic model switching")

        if usage_stats["model_switches"] > 0:
            recommendations.append(
                f"🔄 Model switched {usage_stats['model_switches']} time(s) today to conserve tokens"
            )

        if potential_savings > 0.10:
            recommendations.append(
                f"💰 Potential monthly savings of ${potential_savings:.2f} using Gemini 2.0 Flash Lite"
            )

        if not recommendations:
            recommendations.append("✅ Usage within optimal range")

        return jsonify(
            {
                "status": "success",
                "real_time_usage": {
                    "daily_tokens_used": usage_stats["daily_tokens_used"],
                    "daily_token_limit": usage_stats["daily_token_limit"],
                    "monthly_tokens_used": usage_stats["monthly_tokens_used"],
                    "monthly_token_limit": usage_stats["monthly_token_limit"],
                    "daily_cost": round(usage_stats["daily_cost"], 4),
                    "monthly_cost": round(usage_stats["monthly_cost"], 4),
                    "requests_today": usage_stats["requests_today"],
                    "current_model": usage_stats["current_model"],
                    "model_switches_today": usage_stats["model_switches"],
                    "usage_percentage": round(usage_stats["usage_percentage"], 1),
                },
                "today_analysis_stats": {
                    "total_analyses": daily_stats["analyses_today"],
                    "successful_analyses": daily_stats["successful_analyses"],
                    "success_rate": round(
                        (daily_stats["successful_analyses"] / max(daily_stats["analyses_today"], 1)) * 100, 1
                    ),
                    "models_active": daily_stats["models_used_today"] or "None",
                },
                "model_breakdown": model_breakdown,
                "cost_comparison": {
                    "gemini_2_0_flash_rate": 0.00075,
                    "gemini_2_0_flash_lite_rate": 0.0003,
                    "current_rate": analyzer.cost_per_1k_tokens,
                    "potential_monthly_savings": round(potential_savings, 4),
                },
                "recommendations": recommendations,
                "projection": {
                    "monthly_cost_projection": round(
                        usage_stats["monthly_cost"] * (30 / max(datetime.now().day, 1)), 2
                    ),
                    "daily_tokens_remaining": max(
                        0, usage_stats["daily_token_limit"] - usage_stats["daily_tokens_used"]
                    ),
                    "switch_threshold": round(usage_stats["daily_token_limit"] * 0.75),
                    "should_monitor": usage_stats["usage_percentage"] > 50,
                },
            }
        )

    except Exception as e:
        logger.error(f"Failed to get Gemini usage stats: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/api/ai/set-model", methods=["POST"])
@require_auth
def set_gemini_model():
    """Set the Gemini model for next batch processing"""
    try:
        data = request.get_json()
        model = data.get("model")

        if not model:
            return jsonify({"error": "Model parameter required"}), 400

        # Validate model
        valid_models = ["gemini-2.5-flash", "gemini-2.5-flash-8b", "gemini-2.0-flash-exp", "gemini-2.0-flash-8b"]

        if model not in valid_models:
            return jsonify({"error": "Invalid model specified"}), 400

        # Save to database settings
        db_manager = DatabaseManager()
        db_manager.writer.create_or_update_setting(
            setting_key="gemini_model",
            setting_value=model,
            setting_type="ai_config",
            description="Selected Gemini model for batch processing",
        )

        return jsonify({"success": True, "model": model, "message": f"Model updated to {model}"})

    except Exception as e:
        logging.error(f"Failed to set Gemini model: {e}")
        return jsonify({"error": "Failed to update model"}), 500


@ai_bp.route("/api/dashboard/stats", methods=["GET"])
@require_auth
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        db_manager = DatabaseManager()

        # Get scraping stats (24h and week)
        stats = {"scrapes_24h": 0, "scrapes_week": 0, "applications_24h": 0, "applications_week": 0}

        # Query database for actual stats
        try:
            # Raw scrapes in last 24 hours
            result_24h = db_manager.client.execute_raw_sql(
                "SELECT COUNT(*) FROM raw_job_scrapes WHERE scraped_at >= NOW() - INTERVAL '24 hours'"
            )
            if result_24h and len(result_24h) > 0:
                stats["scrapes_24h"] = result_24h[0][0]

            # Raw scrapes in last week
            result_week = db_manager.client.execute_raw_sql(
                "SELECT COUNT(*) FROM raw_job_scrapes WHERE scraped_at >= NOW() - INTERVAL '7 days'"
            )
            if result_week and len(result_week) > 0:
                stats["scrapes_week"] = result_week[0][0]

            # Applications in last 24 hours
            app_24h = db_manager.client.execute_raw_sql(
                "SELECT COUNT(*) FROM document_jobs WHERE created_at >= NOW() - INTERVAL '24 hours'"
            )
            if app_24h and len(app_24h) > 0:
                stats["applications_24h"] = app_24h[0][0]

            # Applications in last week
            app_week = db_manager.client.execute_raw_sql(
                "SELECT COUNT(*) FROM document_jobs WHERE created_at >= NOW() - INTERVAL '7 days'"
            )
            if app_week and len(app_week) > 0:
                stats["applications_week"] = app_week[0][0]

        except Exception as e:
            logging.error(f"Database query error in dashboard stats: {e}")
            # Return zeros if database queries fail

        return jsonify(stats)

    except Exception as e:
        logging.error(f"Failed to get dashboard stats: {e}")
        return jsonify({"error": "Failed to load dashboard stats"}), 500


@ai_bp.route("/api/dashboard/recent-applications", methods=["GET"])
@require_auth
def recent_applications():
    """Get recent job applications"""
    try:
        db_manager = DatabaseManager()

        # Get recent applications with job details
        result = db_manager.client.execute_raw_sql(
            """
            SELECT 
                dj.title as position,
                dj.author as company,
                'Remote/Hybrid' as location,
                dj.created_at::date as applied_date,
                CASE 
                    WHEN dj.has_error THEN 'Failed'
                    WHEN dj.status = 'completed' THEN 'Submitted'
                    ELSE 'Processing'
                END as status,
                dj.file_path as documents
            FROM document_jobs dj
            ORDER BY dj.created_at DESC
            LIMIT 10
        """
        )

        applications = []
        if result:
            for row in result:
                applications.append(
                    {
                        "position": row[0] or "Marketing Manager",
                        "company": row[1] or "Various Companies",
                        "location": row[2] or "Edmonton, AB",
                        "applied_date": str(row[3]) if row[3] else "N/A",
                        "status": row[4] or "Unknown",
                        "documents": row[5] if row[5] else None,
                    }
                )

        return jsonify({"applications": applications})

    except Exception as e:
        logging.error(f"Failed to get recent applications: {e}")
        return jsonify({"error": "Failed to load recent applications"}), 500


# Apply security headers to all AI blueprint responses
@ai_bp.after_request
def add_ai_security_headers(response):
    return apply_security_headers(response)
