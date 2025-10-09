"""
Smart Typography Enhancement for Document Generation

This module applies professional typography transformations to document text including:
- Smart quotation marks (straight to curly)
- Smart dashes (double hyphen to em dash, ranges to en dash)
- Smart ellipsis (three periods to proper ellipsis character)
- Non-breaking spaces (after titles, units, between initials)
- Special character formatting (degree symbols, trademark, copyright)

Author: Automated Job Application System
Version: 1.0.0
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from .typography_constants import (
    SMART_QUOTE_RULES,
    SMART_DASH_RULES,
    SMART_ELLIPSIS_PATTERN,
    SMART_ELLIPSIS_REPLACEMENT,
    NON_BREAKING_SPACE_RULES,
    SPECIAL_CHARACTER_RULES,
    count_smart_typography,
)
from .authenticity_config import (
    ENABLE_SMART_QUOTES,
    ENABLE_SMART_DASHES,
    ENABLE_SMART_ELLIPSIS,
    ENABLE_NON_BREAKING_SPACES,
    ENABLE_SPECIAL_CHARACTERS,
)

logger = logging.getLogger(__name__)


class SmartTypography:
    """
    Applies professional typography transformations to text

    This class provides methods to enhance document text with smart typography
    including quotes, dashes, ellipsis, non-breaking spaces, and special characters.
    All transformations are configurable and can be enabled/disabled individually.
    """

    def __init__(
        self,
        enable_smart_quotes: bool = ENABLE_SMART_QUOTES,
        enable_smart_dashes: bool = ENABLE_SMART_DASHES,
        enable_smart_ellipsis: bool = ENABLE_SMART_ELLIPSIS,
        enable_non_breaking_spaces: bool = ENABLE_NON_BREAKING_SPACES,
        enable_special_characters: bool = ENABLE_SPECIAL_CHARACTERS,
    ):
        """
        Initialize Smart Typography processor

        Args:
            enable_smart_quotes: Enable smart quotation mark conversion
            enable_smart_dashes: Enable smart dash conversion
            enable_smart_ellipsis: Enable smart ellipsis conversion
            enable_non_breaking_spaces: Enable non-breaking space insertion
            enable_special_characters: Enable special character formatting
        """
        self.enable_smart_quotes = enable_smart_quotes
        self.enable_smart_dashes = enable_smart_dashes
        self.enable_smart_ellipsis = enable_smart_ellipsis
        self.enable_non_breaking_spaces = enable_non_breaking_spaces
        self.enable_special_characters = enable_special_characters

        logger.info(
            f"SmartTypography initialized: "
            f"quotes={enable_smart_quotes}, dashes={enable_smart_dashes}, "
            f"ellipsis={enable_smart_ellipsis}, nbsp={enable_non_breaking_spaces}, "
            f"special={enable_special_characters}"
        )

    def apply_smart_quotes(self, text: str) -> str:
        """
        Convert straight quotes to smart (curly) quotes

        Handles both double and single quotes, including apostrophes in
        contractions and possessives.

        Args:
            text: Input text with straight quotes

        Returns:
            Text with smart curly quotes

        Examples:
            >>> st = SmartTypography()
            >>> st.apply_smart_quotes('"Hello World"')
            '"Hello World"'
            >>> st.apply_smart_quotes("It's John's book")
            "It's John's book"
        """
        if not text or not self.enable_smart_quotes:
            return text

        result = text
        for pattern, replacement in SMART_QUOTE_RULES:
            result = pattern.sub(replacement, result)

        return result

    def apply_smart_dashes(self, text: str) -> str:
        """
        Convert hyphens to appropriate dashes (em dash, en dash)

        - Double hyphens (--) → em dash (—)
        - Number ranges (2020-2023) → en dash (2020–2023)
        - Date ranges (May-June) → en dash (May–June)

        Args:
            text: Input text with hyphens

        Returns:
            Text with appropriate dashes

        Examples:
            >>> st = SmartTypography()
            >>> st.apply_smart_dashes('2020-2023')
            '2020–2023'
            >>> st.apply_smart_dashes('word--word')
            'word—word'
        """
        if not text or not self.enable_smart_dashes:
            return text

        result = text
        for pattern, replacement in SMART_DASH_RULES:
            result = pattern.sub(replacement, result)

        return result

    def apply_smart_ellipsis(self, text: str) -> str:
        """
        Convert three periods to proper ellipsis character

        Args:
            text: Input text with three periods

        Returns:
            Text with proper ellipsis (…)

        Examples:
            >>> st = SmartTypography()
            >>> st.apply_smart_ellipsis('Wait...')
            'Wait…'
        """
        if not text or not self.enable_smart_ellipsis:
            return text

        return SMART_ELLIPSIS_PATTERN.sub(SMART_ELLIPSIS_REPLACEMENT, text)

    def apply_non_breaking_spaces(self, text: str) -> str:
        """
        Insert non-breaking spaces in appropriate locations

        - After titles: Dr. Smith → Dr. Smith (with nbsp)
        - Between initials: J. Smith → J. Smith (with nbsp)
        - Before units: 10 MB → 10 MB (with nbsp)
        - Before percent: 50% → 50% (with nbsp)

        Args:
            text: Input text

        Returns:
            Text with non-breaking spaces inserted

        Examples:
            >>> st = SmartTypography()
            >>> st.apply_non_breaking_spaces('Dr. Smith')
            'Dr. Smith'  # with non-breaking space
        """
        if not text or not self.enable_non_breaking_spaces:
            return text

        result = text
        for pattern, replacement in NON_BREAKING_SPACE_RULES:
            result = pattern.sub(replacement, result)

        return result

    def apply_special_characters(self, text: str) -> str:
        """
        Convert special character sequences to proper Unicode characters

        - (TM) → ™
        - (R) → ®
        - (C) → ©
        - degrees → °
        - Fractions: 1/2 → ½, 1/4 → ¼, etc.
        - Multiplication: 10 x 20 → 10×20

        Args:
            text: Input text

        Returns:
            Text with proper special characters

        Examples:
            >>> st = SmartTypography()
            >>> st.apply_special_characters('Copyright (C) 2025')
            'Copyright © 2025'
            >>> st.apply_special_characters('Temperature: 75 degrees')
            'Temperature: 75°'
        """
        if not text or not self.enable_special_characters:
            return text

        result = text
        for pattern, replacement in SPECIAL_CHARACTER_RULES:
            result = pattern.sub(replacement, result)

        return result

    def apply_all(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Apply all enabled typography transformations

        Applies transformations in optimal order:
        1. Smart quotes
        2. Smart dashes
        3. Smart ellipsis
        4. Non-breaking spaces
        5. Special characters

        Args:
            text: Input text

        Returns:
            Tuple of (transformed_text, transformation_stats)
            Stats include counts of each transformation applied

        Examples:
            >>> st = SmartTypography()
            >>> enhanced_text, stats = st.apply_all('"Hello"--2020-2023...')
            >>> print(enhanced_text)
            '"Hello"—2020–2023…'
            >>> print(stats['smart_quotes'])
            2
        """
        if not text:
            return text, {}

        original_text = text
        result = text

        # Apply transformations in order
        if self.enable_smart_quotes:
            result = self.apply_smart_quotes(result)

        if self.enable_smart_dashes:
            result = self.apply_smart_dashes(result)

        if self.enable_smart_ellipsis:
            result = self.apply_smart_ellipsis(result)

        if self.enable_non_breaking_spaces:
            result = self.apply_non_breaking_spaces(result)

        if self.enable_special_characters:
            result = self.apply_special_characters(result)

        # Calculate transformation statistics
        stats = count_smart_typography(result)
        stats['original_length'] = len(original_text)
        stats['enhanced_length'] = len(result)
        stats['transformations_applied'] = sum([
            self.enable_smart_quotes,
            self.enable_smart_dashes,
            self.enable_smart_ellipsis,
            self.enable_non_breaking_spaces,
            self.enable_special_characters,
        ])

        if stats['smart_quotes'] > 0 or stats['smart_dashes'] > 0 or stats['smart_ellipsis'] > 0:
            logger.debug(
                f"Typography enhanced: {stats['smart_quotes']} quotes, "
                f"{stats['smart_dashes']} dashes, {stats['smart_ellipsis']} ellipsis"
            )

        return result, stats

    def enhance_paragraph_text(self, paragraph_text: str) -> str:
        """
        Convenience method to enhance a paragraph's text

        Args:
            paragraph_text: Paragraph text to enhance

        Returns:
            Enhanced text with all typography transformations
        """
        enhanced_text, _ = self.apply_all(paragraph_text)
        return enhanced_text

    def get_typography_quality_score(self, text: str) -> int:
        """
        Calculate typography quality score (0-100)

        Analyzes text for presence of smart typography elements and
        calculates a quality score based on:
        - Presence of smart quotes vs straight quotes
        - Presence of smart dashes
        - Proper ellipsis usage
        - Non-breaking spaces
        - Special characters

        Args:
            text: Text to analyze

        Returns:
            Quality score from 0 (no smart typography) to 100 (excellent)
        """
        if not text:
            return 0

        stats = count_smart_typography(text)
        score = 0

        # Check for smart quotes (30 points)
        if stats['smart_quotes'] > 0:
            score += 30

        # Check for smart dashes (25 points)
        if stats['smart_dashes'] > 0:
            score += 25

        # Check for smart ellipsis (20 points)
        if stats['smart_ellipsis'] > 0:
            score += 20

        # Check for non-breaking spaces (15 points)
        if stats['non_breaking_spaces'] > 0:
            score += 15

        # Bonus: No straight quotes remaining (10 points)
        if '"' not in text and "'" not in text:
            score += 10

        return min(score, 100)

    def __repr__(self) -> str:
        """String representation of SmartTypography instance"""
        enabled_features = []
        if self.enable_smart_quotes:
            enabled_features.append("quotes")
        if self.enable_smart_dashes:
            enabled_features.append("dashes")
        if self.enable_smart_ellipsis:
            enabled_features.append("ellipsis")
        if self.enable_non_breaking_spaces:
            enabled_features.append("nbsp")
        if self.enable_special_characters:
            enabled_features.append("special")

        return f"SmartTypography(enabled=[{', '.join(enabled_features)}])"


# Module-level convenience functions

def enhance_text(text: str, **kwargs) -> str:
    """
    Convenience function to enhance text with smart typography

    Args:
        text: Text to enhance
        **kwargs: Optional configuration overrides for SmartTypography

    Returns:
        Enhanced text

    Example:
        >>> enhanced = enhance_text('"Hello" -- this is great...')
        >>> print(enhanced)
        '"Hello" — this is great…'
    """
    typography = SmartTypography(**kwargs)
    enhanced_text, _ = typography.apply_all(text)
    return enhanced_text


def get_typography_stats(text: str) -> Dict[str, int]:
    """
    Get typography statistics for text

    Args:
        text: Text to analyze

    Returns:
        Dictionary with counts of smart typography elements
    """
    return count_smart_typography(text)
