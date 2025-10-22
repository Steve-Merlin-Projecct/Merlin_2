"""
Workflow Manager for New Job Processing Pipeline (Refactored Version)
==============================================================

This module manages the new workflow:
raw_job_scrapes -> cleaned_job_scrapes -> pre_analyzed_jobs -> ai analysis -> analyzed_jobs

Key Features:
- Uses centralized DatabaseClient for connection pooling and management
- Separate deduplication methods for pre_analyzed_jobs and analyzed_jobs
- Audit trail tracking per job
- No primary keys passed through LLM prompts
- Clear separation of concerns between pre-analysis and post-analysis data
- Improved error handling with transaction management

Author: Automated Job Application System V2.16
Updated: 2025-10-21 (Refactored to use DatabaseClient)
"""

import logging
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from modules.database.lazy_instances import get_database_client

logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    Manages the new job processing workflow with separate pre-analysis and analysis phases.

    Workflow Steps:
    1. cleaned_job_scrapes -> pre_analyzed_jobs (consolidation + deduplication)
    2. pre_analyzed_jobs -> queue for AI analysis
    3. AI analysis -> analyzed_jobs (with AI insights)
    4. analyzed_jobs -> application workflow

    Now uses centralized DatabaseClient for better connection management and pooling.
    """

    def __init__(self):
        """
        Initialize the workflow manager with database client.

        Uses lazy initialization to prevent connections at import time.
        """
        try:
            self.db_client = get_database_client()
            logger.info("WorkflowManager initialized with DatabaseClient (connection pooling enabled)")
        except Exception as e:
            logger.error(f"Failed to initialize WorkflowManager: {e}")
            raise

    def transfer_cleaned_to_pre_analyzed(self, batch_size: int = 100) -> Dict:
        """
        Transfer jobs from cleaned_job_scrapes to pre_analyzed_jobs.

        This method:
        - Consolidates multiple cleaned scrapes into single pre_analyzed_jobs
        - Performs deduplication specific to pre_analyzed_jobs table
        - Maintains audit trail of source cleaned scrapes
        - Does not pass primary keys to external systems

        Args:
            batch_size: Number of cleaned scrapes to process in one batch

        Returns:
            Dict containing transfer statistics and results
        """
        logger.info(f"Starting transfer from cleaned_job_scrapes to pre_analyzed_jobs (batch_size: {batch_size})")

        try:
            with self.db_client.get_session() as session:
                # Get unprocessed cleaned job scrapes
                query = """
                    SELECT cleaned_job_id, job_title, company_name, location_city,
                           location_province, location_country, work_arrangement,
                           salary_min, salary_max, salary_currency, salary_period,
                           job_description, requirements, benefits, industry,
                           job_type, experience_level, posting_date, application_deadline,
                           external_job_id, source_website, application_url,
                           application_email, confidence_score
                    FROM cleaned_job_scrapes
                    WHERE cleaned_job_id NOT IN (
                        SELECT cleaned_scrape_id
                        FROM pre_analyzed_jobs
                        WHERE cleaned_scrape_id IS NOT NULL
                    )
                    ORDER BY cleaned_timestamp DESC
                    LIMIT :batch_size
                """

                result = session.execute(
                    self.db_client.engine.text(query),
                    {"batch_size": batch_size}
                )
                cleaned_jobs = result.fetchall()

                if not cleaned_jobs:
                    return {
                        "success": True,
                        "transferred": 0,
                        "duplicates_found": 0,
                        "message": "No new cleaned job scrapes to process",
                    }

                logger.info(f"Found {len(cleaned_jobs)} cleaned job scrapes to process")

                transferred = 0
                duplicates_found = 0

                for job in cleaned_jobs:
                    # Create deduplication key for pre_analyzed_jobs
                    dedup_key = self._create_pre_analyzed_dedup_key(
                        job_title=job[1], company_name=job[2], location_city=job[3], location_province=job[4]
                    )

                    # Check if this job already exists in pre_analyzed_jobs
                    if self._check_pre_analyzed_duplicate(session, dedup_key):
                        duplicates_found += 1
                        logger.debug(f"Duplicate found for: {job[1]} at {job[2]}")
                        continue

                    # Resolve or create company
                    company_id = self._resolve_company_id(session, job[2])

                    # Insert into pre_analyzed_jobs
                    try:
                        self._insert_pre_analyzed_job(session, job, company_id, dedup_key)
                        transferred += 1
                    except IntegrityError as e:
                        if "duplicate key" in str(e).lower():
                            logger.warning(f"Duplicate key constraint violation: {job[1]} at {job[2]}")
                            duplicates_found += 1
                            session.rollback()
                            continue
                        raise

                # Commit happens automatically via context manager
                logger.info(
                    f"Transfer completed: {transferred} jobs transferred, {duplicates_found} duplicates skipped"
                )

                return {
                    "success": True,
                    "transferred": transferred,
                    "duplicates_found": duplicates_found,
                    "processed": len(cleaned_jobs),
                    "message": f"Successfully transferred {transferred} jobs to pre_analyzed_jobs",
                }

        except SQLAlchemyError as e:
            logger.error(f"Database error transferring cleaned jobs to pre_analyzed: {e}")
            return {"success": False, "error": f"Database error: {str(e)}", "transferred": 0, "duplicates_found": 0}
        except Exception as e:
            logger.error(f"Unexpected error transferring cleaned jobs to pre_analyzed: {e}")
            return {"success": False, "error": str(e), "transferred": 0, "duplicates_found": 0}

    def queue_jobs_for_analysis(self, limit: int = 50) -> Dict:
        """
        Queue pre_analyzed_jobs for AI analysis.

        This method:
        - Identifies jobs ready for AI analysis
        - Sets queued_for_analysis flag
        - Prepares data for AI analysis without exposing primary keys

        Args:
            limit: Maximum number of jobs to queue

        Returns:
            Dict containing queuing results
        """
        logger.info(f"Queuing jobs for AI analysis (limit: {limit})")

        try:
            with self.db_client.get_session() as session:
                # Find jobs ready for analysis
                query = """
                    UPDATE pre_analyzed_jobs
                    SET queued_for_analysis = true,
                        processed_at = CURRENT_TIMESTAMP
                    WHERE id IN (
                        SELECT id FROM pre_analyzed_jobs
                        WHERE is_active = true
                        AND queued_for_analysis = false
                        AND job_title IS NOT NULL
                        AND job_description IS NOT NULL
                        ORDER BY created_at DESC
                        LIMIT :limit
                    )
                    RETURNING id, job_title, company_id
                """

                result = session.execute(
                    self.db_client.engine.text(query),
                    {"limit": limit}
                )
                queued_jobs = result.fetchall()

                logger.info(f"Queued {len(queued_jobs)} jobs for AI analysis")

                return {
                    "success": True,
                    "queued_count": len(queued_jobs),
                    "job_ids": [str(job[0]) for job in queued_jobs],
                    "message": f"Successfully queued {len(queued_jobs)} jobs for analysis",
                }

        except SQLAlchemyError as e:
            logger.error(f"Database error queuing jobs for analysis: {e}")
            return {"success": False, "error": f"Database error: {str(e)}", "queued_count": 0}
        except Exception as e:
            logger.error(f"Unexpected error queuing jobs for analysis: {e}")
            return {"success": False, "error": str(e), "queued_count": 0}

    def get_jobs_for_ai_analysis(self, batch_size: int = 10) -> List[Dict]:
        """
        Get queued jobs ready for AI analysis.

        This method:
        - Returns job data WITHOUT primary keys for LLM processing
        - Includes only data needed for AI analysis
        - Maintains audit trail through internal job tracking

        Args:
            batch_size: Number of jobs to return for analysis

        Returns:
            List of job dictionaries ready for AI analysis (no primary keys)
        """
        logger.info(f"Retrieving jobs for AI analysis (batch_size: {batch_size})")

        try:
            with self.db_client.get_session() as session:
                query = """
                    SELECT p.job_title, p.job_description, p.company_name,
                           p.industry, p.experience_level, p.salary_min, p.salary_max,
                           p.salary_currency, p.work_arrangement, p.job_type,
                           p.deduplication_key
                    FROM pre_analyzed_jobs p
                    WHERE p.queued_for_analysis = true
                    AND p.is_active = true
                    ORDER BY p.created_at DESC
                    LIMIT :batch_size
                """

                result = session.execute(
                    self.db_client.engine.text(query),
                    {"batch_size": batch_size}
                )
                jobs_data = result.fetchall()

                # Format for AI analysis (no primary keys exposed)
                analysis_jobs = []
                for job in jobs_data:
                    analysis_jobs.append(
                        {
                            "title": job[0],
                            "description": job[1] or "",
                            "company_name": job[2] or "Unknown Company",
                            "industry": job[3],
                            "experience_level": job[4],
                            "salary_min": job[5],
                            "salary_max": job[6],
                            "currency": job[7] or "CAD",
                            "work_arrangement": job[8],
                            "job_type": job[9],
                            "internal_dedup_key": job[10],  # For internal tracking only
                        }
                    )

                logger.info(f"Retrieved {len(analysis_jobs)} jobs for AI analysis")
                return analysis_jobs

        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving jobs for AI analysis: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving jobs for AI analysis: {e}")
            return []

    def save_ai_analysis_results(self, analysis_results: List[Dict]) -> Dict:
        """
        Save AI analysis results to analyzed_jobs table.

        This method:
        - Creates analyzed_jobs records from AI analysis
        - Performs deduplication specific to analyzed_jobs table
        - Maintains audit trail of analysis process
        - Uses deduplication key (not primary keys) for job matching

        Args:
            analysis_results: List of AI analysis results with dedup keys

        Returns:
            Dict containing save operation results
        """
        logger.info(f"Saving AI analysis results for {len(analysis_results)} jobs")

        try:
            with self.db_client.get_session() as session:
                saved_count = 0
                skipped_count = 0

                for result in analysis_results:
                    try:
                        # Get pre_analyzed_job using deduplication key
                        query = """
                            SELECT id, company_id, job_title, job_description,
                                   salary_min, salary_max, salary_period, salary_currency,
                                   work_arrangement, job_type, industry, experience_level,
                                   application_deadline, application_email, application_url,
                                   posting_date, external_job_id, source_website
                            FROM pre_analyzed_jobs
                            WHERE deduplication_key = :dedup_key
                        """

                        pre_analyzed_result = session.execute(
                            self.db_client.engine.text(query),
                            {"dedup_key": result.get("internal_dedup_key")}
                        )
                        pre_analyzed_job = pre_analyzed_result.fetchone()

                        if not pre_analyzed_job:
                            logger.warning(
                                f"Pre-analyzed job not found for dedup key: {result.get('internal_dedup_key')}"
                            )
                            skipped_count += 1
                            continue

                        # Create analyzed_jobs deduplication key
                        analyzed_dedup_key = self._create_analyzed_dedup_key(
                            job_title=pre_analyzed_job[2],
                            company_id=str(pre_analyzed_job[1]) if pre_analyzed_job[1] else "",
                            primary_industry=result.get("primary_industry", ""),
                        )

                        # Check for duplicates in analyzed_jobs
                        if self._check_analyzed_duplicate(session, analyzed_dedup_key):
                            logger.debug(f"Analyzed job duplicate found: {pre_analyzed_job[2]}")
                            skipped_count += 1
                            continue

                        # Insert into analyzed_jobs
                        self._insert_analyzed_job(session, pre_analyzed_job, result, analyzed_dedup_key)
                        saved_count += 1

                        # Mark pre_analyzed_job as processed
                        update_query = """
                            UPDATE pre_analyzed_jobs
                            SET queued_for_analysis = false,
                                processed_at = CURRENT_TIMESTAMP
                            WHERE id = :job_id
                        """
                        session.execute(
                            self.db_client.engine.text(update_query),
                            {"job_id": pre_analyzed_job[0]}
                        )

                    except IntegrityError as e:
                        if "duplicate key" in str(e).lower():
                            logger.warning(f"Duplicate key constraint during save: {result.get('internal_dedup_key')}")
                            skipped_count += 1
                            session.rollback()
                            continue
                        raise

                # Commit happens automatically via context manager
                logger.info(f"AI analysis results saved: {saved_count} new, {skipped_count} skipped")

                return {
                    "success": True,
                    "saved_count": saved_count,
                    "skipped_count": skipped_count,
                    "total_processed": len(analysis_results),
                    "message": f"Saved {saved_count} analyzed jobs, skipped {skipped_count} duplicates",
                }

        except SQLAlchemyError as e:
            logger.error(f"Database error saving AI analysis results: {e}")
            return {"success": False, "error": f"Database error: {str(e)}", "saved_count": 0, "skipped_count": 0}
        except Exception as e:
            logger.error(f"Unexpected error saving AI analysis results: {e}")
            return {"success": False, "error": str(e), "saved_count": 0, "skipped_count": 0}

    def get_workflow_statistics(self) -> Dict:
        """
        Get comprehensive statistics about the new workflow.

        Returns:
            Dict containing statistics for each stage of the workflow
        """
        try:
            with self.db_client.get_session() as session:
                stats = {}

                # Execute count queries
                queries = {
                    "raw_job_scrapes": "SELECT COUNT(*) FROM raw_job_scrapes",
                    "cleaned_job_scrapes": "SELECT COUNT(*) FROM cleaned_job_scrapes",
                    "pre_analyzed_jobs": "SELECT COUNT(*) FROM pre_analyzed_jobs",
                    "pre_analyzed_queued": "SELECT COUNT(*) FROM pre_analyzed_jobs WHERE queued_for_analysis = true",
                    "analyzed_jobs": "SELECT COUNT(*) FROM analyzed_jobs",
                    "analysis_completed": "SELECT COUNT(*) FROM analyzed_jobs WHERE ai_analysis_completed = true",
                    "legacy_jobs": "SELECT COUNT(*) FROM jobs",
                }

                for key, query in queries.items():
                    result = session.execute(self.db_client.engine.text(query))
                    stats[key] = result.fetchone()[0]

                return {
                    "success": True,
                    "statistics": stats,
                    "workflow_health": {
                        "raw_to_cleaned_rate": round(
                            (stats["cleaned_job_scrapes"] / max(stats["raw_job_scrapes"], 1)) * 100, 2
                        ),
                        "cleaned_to_pre_analyzed_rate": round(
                            (stats["pre_analyzed_jobs"] / max(stats["cleaned_job_scrapes"], 1)) * 100, 2
                        ),
                        "pre_analyzed_to_analyzed_rate": round(
                            (stats["analyzed_jobs"] / max(stats["pre_analyzed_jobs"], 1)) * 100, 2
                        ),
                        "analysis_completion_rate": round(
                            (stats["analysis_completed"] / max(stats["analyzed_jobs"], 1)) * 100, 2
                        ),
                    },
                }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting workflow statistics: {e}")
            return {"success": False, "error": f"Database error: {str(e)}", "statistics": {}, "workflow_health": {}}
        except Exception as e:
            logger.error(f"Unexpected error getting workflow statistics: {e}")
            return {"success": False, "error": str(e), "statistics": {}, "workflow_health": {}}

    # Helper methods for deduplication and data management

    def _create_pre_analyzed_dedup_key(
        self, job_title: str, company_name: str, location_city: str, location_province: str
    ) -> str:
        """Create deduplication key for pre_analyzed_jobs table."""
        title_norm = (job_title or "").lower().strip()
        company_norm = (company_name or "").lower().strip()
        city_norm = (location_city or "").lower().strip()
        province_norm = (location_province or "").lower().strip()

        dedup_string = f"{title_norm}|{company_norm}|{city_norm}|{province_norm}"
        return hashlib.sha256(dedup_string.encode("utf-8")).hexdigest()[:32]

    def _create_analyzed_dedup_key(self, job_title: str, company_id: str, primary_industry: str) -> str:
        """Create deduplication key for analyzed_jobs table."""
        title_norm = (job_title or "").lower().strip()
        company_norm = (company_id or "").lower().strip()
        industry_norm = (primary_industry or "").lower().strip()

        dedup_string = f"{title_norm}|{company_norm}|{industry_norm}"
        return hashlib.sha256(dedup_string.encode("utf-8")).hexdigest()[:32]

    def _check_pre_analyzed_duplicate(self, session, dedup_key: str) -> bool:
        """Check if job already exists in pre_analyzed_jobs."""
        query = "SELECT 1 FROM pre_analyzed_jobs WHERE deduplication_key = :dedup_key"
        result = session.execute(self.db_client.engine.text(query), {"dedup_key": dedup_key})
        return result.fetchone() is not None

    def _check_analyzed_duplicate(self, session, dedup_key: str) -> bool:
        """Check if job already exists in analyzed_jobs."""
        query = "SELECT 1 FROM analyzed_jobs WHERE deduplication_key = :dedup_key"
        result = session.execute(self.db_client.engine.text(query), {"dedup_key": dedup_key})
        return result.fetchone() is not None

    def _resolve_company_id(self, session, company_name: str) -> Optional[str]:
        """Resolve company name to company_id, create if not exists."""
        if not company_name:
            return None

        # Check if company exists
        query = "SELECT id FROM companies WHERE LOWER(name) = LOWER(:company_name)"
        result = session.execute(self.db_client.engine.text(query), {"company_name": company_name})
        row = result.fetchone()

        if row:
            return str(row[0])

        # Create new company
        insert_query = """
            INSERT INTO companies (name, created_at)
            VALUES (:company_name, CURRENT_TIMESTAMP)
            RETURNING id
        """
        result = session.execute(
            self.db_client.engine.text(insert_query),
            {"company_name": company_name}
        )
        return str(result.fetchone()[0])

    def _insert_pre_analyzed_job(self, session, job_data: tuple, company_id: Optional[str], dedup_key: str):
        """Insert job into pre_analyzed_jobs table (same structure as cleaned_job_scrapes)."""
        query = """
            INSERT INTO pre_analyzed_jobs (
                cleaned_scrape_id, company_id, job_title, company_name,
                location_city, location_province, location_country, work_arrangement,
                salary_min, salary_max, salary_currency, salary_period,
                job_description, requirements, benefits, industry,
                job_type, experience_level, posting_date, application_deadline,
                external_job_id, source_website, application_url, application_email,
                confidence_score, duplicates_count, deduplication_key,
                is_active, queued_for_analysis, created_at
            ) VALUES (
                :cleaned_job_id, :company_id, :job_title, :company_name,
                :location_city, :location_province, :location_country, :work_arrangement,
                :salary_min, :salary_max, :salary_currency, :salary_period,
                :job_description, :requirements, :benefits, :industry,
                :job_type, :experience_level, :posting_date, :application_deadline,
                :external_job_id, :source_website, :application_url, :application_email,
                :confidence_score, :duplicates_count, :deduplication_key,
                :is_active, :queued_for_analysis, CURRENT_TIMESTAMP
            )
        """

        session.execute(
            self.db_client.engine.text(query),
            {
                "cleaned_job_id": job_data[0],
                "company_id": company_id,
                "job_title": job_data[1],
                "company_name": job_data[2],
                "location_city": job_data[3],
                "location_province": job_data[4],
                "location_country": job_data[5],
                "work_arrangement": job_data[6],
                "salary_min": job_data[7],
                "salary_max": job_data[8],
                "salary_currency": job_data[9] or "CAD",
                "salary_period": job_data[10],
                "job_description": job_data[11] if len(job_data) > 11 else None,
                "requirements": job_data[12] if len(job_data) > 12 else None,
                "benefits": job_data[13] if len(job_data) > 13 else None,
                "industry": job_data[14] if len(job_data) > 14 else None,
                "job_type": job_data[15] if len(job_data) > 15 else None,
                "experience_level": job_data[16] if len(job_data) > 16 else None,
                "posting_date": job_data[17] if len(job_data) > 17 else None,
                "application_deadline": job_data[18] if len(job_data) > 18 else None,
                "external_job_id": job_data[19] if len(job_data) > 19 else None,
                "source_website": job_data[20] if len(job_data) > 20 else None,
                "application_url": job_data[21] if len(job_data) > 21 else None,
                "application_email": job_data[22] if len(job_data) > 22 else None,
                "confidence_score": job_data[23] if len(job_data) > 23 else None,
                "duplicates_count": 1,
                "deduplication_key": dedup_key,
                "is_active": True,
                "queued_for_analysis": False,
            }
        )

    def _insert_analyzed_job(self, session, pre_analyzed_data: tuple, ai_result: Dict, dedup_key: str):
        """Insert job into analyzed_jobs table with AI analysis results."""
        query = """
            INSERT INTO analyzed_jobs (
                pre_analyzed_job_id, company_id, job_title, job_description,
                salary_min, salary_max, salary_period, salary_currency,
                work_arrangement, job_type, industry, experience_level,
                application_deadline, application_email, application_url, posting_date,
                external_job_id, source_website,
                ai_analysis_completed, primary_industry, authenticity_score,
                deduplication_key, application_status, eligibility_flag,
                analysis_date, gemini_model_used, created_at
            ) VALUES (
                :pre_analyzed_job_id, :company_id, :job_title, :job_description,
                :salary_min, :salary_max, :salary_period, :salary_currency,
                :work_arrangement, :job_type, :industry, :experience_level,
                :application_deadline, :application_email, :application_url, :posting_date,
                :external_job_id, :source_website,
                :ai_analysis_completed, :primary_industry, :authenticity_score,
                :deduplication_key, :application_status, :eligibility_flag,
                :analysis_date, :gemini_model_used, CURRENT_TIMESTAMP
            )
        """

        session.execute(
            self.db_client.engine.text(query),
            {
                "pre_analyzed_job_id": pre_analyzed_data[0],
                "company_id": pre_analyzed_data[1],
                "job_title": pre_analyzed_data[2],
                "job_description": pre_analyzed_data[3],
                "salary_min": pre_analyzed_data[4],
                "salary_max": pre_analyzed_data[5],
                "salary_period": pre_analyzed_data[6],
                "salary_currency": pre_analyzed_data[7],
                "work_arrangement": pre_analyzed_data[8],
                "job_type": pre_analyzed_data[9],
                "industry": pre_analyzed_data[10],
                "experience_level": pre_analyzed_data[11],
                "application_deadline": pre_analyzed_data[12],
                "application_email": pre_analyzed_data[13],
                "application_url": pre_analyzed_data[14],
                "posting_date": pre_analyzed_data[15],
                "external_job_id": pre_analyzed_data[16],
                "source_website": pre_analyzed_data[17],
                "ai_analysis_completed": True,
                "primary_industry": ai_result.get("primary_industry"),
                "authenticity_score": ai_result.get("authenticity_score"),
                "deduplication_key": dedup_key,
                "application_status": "not_applied",
                "eligibility_flag": True,
                "analysis_date": datetime.utcnow(),
                "gemini_model_used": ai_result.get("model_used", "gemini-2.0-flash-001"),
            }
        )
