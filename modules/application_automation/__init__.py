"""
Application Automation Module

This module provides automated job application form filling using Apify Actors
and Playwright. It supports Indeed application forms (MVP) with plans to expand
to other platforms.

Components:
- actor_main.py: Apify Actor entry point
- form_filler.py: Core Playwright automation logic
- data_fetcher.py: Fetch application data from Flask API
- screenshot_manager.py: Capture and store screenshots
- form_mappings/: Pre-mapped form selectors

Usage:
    from modules.application_automation import FormFiller, DataFetcher

    # For local testing (outside Apify)
    fetcher = DataFetcher(api_base_url="http://localhost:5000", api_key="your_key")
    data = fetcher.fetch_application_data(job_id="123", application_id="456")

    filler = FormFiller(headless=False)
    result = await filler.fill_application_form(data, application_id="456")
"""

from .data_fetcher import DataFetcher, ApplicationData, ApplicantProfile, JobDetails
from .form_filler import FormFiller, FormFillResult
from .screenshot_manager import ScreenshotManager, Screenshot

__all__ = [
    "DataFetcher",
    "ApplicationData",
    "ApplicantProfile",
    "JobDetails",
    "FormFiller",
    "FormFillResult",
    "ScreenshotManager",
    "Screenshot",
]

__version__ = "1.0.0"
