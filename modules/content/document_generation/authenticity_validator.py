"""
Authenticity Validation and Scoring for Generated Documents

This module validates document authenticity by checking metadata completeness,
timestamp realism, typography quality, template completion, and document structure.
Generates authenticity scores (0-100) and detailed validation reports.

Author: Automated Job Application System
Version: 1.0.0
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .authenticity_config import (
    AUTHENTICITY_SCORING_WEIGHTS,
    get_authenticity_level,
    MINIMUM_AUTHENTICITY_SCORE,
    BUSINESS_HOURS_START,
    BUSINESS_HOURS_END,
)
from .typography_constants import count_smart_typography

logger = logging.getLogger(__name__)


class AuthenticityValidator:
    """
    Validates document authenticity and generates quality scores

    This validator checks multiple aspects of document authenticity:
    1. Metadata completeness (required fields populated)
    2. Timestamp realism (realistic creation/modification dates)
    3. Typography quality (smart quotes, dashes, etc.)
    4. Template completion (no unreplaced variables)
    5. Document statistics (word count, page count reasonable)
    6. Structure integrity (valid file format)
    """

    def __init__(self):
        """Initialize Authenticity Validator"""
        self.scoring_weights = AUTHENTICITY_SCORING_WEIGHTS
        logger.info("AuthenticityValidator initialized")

    def validate_metadata_completeness(self, metadata: Dict) -> Tuple[int, List[str]]:
        """
        Validate metadata completeness (25 points max)

        Checks that all required metadata fields are populated with
        realistic, non-default values.

        Required fields:
        - author (not blank)
        - title (not blank)
        - subject (not blank)
        - created (timestamp present)
        - modified (timestamp present)

        Args:
            metadata: Document metadata dictionary

        Returns:
            Tuple of (score, list_of_issues)
        """
        score = 0
        issues = []
        max_score = self.scoring_weights['metadata_completeness']

        core_props = metadata.get('core_properties', {})

        # Author field (5 points)
        author = core_props.get('author', '')
        if author and len(author) > 2:
            score += 5
        else:
            issues.append("Author field is blank or too short")

        # Title field (5 points)
        title = core_props.get('title', '')
        if title and len(title) > 5:
            score += 5
        else:
            issues.append("Title field is blank or too short")

        # Subject field (5 points)
        subject = core_props.get('subject', '')
        if subject and len(subject) > 3:
            score += 5
        else:
            issues.append("Subject field is blank or too short")

        # Creation timestamp (5 points)
        created = core_props.get('created')
        if created and isinstance(created, datetime):
            score += 5
        else:
            issues.append("Creation timestamp missing or invalid")

        # Modification timestamp (5 points)
        modified = core_props.get('modified')
        if modified and isinstance(modified, datetime):
            score += 5
        else:
            issues.append("Modification timestamp missing or invalid")

        logger.debug(f"Metadata completeness score: {score}/{max_score}")
        return score, issues

    def validate_timestamp_realism(self, metadata: Dict) -> Tuple[int, List[str]]:
        """
        Validate timestamp realism (20 points max)

        Checks that timestamps appear authentic:
        - Created date is 1-90 days ago (not too old, not future)
        - Modified date is after created date
        - Created time is during business hours (9 AM - 6 PM)
        - Created day is weekday (Monday-Friday)

        Args:
            metadata: Document metadata dictionary

        Returns:
            Tuple of (score, list_of_issues)
        """
        score = 0
        issues = []
        max_score = self.scoring_weights['timestamp_realism']

        core_props = metadata.get('core_properties', {})
        created = core_props.get('created')
        modified = core_props.get('modified')

        if not created or not isinstance(created, datetime):
            issues.append("Creation timestamp missing")
            return 0, issues

        now = datetime.now()

        # Created date reasonable (1-90 days ago): 6 points
        days_old = (now - created).days
        if 1 <= days_old <= 90:
            score += 6
        elif days_old < 0:
            issues.append("Creation date is in the future")
        elif days_old > 365:
            issues.append(f"Creation date is very old ({days_old} days)")

        # Modified after created: 5 points
        if modified and isinstance(modified, datetime):
            if modified >= created:
                score += 5
            else:
                issues.append("Modification date is before creation date")
        else:
            issues.append("Modification timestamp missing")

        # Creation during business hours: 5 points
        if BUSINESS_HOURS_START <= created.hour < BUSINESS_HOURS_END:
            score += 5
        else:
            issues.append(f"Creation time outside business hours: {created.hour}:00")

        # Creation on weekday: 4 points
        if created.weekday() < 5:  # Monday=0, Friday=4
            score += 4
        else:
            issues.append(f"Creation date is weekend: {created.strftime('%A')}")

        logger.debug(f"Timestamp realism score: {score}/{max_score}")
        return score, issues

    def validate_editing_time(self, metadata: Dict) -> Tuple[int, List[str]]:
        """
        Validate editing time realism (15 points max)

        Checks that editing time (TotalTime) is set and reasonable:
        - Not 0 (instant creation is suspicious)
        - Not >1000 minutes (unrealistic for resume/cover letter)
        - Within reasonable range: 20-300 minutes

        Args:
            metadata: Document metadata dictionary

        Returns:
            Tuple of (score, list_of_issues)
        """
        score = 0
        issues = []
        max_score = self.scoring_weights['editing_time']

        app_props = metadata.get('app_properties', {})
        total_time = app_props.get('total_time', 0)

        # Editing time is set and > 0: 8 points
        if total_time > 0:
            score += 8
        else:
            issues.append("Editing time is 0 (instant creation is unrealistic)")

        # Editing time in reasonable range (20-300 minutes): 7 points
        if 20 <= total_time <= 300:
            score += 7
        elif total_time > 300:
            issues.append(f"Editing time very high: {total_time} minutes")
        elif 0 < total_time < 20:
            issues.append(f"Editing time very low: {total_time} minutes")

        logger.debug(f"Editing time score: {score}/{max_score} (time={total_time} min)")
        return score, issues

    def validate_typography_quality(self, text_content: str) -> Tuple[int, List[str]]:
        """
        Validate typography quality (15 points max)

        Checks for presence of smart typography:
        - Smart quotes (curly quotes)
        - Smart dashes (em dash, en dash)
        - Smart ellipsis
        - No remaining straight quotes

        Args:
            text_content: Full document text

        Returns:
            Tuple of (score, list_of_issues)
        """
        score = 0
        issues = []
        max_score = self.scoring_weights['typography_quality']

        if not text_content:
            issues.append("No text content to validate")
            return 0, issues

        stats = count_smart_typography(text_content)

        # Smart quotes present: 6 points
        if stats['smart_quotes'] > 0:
            score += 6
        else:
            issues.append("No smart quotes found")

        # Smart dashes present: 5 points
        if stats['smart_dashes'] > 0:
            score += 5
        else:
            issues.append("No smart dashes found")

        # No straight quotes remaining: 4 points
        if '"' not in text_content and "'" not in text_content:
            score += 4
        else:
            straight_count = text_content.count('"') + text_content.count("'")
            issues.append(f"{straight_count} straight quotes remain (should be converted)")

        logger.debug(f"Typography quality score: {score}/{max_score}")
        return score, issues

    def validate_template_completion(self, text_content: str) -> Tuple[int, List[str]]:
        """
        Validate template completion (10 points max)

        Checks for unreplaced template variables:
        - No <<variable>> placeholders remain
        - No {placeholder} variables remain

        Args:
            text_content: Full document text

        Returns:
            Tuple of (score, list_of_issues)
        """
        score = 0
        issues = []
        max_score = self.scoring_weights['template_completion']

        if not text_content:
            issues.append("No text content to validate")
            return 0, issues

        # Check for unreplaced <<variable>> patterns
        template_vars = re.findall(r'<<([^>]+)>>', text_content)

        # Check for unreplaced {variable} patterns (excluding common punctuation)
        job_vars = re.findall(r'\{([a-zA-Z_]+)\}', text_content)

        # All template variables replaced: 5 points
        if not template_vars:
            score += 5
        else:
            issues.append(f"{len(template_vars)} unreplaced template variables: {', '.join(template_vars[:3])}")

        # All job variables replaced: 5 points
        if not job_vars:
            score += 5
        else:
            issues.append(f"{len(job_vars)} unreplaced job variables: {', '.join(job_vars[:3])}")

        logger.debug(f"Template completion score: {score}/{max_score}")
        return score, issues

    def validate_structure_integrity(self, file_path: Optional[str] = None) -> Tuple[int, List[str]]:
        """
        Validate document structure integrity (15 points max)

        Checks that document has valid structure:
        - File exists
        - File size reasonable (20 KB - 500 KB)
        - File is valid ZIP (for DOCX)

        Args:
            file_path: Path to document file

        Returns:
            Tuple of (score, list_of_issues)
        """
        score = 0
        issues = []
        max_score = self.scoring_weights['structure_integrity']

        if not file_path:
            issues.append("No file path provided for structure validation")
            return 0, issues

        path = Path(file_path)

        # File exists: 5 points
        if path.exists():
            score += 5
        else:
            issues.append("File does not exist")
            return score, issues

        # File size reasonable: 5 points
        file_size = path.stat().st_size
        if 20 * 1024 <= file_size <= 500 * 1024:  # 20 KB - 500 KB
            score += 5
        elif file_size < 20 * 1024:
            issues.append(f"File size very small: {file_size/1024:.1f} KB")
        else:
            issues.append(f"File size very large: {file_size/1024:.1f} KB")

        # File is valid ZIP (DOCX): 5 points
        try:
            import zipfile
            if zipfile.is_zipfile(file_path):
                score += 5
            else:
                issues.append("File is not a valid ZIP/DOCX")
        except Exception as e:
            issues.append(f"Error checking ZIP structure: {str(e)}")

        logger.debug(f"Structure integrity score: {score}/{max_score}")
        return score, issues

    def calculate_authenticity_score(
        self,
        metadata: Dict,
        text_content: str = "",
        file_path: Optional[str] = None,
    ) -> Dict:
        """
        Calculate overall authenticity score (0-100)

        Performs all validation checks and combines scores using
        configured weights.

        Args:
            metadata: Document metadata dictionary
            text_content: Full document text
            file_path: Path to document file

        Returns:
            Dictionary with score and detailed results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'scores': {},
            'issues': {},
            'total_score': 0,
            'level': '',
            'passed': False,
        }

        # Run all validation checks
        metadata_score, metadata_issues = self.validate_metadata_completeness(metadata)
        timestamp_score, timestamp_issues = self.validate_timestamp_realism(metadata)
        editing_score, editing_issues = self.validate_editing_time(metadata)
        typography_score, typography_issues = self.validate_typography_quality(text_content)
        template_score, template_issues = self.validate_template_completion(text_content)
        structure_score, structure_issues = self.validate_structure_integrity(file_path)

        # Store individual scores
        results['scores'] = {
            'metadata_completeness': metadata_score,
            'timestamp_realism': timestamp_score,
            'editing_time': editing_score,
            'typography_quality': typography_score,
            'template_completion': template_score,
            'structure_integrity': structure_score,
        }

        # Store issues
        results['issues'] = {
            'metadata_completeness': metadata_issues,
            'timestamp_realism': timestamp_issues,
            'editing_time': editing_issues,
            'typography_quality': typography_issues,
            'template_completion': template_issues,
            'structure_integrity': structure_issues,
        }

        # Calculate total score
        total_score = sum(results['scores'].values())
        results['total_score'] = total_score

        # Determine authenticity level
        results['level'] = get_authenticity_level(total_score)

        # Check if passes minimum threshold
        results['passed'] = total_score >= MINIMUM_AUTHENTICITY_SCORE

        # Count total issues
        all_issues = [issue for issue_list in results['issues'].values() for issue in issue_list]
        results['total_issues'] = len(all_issues)

        logger.info(
            f"Authenticity score: {total_score}/100 ({results['level']}) - "
            f"{len(all_issues)} issues found - "
            f"{'PASSED' if results['passed'] else 'FAILED'}"
        )

        return results

    def generate_verification_report(self, validation_results: Dict) -> str:
        """
        Generate human-readable verification report

        Args:
            validation_results: Results from calculate_authenticity_score()

        Returns:
            Formatted verification report as string
        """
        report = []
        report.append("=" * 70)
        report.append("DOCUMENT AUTHENTICITY VERIFICATION REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {validation_results['timestamp']}")
        report.append(f"Overall Score: {validation_results['total_score']}/100 ({validation_results['level'].upper()})")
        report.append(f"Status: {'✓ PASSED' if validation_results['passed'] else '✗ FAILED'}")
        report.append(f"Total Issues: {validation_results['total_issues']}")
        report.append("")

        # Score breakdown
        report.append("SCORE BREAKDOWN:")
        report.append("-" * 70)
        for component, score in validation_results['scores'].items():
            max_score = self.scoring_weights[component]
            percentage = (score / max_score * 100) if max_score > 0 else 0
            report.append(f"  {component.replace('_', ' ').title():<30} {score:>2}/{max_score:<2} ({percentage:>5.1f}%)")

        # Issues
        if validation_results['total_issues'] > 0:
            report.append("")
            report.append("ISSUES FOUND:")
            report.append("-" * 70)
            for component, issues in validation_results['issues'].items():
                if issues:
                    report.append(f"  {component.replace('_', ' ').title()}:")
                    for issue in issues:
                        report.append(f"    • {issue}")

        report.append("=" * 70)

        return "\n".join(report)


# Module-level convenience function

def validate_document_authenticity(
    metadata: Dict,
    text_content: str = "",
    file_path: Optional[str] = None,
) -> Dict:
    """
    Convenience function to validate document authenticity

    Args:
        metadata: Document metadata
        text_content: Full document text
        file_path: Path to document file

    Returns:
        Validation results dictionary
    """
    validator = AuthenticityValidator()
    return validator.calculate_authenticity_score(metadata, text_content, file_path)
