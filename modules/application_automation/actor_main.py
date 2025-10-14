"""
Apify Actor Entry Point for Application Automation

This is the main entry point for the Apify Actor that automates job applications.
It orchestrates the entire workflow: fetching data, filling forms, capturing
screenshots, and reporting results back to the Flask backend.

Usage:
    This actor is deployed to Apify platform and triggered via API calls from
    the Flask backend. It runs in a containerized environment with Playwright.

Input Schema:
    {
        "job_id": "string",           # Job posting ID from database
        "application_id": "string",   # Application tracking ID
        "api_base_url": "string",     # Flask API base URL
        "api_key": "string",          # API authentication key
        "headless": bool,             # Run browser in headless mode (default: true)
        "timeout": int                # Operation timeout in ms (default: 30000)
    }

Output Schema:
    {
        "success": bool,
        "application_id": "string",
        "job_id": "string",
        "form_type": "string",
        "fields_filled": ["string"],
        "screenshots": [{"filename": "string", "url": "string"}],
        "submission_confirmed": bool,
        "error_message": "string"
    }
"""

import os
import sys
import logging
from typing import Dict, Any
from datetime import datetime
import traceback

# Apify SDK
from apify import Actor

# Add module directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import our automation modules
from data_fetcher import DataFetcher, ApplicationData
from form_filler import FormFiller, FormFillResult
from screenshot_manager import ScreenshotManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ApplicationAutomationActor:
    """
    Apify Actor for automated job application form filling

    This actor encapsulates the entire application automation workflow,
    from data fetching to form submission and result reporting.
    """

    def __init__(self):
        """Initialize actor"""
        self.data_fetcher = None
        self.form_filler = None
        self.screenshot_manager = None

    async def run(self) -> None:
        """
        Main actor execution method

        This method is called by Apify when the actor is triggered.
        It handles the complete workflow and manages all resources.
        """
        async with Actor:
            # Get input from Apify
            actor_input = await Actor.get_input() or {}

            logger.info("=" * 80)
            logger.info("Application Automation Actor Started")
            logger.info("=" * 80)

            # Validate input
            try:
                self._validate_input(actor_input)
            except ValueError as e:
                logger.error(f"Invalid input: {e}")
                await Actor.fail(f"Invalid input: {e}")
                return

            # Extract input parameters
            job_id = actor_input["job_id"]
            application_id = actor_input["application_id"]
            api_base_url = actor_input["api_base_url"]
            api_key = actor_input["api_key"]
            headless = actor_input.get("headless", True)
            timeout = actor_input.get("timeout", 30000)

            logger.info(f"Job ID: {job_id}")
            logger.info(f"Application ID: {application_id}")
            logger.info(f"API Base URL: {api_base_url}")
            logger.info(f"Headless: {headless}")
            logger.info(f"Timeout: {timeout}ms")

            try:
                # Initialize components
                self.data_fetcher = DataFetcher(api_base_url=api_base_url, api_key=api_key)
                self.screenshot_manager = ScreenshotManager()
                self.form_filler = FormFiller(
                    headless=headless, timeout=timeout, screenshot_manager=self.screenshot_manager
                )

                # Step 1: Fetch application data from Flask API
                logger.info("Step 1/4: Fetching application data from Flask API")
                application_data = await self._fetch_application_data(job_id, application_id)

                # Step 2: Fill application form
                logger.info("Step 2/4: Filling application form")
                fill_result = await self._fill_application_form(application_data, application_id)

                # Step 3: Report results back to Flask API
                logger.info("Step 3/4: Reporting results to Flask API")
                await self._report_results(fill_result, api_base_url, api_key)

                # Step 4: Push output to Apify dataset
                logger.info("Step 4/4: Saving results to Apify dataset")
                await Actor.push_data(fill_result.to_dict())

                # Set exit status
                if fill_result.success:
                    logger.info("=" * 80)
                    logger.info("APPLICATION AUTOMATION COMPLETED SUCCESSFULLY")
                    logger.info(f"Fields filled: {len(fill_result.fields_filled)}")
                    logger.info(f"Screenshots captured: {len(fill_result.screenshots)}")
                    logger.info(f"Submission confirmed: {fill_result.submission_confirmed}")
                    logger.info("=" * 80)
                    await Actor.exit()
                else:
                    logger.error("=" * 80)
                    logger.error("APPLICATION AUTOMATION FAILED")
                    logger.error(f"Error: {fill_result.error_message}")
                    logger.error("=" * 80)
                    await Actor.fail(fill_result.error_message)

            except Exception as e:
                logger.error(f"Actor execution failed: {e}")
                logger.error(traceback.format_exc())

                # Create failure result
                failure_result = {
                    "success": False,
                    "application_id": application_id,
                    "job_id": job_id,
                    "error_message": str(e),
                    "error_details": {"traceback": traceback.format_exc()},
                    "timestamp": datetime.utcnow().isoformat(),
                }

                # Push failure data
                await Actor.push_data(failure_result)

                # Report failure to Flask API
                try:
                    await self._report_failure(
                        application_id, str(e), api_base_url, api_key
                    )
                except Exception as report_error:
                    logger.error(f"Failed to report failure to API: {report_error}")

                await Actor.fail(str(e))

            finally:
                # Cleanup resources
                if self.data_fetcher:
                    self.data_fetcher.close()

    def _validate_input(self, actor_input: Dict[str, Any]) -> None:
        """
        Validate actor input parameters

        Args:
            actor_input: Input dictionary from Apify

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        required_fields = ["job_id", "application_id", "api_base_url", "api_key"]

        for field in required_fields:
            if not actor_input.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Validate URL format
        api_url = actor_input["api_base_url"]
        if not api_url.startswith("http://") and not api_url.startswith("https://"):
            raise ValueError(f"Invalid API base URL: {api_url}")

        # Validate timeout
        timeout = actor_input.get("timeout", 30000)
        if not isinstance(timeout, int) or timeout < 5000 or timeout > 120000:
            raise ValueError(f"Invalid timeout (must be 5000-120000ms): {timeout}")

        logger.debug("Input validation passed")

    async def _fetch_application_data(
        self, job_id: str, application_id: str
    ) -> ApplicationData:
        """
        Fetch application data from Flask API

        Args:
            job_id: Job posting ID
            application_id: Application tracking ID

        Returns:
            ApplicationData object with all required information

        Raises:
            Exception: If data fetching fails
        """
        try:
            application_data = self.data_fetcher.fetch_application_data(
                job_id=job_id, application_id=application_id
            )

            logger.info(f"Successfully fetched application data")
            logger.info(f"Job: {application_data.job.title} at {application_data.job.company}")
            logger.info(f"Applicant: {application_data.applicant.full_name}")
            logger.info(f"Resume available: {application_data.documents.has_resume()}")
            logger.info(f"Cover letter available: {application_data.documents.has_cover_letter()}")

            return application_data

        except Exception as e:
            logger.error(f"Failed to fetch application data: {e}")
            raise Exception(f"Data fetching failed: {e}")

    async def _fill_application_form(
        self, application_data: ApplicationData, application_id: str
    ) -> FormFillResult:
        """
        Fill application form using Playwright automation

        Args:
            application_data: Application data bundle
            application_id: Application tracking ID

        Returns:
            FormFillResult with success status and details

        Raises:
            Exception: If form filling encounters critical error
        """
        try:
            result = await self.form_filler.fill_application_form(
                application_data=application_data, application_id=application_id
            )

            if result.success:
                logger.info(f"Form filled successfully")
                logger.info(f"Form type: {result.form_type}")
                logger.info(f"Fields filled: {', '.join(result.fields_filled)}")
            else:
                logger.error(f"Form filling failed: {result.error_message}")

            return result

        except Exception as e:
            logger.error(f"Form filling error: {e}")
            raise Exception(f"Form filling failed: {e}")

    async def _report_results(
        self, result: FormFillResult, api_base_url: str, api_key: str
    ) -> None:
        """
        Report results back to Flask API

        Args:
            result: FormFillResult object
            api_base_url: Flask API base URL
            api_key: API authentication key

        Raises:
            Exception: If reporting fails
        """
        try:
            import requests

            endpoint = f"{api_base_url}/api/application-automation/submissions"

            payload = {
                "application_id": result.application_id,
                "job_id": result.job_id,
                "status": "submitted" if result.success else "failed",
                "form_platform": "indeed",
                "form_type": result.form_type,
                "fields_filled": result.fields_filled,
                "submission_confirmed": result.submission_confirmed,
                "confirmation_message": result.confirmation_message,
                "error_message": result.error_message,
                "error_details": result.error_details,
                "screenshot_count": len(result.screenshots),
                "screenshots": [s.to_dict() for s in result.screenshots],
                "submitted_at": datetime.utcnow().isoformat(),
            }

            response = requests.post(
                endpoint,
                json=payload,
                headers={"X-API-Key": api_key, "Content-Type": "application/json"},
                timeout=30,
            )

            response.raise_for_status()

            logger.info("Successfully reported results to Flask API")

        except Exception as e:
            logger.error(f"Failed to report results to API: {e}")
            # Don't raise - we don't want to fail the entire run if reporting fails
            # The results are already in Apify dataset

    async def _report_failure(
        self, application_id: str, error_message: str, api_base_url: str, api_key: str
    ) -> None:
        """
        Report failure to Flask API

        Args:
            application_id: Application tracking ID
            error_message: Error message
            api_base_url: Flask API base URL
            api_key: API authentication key
        """
        try:
            import requests

            endpoint = f"{api_base_url}/api/application-automation/submissions"

            payload = {
                "application_id": application_id,
                "status": "failed",
                "error_message": error_message,
                "submitted_at": datetime.utcnow().isoformat(),
            }

            response = requests.post(
                endpoint,
                json=payload,
                headers={"X-API-Key": api_key, "Content-Type": "application/json"},
                timeout=30,
            )

            response.raise_for_status()

        except Exception as e:
            logger.error(f"Failed to report failure: {e}")


# Main entry point for Apify Actor
async def main():
    """Main entry point for Apify Actor"""
    actor = ApplicationAutomationActor()
    await actor.run()


# Apify Actor execution
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
