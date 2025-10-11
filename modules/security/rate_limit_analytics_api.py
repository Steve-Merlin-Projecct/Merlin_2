"""
Rate Limiting Analytics API

Provides REST endpoints for rate limiting metrics, analytics,
cache analysis, and monitoring data.

Version: 1.0.0
Created: 2025-10-11
"""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from functools import wraps

from modules.security.rate_limit_manager import limiter, get_rate_limit_status
from modules.security import rate_limit_monitor as monitor
from modules.security import rate_limit_config as config

logger = logging.getLogger(__name__)

# Create blueprint
rate_limit_analytics_bp = Blueprint(
    "rate_limit_analytics",
    __name__,
    url_prefix="/api/rate-limit"
)


# ============================================================================
# AUTHENTICATION
# ============================================================================


def require_auth(f):
    """Require authentication for analytics endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({
                "error": "Authentication required",
                "message": "You must be logged in to access rate limiting analytics"
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================


@rate_limit_analytics_bp.route("/metrics", methods=["GET"])
@require_auth
def get_metrics():
    """
    Get current rate limiting metrics including memory usage,
    active keys, cleanup stats, and health status.

    Returns:
        JSON response with comprehensive metrics
    """
    try:
        if not limiter or not limiter.storage:
            return jsonify({
                "error": "Rate limiter not initialized"
            }), 500

        metrics = monitor.get_metrics(limiter.storage, limiter)

        return jsonify({
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@rate_limit_analytics_bp.route("/metrics/summary", methods=["GET"])
@require_auth
def get_metrics_summary():
    """
    Get human-readable metrics summary.

    Returns:
        Plain text summary of key metrics
    """
    try:
        if not limiter or not limiter.storage:
            return "Rate limiter not initialized", 500

        summary = monitor.get_metrics_summary(limiter.storage, limiter)

        return summary, 200, {"Content-Type": "text/plain"}

    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        return f"Error: {str(e)}", 500


@rate_limit_analytics_bp.route("/status", methods=["GET"])
@require_auth
def get_status():
    """
    Get rate limit status for current user/IP.

    Returns:
        JSON with rate limit key and status information
    """
    try:
        status = get_rate_limit_status()

        return jsonify({
            "status": "success",
            "rate_limit_status": status,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to get rate limit status: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================


@rate_limit_analytics_bp.route("/analytics", methods=["GET"])
@require_auth
def get_analytics():
    """
    Get rate limit violation analytics for specified time period.

    Query Parameters:
        - start_date: Start date (ISO format, default: 7 days ago)
        - end_date: End date (ISO format, default: now)
        - endpoint: Filter by specific endpoint (optional)
        - group_by: Group results by endpoint, ip, or user (default: endpoint)

    Returns:
        JSON with violation analytics
    """
    try:
        from modules.database.database_manager import DatabaseManager

        # Parse query parameters
        end_date = request.args.get("end_date", datetime.now().isoformat())
        start_date = request.args.get(
            "start_date",
            (datetime.now() - timedelta(days=7)).isoformat()
        )
        endpoint_filter = request.args.get("endpoint")
        group_by = request.args.get("group_by", "endpoint")

        # Build query
        db = DatabaseManager()

        if group_by == "endpoint":
            query = """
                SELECT
                    endpoint,
                    COUNT(*) as violation_count,
                    COUNT(DISTINCT client_ip) as unique_ips,
                    MIN(timestamp) as first_violation,
                    MAX(timestamp) as last_violation
                FROM rate_limit_analytics
                WHERE timestamp BETWEEN %s AND %s
            """
            params = [start_date, end_date]

            if endpoint_filter:
                query += " AND endpoint = %s"
                params.append(endpoint_filter)

            query += " GROUP BY endpoint ORDER BY violation_count DESC"

        elif group_by == "ip":
            query = """
                SELECT
                    client_ip,
                    COUNT(*) as violation_count,
                    COUNT(DISTINCT endpoint) as endpoints_hit,
                    MIN(timestamp) as first_violation,
                    MAX(timestamp) as last_violation
                FROM rate_limit_analytics
                WHERE timestamp BETWEEN %s AND %s
            """
            params = [start_date, end_date]

            if endpoint_filter:
                query += " AND endpoint = %s"
                params.append(endpoint_filter)

            query += " GROUP BY client_ip ORDER BY violation_count DESC LIMIT 20"

        else:
            return jsonify({
                "status": "error",
                "error": f"Invalid group_by parameter: {group_by}"
            }), 400

        results = db.execute_query(query, tuple(params))

        return jsonify({
            "status": "success",
            "analytics": {
                "period": {
                    "start": start_date,
                    "end": end_date
                },
                "group_by": group_by,
                "endpoint_filter": endpoint_filter,
                "results": results
            },
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# ============================================================================
# CACHE ANALYSIS ENDPOINTS
# ============================================================================


@rate_limit_analytics_bp.route("/cache-analysis", methods=["GET"])
@require_auth
def get_cache_analysis():
    """
    Get cache analysis showing database optimization opportunities.

    Query Parameters:
        - date: Analysis date (default: latest)
        - lookback_hours: Hours to analyze (default: 24)

    Returns:
        JSON with cache hit potential and recommendations
    """
    try:
        from modules.database.database_manager import DatabaseManager

        db = DatabaseManager()
        analysis_date = request.args.get("date")
        lookback_hours = int(request.args.get("lookback_hours", 24))

        if analysis_date:
            # Get specific date's analysis
            query = """
                SELECT *
                FROM cache_analysis_daily
                WHERE analysis_date = %s
            """
            results = db.execute_query(query, (analysis_date,))
        else:
            # Get latest analysis
            query = """
                SELECT *
                FROM v_latest_cache_analysis
            """
            results = db.execute_query(query)

        if results:
            analysis = results[0]
        else:
            # No stored analysis, calculate on-the-fly
            analysis = calculate_cache_potential(db, lookback_hours)

        return jsonify({
            "status": "success",
            "cache_analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to get cache analysis: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@rate_limit_analytics_bp.route("/cache-analysis/top-queries", methods=["GET"])
@require_auth
def get_top_cacheable_queries():
    """
    Get top cacheable queries (most frequently repeated).

    Query Parameters:
        - limit: Number of queries to return (default: 10)
        - min_count: Minimum execution count (default: 5)

    Returns:
        JSON with most cacheable queries
    """
    try:
        from modules.database.database_manager import DatabaseManager

        db = DatabaseManager()
        limit = int(request.args.get("limit", 10))
        min_count = int(request.args.get("min_count", 5))

        query = """
            SELECT *
            FROM v_top_cacheable_queries
            WHERE execution_count >= %s
            LIMIT %s
        """

        results = db.execute_query(query, (min_count, limit))

        return jsonify({
            "status": "success",
            "top_cacheable_queries": results,
            "criteria": {
                "limit": limit,
                "min_execution_count": min_count
            },
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to get top cacheable queries: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================


@rate_limit_analytics_bp.route("/config", methods=["GET"])
@require_auth
def get_configuration():
    """
    Get current rate limiting configuration.

    Returns:
        JSON with configuration summary
    """
    try:
        config_summary = config.get_configuration_summary()

        return jsonify({
            "status": "success",
            "configuration": config_summary,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def calculate_cache_potential(db, lookback_hours: int = 24) -> dict:
    """
    Calculate cache hit potential for specified lookback period.

    Args:
        db: DatabaseManager instance
        lookback_hours: Hours to analyze

    Returns:
        Dictionary with cache analysis results
    """
    query = "SELECT * FROM calculate_cache_hit_potential(%s)"
    results = db.execute_query(query, (lookback_hours,))

    if results:
        result = results[0]
        return {
            "total_queries": result.get("total_queries", 0),
            "unique_queries": result.get("unique_queries", 0),
            "duplicate_queries": result.get("duplicate_queries", 0),
            "cache_hit_potential_percent": result.get("cache_hit_potential_percent", 0),
            "lookback_hours": lookback_hours,
        }
    else:
        return {
            "total_queries": 0,
            "unique_queries": 0,
            "duplicate_queries": 0,
            "cache_hit_potential_percent": 0,
            "lookback_hours": lookback_hours,
        }
