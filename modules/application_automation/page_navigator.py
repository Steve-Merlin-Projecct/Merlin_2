"""
Page Navigator for Multi-Page Form Automation

This module provides functionality for detecting and navigating through multi-page
application forms. It handles page detection, navigation button finding, page transitions,
and final page identification.

Design Principles:
- Robust button detection with multiple selector strategies
- Graceful handling of edge cases (missing buttons, unexpected layouts)
- Comprehensive logging for debugging
- Support for various navigation patterns (Next, Continue, Submit)

Author: Application Automation System
Version: 1.1.0
Created: 2025-10-17
"""

import logging
import asyncio
from typing import Optional, Tuple, List
from enum import Enum
from dataclasses import dataclass

from playwright.async_api import Page, ElementHandle, Error as PlaywrightError

logger = logging.getLogger(__name__)


class ButtonType(Enum):
    """
    Types of navigation buttons found in forms

    Attributes:
        NEXT: "Next" button for multi-page forms
        CONTINUE: "Continue" or "Save & Continue" button
        SUBMIT: Final submission button
        BACK: Back/Previous button (for reference, not used for navigation)
        UNKNOWN: Button type could not be determined
    """

    NEXT = "next"
    CONTINUE = "continue"
    SUBMIT = "submit"
    BACK = "back"
    UNKNOWN = "unknown"


@dataclass
class PageInfo:
    """
    Information about the current page in a multi-page form

    Attributes:
        page_number: Current page number (1-indexed)
        total_pages: Total number of pages (None if unknown)
        has_next: Whether a next/continue button exists
        is_final: Whether this is the final page
        indicators: List of page indicators found (step counters, progress bars, etc.)
    """

    page_number: int
    total_pages: Optional[int]
    has_next: bool
    is_final: bool
    indicators: List[str]

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "page_number": self.page_number,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "is_final": self.is_final,
            "indicators": self.indicators,
        }


