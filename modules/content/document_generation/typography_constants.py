"""
Typography Constants and Rules for Document Enhancement

This module defines all typography transformation rules for smart quotes, dashes,
ellipsis, non-breaking spaces, and special characters.

Author: Automated Job Application System
Version: 1.0.0
"""

import re
from typing import Dict, Pattern, List, Tuple

# ==============================================================================
# SMART QUOTES PATTERNS
# ==============================================================================

# Unicode characters for smart quotes
LEFT_DOUBLE_QUOTE = '\u201c'    # U+201C - "
RIGHT_DOUBLE_QUOTE = '\u201d'   # U+201D - "
LEFT_SINGLE_QUOTE = '\u2018'    # U+2018 - '
RIGHT_SINGLE_QUOTE = '\u2019'   # U+2019 - '

# Smart quote replacement rules (order matters for correct application)
# Defined directly to avoid scope issues with module-level constants
SMART_QUOTE_RULES: List[Tuple[Pattern, str]] = [
    # Opening double quote after whitespace, start of string, or opening punctuation
    (re.compile(r'(^|[\s\(\[\{<])\"'), r'\1' + LEFT_DOUBLE_QUOTE),

    # Closing double quote before whitespace, end of string, or closing punctuation
    (re.compile(r'\"([\s\.,!?\:;)\]\}>]|$)'), RIGHT_DOUBLE_QUOTE + r'\1'),

    # Opening single quote after whitespace or start
    (re.compile(r'(^|[\s\(\[\{<])\''), r'\1' + LEFT_SINGLE_QUOTE),

    # Apostrophes in contractions and possessives (must come before closing single quote)
    (re.compile(r'([a-zA-Z])\'([a-zA-Z])'), r'\1' + RIGHT_SINGLE_QUOTE + r'\2'),

    # Apostrophe at end of word (possessive)
    (re.compile(r'([a-zA-Z])\'([\s\.,!?\:;)\]\}>]|$)'), r'\1' + RIGHT_SINGLE_QUOTE + r'\2'),

    # Closing single quote
    (re.compile(r'\'([\s\.,!?\:;)\]\}>]|$)'), RIGHT_SINGLE_QUOTE + r'\1'),
]

# ==============================================================================
# SMART DASHES PATTERNS
# ==============================================================================

# Unicode characters for dashes
EM_DASH = '\u2014'  # U+2014 - — (long dash for breaks in thought)
EN_DASH = '\u2013'  # U+2013 - – (medium dash for ranges)

# Smart dash replacement rules
SMART_DASH_RULES: List[Tuple[Pattern, str]] = [
    # Number ranges with hyphen: 2020-2023 → 2020–2023 (en dash)
    (re.compile(r'(\d+)\s*-\s*(\d+)'), r'\1' + EN_DASH + r'\2'),

    # Date ranges: May-June → May–June (en dash)
    (re.compile(r'([A-Z][a-z]+)\s*-\s*([A-Z][a-z]+)'), r'\1' + EN_DASH + r'\2'),

    # Double hyphen to em dash: word--word → word—word
    (re.compile(r'(\w+)\s*--\s*(\w+)'), r'\1' + EM_DASH + r'\2'),

    # Spaced double hyphen: word -- word → word — word
    (re.compile(r'\s--\s'), ' ' + EM_DASH + ' '),
]

# ==============================================================================
# ELLIPSIS PATTERN
# ==============================================================================

# Unicode character for ellipsis
ELLIPSIS = '\u2026'  # U+2026 - …

# Ellipsis replacement rule
SMART_ELLIPSIS_PATTERN = re.compile(r'\.{3}')  # Three periods → …
SMART_ELLIPSIS_REPLACEMENT = ELLIPSIS

# ==============================================================================
# NON-BREAKING SPACE
# ==============================================================================

# Unicode non-breaking space
NON_BREAKING_SPACE = '\u00A0'  # U+00A0

# Titles that should be followed by non-breaking space
TITLES = [
    'Dr', 'Mr', 'Mrs', 'Ms', 'Miss', 'Prof', 'Rev', 'Hon',
    'Sr', 'Jr', 'Esq', 'PhD', 'MD', 'DDS', 'DMD', 'DO'
]

# Non-breaking space replacement rules
# Build the list dynamically for titles, then add other patterns
_nbsp_rules: List[Tuple[Pattern, str]] = []

# After titles: Dr. Smith → Dr. Smith (with nbsp)
for title in TITLES:
    _nbsp_rules.append((re.compile(r'\b' + re.escape(title) + r'\.\s+'),
                        title + '.' + NON_BREAKING_SPACE))

# Between initials: J. Smith → J. Smith (with nbsp)
_nbsp_rules.append((re.compile(r'\b([A-Z])\.\s+([A-Z])'), r'\1.' + NON_BREAKING_SPACE + r'\2'))

# Before units: 10 MB → 10 MB (with nbsp)
_nbsp_rules.append((re.compile(r'(\d+)\s+(KB|MB|GB|TB|km|cm|mm|kg|g|mg)'),
                    r'\1' + NON_BREAKING_SPACE + r'\2'))

# Between number and percent: 50 % → 50% (with nbsp)
_nbsp_rules.append((re.compile(r'(\d+)\s+%'), r'\1' + NON_BREAKING_SPACE + '%'))

