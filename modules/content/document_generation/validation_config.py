"""
Validation Configuration - Centralized Configuration for Pre-Send Validation

This module provides centralized configuration management for the pre-send
validation system, including environment variable loading, default settings,
and configuration profiles.

Author: Automated Job Application System
Version: 1.0.0
Created: 2025-10-24
"""

import os
import json
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationSettings:
    """
    Centralized validation settings

    Provides configuration for all validation checks with sensible defaults
    and environment variable overrides.
    """

    # Default settings
    DEFAULT_ENABLE_FILE_EXISTENCE = True
    DEFAULT_ENABLE_STRUCTURE_CHECK = True
    DEFAULT_ENABLE_WORD_COMPATIBILITY = True
    DEFAULT_ENABLE_SECURITY_SCAN = True
    DEFAULT_ENABLE_VARIABLE_CHECK = True
    DEFAULT_ENABLE_FILE_SIZE_CHECK = True
    DEFAULT_MIN_FILE_SIZE_BYTES = 1000  # 1KB minimum
    DEFAULT_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB maximum
    DEFAULT_STRICT_MODE = True

    # Environment variable names
    ENV_ENABLE_FILE_EXISTENCE = "VALIDATION_FILE_EXISTENCE"
    ENV_ENABLE_STRUCTURE_CHECK = "VALIDATION_STRUCTURE_CHECK"
    ENV_ENABLE_WORD_COMPATIBILITY = "VALIDATION_WORD_COMPAT"
    ENV_ENABLE_SECURITY_SCAN = "VALIDATION_SECURITY_SCAN"
    ENV_ENABLE_VARIABLE_CHECK = "VALIDATION_VARIABLE_CHECK"
    ENV_ENABLE_FILE_SIZE_CHECK = "VALIDATION_FILE_SIZE"
    ENV_MIN_FILE_SIZE = "VALIDATION_MIN_SIZE"
    ENV_MAX_FILE_SIZE = "VALIDATION_MAX_SIZE"
    ENV_STRICT_MODE = "VALIDATION_STRICT_MODE"
    ENV_LOG_DIRECTORY = "VALIDATION_LOG_DIR"

    @classmethod
    def load_from_env(cls) -> Dict:
        """
        Load validation settings from environment variables

        Returns:
            Dictionary of validation settings
        """
        def get_bool(env_var: str, default: bool) -> bool:
            """Get boolean from environment variable"""
            value = os.getenv(env_var, str(default)).lower()
            return value in ["true", "1", "yes", "on"]

        def get_int(env_var: str, default: int) -> int:
            """Get integer from environment variable"""
            try:
                return int(os.getenv(env_var, str(default)))
            except ValueError:
                logger.warning(f"Invalid integer value for {env_var}, using default: {default}")
                return default

        settings = {
            "enable_file_existence": get_bool(cls.ENV_ENABLE_FILE_EXISTENCE, cls.DEFAULT_ENABLE_FILE_EXISTENCE),
            "enable_structure_check": get_bool(cls.ENV_ENABLE_STRUCTURE_CHECK, cls.DEFAULT_ENABLE_STRUCTURE_CHECK),
            "enable_word_compatibility": get_bool(cls.ENV_ENABLE_WORD_COMPATIBILITY, cls.DEFAULT_ENABLE_WORD_COMPATIBILITY),
            "enable_security_scan": get_bool(cls.ENV_ENABLE_SECURITY_SCAN, cls.DEFAULT_ENABLE_SECURITY_SCAN),
            "enable_variable_check": get_bool(cls.ENV_ENABLE_VARIABLE_CHECK, cls.DEFAULT_ENABLE_VARIABLE_CHECK),
            "enable_file_size_check": get_bool(cls.ENV_ENABLE_FILE_SIZE_CHECK, cls.DEFAULT_ENABLE_FILE_SIZE_CHECK),
            "min_file_size_bytes": get_int(cls.ENV_MIN_FILE_SIZE, cls.DEFAULT_MIN_FILE_SIZE_BYTES),
            "max_file_size_bytes": get_int(cls.ENV_MAX_FILE_SIZE, cls.DEFAULT_MAX_FILE_SIZE_BYTES),
            "strict_mode": get_bool(cls.ENV_STRICT_MODE, cls.DEFAULT_STRICT_MODE),
            "log_directory": os.getenv(cls.ENV_LOG_DIRECTORY, os.path.join(os.getcwd(), "storage", "validation_logs"))
        }

        logger.info(f"Validation settings loaded from environment: strict_mode={settings['strict_mode']}")
        return settings

    @classmethod
    def load_from_file(cls, config_file: str) -> Optional[Dict]:
        """
        Load validation settings from JSON configuration file

        Args:
            config_file: Path to JSON configuration file

        Returns:
            Dictionary of validation settings, or None if file not found
        """
        try:
            if not os.path.exists(config_file):
                logger.warning(f"Configuration file not found: {config_file}")
                return None

            with open(config_file, 'r') as f:
                settings = json.load(f)

            logger.info(f"Validation settings loaded from file: {config_file}")
            return settings

        except Exception as e:
            logger.error(f"Failed to load configuration file {config_file}: {str(e)}")
            return None

    @classmethod
    def get_default_settings(cls) -> Dict:
        """
        Get default validation settings

        Returns:
            Dictionary of default validation settings
        """
        return {
            "enable_file_existence": cls.DEFAULT_ENABLE_FILE_EXISTENCE,
            "enable_structure_check": cls.DEFAULT_ENABLE_STRUCTURE_CHECK,
            "enable_word_compatibility": cls.DEFAULT_ENABLE_WORD_COMPATIBILITY,
            "enable_security_scan": cls.DEFAULT_ENABLE_SECURITY_SCAN,
            "enable_variable_check": cls.DEFAULT_ENABLE_VARIABLE_CHECK,
            "enable_file_size_check": cls.DEFAULT_ENABLE_FILE_SIZE_CHECK,
            "min_file_size_bytes": cls.DEFAULT_MIN_FILE_SIZE_BYTES,
            "max_file_size_bytes": cls.DEFAULT_MAX_FILE_SIZE_BYTES,
            "strict_mode": cls.DEFAULT_STRICT_MODE,
            "log_directory": os.path.join(os.getcwd(), "storage", "validation_logs")
        }


