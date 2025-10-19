"""
Custom Document Handler for Application Automation

This module handles the upload of custom resumes and cover letters for each job application.
It enforces a "custom-first" policy where personalized documents are always preferred,
falling back to default documents only after multiple failures.

Business Rule: ALWAYS use custom resume and cover letter for each application.
Fallback: Use default resume/cover letter only after multiple upload failures.

Author: Application Automation System
Version: 1.1.0
Created: 2025-10-18
"""

import os
import logging
import tempfile
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import Page, ElementHandle, Error as PlaywrightError

logger = logging.getLogger(__name__)


@dataclass
class DocumentUploadResult:
    """
    Result of document upload attempt

    Attributes:
        success: Whether upload succeeded
        document_type: Type of document (resume/cover_letter)
        document_used: Path or identifier of document used
        is_custom: Whether custom document was used
        error_message: Error message if failed
        retry_count: Number of attempts made
    """
    success: bool
    document_type: str
    document_used: str
    is_custom: bool
    error_message: Optional[str] = None
    retry_count: int = 0


class CustomDocumentHandler:
    """
    Handles upload of custom resumes and cover letters with fallback logic

    This class enforces the business rule that custom documents should always
    be used first, with fallback to default documents only after multiple failures.

    Example usage:
        handler = CustomDocumentHandler(max_retries=3)

        # Upload custom resume
        result = await handler.upload_custom_resume(
            page=page,
            custom_resume_path="/tmp/custom_resume_job123.pdf",
            default_resume_path="/templates/default_resume.pdf"
        )

        if result.success:
            print(f"Uploaded {'custom' if result.is_custom else 'default'} resume")
    """

    def __init__(self, max_retries: int = 3, fallback_after_failures: int = 2):
        """
        Initialize custom document handler

        Args:
            max_retries: Maximum upload attempts per document
            fallback_after_failures: Number of custom upload failures before fallback to default
        """
        self.max_retries = max_retries
        self.fallback_after_failures = fallback_after_failures
        logger.info(
            f"CustomDocumentHandler initialized (max_retries={max_retries}, "
            f"fallback_after={fallback_after_failures})"
        )

    async def upload_custom_resume(
        self,
        page: Page,
        custom_resume_path: Optional[str] = None,
        custom_resume_content: Optional[bytes] = None,
        default_resume_path: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> DocumentUploadResult:
        """
        Upload custom resume with fallback to default after failures

        Priority:
        1. Always try custom resume first (from path or content)
        2. If custom fails multiple times, fall back to default
        3. Log all attempts for debugging

        Args:
            page: Playwright page object
            custom_resume_path: Path to custom resume file
            custom_resume_content: Custom resume as bytes (if not saved to disk)
            default_resume_path: Path to default resume (fallback)
            job_id: Job ID for logging

        Returns:
            DocumentUploadResult with upload status
        """
        logger.info(f"Starting custom resume upload for job {job_id}")

        # Prepare custom resume
        temp_file_created = False
        if custom_resume_content and not custom_resume_path:
            # Save content to temporary file
            custom_resume_path = await self._save_to_temp_file(
                content=custom_resume_content,
                suffix=".pdf",
                prefix=f"resume_{job_id}_"
            )
            temp_file_created = True
            logger.debug(f"Created temp file for custom resume: {custom_resume_path}")

        # Try custom resume first (always)
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Attempting custom resume upload (attempt {attempt}/{self.max_retries})")

            try:
                success = await self._upload_file(page, custom_resume_path)

                if success:
                    logger.info(f"Successfully uploaded custom resume on attempt {attempt}")

                    # Clean up temp file
                    if temp_file_created:
                        self._cleanup_temp_file(custom_resume_path)

                    return DocumentUploadResult(
                        success=True,
                        document_type="resume",
                        document_used=custom_resume_path,
                        is_custom=True,
                        retry_count=attempt
                    )

            except Exception as e:
                logger.warning(f"Custom resume upload attempt {attempt} failed: {e}")

                # If we've failed enough times, try fallback
                if attempt >= self.fallback_after_failures and default_resume_path:
                    logger.warning(
                        f"Custom resume failed {attempt} times, falling back to default"
                    )

                    # Clean up temp file before fallback
                    if temp_file_created:
                        self._cleanup_temp_file(custom_resume_path)

                    return await self._fallback_to_default_resume(
                        page=page,
                        default_resume_path=default_resume_path,
                        custom_failures=attempt
                    )

        # All attempts failed
        error_msg = f"Failed to upload custom resume after {self.max_retries} attempts"
        logger.error(error_msg)

        # Clean up temp file
        if temp_file_created:
            self._cleanup_temp_file(custom_resume_path)

        return DocumentUploadResult(
            success=False,
            document_type="resume",
            document_used=custom_resume_path or "custom_content",
            is_custom=True,
            error_message=error_msg,
            retry_count=self.max_retries
        )

    async def upload_custom_cover_letter(
        self,
        page: Page,
        custom_cover_letter_path: Optional[str] = None,
        custom_cover_letter_content: Optional[bytes] = None,
        default_cover_letter_path: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> DocumentUploadResult:
        """
        Upload custom cover letter with fallback to default after failures

        Same logic as resume upload but for cover letters.

        Args:
            page: Playwright page object
            custom_cover_letter_path: Path to custom cover letter
            custom_cover_letter_content: Custom cover letter as bytes
            default_cover_letter_path: Path to default cover letter (fallback)
            job_id: Job ID for logging

        Returns:
            DocumentUploadResult with upload status
        """
        logger.info(f"Starting custom cover letter upload for job {job_id}")

        # Similar implementation to upload_custom_resume
        # (Code follows same pattern)

        temp_file_created = False
        if custom_cover_letter_content and not custom_cover_letter_path:
            custom_cover_letter_path = await self._save_to_temp_file(
                content=custom_cover_letter_content,
                suffix=".pdf",
                prefix=f"cover_letter_{job_id}_"
            )
            temp_file_created = True

        # Try custom cover letter first
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Attempting custom cover letter upload (attempt {attempt}/{self.max_retries})")

            try:
                success = await self._upload_file(page, custom_cover_letter_path)

                if success:
                    logger.info(f"Successfully uploaded custom cover letter on attempt {attempt}")

                    if temp_file_created:
                        self._cleanup_temp_file(custom_cover_letter_path)

                    return DocumentUploadResult(
                        success=True,
                        document_type="cover_letter",
                        document_used=custom_cover_letter_path,
                        is_custom=True,
                        retry_count=attempt
                    )

            except Exception as e:
                logger.warning(f"Custom cover letter upload attempt {attempt} failed: {e}")

                if attempt >= self.fallback_after_failures and default_cover_letter_path:
                    logger.warning(
                        f"Custom cover letter failed {attempt} times, falling back to default"
                    )

                    if temp_file_created:
                        self._cleanup_temp_file(custom_cover_letter_path)

                    return await self._fallback_to_default_cover_letter(
                        page=page,
                        default_cover_letter_path=default_cover_letter_path,
                        custom_failures=attempt
                    )

        # All attempts failed
        error_msg = f"Failed to upload custom cover letter after {self.max_retries} attempts"
        logger.error(error_msg)

        if temp_file_created:
            self._cleanup_temp_file(custom_cover_letter_path)

        return DocumentUploadResult(
            success=False,
            document_type="cover_letter",
            document_used=custom_cover_letter_path or "custom_content",
            is_custom=True,
            error_message=error_msg,
            retry_count=self.max_retries
        )

    async def _upload_file(self, page: Page, file_path: str) -> bool:
        """
        Core file upload logic using Playwright

        CRITICAL: This method avoids bot detection by:
        1. NOT making hidden inputs visible (abnormal behavior)
        2. Using Playwright's file chooser API instead
        3. Clicking the site's styled upload buttons

        Args:
            page: Playwright page object
            file_path: Path to file to upload

        Returns:
            True if upload successful, False otherwise
        """
        try:
            # CRITICAL: DO NOT make hidden inputs visible - triggers bot detection!
            # Instead, use Playwright's expect_file_chooser API

            # Strategy 1: Click the upload button and handle file chooser
            upload_button_selectors = [
                "button[data-testid='ResumeOptionsMenu-upload']",  # Indeed specific
                "button[data-testid*='upload-button']",  # Generic upload buttons
                "button:has-text('Upload a file')",
                "button:has-text('Upload')",
                "button:has-text('Choose file')",
                "button:has-text('Select file')",
                "button:has-text('Upload a different file')"
            ]

            upload_button = None
            for selector in upload_button_selectors:
                try:
                    button = await page.query_selector(selector)
                    if button and await button.is_visible():
                        upload_button = button
                        logger.debug(f"Found upload button with selector: {selector}")
                        break
                except:
                    continue

            if upload_button:
                # Use expect_file_chooser to handle the file dialog
                async with page.expect_file_chooser() as fc_info:
                    await upload_button.click()
                    logger.debug("Clicked upload button, waiting for file chooser")

                file_chooser = await fc_info.value
                await file_chooser.set_files(file_path)
                logger.debug(f"Set file via file chooser: {file_path}")

            else:
                # Strategy 2: Direct file input (only if already visible)
                file_input = await page.query_selector("input[type='file']:visible")

                if not file_input:
                    # Try specific Indeed selector (but don't make it visible!)
                    file_input = await page.query_selector(
                        "input[data-testid='resume-selection-file-resume-upload-button-file-input']"
                    )

                if not file_input:
                    raise Exception("Could not find upload button or visible file input")

                # Only use set_input_files if the input is already accessible
                # This is safer than making hidden inputs visible
                await file_input.set_input_files(file_path)
                logger.debug(f"Set file directly on input: {file_path}")

            # Wait for upload to process
            await page.wait_for_timeout(1000)

            # Verify upload (check for filename display, success message, etc.)
            upload_indicators = [
                f"text={Path(file_path).name}",
                "text=/uploaded successfully/i",
                "text=/file selected/i",
                f"[title*='{Path(file_path).name}']"
            ]

            for indicator in upload_indicators:
                try:
                    element = await page.wait_for_selector(indicator, timeout=2000)
                    if element:
                        logger.debug(f"Upload verified via indicator: {indicator}")
                        return True
                except:
                    continue

            # If no explicit confirmation, assume success if no error
            return True

        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return False

    async def _fallback_to_default_resume(
        self,
        page: Page,
        default_resume_path: str,
        custom_failures: int
    ) -> DocumentUploadResult:
        """
        Fallback to default resume after custom resume failures

        Args:
            page: Playwright page object
            default_resume_path: Path to default resume
            custom_failures: Number of custom upload attempts that failed

        Returns:
            DocumentUploadResult with fallback status
        """
        logger.warning(f"FALLBACK: Using default resume after {custom_failures} custom failures")

        try:
            success = await self._upload_file(page, default_resume_path)

            if success:
                logger.info("Successfully uploaded DEFAULT resume as fallback")
                return DocumentUploadResult(
                    success=True,
                    document_type="resume",
                    document_used=default_resume_path,
                    is_custom=False,  # Important: This is NOT custom
                    retry_count=custom_failures + 1
                )
            else:
                error_msg = "Failed to upload even default resume"
                logger.error(error_msg)
                return DocumentUploadResult(
                    success=False,
                    document_type="resume",
                    document_used=default_resume_path,
                    is_custom=False,
                    error_message=error_msg,
                    retry_count=custom_failures + 1
                )

        except Exception as e:
            error_msg = f"Default resume upload failed: {e}"
            logger.error(error_msg)
            return DocumentUploadResult(
                success=False,
                document_type="resume",
                document_used=default_resume_path,
                is_custom=False,
                error_message=error_msg,
                retry_count=custom_failures + 1
            )

    async def _fallback_to_default_cover_letter(
        self,
        page: Page,
        default_cover_letter_path: str,
        custom_failures: int
    ) -> DocumentUploadResult:
        """
        Fallback to default cover letter after custom failures

        Similar to _fallback_to_default_resume but for cover letters.
        """
        logger.warning(f"FALLBACK: Using default cover letter after {custom_failures} custom failures")

        try:
            success = await self._upload_file(page, default_cover_letter_path)

            if success:
                logger.info("Successfully uploaded DEFAULT cover letter as fallback")
                return DocumentUploadResult(
                    success=True,
                    document_type="cover_letter",
                    document_used=default_cover_letter_path,
                    is_custom=False,
                    retry_count=custom_failures + 1
                )
            else:
                error_msg = "Failed to upload even default cover letter"
                logger.error(error_msg)
                return DocumentUploadResult(
                    success=False,
                    document_type="cover_letter",
                    document_used=default_cover_letter_path,
                    is_custom=False,
                    error_message=error_msg,
                    retry_count=custom_failures + 1
                )

        except Exception as e:
            error_msg = f"Default cover letter upload failed: {e}"
            logger.error(error_msg)
            return DocumentUploadResult(
                success=False,
                document_type="cover_letter",
                document_used=default_cover_letter_path,
                is_custom=False,
                error_message=error_msg,
                retry_count=custom_failures + 1
            )

    async def _save_to_temp_file(
        self,
        content: bytes,
        suffix: str = ".pdf",
        prefix: str = "document_"
    ) -> str:
        """
        Save document content to temporary file

        Args:
            content: Document content as bytes
            suffix: File extension
            prefix: File prefix

        Returns:
            Path to temporary file
        """
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix=suffix,
            prefix=prefix,
            delete=False
        ) as tmp_file:
            tmp_file.write(content)
            return tmp_file.name

    def _cleanup_temp_file(self, file_path: str):
        """
        Clean up temporary file

        Args:
            file_path: Path to temporary file
        """
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")

    async def handle_indeed_resume_selection(
        self,
        page: Page,
        custom_resume_path: str,
        default_resume_path: str,
        job_id: str
    ) -> DocumentUploadResult:
        """
        Handle Indeed's specific resume selection page

        Based on real selectors from user's data:
        1. Check if we're on resume selection page
        2. Click "Resume options" button if needed
        3. Click "Upload a different file"
        4. Upload custom resume

        Args:
            page: Playwright page object
            custom_resume_path: Path to custom resume
            default_resume_path: Path to default resume
            job_id: Job ID for logging

        Returns:
            DocumentUploadResult with upload status
        """
        try:
            # Check if we're on the resume selection page
            if "resume-selection" in page.url:
                logger.info("Detected Indeed resume selection page")

                # Look for "Resume options" button
                resume_options_button = await page.query_selector(
                    "button[data-testid='ResumeOptionsMenu']"
                )

                if resume_options_button:
                    logger.info("Clicking Resume options button")
                    await resume_options_button.click()
                    await page.wait_for_timeout(500)

                    # Click "Upload a different file" option
                    upload_option = await page.query_selector(
                        "button[data-testid='ResumeOptionsMenu-upload']"
                    )

                    if upload_option:
                        logger.info("Clicking 'Upload a different file' option")
                        await upload_option.click()
                        await page.wait_for_timeout(1000)

                # Now upload the custom resume
                return await self.upload_custom_resume(
                    page=page,
                    custom_resume_path=custom_resume_path,
                    default_resume_path=default_resume_path,
                    job_id=job_id
                )

        except Exception as e:
            logger.error(f"Indeed resume selection handling failed: {e}")
            return DocumentUploadResult(
                success=False,
                document_type="resume",
                document_used=custom_resume_path,
                is_custom=True,
                error_message=str(e),
                retry_count=1
            )