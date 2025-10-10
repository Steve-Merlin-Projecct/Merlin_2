"""
Document Generation Module

This module provides document generation capabilities with authenticity enhancement.
Includes template processing, smart typography, realistic metadata generation,
and authenticity verification.

Author: Automated Job Application System
Version: 2.0.0 - Authenticity Enhanced
"""

from .template_engine import TemplateEngine
from .document_generator import DocumentGenerator
from .template_converter import TemplateConverter
from .smart_typography import SmartTypography, enhance_text, get_typography_stats
from .metadata_generator import MetadataGenerator, generate_realistic_metadata
from .authenticity_validator import AuthenticityValidator, validate_document_authenticity
from .authenticity_config import get_all_config, get_authenticity_level
from .typography_constants import get_all_typography_rules

__all__ = [
    # Core classes
    'TemplateEngine',
    'DocumentGenerator',
    'TemplateConverter',

    # Authenticity enhancement classes
    'SmartTypography',
    'MetadataGenerator',
    'AuthenticityValidator',

    # Convenience functions
    'enhance_text',
    'get_typography_stats',
    'generate_realistic_metadata',
    'validate_document_authenticity',
    'get_all_config',
    'get_authenticity_level',
    'get_all_typography_rules',
]

__version__ = '2.0.0'
