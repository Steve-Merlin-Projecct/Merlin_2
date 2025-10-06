"""
Workflow-Aware Batch AI Analyzer for New Job Processing Pipeline
==============================================================

This module adapts the existing batch AI analyzer to work with the new workflow:
raw_job_scrapes -> cleaned_job_scrapes -> pre_analyzed_jobs -> ai analysis -> analyzed_jobs

Key Features:
- Processes jobs from pre_analyzed_jobs table
- Saves results to analyzed_jobs table
- No primary keys passed to LLM prompts
- Maintains audit trail and deduplication
- Uses pure Gemini API responses (based on test_pure_gemini_api.py findings)

Author: Automated Job Application System V2.16
Created: 2025-07-26
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.database.workflow_manager import WorkflowManager

logger = logging.getLogger(__name__)


class WorkflowBatchAnalyzer:
    """
    Batch AI analyzer adapted for the new workflow pipeline.

    This analyzer:
    - Gets jobs from pre_analyzed_jobs via WorkflowManager
    - Processes through GeminiJobAnalyzer (pure API responses only)
    - Saves results to analyzed_jobs via WorkflowManager
    - Maintains proper audit trails without exposing primary keys
    """

    def __init__(self):
        """Initialize the workflow batch analyzer."""
        self.workflow_manager = WorkflowManager()
        self.ai_analyzer = GeminiJobAnalyzer()

    def process_queued_jobs(self, batch_size: int = 10) -> Dict:
        """
        Process queued jobs from pre_analyzed_jobs through AI analysis.

        This method:
        1. Gets jobs queued for analysis (without primary keys)
        2. Sends to Gemini AI for analysis
        3. Saves pure AI results to analyzed_jobs
        4. Maintains audit trail throughout process

        Args:
            batch_size: Number of jobs to process in one batch

        Returns:
            Dict containing processing results and statistics
        """
        logger.info(f"Starting workflow batch analysis (batch_size: {batch_size})")

        try:
            # Step 1: Get jobs ready for AI analysis
            jobs_for_analysis = self.workflow_manager.get_jobs_for_ai_analysis(batch_size)

            if not jobs_for_analysis:
                return {
                    "success": True,
                    "processed": 0,
                    "analyzed": 0,
                    "saved": 0,
                    "message": "No jobs queued for analysis",
                }

            logger.info(f"Retrieved {len(jobs_for_analysis)} jobs for AI analysis")

            # Step 2: Prepare jobs for AI analysis (ensuring no primary keys)
            ai_ready_jobs = self._prepare_jobs_for_ai_analysis(jobs_for_analysis)

            # Step 3: Process through Gemini AI analyzer
            ai_results = self.ai_analyzer.analyze_jobs_batch(ai_ready_jobs)

            if not ai_results.get("success"):
                logger.error(f"AI analysis failed: {ai_results.get('error')}")
                return {
                    "success": False,
                    "error": f"AI analysis failed: {ai_results.get('error')}",
                    "processed": len(jobs_for_analysis),
                    "analyzed": 0,
                    "saved": 0,
                }

            analyzed_count = len(ai_results.get("results", []))
            logger.info(f"AI analysis completed for {analyzed_count} jobs")

            # Step 4: Prepare results for saving (add dedup keys back)
            save_ready_results = self._prepare_results_for_saving(ai_results.get("results", []), jobs_for_analysis)

            # Step 5: Save results to analyzed_jobs table
            save_result = self.workflow_manager.save_ai_analysis_results(save_ready_results)

            if not save_result.get("success"):
                logger.error(f"Failed to save AI results: {save_result.get('error')}")
                return {
                    "success": False,
                    "error": f"Failed to save results: {save_result.get('error')}",
                    "processed": len(jobs_for_analysis),
                    "analyzed": analyzed_count,
                    "saved": 0,
                }

            saved_count = save_result.get("saved_count", 0)
            logger.info(f"Workflow batch analysis completed: {saved_count} jobs saved")

            return {
                "success": True,
                "processed": len(jobs_for_analysis),
                "analyzed": analyzed_count,
                "saved": saved_count,
                "skipped": save_result.get("skipped_count", 0),
                "ai_usage": ai_results.get("usage_stats", {}),
                "message": f"Successfully processed {saved_count} jobs through workflow pipeline",
            }

        except Exception as e:
            logger.error(f"Error in workflow batch analysis: {e}")
            return {"success": False, "error": str(e), "processed": 0, "analyzed": 0, "saved": 0}

    def _prepare_jobs_for_ai_analysis(self, workflow_jobs: List[Dict]) -> List[Dict]:
        """
        Prepare jobs for AI analysis ensuring no primary keys are included.

        Based on test_pure_gemini_api.py findings, AI analyzer expects:
        - 'id': string (but we use dedup key, not primary key)
        - 'title': string
        - 'description': string
        - 'company_name': string (optional)

        Args:
            workflow_jobs: Jobs from workflow manager

        Returns:
            List of jobs formatted for AI analysis
        """
        ai_jobs = []

        for i, job in enumerate(workflow_jobs):
            # Create AI-ready job data (no primary keys exposed)
            ai_job = {
                "id": f"workflow_job_{i+1}",  # Sequential ID for AI processing only
                "title": job.get("title", ""),
                "description": job.get("description", ""),
                "company_name": job.get("company_name", "Unknown Company"),
                # Store dedup key separately for result matching
                "_internal_dedup_key": job.get("internal_dedup_key"),
            }

            ai_jobs.append(ai_job)

        logger.info(f"Prepared {len(ai_jobs)} jobs for AI analysis (no primary keys exposed)")
        return ai_jobs

    def _prepare_results_for_saving(self, ai_results: List[Dict], original_jobs: List[Dict]) -> List[Dict]:
        """
        Prepare AI analysis results for saving to analyzed_jobs table.

        This method:
        - Maps AI results back to original jobs using sequential order
        - Adds deduplication keys for proper job matching
        - Includes only pure Gemini API data (as verified by test_pure_gemini_api.py)

        Args:
            ai_results: Results from Gemini AI analysis
            original_jobs: Original jobs with dedup keys

        Returns:
            List of results ready for saving
        """
        save_ready_results = []

        for i, ai_result in enumerate(ai_results):
            if i < len(original_jobs):
                # Get the original job to retrieve dedup key
                original_job = original_jobs[i]

                # Create save-ready result with dedup key
                save_result = {
                    "internal_dedup_key": original_job.get("internal_dedup_key"),
                    # Pure Gemini API fields (verified by test_pure_gemini_api.py)
                    "primary_industry": ai_result.get("primary_industry"),
                    "secondary_industries": ai_result.get("secondary_industries", []),
                    "seniority_level": ai_result.get("seniority_level"),
                    "authenticity_score": ai_result.get("authenticity_score"),
                    "skills_analysis": ai_result.get("skills_analysis", []),
                    "structured_data": ai_result.get("structured_data", {}),
                    # Analysis metadata
                    "model_used": "gemini-2.0-flash-001",
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "gemini_tokens_used": ai_result.get("_analysis_metadata", {}).get("tokens_used", 0),
                }

                save_ready_results.append(save_result)
            else:
                logger.warning(f"AI result {i} has no corresponding original job")

        logger.info(f"Prepared {len(save_ready_results)} results for saving")
        return save_ready_results

    def run_full_workflow_cycle(self, transfer_batch: int = 100, analysis_batch: int = 10) -> Dict:
        """
        Run a complete workflow cycle from cleaned_job_scrapes to analyzed_jobs.

        This method:
        1. Transfers cleaned scrapes to pre_analyzed_jobs
        2. Queues jobs for analysis
        3. Processes queued jobs through AI analysis
        4. Returns comprehensive results

        Args:
            transfer_batch: Batch size for transfer step
            analysis_batch: Batch size for AI analysis step

        Returns:
            Dict containing results from all workflow steps
        """
        logger.info(f"Starting full workflow cycle (transfer: {transfer_batch}, analysis: {analysis_batch})")

        cycle_results = {"success": True, "steps": {}, "summary": {}}

        try:
            # Step 1: Transfer cleaned scrapes to pre_analyzed_jobs
            logger.info("Step 1: Transferring cleaned scrapes to pre_analyzed_jobs")
            transfer_result = self.workflow_manager.transfer_cleaned_to_pre_analyzed(transfer_batch)
            cycle_results["steps"]["transfer"] = transfer_result

            if not transfer_result.get("success"):
                cycle_results["success"] = False
                cycle_results["error"] = f"Transfer step failed: {transfer_result.get('error')}"
                return cycle_results

            # Step 2: Queue jobs for analysis
            logger.info("Step 2: Queuing jobs for AI analysis")
            queue_result = self.workflow_manager.queue_jobs_for_analysis(analysis_batch)
            cycle_results["steps"]["queue"] = queue_result

            if not queue_result.get("success"):
                cycle_results["success"] = False
                cycle_results["error"] = f"Queue step failed: {queue_result.get('error')}"
                return cycle_results

            # Step 3: Process queued jobs through AI analysis
            logger.info("Step 3: Processing jobs through AI analysis")
            analysis_result = self.process_queued_jobs(analysis_batch)
            cycle_results["steps"]["analysis"] = analysis_result

            if not analysis_result.get("success"):
                cycle_results["success"] = False
                cycle_results["error"] = f"Analysis step failed: {analysis_result.get('error')}"
                return cycle_results

            # Step 4: Generate summary
            cycle_results["summary"] = {
                "transferred_to_pre_analyzed": transfer_result.get("transferred", 0),
                "queued_for_analysis": queue_result.get("queued_count", 0),
                "analyzed_jobs": analysis_result.get("analyzed", 0),
                "saved_to_analyzed_jobs": analysis_result.get("saved", 0),
                "total_processing_time": "Completed successfully",
            }

            logger.info(f"Full workflow cycle completed successfully: {cycle_results['summary']}")

            return cycle_results

        except Exception as e:
            logger.error(f"Error in full workflow cycle: {e}")
            cycle_results["success"] = False
            cycle_results["error"] = str(e)
            return cycle_results

    def get_workflow_status(self) -> Dict:
        """
        Get current status of the workflow pipeline.

        Returns:
            Dict containing current workflow statistics and health metrics
        """
        try:
            # Get workflow statistics
            stats_result = self.workflow_manager.get_workflow_statistics()

            if not stats_result.get("success"):
                return {"success": False, "error": "Failed to get workflow statistics"}

            stats = stats_result.get("statistics", {})
            health = stats_result.get("workflow_health", {})

            # Calculate additional metrics
            total_jobs_in_pipeline = stats.get("pre_analyzed_jobs", 0) + stats.get("analyzed_jobs", 0)

            pipeline_efficiency = round((stats.get("analyzed_jobs", 0) / max(total_jobs_in_pipeline, 1)) * 100, 2)

            return {
                "success": True,
                "current_status": {
                    "pipeline_stage_counts": stats,
                    "conversion_rates": health,
                    "pipeline_efficiency": pipeline_efficiency,
                    "jobs_ready_for_analysis": stats.get("pre_analyzed_queued", 0),
                    "analysis_completion_rate": health.get("analysis_completion_rate", 0),
                },
                "recommendations": self._generate_workflow_recommendations(stats, health),
            }

        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {"success": False, "error": str(e)}

    def _generate_workflow_recommendations(self, stats: Dict, health: Dict) -> List[str]:
        """Generate recommendations based on workflow statistics."""
        recommendations = []

        # Check for bottlenecks
        if stats.get("cleaned_job_scrapes", 0) > stats.get("pre_analyzed_jobs", 0) * 2:
            recommendations.append("Consider increasing batch size for cleaned-to-pre_analyzed transfer")

        if stats.get("pre_analyzed_queued", 0) > 50:
            recommendations.append("Large queue detected - consider running AI analysis")

        if health.get("analysis_completion_rate", 0) < 90:
            recommendations.append("Low analysis completion rate - check AI analyzer configuration")

        if stats.get("pre_analyzed_jobs", 0) > stats.get("analyzed_jobs", 0) * 3:
            recommendations.append("Many jobs awaiting analysis - consider batch processing")

        if not recommendations:
            recommendations.append("Workflow operating efficiently")

        return recommendations
