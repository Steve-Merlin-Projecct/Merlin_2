#!/usr/bin/env python3
"""
Scheduler for Copywriting Evaluator System

Handles scheduled processing tasks for production mode including twice-weekly
automated processing runs and maintenance tasks.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import threading
import time

# Database integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

logger = logging.getLogger(__name__)

class ScheduleType(Enum):
    """Types of scheduled tasks"""
    TWICE_WEEKLY = "twice_weekly"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"

@dataclass
class ScheduledTask:
    """Definition of a scheduled task"""
    task_id: str
    name: str
    schedule_type: ScheduleType
    target_function: Callable
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    error_count: int = 0
    custom_schedule: Optional[str] = None  # For cron-like expressions
    max_retries: int = 3

class PipelineScheduler:
    """
    Production mode scheduler for automated pipeline processing
    
    Features:
    - Twice-weekly processing schedule (Tuesday and Friday)
    - Configurable processing windows
    - Automatic retry on failures
    - Task monitoring and logging
    - Thread-safe execution
    """
    
    def __init__(self):
        """Initialize scheduler"""
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_thread = None
        
        # Default schedule: Tuesdays and Fridays at 2 AM
        self.production_schedule = {
            'days': [1, 4],  # 0=Monday, 1=Tuesday, 4=Friday
            'hour': 2,
            'minute': 0
        }
        
        logger.info("Pipeline scheduler initialized")
    
    def add_task(self, task: ScheduledTask) -> None:
        """
        Add a scheduled task
        
        Args:
            task: ScheduledTask configuration
        """
        self.tasks[task.task_id] = task
        self._calculate_next_run(task)
        logger.info(f"Added scheduled task: {task.name} ({task.task_id})")
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a scheduled task
        
        Args:
            task_id: Task identifier to remove
            
        Returns:
            True if task was removed, False if not found
        """
        if task_id in self.tasks:
            task_name = self.tasks[task_id].name
            del self.tasks[task_id]
            logger.info(f"Removed scheduled task: {task_name} ({task_id})")
            return True
        return False
    
    def enable_task(self, task_id: str) -> bool:
        """Enable a scheduled task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            self._calculate_next_run(self.tasks[task_id])
            logger.info(f"Enabled task: {task_id}")
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """Disable a scheduled task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            logger.info(f"Disabled task: {task_id}")
            return True
        return False
    
    def _calculate_next_run(self, task: ScheduledTask) -> None:
        """Calculate next run time for a task"""
        now = datetime.now()
        
        if task.schedule_type == ScheduleType.TWICE_WEEKLY:
            # Find next Tuesday or Friday at scheduled time
            next_run = None
            for days_ahead in range(7):  # Check next 7 days
                check_date = now + timedelta(days=days_ahead)
                if check_date.weekday() in self.production_schedule['days']:
                    scheduled_time = check_date.replace(
                        hour=self.production_schedule['hour'],
                        minute=self.production_schedule['minute'],
                        second=0,
                        microsecond=0
                    )
                    if scheduled_time > now:
                        next_run = scheduled_time
                        break
            
            if not next_run:
                # If no suitable day this week, get next Tuesday
                days_until_tuesday = (1 - now.weekday()) % 7
                if days_until_tuesday == 0:
                    days_until_tuesday = 7
                next_run = (now + timedelta(days=days_until_tuesday)).replace(
                    hour=self.production_schedule['hour'],
                    minute=self.production_schedule['minute'],
                    second=0,
                    microsecond=0
                )
            
            task.next_run = next_run
            
        elif task.schedule_type == ScheduleType.DAILY:
            # Next day at same time
            next_run = (now + timedelta(days=1)).replace(second=0, microsecond=0)
            task.next_run = next_run
            
        elif task.schedule_type == ScheduleType.WEEKLY:
            # Next week at same time
            next_run = (now + timedelta(weeks=1)).replace(second=0, microsecond=0)
            task.next_run = next_run
        
        logger.debug(f"Next run for {task.task_id}: {task.next_run}")
    
    def start(self) -> None:
        """Start the scheduler in a background thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Pipeline scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        logger.info("Pipeline scheduler stopped")
    
    def _run_scheduler(self) -> None:
        """Main scheduler loop (runs in background thread)"""
        logger.info("Scheduler thread started")
        
        while self.running:
            try:
                self._check_and_run_tasks()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def _check_and_run_tasks(self) -> None:
        """Check for tasks that need to run and execute them"""
        now = datetime.now()
        
        for task in self.tasks.values():
            if not task.enabled:
                continue
            
            if task.next_run and now >= task.next_run:
                logger.info(f"Running scheduled task: {task.name} ({task.task_id})")
                self._execute_task(task)
    
    def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a scheduled task with error handling and retry logic"""
        try:
            # Update last run time
            task.last_run = datetime.now()
            
            # Execute the task function
            if asyncio.iscoroutinefunction(task.target_function):
                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(task.target_function())
                finally:
                    loop.close()
            else:
                # Run sync function
                result = task.target_function()
            
            # Update success metrics
            task.run_count += 1
            logger.info(f"Task {task.task_id} completed successfully")
            
            # Calculate next run time
            self._calculate_next_run(task)
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {str(e)}")
            task.error_count += 1
            
            # Retry logic
            if task.error_count < task.max_retries:
                logger.info(f"Scheduling retry for {task.task_id} in 1 hour")
                task.next_run = datetime.now() + timedelta(hours=1)
            else:
                logger.error(f"Task {task.task_id} exceeded max retries, scheduling next regular run")
                self._calculate_next_run(task)
                task.error_count = 0  # Reset for next cycle
    
    def get_task_status(self, task_id: Optional[str] = None) -> Dict:
        """
        Get status of scheduled tasks
        
        Args:
            task_id: Optional specific task ID, if None returns all tasks
            
        Returns:
            Dictionary with task status information
        """
        if task_id:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                return {
                    'task_id': task.task_id,
                    'name': task.name,
                    'enabled': task.enabled,
                    'last_run': task.last_run.isoformat() if task.last_run else None,
                    'next_run': task.next_run.isoformat() if task.next_run else None,
                    'run_count': task.run_count,
                    'error_count': task.error_count,
                    'schedule_type': task.schedule_type.value
                }
            else:
                return {'error': f'Task {task_id} not found'}
        
        # Return all tasks
        tasks_status = {}
        for tid, task in self.tasks.items():
            tasks_status[tid] = {
                'name': task.name,
                'enabled': task.enabled,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'next_run': task.next_run.isoformat() if task.next_run else None,
                'run_count': task.run_count,
                'error_count': task.error_count,
                'schedule_type': task.schedule_type.value
            }
        
        return {
            'scheduler_running': self.running,
            'total_tasks': len(self.tasks),
            'enabled_tasks': sum(1 for t in self.tasks.values() if t.enabled),
            'tasks': tasks_status
        }
    
    def force_run_task(self, task_id: str) -> Dict:
        """
        Force immediate execution of a scheduled task
        
        Args:
            task_id: Task to execute immediately
            
        Returns:
            Execution result dictionary
        """
        if task_id not in self.tasks:
            return {'success': False, 'error': f'Task {task_id} not found'}
        
        task = self.tasks[task_id]
        
        try:
            logger.info(f"Force executing task: {task.name} ({task_id})")
            self._execute_task(task)
            return {
                'success': True,
                'message': f'Task {task_id} executed successfully',
                'execution_time': task.last_run.isoformat() if task.last_run else None
            }
        except Exception as e:
            logger.error(f"Force execution of {task_id} failed: {str(e)}")
            return {'success': False, 'error': str(e)}

