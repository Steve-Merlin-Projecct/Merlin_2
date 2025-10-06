"""
Integration API Module
Provides endpoints for managing the scraping to AI analysis pipeline
"""

import logging
from flask import Blueprint, request, jsonify
from modules.scraping.jobs_populator import JobsPopulator
from modules.ai_job_description_analysis.batch_analyzer import BatchAIAnalyzer
from modules.dashboard_api import require_dashboard_auth

logger = logging.getLogger(__name__)

# Create blueprint for integration endpoints
integration_bp = Blueprint("integration", __name__, url_prefix="/api/integration")


@integration_bp.route("/transfer-jobs", methods=["POST"])
@require_dashboard_auth
def transfer_cleaned_jobs():
    """Transfer cleaned scrapes to jobs table"""
    try:
        batch_size = request.json.get("batch_size", 50) if request.is_json else 50

        populator = JobsPopulator()
        stats = populator.transfer_cleaned_scrapes_to_jobs(batch_size=batch_size)

        return jsonify(
            {
                "success": True,
                "message": f"Transfer completed: {stats['successful']}/{stats['processed']} jobs transferred",
                "statistics": stats,
            }
        )

    except Exception as e:
        logger.error(f"Error in transfer_cleaned_jobs: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@integration_bp.route("/transfer-stats", methods=["GET"])
@require_dashboard_auth
def get_transfer_statistics():
    """Get statistics about job transfer process"""
    try:
        populator = JobsPopulator()
        stats = populator.get_transfer_statistics()

        return jsonify({"success": True, "statistics": stats})

    except Exception as e:
        logger.error(f"Error getting transfer statistics: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@integration_bp.route("/queue-jobs", methods=["POST"])
@require_dashboard_auth
def queue_jobs_for_analysis():
    """Queue jobs for AI analysis based on criteria"""
    try:
        data = request.get_json() or {}

        criteria = data.get("criteria", {"unanalyzed_only": True})
        priority = data.get("priority", "normal")
        limit = data.get("limit", 100)

        batch_analyzer = BatchAIAnalyzer()
        stats = batch_analyzer.queue_jobs_by_criteria(criteria, priority, limit)

        return jsonify({"success": True, "message": f"Queued {stats['queued']} jobs for analysis", "statistics": stats})

    except Exception as e:
        logger.error(f"Error queuing jobs: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@integration_bp.route("/run-analysis", methods=["POST"])
@require_dashboard_auth
def run_scheduled_analysis():
    """Run scheduled AI analysis on queued jobs"""
    try:
        max_jobs = request.json.get("max_jobs", 20) if request.is_json else 20

        batch_analyzer = BatchAIAnalyzer()
        stats = batch_analyzer.run_scheduled_analysis(max_jobs=max_jobs)

        return jsonify(
            {
                "success": True,
                "message": f"Analysis completed: {stats['successful']}/{stats['processed']} jobs analyzed",
                "statistics": stats,
            }
        )

    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@integration_bp.route("/queue-stats", methods=["GET"])
@require_dashboard_auth
def get_queue_statistics():
    """Get analysis queue statistics"""
    try:
        batch_analyzer = BatchAIAnalyzer()
        stats = batch_analyzer.get_queue_statistics()

        return jsonify({"success": True, "statistics": stats})

    except Exception as e:
        logger.error(f"Error getting queue statistics: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@integration_bp.route("/cleanup-queue", methods=["POST"])
@require_dashboard_auth
def cleanup_queue():
    """Clean up old completed queue entries"""
    try:
        older_than_days = request.json.get("older_than_days", 7) if request.is_json else 7

        batch_analyzer = BatchAIAnalyzer()
        deleted_count = batch_analyzer.cleanup_completed_queue_entries(older_than_days)

        return jsonify(
            {
                "success": True,
                "message": f"Cleaned up {deleted_count} old queue entries",
                "deleted_count": deleted_count,
            }
        )

    except Exception as e:
        logger.error(f"Error cleaning up queue: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@integration_bp.route("/pipeline-status", methods=["GET"])
@require_dashboard_auth
def get_pipeline_status():
    """Get comprehensive pipeline status"""
    try:
        populator = JobsPopulator()
        batch_analyzer = BatchAIAnalyzer()

        # Get transfer statistics
        transfer_stats = populator.get_transfer_statistics()

        # Get queue statistics
        queue_stats = batch_analyzer.get_queue_statistics()

        # Get pending jobs from queue
        pending_jobs = batch_analyzer.get_queued_jobs(limit=5, status="pending")

        return jsonify(
            {
                "success": True,
                "pipeline_status": {
                    "transfer_statistics": transfer_stats,
                    "queue_statistics": queue_stats,
                    "next_pending_jobs": len(pending_jobs),
                    "sample_pending_jobs": [
                        {
                            "job_id": str(job["job_id"]),
                            "title": job["job_title"],
                            "priority": job["priority"],
                            "queued_at": job["queued_at"].isoformat() if job["queued_at"] else None,
                        }
                        for job in pending_jobs[:3]
                    ],
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting pipeline status: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@integration_bp.route("/full-pipeline", methods=["POST"])
@require_dashboard_auth
def run_full_pipeline():
    """Run the complete pipeline: transfer jobs → queue → analyze"""
    try:
        data = request.get_json() or {}

        transfer_batch_size = data.get("transfer_batch_size", 50)
        analysis_batch_size = data.get("analysis_batch_size", 20)

        # Step 1: Transfer cleaned scrapes to jobs table
        populator = JobsPopulator()
        transfer_stats = populator.transfer_cleaned_scrapes_to_jobs(batch_size=transfer_batch_size)

        if transfer_stats["successful"] > 0:
            # Step 2: Queue newly transferred jobs for analysis
            batch_analyzer = BatchAIAnalyzer()
            criteria = {"unanalyzed_only": True}
            queue_stats = batch_analyzer.queue_jobs_by_criteria(
                criteria, priority="normal", limit=transfer_stats["successful"]
            )

            # Step 3: Run analysis on queued jobs
            analysis_stats = batch_analyzer.run_scheduled_analysis(max_jobs=analysis_batch_size)
        else:
            queue_stats = {"queued": 0, "already_queued": 0, "errors": 0}
            analysis_stats = {"processed": 0, "successful": 0, "failed": 0, "errors": []}

        return jsonify(
            {
                "success": True,
                "message": f"Full pipeline completed: {transfer_stats['successful']} transferred, {analysis_stats['successful']} analyzed",
                "pipeline_results": {"transfer": transfer_stats, "queuing": queue_stats, "analysis": analysis_stats},
            }
        )

    except Exception as e:
        logger.error(f"Error running full pipeline: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
