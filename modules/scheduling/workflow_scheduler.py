"""
Workflow Scheduler for Automated Job Application System
Handles scheduling of job scraping, AI analysis, and application sending
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowPhase(Enum):
    """Phases of the job application workflow"""

    SCRAPING = "job_scraping"
    AI_ANALYSIS = "ai_analysis"
    ELIGIBILITY_CHECK = "eligibility_check"
    APPLICATION_SENDING = "application_sending"


class ScheduleConfiguration:
    """Configuration for workflow scheduling"""

    # Mountain Time Zone schedules
    JOB_SCRAPING_SCHEDULE = {
        "frequency": "every_second_day",
        "time": "09:30",
        "timezone": "America/Denver",  # Mountain Time
        "description": "Job scraping every second day at 9:30 AM MT",
    }

    AI_ANALYSIS_SCHEDULE = {
        "frequency": "following_night",
        "time": "23:00",  # 11:00 PM MT for low demand
        "timezone": "America/Denver",
        "description": "AI analysis following night of scraping at 11:00 PM MT",
    }

    APPLICATION_SENDING_SCHEDULE = {
        "frequency": "following_morning",
        "time": "10:15",
        "timezone": "America/Denver",
        "description": "Application sending morning after analysis at 10:15 AM MT",
    }


class WorkflowScheduler:
    """
    Manages the automated workflow scheduling for job application system

    Workflow sequence:
    1. Job Scraping: Every 2nd day at 9:30 AM MT
    2. AI Analysis: Following night at 11:00 PM MT (low demand period)
    3. Eligibility Check: Between analysis and sending (future feature)
    4. Application Sending: Following morning at 10:15 AM MT
    """

    def __init__(self):
        self.config = ScheduleConfiguration()
        self.current_workflow_state = {}

    def get_next_scheduled_phase(self, current_phase: Optional[WorkflowPhase] = None) -> Dict:
        """
        Calculate next scheduled workflow phase

        Args:
            current_phase: Current workflow phase (None for next scraping)

        Returns:
            Dictionary with next phase information
        """

        now = datetime.now()

        if current_phase is None or current_phase == WorkflowPhase.APPLICATION_SENDING:
            # Calculate next scraping (every second day)
            next_scraping = self._calculate_next_scraping_date(now)
            return {
                "phase": WorkflowPhase.SCRAPING,
                "scheduled_time": next_scraping,
                "description": self.config.JOB_SCRAPING_SCHEDULE["description"],
            }

        elif current_phase == WorkflowPhase.SCRAPING:
            # AI Analysis following night
            next_analysis = self._calculate_same_day_evening(now)
            return {
                "phase": WorkflowPhase.AI_ANALYSIS,
                "scheduled_time": next_analysis,
                "description": self.config.AI_ANALYSIS_SCHEDULE["description"],
            }

        elif current_phase == WorkflowPhase.AI_ANALYSIS:
            # Application sending following morning
            next_sending = self._calculate_next_morning(now)
            return {
                "phase": WorkflowPhase.APPLICATION_SENDING,
                "scheduled_time": next_sending,
                "description": self.config.APPLICATION_SENDING_SCHEDULE["description"],
            }

        else:
            raise ValueError(f"Unknown workflow phase: {current_phase}")

    def _calculate_next_scraping_date(self, from_date: datetime) -> datetime:
        """Calculate next job scraping date (every second day at 9:30 AM MT)"""

        # Start from tomorrow and check for valid scraping dates
        next_date = from_date.replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)

        # For every second day logic, we can use day number modulo
        # This assumes we start scraping on specific days (e.g., odd days)
        while next_date.day % 2 == 0:  # Skip even days
            next_date += timedelta(days=1)

        return next_date

    def _calculate_same_day_evening(self, from_date: datetime) -> datetime:
        """Calculate AI analysis time (same day at 11:00 PM MT)"""
        return from_date.replace(hour=23, minute=0, second=0, microsecond=0)

    def _calculate_next_morning(self, from_date: datetime) -> datetime:
        """Calculate application sending time (next day at 10:15 AM MT)"""
        next_morning = from_date.replace(hour=10, minute=15, second=0, microsecond=0) + timedelta(days=1)
        return next_morning

    def get_workflow_status(self) -> Dict:
        """Get current workflow scheduling status"""

        now = datetime.now()
        next_phase = self.get_next_scheduled_phase()

        return {
            "current_time": now.isoformat(),
            "timezone": "America/Denver",
            "next_phase": {
                "phase": next_phase["phase"].value,
                "scheduled_time": next_phase["scheduled_time"].isoformat(),
                "description": next_phase["description"],
                "time_until": str(next_phase["scheduled_time"] - now),
            },
            "workflow_phases": [
                {"phase": WorkflowPhase.SCRAPING.value, "schedule": self.config.JOB_SCRAPING_SCHEDULE},
                {"phase": WorkflowPhase.AI_ANALYSIS.value, "schedule": self.config.AI_ANALYSIS_SCHEDULE},
                {
                    "phase": WorkflowPhase.APPLICATION_SENDING.value,
                    "schedule": self.config.APPLICATION_SENDING_SCHEDULE,
                },
            ],
        }

    def is_phase_ready(self, phase: WorkflowPhase, last_run: Optional[datetime] = None) -> bool:
        """
        Check if a workflow phase is ready to run

        Args:
            phase: Workflow phase to check
            last_run: When this phase was last executed

        Returns:
            True if phase is ready to run
        """

        now = datetime.now()

        if phase == WorkflowPhase.SCRAPING:
            # Check if it's a scraping day and time
            if now.hour == 9 and now.minute >= 30:
                if last_run is None:
                    return True
                # Check if last run was more than 1 day ago
                return (now - last_run).days >= 1

        elif phase == WorkflowPhase.AI_ANALYSIS:
            # Check if it's analysis time (11 PM)
            if now.hour == 23:
                if last_run is None:
                    return True
                return (now - last_run).days >= 1

        elif phase == WorkflowPhase.APPLICATION_SENDING:
            # Check if it's sending time (10:15 AM)
            if now.hour == 10 and now.minute >= 15:
                if last_run is None:
                    return True
                return (now - last_run).days >= 1

        return False


def get_scheduler() -> WorkflowScheduler:
    """Get workflow scheduler instance"""
    return WorkflowScheduler()
