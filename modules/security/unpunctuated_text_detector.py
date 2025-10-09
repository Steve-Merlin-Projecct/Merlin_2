"""
Unpunctuated Text Stream Detector
Detects LLM injection attacks using long text streams without punctuation

This module implements detection for a new LLM injection attack vector where
attackers use long streams of text without adequate punctuation to bypass
security controls or cause model failures.

Author: Automated Job Application System
Version: 1.0
Date: 2025-10-09
"""

import re
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """
    Results from unpunctuated text detection

    Attributes:
        detected: Whether suspicious unpunctuated streams were found
        severity: Severity level ('low', 'medium', 'high', 'critical')
        suspicious_sequences: List of detected suspicious text sequences
        total_sequences_checked: Total number of sequences analyzed
        detection_details: Additional details about the detection
        timestamp: When the detection was performed
    """

    detected: bool
    severity: str
    suspicious_sequences: List[Dict] = field(default_factory=list)
    total_sequences_checked: int = 0
    detection_details: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class UnpunctuatedTextDetector:
    """
    Detects long streams of text without adequate punctuation

    This detector analyzes text input for sequences that exceed a character
    threshold while having insufficient punctuation density, which may indicate
    an LLM injection attack attempt.

    Usage:
        detector = UnpunctuatedTextDetector()
        result = detector.detect(job_description)
        if result.detected:
            logger.warning(f"Suspicious text detected: {result.severity}")
    """

    def __init__(
        self,
        char_threshold: int = 200,
        min_punctuation_ratio: float = 0.02,
        punctuation_marks: str = ".,;:!?-—()[]{}'\""
    ):
        """
        Initialize detector with configurable thresholds

        Args:
            char_threshold: Minimum character count to flag (default: 200)
            min_punctuation_ratio: Minimum punctuation density (default: 0.02 = 2%)
            punctuation_marks: String of characters considered punctuation
        """
        self.char_threshold = char_threshold
        self.min_punctuation_ratio = min_punctuation_ratio
        self.punctuation_marks = set(punctuation_marks)

        logger.info(
            f"UnpunctuatedTextDetector initialized: threshold={char_threshold}, "
            f"min_ratio={min_punctuation_ratio}"
        )

    def detect(self, text: str) -> DetectionResult:
        """
        Detect unpunctuated text streams in input

        Analyzes the input text by:
        1. Splitting into analyzable sequences (by newlines/paragraphs)
        2. Checking each sequence for character length and punctuation density
        3. Flagging sequences that meet suspicious criteria
        4. Calculating overall severity based on findings

        Args:
            text: Input text to analyze

        Returns:
            DetectionResult with detection findings
        """
        if not text or not isinstance(text, str):
            return DetectionResult(
                detected=False,
                severity='low',
                detection_details={'reason': 'Empty or invalid input'}
            )

        # Split text into sequences
        sequences = self._split_into_sequences(text)

        # Analyze each sequence
        suspicious_sequences = []
        total_checked = 0

        for sequence in sequences:
            total_checked += 1
            is_suspicious, details = self._analyze_sequence(sequence)

            if is_suspicious:
                suspicious_sequences.append(details)

        # Determine overall detection result
        detected = len(suspicious_sequences) > 0

        if detected:
            severity = self._calculate_overall_severity(suspicious_sequences)
            logger.warning(
                f"Unpunctuated stream detected: {len(suspicious_sequences)} sequences, "
                f"severity={severity}"
            )
        else:
            severity = 'low'

        return DetectionResult(
            detected=detected,
            severity=severity,
            suspicious_sequences=suspicious_sequences,
            total_sequences_checked=total_checked,
            detection_details={
                'threshold_used': self.char_threshold,
                'min_ratio_used': self.min_punctuation_ratio,
                'total_sequences': total_checked,
                'suspicious_count': len(suspicious_sequences)
            }
        )

    def _split_into_sequences(self, text: str) -> List[str]:
        """
        Split text into analyzable sequences

        Splits on double newlines (paragraphs) and single newlines,
        filtering out empty sequences.

        Args:
            text: Input text to split

        Returns:
            List of text sequences to analyze
        """
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)

        sequences = []
        for para in paragraphs:
            # Further split by single newlines for line-by-line analysis
            lines = para.split('\n')
            sequences.extend(lines)

        # Filter out empty sequences and strip whitespace
        sequences = [s.strip() for s in sequences if s.strip()]

        return sequences

    def _analyze_sequence(self, sequence: str) -> Tuple[bool, Dict]:
        """
        Analyze a single sequence for punctuation density

        Args:
            sequence: Text sequence to analyze

        Returns:
            Tuple of (is_suspicious, details_dict)
        """
        # Check if sequence meets minimum length threshold
        if len(sequence) < self.char_threshold:
            return False, {}

        # Count punctuation marks
        punct_count = sum(1 for char in sequence if char in self.punctuation_marks)

        # Calculate punctuation ratio
        punct_ratio = punct_count / len(sequence) if len(sequence) > 0 else 0

        # Determine if suspicious
        is_suspicious = punct_ratio < self.min_punctuation_ratio

        if is_suspicious:
            severity = self._calculate_severity(sequence, punct_ratio)

            details = {
                'sequence_length': len(sequence),
                'punctuation_count': punct_count,
                'punctuation_ratio': round(punct_ratio, 4),
                'severity': severity,
                'text_sample': sequence[:200] + '...' if len(sequence) > 200 else sequence,
                'threshold_exceeded_by': len(sequence) - self.char_threshold,
                'ratio_below_threshold_by': round(self.min_punctuation_ratio - punct_ratio, 4)
            }

            return True, details

        return False, {}

    def _calculate_severity(self, sequence: str, punct_ratio: float) -> str:
        """
        Calculate severity level based on sequence characteristics

        Severity levels:
        - low: Slightly below threshold
        - medium: Moderately below threshold
        - high: Significantly below threshold
        - critical: Zero or near-zero punctuation with very long sequence

        Args:
            sequence: The text sequence
            punct_ratio: Calculated punctuation ratio

        Returns:
            Severity level string
        """
        ratio_diff = self.min_punctuation_ratio - punct_ratio
        length = len(sequence)

        # Critical: zero punctuation and very long (500+ chars)
        if punct_ratio == 0 and length >= 500:
            return 'critical'

        # Critical: near-zero punctuation and extremely long (800+ chars)
        if punct_ratio < 0.005 and length >= 800:
            return 'critical'

        # High: very low punctuation (< 1%) or very long (600+ chars)
        if punct_ratio < 0.01 or length >= 600:
            return 'high'

        # Medium: below threshold by significant margin
        if ratio_diff >= 0.015:  # 1.5% or more below threshold
            return 'medium'

        # Low: barely below threshold
        return 'low'

    def _calculate_overall_severity(self, suspicious_sequences: List[Dict]) -> str:
        """
        Calculate overall severity based on all suspicious sequences found

        Args:
            suspicious_sequences: List of suspicious sequence details

        Returns:
            Overall severity level
        """
        if not suspicious_sequences:
            return 'low'

        # Count sequences by severity
        severities = [seq['severity'] for seq in suspicious_sequences]

        # Critical if any critical sequences
        if 'critical' in severities:
            return 'critical'

        # High if multiple high-severity or many medium
        if severities.count('high') >= 2 or severities.count('medium') >= 3:
            return 'high'

        # High if single high-severity
        if 'high' in severities:
            return 'high'

        # Medium if any medium-severity
        if 'medium' in severities:
            return 'medium'

        return 'low'


