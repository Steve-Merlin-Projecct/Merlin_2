"""
APify Indeed Job Scraper Integration
Handles job scraping using the misceres/indeed-scraper actor on Apify platform

EDUCATIONAL PURPOSE ONLY:
This scraper is designed for educational and research purposes only.
Users must comply with Indeed's Terms of Service and applicable laws.
Respect rate limits and use responsibly for learning automation concepts.
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from apify_client import ApifyClient
from modules.database.database_manager import DatabaseManager
from .scrape_pipeline import ScrapeDataPipeline
from modules.security.security_manager import SecurityManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApifyJobScraper:
    """
    Handles job scraping using Apify's misceres/indeed-scraper actor
    """

    def __init__(self):
        """Initialize the Apify job scraper"""
        self.pipeline = ScrapeDataPipeline()
        self.security = SecurityManager()
        self.apify_token = os.environ.get("APIFY_TOKEN")
        self.actor_id = "misceres/indeed-scraper"
        self.base_url = "https://api.apify.com/v2"
        self.db_manager = DatabaseManager()
        self.client = ApifyClient(self.apify_token)

        if not self.apify_token:
            raise ValueError("APIFY_TOKEN environment variable is required")

        # Validate API token
        if not self.security.validate_apify_token(self.apify_token):
            raise ValueError("Invalid APIFY_TOKEN - token validation failed")

    def create_search_url(self, job_title: str, location: str, country: str = "CA") -> str:
        """
        Create Indeed search URL based on job criteria

        Args:
            job_title: Job title to search for
            location: Location (e.g., "Edmonton, AB")
            country: Country code (CA for Canada, US for USA)

        Returns:
            Indeed search URL
        """
        base_urls = {"CA": "https://ca.indeed.com/jobs", "US": "https://www.indeed.com/jobs"}

        base_url = base_urls.get(country, base_urls["CA"])

        # URL encode the parameters
        import urllib.parse

        params = {"q": job_title, "l": location}

        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"

    def start_scraping_run(self, search_configs: List[Dict], max_results: int = 100) -> str:
        """
        Start a scraping run using misceres/indeed-scraper with correct input format

        Args:
            search_configs: List of search configurations
            max_results: Maximum results to scrape

        Returns:
            Run ID from Apify
        """
        # Use misceres/indeed-scraper input format based on official schema
        primary_config = search_configs[0] if search_configs else {}

        input_data = {
            "position": primary_config.get("job_title", "Marketing Manager"),
            "country": primary_config.get("country", "CA"),
            "location": primary_config.get("location", "Edmonton, AB"),
            "maxItems": max_results,
            "parseCompanyDetails": False,
            "saveOnlyUniqueItems": True,
            "followApplyRedirects": False,
        }

        # If multiple search configs, add startUrls for additional searches
        if len(search_configs) > 1:
            start_urls = []
            for config in search_configs[1:]:  # Skip first config (used for position search)
                search_url = self.create_search_url(
                    config.get("job_title", ""), config.get("location", ""), config.get("country", "CA")
                )
                start_urls.append({"url": search_url})

            if start_urls:
                input_data["startUrls"] = start_urls
                input_data["maxItemsPerSearch"] = max_results // len(search_configs)

        # Start the actor run using Apify client (more reliable)
        try:
            run = self.client.actor(self.actor_id).call(run_input=input_data)
            run_id = run["id"]

            logger.info(f"Started Apify scraping run: {run_id}")
            return run_id
        except Exception as e:
            logger.error(f"Failed to start scraping run: {e}")
            raise Exception(f"Failed to start scraping run: {e}")

    def get_run_status(self, run_id: str) -> Dict:
        """
        Get the status of a scraping run

        Args:
            run_id: Apify run ID

        Returns:
            Run status information
        """
        url = f"{self.base_url}/acts/{self.actor_id}/runs/{run_id}"
        headers = {"Authorization": f"Bearer {self.apify_token}"}

        try:
            run_info = self.client.run(run_id).get()
            return run_info
        except Exception as e:
            raise Exception(f"Failed to get run status: {e}")

    def wait_for_completion(self, run_id: str, max_wait_minutes: int = 30) -> bool:
        """
        Wait for scraping run to complete

        Args:
            run_id: Apify run ID
            max_wait_minutes: Maximum time to wait

        Returns:
            True if completed successfully, False if timed out or failed
        """
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60

        while time.time() - start_time < max_wait_seconds:
            status = self.get_run_status(run_id)

            if status["status"] == "SUCCEEDED":
                logger.info(f"Scraping run {run_id} completed successfully")
                return True
            elif status["status"] == "FAILED":
                logger.error(f"Scraping run {run_id} failed: {status.get('statusMessage', '')}")
                return False
            elif status["status"] in ["RUNNING", "READY"]:
                logger.info(f"Scraping run {run_id} still running...")
                time.sleep(30)  # Check every 30 seconds
            else:
                logger.warning(f"Unexpected status for run {run_id}: {status['status']}")
                time.sleep(30)

        logger.error(f"Scraping run {run_id} timed out after {max_wait_minutes} minutes")
        return False

    def get_scraped_data(self, run_id: str) -> List[Dict]:
        """
        Get scraped data from completed run

        Args:
            run_id: Apify run ID

        Returns:
            List of scraped job data
        """
        url = f"{self.base_url}/acts/{self.actor_id}/runs/{run_id}/dataset/items"
        headers = {"Authorization": f"Bearer {self.apify_token}"}

        try:
            dataset_items = list(self.client.dataset(run_id).iterate_items())
            return dataset_items
        except Exception as e:
            raise Exception(f"Failed to get scraped data: {e}")

    def transform_job_data(self, raw_job: Dict) -> Dict:
        """
        Transform raw misceres/indeed-scraper data to our database format

        Args:
            raw_job: Raw job data from misceres/indeed-scraper (exact format from attached file)

        Returns:
            Transformed job data matching our database schema
        """
        # Extract salary information from misceres format - salary is now a STRING
        salary_low = None
        salary_high = None

        if raw_job.get("salary"):
            salary_low, salary_high = self._parse_salary_string(raw_job["salary"])

        # Extract job types - misceres returns as array
        job_type_str = None
        if raw_job.get("jobType") and isinstance(raw_job["jobType"], list):
            job_type_str = ", ".join(raw_job["jobType"])
        elif raw_job.get("jobType"):
            job_type_str = str(raw_job["jobType"])

        # Extract company information - now nested in companyInfo
        company_info = raw_job.get("companyInfo", {})
        company_logo = company_info.get("companyLogo")
        company_rating = raw_job.get("rating") or company_info.get("rating")  # Try both locations
        reviews_count = raw_job.get("reviewsCount") or company_info.get("reviewCount", 0)

        # Parse posting date - use postingDateParsed ISO timestamp if available
        posted_date = None
        if raw_job.get("postingDateParsed"):
            try:
                from datetime import datetime

                posted_date = datetime.fromisoformat(raw_job["postingDateParsed"].replace("Z", "+00:00"))
            except:
                posted_date = self._parse_date(raw_job.get("postedAt", ""))
        else:
            posted_date = self._parse_date(raw_job.get("postedAt", ""))

        return {
            "job_id": raw_job.get("id", ""),  # misceres uses 'id' field
            "title": raw_job.get("positionName", ""),  # misceres uses 'positionName'
            "company": raw_job.get("company", ""),
            "location": raw_job.get("location", ""),
            "description": raw_job.get("description", ""),
            "description_html": raw_job.get("descriptionHTML", ""),  # Additional field from misceres
            "salary_low": salary_low,
            "salary_high": salary_high,
            "job_type": job_type_str,
            "posted_date": posted_date,
            "apply_url": raw_job.get("url", ""),
            "external_apply_url": raw_job.get("externalApplyLink"),  # misceres specific field
            "company_rating": company_rating,
            "company_logo": company_logo or "",  # Handle None values
            "reviews_count": reviews_count,
            "is_expired": raw_job.get("isExpired", False),  # misceres tracks expiration
            "scraped_at": raw_job.get("scrapedAt", ""),  # misceres timestamp
            "remote_work": self._extract_remote_work(raw_job),
            "source": "indeed",
            "raw_data": json.dumps(raw_job),
        }

    def _parse_salary_string(self, salary_str: str) -> tuple:
        """
        Parse salary string like '$100,000–$110,000 a year' into low/high values

        Args:
            salary_str: Salary string from APIFY

        Returns:
            Tuple of (salary_low, salary_high) or (None, None)
        """
        if not salary_str:
            return None, None

        import re

        # Remove common non-numeric characters but keep numbers, commas, periods, and dashes
        cleaned = re.sub(r"[^\d,.\-–—]", " ", salary_str)

        # Find all numbers (handling commas as thousands separators)
        numbers = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?", cleaned)

        if len(numbers) >= 2:
            # Range format: convert to integers
            try:
                low = int(numbers[0].replace(",", ""))
                high = int(numbers[1].replace(",", ""))
                return low, high
            except ValueError:
                return None, None
        elif len(numbers) == 1:
            # Single salary value
            try:
                salary = int(numbers[0].replace(",", ""))
                return salary, salary
            except ValueError:
                return None, None

        return None, None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse relative date strings from Indeed"""
        if not date_str:
            return None

        now = datetime.now()
        date_str = date_str.lower()

        if "today" in date_str:
            return now
        elif "yesterday" in date_str:
            return now - timedelta(days=1)
        elif "days ago" in date_str:
            try:
                days = int(date_str.split()[0])
                return now - timedelta(days=days)
            except (ValueError, IndexError):
                return None
        elif "hours ago" in date_str:
            try:
                hours = int(date_str.split()[0])
                return now - timedelta(hours=hours)
            except (ValueError, IndexError):
                return None

        return None

    def _extract_remote_work(self, raw_job: Dict) -> Optional[str]:
        """Extract remote work information"""
        if raw_job.get("remoteLocation"):
            return "remote"
        elif raw_job.get("remoteWorkModel", {}).get("type"):
            return raw_job["remoteWorkModel"]["type"].lower()

        # Check job description for remote keywords
        description = raw_job.get("description", "") + " " + raw_job.get("snippet", "")
        description = description.lower()

        if any(keyword in description for keyword in ["remote", "work from home", "telecommute"]):
            return "remote"
        elif any(keyword in description for keyword in ["hybrid", "flexible"]):
            return "hybrid"

        return None

    def _extract_job_url(self, raw_job: Dict) -> str:
        """Extract the job URL from raw job data"""
        # Try multiple possible URL fields
        url = raw_job.get("url") or raw_job.get("link") or raw_job.get("jobUrl") or raw_job.get("externalApplyLink")

        if url:
            return url

        # Construct Indeed URL from job ID if available
        job_id = raw_job.get("id") or raw_job.get("jobId")
        if job_id:
            return f"https://ca.indeed.com/viewjob?jk={job_id}"

        # Fallback to search URL
        return "https://ca.indeed.com/jobs"

    def scrape_jobs(self, search_configs: List[Dict]) -> List[Dict]:
        """
        Complete job scraping workflow with security validation

        Args:
            search_configs: List of search configurations

        Returns:
            List of processed job data
        """
        logger.info(f"Starting job scraping with {len(search_configs)} search configurations")

        # Security validation
        for config in search_configs:
            if not self.security.validate_search_params(config):
                raise ValueError(f"Invalid search parameters: {config}")

            # Check rate limits
            request_id = self.security.generate_request_signature(config)
            if not self.security.check_rate_limit("apify_request", request_id):
                raise Exception("Rate limit exceeded - too many scraping requests")

        # Log security event
        self.security.log_security_event(
            "scraping_started", {"config_count": len(search_configs), "actor_id": self.actor_id}
        )

        # Start scraping run
        run_id = self.start_scraping_run(search_configs)

        # Wait for completion
        if not self.wait_for_completion(run_id):
            raise Exception(f"Scraping run {run_id} did not complete successfully")

        # Get scraped data
        raw_jobs = self.get_scraped_data(run_id)
        logger.info(f"Scraped {len(raw_jobs)} jobs from Indeed")

        # Store raw scrapes and transform data
        processed_jobs = []
        for raw_job in raw_jobs:
            try:
                # Sanitize raw data for security
                sanitized_job = self.security.sanitize_job_data(raw_job)

                # Store raw scrape data first
                source_url = self._extract_job_url(sanitized_job)
                scrape_id = self.pipeline.insert_raw_scrape(
                    source_website="indeed.ca",
                    source_url=source_url,
                    raw_data=sanitized_job,
                    scraper_used="apify/misceres-indeed-scraper",
                    scraper_run_id=run_id,
                    user_agent="ApifyJobScraper/1.0",
                )

                # Transform for legacy compatibility (using sanitized data)
                processed_job = self.transform_job_data(raw_job)
                processed_jobs.append(processed_job)
            except Exception as e:
                logger.error(f"Error processing job data: {e}")
                continue

        logger.info(f"Successfully processed {len(processed_jobs)} jobs")
        return processed_jobs

    def get_usage_stats(self) -> Dict:
        """Get Apify usage and cost statistics"""
        try:
            # Get account usage information
            account_info = self.client.user().get()

            return {
                "account_name": account_info.get("username", "Unknown"),
                "monthly_usage": account_info.get("usage", {}),
                "monthly_credits_limit": account_info.get("plan", {}).get("monthlyCredits", 0),
                "current_credits": account_info.get("usageStats", {}).get("credits", 0),
                "actor_id": self.actor_id,
                "estimated_cost_per_1000_jobs": 5.0,  # $5 per 1000 results
            }
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {"error": str(e), "actor_id": self.actor_id, "estimated_cost_per_1000_jobs": 5.0}

    def scrape_jobs_simple(self, input_data: Dict) -> Dict:
        """
        Simple job scraping method for API endpoints

        Args:
            input_data: Scraping parameters

        Returns:
            Results with scrape_id and job count
        """
        try:
            # Start scraping run
            run = self.client.actor(self.actor_id).call(run_input=input_data)
            run_id = run["id"]

            # Get scraped data
            dataset_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            # Store in pipeline
            job_count = 0
            for raw_job in dataset_items:
                try:
                    source_url = self._extract_job_url(raw_job)
                    self.pipeline.insert_raw_scrape(
                        source_website="indeed.ca",
                        source_url=source_url,
                        raw_data=raw_job,
                        scraper_used="apify/misceres-indeed-scraper",
                        scraper_run_id=run_id,
                        user_agent="ApifyJobScraper/1.0",
                    )
                    job_count += 1
                except Exception as e:
                    logger.error(f"Error storing job data: {e}")
                    continue

            # Calculate cost estimate
            cost_estimate = (job_count / 1000) * 5.0  # $5 per 1000 jobs

            return {
                "scrape_id": run_id,
                "jobs_scraped": job_count,
                "cost_estimate": cost_estimate,
                "processing_time": run.get("stats", {}).get("runTimeSecs", 0),
            }

        except Exception as e:
            logger.error(f"Error in simple scraping: {e}")
            raise Exception(f"Scraping failed: {e}")

    def save_jobs_to_database(self, jobs: List[Dict]) -> int:
        """
        Save scraped jobs to database

        Args:
            jobs: List of processed job data

        Returns:
            Number of jobs saved
        """
        saved_count = 0

        for job in jobs:
            try:
                # Check if job already exists
                existing_job = self.db_manager.execute_raw_sql(
                    "SELECT job_id FROM jobs WHERE job_id = %s", (job["job_id"],)
                )

                if not existing_job:
                    # Insert new job
                    self.db_manager.execute_raw_sql(
                        """
                        INSERT INTO jobs (
                            job_id, title, company, location, description, 
                            salary_low, salary_high, job_type, posted_date, 
                            apply_url, company_rating, remote_work, source, 
                            raw_data, scraped_at, status
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s
                        )
                    """,
                        (
                            job["job_id"],
                            job["title"],
                            job["company"],
                            job["location"],
                            job["description"],
                            job["salary_low"],
                            job["salary_high"],
                            job["job_type"],
                            job["posted_date"],
                            job["apply_url"],
                            job["company_rating"],
                            job["remote_work"],
                            job["source"],
                            job["raw_data"],
                            datetime.now(),
                            "scraped",
                        ),
                    )
                    saved_count += 1

            except Exception as e:
                logger.error(f"Error saving job {job.get('job_id', 'unknown')}: {e}")
                continue

        logger.info(f"Saved {saved_count} new jobs to database")
        return saved_count

    def get_monthly_job_count(self) -> int:
        """
        Get the number of jobs scraped in the current month

        Returns:
            Number of jobs scraped this month
        """
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        result = self.db_manager.execute_raw_sql(
            """
            SELECT COUNT(*) FROM jobs 
            WHERE scraped_at >= %s AND source = 'indeed'
        """,
            (current_month,),
        )

        return result[0][0] if result else 0


# Convenience function for direct use
def scrape_indeed_jobs(job_title: str = "Marketing Manager", location: str = "Edmonton, AB") -> List[Dict]:
    """
    Convenience function to scrape Indeed jobs

    Args:
        job_title: Job title to search for
        location: Location to search in

    Returns:
        List of processed job data
    """
    scraper = ApifyJobScraper()

    search_configs = [{"job_title": job_title, "location": location, "country": "CA"}]

    jobs = scraper.scrape_jobs(search_configs)
    scraper.save_jobs_to_database(jobs)

    return jobs
