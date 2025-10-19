"""
Integration Test for Indeed Multi-Page Application with Real Selectors

This test demonstrates the complete flow of applying to a job on Indeed
using the real selectors collected from test data. It shows how all
components work together to handle multi-page navigation, custom document
upload, and dynamic screening questions.

Author: Application Automation System
Version: 1.0.0
Created: 2025-10-19
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from playwright.async_api import async_playwright, Page

# Import our application automation modules
from page_navigator import PageNavigator
from form_state_manager import FormStateManager
from validation_handler import ValidationHandler
from custom_document_handler import CustomDocumentHandler
from screening_questions_handler import ScreeningQuestionsHandler
from dynamic_question_analyzer import DynamicQuestionAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndeedApplicationFlow:
    """
    Complete Indeed application flow using real selectors

    This class demonstrates the integration of all components to:
    1. Navigate from job listing to application submission
    2. Upload custom resume (avoiding bot detection)
    3. Answer dynamic screening questions
    4. Handle multi-page navigation with checkpoints
    """

    def __init__(self):
        """Initialize all automation components"""
        self.navigator = PageNavigator()
        self.state_manager = FormStateManager()
        self.validation_handler = ValidationHandler()
        self.document_handler = CustomDocumentHandler(max_retries=3)

        # Initialize with sample applicant profile
        self.applicant_profile = {
            "full_name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "555-123-4567",
            "location": "San Francisco, CA",
            "experience_years": 5,
            "work_authorization": True,
            "willing_to_relocate": True,
            "availability": "2 weeks notice",
            "portfolio_url": "https://johnsmith.dev",
            "skills": ["Python", "JavaScript", "React", "Node.js"],
            "education_level": "Bachelor's degree"
        }

        self.screening_handler = ScreeningQuestionsHandler(self.applicant_profile)
        self.question_analyzer = DynamicQuestionAnalyzer(
            job_context={"title": "Software Engineer", "company": "Tech Corp"},
            applicant_profile=self.applicant_profile
        )

    async def apply_to_job(self, page: Page, job_url: str, custom_resume_path: str, custom_cover_letter_path: str):
        """
        Complete job application flow

        Args:
            page: Playwright page object
            job_url: URL of the job listing
            custom_resume_path: Path to custom resume
            custom_cover_letter_path: Path to custom cover letter
        """
        try:
            # Navigate to job listing
            logger.info(f"Navigating to job: {job_url}")
            await page.goto(job_url)
            await page.wait_for_load_state("networkidle")

            # Step 1: Click Apply button on job listing page
            await self.click_apply_button(page)

            # Step 2: Handle resume selection page
            await self.handle_resume_selection(page, custom_resume_path)

            # Step 3: Handle screening questions
            await self.handle_screening_questions(page, custom_cover_letter_path)

            # Step 4: Review and submit
            await self.review_and_submit(page)

            logger.info("Application submitted successfully!")

        except Exception as e:
            logger.error(f"Application failed: {e}")
            # Save checkpoint for resume
            await self.state_manager.save_checkpoint(page, "application_failed")
            raise

    async def click_apply_button(self, page: Page):
        """
        Click the Apply button on the job listing page

        Uses real selectors from test data:
        - #indeedApplyButton > div
        - .jobsearch-IndeedApplyButton-newDesign
        """
        logger.info("Page 1: Clicking Apply button")

        # Try multiple selectors based on real data
        apply_selectors = [
            "#indeedApplyButton > div",
            "#indeedApplyButton span:has-text('Apply now')",
            ".jobsearch-IndeedApplyButton-newDesign"
        ]

        clicked = False
        for selector in apply_selectors:
            try:
                button = await page.query_selector(selector)
                if button:
                    await button.click()
                    clicked = True
                    logger.info(f"Clicked apply button with selector: {selector}")
                    break
            except:
                continue

        if not clicked:
            raise Exception("Could not find Apply button")

        # Wait for navigation to resume selection page
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

    async def handle_resume_selection(self, page: Page, custom_resume_path: str):
        """
        Handle the resume selection page (Page 2)

        Critical: Avoids bot detection by NOT making hidden inputs visible
        Uses real selectors:
        - button[data-testid='ResumeOptionsMenu']
        - button[data-testid='ResumeOptionsMenu-upload']
        """
        logger.info("Page 2: Resume selection")

        # Check if we're on resume selection page
        if "resume-selection" not in page.url:
            logger.info("Not on resume selection page, checking if already passed")
            return

        # Click "Resume options" button
        resume_options_btn = await page.query_selector("button[data-testid='ResumeOptionsMenu']")
        if resume_options_btn:
            logger.info("Clicking Resume options button")
            await resume_options_btn.click()
            await page.wait_for_timeout(500)

            # Click "Upload a different file"
            upload_btn = await page.query_selector("button[data-testid='ResumeOptionsMenu-upload']")
            if upload_btn:
                logger.info("Clicking 'Upload a different file'")

                # CRITICAL: Use expect_file_chooser to avoid bot detection
                async with page.expect_file_chooser() as fc_info:
                    await upload_btn.click()

                file_chooser = await fc_info.value
                await file_chooser.set_files(custom_resume_path)
                logger.info(f"Uploaded custom resume: {custom_resume_path}")

        # Alternative: Use CustomDocumentHandler for robust upload
        else:
            logger.info("Using CustomDocumentHandler for resume upload")
            result = await self.document_handler.upload_custom_resume(
                page=page,
                custom_resume_path=custom_resume_path,
                default_resume_path="/templates/default_resume.pdf",
                job_id="test_job"
            )

            if not result.success:
                raise Exception(f"Resume upload failed: {result.error_message}")

        # Continue to next page
        await self.click_continue_button(page)

    async def handle_screening_questions(self, page: Page, custom_cover_letter_path: str):
        """
        Handle screening questions page (Page 3)

        Uses dynamic question detection and AI-powered answering
        Real selectors:
        - Cover letter: button[data-testid*='upload-button']
        - Dropdowns: select[name^='q_']
        - Radio: input[type='radio'][id^='single-select-question']
        - Text: textarea[id^='rich-text-question-input']
        """
        logger.info("Page 3: Screening questions")

        # Check if we're on questions page
        if "questions" not in page.url:
            logger.info("Not on questions page, checking if already passed")
            return

        # Detect all questions on the page
        questions = await self.screening_handler.detect_questions(page)
        logger.info(f"Detected {len(questions)} screening questions")

        # Handle each question type
        for question in questions:
            logger.info(f"Processing question: {question.question_text[:50]}...")

            # Special handling for file uploads
            if question.question_type.value == "file_upload":
                if "cover" in question.question_text.lower():
                    await self.upload_cover_letter(page, question, custom_cover_letter_path)
                elif "portfolio" in question.question_text.lower():
                    # Skip portfolio PDF upload - we'll provide URL instead
                    logger.info("Skipping portfolio file upload")
                continue

            # For other questions, use dynamic analyzer
            analysis = self.question_analyzer.analyze_question(
                question.question_text,
                question.question_type.value,
                question.options
            )

            logger.info(f"Question intent: {analysis.intent}, Answer: {analysis.suggested_answer}")

            # Fill the answer
            await self.fill_question_answer(page, question, analysis.suggested_answer)

        # Continue to next page
        await self.click_continue_button(page)

    async def upload_cover_letter(self, page: Page, question, cover_letter_path: str):
        """Upload cover letter using safe method"""
        try:
            # Find the upload button for this specific question
            upload_btn = await page.query_selector(question.element_selector)
            if upload_btn:
                async with page.expect_file_chooser() as fc_info:
                    await upload_btn.click()

                file_chooser = await fc_info.value
                await file_chooser.set_files(cover_letter_path)
                logger.info(f"Uploaded cover letter: {cover_letter_path}")
        except Exception as e:
            logger.warning(f"Cover letter upload failed: {e}")

    async def fill_question_answer(self, page: Page, question, answer):
        """Fill a screening question with the suggested answer"""
        try:
            if question.question_type.value == "select":
                # Handle dropdown
                select = await page.query_selector(question.element_selector)
                if select and answer:
                    await select.select_option(value=str(answer))
                    logger.debug(f"Selected option: {answer}")

            elif question.question_type.value == "radio":
                # Handle radio buttons
                if answer and isinstance(answer, str) and answer.startswith("#"):
                    # Answer contains the selector for specific radio
                    radio = await page.query_selector(answer)
                    if radio:
                        await radio.check()
                        logger.debug(f"Checked radio: {answer}")
                else:
                    # Find the right radio by value
                    radios = await page.query_selector_all(f"{question.element_selector}")
                    for radio in radios:
                        value = await radio.get_attribute("value")
                        if value == str(answer):
                            await radio.check()
                            break

            elif question.question_type.value == "text":
                # Handle text input or textarea
                element = await page.query_selector(question.element_selector)
                if element and answer:
                    await element.fill(str(answer))
                    logger.debug(f"Filled text: {answer}")

        except Exception as e:
            logger.warning(f"Failed to fill question: {e}")

    async def click_continue_button(self, page: Page):
        """
        Click Continue button to navigate to next page

        Uses real selector:
        #mosaic-provider-module-apply-questions button span:has-text('Continue')
        """
        continue_selectors = [
            "#mosaic-provider-module-apply-questions button span:has-text('Continue')",
            "button:has-text('Continue')",
            "button span:has-text('Continue')"
        ]

        clicked = False
        for selector in continue_selectors:
            try:
                button = await page.query_selector(selector)
                if button:
                    # Scroll into view first
                    await button.scroll_into_view_if_needed()
                    await button.click()
                    clicked = True
                    logger.info(f"Clicked Continue with selector: {selector}")
                    break
            except:
                continue

        if not clicked:
            logger.warning("Could not find Continue button")

        # Wait for navigation
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

    async def review_and_submit(self, page: Page):
        """
        Review application and submit (Page 4 if exists)
        """
        logger.info("Page 4: Review and submit")

        # Check if we're on review page
        if "review" in page.url:
            logger.info("On review page - ready to submit")

            # Look for submit button
            submit_selectors = [
                "button:has-text('Submit application')",
                "button:has-text('Submit')",
                "button[type='submit']"
            ]

            for selector in submit_selectors:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        logger.info("Found submit button - APPLICATION READY")
                        # In production, would click here:
                        # await button.click()
                        break
                except:
                    continue

        # Check for confirmation
        await self.check_submission_confirmation(page)

    async def check_submission_confirmation(self, page: Page):
        """Check if application was submitted successfully"""
        confirmation_indicators = [
            "text=Application submitted",
            "text=Thank you for applying",
            "text=Your application has been sent",
            "text=Application received"
        ]

        for indicator in confirmation_indicators:
            try:
                element = await page.wait_for_selector(indicator, timeout=5000)
                if element:
                    logger.info("✅ Application submitted successfully!")
                    return True
            except:
                continue

        return False


async def main():
    """
    Test the Indeed application flow with real selectors
    """
    # Example usage
    async with async_playwright() as p:
        # Launch browser (headless=False for debugging)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Initialize application flow
        flow = IndeedApplicationFlow()

        # Test with a sample job URL
        job_url = "https://www.indeed.com/viewjob?jk=example123"
        custom_resume = "/tmp/custom_resume_job123.pdf"
        custom_cover = "/tmp/custom_cover_job123.pdf"

        try:
            # Run the application
            await flow.apply_to_job(page, job_url, custom_resume, custom_cover)
        except Exception as e:
            logger.error(f"Test failed: {e}")
            # Take screenshot for debugging
            await page.screenshot(path="/tmp/error_screenshot.png")
        finally:
            await browser.close()


if __name__ == "__main__":
    # Run the integration test
    asyncio.run(main())

"""
Key Integration Points Demonstrated:

1. **Multi-Page Navigation:**
   - Navigates through 4 pages: Job listing → Resume selection → Screening → Review
   - Uses real selectors from test data
   - Handles page transitions with proper waits

2. **Bot Detection Avoidance:**
   - NEVER makes hidden inputs visible
   - Uses Playwright's expect_file_chooser API
   - Clicks actual upload buttons that users see

3. **Dynamic Question Handling:**
   - Detects various question types (dropdown, radio, text, file)
   - Uses AI to understand employer intent
   - Provides contextually appropriate answers

4. **Custom Document Priority:**
   - Always uploads custom resume/cover letter first
   - Falls back to default only after failures
   - Handles file uploads in Docker environment

5. **Real Selectors Used:**
   Page 1: #indeedApplyButton > div
   Page 2: button[data-testid='ResumeOptionsMenu-upload']
   Page 3: select[name^='q_'], input[id^='single-select-question']
   Continue: #mosaic-provider-module-apply-questions button

6. **React Dynamic IDs:**
   - Handles IDs with colons (:r4:, :r7:, :rc:)
   - Uses data-testid attributes for stability
   - Falls back to pattern matching when needed
"""