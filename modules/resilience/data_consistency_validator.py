#!/usr/bin/env python3
"""
Data Consistency Validator - Step 2.3 Implementation

Validates and maintains data consistency across workflow stages.
Detects inconsistencies, provides automatic corrections, and ensures
data integrity throughout the automated job application process.

Features:
- Cross-table consistency validation
- Orphaned record detection and cleanup
- Workflow state integrity checks
- Automatic data correction where possible
- Comprehensive consistency reporting
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
import os


class ConsistencyIssue:
    """Represents a data consistency issue"""

    def __init__(
        self,
        issue_type: str,
        severity: str,
        description: str,
        affected_records: List[str],
        correctable: bool = False,
        correction_action: Optional[str] = None,
    ):
        self.issue_type = issue_type
        self.severity = severity  # 'critical', 'warning', 'info'
        self.description = description
        self.affected_records = affected_records
        self.correctable = correctable
        self.correction_action = correction_action
        self.detected_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "affected_records": self.affected_records,
            "correctable": self.correctable,
            "correction_action": self.correction_action,
            "detected_at": self.detected_at.isoformat(),
        }


class DataConsistencyValidator:
    """
    Comprehensive data consistency validation and correction system

    Validates data integrity across all workflow stages and provides
    automatic correction capabilities where possible.
    """

    def __init__(self):
        """Initialize the data consistency validator"""
        self.db_url = os.environ.get("DATABASE_URL")
        self.logger = logging.getLogger(__name__)

        # Initialize validation tracking
        self._initialize_validation_tables()

        self.logger.info("DataConsistencyValidator initialized for Step 2.3")

    def _initialize_validation_tables(self):
        """Create tables for tracking validation results"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Create consistency_validation_logs table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS consistency_validation_logs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        validation_run_id UUID NOT NULL,
                        issue_type VARCHAR(100),
                        severity VARCHAR(20),
                        description TEXT,
                        affected_record_count INTEGER,
                        correctable BOOLEAN,
                        correction_applied BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """
                )

                # Create data_corrections table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS data_corrections (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        validation_run_id UUID NOT NULL,
                        correction_type VARCHAR(100),
                        affected_table VARCHAR(100),
                        affected_records JSONB,
                        correction_sql TEXT,
                        applied_at TIMESTAMP DEFAULT NOW(),
                        success BOOLEAN DEFAULT TRUE
                    )
                """
                )

                conn.commit()

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
            self.logger.error(f"Database error in consistency validator: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def validate_complete_workflow(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive workflow consistency validation

        Args:
            workflow_id: Optional specific workflow to validate

        Returns:
            Dict: Comprehensive validation results
        """
        validation_run_id = str(uuid.uuid4())
        start_time = datetime.now()

        self.logger.info(f"Starting comprehensive consistency validation (run: {validation_run_id})")

        issues = []
        corrections_applied = []

        # Run all validation checks
        issues.extend(self._validate_job_application_consistency())
        issues.extend(self._validate_company_relationships())
        issues.extend(self._validate_workflow_state_integrity())
        issues.extend(self._validate_document_tracking())
        issues.extend(self._validate_email_tracking())
        issues.extend(self._validate_ai_analysis_completeness())
        issues.extend(self._validate_preference_matching())
        issues.extend(self._validate_temporal_consistency())

        # Apply automatic corrections where possible
        for issue in issues:
            if issue.correctable:
                try:
                    correction_result = self._apply_correction(issue, validation_run_id)
                    if correction_result:
                        corrections_applied.append(correction_result)
                        issue.correctable = False  # Mark as corrected
                except Exception as e:
                    self.logger.error(f"Failed to apply correction for {issue.issue_type}: {e}")

        # Log validation results
        self._log_validation_results(validation_run_id, issues, corrections_applied)

        validation_time = (datetime.now() - start_time).total_seconds()

        # Compile results
        results = {
            "validation_run_id": validation_run_id,
            "validation_time": validation_time,
            "total_issues": len(issues),
            "critical_issues": len([i for i in issues if i.severity == "critical"]),
            "warning_issues": len([i for i in issues if i.severity == "warning"]),
            "info_issues": len([i for i in issues if i.severity == "info"]),
            "correctable_issues": len([i for i in issues if i.correctable]),
            "corrections_applied": len(corrections_applied),
            "overall_status": self._determine_overall_status(issues),
            "issues": [issue.to_dict() for issue in issues],
            "corrections": corrections_applied,
        }

        self.logger.info(
            f"Consistency validation completed: {results['overall_status']} "
            f"({len(issues)} issues, {len(corrections_applied)} corrections)"
        )

        return results

    def _validate_job_application_consistency(self) -> List[ConsistencyIssue]:
        """Validate job application data consistency"""
        issues = []

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
                        issues.append(
                            ConsistencyIssue(
                                issue_type="orphaned_job_applications",
                                severity="critical",
                                description=f"Found {len(orphaned_applications)} job applications referencing non-existent jobs",
                                affected_records=[str(row["id"]) for row in orphaned_applications],
                                correctable=True,
                                correction_action="Delete orphaned job application records",
                            )
                        )

                    # Check for jobs without applications that should have them
                    cursor.execute(
                        """
                        SELECT j.id, j.job_title, j.eligibility_flag
                        FROM jobs j
                        LEFT JOIN job_applications ja ON j.id = ja.job_id
                        WHERE j.eligibility_flag = TRUE 
                        AND j.analysis_completed = TRUE
                        AND ja.id IS NULL
                        AND j.created_at < NOW() - INTERVAL '1 hour'
                    """
                    )

                    missing_applications = cursor.fetchall()
                    if missing_applications:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="missing_job_applications",
                                severity="warning",
                                description=f"Found {len(missing_applications)} eligible jobs without application records",
                                affected_records=[str(row["id"]) for row in missing_applications],
                                correctable=True,
                                correction_action="Create missing job application records",
                            )
                        )

                    # Check for duplicate applications
                    cursor.execute(
                        """
                        SELECT job_id, COUNT(*) as app_count
                        FROM job_applications
                        GROUP BY job_id
                        HAVING COUNT(*) > 1
                    """
                    )

                    duplicate_applications = cursor.fetchall()
                    if duplicate_applications:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="duplicate_job_applications",
                                severity="warning",
                                description=f"Found {len(duplicate_applications)} jobs with multiple application records",
                                affected_records=[str(row["job_id"]) for row in duplicate_applications],
                                correctable=True,
                                correction_action="Merge or remove duplicate application records",
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error validating job application consistency: {e}")
            issues.append(
                ConsistencyIssue(
                    issue_type="validation_error",
                    severity="critical",
                    description=f"Job application validation failed: {str(e)}",
                    affected_records=[],
                    correctable=False,
                )
            )

        return issues

    def _validate_company_relationships(self) -> List[ConsistencyIssue]:
        """Validate company relationship consistency"""
        issues = []

        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                    # Check for jobs with invalid company references
                    cursor.execute(
                        """
                        SELECT j.id, j.company_id, j.job_title
                        FROM jobs j
                        LEFT JOIN companies c ON j.company_id = c.id
                        WHERE j.company_id IS NOT NULL AND c.id IS NULL
                    """
                    )

                    invalid_company_refs = cursor.fetchall()
                    if invalid_company_refs:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="invalid_company_references",
                                severity="critical",
                                description=f"Found {len(invalid_company_refs)} jobs with invalid company references",
                                affected_records=[str(row["id"]) for row in invalid_company_refs],
                                correctable=True,
                                correction_action="Create missing company records or clear invalid references",
                            )
                        )

                    # Check for unused companies
                    cursor.execute(
                        """
                        SELECT c.id, c.name
                        FROM companies c
                        LEFT JOIN jobs j ON c.id = j.company_id
                        WHERE j.id IS NULL
                        AND c.created_at < NOW() - INTERVAL '7 days'
                    """
                    )

                    unused_companies = cursor.fetchall()
                    if unused_companies:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="unused_companies",
                                severity="info",
                                description=f"Found {len(unused_companies)} companies with no associated jobs",
                                affected_records=[str(row["id"]) for row in unused_companies],
                                correctable=True,
                                correction_action="Archive or remove unused company records",
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error validating company relationships: {e}")
            issues.append(
                ConsistencyIssue(
                    issue_type="validation_error",
                    severity="critical",
                    description=f"Company relationship validation failed: {str(e)}",
                    affected_records=[],
                    correctable=False,
                )
            )

        return issues

    def _validate_workflow_state_integrity(self) -> List[ConsistencyIssue]:
        """Validate workflow state consistency"""
        issues = []

        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                    # Check for inconsistent analysis states
                    cursor.execute(
                        """
                        SELECT j.id, j.analysis_completed, j.eligibility_flag
                        FROM jobs j
                        WHERE j.analysis_completed = FALSE 
                        AND j.eligibility_flag IS NOT NULL
                    """
                    )

                    inconsistent_analysis = cursor.fetchall()
                    if inconsistent_analysis:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="inconsistent_analysis_state",
                                severity="warning",
                                description=f"Found {len(inconsistent_analysis)} jobs with eligibility set but analysis not completed",
                                affected_records=[str(row["id"]) for row in inconsistent_analysis],
                                correctable=True,
                                correction_action="Reset eligibility flag for incomplete analysis",
                            )
                        )

                    # Check for stalled workflows
                    cursor.execute(
                        """
                        SELECT j.id, j.created_at, j.analysis_completed
                        FROM jobs j
                        WHERE j.analysis_completed = FALSE
                        AND j.created_at < NOW() - INTERVAL '24 hours'
                    """
                    )

                    stalled_workflows = cursor.fetchall()
                    if stalled_workflows:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="stalled_workflows",
                                severity="warning",
                                description=f"Found {len(stalled_workflows)} jobs with stalled analysis (>24h)",
                                affected_records=[str(row["id"]) for row in stalled_workflows],
                                correctable=True,
                                correction_action="Re-queue jobs for analysis or mark as failed",
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error validating workflow state: {e}")
            issues.append(
                ConsistencyIssue(
                    issue_type="validation_error",
                    severity="critical",
                    description=f"Workflow state validation failed: {str(e)}",
                    affected_records=[],
                    correctable=False,
                )
            )

        return issues

    def _validate_document_tracking(self) -> List[ConsistencyIssue]:
        """Validate document generation tracking"""
        issues = []

        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                    # Check for applications without document tracking
                    cursor.execute(
                        """
                        SELECT ja.id, ja.application_status
                        FROM job_applications ja
                        LEFT JOIN document_job dj ON ja.id::text = dj.webhook_data->>'application_id'
                        WHERE ja.application_status = 'sent'
                        AND dj.id IS NULL
                    """
                    )

                    missing_document_tracking = cursor.fetchall()
                    if missing_document_tracking:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="missing_document_tracking",
                                severity="warning",
                                description=f"Found {len(missing_document_tracking)} sent applications without document tracking",
                                affected_records=[str(row["id"]) for row in missing_document_tracking],
                                correctable=False,
                                correction_action="Document tracking cannot be retroactively created",
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error validating document tracking: {e}")

        return issues

    def _validate_email_tracking(self) -> List[ConsistencyIssue]:
        """Validate email tracking consistency"""
        issues = []

        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                    # Check for sent applications without email tracking
                    cursor.execute(
                        """
                        SELECT ja.id, ja.email_sent_at
                        FROM job_applications ja
                        WHERE ja.application_status = 'sent'
                        AND ja.email_sent_at IS NULL
                    """
                    )

                    missing_email_tracking = cursor.fetchall()
                    if missing_email_tracking:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="missing_email_tracking",
                                severity="warning",
                                description=f"Found {len(missing_email_tracking)} applications marked as sent without email timestamp",
                                affected_records=[str(row["id"]) for row in missing_email_tracking],
                                correctable=True,
                                correction_action="Update email_sent_at timestamp or correct application status",
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error validating email tracking: {e}")

        return issues

    def _validate_ai_analysis_completeness(self) -> List[ConsistencyIssue]:
        """Validate AI analysis completeness"""
        issues = []

        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                    # Check for jobs marked as analyzed but missing analysis data
                    cursor.execute(
                        """
                        SELECT j.id, j.job_title
                        FROM jobs j
                        LEFT JOIN analyzed_jobs aj ON j.id = aj.job_id
                        WHERE j.analysis_completed = TRUE
                        AND aj.id IS NULL
                    """
                    )

                    missing_analysis_data = cursor.fetchall()
                    if missing_analysis_data:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="missing_analysis_data",
                                severity="critical",
                                description=f"Found {len(missing_analysis_data)} jobs marked as analyzed but missing analysis data",
                                affected_records=[str(row["id"]) for row in missing_analysis_data],
                                correctable=True,
                                correction_action="Reset analysis_completed flag to trigger re-analysis",
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error validating AI analysis: {e}")

        return issues

    def _validate_preference_matching(self) -> List[ConsistencyIssue]:
        """Validate preference matching consistency"""
        issues = []

        # This would validate user preference matching logic
        # For now, returning empty list as preferences are handled by fallback defaults

        return issues

    def _validate_temporal_consistency(self) -> List[ConsistencyIssue]:
        """Validate temporal consistency (timestamps, ordering)"""
        issues = []

        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                    # Check for applications created before jobs
                    cursor.execute(
                        """
                        SELECT ja.id, ja.created_at as app_created, j.created_at as job_created
                        FROM job_applications ja
                        JOIN jobs j ON ja.job_id = j.id
                        WHERE ja.created_at < j.created_at
                    """
                    )

                    temporal_inconsistencies = cursor.fetchall()
                    if temporal_inconsistencies:
                        issues.append(
                            ConsistencyIssue(
                                issue_type="temporal_inconsistency",
                                severity="warning",
                                description=f"Found {len(temporal_inconsistencies)} applications created before their associated jobs",
                                affected_records=[str(row["id"]) for row in temporal_inconsistencies],
                                correctable=True,
                                correction_action="Correct timestamps to maintain proper temporal ordering",
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error validating temporal consistency: {e}")

        return issues

    def _apply_correction(self, issue: ConsistencyIssue, validation_run_id: str) -> Optional[Dict[str, Any]]:
        """
        Apply automatic correction for correctable issues

        Args:
            issue: ConsistencyIssue to correct
            validation_run_id: Validation run identifier

        Returns:
            Dict: Correction result information
        """
        if not issue.correctable:
            return None

        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:

                    correction_sql = None

                    if issue.issue_type == "orphaned_job_applications":
                        # Delete orphaned job applications
                        placeholders = ",".join(["%s"] * len(issue.affected_records))
                        correction_sql = f"DELETE FROM job_applications WHERE id IN ({placeholders})"
                        cursor.execute(correction_sql, issue.affected_records)

                    elif issue.issue_type == "missing_job_applications":
                        # Create missing job application records
                        for job_id in issue.affected_records:
                            cursor.execute(
                                """
                                INSERT INTO job_applications (id, job_id, application_status, created_at)
                                VALUES (gen_random_uuid(), %s, 'pending', NOW())
                                ON CONFLICT DO NOTHING
                            """,
                                (job_id,),
                            )
                        correction_sql = "INSERT job_applications for eligible jobs"

                    elif issue.issue_type == "inconsistent_analysis_state":
                        # Reset eligibility flags for incomplete analysis
                        placeholders = ",".join(["%s"] * len(issue.affected_records))
                        correction_sql = f"UPDATE jobs SET eligibility_flag = NULL WHERE id IN ({placeholders})"
                        cursor.execute(correction_sql, issue.affected_records)

                    elif issue.issue_type == "missing_analysis_data":
                        # Reset analysis_completed flag
                        placeholders = ",".join(["%s"] * len(issue.affected_records))
                        correction_sql = f"UPDATE jobs SET analysis_completed = FALSE WHERE id IN ({placeholders})"
                        cursor.execute(correction_sql, issue.affected_records)

                    # Log the correction
                    cursor.execute(
                        """
                        INSERT INTO data_corrections (
                            validation_run_id, correction_type, affected_table, 
                            affected_records, correction_sql
                        ) VALUES (%s, %s, %s, %s, %s)
                    """,
                        (
                            validation_run_id,
                            issue.issue_type,
                            self._get_affected_table(issue.issue_type),
                            json.dumps(issue.affected_records),
                            correction_sql,
                        ),
                    )

                    conn.commit()

                    self.logger.info(
                        f"Applied correction for {issue.issue_type}: {len(issue.affected_records)} records"
                    )

                    return {
                        "correction_type": issue.issue_type,
                        "records_affected": len(issue.affected_records),
                        "correction_sql": correction_sql,
                        "success": True,
                    }

        except Exception as e:
            self.logger.error(f"Failed to apply correction for {issue.issue_type}: {e}")
            return {"correction_type": issue.issue_type, "records_affected": 0, "error": str(e), "success": False}

    def _get_affected_table(self, issue_type: str) -> str:
        """Determine primary affected table for issue type"""
        table_mapping = {
            "orphaned_job_applications": "job_applications",
            "missing_job_applications": "job_applications",
            "duplicate_job_applications": "job_applications",
            "invalid_company_references": "jobs",
            "unused_companies": "companies",
            "inconsistent_analysis_state": "jobs",
            "stalled_workflows": "jobs",
            "missing_analysis_data": "jobs",
            "temporal_inconsistency": "job_applications",
        }
        return table_mapping.get(issue_type, "unknown")

    def _log_validation_results(
        self, validation_run_id: str, issues: List[ConsistencyIssue], corrections: List[Dict[str, Any]]
    ):
        """Log validation results to database"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:

                    for issue in issues:
                        cursor.execute(
                            """
                            INSERT INTO consistency_validation_logs (
                                validation_run_id, issue_type, severity, description,
                                affected_record_count, correctable, correction_applied
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                            (
                                validation_run_id,
                                issue.issue_type,
                                issue.severity,
                                issue.description,
                                len(issue.affected_records),
                                issue.correctable,
                                not issue.correctable,  # If not correctable, no correction applied
                            ),
                        )

                    conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to log validation results: {e}")

    def _determine_overall_status(self, issues: List[ConsistencyIssue]) -> str:
        """Determine overall validation status"""
        if not issues:
            return "EXCELLENT"

        critical_count = len([i for i in issues if i.severity == "critical"])
        warning_count = len([i for i in issues if i.severity == "warning"])

        if critical_count > 0:
            return "CRITICAL_ISSUES"
        elif warning_count > 5:
            return "MULTIPLE_WARNINGS"
        elif warning_count > 0:
            return "MINOR_ISSUES"
        else:
            return "GOOD"

    def get_validation_history(self, days: int = 7) -> Dict[str, Any]:
        """Get validation history for specified period"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                    cursor.execute(
                        """
                        SELECT 
                            validation_run_id,
                            COUNT(*) as total_issues,
                            SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_issues,
                            SUM(CASE WHEN severity = 'warning' THEN 1 ELSE 0 END) as warning_issues,
                            SUM(CASE WHEN correction_applied THEN 1 ELSE 0 END) as corrections_applied,
                            DATE(created_at) as validation_date,
                            MIN(created_at) as first_issue_time
                        FROM consistency_validation_logs
                        WHERE created_at >= NOW() - INTERVAL '%s days'
                        GROUP BY validation_run_id, DATE(created_at)
                        ORDER BY first_issue_time DESC
                    """,
                        (days,),
                    )

                    history = cursor.fetchall()

                    return {
                        "validation_runs": [dict(row) for row in history],
                        "summary": {
                            "total_runs": len(history),
                            "total_issues": sum(row["total_issues"] for row in history),
                            "total_corrections": sum(row["corrections_applied"] for row in history),
                        },
                    }

        except Exception as e:
            self.logger.error(f"Failed to get validation history: {e}")
            return {"error": str(e)}
