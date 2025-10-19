"""
Screening Questions Handler for Application Automation

This module handles various types of screening questions commonly found in job applications.
It supports multiple question types (text, select, radio, checkbox, file upload) and
uses intelligent matching to handle dynamic question IDs.

Business Rule: Answer screening questions accurately based on applicant profile data.
Fallback: Use conservative/safe answers when specific data is unavailable.

Author: Application Automation System
Version: 1.0.0
Created: 2025-10-19
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from playwright.async_api import Page, ElementHandle

logger = logging.getLogger(__name__)


class QuestionType(Enum):
    """
    Types of screening questions encountered in applications

    Each type requires different interaction methods:
    - TEXT: Simple text input or textarea
    - SELECT: Dropdown selection
    - RADIO: Single choice from multiple options
    - CHECKBOX: Multiple choice selection
    - FILE_UPLOAD: Document upload
    - RANGE: Slider or number range input
    """
    TEXT = "text"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    FILE_UPLOAD = "file_upload"
    RANGE = "range"


@dataclass
class ScreeningQuestion:
    """
    Represents a screening question found on the page

    Attributes:
        question_text: The actual question being asked
        question_type: Type of input required
        element_selector: CSS/XPath selector to find the element
        required: Whether the question is mandatory
        options: Available choices for select/radio/checkbox
        current_value: Currently selected/entered value
        field_name: HTML name attribute (often hashed)
        data_testid: React test ID for reliable selection
    """
    question_text: str
    question_type: QuestionType
    element_selector: str
    required: bool = False
    options: List[Dict[str, str]] = None
    current_value: Optional[str] = None
    field_name: Optional[str] = None
    data_testid: Optional[str] = None


class ScreeningQuestionsHandler:
    """
    Handles detection and answering of screening questions

    This class intelligently detects question types, maps them to applicant data,
    and fills them appropriately. It handles Indeed's dynamic React IDs and
    provides fallback strategies for unknown questions.

    Example usage:
        handler = ScreeningQuestionsHandler(applicant_profile)
        questions = await handler.detect_questions(page)
        answers = handler.prepare_answers(questions)
        await handler.fill_questions(page, answers)
    """

    # Common question patterns and their preferred answers
    QUESTION_PATTERNS = {
        r"years?.+experience": "experience_years",
        r"work.+in-person|on-site|office": "work_location_preference",
        r"authorized.+work": "work_authorization",
        r"require.+sponsor": "sponsorship_needed",
        r"salary|compensation": "salary_expectation",
        r"start.+immediately|available": "availability",
        r"portfolio|samples": "portfolio_url",
        r"cover.+letter": "cover_letter_path",
        r"education|degree": "education_level",
        r"relocate|willing.+move": "willing_to_relocate"
    }

    def __init__(self, applicant_profile: Dict[str, Any] = None):
        """
        Initialize screening questions handler

        Args:
            applicant_profile: Dictionary containing applicant information
                               to use when answering questions
        """
        self.applicant_profile = applicant_profile or {}
        logger.info("ScreeningQuestionsHandler initialized with profile data")

    async def detect_questions(self, page: Page) -> List[ScreeningQuestion]:
        """
        Detect all screening questions on the current page

        This method scans the page for various question types using multiple
        strategies to ensure all questions are found, even with dynamic IDs.

        Args:
            page: Playwright page object

        Returns:
            List of detected ScreeningQuestion objects
        """
        questions = []
        logger.info("Starting screening questions detection")

        try:
            # Strategy 1: Find all fieldsets (common question container)
            fieldsets = await page.query_selector_all("fieldset")
            for fieldset in fieldsets:
                question = await self._analyze_fieldset(fieldset)
                if question:
                    questions.append(question)

            # Strategy 2: Find select dropdowns
            selects = await page.query_selector_all("select")
            for select in selects:
                question = await self._analyze_select(select)
                if question and question not in questions:
                    questions.append(question)

            # Strategy 3: Find radio button groups
            radio_groups = await self._find_radio_groups(page)
            for group in radio_groups:
                question = await self._analyze_radio_group(page, group)
                if question and question not in questions:
                    questions.append(question)

            # Strategy 4: Find textareas (often for longer responses)
            textareas = await page.query_selector_all("textarea")
            for textarea in textareas:
                question = await self._analyze_textarea(textarea)
                if question and question not in questions:
                    questions.append(question)

            # Strategy 5: Find file upload buttons with Indeed's pattern
            upload_buttons = await page.query_selector_all(
                "button[data-testid*='upload-button']"
            )
            for button in upload_buttons:
                question = await self._analyze_upload_button(button)
                if question and question not in questions:
                    questions.append(question)

            logger.info(f"Detected {len(questions)} screening questions")
            return questions

        except Exception as e:
            logger.error(f"Error detecting screening questions: {e}")
            return questions

    async def _analyze_fieldset(self, fieldset: ElementHandle) -> Optional[ScreeningQuestion]:
        """
        Analyze a fieldset element to extract question information

        Args:
            fieldset: Fieldset element to analyze

        Returns:
            ScreeningQuestion if valid question found, None otherwise
        """
        try:
            # Get question text from legend or label
            legend = await fieldset.query_selector("legend")
            question_text = ""
            if legend:
                question_text = await legend.inner_text()

            # Check for file upload button
            upload_btn = await fieldset.query_selector("button[data-testid*='upload']")
            if upload_btn:
                data_testid = await upload_btn.get_attribute("data-testid")
                selector = f"button[data-testid='{data_testid}']"

                return ScreeningQuestion(
                    question_text=question_text or "File Upload",
                    question_type=QuestionType.FILE_UPLOAD,
                    element_selector=selector,
                    required="*" in question_text,
                    data_testid=data_testid
                )

        except Exception as e:
            logger.debug(f"Error analyzing fieldset: {e}")

        return None

    async def _analyze_select(self, select: ElementHandle) -> Optional[ScreeningQuestion]:
        """
        Analyze a select dropdown element

        Args:
            select: Select element to analyze

        Returns:
            ScreeningQuestion if valid, None otherwise
        """
        try:
            # Get associated label
            select_id = await select.get_attribute("id")
            name = await select.get_attribute("name")
            data_testid = await select.get_attribute("data-testid")

            # Find label text
            question_text = ""
            if select_id:
                label = await select.evaluate_handle(
                    f"(el) => document.querySelector('label[for=\"{select_id}\"]')"
                )
                if label:
                    question_text = await label.inner_text()

            # Get options
            options = []
            option_elements = await select.query_selector_all("option")
            for opt in option_elements:
                value = await opt.get_attribute("value")
                label = await opt.get_attribute("label") or await opt.inner_text()
                if value:  # Skip empty/placeholder options
                    options.append({"value": value, "label": label})

            # Build selector
            selector = f"select[name='{name}']" if name else f"#{select_id}"

            return ScreeningQuestion(
                question_text=question_text,
                question_type=QuestionType.SELECT,
                element_selector=selector,
                required="*" in question_text,
                options=options,
                field_name=name,
                data_testid=data_testid
            )

        except Exception as e:
            logger.debug(f"Error analyzing select: {e}")

        return None

    async def _find_radio_groups(self, page: Page) -> List[str]:
        """
        Find all radio button group names on the page

        Returns:
            List of unique radio group names
        """
        try:
            radio_names = await page.evaluate("""
                () => {
                    const radios = document.querySelectorAll('input[type="radio"]');
                    const names = new Set();
                    radios.forEach(r => {
                        if (r.name) names.add(r.name);
                    });
                    return Array.from(names);
                }
            """)
            return radio_names
        except:
            return []

    async def _analyze_radio_group(self, page: Page, group_name: str) -> Optional[ScreeningQuestion]:
        """
        Analyze a radio button group

        Args:
            page: Playwright page object
            group_name: Name attribute of the radio group

        Returns:
            ScreeningQuestion if valid, None otherwise
        """
        try:
            radios = await page.query_selector_all(f"input[type='radio'][name='{group_name}']")
            if not radios:
                return None

            # Get question text from nearest label or parent
            first_radio = radios[0]
            first_id = await first_radio.get_attribute("id")

            question_text = ""
            parent = await first_radio.evaluate_handle("(el) => el.closest('fieldset, div')")
            if parent:
                # Look for question text in parent
                text_elements = await parent.query_selector_all("label, legend, p, span")
                for elem in text_elements:
                    text = await elem.inner_text()
                    if text and len(text) > 10 and "?" in text:
                        question_text = text
                        break

            # Get options
            options = []
            for radio in radios:
                radio_id = await radio.get_attribute("id")
                value = await radio.get_attribute("value")
                label_elem = await page.query_selector(f"label[for='{radio_id}']")
                label_text = await label_elem.inner_text() if label_elem else ""

                options.append({
                    "value": value,
                    "label": label_text,
                    "selector": f"#{radio_id}"
                })

            return ScreeningQuestion(
                question_text=question_text,
                question_type=QuestionType.RADIO,
                element_selector=f"input[name='{group_name}']",
                required="*" in question_text,
                options=options,
                field_name=group_name
            )

        except Exception as e:
            logger.debug(f"Error analyzing radio group {group_name}: {e}")

        return None

    async def _analyze_textarea(self, textarea: ElementHandle) -> Optional[ScreeningQuestion]:
        """
        Analyze a textarea element

        Args:
            textarea: Textarea element to analyze

        Returns:
            ScreeningQuestion if valid, None otherwise
        """
        try:
            textarea_id = await textarea.get_attribute("id")
            name = await textarea.get_attribute("name")

            # Find associated label or question text
            question_text = ""
            if textarea_id:
                label = await textarea.evaluate_handle(
                    f"(el) => document.querySelector('label[for=\"{textarea_id}\"]')"
                )
                if label:
                    question_text = await label.inner_text()

            # If no label, check parent for question text
            if not question_text:
                parent_text = await textarea.evaluate("""
                    (el) => {
                        const parent = el.closest('div, fieldset');
                        if (parent) {
                            const texts = parent.querySelectorAll('label, p, span');
                            for (let t of texts) {
                                if (t.textContent.includes('?')) {
                                    return t.textContent;
                                }
                            }
                        }
                        return '';
                    }
                """)
                question_text = parent_text

            selector = f"#{textarea_id}" if textarea_id else f"textarea[name='{name}']"

            return ScreeningQuestion(
                question_text=question_text,
                question_type=QuestionType.TEXT,
                element_selector=selector,
                required="*" in question_text,
                field_name=name
            )

        except Exception as e:
            logger.debug(f"Error analyzing textarea: {e}")

        return None

    async def _analyze_upload_button(self, button: ElementHandle) -> Optional[ScreeningQuestion]:
        """
        Analyze a file upload button (Indeed pattern)

        Args:
            button: Upload button element

        Returns:
            ScreeningQuestion if valid, None otherwise
        """
        try:
            data_testid = await button.get_attribute("data-testid")

            # Extract question ID from testid
            # Pattern: input-q_[hash]-upload-button
            match = re.search(r'input-(q_[a-f0-9]+)-upload', data_testid or "")
            field_name = match.group(1) if match else None

            # Get question text from parent
            parent = await button.evaluate_handle("(el) => el.closest('fieldset, div')")
            question_text = ""
            if parent:
                legend = await parent.query_selector("legend")
                if legend:
                    question_text = await legend.inner_text()

            return ScreeningQuestion(
                question_text=question_text or "File Upload",
                question_type=QuestionType.FILE_UPLOAD,
                element_selector=f"button[data-testid='{data_testid}']",
                required="*" in question_text,
                field_name=field_name,
                data_testid=data_testid
            )

        except Exception as e:
            logger.debug(f"Error analyzing upload button: {e}")

        return None

    def prepare_answers(self, questions: List[ScreeningQuestion]) -> Dict[str, Any]:
        """
        Prepare answers for detected questions based on applicant profile

        This method uses intelligent matching to map questions to profile data
        and provides safe fallback answers when data is unavailable.

        Args:
            questions: List of detected questions

        Returns:
            Dictionary mapping question selectors to answers
        """
        answers = {}

        for question in questions:
            answer = self._get_answer_for_question(question)
            if answer is not None:
                answers[question.element_selector] = {
                    "value": answer,
                    "type": question.question_type,
                    "question": question.question_text
                }
                logger.debug(f"Prepared answer for '{question.question_text}': {answer}")

        return answers

    def _get_answer_for_question(self, question: ScreeningQuestion) -> Optional[Union[str, bool, Dict]]:
        """
        Get appropriate answer for a specific question

        Args:
            question: The question to answer

        Returns:
            Answer value appropriate for the question type
        """
        question_lower = question.question_text.lower()

        # Try pattern matching first
        for pattern, profile_key in self.QUESTION_PATTERNS.items():
            if re.search(pattern, question_lower):
                if profile_key in self.applicant_profile:
                    value = self.applicant_profile[profile_key]

                    # Handle different question types
                    if question.question_type == QuestionType.SELECT:
                        return self._match_select_option(value, question.options)
                    elif question.question_type == QuestionType.RADIO:
                        return self._match_radio_option(value, question.options)
                    else:
                        return str(value)

        # Provide safe defaults for common questions
        if "experience" in question_lower and "years" in question_lower:
            return self._get_safe_experience_answer(question)

        if "work" in question_lower and ("in-person" in question_lower or "office" in question_lower):
            return self._get_safe_location_answer(question)

        if "authorized" in question_lower and "work" in question_lower:
            return "Yes" if question.question_type == QuestionType.RADIO else "yes"

        if "sponsor" in question_lower:
            return "No" if question.question_type == QuestionType.RADIO else "no"

        if "portfolio" in question_lower and question.question_type == QuestionType.TEXT:
            return self.applicant_profile.get("portfolio_url", "")

        # For file uploads, return path if available
        if question.question_type == QuestionType.FILE_UPLOAD:
            if "cover" in question_lower:
                return self.applicant_profile.get("cover_letter_path")
            elif "portfolio" in question_lower:
                return self.applicant_profile.get("portfolio_pdf_path")

        logger.warning(f"No answer found for question: {question.question_text}")
        return None

    def _match_select_option(self, value: str, options: List[Dict]) -> Optional[str]:
        """
        Match a value to the closest select option

        Args:
            value: The desired value
            options: Available select options

        Returns:
            Best matching option value
        """
        if not options:
            return value

        value_lower = str(value).lower()

        # Try exact match first
        for opt in options:
            if opt["label"].lower() == value_lower:
                return opt["value"]

        # Try partial match
        for opt in options:
            if value_lower in opt["label"].lower() or opt["label"].lower() in value_lower:
                return opt["value"]

        # For years of experience, try numeric matching
        if value.isdigit():
            years = int(value)
            for opt in options:
                # Match patterns like "3 years", "3-5 years", "3+ years"
                if re.search(rf"\b{years}\b", opt["label"]):
                    return opt["value"]

        return None

    def _match_radio_option(self, value: Any, options: List[Dict]) -> Optional[str]:
        """
        Match a value to the appropriate radio option

        Args:
            value: The desired value (often boolean)
            options: Available radio options

        Returns:
            Selector for the matching radio button
        """
        if not options:
            return None

        # Handle boolean values
        if isinstance(value, bool):
            positive = ["yes", "true", "agree", "able", "can"]
            negative = ["no", "false", "disagree", "unable", "cannot"]

            for opt in options:
                label_lower = opt["label"].lower()
                if value and any(p in label_lower for p in positive):
                    return opt["selector"]
                elif not value and any(n in label_lower for n in negative):
                    return opt["selector"]

        # Handle string matching
        value_str = str(value).lower()
        for opt in options:
            if value_str in opt["label"].lower():
                return opt["selector"]

        return None

    def _get_safe_experience_answer(self, question: ScreeningQuestion) -> Optional[str]:
        """
        Provide a safe default for experience questions

        Args:
            question: The experience question

        Returns:
            Safe default answer
        """
        # Default to mid-range experience if not specified
        if question.question_type == QuestionType.SELECT and question.options:
            # Look for 2-3 years option as safe default
            for opt in question.options:
                if "2" in opt["label"] or "3" in opt["label"]:
                    return opt["value"]
            # Otherwise return first non-zero option
            for opt in question.options:
                if "0" not in opt["label"] and "less" not in opt["label"].lower():
                    return opt["value"]

        return "2"  # Safe default

    def _get_safe_location_answer(self, question: ScreeningQuestion) -> Optional[str]:
        """
        Provide safe answer for location/in-person questions

        Args:
            question: The location question

        Returns:
            Safe default answer (usually "yes" to show flexibility)
        """
        if question.question_type == QuestionType.RADIO and question.options:
            # Default to "yes" for in-person to show flexibility
            for opt in question.options:
                if "yes" in opt["label"].lower() or "able" in opt["label"].lower():
                    return opt["selector"]

        return "yes"

    async def fill_questions(self, page: Page, answers: Dict[str, Any]) -> Dict[str, bool]:
        """
        Fill screening questions with prepared answers

        Args:
            page: Playwright page object
            answers: Dictionary of answers from prepare_answers()

        Returns:
            Dictionary mapping selectors to success status
        """
        results = {}

        for selector, answer_data in answers.items():
            try:
                question_type = answer_data["type"]
                value = answer_data["value"]

                if question_type == QuestionType.TEXT:
                    element = await page.query_selector(selector)
                    if element:
                        await element.fill(value)
                        results[selector] = True

                elif question_type == QuestionType.SELECT:
                    element = await page.query_selector(selector)
                    if element:
                        await element.select_option(value=value)
                        results[selector] = True

                elif question_type == QuestionType.RADIO:
                    # Value contains the selector for the specific radio button
                    radio = await page.query_selector(value)
                    if radio:
                        await radio.check()
                        results[selector] = True

                elif question_type == QuestionType.FILE_UPLOAD:
                    # Skip file uploads - handled by CustomDocumentHandler
                    logger.info(f"Skipping file upload for {selector} - handled separately")
                    results[selector] = False

                logger.info(f"Successfully filled question: {answer_data['question']}")

            except Exception as e:
                logger.error(f"Failed to fill {selector}: {e}")
                results[selector] = False

        return results

    async def validate_required_fields(self, page: Page, questions: List[ScreeningQuestion]) -> List[str]:
        """
        Check that all required questions have been answered

        Args:
            page: Playwright page object
            questions: List of questions to validate

        Returns:
            List of selectors for unanswered required questions
        """
        unanswered = []

        for question in questions:
            if not question.required:
                continue

            try:
                if question.question_type == QuestionType.TEXT:
                    elem = await page.query_selector(question.element_selector)
                    value = await elem.input_value() if elem else ""
                    if not value.strip():
                        unanswered.append(question.element_selector)

                elif question.question_type == QuestionType.SELECT:
                    elem = await page.query_selector(question.element_selector)
                    value = await elem.input_value() if elem else ""
                    if not value or value == "":  # Empty option value
                        unanswered.append(question.element_selector)

                elif question.question_type == QuestionType.RADIO:
                    checked = await page.query_selector(
                        f"{question.element_selector}:checked"
                    )
                    if not checked:
                        unanswered.append(question.element_selector)

            except Exception as e:
                logger.warning(f"Error validating {question.element_selector}: {e}")

        if unanswered:
            logger.warning(f"Found {len(unanswered)} unanswered required questions")

        return unanswered