# Global scheduler instance for production mode
_production_scheduler = None

def get_production_scheduler() -> PipelineScheduler:
    """Get or create the global production scheduler instance"""
    global _production_scheduler
    if _production_scheduler is None:
        _production_scheduler = PipelineScheduler()
    return _production_scheduler

def setup_production_schedule(pipeline_processor_class) -> None:
    """
    Set up the default production processing schedule
    
    Args:
        pipeline_processor_class: The CopywritingEvaluatorPipeline class for scheduled execution
    """
    scheduler = get_production_scheduler()
    
    async def run_full_pipeline():
        """Async wrapper for running the full pipeline processing"""
        from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline, PipelineConfig, ProcessingMode
        
        # Create production mode pipeline
        config = PipelineConfig(mode=ProcessingMode.PRODUCTION)
        pipeline = CopywritingEvaluatorPipeline(config)
        
        try:
            # Process both sentence bank tables
            cover_letter_stats = await pipeline.process_sentences(table_name='sentence_bank_cover_letter')
            resume_stats = await pipeline.process_sentences(table_name='sentence_bank_resume')
            
            logger.info(f"Scheduled processing complete - Cover letters: {cover_letter_stats.processed_sentences}, "
                       f"Resumes: {resume_stats.processed_sentences}")
            
            return {
                'cover_letter_stats': cover_letter_stats,
                'resume_stats': resume_stats
            }
            
        except Exception as e:
            logger.error(f"Scheduled pipeline processing failed: {str(e)}")
            raise
    
    # Create the scheduled task
    processing_task = ScheduledTask(
        task_id="pipeline_processing",
        name="Twice-Weekly Pipeline Processing",
        schedule_type=ScheduleType.TWICE_WEEKLY,
        target_function=run_full_pipeline,
        enabled=True
    )
    
    scheduler.add_task(processing_task)
    
    if not scheduler.running:
        scheduler.start()
    
    logger.info("Production processing schedule configured (Tuesdays and Fridays at 2:00 AM)")