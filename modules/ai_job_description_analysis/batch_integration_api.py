"""
Batch AI Analysis Integration API - Step 1.2 API Endpoints
REST API endpoints for managing batch AI job analysis workflow

This module provides HTTP endpoints for the BatchAIAnalyzer system including
queue management, processing control, and status monitoring.

Author: Automated Job Application System v2.16
Date: July 24, 2025
"""

import logging
from flask import Blueprint, request, jsonify
from typing import Dict, List, Optional
from modules.ai_job_description_analysis.batch_analyzer import BatchAIAnalyzer
from modules.integration.jobs_populator import JobsPopulator
from modules.dashboard_api import require_dashboard_auth as require_auth

logger = logging.getLogger(__name__)

# Create Blueprint for batch AI analysis API
batch_ai_bp = Blueprint("batch_ai", __name__, url_prefix="/api/batch-ai")


@batch_ai_bp.route("/process-queue", methods=["POST"])
@require_auth
def process_analysis_queue():
    """
    Process jobs from the analysis queue with AI analysis

    POST /api/batch-ai/process-queue
    Body: {
        "batch_size": 10,      // Optional: number of jobs to process
        "force_run": false     // Optional: override scheduling restrictions
    }

    Returns:
        JSON: Processing statistics and results
    """
    try:
        data = request.get_json() or {}
        batch_size = data.get("batch_size", 10)
        force_run = data.get("force_run", False)

        # Validate batch_size
        if not isinstance(batch_size, int) or batch_size < 1 or batch_size > 50:
            return jsonify({"error": "batch_size must be integer between 1 and 50", "provided": batch_size}), 400

        logger.info(f"Processing analysis queue: batch_size={batch_size}, force_run={force_run}")

        # Initialize batch analyzer and process queue
        analyzer = BatchAIAnalyzer()
        result = analyzer.process_analysis_queue(batch_size=batch_size, force_run=force_run)

        return jsonify(
            {
                "success": True,
                "results": result,
                "message": f"Processed {result.get('processed', 0)} jobs from analysis queue",
            }
        )

    except Exception as e:
        logger.error(f"Error processing analysis queue: {e}")
        return jsonify({"success": False, "error": str(e), "message": "Failed to process analysis queue"}), 500


@batch_ai_bp.route("/queue-jobs", methods=["POST"])
@require_auth
def queue_jobs_for_analysis():
    """
    Add jobs to the analysis queue

    POST /api/batch-ai/queue-jobs
    Body: {
        "job_ids": ["uuid1", "uuid2"],  // Optional: specific job IDs
        "priority": 5                   // Optional: queue priority (1-10)
    }

    Returns:
        JSON: Queueing statistics
    """
    try:
        data = request.get_json() or {}
        job_ids = data.get("job_ids")
        priority = data.get("priority", 5)

        # Validate priority
        if not isinstance(priority, int) or priority < 1 or priority > 10:
            return jsonify({"error": "priority must be integer between 1 and 10", "provided": priority}), 400

        logger.info(f"Queueing jobs for analysis: job_ids={len(job_ids) if job_ids else 'all'}, priority={priority}")

        # Initialize batch analyzer and queue jobs
        analyzer = BatchAIAnalyzer()
        result = analyzer.queue_jobs_for_analysis(job_ids=job_ids, priority=priority)

        return jsonify(
            {"success": True, "results": result, "message": f"Queued {result.get('queued', 0)} jobs for AI analysis"}
        )

    except Exception as e:
        logger.error(f"Error queueing jobs for analysis: {e}")
        return jsonify({"success": False, "error": str(e), "message": "Failed to queue jobs for analysis"}), 500


@batch_ai_bp.route("/queue-status", methods=["GET"])
@require_auth
def get_queue_status():
    """
    Get current analysis queue status and statistics

    GET /api/batch-ai/queue-status

    Returns:
        JSON: Queue status information including counts and processing stats
    """
    try:
        analyzer = BatchAIAnalyzer()
        status = analyzer.get_queue_status()

        return jsonify(
            {
                "success": True,
                "status": status,
                "message": f"Queue contains {status.get('total_queued', 0)} pending jobs",
            }
        )

    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        return jsonify({"success": False, "error": str(e), "message": "Failed to get queue status"}), 500


@batch_ai_bp.route("/scheduling/enable", methods=["POST"])
@require_auth
def enable_scheduling():
    """
    Enable scheduled processing with custom hours

    POST /api/batch-ai/scheduling/enable
    Body: {
        "start_hour": 2,    // Optional: start hour (default: 2am)
        "end_hour": 6       // Optional: end hour (default: 6am)
    }

    Returns:
        JSON: Configuration status
    """
    try:
        data = request.get_json() or {}
        start_hour = data.get("start_hour", 2)
        end_hour = data.get("end_hour", 6)

        # Validate hours
        if not isinstance(start_hour, int) or start_hour < 0 or start_hour > 23:
            return jsonify({"error": "start_hour must be integer between 0 and 23", "provided": start_hour}), 400

        if not isinstance(end_hour, int) or end_hour < 0 or end_hour > 23:
            return jsonify({"error": "end_hour must be integer between 0 and 23", "provided": end_hour}), 400

        logger.info(f"Enabling scheduling: {start_hour}:00 - {end_hour}:00")

        analyzer = BatchAIAnalyzer()
        result = analyzer.enable_scheduling(start_hour=start_hour, end_hour=end_hour)

        return jsonify(
            {
                "success": True,
                "configuration": result,
                "message": f"Scheduling enabled from {start_hour}:00 to {end_hour}:00",
            }
        )

    except Exception as e:
        logger.error(f"Error enabling scheduling: {e}")
        return jsonify({"success": False, "error": str(e), "message": "Failed to enable scheduling"}), 500


