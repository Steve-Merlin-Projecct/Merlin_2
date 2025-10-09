"""
Authenticity Configuration for Document Generation

This module contains configuration settings for document authenticity features
including metadata generation, typography enhancement, and verification thresholds.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
from typing import Dict, Any

# ==============================================================================
# METADATA GENERATION CONFIGURATION
# ==============================================================================

# Creation timestamp settings
CREATION_DATE_RANGE_DAYS = int(os.getenv('DOCX_CREATION_DATE_RANGE_DAYS', '30'))
"""How far back to randomize creation dates (1-30 days ago)"""

MODIFICATION_MAX_DAYS = int(os.getenv('DOCX_MODIFICATION_MAX_DAYS', '7'))
"""Maximum days between creation and modification (0-7 days)"""

# Business hours for realistic timestamps (9 AM - 6 PM)
BUSINESS_HOURS_START = int(os.getenv('DOCX_BUSINESS_HOURS_START', '9'))
"""Start of business hours for creation timestamps (default: 9 AM)"""

BUSINESS_HOURS_END = int(os.getenv('DOCX_BUSINESS_HOURS_END', '18'))
"""End of business hours for creation timestamps (default: 6 PM)"""

# Editing time simulation (minutes)
MIN_EDITING_TIME_MINUTES = int(os.getenv('DOCX_MIN_EDITING_TIME_MINUTES', '30'))
"""Minimum editing time for documents (default: 30 minutes)"""

MAX_EDITING_TIME_MINUTES = int(os.getenv('DOCX_MAX_EDITING_TIME_MINUTES', '180'))
"""Maximum editing time for documents (default: 180 minutes / 3 hours)"""

# Editing time ranges by document type
EDITING_TIME_RANGES = {
    'resume': (30, 180),      # 0.5 - 3 hours
    'coverletter': (20, 120),  # 0.3 - 2 hours
    'default': (30, 120)       # 0.5 - 2 hours
}

# Revision number ranges by document type
REVISION_RANGES = {
    'resume': (1, 3),          # 1-3 revisions
    'coverletter': (1, 3),     # 1-3 revisions
    'template': (2, 5),        # 2-5 revisions (template being populated)
    'default': (1, 3)          # 1-3 revisions
}

# ==============================================================================
# TYPOGRAPHY ENHANCEMENT CONFIGURATION
# ==============================================================================

ENABLE_SMART_QUOTES = os.getenv('DOCX_ENABLE_SMART_QUOTES', 'true').lower() == 'true'
"""Enable smart quotation marks (straight to curly)"""

ENABLE_SMART_DASHES = os.getenv('DOCX_ENABLE_SMART_DASHES', 'true').lower() == 'true'
"""Enable smart dashes (double hyphen to em dash, date ranges to en dash)"""

ENABLE_SMART_ELLIPSIS = os.getenv('DOCX_ENABLE_SMART_ELLIPSIS', 'true').lower() == 'true'
"""Enable smart ellipsis (three periods to ellipsis character)"""

ENABLE_NON_BREAKING_SPACES = os.getenv('DOCX_ENABLE_NON_BREAKING_SPACES', 'true').lower() == 'true'
"""Enable non-breaking spaces after titles, units, etc."""

ENABLE_SPECIAL_CHARACTERS = os.getenv('DOCX_ENABLE_SPECIAL_CHARACTERS', 'true').lower() == 'true'
"""Enable special character formatting (degree symbols, trademark, etc.)"""

# ==============================================================================
# VERIFICATION CONFIGURATION
# ==============================================================================

ENABLE_PRE_DELIVERY_VERIFICATION = os.getenv('DOCX_ENABLE_PRE_DELIVERY_VERIFICATION', 'true').lower() == 'true'
"""Enable authenticity verification before document delivery"""

BLOCK_ON_VERIFICATION_FAILURE = os.getenv('DOCX_BLOCK_ON_VERIFICATION_FAILURE', 'true').lower() == 'true'
"""Block document delivery if verification fails"""

VERIFICATION_TIMEOUT_SECONDS = int(os.getenv('DOCX_VERIFICATION_TIMEOUT_SECONDS', '10'))
"""Maximum time for verification process (default: 10 seconds)"""

# Authenticity score thresholds
AUTHENTICITY_SCORE_EXCELLENT = 90  # 90-100: Excellent
AUTHENTICITY_SCORE_GOOD = 75       # 75-89: Good
AUTHENTICITY_SCORE_ACCEPTABLE = 60 # 60-74: Acceptable
AUTHENTICITY_SCORE_POOR = 0        # 0-59: Poor (fails)

# Minimum score to allow delivery (if BLOCK_ON_VERIFICATION_FAILURE is True)
MINIMUM_AUTHENTICITY_SCORE = int(os.getenv('DOCX_MINIMUM_AUTHENTICITY_SCORE', '75'))
"""Minimum authenticity score to allow document delivery (default: 75)"""

# ==============================================================================
# AUTHENTICITY SCORING WEIGHTS
# ==============================================================================

AUTHENTICITY_SCORING_WEIGHTS = {
    'metadata_completeness': 25,   # All required fields populated
    'timestamp_realism': 20,       # Realistic creation/modification dates
    'editing_time': 15,            # Reasonable editing time set
    'typography_quality': 15,      # Smart quotes, dashes, etc.
    'structure_integrity': 15,     # Valid ZIP/OOXML structure
    'template_completion': 10,     # No unreplaced variables
}
"""
Scoring weights for authenticity components (total: 100)

