"""
Main Job Application System Orchestrator
Coordinates all components to run the complete automated job application workflow
"""

import logging
from typing import Dict, List
from ..scraping.job_scraper import JobScraper
from ..ai_job_description_analysis.llm_analyzer import LLMJobAnalyzer
from .content_manager import ContentManager
from ..link_tracker import LinkTracker
from ..database.database_client import DatabaseClient
from sqlalchemy import text


class JobApplicationSystem:
    """
    Main orchestrator for the automated job application system
    """

    def __init__(self):
        self.job_scraper = JobScraper()
        self.llm_analyzer = LLMJobAnalyzer()
        self.content_manager = ContentManager()
        self.link_tracker = LinkTracker()
        self.db_client = DatabaseClient()

        # Setup user preferences (simulated)
        self.setup_user_preferences()

    def setup_user_preferences(self):
        """
        Setup user job preferences - comprehensive job criteria for Steve Glen
        """
        logging.info("User preferences already configured in database with comprehensive criteria")

        # Verify preferences exist
        with self.db_client.get_session() as session:
            try:
                result = session.execute(text("SELECT COUNT(*) FROM user_job_preferences WHERE is_active = true"))
                count = result.fetchone()[0]
                if count == 0:
                    logging.warning("No active user preferences found - preferences should be configured manually")
                else:
                    logging.info(f"Found {count} active user preference profile(s)")
            except Exception as e:
                logging.warning(f"Could not verify preferences: {e}")

    def run_complete_workflow(self) -> Dict:
        """
        Run the complete job application workflow
        """
        logging.info("Starting complete job application workflow")

        # 1. Initialize content library
        self.content_manager.seed_content_library()

        # 2. Scrape jobs (simulated APify)
        job_ids = self.job_scraper.run_job_scrape("marketing manager", "Edmonton, Alberta")

        # 3. Analyze jobs with LLM
        analysis_results = self.llm_analyzer.batch_analyze_jobs(job_ids)

        # 4. Check eligibility and set flags
        eligible_jobs = self.check_job_eligibility(job_ids)

        # 5. Generate application packages for eligible jobs
        application_packages = []
        for job_id in eligible_jobs[:2]:  # Limit to 2 applications for demo
            try:
                package = self.generate_application_package(job_id)
                application_packages.append(package)
            except Exception as e:
                logging.error(f"Failed to generate package for job {job_id}: {e}")

        results = {
            "jobs_scraped": len(job_ids),
            "jobs_analyzed": len(analysis_results),
            "eligible_jobs": len(eligible_jobs),
            "applications_generated": len(application_packages),
            "job_ids": job_ids,
            "eligible_job_ids": eligible_jobs,
            "application_packages": application_packages,
        }

        logging.info(
            f"Workflow completed: {results['applications_generated']} applications generated from {results['jobs_scraped']} scraped jobs"
        )
        return results

    def check_job_eligibility(self, job_ids: List[str]) -> List[str]:
        """
        Check which jobs meet comprehensive user preferences and mark as eligible
        """
        eligible_jobs = []

        with self.db_client.get_session() as session:
            # Get comprehensive user preferences
            pref_result = session.execute(
                """
                SELECT salary_minimum, salary_maximum, work_arrangement, travel_percentage_maximum,
                       preferred_city, preferred_province_state, preferred_country,
                       preferred_industries, excluded_industries, experience_level_minimum,
                       experience_level_maximum, hours_per_week_minimum, hours_per_week_maximum,
                       industry_prestige_importance, work_life_balance_importance,
                       company_size_minimum, company_size_maximum
                FROM user_job_preferences WHERE is_active = true LIMIT 1
            """
            )
            preferences = pref_result.fetchone()

            if not preferences:
                logging.warning("No active user preferences found - using fallback eligibility")
                return job_ids[:2]  # Return first 2 jobs as fallback

            # Check each job against comprehensive criteria
            for job_id in job_ids:
                result = session.execute(
                    """
                    SELECT j.salary_low, j.salary_high, j.experience_level, j.industry, 
                           j.remote_friendly, j.title, j.location_city, j.location_province, 
                           j.location_country, j.employment_type, c.size, j.description
                    FROM jobs j 
                    LEFT JOIN companies c ON j.company_id = c.id
                    WHERE j.id = %s
                """,
                    (job_id,),
                )
                job = result.fetchone()

                if not job:
                    continue

                is_eligible = True
                eligibility_reasons = []

                # Salary eligibility check
                if preferences[0] and job[0] and job[0] < preferences[0]:  # salary_minimum
                    is_eligible = False
                    eligibility_reasons.append(f"Salary ${job[0]} below minimum ${preferences[0]}")

                # Location eligibility check
                if preferences[4] and job[6]:  # preferred_city
                    if preferences[4].lower() not in job[6].lower():
                        is_eligible = False
                        eligibility_reasons.append(f"Location {job[6]} not in preferred city {preferences[4]}")

                if preferences[5] and job[7]:  # preferred_province_state
                    if preferences[5].lower() not in job[7].lower():
                        is_eligible = False
                        eligibility_reasons.append(f"Province {job[7]} not preferred")

                # Industry eligibility check
                if preferences[7]:  # preferred_industries (array)
                    industry_match = False
                    for pref_industry in preferences[7]:
                        if job[3] and pref_industry.lower() in job[3].lower():
                            industry_match = True
                            break
                    if not industry_match:
                        is_eligible = False
                        eligibility_reasons.append(f"Industry {job[3]} not in preferred list")

                if preferences[8]:  # excluded_industries (array)
                    for excluded_industry in preferences[8]:
                        if job[3] and excluded_industry.lower() in job[3].lower():
                            is_eligible = False
                            eligibility_reasons.append(f"Industry {job[3]} in excluded list")
                            break

                # Experience level eligibility check
                experience_levels = ["entry", "mid", "senior", "lead", "executive"]
                if preferences[9] and job[2]:  # experience_level_minimum
                    try:
                        min_idx = experience_levels.index(preferences[9])
                        job_idx = experience_levels.index(job[2]) if job[2] in experience_levels else 1
                        if job_idx < min_idx:
                            is_eligible = False
                            eligibility_reasons.append(f"Experience level {job[2]} below minimum {preferences[9]}")
                    except ValueError:
                        pass  # Handle invalid experience levels gracefully

                if preferences[10] and job[2]:  # experience_level_maximum
                    try:
                        max_idx = experience_levels.index(preferences[10])
                        job_idx = experience_levels.index(job[2]) if job[2] in experience_levels else 1
                        if job_idx > max_idx:
                            is_eligible = False
                            eligibility_reasons.append(f"Experience level {job[2]} above maximum {preferences[10]}")
                    except ValueError:
                        pass  # Handle invalid experience levels gracefully

                # Company size eligibility check
                if preferences[15] and job[10] and job[10] < preferences[15]:  # company_size_minimum
                    is_eligible = False
                    eligibility_reasons.append(f"Company size {job[10]} below minimum {preferences[15]}")

                if preferences[16] and job[10] and job[10] > preferences[16]:  # company_size_maximum
                    is_eligible = False
                    eligibility_reasons.append(f"Company size {job[10]} above maximum {preferences[16]}")

                # Update job record and log decision
                if is_eligible:
                    session.execute(
                        """
                        UPDATE jobs SET 
                            eligibility_flag = true,
                            application_method = 'email'
                        WHERE id = %s
                    """,
                        (job_id,),
                    )
                    eligible_jobs.append(job_id)
                    logging.info(f"✓ Job {job_id} ({job[5]}) is eligible - meets all criteria")
                else:
                    session.execute(
                        """
                        UPDATE jobs SET 
                            eligibility_flag = false,
                            application_method = null
                        WHERE id = %s
                    """,
                        (job_id,),
                    )
                    logging.info(f"✗ Job {job_id} ({job[5]}) rejected: {', '.join(eligibility_reasons)}")

        logging.info(f"Comprehensive eligibility check complete: {len(eligible_jobs)} of {len(job_ids)} jobs eligible")
        return eligible_jobs

    def generate_application_package(self, job_id: str) -> Dict:
        """
        Generate complete application package for a job
        """
        # Generate application package
        package = self.content_manager.generate_application_package(job_id)

        # Generate tracked links
        tracked_links = self.link_tracker.generate_tracked_links(job_id, package["application_id"])

        # Update email content with tracked links
        email_content = package["email"]
        email_content["body"] = (
            email_content["body"]
            .replace("https://linkedin.com/in/steveglen", tracked_links["linkedin"])
            .replace("https://steveglen.com", tracked_links["portfolio"])
        )

        package["tracked_links"] = tracked_links

        # Mark job as applied
        with self.db_client.get_session() as session:
            session.execute(
                """
                UPDATE jobs SET 
                    application_status = 'applied',
                    last_application_attempt = CURRENT_TIMESTAMP
                WHERE id = %s
            """,
                (job_id,),
            )

        return package

    def get_system_stats(self) -> Dict:
        """
        Get comprehensive system statistics
        """
        with self.db_client.get_session() as session:
            # Job stats
            job_stats = session.execute(
                """
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(*) FILTER (WHERE eligibility_flag = true) as eligible_jobs,
                    COUNT(*) FILTER (WHERE application_status = 'applied') as applied_jobs,
                    COUNT(*) FILTER (WHERE analysis_completed = true) as analyzed_jobs
                FROM jobs
            """
            ).fetchone()

            # Application stats
            app_stats = session.execute(
                """
                SELECT 
                    COUNT(*) as total_applications,
                    AVG(tone_coherence_score) as avg_coherence_score,
                    AVG(total_tone_travel) as avg_tone_travel
                FROM job_applications
            """
            ).fetchone()

            # Content stats
            content_stats = session.execute(
                """
                SELECT 
                    (SELECT COUNT(*) FROM sentence_bank_resume WHERE stage = 'Approved') as resume_sentences,
                    (SELECT COUNT(*) FROM sentence_bank_cover_letter WHERE stage = 'Approved') as cover_letter_sentences
            """
            ).fetchone()

        return {
            "jobs": dict(job_stats._mapping) if job_stats else {},
            "applications": dict(app_stats._mapping) if app_stats else {},
            "content": dict(content_stats._mapping) if content_stats else {},
        }