class ValidationProfiles:
    """
    Pre-defined validation profiles for different use cases

    Profiles:
    - production: Strictest validation (all checks enabled, strict mode)
    - development: Relaxed validation (security/variables only, non-strict)
    - testing: Minimal validation (file existence only)
    - custom: User-defined configuration
    """

    @staticmethod
    def get_production_profile() -> Dict:
        """Get production validation profile (strictest)"""
        return {
            "enable_file_existence": True,
            "enable_structure_check": True,
            "enable_word_compatibility": True,
            "enable_security_scan": True,
            "enable_variable_check": True,
            "enable_file_size_check": True,
            "min_file_size_bytes": 1000,
            "max_file_size_bytes": 10 * 1024 * 1024,
            "strict_mode": True,
            "profile_name": "production"
        }

    @staticmethod
    def get_development_profile() -> Dict:
        """Get development validation profile (relaxed)"""
        return {
            "enable_file_existence": True,
            "enable_structure_check": False,  # Skip in dev
            "enable_word_compatibility": True,
            "enable_security_scan": True,
            "enable_variable_check": True,
            "enable_file_size_check": False,  # Skip in dev
            "min_file_size_bytes": 100,
            "max_file_size_bytes": 50 * 1024 * 1024,  # 50MB for dev
            "strict_mode": False,  # Allow warnings
            "profile_name": "development"
        }

    @staticmethod
    def get_testing_profile() -> Dict:
        """Get testing validation profile (minimal)"""
        return {
            "enable_file_existence": True,
            "enable_structure_check": False,
            "enable_word_compatibility": False,
            "enable_security_scan": False,
            "enable_variable_check": False,
            "enable_file_size_check": False,
            "min_file_size_bytes": 0,
            "max_file_size_bytes": 100 * 1024 * 1024,
            "strict_mode": False,
            "profile_name": "testing"
        }

    @staticmethod
    def get_security_focused_profile() -> Dict:
        """Get security-focused validation profile"""
        return {
            "enable_file_existence": True,
            "enable_structure_check": True,
            "enable_word_compatibility": True,
            "enable_security_scan": True,  # Primary focus
            "enable_variable_check": False,
            "enable_file_size_check": True,
            "min_file_size_bytes": 1000,
            "max_file_size_bytes": 10 * 1024 * 1024,
            "strict_mode": True,
            "profile_name": "security_focused"
        }

    @classmethod
    def get_profile(cls, profile_name: str) -> Dict:
        """
        Get validation profile by name

        Args:
            profile_name: Name of profile (production, development, testing, security_focused)

        Returns:
            Dictionary of validation settings for the profile
        """
        profiles = {
            "production": cls.get_production_profile,
            "development": cls.get_development_profile,
            "testing": cls.get_testing_profile,
            "security_focused": cls.get_security_focused_profile,
        }

        profile_func = profiles.get(profile_name.lower())
        if profile_func:
            return profile_func()
        else:
            logger.warning(f"Unknown profile: {profile_name}, using production profile")
            return cls.get_production_profile()


