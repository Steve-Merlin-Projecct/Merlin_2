"""
Module: batch_analyzer.py
Purpose: Automated batch processing system for AI job analysis
Created: 2024-07-24
Modified: 2025-10-21
Dependencies: database_manager, ai_analyzer, normalized_analysis_writer
Related: ai_analyzer.py, sequential_batch_scheduler.py, batch_integration_api.py
Description: Processes jobs from job_analysis_queue using Google Gemini AI with
             queue management, scheduled processing (2am-6am configurable), retry
             logic, results storage in normalized tables, and usage tracking.
             Implements comprehensive error handling and rate limiting.
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4
from modules.database.database_manager import DatabaseManager
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.ai_job_description_analysis.normalized_analysis_writer import NormalizedAnalysisWriter

logger = logging.getLogger(__name__)


class BatchAIAnalyzer:
    """
    Automated batch processing system for AI job analysis

    Features:
    - Queue management for job_analysis_queue table
    - Scheduled processing between 2am-6am (configurable)
    - Comprehensive error handling and retry logic
    - Results storage in normalized database tables
    - Usage tracking and rate limiting
    """

    def __init__(self):
        """Initialize the batch analyzer with database and AI components"""
        self.db = DatabaseManager()
        self.ai_analyzer = GeminiJobAnalyzer()
        self.analysis_writer = NormalizedAnalysisWriter()

        # Scheduling configuration
        self.schedule_enabled = False  # Temporarily disabled for testing
        self.schedule_start_hour = 2  # 2 AM
        self.schedule_end_hour = 6  # 6 AM

        # Batch processing settings
        self.default_batch_size = 10
        self.max_retry_attempts = 3
        self.retry_delay_seconds = 300  # 5 minutes

        logger.info("BatchAIAnalyzer initialized with scheduling disabled for testing")

    def process_analysis_queue(self, batch_size: Optional[int] = None, force_run: bool = False) -> Dict:
        """
        Process jobs from the analysis queue with AI analysis

        Args:
            batch_size: Number of jobs to process in one batch (default: 10)
            force_run: Override scheduling restrictions for testing

        Returns:
            Dict: Processing statistics and results
        """
        batch_size = batch_size or self.default_batch_size

        # Check scheduling constraints unless force_run is True
        if not force_run and not self._is_processing_time_allowed():
            logger.info("Processing not allowed outside scheduled hours (2am-6am)")
            return {"error": "Outside scheduled processing hours", "processed": 0}

        logger.info(f"Starting batch AI analysis processing (batch_size: {batch_size})")

        try:
            # Get jobs from analysis queue
            queued_jobs = self._get_queued_jobs(batch_size)

            if not queued_jobs:
                logger.info("No jobs in analysis queue")
                return {"processed": 0, "analyzed": 0, "errors": 0, "skipped": 0}

            logger.info(f"Processing {len(queued_jobs)} jobs from analysis queue")

            processed_count = 0
            analyzed_count = 0
            error_count = 0
            skipped_count = 0

            for job_data in queued_jobs:
                try:
                    # Check if job already has analysis to avoid duplicates
                    if self._has_existing_analysis(job_data["job_id"]):
                        logger.info(f"Skipping job {job_data['job_id']} - already analyzed")
                        self._remove_from_queue(job_data["queue_id"])
                        skipped_count += 1
                        processed_count += 1
                        continue

                    # Perform AI analysis
                    analysis_result = self._analyze_single_job(job_data)

                    if analysis_result["success"]:
                        # Store analysis results in normalized tables
                        self._store_analysis_results(job_data["job_id"], analysis_result["analysis"])

                        # Remove from queue after successful processing
                        self._remove_from_queue(job_data["queue_id"])

                        analyzed_count += 1
                        logger.info(f"Successfully analyzed job {job_data['job_id']}")

                    else:
                        # Handle analysis failure with retry logic
                        self._handle_analysis_failure(job_data, analysis_result["error"])
                        error_count += 1

                    processed_count += 1

                    # Add delay between API calls to respect rate limits
                    time.sleep(1)

                except Exception as e:
                    logger.error(f"Error processing job {job_data.get('job_id', 'unknown')}: {e}")
                    error_count += 1
                    processed_count += 1
                    continue

            result = {
                "processed": processed_count,
                "analyzed": analyzed_count,
                "errors": error_count,
                "skipped": skipped_count,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"Batch processing completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in process_analysis_queue: {e}")
            raise

    def queue_jobs_for_analysis(self, job_ids: Optional[List[UUID]] = None, priority: int = 5) -> Dict:
        """
        Add jobs to the analysis queue

        Args:
            job_ids: Specific job IDs to queue (if None, queues all unanalyzed jobs)
            priority: Queue priority (1=highest, 10=lowest, default=5)

        Returns:
            Dict: Queueing statistics
        """
        try:
            if job_ids:
                # Queue specific jobs
                queued_count = self._queue_specific_jobs(job_ids, priority)
            else:
                # Queue all unanalyzed jobs
                queued_count = self._queue_unanalyzed_jobs(priority)

            logger.info(f"Queued {queued_count} jobs for AI analysis")

            return {"queued": queued_count, "priority": priority, "timestamp": datetime.now().isoformat()}

        except Exception as e:
            logger.error(f"Error in queue_jobs_for_analysis: {e}")
            raise

    def get_queue_status(self) -> Dict:
        """
        Get current analysis queue status and statistics

        Returns:
            Dict: Queue status information
        """
        try:
            # Get queue counts by priority
            priority_counts = self._get_queue_priority_counts()

            # Get total queue size
            total_queued = sum(priority_counts.values())

            # Get processing statistics
            processing_stats = self._get_processing_statistics()

            # Check if currently in processing window
            in_processing_window = self._is_processing_time_allowed()

            return {
                "total_queued": total_queued,
                "priority_breakdown": priority_counts,
                "processing_stats": processing_stats,
                "schedule_enabled": self.schedule_enabled,
                "in_processing_window": in_processing_window,
                "next_processing_window": self._get_next_processing_window(),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in get_queue_status: {e}")
            raise

    def enable_scheduling(self, start_hour: int = 2, end_hour: int = 6) -> Dict:
        """
        Enable scheduled processing with custom hours

        Args:
            start_hour: Start hour for processing (24-hour format)
            end_hour: End hour for processing (24-hour format)

        Returns:
            Dict: Configuration status
        """
        self.schedule_enabled = True
        self.schedule_start_hour = start_hour
        self.schedule_end_hour = end_hour

        logger.info(f"Scheduling enabled: {start_hour}:00 - {end_hour}:00")

        return {
            "schedule_enabled": True,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "next_window": self._get_next_processing_window(),
        }

    def disable_scheduling(self) -> Dict:
        """
        Disable scheduled processing (for testing)

        Returns:
            Dict: Configuration status
        """
        self.schedule_enabled = False
        logger.info("Scheduling disabled - processing allowed anytime")

        return {"schedule_enabled": False, "message": "Processing now allowed anytime for testing"}

    # Private helper methods

    def _is_processing_time_allowed(self) -> bool:
        """Check if current time is within allowed processing window"""
        if not self.schedule_enabled:
            return True  # Always allowed when scheduling is disabled

        current_hour = datetime.now().hour

        if self.schedule_start_hour <= self.schedule_end_hour:
            # Normal case: 2am-6am
            return self.schedule_start_hour <= current_hour < self.schedule_end_hour
        else:
            # Wrap-around case: 10pm-6am
            return current_hour >= self.schedule_start_hour or current_hour < self.schedule_end_hour

    def _get_next_processing_window(self) -> str:
        """Get the next scheduled processing window"""
        if not self.schedule_enabled:
            return "Scheduling disabled - processing allowed anytime"

        now = datetime.now()

        # Calculate next processing start time
        if now.hour < self.schedule_start_hour:
            # Today's window hasn't started yet
            next_start = now.replace(hour=self.schedule_start_hour, minute=0, second=0, microsecond=0)
        else:
            # Tomorrow's window
            next_start = (now + timedelta(days=1)).replace(
                hour=self.schedule_start_hour, minute=0, second=0, microsecond=0
            )

        next_end = next_start.replace(hour=self.schedule_end_hour)

        return f"{next_start.strftime('%Y-%m-%d %H:%M')} - {next_end.strftime('%H:%M')}"

    def _get_queued_jobs(self, limit: int) -> List[Dict]:
        """Get jobs from analysis queue ordered by priority and timestamp"""
        query = """
            SELECT jaq.id as queue_id, jaq.job_id, jaq.priority, jaq.retry_count,
                   j.job_title, j.company_id, j.job_description, c.name as company_name
            FROM job_analysis_queue jaq
            JOIN jobs j ON jaq.job_id = j.id
            JOIN companies c ON j.company_id = c.id
            WHERE jaq.status = 'pending'
              AND jaq.scheduled_for <= %s
            ORDER BY jaq.priority ASC, jaq.created_at ASC
            LIMIT %s
        """

        results = self.db.execute_query(query, (datetime.now(), limit))
        if not results:
            return []

        columns = [
            "queue_id",
            "job_id",
            "priority",
            "retry_count",
            "job_title",
            "company_id",
            "job_description",
            "company_name",
        ]

        return [dict(zip(columns, row)) for row in results]

    def _has_existing_analysis(self, job_id: UUID) -> bool:
        """Check if job already has AI analysis results"""
        query = "SELECT COUNT(*) FROM analyzed_jobs WHERE job_id = %s"
        result = self.db.execute_query(query, (job_id,))
        return result and result[0][0] > 0

    def _analyze_single_job(self, job_data: Dict) -> Dict:
        """Perform AI analysis on a single job"""
        try:
            # Prepare job data for AI analysis
            job_info = {
                "job_id": str(job_data["job_id"]),
                "title": job_data["job_title"],
                "company": job_data["company_name"],
                "description": job_data["job_description"],
            }

            # Call AI analyzer
            analysis_result = self.ai_analyzer.analyze_job_batch([job_info])

            if analysis_result and len(analysis_result) > 0:
                return {"success": True, "analysis": analysis_result[0]}  # First (and only) result
            else:
                return {"success": False, "error": "No analysis results returned from AI"}

        except Exception as e:
            logger.error(f"AI analysis failed for job {job_data['job_id']}: {e}")
            return {"success": False, "error": str(e)}

    def _store_analysis_results(self, job_id: UUID, analysis_data: Dict):
        """Store AI analysis results in normalized database tables"""
        try:
            # Use the existing NormalizedAnalysisWriter
            self.analysis_writer.save_analysis_results(job_id, analysis_data)
            logger.info(f"Stored analysis results for job {job_id}")

        except Exception as e:
            logger.error(f"Failed to store analysis results for job {job_id}: {e}")
            raise

    def _remove_from_queue(self, queue_id: int):
        """Remove job from analysis queue after successful processing"""
        try:
            update_query = """
                UPDATE job_analysis_queue 
                SET status = 'completed', completed_at = %s
                WHERE id = %s
            """
            self.db.execute_query(update_query, (datetime.now(), queue_id))

        except Exception as e:
            logger.error(f"Failed to remove queue item {queue_id}: {e}")
            raise

    def _handle_analysis_failure(self, job_data: Dict, error: str):
        """Handle analysis failure with retry logic"""
        try:
            retry_count = job_data.get("retry_count", 0) + 1

            if retry_count <= self.max_retry_attempts:
                # Schedule for retry
                next_attempt = datetime.now() + timedelta(seconds=self.retry_delay_seconds)

                update_query = """
                    UPDATE job_analysis_queue 
                    SET retry_count = %s, scheduled_for = %s, last_error = %s
                    WHERE id = %s
                """
                self.db.execute_query(update_query, (retry_count, next_attempt, error, job_data["queue_id"]))

                logger.warning(f"Scheduled retry {retry_count}/{self.max_retry_attempts} for job {job_data['job_id']}")

            else:
                # Mark as failed after max retries
                update_query = """
                    UPDATE job_analysis_queue 
                    SET status = 'failed', last_error = %s
                    WHERE id = %s
                """
                self.db.execute_query(update_query, (error, job_data["queue_id"]))

                logger.error(f"Job {job_data['job_id']} failed after {self.max_retry_attempts} attempts: {error}")

        except Exception as e:
            logger.error(f"Failed to handle analysis failure for job {job_data['job_id']}: {e}")

    def _queue_specific_jobs(self, job_ids: List[UUID], priority: int) -> int:
        """Queue specific jobs for analysis"""
        queued_count = 0

        for job_id in job_ids:
            try:
                # Check if already in queue
                existing_query = "SELECT COUNT(*) FROM job_analysis_queue WHERE job_id = %s AND status = 'pending'"
                existing_result = self.db.execute_query(existing_query, (job_id,))

                if existing_result and existing_result[0][0] > 0:
                    logger.info(f"Job {job_id} already in queue, skipping")
                    continue

                # Add to queue
                insert_query = """
                    INSERT INTO job_analysis_queue (job_id, priority, status, created_at, scheduled_for)
                    VALUES (%s, %s, 'pending', %s, %s)
                """
                self.db.execute_query(insert_query, (job_id, priority, datetime.now(), datetime.now()))

                queued_count += 1

            except Exception as e:
                logger.error(f"Failed to queue job {job_id}: {e}")
                continue

        return queued_count

    def _queue_unanalyzed_jobs(self, priority: int) -> int:
        """Queue all jobs that don't have AI analysis yet"""
        try:
            # Find jobs without analysis
            unanalyzed_query = """
                SELECT j.id 
                FROM jobs j
                LEFT JOIN analyzed_jobs aj ON j.id = aj.job_id
                LEFT JOIN job_analysis_queue jaq ON j.id = jaq.job_id AND jaq.status = 'pending'
                WHERE aj.job_id IS NULL AND jaq.job_id IS NULL
                  AND j.is_active = true
            """

            results = self.db.execute_query(unanalyzed_query)
            if not results:
                return 0

            job_ids = [row[0] for row in results]
            return self._queue_specific_jobs(job_ids, priority)

        except Exception as e:
            logger.error(f"Failed to queue unanalyzed jobs: {e}")
            return 0

    def _get_queue_priority_counts(self) -> Dict[int, int]:
        """Get count of queued jobs by priority level"""
        try:
            query = """
                SELECT priority, COUNT(*) 
                FROM job_analysis_queue 
                WHERE status = 'pending'
                GROUP BY priority
                ORDER BY priority
            """

            results = self.db.execute_query(query)
            if not results:
                return {}

            return {row[0]: row[1] for row in results}

        except Exception as e:
            logger.error(f"Failed to get priority counts: {e}")
            return {}

    def _get_processing_statistics(self) -> Dict:
        """Get historical processing statistics"""
        try:
            # Get statistics for last 24 hours
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

            stats_query = """
                SELECT 
                    COUNT(*) as total_processed,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    AVG(retry_count) as avg_retries
                FROM job_analysis_queue
                WHERE created_at >= %s
            """

            result = self.db.execute_query(stats_query, (twenty_four_hours_ago,))
            if not result:
                return {}

            row = result[0]
            return {
                "last_24h_processed": row[0] or 0,
                "last_24h_completed": row[1] or 0,
                "last_24h_failed": row[2] or 0,
                "avg_retry_count": float(row[3] or 0),
            }

        except Exception as e:
            logger.error(f"Failed to get processing statistics: {e}")
            return {}
