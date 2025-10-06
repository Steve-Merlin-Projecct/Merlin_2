#!/usr/bin/env python3
"""
Failure Recovery Manager - Step 2.3 Implementation

Comprehensive error handling and recovery system for automated job applications.
Implements intelligent retry logic, workflow checkpoints, and data consistency validation.

Features:
- Automatic recovery from transient failures
- Workflow checkpoint and resume capabilities
- Error categorization and specific handling strategies
- Data consistency validation and correction
- Comprehensive audit logging for troubleshooting
"""

import logging
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from contextlib import contextmanager
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Import system components
from modules.database.database_manager import DatabaseManager


class FailureType(Enum):
    """Classification of different failure types for targeted recovery"""

    # Network and API failures
    NETWORK_TIMEOUT = "network_timeout"
    API_RATE_LIMIT = "api_rate_limit"
    API_QUOTA_EXCEEDED = "api_quota_exceeded"
    CONNECTION_RESET = "connection_reset"

    # Database failures
    DATABASE_CONNECTION = "database_connection"
    FOREIGN_KEY_VIOLATION = "foreign_key_violation"
    UNIQUE_CONSTRAINT = "unique_constraint"
    DEADLOCK = "deadlock"

    # Document generation failures
    TEMPLATE_NOT_FOUND = "template_not_found"
    STORAGE_FULL = "storage_full"
    DOCUMENT_CORRUPTION = "document_corruption"

    # Email failures
    EMAIL_AUTH_FAILURE = "email_auth_failure"
    EMAIL_QUOTA_EXCEEDED = "email_quota_exceeded"
    INVALID_RECIPIENT = "invalid_recipient"

    # Workflow failures
    WORKFLOW_TIMEOUT = "workflow_timeout"
    DATA_INCONSISTENCY = "data_inconsistency"
    BUSINESS_LOGIC_ERROR = "business_logic_error"

    # System failures
    MEMORY_ERROR = "memory_error"
    DISK_FULL = "disk_full"
    PERMISSION_DENIED = "permission_denied"

    # Unknown failures
    UNKNOWN = "unknown"