def integrate_with_sanitizer(text: str) -> Tuple[str, DetectionResult]:
    """
    Integration point for existing sanitize_job_description()

    This function provides a clean integration point for the existing
    job description sanitizer. It detects unpunctuated streams and logs
    findings, but returns the original text unchanged (non-destructive).

    Args:
        text: Job description text to check

    Returns:
        Tuple of (original_text, detection_result)
    """
    detector = UnpunctuatedTextDetector()
    result = detector.detect(text)

    if result.detected:
        logger.warning(
            f"Unpunctuated stream detected - Severity: {result.severity}, "
            f"Sequences: {len(result.suspicious_sequences)}, "
            f"Samples: {[s.get('text_sample', '')[:100] for s in result.suspicious_sequences[:2]]}"
        )

        # Additional detailed logging for high/critical severity
        if result.severity in ['high', 'critical']:
            logger.error(
                f"HIGH-SEVERITY unpunctuated stream detected!\n"
                f"Details: {result.detection_details}\n"
                f"Suspicious sequences: {len(result.suspicious_sequences)}"
            )

    return text, result


# Convenience function for quick checks
def quick_check(text: str, threshold: int = 200) -> bool:
    """
    Quick check for unpunctuated streams (convenience function)

    Args:
        text: Text to check
        threshold: Character threshold (default: 200)

    Returns:
        True if suspicious streams detected, False otherwise
    """
    detector = UnpunctuatedTextDetector(char_threshold=threshold)
    result = detector.detect(text)
    return result.detected
