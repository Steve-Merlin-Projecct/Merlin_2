"""
Validation Error Handler for Form Automation

This module provides functionality for detecting and handling form validation errors
during automated form filling. It can detect error messages, identify which fields
failed validation, and apply format corrections for retry attempts.

Design Principles:
- Multiple detection strategies for robustness
- Field-specific format correction
- Retry limit to prevent infinite loops
- Comprehensive logging for debugging

Author: Application Automation System
Version: 1.1.0
Created: 2025-10-17
"""

import logging
import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from playwright.async_api import Page, ElementHandle, Error as PlaywrightError

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """
    Represents a form validation error

    Attributes:
        field_name: Name of the field that failed validation
        error_message: Error message from the form
        element: Playwright element handle for the error (optional)
        retry_count: Number of times this field has been retried
        correction_attempted: Whether a format correction was attempted
    """

    field_name: str
    error_message: str
    element: Optional[ElementHandle] = None
    retry_count: int = 0
    correction_attempted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "field_name": self.field_name,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "correction_attempted": self.correction_attempted,
        }


class ValidationHandler:
    """
    Handles detection and resolution of form validation errors

    This class provides methods to detect validation errors on a page,
    identify which fields failed, and apply format corrections for retry.

    Example usage:
        handler = ValidationHandler(max_retries=2)

        # Check for errors after filling form
        errors = await handler.check_for_errors(page)

        if errors:
            for error in errors:
                print(f"Field {error.field_name}: {error.error_message}")

                # Try to correct and retry
                correction = handler.suggest_correction(
                    error.field_name,
                    original_value,
                    error.error_message
                )
                if correction:
                    await handler.retry_field(page, error.field_name, correction)
    """

    def __init__(self, max_retries: int = 2):
        """
        Initialize validation handler

        Args:
            max_retries: Maximum number of retry attempts per field
        """
        self.max_retries = max_retries
        logger.info(f"ValidationHandler initialized (max_retries={max_retries})")

    async def check_for_errors(self, page: Page) -> List[ValidationError]:
        """
        Check page for validation errors

        This method looks for error messages using multiple detection strategies:
        1. Error containers with common classes/roles
        2. Field-specific error messages
        3. Form-level error summaries

        Args:
            page: Playwright page object

        Returns:
            List of ValidationError objects found on the page

        Example:
            errors = await handler.check_for_errors(page)
            if errors:
                print(f"Found {len(errors)} validation errors")
                for error in errors:
                    print(f"- {error.field_name}: {error.error_message}")
        """
        errors = []

        try:
            # Strategy 1: Look for error containers
            error_container_selectors = [
                ".error-message",
                ".field-error",
                "[role='alert']",
                ".ia-FieldError",
                ".alert-danger",
                ".form-error",
                "[class*='error' i][class*='message' i]",
            ]

            for selector in error_container_selectors:
                try:
                    error_elements = await page.query_selector_all(selector)

                    for element in error_elements:
                        # Check if element is visible
                        if not await element.is_visible():
                            continue

                        error_text = await element.inner_text()
                        error_text = error_text.strip()

                        if not error_text:
                            continue

                        # Try to find associated field name
                        field_name = await self._find_field_name_for_error(page, element)

                        error = ValidationError(
                            field_name=field_name or "unknown",
                            error_message=error_text,
                            element=element,
                        )
                        errors.append(error)

                        logger.info(
                            f"Detected validation error: field={field_name}, "
                            f"message={error_text[:50]}"
                        )

                except PlaywrightError:
                    continue

            # Strategy 2: Look for input fields with error state
            error_input_selectors = [
                "input.error",
                "input[aria-invalid='true']",
                "input[class*='error' i]",
                "select.error",
                "textarea.error",
            ]

            for selector in error_input_selectors:
                try:
                    error_inputs = await page.query_selector_all(selector)

                    for input_element in error_inputs:
                        if not await input_element.is_visible():
                            continue

                        # Get field name
                        field_name = await self._get_field_name(input_element)

                        # Look for associated error message
                        error_message = await self._find_error_message_for_field(
                            page, input_element
                        )

                        if field_name and error_message:
                            error = ValidationError(
                                field_name=field_name,
                                error_message=error_message,
                                element=input_element,
                            )
                            errors.append(error)

                            logger.info(
                                f"Detected field error: field={field_name}, "
                                f"message={error_message[:50]}"
                            )

                except PlaywrightError:
                    continue

            # Remove duplicates (same field_name)
            unique_errors = {}
            for error in errors:
                if error.field_name not in unique_errors:
                    unique_errors[error.field_name] = error

            errors = list(unique_errors.values())

            if errors:
                logger.warning(f"Found {len(errors)} validation errors on page")
            else:
                logger.debug("No validation errors detected on page")

            return errors

        except Exception as e:
            logger.error(f"Error detection failed: {e}")
            return []

    async def get_error_fields(self, page: Page) -> List[str]:
        """
        Get list of field names that have validation errors

        Args:
            page: Playwright page object

        Returns:
            List of field names with errors

        Example:
            error_fields = await handler.get_error_fields(page)
            print(f"Fields with errors: {', '.join(error_fields)}")
        """
        errors = await self.check_for_errors(page)
        return [error.field_name for error in errors if error.field_name != "unknown"]

    async def extract_error_message(self, element: ElementHandle) -> str:
        """
        Extract error message text from an element

        Args:
            element: Playwright element handle

        Returns:
            Error message text (cleaned)

        Example:
            error_element = await page.query_selector(".error-message")
            message = await handler.extract_error_message(error_element)
        """
        try:
            text = await element.inner_text()
            # Clean up message
            text = text.strip()
            text = re.sub(r"\s+", " ", text)  # Normalize whitespace
            return text
        except Exception as e:
            logger.error(f"Failed to extract error message: {e}")
            return ""

    async def retry_field(
        self,
        page: Page,
        field_name: str,
        corrected_value: str,
        field_selector: Optional[str] = None,
    ) -> bool:
        """
        Retry filling a field with corrected value

        Args:
            page: Playwright page object
            field_name: Name of field to retry
            corrected_value: Corrected value to fill
            field_selector: Optional specific selector for field

        Returns:
            True if field filled successfully, False otherwise

        Example:
            # Phone number failed validation
            corrected_phone = handler.format_phone_number("5551234567")
            success = await handler.retry_field(
                page,
                "phone",
                corrected_phone
            )
        """
        try:
            # Find field element
            if field_selector:
                selectors = [field_selector]
            else:
                # Generate common selector patterns
                selectors = [
                    f"input[name='{field_name}']",
                    f"input[id='{field_name}']",
                    f"input[name*='{field_name}' i]",
                    f"textarea[name='{field_name}']",
                    f"select[name='{field_name}']",
                ]

            field_element = None
            for selector in selectors:
                try:
                    field_element = await page.wait_for_selector(selector, timeout=3000)
                    if field_element:
                        break
                except PlaywrightError:
                    continue

            if not field_element:
                logger.error(f"Could not find field element for retry: {field_name}")
                return False

            # Clear and fill field
            await field_element.click()
            await field_element.fill("")  # Clear
            await field_element.fill(corrected_value)

            logger.info(f"Retried field: {field_name} with corrected value")

            # Give time for validation to run
            import asyncio

            await asyncio.sleep(1)

            return True

        except Exception as e:
            logger.error(f"Field retry failed: {field_name}: {e}")
            return False

    def suggest_correction(
        self, field_name: str, original_value: str, error_message: str
    ) -> Optional[str]:
        """
        Suggest a corrected value based on field name and error message

        Args:
            field_name: Name of field that failed
            original_value: Original value that failed
            error_message: Error message from form

        Returns:
            Corrected value if correction possible, None otherwise

        Example:
            corrected = handler.suggest_correction(
                "phone",
                "5551234567",
                "Invalid phone format"
            )
            # Returns: "(555) 123-4567"
        """
        field_lower = field_name.lower()

        # Phone number corrections
        if "phone" in field_lower:
            return self.format_phone_number(original_value)

        # Email corrections
        elif "email" in field_lower:
            return self.format_email(original_value)

        # URL corrections
        elif "url" in field_lower or "website" in field_lower:
            return self.format_url(original_value)

        # Date corrections
        elif "date" in field_lower:
            return self.format_date(original_value)

        logger.debug(f"No correction strategy for field: {field_name}")
        return None

    @staticmethod
    def format_phone_number(phone: str) -> str:
        """
        Format phone number to common US format: (555) 123-4567

        Args:
            phone: Raw phone number

        Returns:
            Formatted phone number

        Example:
            formatted = ValidationHandler.format_phone_number("5551234567")
            # Returns: "(555) 123-4567"
        """
        # Remove all non-digits
        digits = re.sub(r"\D", "", phone)

        # Format based on length
        if len(digits) == 10:
            return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
        elif len(digits) == 11 and digits[0] == "1":
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
        else:
            # Return as-is if we can't format
            return phone

    @staticmethod
    def format_email(email: str) -> str:
        """
        Clean up email address

        Args:
            email: Email address

        Returns:
            Cleaned email address
        """
        # Remove whitespace
        email = email.strip().lower()
        return email

    @staticmethod
    def format_url(url: str) -> str:
        """
        Ensure URL has protocol

        Args:
            url: URL string

        Returns:
            URL with protocol
        """
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        return url

    @staticmethod
    def format_date(date_str: str) -> str:
        """
        Format date to MM/DD/YYYY

        Args:
            date_str: Date string

        Returns:
            Formatted date
        """
        # This is a simple implementation - real implementation would parse various formats
        return date_str

    async def _get_field_name(self, element: ElementHandle) -> Optional[str]:
        """Get field name from input element (internal helper)"""
        try:
            # Try name attribute first
            name = await element.get_attribute("name")
            if name:
                return name

            # Try id attribute
            id_attr = await element.get_attribute("id")
            if id_attr:
                return id_attr

            # Try aria-label
            aria_label = await element.get_attribute("aria-label")
            if aria_label:
                return aria_label

            return None
        except Exception as e:
            logger.debug(f"Failed to get field name: {e}")
            return None

    async def _find_field_name_for_error(
        self, page: Page, error_element: ElementHandle
    ) -> Optional[str]:
        """Find associated field name for error message (internal helper)"""
        try:
            # Strategy 1: Check for data-field attribute
            field_attr = await error_element.get_attribute("data-field")
            if field_attr:
                return field_attr

            # Strategy 2: Look for sibling input elements
            parent = await error_element.evaluate_handle("el => el.parentElement")
            if parent:
                input_element = await parent.query_selector("input, select, textarea")
                if input_element:
                    return await self._get_field_name(input_element)

            return None
        except Exception as e:
            logger.debug(f"Failed to find field name for error: {e}")
            return None

    async def _find_error_message_for_field(
        self, page: Page, field_element: ElementHandle
    ) -> Optional[str]:
        """Find error message associated with field (internal helper)"""
        try:
            # Strategy 1: Check aria-describedby
            described_by = await field_element.get_attribute("aria-describedby")
            if described_by:
                error_element = await page.query_selector(f"#{described_by}")
                if error_element:
                    return await self.extract_error_message(error_element)

            # Strategy 2: Look for sibling error element
            parent = await field_element.evaluate_handle("el => el.parentElement")
            if parent:
                error_element = await parent.query_selector(
                    ".error-message, .field-error, [role='alert']"
                )
                if error_element and await error_element.is_visible():
                    return await self.extract_error_message(error_element)

            return None
        except Exception as e:
            logger.debug(f"Failed to find error message for field: {e}")
            return None
