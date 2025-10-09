"""
Flask API Routes for Tiered Job Analysis
Provides REST endpoints for three-tier sequential batch processing

Endpoints:
- POST /api/analyze/tier1 - Run Tier 1 (Core) analysis
- POST /api/analyze/tier2 - Run Tier 2 (Enhanced) analysis
- POST /api/analyze/tier3 - Run Tier 3 (Strategic) analysis
- POST /api/analyze/sequential-batch - Run full sequential batch (all tiers)
- GET /api/analyze/status - Get processing pipeline status
- GET /api/analyze/tier-stats - Get tier completion statistics
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Optional
from modules.ai_job_description_analysis.sequential_batch_scheduler import (
    SequentialBatchScheduler,
    get_status
)

logger = logging.getLogger(__name__)

# Create Blueprint
tiered_analysis_bp = Blueprint('tiered_analysis', __name__, url_prefix='/api/analyze')


def validate_api_key():
    """Validate API key from request headers"""
    import os
    api_key = request.headers.get('X-API-Key')
    expected_key = os.getenv('WEBHOOK_API_KEY')

    if not expected_key:
        logger.warning("WEBHOOK_API_KEY not configured")
        return False

    return api_key == expected_key


def require_api_key(f):
    """Decorator to require API key authentication"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_api_key():
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Valid API key required'
            }), 401
        return f(*args, **kwargs)

    return decorated_function


@tiered_analysis_bp.route('/tier1', methods=['POST'])
@require_api_key
def run_tier1_analysis():
    """
    Run Tier 1 (Core Analysis) batch processing

    Request Body (optional):
    {
        "max_jobs": 100,  // Optional limit on jobs to process
        "model_override": "gemini-2.0-flash-lite-001"  // Optional model override
    }

    Response:
    {
        "tier": 1,
        "total_jobs": 50,
        "successful": 48,
        "failed": 2,
        "total_tokens": 85000,
        "avg_response_time_ms": 2100,
        "jobs_per_second": 0.8,
        "timestamp": "2025-10-09T02:30:00"
    }
    """
    try:
        data = request.get_json() or {}
        max_jobs = data.get('max_jobs')
        model_override = data.get('model_override')

        logger.info(f"Tier 1 analysis requested (max_jobs={max_jobs}, model={model_override})")

        # Initialize scheduler
        scheduler = SequentialBatchScheduler(tier1_model=model_override)

        # Run Tier 1 batch
        results = scheduler.run_tier1_batch(max_jobs=max_jobs)

        # Add timestamp
        results['timestamp'] = datetime.now().isoformat()

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Tier 1 analysis failed: {e}", exc_info=True)
        return jsonify({
            'error': 'Tier 1 analysis failed',
            'message': str(e),
            'tier': 1
        }), 500


@tiered_analysis_bp.route('/tier2', methods=['POST'])
@require_api_key
def run_tier2_analysis():
    """
    Run Tier 2 (Enhanced Analysis) batch processing

    Request Body (optional):
    {
        "max_jobs": 100,
        "model_override": "gemini-2.0-flash-001"
    }

    Response: Same format as tier1
    """
    try:
        data = request.get_json() or {}
        max_jobs = data.get('max_jobs')
        model_override = data.get('model_override')

        logger.info(f"Tier 2 analysis requested (max_jobs={max_jobs}, model={model_override})")

        scheduler = SequentialBatchScheduler(tier2_model=model_override)
        results = scheduler.run_tier2_batch(max_jobs=max_jobs)
        results['timestamp'] = datetime.now().isoformat()

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Tier 2 analysis failed: {e}", exc_info=True)
        return jsonify({
            'error': 'Tier 2 analysis failed',
            'message': str(e),
            'tier': 2
        }), 500


