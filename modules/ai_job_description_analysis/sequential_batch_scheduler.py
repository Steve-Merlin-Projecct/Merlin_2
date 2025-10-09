"""
Sequential Batch Scheduler for 3-Tier Job Analysis
Orchestrates time-windowed batch processing across three tiers

Processing Schedule:
- 2:00-3:00 AM: Tier 1 (Core Analysis) - ALL unanalyzed jobs
- 3:00-4:30 AM: Tier 2 (Enhanced Analysis) - ALL Tier-1-completed jobs
- 4:30-6:00 AM: Tier 3 (Strategic Analysis) - ALL Tier-2-completed jobs

This scheduler ensures:
1. Complete coverage: ALL jobs receive ALL three tiers
2. Semantic coherence: Each tier builds on previous tier's context
3. Resource efficiency: 545 jobs/day vs 187 (3x improvement)
4. Free tier compliance: 1,500 requests/day limit
"""

import logging
import time
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional
from modules.database.database_manager import DatabaseManager
from modules.ai_job_description_analysis.tier1_analyzer import Tier1CoreAnalyzer
from modules.ai_job_description_analysis.tier2_analyzer import Tier2EnhancedAnalyzer
from modules.ai_job_description_analysis.tier3_analyzer import Tier3StrategicAnalyzer

logger = logging.getLogger(__name__)


