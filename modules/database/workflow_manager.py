"""
Workflow Manager for New Job Processing Pipeline (Fixed Version)
==============================================================

This module manages the new workflow:
raw_job_scrapes -> cleaned_job_scrapes -> pre_analyzed_jobs -> ai analysis -> analyzed_jobs

Key Features:
- Separate deduplication methods for pre_analyzed_jobs and analyzed_jobs
- Audit trail tracking per job
- No primary keys passed through LLM prompts
- Clear separation of concerns between pre-analysis and post-analysis data

Author: Automated Job Application System V2.16
Created: 2025-07-26
"""

import logging
import hashlib
import psycopg2
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    Manages the new job processing workflow with separate pre-analysis and analysis phases.

    Workflow Steps:
    1. cleaned_job_scrapes -> pre_analyzed_jobs (consolidation + deduplication)
    2. pre_analyzed_jobs -> queue for AI analysis
    3. AI analysis -> analyzed_jobs (with AI insights)
    4. analyzed_jobs -> application workflow
    """

    def __init__(self):
        """Initialize the workflow manager with database connection."""
        self.database_url = os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

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
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    # Get unprocessed cleaned job scrapes
                    cursor.execute(
                        """
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
                        LIMIT %s
                    """,
                        (batch_size,),
                    )

                    cleaned_jobs = cursor.fetchall()

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
                        if self._check_pre_analyzed_duplicate(cursor, dedup_key):
                            duplicates_found += 1
                            logger.debug(f"Duplicate found for: {job[1]} at {job[2]}")
                            continue

                        # Resolve or create company
                        company_id = self._resolve_company_id(cursor, job[2])

                        # Insert into pre_analyzed_jobs
                        self._insert_pre_analyzed_job(cursor, job, company_id, dedup_key)
                        transferred += 1

                    conn.commit()

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

        except Exception as e:
            logger.error(f"Error transferring cleaned jobs to pre_analyzed: {e}")
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
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    # Find jobs ready for analysis
                    cursor.execute(
                        """
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
                            LIMIT %s
                        )
                        RETURNING id, job_title, company_id
                    """,
                        (limit,),
                    )

                    queued_jobs = cursor.fetchall()
                    conn.commit()

                    logger.info(f"Queued {len(queued_jobs)} jobs for AI analysis")

                    return {
                        "success": True,
                        "queued_count": len(queued_jobs),
                        "job_ids": [str(job[0]) for job in queued_jobs],
                        "message": f"Successfully queued {len(queued_jobs)} jobs for analysis",
                    }

        except Exception as e:
            logger.error(f"Error queuing jobs for analysis: {e}")
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
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT p.job_title, p.job_description, p.company_name,
                               p.industry, p.experience_level, p.salary_min, p.salary_max,
                               p.salary_currency, p.work_arrangement, p.job_type,
                               p.deduplication_key
                        FROM pre_analyzed_jobs p
                        WHERE p.queued_for_analysis = true
                        AND p.is_active = true
                        ORDER BY p.created_at DESC
                        LIMIT %s
                    """,
                        (batch_size,),
                    )

                    jobs_data = cursor.fetchall()

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

        except Exception as e:
            logger.error(f"Error retrieving jobs for AI analysis: {e}")
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
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    saved_count = 0
                    skipped_count = 0

                    for result in analysis_results:
                        # Get pre_analyzed_job using deduplication key
                        cursor.execute(
                            """
                            SELECT id, company_id, job_title, job_description,
                                   salary_min, salary_max, salary_period, salary_currency,
                                   work_arrangement, job_type, industry, experience_level,
                                   application_deadline, application_email, application_url,
                                   posting_date, external_job_id, source_website
                            FROM pre_analyzed_jobs 
                            WHERE deduplication_key = %s
                        """,
                            (result.get("internal_dedup_key"),),
                        )

                        pre_analyzed_job = cursor.fetchone()

                        if not pre_analyzed_job:
                            logger.warning(
                                f"Pre-analyzed job not found for dedup key: {result.get('internal_dedup_key')}"
                            )
                            skipped_count += 1
                            continue

                        # Create analyzed_jobs deduplication key
                        analyzed_dedup_key = self._create_analyzed_dedup_key(
                            job_title=pre_analyzed_job[2],
                            company_id=str(pre_analyzed_job[1]),
                            primary_industry=result.get("primary_industry", ""),
                        )

                        # Check for duplicates in analyzed_jobs
                        if self._check_analyzed_duplicate(cursor, analyzed_dedup_key):
                            logger.debug(f"Analyzed job duplicate found: {pre_analyzed_job[2]}")
                            skipped_count += 1
                            continue

                        # Insert into analyzed_jobs
                        self._insert_analyzed_job(cursor, pre_analyzed_job, result, analyzed_dedup_key)
                        saved_count += 1

                        # Mark pre_analyzed_job as processed
                        cursor.execute(
                            """
                            UPDATE pre_analyzed_jobs 
                            SET queued_for_analysis = false,
                                processed_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """,
                            (pre_analyzed_job[0],),
                        )

                    conn.commit()

                    logger.info(f"AI analysis results saved: {saved_count} new, {skipped_count} skipped")

                    return {
                        "success": True,
                        "saved_count": saved_count,
                        "skipped_count": skipped_count,
                        "total_processed": len(analysis_results),
                        "message": f"Saved {saved_count} analyzed jobs, skipped {skipped_count} duplicates",
                    }

        except Exception as e:
            logger.error(f"Error saving AI analysis results: {e}")
            return {"success": False, "error": str(e), "saved_count": 0, "skipped_count": 0}

    def get_workflow_statistics(self) -> Dict:
        """
        Get comprehensive statistics about the new workflow.

        Returns:
            Dict containing statistics for each stage of the workflow
        """
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    stats = {}

                    # Raw job scrapes
                    cursor.execute("SELECT COUNT(*) FROM raw_job_scrapes")
                    stats["raw_job_scrapes"] = cursor.fetchone()[0]

                    # Cleaned job scrapes
                    cursor.execute("SELECT COUNT(*) FROM cleaned_job_scrapes")
                    stats["cleaned_job_scrapes"] = cursor.fetchone()[0]

                    # Pre-analyzed jobs
                    cursor.execute("SELECT COUNT(*) FROM pre_analyzed_jobs")
                    stats["pre_analyzed_jobs"] = cursor.fetchone()[0]

                    cursor.execute("SELECT COUNT(*) FROM pre_analyzed_jobs WHERE queued_for_analysis = true")
                    stats["pre_analyzed_queued"] = cursor.fetchone()[0]

                    # Analyzed jobs
                    cursor.execute("SELECT COUNT(*) FROM analyzed_jobs")
                    stats["analyzed_jobs"] = cursor.fetchone()[0]

                    cursor.execute("SELECT COUNT(*) FROM analyzed_jobs WHERE ai_analysis_completed = true")
                    stats["analysis_completed"] = cursor.fetchone()[0]

                    # Legacy jobs table (for comparison)
                    cursor.execute("SELECT COUNT(*) FROM jobs")
                    stats["legacy_jobs"] = cursor.fetchone()[0]

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

        except Exception as e:
            logger.error(f"Error getting workflow statistics: {e}")
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

    def _check_pre_analyzed_duplicate(self, cursor, dedup_key: str) -> bool:
        """Check if job already exists in pre_analyzed_jobs."""
        cursor.execute("SELECT 1 FROM pre_analyzed_jobs WHERE deduplication_key = %s", (dedup_key,))
        return cursor.fetchone() is not None

    def _check_analyzed_duplicate(self, cursor, dedup_key: str) -> bool:
        """Check if job already exists in analyzed_jobs."""
        cursor.execute("SELECT 1 FROM analyzed_jobs WHERE deduplication_key = %s", (dedup_key,))
        return cursor.fetchone() is not None

    def _resolve_company_id(self, cursor, company_name: str) -> Optional[str]:
        """Resolve company name to company_id, create if not exists."""
        if not company_name:
            return None

        # Check if company exists
        cursor.execute("SELECT id FROM companies WHERE LOWER(name) = LOWER(%s)", (company_name,))
        result = cursor.fetchone()

        if result:
            return str(result[0])

        # Create new company
        cursor.execute(
            """
            INSERT INTO companies (name, created_at) 
            VALUES (%s, CURRENT_TIMESTAMP) 
            RETURNING id
        """,
            (company_name,),
        )

        return str(cursor.fetchone()[0])

    def _insert_pre_analyzed_job(self, cursor, job_data: tuple, company_id: Optional[str], dedup_key: str):
        """Insert job into pre_analyzed_jobs table (same structure as cleaned_job_scrapes)."""
        cursor.execute(
            """
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
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
            )
        """,
            (
                job_data[0],  # cleaned_job_id
                company_id,  # company_id
                job_data[1],  # job_title
                job_data[2],  # company_name
                job_data[3],  # location_city
                job_data[4],  # location_province
                job_data[5],  # location_country
                job_data[6],  # work_arrangement
                job_data[7],  # salary_min
                job_data[8],  # salary_max
                job_data[9] or "CAD",  # salary_currency
                job_data[10],  # salary_period
                job_data[12],  # job_description
                job_data[13],  # requirements
                job_data[14],  # benefits (this is actually benefits, not industry)
                job_data[14],  # industry (fix this mapping)
                job_data[15],  # job_type
                job_data[16],  # experience_level
                job_data[17],  # posting_date
                job_data[18],  # application_deadline
                job_data[19],  # external_job_id
                job_data[20],  # source_website
                job_data[21],  # application_url
                job_data[22],  # application_email
                job_data[23],  # confidence_score
                1,  # duplicates_count
                dedup_key,  # deduplication_key
                True,  # is_active
                False,  # queued_for_analysis
            ),
        )

    def _insert_analyzed_job(self, cursor, pre_analyzed_data: tuple, ai_result: Dict, dedup_key: str):
        """Insert job into analyzed_jobs table with AI analysis results."""
        cursor.execute(
            """
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
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
            )
        """,
            (
                pre_analyzed_data[0],  # pre_analyzed_job_id
                pre_analyzed_data[1],  # company_id
                pre_analyzed_data[2],  # job_title
                pre_analyzed_data[3],  # job_description
                pre_analyzed_data[4],  # salary_min
                pre_analyzed_data[5],  # salary_max
                pre_analyzed_data[6],  # salary_period
                pre_analyzed_data[7],  # salary_currency
                pre_analyzed_data[8],  # work_arrangement
                pre_analyzed_data[9],  # job_type
                pre_analyzed_data[10],  # industry
                pre_analyzed_data[11],  # experience_level
                pre_analyzed_data[12],  # application_deadline
                pre_analyzed_data[13],  # application_email
                pre_analyzed_data[14],  # application_url
                pre_analyzed_data[15],  # posting_date
                pre_analyzed_data[16],  # external_job_id
                pre_analyzed_data[17],  # source_website
                True,  # ai_analysis_completed
                ai_result.get("primary_industry"),
                ai_result.get("authenticity_score"),
                dedup_key,
                "not_applied",  # application_status
                True,  # eligibility_flag
                datetime.utcnow(),  # analysis_date
                ai_result.get("model_used", "gemini-2.0-flash-001"),
            ),
        )
