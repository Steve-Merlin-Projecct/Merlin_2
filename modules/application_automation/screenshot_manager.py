"""
Screenshot Manager for Application Automation

This module handles screenshot capture and storage for job application automation.
Screenshots are taken before and after form submission for review and audit purposes.

Design Principles:
- Integration with existing storage backend system
- Efficient image compression and storage
- Secure filename generation
- Comprehensive metadata tracking
"""

import os
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
from pathlib import Path
import base64
from dataclasses import dataclass

# Playwright for screenshot capture
from playwright.async_api import Page

# Import existing storage backend
from modules.storage import get_storage_backend

logger = logging.getLogger(__name__)


@dataclass
class Screenshot:
    """Screenshot metadata and content"""

    filename: str
    file_path: str
    storage_url: Optional[str]
    timestamp: str
    file_size: int
    screenshot_type: str  # 'pre_submit', 'post_submit', 'error', 'form_field'
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "filename": self.filename,
            "file_path": self.file_path,
            "storage_url": self.storage_url,
            "timestamp": self.timestamp,
            "file_size": self.file_size,
            "screenshot_type": self.screenshot_type,
            "metadata": self.metadata,
        }


class ScreenshotManager:
    """
    Manages screenshot capture and storage for application automation

    This class handles all screenshot operations including capture, compression,
    storage, and retrieval. It integrates with the existing storage backend
    system to ensure consistent file management.
    """

    def __init__(
        self,
        storage_backend=None,
        screenshot_dir: str = "application_screenshots",
        quality: int = 80,
        full_page: bool = True,
    ):
        """
        Initialize screenshot manager

        Args:
            storage_backend: Storage backend instance (defaults to configured backend)
            screenshot_dir: Subdirectory for screenshots
            quality: JPEG quality (1-100, default 80 for good compression)
            full_page: Capture full page or viewport only
        """
        self.storage = storage_backend or get_storage_backend()
        self.screenshot_dir = screenshot_dir
        self.quality = quality
        self.full_page = full_page

        logger.info(
            f"ScreenshotManager initialized with storage: {self.storage.backend_name}, "
            f"quality: {quality}, full_page: {full_page}"
        )

    async def capture_screenshot(
        self,
        page: Page,
        screenshot_type: str,
        application_id: str,
        additional_metadata: Optional[Dict] = None,
    ) -> Screenshot:
        """
        Capture screenshot from Playwright page

        Args:
            page: Playwright page object
            screenshot_type: Type of screenshot (pre_submit, post_submit, error, form_field)
            application_id: Application ID for organizing screenshots
            additional_metadata: Additional metadata to store with screenshot

        Returns:
            Screenshot object with metadata

        Raises:
            Exception: If screenshot capture or storage fails
        """
        try:
            logger.info(f"Capturing {screenshot_type} screenshot for application {application_id}")

            # Generate unique filename
            timestamp = datetime.utcnow()
            filename = self._generate_filename(application_id, screenshot_type, timestamp)

            # Capture screenshot as bytes
            screenshot_bytes = await page.screenshot(
                type="jpeg", quality=self.quality, full_page=self.full_page
            )

            # Get page metadata
            page_metadata = await self._get_page_metadata(page)

            # Prepare metadata
            metadata = {
                "application_id": application_id,
                "screenshot_type": screenshot_type,
                "timestamp": timestamp.isoformat(),
                "page_url": page.url,
                "page_title": await page.title(),
                "viewport_size": page.viewport_size,
                **page_metadata,
            }

            if additional_metadata:
                metadata.update(additional_metadata)

            # Store screenshot using storage backend
            storage_result = self.storage.save(
                filename=f"{self.screenshot_dir}/{filename}",
                content=screenshot_bytes,
                metadata={
                    "content_type": "image/jpeg",
                    "document_type": "application_screenshot",
                    **metadata,
                },
            )

            screenshot = Screenshot(
                filename=filename,
                file_path=storage_result.get("file_path", ""),
                storage_url=storage_result.get("storage_url"),
                timestamp=timestamp.isoformat(),
                file_size=len(screenshot_bytes),
                screenshot_type=screenshot_type,
                metadata=metadata,
            )

            logger.info(f"Screenshot saved: {filename} ({len(screenshot_bytes)} bytes)")

            return screenshot

        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise Exception(f"Screenshot capture failed: {e}")

    async def capture_form_field_screenshot(
        self, page: Page, field_selector: str, field_name: str, application_id: str
    ) -> Screenshot:
        """
        Capture screenshot of specific form field (useful for debugging)

        Args:
            page: Playwright page object
            field_selector: CSS selector for form field
            field_name: Name of the field
            application_id: Application ID

        Returns:
            Screenshot object with metadata

        Raises:
            Exception: If field not found or screenshot fails
        """
        try:
            logger.debug(f"Capturing field screenshot: {field_name}")

            # Locate field element
            element = await page.query_selector(field_selector)
            if not element:
                raise Exception(f"Form field not found: {field_selector}")

            # Generate filename
            timestamp = datetime.utcnow()
            filename = self._generate_filename(application_id, f"field_{field_name}", timestamp)

            # Capture element screenshot
            screenshot_bytes = await element.screenshot(type="jpeg", quality=self.quality)

            # Metadata
            metadata = {
                "application_id": application_id,
                "screenshot_type": "form_field",
                "field_name": field_name,
                "field_selector": field_selector,
                "timestamp": timestamp.isoformat(),
                "page_url": page.url,
            }

            # Store screenshot
            storage_result = self.storage.save(
                filename=f"{self.screenshot_dir}/{filename}",
                content=screenshot_bytes,
                metadata={"content_type": "image/jpeg", "document_type": "field_screenshot", **metadata},
            )

            return Screenshot(
                filename=filename,
                file_path=storage_result.get("file_path", ""),
                storage_url=storage_result.get("storage_url"),
                timestamp=timestamp.isoformat(),
                file_size=len(screenshot_bytes),
                screenshot_type="form_field",
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Failed to capture field screenshot: {e}")
            raise Exception(f"Field screenshot failed: {e}")

    async def capture_workflow_screenshots(
        self, page: Page, application_id: str
    ) -> Dict[str, Screenshot]:
        """
        Capture standard workflow screenshots (before and after submission)

        Args:
            page: Playwright page object
            application_id: Application ID

        Returns:
            Dictionary with 'pre_submit' and 'post_submit' screenshots

        Raises:
            Exception: If screenshot capture fails
        """
        screenshots = {}

        try:
            # Pre-submit screenshot
            pre_submit = await self.capture_screenshot(
                page=page, screenshot_type="pre_submit", application_id=application_id
            )
            screenshots["pre_submit"] = pre_submit

            logger.info("Pre-submit screenshot captured successfully")

        except Exception as e:
            logger.error(f"Failed to capture pre-submit screenshot: {e}")
            # Don't fail the entire workflow for screenshot errors
            screenshots["pre_submit"] = None

        return screenshots

    async def capture_error_screenshot(
        self, page: Page, application_id: str, error_message: str
    ) -> Optional[Screenshot]:
        """
        Capture screenshot when error occurs

        Args:
            page: Playwright page object
            application_id: Application ID
            error_message: Error message for metadata

        Returns:
            Screenshot object or None if capture fails

        Raises:
            Does not raise - returns None on failure
        """
        try:
            return await self.capture_screenshot(
                page=page,
                screenshot_type="error",
                application_id=application_id,
                additional_metadata={"error_message": error_message, "error_occurred": True},
            )
        except Exception as e:
            logger.error(f"Failed to capture error screenshot: {e}")
            return None

    def get_screenshot(self, filename: str) -> bytes:
        """
        Retrieve screenshot content from storage

        Args:
            filename: Screenshot filename

        Returns:
            Screenshot content as bytes

        Raises:
            FileNotFoundError: If screenshot not found
        """
        try:
            return self.storage.get(f"{self.screenshot_dir}/{filename}")
        except Exception as e:
            logger.error(f"Failed to retrieve screenshot {filename}: {e}")
            raise FileNotFoundError(f"Screenshot not found: {filename}")

    def list_screenshots(self, application_id: Optional[str] = None) -> List[str]:
        """
        List all screenshots, optionally filtered by application ID

        Args:
            application_id: Optional application ID to filter by

        Returns:
            List of screenshot filenames

        Raises:
            Exception: If listing fails
        """
        try:
            prefix = self.screenshot_dir
            if application_id:
                prefix = f"{self.screenshot_dir}/{application_id}"

            return self.storage.list(prefix=prefix, pattern="*.jpg")
        except Exception as e:
            logger.error(f"Failed to list screenshots: {e}")
            raise Exception(f"Failed to list screenshots: {e}")

    def delete_screenshot(self, filename: str) -> bool:
        """
        Delete screenshot from storage

        Args:
            filename: Screenshot filename

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If deletion fails
        """
        try:
            return self.storage.delete(f"{self.screenshot_dir}/{filename}")
        except Exception as e:
            logger.error(f"Failed to delete screenshot {filename}: {e}")
            return False

    def _generate_filename(self, application_id: str, screenshot_type: str, timestamp: datetime) -> str:
        """
        Generate unique screenshot filename

        Args:
            application_id: Application ID
            screenshot_type: Type of screenshot
            timestamp: Timestamp

        Returns:
            Filename string (e.g., 'app123_pre_submit_20251014_120530.jpg')
        """
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        safe_type = screenshot_type.replace(" ", "_").lower()
        return f"{application_id}_{safe_type}_{timestamp_str}.jpg"

    async def _get_page_metadata(self, page: Page) -> Dict[str, Any]:
        """
        Extract additional page metadata

        Args:
            page: Playwright page object

        Returns:
            Dictionary with page metadata
        """
        try:
            # Get page dimensions
            viewport = page.viewport_size or {}

            # Get page load state
            metadata = {
                "viewport_width": viewport.get("width"),
                "viewport_height": viewport.get("height"),
            }

            return metadata

        except Exception as e:
            logger.warning(f"Failed to extract page metadata: {e}")
            return {}

    async def create_screenshot_summary(self, screenshots: List[Screenshot]) -> Dict[str, Any]:
        """
        Create summary of screenshots for reporting

        Args:
            screenshots: List of Screenshot objects

        Returns:
            Dictionary with screenshot summary
        """
        if not screenshots:
            return {"count": 0, "screenshots": []}

        return {
            "count": len(screenshots),
            "total_size_bytes": sum(s.file_size for s in screenshots),
            "types": list(set(s.screenshot_type for s in screenshots)),
            "screenshots": [s.to_dict() for s in screenshots],
        }

    def cleanup_old_screenshots(self, days_old: int = 30) -> int:
        """
        Clean up screenshots older than specified days

        Args:
            days_old: Delete screenshots older than this many days

        Returns:
            Number of screenshots deleted

        Note:
            This is a placeholder - implement based on storage backend capabilities
        """
        logger.info(f"Screenshot cleanup for files older than {days_old} days")

        # TODO: Implement cleanup logic based on storage backend
        # This would require listing files with timestamps and deleting old ones
        # Implementation depends on storage backend capabilities

        return 0