NON_BREAKING_SPACE_RULES: List[Tuple[Pattern, str]] = _nbsp_rules

# ==============================================================================
# SPECIAL CHARACTERS
# ==============================================================================

# Special character replacements (pattern -> replacement)
SPECIAL_CHARACTERS = {
    # Degree symbols
    r' degrees\b': '°',
    r'\bdegrees\b': '°',

    # Multiplication
    r'\b(\d+)\s*x\s*(\d+)\b': r'\1×\2',  # 10 x 20 → 10×20

    # Trademark
    r'\(TM\)': '™',
    r'\(tm\)': '™',

    # Registered trademark
    r'\(R\)': '®',
    r'\(r\)': '®',

    # Copyright
    r'\(C\)': '©',
    r'\(c\)': '©',

    # Fractions (common ones) - with word boundaries
    r'\b1/2\b': '½',
    r'\b1/4\b': '¼',
    r'\b3/4\b': '¾',
    r'\b1/3\b': '⅓',
    r'\b2/3\b': '⅔',
}

# Special character replacement rules (compile patterns from dictionary)
SPECIAL_CHARACTER_RULES: List[Tuple[Pattern, str]] = [
    (re.compile(pattern), replacement)
    for pattern, replacement in SPECIAL_CHARACTERS.items()
]

# ==============================================================================
# ACRONYM PATTERNS
# ==============================================================================

# Common acronyms that should be in small caps (optional future feature)
COMMON_ACRONYMS = [
    'ATS', 'PDF', 'CEO', 'CTO', 'CFO', 'COO', 'CIO', 'CMO',
    'VP', 'SVP', 'EVP', 'MBA', 'BA', 'BS', 'MS', 'PhD',
    'USA', 'US', 'UK', 'EU', 'UN', 'NASA', 'FBI', 'CIA',
    'IT', 'HR', 'PR', 'QA', 'UI', 'UX', 'API', 'SDK',
    'SQL', 'HTML', 'CSS', 'XML', 'JSON', 'REST', 'HTTP', 'HTTPS'
]

# ==============================================================================
# PUBLICATION NAMES (for italics)
# ==============================================================================

# Pattern for publication names (from template_engine.py)
PUBLICATION_PATTERN = re.compile(
    r'\b(?:[A-Z][a-z]*(?:\s[A-Z][a-z]*)*\s'
    r'(?:Journal|Magazine|Review|Times|Post|Herald|Tribune|Gazette|Chronicle|'
    r'News|Weekly|Monthly|Quarterly|Report|Bulletin|Digest|Today|Business|'
    r'Financial|Economic|Scientific|Academic|Medical|Legal|Technical|'
    r'International|National|Global|Daily|Press|Media|Communications?|'
    r'Technology|Science|Nature|Cell|PLOS|BMJ|NEJM|JAMA|IEEE|ACM|'
    r'Harvard|Stanford|MIT|Oxford|Cambridge))\b'
)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_all_typography_rules() -> Dict[str, any]:
    """
    Get all typography rules as a dictionary

    Returns:
        Dictionary containing all typography transformation rules
    """
    return {
        'smart_quotes': {
            'rules': SMART_QUOTE_RULES,
            'characters': {
                'left_double': LEFT_DOUBLE_QUOTE,
                'right_double': RIGHT_DOUBLE_QUOTE,
                'left_single': LEFT_SINGLE_QUOTE,
                'right_single': RIGHT_SINGLE_QUOTE,
            }
        },
        'smart_dashes': {
            'rules': SMART_DASH_RULES,
            'characters': {
                'em_dash': EM_DASH,
                'en_dash': EN_DASH,
            }
        },
        'ellipsis': {
            'pattern': SMART_ELLIPSIS_PATTERN,
            'replacement': SMART_ELLIPSIS_REPLACEMENT,
            'character': ELLIPSIS,
        },
        'non_breaking_spaces': {
            'rules': NON_BREAKING_SPACE_RULES,
            'character': NON_BREAKING_SPACE,
            'titles': TITLES,
        },
        'special_characters': {
            'rules': SPECIAL_CHARACTER_RULES,
        },
        'publications': {
            'pattern': PUBLICATION_PATTERN,
        }
    }


def is_smart_quote(char: str) -> bool:
    """Check if character is a smart quote"""
    return char in (LEFT_DOUBLE_QUOTE, RIGHT_DOUBLE_QUOTE, LEFT_SINGLE_QUOTE, RIGHT_SINGLE_QUOTE)


def is_smart_dash(char: str) -> bool:
    """Check if character is a smart dash"""
    return char in (EM_DASH, EN_DASH)


def is_smart_ellipsis(char: str) -> bool:
    """Check if character is smart ellipsis"""
    return char == ELLIPSIS


def count_smart_typography(text: str) -> Dict[str, int]:
    """
    Count smart typography characters in text

    Args:
        text: Text to analyze

    Returns:
        Dictionary with counts of each smart typography type
    """
    return {
        'smart_quotes': sum(1 for c in text if is_smart_quote(c)),
        'smart_dashes': sum(1 for c in text if is_smart_dash(c)),
        'smart_ellipsis': text.count(ELLIPSIS),
        'non_breaking_spaces': text.count(NON_BREAKING_SPACE),
    }
