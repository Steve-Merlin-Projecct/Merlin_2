"""
Form Filler for Indeed Application Automation

This module contains the core Playwright automation logic for filling out
Indeed job application forms. It uses pre-mapped selectors from form mappings
and implements robust error handling and retry logic.

Design Principles:
- Pre-mapped selectors for Indeed (MVP)
- Robust element detection with fallback strategies
- Comprehensive error handling and logging
- Screenshot capture at key points
- Auto-submit with post-review workflow

TODO: Future enhancement - Implement hybrid approach (pre-mapped + AI fallback)
"""

import os
import json
import logging
from typing import Dict, Optional, List, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import asyncio

from playwright.async_api import Page, Browser, Playwright, async_playwright, Error as PlaywrightError

from .data_fetcher import ApplicationData, ApplicantProfile, JobDetails
from .screenshot_manager import ScreenshotManager, Screenshot

logger = logging.getLogger(__name__)


@dataclass
class FormFillResult:
    """Result of form filling operation"""

    success: bool
    application_id: str
    job_id: str
    form_type: str
    fields_filled: List[str]
    screenshots: List[Screenshot]
    error_message: Optional[str] = None
    error_details: Optional[Dict] = None
    submission_confirmed: bool = False
    confirmation_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "application_id": self.application_id,
            "job_id": self.job_id,
            "form_type": self.form_type,
            "fields_filled": self.fields_filled,
            "screenshots": [s.to_dict() for s in self.screenshots],
            "error_message": self.error_message,
            "error_details": self.error_details,
            "submission_confirmed": self.submission_confirmed,
            "confirmation_message": self.confirmation_message,
        }