@tiered_analysis_bp.route('/tier3', methods=['POST'])
@require_api_key
def run_tier3_analysis():
    """
    Run Tier 3 (Strategic Analysis) batch processing

    Request Body (optional):
    {
        "max_jobs": 100,
        "model_override": "gemini-1.5-pro"  // For better strategic reasoning
    }

    Response: Same format as tier1
    """
    try:
        data = request.get_json() or {}
        max_jobs = data.get('max_jobs')
        model_override = data.get('model_override')

        logger.info(f"Tier 3 analysis requested (max_jobs={max_jobs}, model={model_override})")

        scheduler = SequentialBatchScheduler(tier3_model=model_override)
        results = scheduler.run_tier3_batch(max_jobs=max_jobs)
        results['timestamp'] = datetime.now().isoformat()

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Tier 3 analysis failed: {e}", exc_info=True)
        return jsonify({
            'error': 'Tier 3 analysis failed',
            'message': str(e),
            'tier': 3
        }), 500


@tiered_analysis_bp.route('/sequential-batch', methods=['POST'])
@require_api_key
def run_sequential_batch():
    """
    Run complete sequential batch processing (all three tiers)

    Executes:
    1. Tier 1 for ALL unanalyzed jobs
    2. Tier 2 for ALL Tier-1-completed jobs
    3. Tier 3 for ALL Tier-2-completed jobs

    Request Body (optional):
    {
        "tier1_max_jobs": 100,
        "tier2_max_jobs": 100,
        "tier3_max_jobs": 100,
        "tier1_model": "gemini-2.0-flash-lite-001",
        "tier2_model": "gemini-2.0-flash-001",
        "tier3_model": "gemini-1.5-pro"
    }

    Response:
    {
        "execution_type": "full_sequential_batch",
        "total_time_seconds": 450.2,
        "tier1": {
            "tier": 1,
            "successful": 48,
            "failed": 2,
            ...
        },
        "tier2": {
            "tier": 2,
            "successful": 47,
            "failed": 1,
            ...
        },
        "tier3": {
            "tier": 3,
            "successful": 46,
            "failed": 1,
            ...
        },
        "summary": {
            "total_jobs_processed": 141,
            "total_failures": 4,
            "total_tokens": 285000
        }
    }
    """
    try:
        data = request.get_json() or {}

        tier1_max = data.get('tier1_max_jobs')
        tier2_max = data.get('tier2_max_jobs')
        tier3_max = data.get('tier3_max_jobs')

        tier1_model = data.get('tier1_model')
        tier2_model = data.get('tier2_model')
        tier3_model = data.get('tier3_model')

        logger.info(
            f"Sequential batch requested: "
            f"tier1_max={tier1_max}, tier2_max={tier2_max}, tier3_max={tier3_max}"
        )

        # Initialize scheduler with model overrides
        scheduler = SequentialBatchScheduler(
            tier1_model=tier1_model,
            tier2_model=tier2_model,
            tier3_model=tier3_model
        )

        # Run full sequential batch
        results = scheduler.run_full_sequential_batch(
            tier1_max_jobs=tier1_max,
            tier2_max_jobs=tier2_max,
            tier3_max_jobs=tier3_max
        )

        results['timestamp'] = datetime.now().isoformat()

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Sequential batch failed: {e}", exc_info=True)
        return jsonify({
            'error': 'Sequential batch failed',
            'message': str(e)
        }), 500


@tiered_analysis_bp.route('/status', methods=['GET'])
@require_api_key
def get_pipeline_status():
    """
    Get current status of tier processing pipeline

    Response:
    {
        "pending_tier1": 120,   // Jobs needing Tier 1 analysis
        "pending_tier2": 45,    // Jobs needing Tier 2 analysis
        "pending_tier3": 12,    // Jobs needing Tier 3 analysis
        "fully_analyzed": 1250, // Jobs with all three tiers complete
        "active_tier": 1,       // Currently active tier (1, 2, 3, or null)
        "current_time": "2025-10-09T02:45:00"
    }
    """
    try:
        status = get_status()
        return jsonify(status), 200

    except Exception as e:
        logger.error(f"Failed to get status: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to get status',
            'message': str(e)
        }), 500