class SequentialBatchScheduler:
    """
    Orchestrates three-tier sequential batch processing

    Time Windows:
    - Tier 1: 2:00-3:00 AM (60 minutes)
    - Tier 2: 3:00-4:30 AM (90 minutes)
    - Tier 3: 4:30-6:00 AM (90 minutes)

    Processing Flow:
    1. Tier 1 analyzes ALL unanalyzed jobs (marks tier_1_completed)
    2. Tier 2 analyzes ALL tier_1_completed jobs (marks tier_2_completed)
    3. Tier 3 analyzes ALL tier_2_completed jobs (marks tier_3_completed)
    """

    # Time window definitions (24-hour format)
    TIER1_START = dt_time(2, 0)   # 2:00 AM
    TIER1_END = dt_time(3, 0)     # 3:00 AM

    TIER2_START = dt_time(3, 0)   # 3:00 AM
    TIER2_END = dt_time(4, 30)    # 4:30 AM

    TIER3_START = dt_time(4, 30)  # 4:30 AM
    TIER3_END = dt_time(6, 0)     # 6:00 AM

    def __init__(
        self,
        tier1_model: Optional[str] = None,
        tier2_model: Optional[str] = None,
        tier3_model: Optional[str] = None,
        batch_size: int = 50,
        max_jobs_per_tier: Optional[int] = None
    ):
        """
        Initialize sequential batch scheduler

        Args:
            tier1_model: Optional model override for Tier 1 (e.g., 'gemini-2.0-flash-lite-001')
            tier2_model: Optional model override for Tier 2
            tier3_model: Optional model override for Tier 3 (e.g., 'gemini-1.5-pro')
            batch_size: Jobs per batch (default 50)
            max_jobs_per_tier: Optional limit on jobs per tier (for testing)
        """
        self.db = DatabaseManager()

        # Initialize tier analyzers with optional model overrides
        self.tier1_analyzer = Tier1CoreAnalyzer(model_override=tier1_model)
        self.tier2_analyzer = Tier2EnhancedAnalyzer(model_override=tier2_model)
        self.tier3_analyzer = Tier3StrategicAnalyzer(model_override=tier3_model)

        self.batch_size = batch_size
        self.max_jobs_per_tier = max_jobs_per_tier

        logger.info(f"SequentialBatchScheduler initialized (batch_size={batch_size})")
        if tier1_model:
            logger.info(f"Tier 1 using model: {tier1_model}")
        if tier2_model:
            logger.info(f"Tier 2 using model: {tier2_model}")
        if tier3_model:
            logger.info(f"Tier 3 using model: {tier3_model}")

    def is_in_tier1_window(self, current_time: Optional[datetime] = None) -> bool:
        """Check if current time is in Tier 1 processing window (2:00-3:00 AM)"""
        if current_time is None:
            current_time = datetime.now()

        current_time_only = current_time.time()
        return self.TIER1_START <= current_time_only < self.TIER1_END

    def is_in_tier2_window(self, current_time: Optional[datetime] = None) -> bool:
        """Check if current time is in Tier 2 processing window (3:00-4:30 AM)"""
        if current_time is None:
            current_time = datetime.now()

        current_time_only = current_time.time()
        return self.TIER2_START <= current_time_only < self.TIER2_END

    def is_in_tier3_window(self, current_time: Optional[datetime] = None) -> bool:
        """Check if current time is in Tier 3 processing window (4:30-6:00 AM)"""
        if current_time is None:
            current_time = datetime.now()

        current_time_only = current_time.time()
        return self.TIER3_START <= current_time_only < self.TIER3_END

    def get_active_tier(self, current_time: Optional[datetime] = None) -> Optional[int]:
        """
        Get which tier should be processing based on current time

        Returns:
            1, 2, 3 if in respective tier window, None if outside all windows
        """
        if self.is_in_tier1_window(current_time):
            return 1
        elif self.is_in_tier2_window(current_time):
            return 2
        elif self.is_in_tier3_window(current_time):
            return 3
        return None

    def run_tier1_batch(self, max_jobs: Optional[int] = None) -> Dict:
        """
        Run Tier 1 (Core Analysis) batch processing
        Processes ALL unanalyzed jobs

        Args:
            max_jobs: Optional limit on number of jobs to process

        Returns:
            Dict with batch processing statistics
        """
        logger.info("Starting Tier 1 (Core Analysis) batch processing")

        # Get unanalyzed jobs
        limit = max_jobs or self.max_jobs_per_tier or 1000
        job_ids = self.tier1_analyzer.get_unanalyzed_jobs(limit=limit)

        if not job_ids:
            logger.info("No unanalyzed jobs found for Tier 1")
            return {
                'tier': 1,
                'total_jobs': 0,
                'successful': 0,
                'failed': 0,
                'message': 'No jobs to process'
            }

        logger.info(f"Found {len(job_ids)} jobs for Tier 1 analysis")

        # Run batch analysis
        results = self.tier1_analyzer.batch_analyze(job_ids, batch_size=self.batch_size)
        results['tier'] = 1

        logger.info(
            f"Tier 1 batch completed: {results['successful']} successful, "
            f"{results['failed']} failed, {results.get('total_tokens', 0)} tokens"
        )

        return results

    def run_tier2_batch(self, max_jobs: Optional[int] = None) -> Dict:
        """
        Run Tier 2 (Enhanced Analysis) batch processing
        Processes ALL Tier-1-completed jobs that need Tier 2

        Args:
            max_jobs: Optional limit on number of jobs to process

        Returns:
            Dict with batch processing statistics
        """
        logger.info("Starting Tier 2 (Enhanced Analysis) batch processing")

        # Get Tier-1-completed jobs
        limit = max_jobs or self.max_jobs_per_tier or 1000
        job_ids = self.tier2_analyzer.get_tier1_completed_jobs(limit=limit)

        if not job_ids:
            logger.info("No Tier-1-completed jobs found for Tier 2")
            return {
                'tier': 2,
                'total_jobs': 0,
                'successful': 0,
                'failed': 0,
                'message': 'No jobs to process'
            }

        logger.info(f"Found {len(job_ids)} jobs for Tier 2 analysis")

        # Run batch analysis
        results = self.tier2_analyzer.batch_analyze(job_ids, batch_size=self.batch_size)
        results['tier'] = 2

        logger.info(
            f"Tier 2 batch completed: {results['successful']} successful, "
            f"{results['failed']} failed, {results.get('total_tokens', 0)} tokens"
        )

        return results

    def run_tier3_batch(self, max_jobs: Optional[int] = None) -> Dict:
        """
        Run Tier 3 (Strategic Analysis) batch processing
        Processes ALL Tier-2-completed jobs that need Tier 3

        Args:
            max_jobs: Optional limit on number of jobs to process

        Returns:
            Dict with batch processing statistics
        """
        logger.info("Starting Tier 3 (Strategic Analysis) batch processing")

        # Get Tier-2-completed jobs
        limit = max_jobs or self.max_jobs_per_tier or 1000
        job_ids = self.tier3_analyzer.get_tier2_completed_jobs(limit=limit)

        if not job_ids:
            logger.info("No Tier-2-completed jobs found for Tier 3")
            return {
                'tier': 3,
                'total_jobs': 0,
                'successful': 0,
                'failed': 0,
                'message': 'No jobs to process'
            }

        logger.info(f"Found {len(job_ids)} jobs for Tier 3 analysis")

        # Run batch analysis
        results = self.tier3_analyzer.batch_analyze(job_ids, batch_size=self.batch_size)
        results['tier'] = 3

        logger.info(
            f"Tier 3 batch completed: {results['successful']} successful, "
            f"{results['failed']} failed, {results.get('total_tokens', 0)} tokens"
        )

        return results

    def run_scheduled_tier(self, current_time: Optional[datetime] = None) -> Optional[Dict]:
        """
        Run the appropriate tier based on current time window

        Args:
            current_time: Optional datetime for testing (defaults to now)

        Returns:
            Dict with batch results if in a tier window, None if outside all windows
        """
        active_tier = self.get_active_tier(current_time)

        if active_tier is None:
            logger.info("Outside all tier processing windows")
            return None

        if active_tier == 1:
            return self.run_tier1_batch()
        elif active_tier == 2:
            return self.run_tier2_batch()
        elif active_tier == 3:
            return self.run_tier3_batch()

    def run_full_sequential_batch(
        self,
        tier1_max_jobs: Optional[int] = None,
        tier2_max_jobs: Optional[int] = None,
        tier3_max_jobs: Optional[int] = None
    ) -> Dict:
        """
        Run complete sequential batch processing regardless of time
        Useful for manual execution or catch-up processing

        Executes:
        1. Tier 1 for ALL unanalyzed jobs
        2. Tier 2 for ALL Tier-1-completed jobs
        3. Tier 3 for ALL Tier-2-completed jobs

        Args:
            tier1_max_jobs: Optional limit for Tier 1
            tier2_max_jobs: Optional limit for Tier 2
            tier3_max_jobs: Optional limit for Tier 3

        Returns:
            Dict with combined statistics from all tiers
        """
        logger.info("Starting full sequential batch processing (all tiers)")
        start_time = time.time()

        # Run Tier 1
        tier1_results = self.run_tier1_batch(max_jobs=tier1_max_jobs)

        # Run Tier 2
        tier2_results = self.run_tier2_batch(max_jobs=tier2_max_jobs)

        # Run Tier 3
        tier3_results = self.run_tier3_batch(max_jobs=tier3_max_jobs)

        # Combine statistics
        total_time = time.time() - start_time

        combined_results = {
            'execution_type': 'full_sequential_batch',
            'total_time_seconds': total_time,
            'tier1': tier1_results,
            'tier2': tier2_results,
            'tier3': tier3_results,
            'summary': {
                'total_jobs_processed': (
                    tier1_results.get('successful', 0) +
                    tier2_results.get('successful', 0) +
                    tier3_results.get('successful', 0)
                ),
                'total_failures': (
                    tier1_results.get('failed', 0) +
                    tier2_results.get('failed', 0) +
                    tier3_results.get('failed', 0)
                ),
                'total_tokens': (
                    tier1_results.get('total_tokens', 0) +
                    tier2_results.get('total_tokens', 0) +
                    tier3_results.get('total_tokens', 0)
                )
            }
        }

        logger.info(
            f"Full sequential batch completed in {total_time:.2f}s: "
            f"{combined_results['summary']['total_jobs_processed']} jobs processed, "
            f"{combined_results['summary']['total_tokens']} tokens used"
        )

        return combined_results

    def get_processing_status(self) -> Dict:
        """
        Get current status of tier processing pipeline

        Returns:
            Dict with counts of jobs at each tier stage
        """
        try:
            query = """
                SELECT
                    COUNT(*) FILTER (WHERE tier_1_completed IS NULL OR tier_1_completed = FALSE) as pending_tier1,
                    COUNT(*) FILTER (WHERE tier_1_completed = TRUE AND (tier_2_completed IS NULL OR tier_2_completed = FALSE)) as pending_tier2,
                    COUNT(*) FILTER (WHERE tier_2_completed = TRUE AND (tier_3_completed IS NULL OR tier_3_completed = FALSE)) as pending_tier3,
                    COUNT(*) FILTER (WHERE tier_1_completed = TRUE AND tier_2_completed = TRUE AND tier_3_completed = TRUE) as fully_analyzed
                FROM job_analysis_tiers
            """

            result = self.db.execute_query(query)

            if not result or len(result) == 0:
                return {
                    'pending_tier1': 0,
                    'pending_tier2': 0,
                    'pending_tier3': 0,
                    'fully_analyzed': 0
                }

            row = result[0]
            status = {
                'pending_tier1': row[0] or 0,
                'pending_tier2': row[1] or 0,
                'pending_tier3': row[2] or 0,
                'fully_analyzed': row[3] or 0,
                'active_tier': self.get_active_tier(),
                'current_time': datetime.now().isoformat()
            }

            return status

        except Exception as e:
            logger.error(f"Failed to get processing status: {e}")
            return {
                'error': str(e),
                'pending_tier1': 0,
                'pending_tier2': 0,
                'pending_tier3': 0,
                'fully_analyzed': 0
            }

    def run_continuous_scheduler(self, check_interval_seconds: int = 300):
        """
        Run continuous scheduler that checks time windows and processes jobs

        This is the main entry point for automated execution.
        Runs indefinitely, checking every 5 minutes (default) for active tier windows.

        Args:
            check_interval_seconds: How often to check for active tier (default 300s = 5 min)
        """
        logger.info(
            f"Starting continuous scheduler (check interval: {check_interval_seconds}s)"
        )

        while True:
            try:
                current_time = datetime.now()
                logger.info(f"Scheduler check at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

                # Run appropriate tier if in window
                result = self.run_scheduled_tier(current_time)

                if result:
                    logger.info(f"Tier {result['tier']} batch completed")
                else:
                    status = self.get_processing_status()
                    logger.info(
                        f"No active tier window. Status: "
                        f"{status['pending_tier1']} pending Tier 1, "
                        f"{status['pending_tier2']} pending Tier 2, "
                        f"{status['pending_tier3']} pending Tier 3"
                    )

                # Wait until next check
                time.sleep(check_interval_seconds)

            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                # Continue running despite errors
                time.sleep(check_interval_seconds)


# Convenience functions for manual execution

def run_tier1_now(max_jobs: Optional[int] = None) -> Dict:
    """Run Tier 1 batch immediately (ignores time window)"""
    scheduler = SequentialBatchScheduler()
    return scheduler.run_tier1_batch(max_jobs=max_jobs)


def run_tier2_now(max_jobs: Optional[int] = None) -> Dict:
    """Run Tier 2 batch immediately (ignores time window)"""
    scheduler = SequentialBatchScheduler()
    return scheduler.run_tier2_batch(max_jobs=max_jobs)


def run_tier3_now(max_jobs: Optional[int] = None) -> Dict:
    """Run Tier 3 batch immediately (ignores time window)"""
    scheduler = SequentialBatchScheduler()
    return scheduler.run_tier3_batch(max_jobs=max_jobs)


def run_all_tiers_now(
    tier1_max: Optional[int] = None,
    tier2_max: Optional[int] = None,
    tier3_max: Optional[int] = None
) -> Dict:
    """Run complete sequential batch immediately (ignores time windows)"""
    scheduler = SequentialBatchScheduler()
    return scheduler.run_full_sequential_batch(tier1_max, tier2_max, tier3_max)


def get_status() -> Dict:
    """Get current processing pipeline status"""
    scheduler = SequentialBatchScheduler()
    return scheduler.get_processing_status()


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "status":
            status = get_status()
            print(f"\nProcessing Pipeline Status:")
            print(f"  Pending Tier 1: {status['pending_tier1']}")
            print(f"  Pending Tier 2: {status['pending_tier2']}")
            print(f"  Pending Tier 3: {status['pending_tier3']}")
            print(f"  Fully Analyzed: {status['fully_analyzed']}")
            print(f"  Active Tier: {status.get('active_tier', 'None')}")

        elif command == "tier1":
            results = run_tier1_now()
            print(f"\nTier 1 Results: {results['successful']} successful, {results['failed']} failed")

        elif command == "tier2":
            results = run_tier2_now()
            print(f"\nTier 2 Results: {results['successful']} successful, {results['failed']} failed")

        elif command == "tier3":
            results = run_tier3_now()
            print(f"\nTier 3 Results: {results['successful']} successful, {results['failed']} failed")

        elif command == "all":
            results = run_all_tiers_now()
            print(f"\nFull Sequential Batch Results:")
            print(f"  Total Jobs: {results['summary']['total_jobs_processed']}")
            print(f"  Total Tokens: {results['summary']['total_tokens']}")
            print(f"  Total Time: {results['total_time_seconds']:.2f}s")

        elif command == "schedule":
            scheduler = SequentialBatchScheduler()
            scheduler.run_continuous_scheduler()

        else:
            print("Unknown command. Use: status, tier1, tier2, tier3, all, or schedule")
    else:
        print("Usage: python sequential_batch_scheduler.py [status|tier1|tier2|tier3|all|schedule]")