@batch_ai_bp.route("/scheduling/disable", methods=["POST"])
@require_auth
def disable_scheduling():
    """
    Disable scheduled processing (for testing)

    POST /api/batch-ai/scheduling/disable

    Returns:
        JSON: Configuration status
    """
    try:
        logger.info("Disabling scheduling for testing")

        analyzer = BatchAIAnalyzer()
        result = analyzer.disable_scheduling()

        return jsonify(
            {
                "success": True,
                "configuration": result,
                "message": "Scheduling disabled - processing allowed anytime for testing",
            }
        )

    except Exception as e:
        logger.error(f"Error disabling scheduling: {e}")
        return jsonify({"success": False, "error": str(e), "message": "Failed to disable scheduling"}), 500


@batch_ai_bp.route("/full-pipeline", methods=["POST"])
@require_auth
def run_full_pipeline():
    """
    Execute complete pipeline: transfer cleaned jobs → queue → analyze

    POST /api/batch-ai/full-pipeline
    Body: {
        "transfer_batch_size": 50,    // Optional: batch size for job transfer
        "analysis_batch_size": 10,    // Optional: batch size for AI analysis
        "analysis_priority": 5,       // Optional: queue priority for analysis
        "force_analysis": false       // Optional: override scheduling restrictions
    }

    Returns:
        JSON: Complete pipeline statistics
    """
    try:
        data = request.get_json() or {}
        transfer_batch_size = data.get("transfer_batch_size", 50)
        analysis_batch_size = data.get("analysis_batch_size", 10)
        analysis_priority = data.get("analysis_priority", 5)
        force_analysis = data.get("force_analysis", False)

        logger.info(f"Running full pipeline: transfer={transfer_batch_size}, analysis={analysis_batch_size}")

        pipeline_results = {}

        # Step 1: Transfer cleaned jobs to jobs table
        logger.info("Step 1: Transferring cleaned jobs to jobs table")
        populator = JobsPopulator()
        transfer_result = populator.process_batch(batch_size=transfer_batch_size)
        pipeline_results["transfer"] = transfer_result

        # Step 2: Queue newly transferred jobs for analysis
        if transfer_result.get("jobs_created", 0) > 0:
            logger.info("Step 2: Queueing transferred jobs for AI analysis")
            analyzer = BatchAIAnalyzer()
            queue_result = analyzer.queue_jobs_for_analysis(priority=analysis_priority)
            pipeline_results["queue"] = queue_result

            # Step 3: Process analysis queue
            if queue_result.get("queued", 0) > 0:
                logger.info("Step 3: Processing AI analysis queue")
                analysis_result = analyzer.process_analysis_queue(
                    batch_size=analysis_batch_size, force_run=force_analysis
                )
                pipeline_results["analysis"] = analysis_result
            else:
                pipeline_results["analysis"] = {"message": "No jobs queued for analysis"}
        else:
            pipeline_results["queue"] = {"message": "No new jobs to queue"}
            pipeline_results["analysis"] = {"message": "No jobs to analyze"}

        # Calculate summary statistics
        total_processed = transfer_result.get("processed", 0)
        total_jobs_created = transfer_result.get("jobs_created", 0)
        total_analyzed = pipeline_results.get("analysis", {}).get("analyzed", 0)

        return jsonify(
            {
                "success": True,
                "pipeline_results": pipeline_results,
                "summary": {
                    "cleaned_jobs_processed": total_processed,
                    "jobs_created": total_jobs_created,
                    "jobs_analyzed": total_analyzed,
                },
                "message": f"Pipeline complete: {total_jobs_created} jobs created, {total_analyzed} analyzed",
            }
        )

    except Exception as e:
        logger.error(f"Error running full pipeline: {e}")
        return jsonify({"success": False, "error": str(e), "message": "Failed to run full pipeline"}), 500


@batch_ai_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for batch AI analysis system

    GET /api/batch-ai/health

    Returns:
        JSON: System health status
    """
    try:
        # Basic health checks
        analyzer = BatchAIAnalyzer()
        populator = JobsPopulator()

        # Check database connectivity
        db_status = analyzer.db.test_connection()

        # Get basic system stats
        queue_status = analyzer.get_queue_status()

        health_status = {
            "database_connected": db_status,
            "batch_analyzer_ready": True,
            "jobs_populator_ready": True,
            "total_queued_jobs": queue_status.get("total_queued", 0),
            "scheduling_enabled": queue_status.get("schedule_enabled", False),
            "timestamp": queue_status.get("timestamp"),
        }

        return jsonify({"success": True, "health": health_status, "message": "Batch AI analysis system is healthy"})

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return (
            jsonify({"success": False, "error": str(e), "message": "Batch AI analysis system health check failed"}),
            500,
        )