Each component contributes to the overall authenticity score:
- metadata_completeness: Author, title, subject, keywords populated
- timestamp_realism: Creation/modification dates realistic
- editing_time: Editing time set and within acceptable range
- typography_quality: Smart typography applied
- structure_integrity: Valid document structure
- template_completion: All template variables replaced
"""

# ==============================================================================
# APPLICATION PROPERTIES
# ==============================================================================

# Microsoft Office application settings
DEFAULT_APPLICATION = "Microsoft Office Word"
DEFAULT_APP_VERSION = "16.0000"  # Office 2016/2019/365
DEFAULT_DOC_SECURITY = 0          # No protection

# File size expectations (bytes)
EXPECTED_FILE_SIZE_MIN = 20 * 1024      # 20 KB
EXPECTED_FILE_SIZE_MAX = 200 * 1024     # 200 KB
EXPECTED_FILE_SIZE_RESUME = 50 * 1024   # 50 KB typical

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_editing_time_range(document_type: str) -> tuple:
    """
    Get editing time range for document type

    Args:
        document_type: Type of document ('resume', 'coverletter', etc.)

    Returns:
        Tuple of (min_minutes, max_minutes)
    """
    return EDITING_TIME_RANGES.get(document_type.lower(), EDITING_TIME_RANGES['default'])


def get_revision_range(document_type: str) -> tuple:
    """
    Get revision number range for document type

    Args:
        document_type: Type of document ('resume', 'coverletter', 'template', etc.)

    Returns:
        Tuple of (min_revisions, max_revisions)
    """
    return REVISION_RANGES.get(document_type.lower(), REVISION_RANGES['default'])


def get_authenticity_level(score: int) -> str:
    """
    Get authenticity level description from score

    Args:
        score: Authenticity score (0-100)

    Returns:
        Level description: 'excellent', 'good', 'acceptable', or 'poor'
    """
    if score >= AUTHENTICITY_SCORE_EXCELLENT:
        return 'excellent'
    elif score >= AUTHENTICITY_SCORE_GOOD:
        return 'good'
    elif score >= AUTHENTICITY_SCORE_ACCEPTABLE:
        return 'acceptable'
    else:
        return 'poor'


def get_all_config() -> Dict[str, Any]:
    """
    Get all configuration settings as dictionary

    Returns:
        Dictionary of all configuration settings
    """
    return {
        'metadata': {
            'creation_date_range_days': CREATION_DATE_RANGE_DAYS,
            'modification_max_days': MODIFICATION_MAX_DAYS,
            'business_hours_start': BUSINESS_HOURS_START,
            'business_hours_end': BUSINESS_HOURS_END,
            'min_editing_time_minutes': MIN_EDITING_TIME_MINUTES,
            'max_editing_time_minutes': MAX_EDITING_TIME_MINUTES,
            'editing_time_ranges': EDITING_TIME_RANGES,
            'revision_ranges': REVISION_RANGES,
        },
        'typography': {
            'enable_smart_quotes': ENABLE_SMART_QUOTES,
            'enable_smart_dashes': ENABLE_SMART_DASHES,
            'enable_smart_ellipsis': ENABLE_SMART_ELLIPSIS,
            'enable_non_breaking_spaces': ENABLE_NON_BREAKING_SPACES,
            'enable_special_characters': ENABLE_SPECIAL_CHARACTERS,
        },
        'verification': {
            'enable_pre_delivery_verification': ENABLE_PRE_DELIVERY_VERIFICATION,
            'block_on_verification_failure': BLOCK_ON_VERIFICATION_FAILURE,
            'verification_timeout_seconds': VERIFICATION_TIMEOUT_SECONDS,
            'minimum_authenticity_score': MINIMUM_AUTHENTICITY_SCORE,
            'score_thresholds': {
                'excellent': AUTHENTICITY_SCORE_EXCELLENT,
                'good': AUTHENTICITY_SCORE_GOOD,
                'acceptable': AUTHENTICITY_SCORE_ACCEPTABLE,
                'poor': AUTHENTICITY_SCORE_POOR,
            },
            'scoring_weights': AUTHENTICITY_SCORING_WEIGHTS,
        },
        'application': {
            'default_application': DEFAULT_APPLICATION,
            'default_app_version': DEFAULT_APP_VERSION,
            'default_doc_security': DEFAULT_DOC_SECURITY,
        },
        'file_size': {
            'min': EXPECTED_FILE_SIZE_MIN,
            'max': EXPECTED_FILE_SIZE_MAX,
            'typical_resume': EXPECTED_FILE_SIZE_RESUME,
        }
    }