class FormFiller:
    """
    Fills out Indeed application forms using Playwright automation

    This class implements the core form filling logic using pre-mapped selectors
    from the Indeed form mappings file. It handles field detection, data entry,
    document upload, and form submission.
    """

    def __init__(
        self,
        headless: bool = True,
        slow_mo: int = 100,
        timeout: int = 30000,
        screenshot_manager: Optional[ScreenshotManager] = None,
    ):
        """
        Initialize form filler

        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by milliseconds (for debugging)
            timeout: Default timeout for operations in milliseconds
            screenshot_manager: Screenshot manager instance
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.timeout = timeout
        self.screenshot_manager = screenshot_manager or ScreenshotManager()

        # Load form mappings
        self.form_mappings = self._load_form_mappings()

        logger.info(
            f"FormFiller initialized (headless={headless}, slow_mo={slow_mo}ms, timeout={timeout}ms)"
        )

    def _load_form_mappings(self) -> Dict[str, Any]:
        """
        Load Indeed form mappings from JSON file

        Returns:
            Form mappings dictionary

        Raises:
            Exception: If mappings file not found or invalid
        """
        mappings_path = Path(__file__).parent / "form_mappings" / "indeed.json"

        try:
            with open(mappings_path, "r") as f:
                mappings = json.load(f)
                logger.info(f"Loaded form mappings for platform: {mappings.get('platform')}")
                return mappings
        except FileNotFoundError:
            raise Exception(f"Form mappings not found: {mappings_path}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid form mappings JSON: {e}")

    async def fill_application_form(
        self, application_data: ApplicationData, application_id: str
    ) -> FormFillResult:
        """
        Main method to fill out Indeed application form

        This is the primary entry point for form filling automation. It handles
        the entire workflow: navigation, form detection, field filling, document
        upload, screenshot capture, and submission.

        Args:
            application_data: Complete application data bundle
            application_id: Unique application ID for tracking

        Returns:
            FormFillResult with success status and details

        Raises:
            Exception: If critical error occurs (will be caught and logged)
        """
        screenshots = []
        fields_filled = []
        form_type = "unknown"

        try:
            logger.info(f"Starting form fill for application {application_id}")
            logger.info(f"Job: {application_data.job.title} at {application_data.job.company}")

            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)

                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                )

                page = await context.new_page()
                page.set_default_timeout(self.timeout)

                try:
                    # Navigate to application URL
                    logger.info(f"Navigating to: {application_data.job.apply_url}")
                    await page.goto(application_data.job.apply_url, wait_until="networkidle")

                    # Wait for page to load
                    await asyncio.sleep(2)

                    # Detect form type
                    form_type = await self._detect_form_type(page)
                    logger.info(f"Detected form type: {form_type}")

                    # Capture pre-submit screenshot
                    pre_submit_screenshot = await self.screenshot_manager.capture_screenshot(
                        page=page, screenshot_type="pre_submit", application_id=application_id
                    )
                    screenshots.append(pre_submit_screenshot)

                    # Fill form based on detected type
                    if form_type == "indeed_quick_apply":
                        fields_filled = await self._fill_quick_apply_form(page, application_data)
                    elif form_type == "standard_indeed_apply":
                        fields_filled = await self._fill_standard_form(page, application_data)
                    else:
                        raise Exception(f"Unknown form type: {form_type}")

                    logger.info(f"Successfully filled {len(fields_filled)} form fields")

                    # Submit form
                    submission_result = await self._submit_form(page, form_type)

                    # Wait for submission to process
                    await asyncio.sleep(3)

                    # Capture post-submit screenshot
                    post_submit_screenshot = await self.screenshot_manager.capture_screenshot(
                        page=page, screenshot_type="post_submit", application_id=application_id
                    )
                    screenshots.append(post_submit_screenshot)

                    # Verify submission
                    confirmation_message = await self._verify_submission(page, form_type)

                    return FormFillResult(
                        success=True,
                        application_id=application_id,
                        job_id=application_data.job.job_id,
                        form_type=form_type,
                        fields_filled=fields_filled,
                        screenshots=screenshots,
                        submission_confirmed=bool(confirmation_message),
                        confirmation_message=confirmation_message,
                    )

                finally:
                    await browser.close()

        except Exception as e:
            logger.error(f"Form filling failed for application {application_id}: {e}")

            # Capture error screenshot if possible
            try:
                if "page" in locals() and page:
                    error_screenshot = await self.screenshot_manager.capture_error_screenshot(
                        page=page, application_id=application_id, error_message=str(e)
                    )
                    if error_screenshot:
                        screenshots.append(error_screenshot)
            except Exception as screenshot_error:
                logger.error(f"Failed to capture error screenshot: {screenshot_error}")

            return FormFillResult(
                success=False,
                application_id=application_id,
                job_id=application_data.job.job_id,
                form_type=form_type,
                fields_filled=fields_filled,
                screenshots=screenshots,
                error_message=str(e),
                error_details={"error_type": type(e).__name__, "error_message": str(e)},
            )

    async def _detect_form_type(self, page: Page) -> str:
        """
        Detect which type of Indeed form is present

        Uses detection strategy from form mappings to identify form type.

        Args:
            page: Playwright page object

        Returns:
            Form type identifier (e.g., 'indeed_quick_apply', 'standard_indeed_apply')

        Raises:
            Exception: If no form type detected
        """
        detection = self.form_mappings.get("detection_strategy", {})
        priority_order = detection.get("priority_order", [])
        timeout = detection.get("detection_timeout_ms", 5000)

        for form_type in priority_order:
            form_config = self.form_mappings["form_types"].get(form_type)
            if not form_config:
                continue

            logger.debug(f"Checking for form type: {form_type}")

            # Check URL patterns
            url_patterns = form_config.get("url_patterns", [])
            current_url = page.url
            for pattern in url_patterns:
                pattern_regex = pattern.replace("*", ".*")
                if pattern_regex in current_url:
                    logger.debug(f"URL pattern matched: {pattern}")
                    return form_type

            # Check for key elements
            fields = form_config.get("fields", {})
            for field_name, field_config in fields.items():
                selectors = field_config.get("selectors", [])
                for selector in selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=timeout)
                        if element:
                            logger.debug(f"Found form element: {field_name} with selector {selector}")
                            return form_type
                    except PlaywrightError:
                        continue

        raise Exception("Could not detect Indeed form type - no matching selectors found")

    async def _fill_standard_form(self, page: Page, data: ApplicationData) -> List[str]:
        """
        Fill standard Indeed application form

        Args:
            page: Playwright page object
            data: Application data

        Returns:
            List of successfully filled field names

        Raises:
            Exception: If critical field filling fails
        """
        form_config = self.form_mappings["form_types"]["standard_indeed_apply"]
        fields = form_config["fields"]
        filled_fields = []

        # Map data to form fields
        field_data = {
            "full_name": data.applicant.full_name,
            "email": data.applicant.email,
            "phone": data.applicant.phone,
            "location": data.applicant.location,
            "linkedin_url": data.applicant.linkedin_url,
            "website": data.applicant.website,
            "years_experience": data.applicant.years_experience,
        }

        # Fill text fields
        for field_name, value in field_data.items():
            if not value:
                continue

            field_config = fields.get(field_name)
            if not field_config:
                continue

            try:
                filled = await self._fill_field(page, field_name, value, field_config)
                if filled:
                    filled_fields.append(field_name)
            except Exception as e:
                logger.warning(f"Failed to fill field {field_name}: {e}")
                if field_config.get("required"):
                    raise Exception(f"Failed to fill required field: {field_name}")

        # Upload resume
        if data.documents.has_resume():
            try:
                await self._upload_document(page, "resume", data.documents, fields["resume"])
                filled_fields.append("resume")
            except Exception as e:
                logger.error(f"Failed to upload resume: {e}")
                raise Exception("Failed to upload required resume")

        # Upload cover letter (optional)
        if data.documents.has_cover_letter():
            try:
                await self._upload_document(page, "cover_letter", data.documents, fields["cover_letter"])
                filled_fields.append("cover_letter")
            except Exception as e:
                logger.warning(f"Failed to upload cover letter: {e}")

        return filled_fields

    async def _fill_quick_apply_form(self, page: Page, data: ApplicationData) -> List[str]:
        """
        Fill Indeed Quick Apply form (one-click apply with saved profile)

        Args:
            page: Playwright page object
            data: Application data

        Returns:
            List of successfully filled field names

        Raises:
            Exception: If Quick Apply not available or fails
        """
        form_config = self.form_mappings["form_types"]["indeed_quick_apply"]
        fields = form_config["fields"]

        # Click Quick Apply button
        quick_apply_selectors = fields["quick_apply_button"]["selectors"]

        for selector in quick_apply_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    await element.click()
                    logger.info(f"Clicked Quick Apply button: {selector}")
                    await asyncio.sleep(2)
                    return ["quick_apply_button"]
            except PlaywrightError:
                continue

        raise Exception("Quick Apply button not found")

    async def _fill_field(
        self, page: Page, field_name: str, value: str, field_config: Dict
    ) -> bool:
        """
        Fill a single form field with retry logic

        Args:
            page: Playwright page object
            field_name: Name of field
            value: Value to fill
            field_config: Field configuration from mappings

        Returns:
            True if successfully filled, False otherwise
        """
        selectors = field_config.get("selectors", [])
        field_type = field_config.get("type", "text")

        for selector in selectors:
            try:
                logger.debug(f"Attempting to fill {field_name} with selector: {selector}")

                element = await page.wait_for_selector(selector, timeout=5000)
                if not element:
                    continue

                # Clear existing value
                await element.click()
                await element.fill("")

                # Fill new value
                if field_type == "text_or_select":
                    # Try filling as text first, then select if that fails
                    try:
                        await element.fill(value)
                    except PlaywrightError:
                        await element.select_option(value)
                else:
                    await element.fill(value)

                logger.info(f"Successfully filled field: {field_name}")
                return True

            except PlaywrightError as e:
                logger.debug(f"Selector failed for {field_name}: {selector} - {e}")
                continue

        logger.warning(f"Could not fill field {field_name} - no selectors matched")
        return False

    async def _upload_document(
        self, page: Page, doc_type: str, documents, field_config: Dict
    ) -> bool:
        """
        Upload document (resume or cover letter)

        Args:
            page: Playwright page object
            doc_type: Document type ('resume' or 'cover_letter')
            documents: ApplicationDocuments object
            field_config: Field configuration from mappings

        Returns:
            True if successfully uploaded

        Raises:
            Exception: If upload fails
        """
        selectors = field_config.get("selectors", [])

        # Get document content
        if doc_type == "resume":
            content = documents.resume_content
        elif doc_type == "cover_letter":
            content = documents.cover_letter_content
        else:
            raise Exception(f"Unknown document type: {doc_type}")

        if not content:
            raise Exception(f"Document content not available: {doc_type}")

        # Save to temporary file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            for selector in selectors:
                try:
                    logger.debug(f"Attempting to upload {doc_type} with selector: {selector}")

                    # Check if it's a file input
                    if "input[type='file']" in selector or "type='file'" in selector:
                        file_input = await page.wait_for_selector(selector, timeout=5000)
                        if file_input:
                            await file_input.set_input_files(tmp_path)
                            logger.info(f"Successfully uploaded {doc_type}")
                            return True

                except PlaywrightError as e:
                    logger.debug(f"Upload selector failed: {selector} - {e}")
                    continue

            raise Exception(f"No file input found for {doc_type}")

        finally:
            # Cleanup temp file
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {tmp_path}: {e}")

    async def _submit_form(self, page: Page, form_type: str) -> bool:
        """
        Submit the application form

        Args:
            page: Playwright page object
            form_type: Type of form being submitted

        Returns:
            True if submission attempted

        Raises:
            Exception: If submit button not found
        """
        form_config = self.form_mappings["form_types"][form_type]
        submit_config = form_config.get("submit_button", {})
        selectors = submit_config.get("selectors", [])

        for selector in selectors:
            try:
                logger.debug(f"Looking for submit button: {selector}")

                submit_button = await page.wait_for_selector(selector, timeout=5000)
                if submit_button:
                    await submit_button.click()
                    logger.info(f"Clicked submit button: {selector}")
                    return True

            except PlaywrightError as e:
                logger.debug(f"Submit selector failed: {selector} - {e}")
                continue

        raise Exception("Submit button not found")

    async def _verify_submission(self, page: Page, form_type: str) -> Optional[str]:
        """
        Verify that application was submitted successfully

        Args:
            page: Playwright page object
            form_type: Type of form that was submitted

        Returns:
            Confirmation message if found, None otherwise
        """
        form_config = self.form_mappings["form_types"][form_type]
        confirmation_config = form_config.get("confirmation_indicators", {})

        # Check URL patterns
        url_patterns = confirmation_config.get("url_patterns", [])
        current_url = page.url
        for pattern in url_patterns:
            if pattern.replace("**", "") in current_url:
                logger.info(f"Submission confirmed via URL: {current_url}")
                return "Application submitted successfully (URL confirmation)"

        # Check for success selectors
        success_selectors = confirmation_config.get("success_selectors", [])
        for selector in success_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=10000)
                if element:
                    message = await element.inner_text()
                    logger.info(f"Submission confirmed via selector: {message}")
                    return message
            except PlaywrightError:
                continue

        # Check for success messages in page content
        success_messages = confirmation_config.get("success_messages", [])
        page_content = await page.content()
        for message in success_messages:
            if message.lower() in page_content.lower():
                logger.info(f"Submission confirmed via text: {message}")
                return message

        logger.warning("Could not verify submission confirmation")
        return None
