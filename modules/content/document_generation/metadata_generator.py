"""
Metadata Generation for Authentic Document Properties

This module generates realistic document metadata including timestamps, editing times,
revision numbers, and document statistics to make generated documents appear
authentically created by humans rather than machines.

Author: Automated Job Application System
Version: 1.0.0
"""

import random
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

from .authenticity_config import (
    CREATION_DATE_RANGE_DAYS,
    MODIFICATION_MAX_DAYS,
    BUSINESS_HOURS_START,
    BUSINESS_HOURS_END,
    get_editing_time_range,
    get_revision_range,
    DEFAULT_APPLICATION,
    DEFAULT_APP_VERSION,
    DEFAULT_DOC_SECURITY,
)

logger = logging.getLogger(__name__)


class MetadataGenerator:
    """
    Generates realistic document metadata for authenticity

    This class creates timestamps, editing times, revision numbers, and other
    metadata that makes generated documents indistinguishable from manually
    created professional documents.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize Metadata Generator

        Args:
            seed: Optional random seed for reproducible metadata generation
        """
        if seed is not None:
            random.seed(seed)

        logger.info("MetadataGenerator initialized")

    def generate_creation_timestamp(self, base_date: Optional[datetime] = None) -> datetime:
        """
        Generate realistic creation timestamp

        Creates a timestamp that appears authentic:
        - Random date 1-30 days ago (or relative to base_date)
        - During business hours (9 AM - 6 PM)
        - Only on weekdays (Monday-Friday)
        - Random minute and second (not always on the hour)

        Args:
            base_date: Optional base date to calculate from (defaults to now)

        Returns:
            datetime: Realistic creation timestamp

        Examples:
            >>> mg = MetadataGenerator()
            >>> created = mg.generate_creation_timestamp()
            >>> # Returns something like: 2025-09-23 14:37:42
        """
        if base_date is None:
            base_date = datetime.now()

        # Random number of days ago (1-30)
        days_ago = random.randint(1, CREATION_DATE_RANGE_DAYS)

        # Start with that many days ago
        target_date = base_date - timedelta(days=days_ago)

        # Ensure it's a weekday (Monday=0 to Friday=4)
        while target_date.weekday() > 4:  # Saturday=5, Sunday=6
            days_ago += 1
            target_date = base_date - timedelta(days=days_ago)

        # Random hour during business hours
        hour = random.randint(BUSINESS_HOURS_START, BUSINESS_HOURS_END - 1)

        # Random minute and second (not always :00:00)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        timestamp = target_date.replace(
            hour=hour,
            minute=minute,
            second=second,
            microsecond=0
        )

        logger.debug(f"Generated creation timestamp: {timestamp}")
        return timestamp

    def generate_modification_timestamp(
        self,
        creation_date: datetime,
        max_days_after: int = MODIFICATION_MAX_DAYS
    ) -> datetime:
        """
        Generate realistic modification timestamp

        Creates a modification timestamp that:
        - Is 0-7 days after creation date
        - Has different time than creation (simulates editing session)
        - Is during business hours
        - Is on a weekday

        Args:
            creation_date: Document creation timestamp
            max_days_after: Maximum days after creation (default: 7)

        Returns:
            datetime: Realistic modification timestamp

        Examples:
            >>> mg = MetadataGenerator()
            >>> created = datetime(2025, 9, 23, 14, 30, 0)
            >>> modified = mg.generate_modification_timestamp(created)
            >>> # Returns something like: 2025-09-24 10:15:23
        """
        # Random days after creation (0-7)
        days_after = random.randint(0, max_days_after)

        # Start with creation date + days
        mod_date = creation_date + timedelta(days=days_after)

        # Ensure it's a weekday
        while mod_date.weekday() > 4:
            days_after += 1
            mod_date = creation_date + timedelta(days=days_after)

        # Random hour during business hours
        hour = random.randint(BUSINESS_HOURS_START, BUSINESS_HOURS_END - 1)

        # If same day, ensure different hour
        if days_after == 0:
            while hour == creation_date.hour:
                hour = random.randint(BUSINESS_HOURS_START, BUSINESS_HOURS_END - 1)

        # Random minute and second
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        timestamp = mod_date.replace(
            hour=hour,
            minute=minute,
            second=second,
            microsecond=0
        )

        logger.debug(f"Generated modification timestamp: {timestamp} (creation: {creation_date})")
        return timestamp

    def generate_editing_time(self, document_type: str = "resume") -> int:
        """
        Generate realistic editing time in minutes

        Different document types have different expected editing times:
        - Resume: 30-180 minutes (0.5-3 hours)
        - Cover letter: 20-120 minutes (0.3-2 hours)
        - Default: 30-120 minutes

        Args:
            document_type: Type of document ('resume', 'coverletter', etc.)

        Returns:
            int: Editing time in minutes

        Examples:
            >>> mg = MetadataGenerator()
            >>> time = mg.generate_editing_time('resume')
            >>> # Returns something like: 127 minutes
        """
        min_time, max_time = get_editing_time_range(document_type)
        editing_time = random.randint(min_time, max_time)

        logger.debug(f"Generated editing time for {document_type}: {editing_time} minutes")
        return editing_time

    def generate_revision_number(self, document_type: str = "resume") -> int:
        """
        Generate realistic revision number

        Different document types have different typical revision counts:
        - Resume: 1-3 revisions
        - Cover letter: 1-3 revisions
        - Template: 2-5 revisions
        - Default: 1-3 revisions

        Args:
            document_type: Type of document ('resume', 'coverletter', 'template')

        Returns:
            int: Revision number

        Examples:
            >>> mg = MetadataGenerator()
            >>> revision = mg.generate_revision_number('resume')
            >>> # Returns something like: 2
        """
        min_rev, max_rev = get_revision_range(document_type)
        revision = random.randint(min_rev, max_rev)

        logger.debug(f"Generated revision number for {document_type}: {revision}")
        return revision

    def calculate_document_statistics(self, text_content: str) -> Dict[str, int]:
        """
        Calculate document statistics from content

        Computes:
        - Word count
        - Character count (with and without spaces)
        - Paragraph count (from newlines)
        - Line count (estimated)

        Args:
            text_content: Full document text content

        Returns:
            Dictionary with document statistics

        Examples:
            >>> mg = MetadataGenerator()
            >>> stats = mg.calculate_document_statistics("Hello world. This is a test.")
            >>> print(stats['words'])
            6
        """
        if not text_content:
            return {
                'words': 0,
                'characters': 0,
                'characters_with_spaces': 0,
                'paragraphs': 0,
                'lines': 0,
            }

        # Word count (split by whitespace)
        words = len(text_content.split())

        # Character counts
        characters = len(text_content.replace(' ', '').replace('\n', ''))
        characters_with_spaces = len(text_content.replace('\n', ''))

        # Paragraph count (split by double newlines or single newlines)
        paragraphs = len([p for p in text_content.split('\n') if p.strip()])

        # Estimated line count (assume ~12 words per line)
        lines = max(1, words // 12)

        return {
            'words': words,
            'characters': characters,
            'characters_with_spaces': characters_with_spaces,
            'paragraphs': paragraphs,
            'lines': lines,
        }

    def generate_complete_metadata(
        self,
        document_type: str = "resume",
        author_name: str = "",
        document_title: str = "",
        subject: str = "",
        keywords: str = "",
        base_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Generate complete metadata package for a document

        Creates all metadata fields needed for authentic document properties:
        - Creation and modification timestamps
        - Editing time
        - Revision number
        - Application properties
        - Core properties

        Args:
            document_type: Type of document ('resume', 'coverletter', etc.)
            author_name: Document author name
            document_title: Document title
            subject: Document subject
            keywords: Document keywords
            base_date: Optional base date for timestamp generation

        Returns:
            Dictionary with complete metadata

        Examples:
            >>> mg = MetadataGenerator()
            >>> metadata = mg.generate_complete_metadata(
            ...     document_type='resume',
            ...     author_name='John Doe',
            ...     document_title='John Doe Resume'
            ... )
            >>> print(metadata['core_properties']['created'])
            2025-09-23 14:37:42
        """
        # Generate timestamps
        created = self.generate_creation_timestamp(base_date)
        modified = self.generate_modification_timestamp(created)

        # Generate editing time and revision
        editing_time = self.generate_editing_time(document_type)
        revision = self.generate_revision_number(document_type)

        # Build complete metadata package
        metadata = {
            'core_properties': {
                'title': document_title,
                'author': author_name,
                'subject': subject,
                'keywords': keywords,
                'comments': f"Professional {document_type} document",
                'category': "Job Application",
                'language': "en-CA",
                'created': created,
                'modified': modified,
                'last_modified_by': author_name,
                'revision': revision,
            },
            'app_properties': {
                'application': DEFAULT_APPLICATION,
                'app_version': DEFAULT_APP_VERSION,
                'doc_security': DEFAULT_DOC_SECURITY,
                'total_time': editing_time,  # In minutes
            },
            'generation_info': {
                'generation_method': 'enhanced_metadata',
                'document_type': document_type,
                'authenticity_enhanced': True,
                'timestamp_generated': datetime.now().isoformat(),
            }
        }

        logger.info(
            f"Generated complete metadata for {document_type}: "
            f"created={created.strftime('%Y-%m-%d %H:%M')}, "
            f"editing_time={editing_time}min, revision={revision}"
        )

        return metadata

    def generate_metadata_for_doc_object(
        self,
        doc,
        document_type: str = "resume",
        author_name: str = "",
        document_title: str = "",
        subject: str = "",
        keywords: str = "",
    ) -> Dict:
        """
        Generate metadata and apply directly to python-docx Document object

        This method generates complete metadata and sets it on the document's
        core_properties object.

        Args:
            doc: python-docx Document object
            document_type: Type of document
            author_name: Author name
            document_title: Document title
            subject: Document subject
            keywords: Keywords

        Returns:
            Dictionary with generated metadata (for tracking/logging)
        """
        # Generate complete metadata
        metadata = self.generate_complete_metadata(
            document_type=document_type,
            author_name=author_name,
            document_title=document_title,
            subject=subject,
            keywords=keywords,
        )

        # Apply core properties
        core_props = doc.core_properties
        core_props.title = metadata['core_properties']['title']
        core_props.author = metadata['core_properties']['author']
        core_props.subject = metadata['core_properties']['subject']
        core_props.keywords = metadata['core_properties']['keywords']
        core_props.comments = metadata['core_properties']['comments']
        core_props.category = metadata['core_properties']['category']
        core_props.language = metadata['core_properties']['language']
        core_props.created = metadata['core_properties']['created']
        core_props.modified = metadata['core_properties']['modified']
        core_props.last_modified_by = metadata['core_properties']['last_modified_by']
        core_props.revision = metadata['core_properties']['revision']

        logger.info(f"Applied metadata to document object for {document_type}")

        return metadata

    def get_timestamp_realism_score(self, created: datetime, modified: datetime) -> int:
        """
        Calculate timestamp realism score (0-100)

        Evaluates timestamp authenticity based on:
        - Realistic creation date (not too old, not future)
        - Modification after creation
        - Business hours
        - Weekday

        Args:
            created: Creation timestamp
            modified: Modification timestamp

        Returns:
            Score from 0-100
        """
        score = 0
        now = datetime.now()

        # Creation date reasonable (1-90 days ago): 30 points
        days_old = (now - created).days
        if 1 <= days_old <= 90:
            score += 30

        # Modified after created: 25 points
        if modified >= created:
            score += 25

        # Creation during business hours: 20 points
        if BUSINESS_HOURS_START <= created.hour < BUSINESS_HOURS_END:
            score += 20

        # Creation on weekday: 15 points
        if created.weekday() < 5:
            score += 15

        # Modified on different day or hour: 10 points
        if modified.date() != created.date() or modified.hour != created.hour:
            score += 10

        return min(score, 100)


# Module-level convenience functions

def generate_realistic_metadata(
    document_type: str = "resume",
    author_name: str = "",
    **kwargs
) -> Dict:
    """
    Convenience function to generate realistic metadata

    Args:
        document_type: Type of document
        author_name: Author name
        **kwargs: Additional metadata fields

    Returns:
        Complete metadata dictionary
    """
    generator = MetadataGenerator()
    return generator.generate_complete_metadata(
        document_type=document_type,
        author_name=author_name,
        **kwargs
    )