@tiered_analysis_bp.route('/tier-stats', methods=['GET'])
@require_api_key
def get_tier_statistics():
    """
    Get detailed statistics for tier completion

    Response:
    {
        "tier1_stats": {
            "total_analyzed": 1500,
            "avg_tokens": 1850,
            "avg_response_time_ms": 2100,
            "success_rate": 0.96
        },
        "tier2_stats": {
            "total_analyzed": 1450,
            "avg_tokens": 1250,
            "avg_response_time_ms": 2800,
            "success_rate": 0.97
        },
        "tier3_stats": {
            "total_analyzed": 1420,
            "avg_tokens": 1650,
            "avg_response_time_ms": 3200,
            "success_rate": 0.98
        }
    }
    """
    try:
        from modules.database.database_manager import DatabaseManager

        db = DatabaseManager()

        # Get Tier 1 stats
        tier1_query = """
            SELECT
                COUNT(*) as total_analyzed,
                AVG(tier_1_tokens_used) as avg_tokens,
                AVG(tier_1_response_time_ms) as avg_response_time_ms,
                COUNT(*) FILTER (WHERE tier_1_completed = TRUE)::FLOAT / NULLIF(COUNT(*), 0) as success_rate
            FROM job_analysis_tiers
            WHERE tier_1_completed = TRUE
        """

        tier1_result = db.execute_query(tier1_query)

        # Get Tier 2 stats
        tier2_query = """
            SELECT
                COUNT(*) as total_analyzed,
                AVG(tier_2_tokens_used) as avg_tokens,
                AVG(tier_2_response_time_ms) as avg_response_time_ms,
                COUNT(*) FILTER (WHERE tier_2_completed = TRUE)::FLOAT / NULLIF(COUNT(*), 0) as success_rate
            FROM job_analysis_tiers
            WHERE tier_2_completed = TRUE
        """

        tier2_result = db.execute_query(tier2_query)

        # Get Tier 3 stats
        tier3_query = """
            SELECT
                COUNT(*) as total_analyzed,
                AVG(tier_3_tokens_used) as avg_tokens,
                AVG(tier_3_response_time_ms) as avg_response_time_ms,
                COUNT(*) FILTER (WHERE tier_3_completed = TRUE)::FLOAT / NULLIF(COUNT(*), 0) as success_rate
            FROM job_analysis_tiers
            WHERE tier_3_completed = TRUE
        """

        tier3_result = db.execute_query(tier3_query)

        # Format results
        def format_tier_stats(result):
            if not result or len(result) == 0:
                return {
                    'total_analyzed': 0,
                    'avg_tokens': 0,
                    'avg_response_time_ms': 0,
                    'success_rate': 0.0
                }

            row = result[0]
            return {
                'total_analyzed': int(row[0] or 0),
                'avg_tokens': int(row[1] or 0),
                'avg_response_time_ms': int(row[2] or 0),
                'success_rate': float(row[3] or 0.0)
            }

        response = {
            'tier1_stats': format_tier_stats(tier1_result),
            'tier2_stats': format_tier_stats(tier2_result),
            'tier3_stats': format_tier_stats(tier3_result),
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Failed to get tier statistics: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to get statistics',
            'message': str(e)
        }), 500


@tiered_analysis_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint (no authentication required)

    Response:
    {
        "status": "healthy",
        "service": "tiered_job_analysis",
        "timestamp": "2025-10-09T02:45:00"
    }
    """
    return jsonify({
        'status': 'healthy',
        'service': 'tiered_job_analysis',
        'timestamp': datetime.now().isoformat()
    }), 200


# Error handlers

@tiered_analysis_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400


@tiered_analysis_bp.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized errors"""
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Valid API key required'
    }), 401


@tiered_analysis_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


# Registration helper

def register_tiered_analysis_routes(app):
    """
    Register tiered analysis blueprint with Flask app

    Usage:
        from modules.ai_job_description_analysis.api_routes_tiered import register_tiered_analysis_routes

        app = Flask(__name__)
        register_tiered_analysis_routes(app)
    """
    app.register_blueprint(tiered_analysis_bp)
    logger.info("Tiered analysis routes registered at /api/analyze")
