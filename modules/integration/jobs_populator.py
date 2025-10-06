"""
Jobs Populator - Transfer cleaned job scrapes to the main jobs table
Phase 1 Step 1.1 Implementation
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class JobsPopulator:
    """
    Transfers data from cleaned_job_scrapes to the main jobs table
    Handles company resolution and duplicate detection
    """

    def __init__(self):
        self.db = DatabaseManager()

    def process_batch(self, batch_size: int = 50) -> Dict:
        """
        Process a batch of cleaned jobs with comprehensive batch processing

        Args:
            batch_size: Number of cleaned jobs to process in one batch

        Returns:
            Dict: Batch processing statistics
        """
        return self.transfer_cleaned_jobs_to_jobs_table(batch_size)

    def transfer_cleaned_jobs_to_jobs_table(self, batch_size: int = 50) -> Dict:
        """
        Transfer cleaned job scrapes to the main jobs table

        Args:
            batch_size: Number of cleaned jobs to process in one batch

        Returns:
            Dict: Transfer statistics
        """
        try:
            # Get unprocessed cleaned jobs
            cleaned_jobs = self._get_unprocessed_cleaned_jobs(batch_size)

            if not cleaned_jobs:
                logger.info("No unprocessed cleaned jobs found")
                return {"processed": 0, "jobs_created": 0, "companies_created": 0, "duplicates_skipped": 0}

            logger.info(f"Processing {len(cleaned_jobs)} cleaned jobs")

            processed_count = 0
            jobs_created = 0
            companies_created = 0
            duplicates_skipped = 0

            for cleaned_job in cleaned_jobs:
                try:
                    # Check for existing job to avoid duplicates
                    existing_job = self._find_existing_job(cleaned_job)

                    if existing_job:
                        logger.info(
                            f"Skipping duplicate job: {cleaned_job['job_title']} at {cleaned_job['company_name']}"
                        )
                        duplicates_skipped += 1
                    else:
                        # Resolve or create company
                        company_id = self._resolve_company(cleaned_job)
                        if not company_id:
                            # Create new company
                            company_id = self._create_company(cleaned_job)
                            companies_created += 1

                        # Create job record
                        job_id = self._create_job_record(cleaned_job, company_id)
                        jobs_created += 1
                        logger.info(f"Created job: {cleaned_job['job_title']} at {cleaned_job['company_name']}")

                    processed_count += 1

                except Exception as e:
                    logger.error(f"Error processing cleaned job {cleaned_job.get('cleaned_job_id', 'unknown')}: {e}")
                    continue

            result = {
                "processed": processed_count,
                "jobs_created": jobs_created,
                "companies_created": companies_created,
                "duplicates_skipped": duplicates_skipped,
            }

            logger.info(f"Transfer completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in transfer_cleaned_jobs_to_jobs_table: {e}")
            raise

    def _get_unprocessed_cleaned_jobs(self, limit: int) -> List[Dict]:
        """Get cleaned jobs that haven't been transferred to jobs table yet"""
        query = """
            SELECT cjs.cleaned_job_id, cjs.job_title, cjs.company_name, cjs.location_city,
                   cjs.location_province, cjs.location_country, cjs.work_arrangement,
                   cjs.salary_min, cjs.salary_max, cjs.salary_currency, cjs.salary_period,
                   cjs.job_description, cjs.external_job_id, cjs.source_website,
                   cjs.application_url, cjs.job_type, cjs.posting_date,
                   cjs.application_email
            FROM cleaned_job_scrapes cjs
            LEFT JOIN jobs j ON j.primary_source_url = cjs.application_url
            WHERE j.id IS NULL
            ORDER BY cjs.cleaned_timestamp DESC
            LIMIT %s
        """

        results = self.db.execute_query(query, (limit,))
        if not results:
            return []

        # Convert rows to dictionaries using column names
        columns = [
            "cleaned_job_id",
            "job_title",
            "company_name",
            "location_city",
            "location_province",
            "location_country",
            "work_arrangement",
            "salary_min",
            "salary_max",
            "salary_currency",
            "salary_period",
            "job_description",
            "external_job_id",
            "source_website",
            "application_url",
            "job_type",
            "posting_date",
            "application_email",
        ]

        return [dict(zip(columns, row)) for row in results]

    def _find_existing_job(self, cleaned_job: Dict) -> Optional[Dict]:
        """Find existing job by title and company to avoid duplicates"""
        query = """
            SELECT j.id, j.job_title, c.name as company_name
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE LOWER(j.job_title) = LOWER(%s) 
              AND LOWER(c.name) = LOWER(%s)
              AND j.is_active = true
            LIMIT 1
        """

        results = self.db.execute_query(query, (cleaned_job["job_title"], cleaned_job["company_name"]))

        if results:
            row = results[0]
            return {"id": row[0], "job_title": row[1], "company_name": row[2]}
        return None

    def _resolve_company(self, cleaned_job: Dict) -> Optional[UUID]:
        """Find existing company by name"""
        query = """
            SELECT id FROM companies 
            WHERE LOWER(name) = LOWER(%s)
            LIMIT 1
        """

        results = self.db.execute_query(query, (cleaned_job["company_name"],))

        if results:
            return results[0][0]
        return None

    def _create_company(self, cleaned_job: Dict) -> UUID:
        """Create new company record"""
        company_id = uuid4()

        query = """
            INSERT INTO companies (
                id, name, created_at
            ) VALUES (%s, %s, %s)
            RETURNING id
        """

        params = (company_id, cleaned_job["company_name"], datetime.now())

        result = self.db.execute_query(query, params)
        logger.info(f"Created company: {cleaned_job['company_name']}")

        return company_id

    def _create_job_record(self, cleaned_job: Dict, company_id: UUID) -> UUID:
        """Create new job record in the jobs table"""
        job_id = uuid4()

        # Map cleaned job data to jobs table schema
        query = """
            INSERT INTO jobs (
                id, company_id, job_title, job_description, salary_low, salary_high,
                salary_period, remote_options, job_type, industry, application_deadline,
                is_active, application_method, primary_source_url, posted_date,
                office_city, office_province, office_country, compensation_currency,
                application_email, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """

        # Map work arrangement to remote options
        remote_options = self._map_work_arrangement(cleaned_job.get("work_arrangement"))

        # Default industry based on job title (can be enhanced with AI later)
        industry = self._infer_industry(cleaned_job.get("job_title", ""))

        params = (
            job_id,
            company_id,
            cleaned_job["job_title"],
            cleaned_job.get("job_description"),
            cleaned_job.get("salary_min"),
            cleaned_job.get("salary_max"),
            cleaned_job.get("salary_period", "annually"),
            remote_options,
            cleaned_job.get("job_type", "full-time"),
            industry,
            None,  # application_deadline - not available from scrapes
            True,  # is_active
            "online",  # application_method
            cleaned_job.get("application_url"),
            cleaned_job.get("posting_date"),
            cleaned_job.get("location_city"),
            cleaned_job.get("location_province"),
            cleaned_job.get("location_country", "Canada"),
            cleaned_job.get("salary_currency", "CAD"),
            cleaned_job.get("application_email"),
            datetime.now(),
        )

        result = self.db.execute_query(query, params)
        return job_id

    def _map_work_arrangement(self, work_arrangement: str) -> str:
        """Map work arrangement to remote options format"""
        if not work_arrangement:
            return "onsite"

        arrangement_lower = work_arrangement.lower()
        if "remote" in arrangement_lower:
            return "remote"
        elif "hybrid" in arrangement_lower:
            return "hybrid"
        else:
            return "onsite"

    def _infer_industry(self, job_title: str) -> Optional[str]:
        """Basic industry inference from job title"""
        if not job_title:
            return None

        title_lower = job_title.lower()

        # Simple keyword matching for common industries
        if any(keyword in title_lower for keyword in ["marketing", "digital marketing", "communications"]):
            return "Marketing & Communications"
        elif any(keyword in title_lower for keyword in ["software", "developer", "programmer", "engineer"]):
            return "Technology"
        elif any(keyword in title_lower for keyword in ["financial", "finance", "analyst", "accounting"]):
            return "Finance & Accounting"
        elif any(keyword in title_lower for keyword in ["sales", "business development"]):
            return "Sales"
        elif any(keyword in title_lower for keyword in ["hr", "human resources", "recruiter"]):
            return "Human Resources"
        else:
            return "General"
