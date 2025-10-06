"""
Job Population Module
Transfers cleaned job scrapes to the jobs table with company resolution
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4
from modules.database.database_manager import DatabaseManager
from modules.utils.fuzzy_matcher import fuzzy_matcher

logger = logging.getLogger(__name__)


class JobsPopulator:
    """
    Handles the transfer of cleaned job scrapes to the jobs table
    Includes company resolution and data mapping
    """

    def __init__(self):
        self.db = DatabaseManager()

        # Column mapping from cleaned_job_scrapes to jobs table
        self.COLUMN_MAPPING = {
            # Direct mappings
            "job_title": "job_title",
            "job_description": "job_description",
            "external_job_id": "job_number",
            "posting_date": "posted_date",
            "job_type": "job_type",
            "industry": "industry",
            "application_email": "application_email",
            # Renamed mappings
            "salary_min": "salary_low",
            "salary_max": "salary_high",
            "salary_currency": "compensation_currency",
            "experience_level": "seniority_level",
            "location_city": "office_city",
            "location_province": "office_province",
            "location_country": "office_country",
            "work_arrangement": "remote_options",
            "location_street_address": "office_address",
            "application_url": "primary_source_url",
        }

    def transfer_cleaned_scrapes_to_jobs(self, batch_size: int = 50) -> Dict:
        """
        Transfer unprocessed cleaned scrapes to jobs table

        Args:
            batch_size: Number of records to process in each batch

        Returns:
            Dictionary with transfer statistics
        """
        stats = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "companies_created": 0,
            "companies_matched": 0,
            "errors": [],
        }

        try:
            # Get unprocessed cleaned scrapes
            cleaned_scrapes = self._get_unprocessed_cleaned_scrapes(batch_size)

            if not cleaned_scrapes:
                logger.info("No unprocessed cleaned scrapes found")
                return stats

            logger.info(f"Processing {len(cleaned_scrapes)} cleaned scrapes")

            for scrape in cleaned_scrapes:
                stats["processed"] += 1

                try:
                    # CRITICAL: Check if a similar job already exists with AI analysis
                    existing_job = self._find_existing_analyzed_job(scrape.get("job_title"), scrape.get("company_name"))

                    if existing_job:
                        logger.info(
                            f"Skipping job '{scrape.get('job_title')}' - analyzed job exists (ID: {existing_job['id']})"
                        )
                        # Mark as processed but don't create duplicate
                        self._mark_cleaned_scrape_processed(scrape["cleaned_job_id"], existing_job["id"])
                        stats["successful"] += 1
                        continue

                    # Resolve company ID
                    company_id, is_new_company = self._resolve_company_id(
                        scrape.get("company_name"), scrape.get("company_website")
                    )

                    if is_new_company:
                        stats["companies_created"] += 1
                    else:
                        stats["companies_matched"] += 1

                    # Map cleaned data to jobs table format
                    jobs_data = self._map_cleaned_to_jobs_data(scrape, company_id)

                    # Validate data before insertion
                    if not self._validate_jobs_data(jobs_data):
                        stats["failed"] += 1
                        stats["errors"].append(f"Validation failed for job: {scrape.get('job_title')}")
                        continue

                    # Insert job record
                    job_id = self._insert_job_record(jobs_data)

                    if job_id:
                        # Mark cleaned scrape as processed
                        self._mark_cleaned_scrape_processed(scrape["cleaned_job_id"], job_id)
                        stats["successful"] += 1
                        logger.info(f"Successfully created job {job_id} from cleaned scrape {scrape['cleaned_job_id']}")
                    else:
                        stats["failed"] += 1
                        stats["errors"].append(f"Failed to insert job: {scrape.get('job_title')}")

                except Exception as e:
                    stats["failed"] += 1
                    error_msg = f"Error processing scrape {scrape.get('cleaned_job_id')}: {str(e)}"
                    stats["errors"].append(error_msg)
                    logger.error(error_msg)

            logger.info(f"Transfer completed: {stats['successful']}/{stats['processed']} successful")
            return stats

        except Exception as e:
            logger.error(f"Error in transfer_cleaned_scrapes_to_jobs: {str(e)}")
            stats["errors"].append(str(e))
            return stats

    def _get_unprocessed_cleaned_scrapes(self, limit: int) -> List[Dict]:
        """Get cleaned scrapes that haven't been transferred to jobs table"""
        query = """
            SELECT c.* FROM cleaned_job_scrapes c
            LEFT JOIN cleaned_job_scrape_sources s ON c.cleaned_job_id = s.cleaned_job_id
            WHERE s.processed_to_jobs IS NULL OR s.processed_to_jobs = false
            ORDER BY c.cleaned_timestamp DESC
            LIMIT %s
        """

        try:
            results = self.db.execute_query(query, (limit,))
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Error fetching unprocessed cleaned scrapes: {str(e)}")
            return []

    def _resolve_company_id(self, company_name: str, company_website: str = None) -> Tuple[UUID, bool]:
        """
        Resolve company name to company_id, creating company if needed

        Returns:
            Tuple of (company_id, is_new_company)
        """
        if not company_name:
            # Create a placeholder company for jobs without company names
            company_name = "Unknown Company"

        # First, try exact match
        company_id = self._find_company_by_name(company_name)
        if company_id:
            return company_id, False

        # Try fuzzy matching for similar names
        company_id = self._find_company_fuzzy_match(company_name)
        if company_id:
            return company_id, False

        # Create new company
        company_id = self._create_company_record(company_name, company_website)
        return company_id, True

    def _find_company_by_name(self, company_name: str) -> Optional[UUID]:
        """Find company by exact name match"""
        query = "SELECT id FROM companies WHERE LOWER(name) = LOWER(%s) LIMIT 1"

        try:
            result = self.db.execute_query(query, (company_name,))
            return result[0]["id"] if result else None
        except Exception as e:
            logger.error(f"Error finding company by name: {str(e)}")
            return None

    def _find_existing_analyzed_job(self, job_title: str, company_name: str) -> Optional[Dict]:
        """
        Find existing job with AI analysis completed to prevent overwriting

        CRITICAL DATA PROTECTION: This prevents AI-analyzed jobs from being overwritten
        by new raw scrapes that might contain the same job posting.
        Uses enhanced fuzzy matching for more accurate detection.
        """
        if not job_title or not company_name:
            return None

        try:
            # Get all analyzed jobs for potential matching
            query = """
                SELECT j.id, j.job_title, j.analysis_completed, j.company_id, c.name as company_name
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE j.analysis_completed = true
                ORDER BY j.created_at DESC
                LIMIT 50
            """

            analyzed_jobs = self.db.execute_query(query)

            if not analyzed_jobs:
                return None

            # Use enhanced fuzzy matching to find best match
            best_job_match = None
            best_combined_score = 0.0

            for job in analyzed_jobs:
                # Calculate job title similarity
                title_score = fuzzy_matcher.calculate_job_similarity(job_title, job["job_title"])

                # Calculate company name similarity
                company_score = fuzzy_matcher.calculate_company_similarity(company_name, job["company_name"])

                # Combined score (both must be reasonably high)
                if title_score >= 0.7 and company_score >= 0.8:
                    combined_score = (title_score * 0.6) + (company_score * 0.4)

                    if combined_score > best_combined_score:
                        best_combined_score = combined_score
                        best_job_match = job
                        best_job_match["_title_similarity"] = title_score
                        best_job_match["_company_similarity"] = company_score
                        best_job_match["_combined_score"] = combined_score

            if best_job_match:
                logger.info(
                    f"Found existing analyzed job: '{best_job_match['job_title']}' at '{best_job_match['company_name']}' "
                    f"(similarity: {best_combined_score:.2f})"
                )
                return best_job_match

            return None

        except Exception as e:
            logger.error(f"Error finding existing analyzed job: {str(e)}")
            return None

    def _find_company_fuzzy_match(self, company_name: str) -> Optional[UUID]:
        """Find company using enhanced fuzzy matching for similar names"""
        try:
            # Get all companies for fuzzy matching
            query = "SELECT id, name FROM companies ORDER BY created_at DESC LIMIT 100"
            companies = self.db.execute_query(query)

            if not companies:
                return None

            # Use enhanced fuzzy matching
            best_match = fuzzy_matcher.find_best_match(
                target=company_name, candidates=companies, field_name="name", match_type="company", threshold=0.8
            )

            if best_match:
                logger.info(
                    f"Fuzzy matched company '{company_name}' to '{best_match['name']}' "
                    f"(similarity: {best_match.get('_similarity_score', 0):.2f})"
                )
                return best_match["id"]

            return None

        except Exception as e:
            logger.error(f"Error in enhanced fuzzy company matching: {str(e)}")
            return None

    def _create_company_record(self, company_name: str, company_website: str = None) -> UUID:
        """Create a new company record"""
        company_id = uuid4()

        query = """
            INSERT INTO companies (
                id, name, company_url, created_at
            ) VALUES (%s, %s, %s, %s)
            RETURNING id
        """

        try:
            result = self.db.execute_query(query, (company_id, company_name, company_website, datetime.now()))

            logger.info(f"Created new company: {company_name} ({company_id})")
            return company_id

        except Exception as e:
            logger.error(f"Error creating company record: {str(e)}")
            raise

    def _map_cleaned_to_jobs_data(self, cleaned_record: Dict, company_id: UUID) -> Dict:
        """Map cleaned_job_scrapes record to jobs table format"""
        jobs_data = {
            "id": uuid4(),
            "company_id": company_id,
            "is_active": True,
            "analysis_completed": False,
            "application_status": "not_applied",
            "eligibility_flag": True,
            "created_at": datetime.now(),
        }

        # Apply column mappings
        for cleaned_col, jobs_col in self.COLUMN_MAPPING.items():
            if cleaned_record.get(cleaned_col) is not None:
                jobs_data[jobs_col] = cleaned_record[cleaned_col]

        # Handle special cases
        if cleaned_record.get("application_url"):
            # Truncate if too long for primary_source_url field
            url = cleaned_record["application_url"]
            jobs_data["primary_source_url"] = url[:500] if len(url) > 500 else url

        # Set salary period if not provided
        if cleaned_record.get("salary_min") and not cleaned_record.get("salary_period"):
            jobs_data["salary_period"] = "annual"  # Default assumption

        return jobs_data

    def _validate_jobs_data(self, jobs_data: Dict) -> bool:
        """Validate jobs data before insertion"""
        required_fields = ["job_title", "company_id"]

        for field in required_fields:
            if not jobs_data.get(field):
                logger.warning(f"Missing required field: {field}")
                return False

        # Validate data types and constraints
        if jobs_data.get("salary_low") and not isinstance(jobs_data["salary_low"], (int, float)):
            logger.warning("Invalid salary_low data type")
            return False

        if jobs_data.get("salary_high") and not isinstance(jobs_data["salary_high"], (int, float)):
            logger.warning("Invalid salary_high data type")
            return False

        return True

    def _insert_job_record(self, jobs_data: Dict) -> Optional[UUID]:
        """Insert job record into jobs table"""
        # Build dynamic INSERT query based on provided data
        columns = list(jobs_data.keys())
        placeholders = ", ".join(["%s"] * len(columns))
        column_names = ", ".join(columns)

        query = f"""
            INSERT INTO jobs ({column_names})
            VALUES ({placeholders})
            RETURNING id
        """

        values = list(jobs_data.values())

        try:
            result = self.db.execute_query(query, values)
            return result[0]["id"] if result else None
        except Exception as e:
            logger.error(f"Error inserting job record: {str(e)}")
            return None

    def _mark_cleaned_scrape_processed(self, cleaned_job_id: UUID, job_id: UUID) -> bool:
        """Mark cleaned scrape as processed and link to job"""
        query = """
            UPDATE cleaned_job_scrape_sources 
            SET processed_to_jobs = true, job_id = %s, processed_at = %s
            WHERE cleaned_job_id = %s
        """

        try:
            self.db.execute_query(query, (job_id, datetime.now(), cleaned_job_id))
            return True
        except Exception as e:
            logger.error(f"Error marking cleaned scrape as processed: {str(e)}")
            return False

    def get_transfer_statistics(self) -> Dict:
        """Get statistics about the transfer process"""
        query = """
            SELECT 
                COUNT(*) as total_cleaned,
                COUNT(CASE WHEN s.processed_to_jobs = true THEN 1 END) as processed,
                COUNT(CASE WHEN s.processed_to_jobs IS NULL OR s.processed_to_jobs = false THEN 1 END) as pending
            FROM cleaned_job_scrapes c
            LEFT JOIN cleaned_job_scrape_sources s ON c.cleaned_job_id = s.cleaned_job_id
        """

        try:
            result = self.db.execute_query(query)
            return dict(result[0]) if result else {}
        except Exception as e:
            logger.error(f"Error getting transfer statistics: {str(e)}")
            return {}
