"""
Intelligent Job Scraper
Uses preference packages to perform targeted job searches

EDUCATIONAL PURPOSE ONLY:
This system is designed for educational and research purposes only.
All scraping activities must comply with website Terms of Service and applicable laws.
Use responsibly for learning automation and job search concepts.
"""

import logging
from typing import Dict, List, Optional
from modules.preference_packages import PreferencePackages
from modules.scraping.job_scraper_apify import ApifyJobScraper
from modules.content.job_application_system import JobApplicationSystem

logger = logging.getLogger(__name__)


class IntelligentScraper:
    """
    Combines preference packages with Apify scraper for targeted job searches
    """

    def __init__(self):
        self.preference_packages = PreferencePackages()
        self.apify_scraper = ApifyJobScraper()
        self.app_system = JobApplicationSystem()

    def run_targeted_scrape(self, user_id: str, max_jobs_per_package: int = 50) -> Dict:
        """
        Run targeted job scraping based on user's preference packages

        Args:
            user_id: User identifier
            max_jobs_per_package: Maximum jobs to scrape per package

        Returns:
            Dict with scraping results and statistics
        """
        logger.info(f"Starting intelligent scrape for user {user_id}")

        # Get user's targeted search configurations
        search_configs = self.preference_packages.get_targeted_search_configs(user_id)

        if not search_configs:
            logger.warning(f"No preference packages found for user {user_id}")
            return {
                "success": False,
                "error": "No preference packages configured",
                "packages_processed": 0,
                "total_jobs_scraped": 0,
            }

        results = {
            "success": True,
            "packages_processed": 0,
            "total_jobs_scraped": 0,
            "package_results": [],
            "eligible_jobs": 0,
            "applications_generated": 0,
        }

        for config in search_configs:
            try:
                package_result = self._scrape_package(user_id, config, max_jobs_per_package)
                results["package_results"].append(package_result)
                results["packages_processed"] += 1
                results["total_jobs_scraped"] += package_result["jobs_scraped"]
                results["eligible_jobs"] += package_result["eligible_jobs"]
                results["applications_generated"] += package_result["applications_generated"]

                logger.info(
                    f"Package '{config['package_name']}': {package_result['jobs_scraped']} jobs, {package_result['eligible_jobs']} eligible"
                )

            except Exception as e:
                logger.error(f"Error processing package '{config['package_name']}': {e}")
                results["package_results"].append(
                    {
                        "package_name": config["package_name"],
                        "success": False,
                        "error": str(e),
                        "jobs_scraped": 0,
                        "eligible_jobs": 0,
                        "applications_generated": 0,
                    }
                )

        logger.info(
            f"Intelligent scrape completed: {results['total_jobs_scraped']} total jobs, {results['eligible_jobs']} eligible"
        )
        return results

    def _scrape_package(self, user_id: str, config: Dict, max_jobs: int) -> Dict:
        """
        Scrape jobs for a specific preference package

        Args:
            user_id: User identifier
            config: Package search configuration
            max_jobs: Maximum jobs to scrape

        Returns:
            Dict with package scraping results
        """
        package_name = config["package_name"]
        logger.info(f"Processing package: {package_name}")

        # Prepare Apify search configurations
        apify_configs = []

        for job_title in config.get("job_titles", ["Marketing Manager"]):
            for location in config.get("locations", ["Edmonton, AB"]):
                apify_config = {"job_title": job_title, "location": location, "country": "CA"}

                # Add salary filters if available
                if "salary_min" in config:
                    apify_config["salary_min"] = config["salary_min"]
                if "salary_max" in config:
                    apify_config["salary_max"] = config["salary_max"]

                # Add work arrangement filters
                if "remote_work" in config:
                    apify_config["remote_work"] = config["remote_work"]

                apify_configs.append(apify_config)

        # Limit the number of search combinations to control costs
        apify_configs = apify_configs[:3]  # Max 3 search combinations per package

        # Scrape jobs using Apify
        try:
            jobs = self.apify_scraper.scrape_jobs(apify_configs)

            # Save jobs to database
            saved_count = self.apify_scraper.save_jobs_to_database(jobs)

            # Process jobs through eligibility system
            eligible_jobs = 0
            applications_generated = 0

            for job in jobs:
                # Check eligibility using the specific package context
                package_context = self._create_job_context(job, config)

                # Get the matching preference package for this job
                matching_package = self.preference_packages.get_matching_package(user_id, package_context)

                if matching_package and self.app_system.check_job_eligibility(job["job_id"]):
                    eligible_jobs += 1

                    # Generate application package if eligible
                    try:
                        self.app_system.generate_application_package(job["job_id"])
                        applications_generated += 1
                    except Exception as e:
                        logger.warning(f"Failed to generate application for job {job['job_id']}: {e}")

            return {
                "package_name": package_name,
                "success": True,
                "jobs_scraped": len(jobs),
                "jobs_saved": saved_count,
                "eligible_jobs": eligible_jobs,
                "applications_generated": applications_generated,
                "search_configs_used": len(apify_configs),
            }

        except Exception as e:
            logger.error(f"Error scraping jobs for package {package_name}: {e}")
            return {
                "package_name": package_name,
                "success": False,
                "error": str(e),
                "jobs_scraped": 0,
                "jobs_saved": 0,
                "eligible_jobs": 0,
                "applications_generated": 0,
            }

    def _create_job_context(self, job: Dict, package_config: Dict) -> Dict:
        """
        Create job context for preference matching

        Args:
            job: Job data from scraper
            package_config: Package configuration

        Returns:
            Job context dict for preference matching
        """
        return {
            "job_id": job.get("job_id"),
            "location": job.get("location", ""),
            "salary_low": job.get("salary_low", 0),
            "salary_high": job.get("salary_high", 0),
            "remote_work": job.get("remote_work", ""),
            "company_size": job.get("company_size", ""),
            "industry": job.get("industry", ""),
            "job_type": job.get("job_type", ""),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "package_context": {
                "package_name": package_config["package_name"],
                "package_id": package_config.get("package_id"),
            },
        }

    def get_package_performance(self, user_id: str, days: int = 30) -> List[Dict]:
        """
        Get performance statistics for each preference package

        Args:
            user_id: User identifier
            days: Number of days to analyze

        Returns:
            List of package performance metrics
        """
        # This would query the database for historical performance
        # For now, return placeholder structure
        return [
            {
                "package_name": "Local Edmonton Jobs",
                "jobs_scraped": 45,
                "eligible_jobs": 12,
                "applications_sent": 8,
                "response_rate": 0.25,
                "cost_per_eligible_job": 1.85,
            },
            {
                "package_name": "Regional Alberta Jobs",
                "jobs_scraped": 23,
                "eligible_jobs": 6,
                "applications_sent": 4,
                "response_rate": 0.50,
                "cost_per_eligible_job": 5.00,
            },
            {
                "package_name": "Remote-First Opportunities",
                "jobs_scraped": 67,
                "eligible_jobs": 18,
                "applications_sent": 15,
                "response_rate": 0.33,
                "cost_per_eligible_job": 1.86,
            },
        ]