def setup_validation_logging(log_directory: Optional[str] = None) -> None:
    """
    Setup validation logging directory

    Args:
        log_directory: Directory for validation logs (uses default if not provided)
    """
    if log_directory is None:
        log_directory = os.path.join(os.getcwd(), "storage", "validation_logs")

    try:
        Path(log_directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Validation logging directory created: {log_directory}")
    except Exception as e:
        logger.error(f"Failed to create validation logging directory: {str(e)}")


def get_validation_stats(log_directory: Optional[str] = None) -> Dict:
    """
    Get validation statistics from log files

    Args:
        log_directory: Directory containing validation logs

    Returns:
        Dictionary with validation statistics
    """
    if log_directory is None:
        log_directory = os.path.join(os.getcwd(), "storage", "validation_logs")

    stats = {
        "total_validations": 0,
        "passed_validations": 0,
        "failed_validations": 0,
        "total_errors": 0,
        "total_warnings": 0,
        "validation_files": []
    }

    try:
        if not os.path.exists(log_directory):
            logger.warning(f"Validation log directory not found: {log_directory}")
            return stats

        for filename in os.listdir(log_directory):
            if filename.endswith(".json"):
                filepath = os.path.join(log_directory, filename)

                try:
                    with open(filepath, 'r') as f:
                        validation_result = json.load(f)

                    stats["total_validations"] += 1

                    if validation_result.get("safe_to_send", False):
                        stats["passed_validations"] += 1
                    else:
                        stats["failed_validations"] += 1

                    stats["total_errors"] += len(validation_result.get("errors", []))
                    stats["total_warnings"] += len(validation_result.get("warnings", []))

                    stats["validation_files"].append({
                        "filename": filename,
                        "safe_to_send": validation_result.get("safe_to_send", False),
                        "timestamp": validation_result.get("timestamp", "unknown"),
                        "document_type": validation_result.get("document_type", "unknown")
                    })

                except Exception as e:
                    logger.error(f"Failed to parse validation log {filename}: {str(e)}")

        logger.info(
            f"Validation stats: {stats['total_validations']} total, "
            f"{stats['passed_validations']} passed, {stats['failed_validations']} failed"
        )

        return stats

    except Exception as e:
        logger.error(f"Failed to get validation statistics: {str(e)}")
        return stats