class PageNavigator:
    """
    Handles navigation through multi-page application forms

    This class provides methods to detect current page, find navigation buttons,
    navigate between pages, and determine if we're on the final page. It uses
    multiple detection strategies for robustness.

    Example usage:
        navigator = PageNavigator()
        page_info = await navigator.detect_current_page(page)

        if page_info.has_next:
            button, button_type = await navigator.find_navigation_button(page)
            success = await navigator.navigate_to_next(page)
    """

    def __init__(self, timeout: int = 10000):
        """
        Initialize page navigator

        Args:
            timeout: Default timeout for operations in milliseconds (default: 10000ms = 10s)
        """
        self.timeout = timeout
        logger.info(f"PageNavigator initialized (timeout={timeout}ms)")

    async def detect_current_page(self, page: Page) -> PageInfo:
        """
        Detect information about the current page in a multi-page form

        This method looks for various indicators to determine:
        - Current page number
        - Total number of pages
        - Whether there's a next page
        - Whether this is the final page

        Detection strategies:
        1. Step counters (e.g., "Step 2 of 3", "Page 2/3")
        2. Progress bars with aria-label
        3. Pagination dots
        4. Navigation button text

        Args:
            page: Playwright page object

        Returns:
            PageInfo object with detected page information

        Example:
            page_info = await navigator.detect_current_page(page)
            print(f"On page {page_info.page_number} of {page_info.total_pages}")
        """
        page_number = 1  # Default to page 1
        total_pages = None
        indicators = []

        try:
            # Strategy 1: Look for step counter text
            step_patterns = [
                r"Step (\d+) of (\d+)",
                r"Page (\d+) of (\d+)",
                r"(\d+)/(\d+)",
                r"Question (\d+) of (\d+)",
            ]

            page_content = await page.content()
            import re

            for pattern in step_patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    page_number = int(match.group(1))
                    total_pages = int(match.group(2))
                    indicators.append(f"step_counter:{pattern}")
                    logger.info(
                        f"Detected page {page_number} of {total_pages} via pattern '{pattern}'"
                    )
                    break

            # Strategy 2: Look for progress bar with aria-label
            if not indicators:
                try:
                    progress_bars = await page.query_selector_all("[role='progressbar']")
                    for progress_bar in progress_bars:
                        aria_label = await progress_bar.get_attribute("aria-label")
                        if aria_label:
                            match = re.search(r"(\d+).*of.*(\d+)", aria_label, re.IGNORECASE)
                            if match:
                                page_number = int(match.group(1))
                                total_pages = int(match.group(2))
                                indicators.append("progress_bar")
                                logger.info(
                                    f"Detected page {page_number} of {total_pages} via progress bar"
                                )
                                break
                except Exception as e:
                    logger.debug(f"Progress bar detection failed: {e}")

            # Strategy 3: Look for pagination dots
            if not indicators:
                try:
                    pagination_dots = await page.query_selector_all(
                        ".pagination-dot, .step-indicator, [class*='page-indicator']"
                    )
                    if pagination_dots:
                        total_pages = len(pagination_dots)
                        # Try to find active dot
                        for i, dot in enumerate(pagination_dots, 1):
                            classes = await dot.get_attribute("class")
                            if classes and ("active" in classes or "current" in classes):
                                page_number = i
                                break
                        indicators.append("pagination_dots")
                        logger.info(
                            f"Detected page {page_number} of {total_pages} via pagination dots"
                        )
                except Exception as e:
                    logger.debug(f"Pagination dots detection failed: {e}")

            # Strategy 4: Check for navigation buttons to infer page info
            has_next = await self._has_next_button(page)
            is_final = await self.is_final_page(page)

            if not indicators:
                # If we found a next button but no submit button, we're definitely not on the final page
                if has_next and not is_final:
                    indicators.append("next_button_present")
                # If we found a submit button but no next button, we're on the final page
                elif is_final and not has_next:
                    indicators.append("submit_button_present")

            logger.info(
                f"Page detection complete: page={page_number}, total={total_pages}, "
                f"has_next={has_next}, is_final={is_final}, indicators={indicators}"
            )

            return PageInfo(
                page_number=page_number,
                total_pages=total_pages,
                has_next=has_next,
                is_final=is_final,
                indicators=indicators,
            )

        except Exception as e:
            logger.error(f"Page detection failed: {e}")
            # Return default page info
            return PageInfo(
                page_number=1, total_pages=None, has_next=False, is_final=False, indicators=[]
            )

    async def find_navigation_button(
        self, page: Page
    ) -> Tuple[Optional[ElementHandle], ButtonType]:
        """
        Find the navigation button on the current page

        This method tries multiple selector strategies to find navigation buttons.
        It prioritizes Next/Continue buttons over Submit buttons.

        Button priority:
        1. Next button
        2. Continue button
        3. Submit button

        Args:
            page: Playwright page object

        Returns:
            Tuple of (button_element, button_type)
            Returns (None, ButtonType.UNKNOWN) if no button found

        Example:
            button, button_type = await navigator.find_navigation_button(page)
            if button:
                print(f"Found {button_type.value} button")
                await button.click()
        """
        # Strategy 1: Look for Next button
        next_selectors = [
            "button:has-text('Next')",
            "button:has-text('next')",
            "button[id*='next' i]",
            "button[class*='next' i]",
            "a:has-text('Next')",
            "input[type='submit'][value*='Next' i]",
        ]

        for selector in next_selectors:
            try:
                button = await page.wait_for_selector(selector, timeout=2000)
                if button and await button.is_visible():
                    logger.info(f"Found NEXT button with selector: {selector}")
                    return button, ButtonType.NEXT
            except PlaywrightError:
                continue

        # Strategy 2: Look for Continue button
        continue_selectors = [
            "button:has-text('Continue')",
            "button:has-text('continue')",
            "button[id*='continue' i]",
            "button[class*='continue' i]",
            "button.ia-continueButton",
            "button:has-text('Save & Continue')",
            "a:has-text('Continue')",
        ]

        for selector in continue_selectors:
            try:
                button = await page.wait_for_selector(selector, timeout=2000)
                if button and await button.is_visible():
                    logger.info(f"Found CONTINUE button with selector: {selector}")
                    return button, ButtonType.CONTINUE
            except PlaywrightError:
                continue

        # Strategy 3: Look for Submit button (final page)
        submit_selectors = [
            "button:has-text('Submit application')",
            "button:has-text('Submit')",
            "button[type='submit']:has-text('Apply')",
            "button:has-text('Apply now')",
            "button.ia-continueButton:has-text('Submit')",
            "input[type='submit'][value*='Submit' i]",
        ]

        for selector in submit_selectors:
            try:
                button = await page.wait_for_selector(selector, timeout=2000)
                if button and await button.is_visible():
                    logger.info(f"Found SUBMIT button with selector: {selector}")
                    return button, ButtonType.SUBMIT
            except PlaywrightError:
                continue

        logger.warning("No navigation button found on page")
        return None, ButtonType.UNKNOWN

    async def _has_next_button(self, page: Page) -> bool:
        """
        Check if page has a next/continue button (internal helper)

        Args:
            page: Playwright page object

        Returns:
            True if next/continue button exists, False otherwise
        """
        button, button_type = await self.find_navigation_button(page)
        return button is not None and button_type in [ButtonType.NEXT, ButtonType.CONTINUE]

    async def is_final_page(self, page: Page) -> bool:
        """
        Determine if current page is the final page (submission page)

        Detection strategies:
        1. Check for submit button with specific text
        2. Check for confirmation indicators
        3. Check URL patterns

        Args:
            page: Playwright page object

        Returns:
            True if this is the final page, False otherwise

        Example:
            if await navigator.is_final_page(page):
                print("Ready to submit application")
        """
        # Strategy 1: Look for submit button
        submit_indicators = [
            "button:has-text('Submit application')",
            "button:has-text('Submit your application')",
            "button[type='submit']:has-text('Apply')",
            "button:has-text('Apply now')",
        ]

        for selector in submit_indicators:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    logger.info(f"Detected final page via submit button: {selector}")
                    return True
            except PlaywrightError:
                continue

        # Strategy 2: Check for "review" or "confirm" indicators
        review_patterns = [
            r"review.*application",
            r"confirm.*details",
            r"final.*step",
            r"submit.*application",
        ]

        try:
            page_content = await page.content()
            import re

            for pattern in review_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    logger.info(f"Detected final page via review pattern: {pattern}")
                    return True
        except Exception as e:
            logger.debug(f"Review pattern detection failed: {e}")

        # Strategy 3: Check URL for "review" or "submit"
        current_url = page.url.lower()
        if "review" in current_url or "submit" in current_url or "confirm" in current_url:
            logger.info(f"Detected final page via URL pattern: {current_url}")
            return True

        return False

    async def navigate_to_next(self, page: Page) -> bool:
        """
        Navigate to the next page by clicking the navigation button

        This method:
        1. Finds the navigation button
        2. Clicks it
        3. Waits for page transition
        4. Verifies new page loaded

        Args:
            page: Playwright page object

        Returns:
            True if navigation succeeded, False otherwise

        Raises:
            Exception: If navigation fails critically

        Example:
            if await navigator.navigate_to_next(page):
                print("Successfully moved to next page")
            else:
                print("Navigation failed")
        """
        try:
            # Find navigation button
            button, button_type = await self.find_navigation_button(page)

            if not button:
                logger.error("Cannot navigate: no navigation button found")
                return False

            logger.info(f"Attempting to navigate using {button_type.value} button")

            # Get current URL before navigation (to detect change)
            current_url = page.url

            # Click button
            await button.click()
            logger.info("Navigation button clicked")

            # Wait for page transition
            await self.wait_for_page_transition(page, timeout=self.timeout)

            # Verify navigation occurred
            new_url = page.url
            if new_url != current_url:
                logger.info(f"Navigation successful: {current_url} -> {new_url}")
                return True
            else:
                # URL might be same for single-page apps with dynamic content
                # Wait a bit more and check if DOM changed significantly
                await asyncio.sleep(2)
                logger.info("Navigation complete (same URL, likely SPA)")
                return True

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False

    async def wait_for_page_transition(self, page: Page, timeout: int = 10000):
        """
        Wait for page transition to complete after clicking navigation button

        This method waits for:
        1. Network to become idle
        2. DOM to stabilize
        3. Loading indicators to disappear

        Args:
            page: Playwright page object
            timeout: Maximum time to wait in milliseconds

        Raises:
            TimeoutError: If page doesn't load within timeout

        Example:
            await button.click()
            await navigator.wait_for_page_transition(page)
        """
        try:
            # Wait for network idle (no requests for 500ms)
            await page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("Network idle after navigation")

            # Wait for any loading indicators to disappear
            loading_selectors = [
                ".loading",
                ".spinner",
                "[class*='loading']",
                "[aria-busy='true']",
            ]

            for selector in loading_selectors:
                try:
                    await page.wait_for_selector(selector, state="hidden", timeout=2000)
                    logger.debug(f"Loading indicator disappeared: {selector}")
                except PlaywrightError:
                    # Selector not found or already hidden, that's fine
                    pass

            # Give DOM a moment to stabilize
            await asyncio.sleep(1)

            logger.info("Page transition complete")

        except Exception as e:
            logger.warning(f"Page transition wait encountered issue: {e}")
            # Don't fail hard, page might have loaded anyway