def initialize_steve_glen_preferences():
    """
    Initialize Steve Glen's preference packages if they don't exist
    """
    from modules.preference_packages import create_steve_glen_packages

    try:
        # Check if packages already exist
        pp = PreferencePackages()
        existing_configs = pp.get_targeted_search_configs("steve_glen")

        if not existing_configs:
            logger.info("Creating Steve Glen's preference packages...")
            package_ids = create_steve_glen_packages()
            logger.info(f"Created packages: {package_ids}")
        else:
            logger.info(f"Found {len(existing_configs)} existing preference packages for Steve Glen")

    except Exception as e:
        logger.error(f"Error initializing Steve Glen preferences: {e}")
        raise


if __name__ == "__main__":
    # Test the intelligent scraper
    logging.basicConfig(level=logging.INFO)

    # Initialize Steve Glen's preferences
    initialize_steve_glen_preferences()

    # Run intelligent scrape
    scraper = IntelligentScraper()
    results = scraper.run_targeted_scrape("steve_glen", max_jobs_per_package=20)

    print(f"Scraping Results:")
    print(f"- Packages processed: {results['packages_processed']}")
    print(f"- Total jobs scraped: {results['total_jobs_scraped']}")
    print(f"- Eligible jobs: {results['eligible_jobs']}")
    print(f"- Applications generated: {results['applications_generated']}")

    for package_result in results["package_results"]:
        print(
            f"  {package_result['package_name']}: {package_result['jobs_scraped']} jobs, {package_result['eligible_jobs']} eligible"
        )