class RetryStrategy:
    """Configurable retry strategy for different failure types"""

    def __init__(
        self, max_attempts: int = 3, base_delay: float = 1.0, exponential_backoff: bool = True, max_delay: float = 60.0
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.exponential_backoff = exponential_backoff
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        if not self.exponential_backoff:
            return self.base_delay

        delay = self.base_delay * (2 ** (attempt - 1))
        return min(delay, self.max_delay)


class WorkflowCheckpoint:
    """Represents a workflow checkpoint for recovery"""

    def __init__(self, checkpoint_id: str, workflow_id: str, stage: str, data: Dict, timestamp: datetime):
        self.checkpoint_id = checkpoint_id
        self.workflow_id = workflow_id
        self.stage = stage
        self.data = data
        self.timestamp = timestamp

    def to_dict(self) -> Dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "workflow_id": self.workflow_id,
            "stage": self.stage,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


class FailureRecoveryManager:
    """
    Central coordinator for error handling and recovery operations

    Manages the complete failure recovery workflow including:
    - Error classification and strategy selection
    - Retry execution with intelligent backoff
    - Workflow checkpoint management
    - Data consistency validation
    - Comprehensive audit logging
    """

    def __init__(self):
        """Initialize the failure recovery manager"""
        self.db_url = os.environ.get("DATABASE_URL")
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)

        # Initialize failure recovery database tables
        self._initialize_recovery_tables()

        # Configure retry strategies for different failure types
        self.retry_strategies = self._configure_retry_strategies()

        self.logger.info("FailureRecoveryManager initialized for Step 2.3 implementation")

    def _initialize_recovery_tables(self):
        """Create necessary tables for failure recovery tracking"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Create failure_logs table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS failure_logs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        failure_type VARCHAR(100) NOT NULL,
                        operation_name VARCHAR(200) NOT NULL,
                        workflow_id UUID,
                        error_message TEXT,
                        error_details JSONB,
                        recovery_attempts INTEGER DEFAULT 0,
                        recovery_successful BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        resolved_at TIMESTAMP
                    )
                """
                )

                # Create workflow_checkpoints table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        checkpoint_id VARCHAR(100) UNIQUE NOT NULL,
                        workflow_id UUID NOT NULL,
                        stage VARCHAR(100) NOT NULL,
                        checkpoint_data JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """
                )

                # Create recovery_statistics table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS recovery_statistics (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        date DATE DEFAULT CURRENT_DATE,
                        failure_type VARCHAR(100),
                        total_failures INTEGER DEFAULT 0,
                        successful_recoveries INTEGER DEFAULT 0,
                        failed_recoveries INTEGER DEFAULT 0,
                        average_recovery_time DECIMAL(10,2),
                        created_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(date, failure_type)
                    )
                """
                )

                conn.commit()

    def _configure_retry_strategies(self) -> Dict[FailureType, RetryStrategy]:
        """Configure retry strategies for different failure types"""
        return {
            # Network failures - aggressive retry
            FailureType.NETWORK_TIMEOUT: RetryStrategy(max_attempts=5, base_delay=2.0, max_delay=120.0),
            FailureType.CONNECTION_RESET: RetryStrategy(max_attempts=4, base_delay=1.5, max_delay=60.0),
            # API rate limiting - respectful retry
            FailureType.API_RATE_LIMIT: RetryStrategy(max_attempts=3, base_delay=30.0, max_delay=300.0),
            FailureType.API_QUOTA_EXCEEDED: RetryStrategy(max_attempts=2, base_delay=3600.0, max_delay=7200.0),
            # Database failures - moderate retry
            FailureType.DATABASE_CONNECTION: RetryStrategy(max_attempts=4, base_delay=2.0, max_delay=60.0),
            FailureType.DEADLOCK: RetryStrategy(max_attempts=3, base_delay=0.5, max_delay=10.0),
            FailureType.FOREIGN_KEY_VIOLATION: RetryStrategy(max_attempts=2, base_delay=1.0, max_delay=5.0),
            # Document generation - limited retry
            FailureType.TEMPLATE_NOT_FOUND: RetryStrategy(max_attempts=2, base_delay=1.0, max_delay=5.0),
            FailureType.DOCUMENT_CORRUPTION: RetryStrategy(max_attempts=2, base_delay=2.0, max_delay=10.0),
            # Email failures - conservative retry
            FailureType.EMAIL_AUTH_FAILURE: RetryStrategy(max_attempts=2, base_delay=5.0, max_delay=30.0),
            FailureType.EMAIL_QUOTA_EXCEEDED: RetryStrategy(max_attempts=1, base_delay=3600.0, max_delay=3600.0),
            # System failures - minimal retry
            FailureType.MEMORY_ERROR: RetryStrategy(max_attempts=1, base_delay=10.0, max_delay=10.0),
            FailureType.DISK_FULL: RetryStrategy(max_attempts=1, base_delay=60.0, max_delay=60.0),
            # Default strategy
            FailureType.UNKNOWN: RetryStrategy(max_attempts=2, base_delay=2.0, max_delay=30.0),
        }

    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            conn.autocommit = False
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error in failure recovery: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_with_recovery(
        self, operation_func: Callable, operation_name: str, workflow_id: Optional[str] = None, **kwargs
    ) -> Any:
        """
        Execute an operation with automatic failure recovery and retry logic

        Args:
            operation_func: Function to execute
            operation_name: Human-readable operation name for logging
            workflow_id: Optional workflow ID for tracking
            **kwargs: Arguments to pass to operation_func

        Returns:
            Any: Result of successful operation execution

        Raises:
            Exception: If operation fails after all retry attempts
        """
        failure_id = str(uuid.uuid4())
        start_time = datetime.now()

        for attempt in range(1, 6):  # Maximum 5 attempts across all strategies
            try:
                # Log attempt
                self.logger.info(f"Executing {operation_name} (attempt {attempt})")

                # Execute operation
                result = operation_func(**kwargs)

                # Log success
                if attempt > 1:
                    self.logger.info(f"Operation {operation_name} succeeded on attempt {attempt}")
                    self._log_recovery_success(failure_id, operation_name, workflow_id, attempt, start_time)

                return result

            except Exception as e:
                # Classify the failure
                failure_type = self._classify_error(e)

                # Log the failure
                self._log_failure(failure_id, failure_type, operation_name, workflow_id, e, attempt)

                # Get retry strategy
                strategy = self.retry_strategies.get(failure_type, self.retry_strategies[FailureType.UNKNOWN])

                # Check if we should retry
                if attempt >= strategy.max_attempts:
                    self.logger.error(f"Operation {operation_name} failed after {attempt} attempts")
                    self._log_recovery_failure(failure_id, operation_name, workflow_id, attempt, start_time)
                    raise e

                # Calculate delay and wait
                delay = strategy.get_delay(attempt)
                self.logger.warning(f"Retrying {operation_name} in {delay:.1f} seconds (attempt {attempt + 1})")
                time.sleep(delay)

        # This should never be reached due to the raise in the loop
        raise Exception(f"Unexpected error in retry logic for {operation_name}")

    def _classify_error(self, error: Exception) -> FailureType:
        """Classify error into appropriate failure type"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()

        # Network and connection errors
        if "timeout" in error_str or "timed out" in error_str:
            return FailureType.NETWORK_TIMEOUT
        if "connection reset" in error_str or "connectionreseterror" in error_type:
            return FailureType.CONNECTION_RESET
        if "rate limit" in error_str or "too many requests" in error_str:
            return FailureType.API_RATE_LIMIT
        if "quota exceeded" in error_str or "quota limit" in error_str:
            return FailureType.API_QUOTA_EXCEEDED

        # Database errors
        if "connection" in error_str and ("database" in error_str or "postgres" in error_str):
            return FailureType.DATABASE_CONNECTION
        if "foreign key" in error_str or "violates foreign key constraint" in error_str:
            return FailureType.FOREIGN_KEY_VIOLATION
        if "unique constraint" in error_str or "duplicate key" in error_str:
            return FailureType.UNIQUE_CONSTRAINT
        if "deadlock" in error_str:
            return FailureType.DEADLOCK

        # Document generation errors
        if "template not found" in error_str or "filenotfounderror" in error_type:
            return FailureType.TEMPLATE_NOT_FOUND
        if "no space left" in error_str or "disk full" in error_str:
            return FailureType.STORAGE_FULL

        # Email errors
        if "authentication" in error_str and "email" in error_str:
            return FailureType.EMAIL_AUTH_FAILURE
        if "invalid recipient" in error_str or "invalid email" in error_str:
            return FailureType.INVALID_RECIPIENT

        # System errors
        if "memoryerror" in error_type or "out of memory" in error_str:
            return FailureType.MEMORY_ERROR
        if "permission denied" in error_str or "permissionerror" in error_type:
            return FailureType.PERMISSION_DENIED

        # Default classification
        return FailureType.UNKNOWN

    def _log_failure(
        self,
        failure_id: str,
        failure_type: FailureType,
        operation_name: str,
        workflow_id: Optional[str],
        error: Exception,
        attempt: int,
    ):
        """Log failure details to database"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO failure_logs (
                            id, failure_type, operation_name, workflow_id, 
                            error_message, error_details, recovery_attempts
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            recovery_attempts = %s,
                            error_details = %s
                    """,
                        (
                            failure_id,
                            failure_type.value,
                            operation_name,
                            workflow_id,
                            str(error),
                            json.dumps(
                                {
                                    "error_type": type(error).__name__,
                                    "attempt": attempt,
                                    "timestamp": datetime.now().isoformat(),
                                }
                            ),
                            attempt,
                            attempt,
                            json.dumps(
                                {
                                    "error_type": type(error).__name__,
                                    "attempt": attempt,
                                    "timestamp": datetime.now().isoformat(),
                                }
                            ),
                        ),
                    )
                    conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log failure: {e}")

    def _log_recovery_success(
        self, failure_id: str, operation_name: str, workflow_id: Optional[str], attempts: int, start_time: datetime
    ):
        """Log successful recovery"""
        try:
            recovery_time = (datetime.now() - start_time).total_seconds()

            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Update failure log
                    cursor.execute(
                        """
                        UPDATE failure_logs 
                        SET recovery_successful = TRUE, resolved_at = NOW()
                        WHERE id = %s
                    """,
                        (failure_id,),
                    )

                    # Update statistics
                    cursor.execute(
                        """
                        INSERT INTO recovery_statistics (
                            date, failure_type, total_failures, successful_recoveries, average_recovery_time
                        ) 
                        SELECT 
                            CURRENT_DATE, 
                            failure_type, 
                            1, 
                            1, 
                            %s
                        FROM failure_logs WHERE id = %s
                        ON CONFLICT (date, failure_type) DO UPDATE SET
                            total_failures = recovery_statistics.total_failures + 1,
                            successful_recoveries = recovery_statistics.successful_recoveries + 1,
                            average_recovery_time = (recovery_statistics.average_recovery_time + %s) / 2
                    """,
                        (recovery_time, failure_id, recovery_time),
                    )

                    conn.commit()

            self.logger.info(
                f"Recovery successful for {operation_name} after {attempts} attempts ({recovery_time:.2f}s)"
            )

        except Exception as e:
            self.logger.error(f"Failed to log recovery success: {e}")

    def _log_recovery_failure(
        self, failure_id: str, operation_name: str, workflow_id: Optional[str], attempts: int, start_time: datetime
    ):
        """Log failed recovery attempt"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Update statistics
                    cursor.execute(
                        """
                        INSERT INTO recovery_statistics (
                            date, failure_type, total_failures, failed_recoveries
                        ) 
                        SELECT 
                            CURRENT_DATE, 
                            failure_type, 
                            1, 
                            1
                        FROM failure_logs WHERE id = %s
                        ON CONFLICT (date, failure_type) DO UPDATE SET
                            total_failures = recovery_statistics.total_failures + 1,
                            failed_recoveries = recovery_statistics.failed_recoveries + 1
                    """,
                        (failure_id,),
                    )

                    conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to log recovery failure: {e}")

    def create_checkpoint(self, workflow_id: str, stage: str, data: Dict) -> str:
        """
        Create a workflow checkpoint for recovery purposes

        Args:
            workflow_id: Unique workflow identifier
            stage: Current workflow stage
            data: Checkpoint data to preserve

        Returns:
            str: Checkpoint ID
        """
        checkpoint_id = f"{workflow_id}_{stage}_{int(time.time())}"

        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO workflow_checkpoints (
                            checkpoint_id, workflow_id, stage, checkpoint_data
                        ) VALUES (%s, %s, %s, %s)
                    """,
                        (checkpoint_id, workflow_id, stage, json.dumps(data)),
                    )
                    conn.commit()

            self.logger.info(f"Checkpoint created: {checkpoint_id} for stage {stage}")
            return checkpoint_id

        except Exception as e:
            self.logger.error(f"Failed to create checkpoint: {e}")
            raise

    def get_latest_checkpoint(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        """
        Retrieve the latest checkpoint for a workflow

        Args:
            workflow_id: Workflow identifier

        Returns:
            WorkflowCheckpoint: Latest checkpoint or None if not found
        """
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT checkpoint_id, workflow_id, stage, checkpoint_data, created_at
                        FROM workflow_checkpoints
                        WHERE workflow_id = %s
                        ORDER BY created_at DESC
                        LIMIT 1
                    """,
                        (workflow_id,),
                    )

                    row = cursor.fetchone()
                    if row:
                        return WorkflowCheckpoint(
                            checkpoint_id=row["checkpoint_id"],
                            workflow_id=row["workflow_id"],
                            stage=row["stage"],
                            data=row["checkpoint_data"],
                            timestamp=row["created_at"],
                        )

            return None

        except Exception as e:
            self.logger.error(f"Failed to retrieve checkpoint: {e}")
            return None

    def validate_data_consistency(self, workflow_id: str) -> Dict[str, Any]:
        """
        Validate data consistency across workflow stages

        Args:
            workflow_id: Workflow identifier

        Returns:
            Dict: Validation results and any inconsistencies found
        """
        validation_results = {"consistent": True, "issues": [], "corrections_applied": []}

        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                    # Check for orphaned job applications
                    cursor.execute(
                        """
                        SELECT ja.id, ja.job_id
                        FROM job_applications ja
                        LEFT JOIN jobs j ON ja.job_id = j.id
                        WHERE j.id IS NULL
                    """
                    )

                    orphaned_applications = cursor.fetchall()
                    if orphaned_applications:
                        validation_results["consistent"] = False
                        validation_results["issues"].append(
                            {
                                "type": "orphaned_job_applications",
                                "count": len(orphaned_applications),
                                "description": "Job applications referencing non-existent jobs",
                            }
                        )

                    # Check for incomplete workflow states
                    cursor.execute(
                        """
                        SELECT j.id, j.job_title, j.analysis_completed, ja.application_status
                        FROM jobs j
                        LEFT JOIN job_applications ja ON j.id = ja.job_id
                        WHERE j.analysis_completed = TRUE 
                        AND j.eligibility_flag = TRUE
                        AND (ja.id IS NULL OR ja.application_status IS NULL)
                    """
                    )

                    incomplete_workflows = cursor.fetchall()
                    if incomplete_workflows:
                        validation_results["issues"].append(
                            {
                                "type": "incomplete_workflows",
                                "count": len(incomplete_workflows),
                                "description": "Eligible jobs without application records",
                            }
                        )

            self.logger.info(f"Data consistency validation completed for workflow {workflow_id}")
            return validation_results

        except Exception as e:
            self.logger.error(f"Data consistency validation failed: {e}")
            validation_results["consistent"] = False
            validation_results["issues"].append(
                {"type": "validation_error", "description": f"Validation process failed: {str(e)}"}
            )
            return validation_results

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive recovery statistics

        Returns:
            Dict: Recovery performance metrics and statistics
        """
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                    # Overall recovery statistics
                    cursor.execute(
                        """
                        SELECT 
                            COUNT(*) as total_failures,
                            SUM(CASE WHEN recovery_successful THEN 1 ELSE 0 END) as successful_recoveries,
                            ROUND(AVG(recovery_attempts), 2) as avg_attempts,
                            failure_type
                        FROM failure_logs
                        WHERE created_at >= NOW() - INTERVAL '7 days'
                        GROUP BY failure_type
                        ORDER BY total_failures DESC
                    """
                    )

                    failure_stats = cursor.fetchall()

                    # Recovery trends
                    cursor.execute(
                        """
                        SELECT 
                            date,
                            SUM(total_failures) as daily_failures,
                            SUM(successful_recoveries) as daily_recoveries,
                            ROUND(AVG(average_recovery_time), 2) as avg_recovery_time
                        FROM recovery_statistics
                        WHERE date >= CURRENT_DATE - INTERVAL '7 days'
                        GROUP BY date
                        ORDER BY date DESC
                    """
                    )

                    trend_stats = cursor.fetchall()

            return {
                "failure_breakdown": [dict(row) for row in failure_stats],
                "daily_trends": [dict(row) for row in trend_stats],
                "summary": {
                    "total_failures": sum(row["total_failures"] for row in failure_stats),
                    "total_recoveries": sum(row["successful_recoveries"] for row in failure_stats),
                    "overall_success_rate": sum(row["successful_recoveries"] for row in failure_stats)
                    / max(sum(row["total_failures"] for row in failure_stats), 1)
                    * 100,
                },
            }

        except Exception as e:
            self.logger.error(f"Failed to get recovery statistics: {e}")
            return {"error": str(e)}


def main():
    """Test the FailureRecoveryManager implementation"""
    print("Step 2.3: Failure Recovery and Retry Mechanisms Test")
    print("=" * 60)

    try:
        recovery_manager = FailureRecoveryManager()

        # Test error classification
        print("\n🔍 Testing error classification...")
        test_errors = [
            ConnectionResetError("Connection reset by peer"),
            Exception("Template not found: test.docx"),
            Exception("Foreign key violation"),
            TimeoutError("Request timed out"),
        ]

        for error in test_errors:
            failure_type = recovery_manager._classify_error(error)
            print(f"   {type(error).__name__}: {failure_type.value}")

        # Test checkpoint creation
        print("\n📍 Testing checkpoint creation...")
        test_workflow_id = str(uuid.uuid4())
        checkpoint_id = recovery_manager.create_checkpoint(
            workflow_id=test_workflow_id, stage="job_discovery", data={"jobs_found": 5, "last_processed": "job_123"}
        )
        print(f"   Checkpoint created: {checkpoint_id}")

        # Test checkpoint retrieval
        checkpoint = recovery_manager.get_latest_checkpoint(test_workflow_id)
        if checkpoint:
            print(f"   Checkpoint retrieved: Stage {checkpoint.stage}, Data: {checkpoint.data}")

        # Test data consistency validation
        print("\n✅ Testing data consistency validation...")
        validation = recovery_manager.validate_data_consistency(test_workflow_id)
        print(f"   Consistency check: {'PASS' if validation['consistent'] else 'ISSUES FOUND'}")
        if validation["issues"]:
            for issue in validation["issues"]:
                print(f"   - {issue['type']}: {issue['description']}")

        # Test recovery statistics
        print("\n📊 Testing recovery statistics...")
        stats = recovery_manager.get_recovery_statistics()
        if "summary" in stats:
            summary = stats["summary"]
            print(f"   Total failures: {summary['total_failures']}")
            print(f"   Successful recoveries: {summary['total_recoveries']}")
            print(f"   Success rate: {summary['overall_success_rate']:.1f}%")

        print(f"\n✅ Step 2.3 Failure Recovery and Retry Mechanisms implementation complete!")

    except Exception as e:
        print(f"\n❌ Failure recovery test failed: {e}")
        print("Check database connectivity and permissions")


if __name__ == "__main__":
    main()
