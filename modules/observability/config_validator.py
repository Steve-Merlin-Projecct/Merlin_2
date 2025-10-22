"""
Configuration Validator for Observability System

Validates logging and monitoring configuration at application startup to catch
configuration errors early and provide clear error messages.

Checks:
- LOG_LEVEL is valid
- LOG_FORMAT is supported
- LOG_FILE directory exists and is writable
- Log directory has sufficient disk space
- Required environment variables are set
- Configuration values are within acceptable ranges
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class ConfigurationError(Exception):
    """
    Raised when configuration validation fails.

    Provides clear error messages to help diagnose configuration issues.
    """
    pass


class ConfigValidator:
    """
    Validates observability system configuration.

    Performs comprehensive checks at startup to ensure the logging and
    monitoring system is properly configured.

    Example:
        >>> validator = ConfigValidator()
        >>> validator.validate_all()  # Raises ConfigurationError if invalid
    """

    # Valid log levels
    VALID_LOG_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}

    # Valid log formats
    VALID_LOG_FORMATS = {'json', 'human'}

    # Minimum required disk space in bytes (100MB default)
    MIN_DISK_SPACE_MB = 100
    MIN_DISK_SPACE_BYTES = MIN_DISK_SPACE_MB * 1024 * 1024

    # Warning threshold for disk space (500MB)
    WARN_DISK_SPACE_MB = 500
    WARN_DISK_SPACE_BYTES = WARN_DISK_SPACE_MB * 1024 * 1024

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize configuration validator.

        Args:
            logger: Logger instance for validation messages (optional)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def validate_log_level(self, log_level: Optional[str] = None) -> str:
        """
        Validate LOG_LEVEL configuration.

        Args:
            log_level: Log level to validate (reads from env if None)

        Returns:
            Validated log level (uppercase)

        Raises:
            ConfigurationError: If log level is invalid

        Example:
            >>> validator.validate_log_level('info')
            'INFO'
        """
        level = (log_level or os.environ.get('LOG_LEVEL', 'INFO')).upper()

        if level not in self.VALID_LOG_LEVELS:
            raise ConfigurationError(
                f"Invalid LOG_LEVEL: '{level}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_LOG_LEVELS))}"
            )

        return level

    def validate_log_format(self, log_format: Optional[str] = None) -> str:
        """
        Validate LOG_FORMAT configuration.

        Args:
            log_format: Log format to validate (reads from env if None)

        Returns:
            Validated log format (lowercase)

        Raises:
            ConfigurationError: If log format is invalid

        Example:
            >>> validator.validate_log_format('JSON')
            'json'
        """
        format_type = (log_format or os.environ.get('LOG_FORMAT', 'human')).lower()

        if format_type not in self.VALID_LOG_FORMATS:
            raise ConfigurationError(
                f"Invalid LOG_FORMAT: '{format_type}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_LOG_FORMATS))}"
            )

        return format_type

    def validate_log_directory(self, log_dir: Optional[str] = None) -> Path:
        """
        Validate log directory exists and is writable.

        Creates directory if it doesn't exist. Checks write permissions.

        Args:
            log_dir: Log directory path to validate (reads from env if None)

        Returns:
            Path object for validated directory

        Raises:
            ConfigurationError: If directory cannot be created or is not writable

        Example:
            >>> path = validator.validate_log_directory('./logs')
            >>> print(path.exists())
            True
        """
        # Determine log directory
        if log_dir is None:
            log_file = os.environ.get('LOG_FILE')
            if log_file:
                log_dir = os.path.dirname(log_file) or './logs'
            else:
                log_dir = os.environ.get('LOG_DIR', './logs')

        log_path = Path(log_dir).resolve()

        # Try to create directory if it doesn't exist
        try:
            log_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConfigurationError(
                f"Cannot create log directory '{log_path}': {str(e)}"
            )

        # Check if directory exists
        if not log_path.exists():
            raise ConfigurationError(
                f"Log directory does not exist: '{log_path}'"
            )

        # Check if it's actually a directory
        if not log_path.is_dir():
            raise ConfigurationError(
                f"Log path is not a directory: '{log_path}'"
            )

        # Check write permissions
        if not os.access(log_path, os.W_OK):
            raise ConfigurationError(
                f"Log directory is not writable: '{log_path}'"
            )

        return log_path

    def validate_disk_space(self, log_dir: Optional[str] = None) -> Tuple[int, float]:
        """
        Validate sufficient disk space is available.

        Args:
            log_dir: Log directory to check (uses default if None)

        Returns:
            Tuple of (free_bytes, free_percent)

        Raises:
            ConfigurationError: If insufficient disk space

        Example:
            >>> free_bytes, free_pct = validator.validate_disk_space('./logs')
            >>> print(f"{free_bytes / 1024 / 1024:.1f}MB free ({free_pct:.1f}%)")
        """
        try:
            import shutil
        except ImportError:
            self.warnings.append("Cannot check disk space - shutil not available")
            return 0, 0.0

        # Get log directory path
        if log_dir is None:
            try:
                log_path = self.validate_log_directory()
            except ConfigurationError:
                # If directory doesn't exist yet, check parent or current directory
                log_path = Path('./logs').parent.resolve()
        else:
            log_path = Path(log_dir).resolve()

        # Get disk usage
        try:
            stat = shutil.disk_usage(log_path)
            free_bytes = stat.free
            free_percent = (stat.free / stat.total * 100) if stat.total > 0 else 0

            # Check critical threshold
            if free_bytes < self.MIN_DISK_SPACE_BYTES:
                raise ConfigurationError(
                    f"Insufficient disk space in '{log_path}'. "
                    f"Available: {free_bytes / 1024 / 1024:.1f}MB, "
                    f"Required: {self.MIN_DISK_SPACE_MB}MB"
                )

            # Check warning threshold
            if free_bytes < self.WARN_DISK_SPACE_BYTES:
                self.warnings.append(
                    f"Low disk space in '{log_path}': "
                    f"{free_bytes / 1024 / 1024:.1f}MB free "
                    f"({free_percent:.1f}%)"
                )

            return free_bytes, free_percent

        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            self.warnings.append(f"Cannot check disk space: {str(e)}")
            return 0, 0.0

    def validate_api_key(self, required: bool = True) -> Optional[str]:
        """
        Validate API key configuration for monitoring endpoints.

        Args:
            required: Whether API key is required (default: True)

        Returns:
            API key value or None if not required

        Raises:
            ConfigurationError: If API key is required but not set

        Example:
            >>> api_key = validator.validate_api_key(required=True)
        """
        api_key = os.environ.get('MONITORING_API_KEY') or os.environ.get('WEBHOOK_API_KEY')

        if required and not api_key:
            # Check if in dev mode
            dev_mode = os.environ.get('MONITORING_DEV_MODE', 'false').lower() == 'true'

            if not dev_mode:
                raise ConfigurationError(
                    "MONITORING_API_KEY or WEBHOOK_API_KEY environment variable is required. "
                    "Set one of these or enable MONITORING_DEV_MODE=true for development."
                )
            else:
                self.warnings.append(
                    "MONITORING_DEV_MODE is enabled - API authentication is bypassed. "
                    "Do not use in production!"
                )

        return api_key

    def validate_rotation_settings(
        self,
        max_bytes: Optional[int] = None,
        backup_count: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        Validate log rotation settings.

        Args:
            max_bytes: Maximum log file size in bytes (reads from env if None)
            backup_count: Number of backup files (reads from env if None)

        Returns:
            Tuple of (max_bytes, backup_count)

        Raises:
            ConfigurationError: If settings are invalid

        Example:
            >>> max_bytes, backup_count = validator.validate_rotation_settings()
        """
        # Get values from environment or use defaults
        if max_bytes is None:
            max_bytes = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))

        if backup_count is None:
            backup_count = int(os.environ.get('LOG_BACKUP_COUNT', 5))

        # Validate max_bytes
        MIN_MAX_BYTES = 1024 * 1024  # 1MB minimum
        MAX_MAX_BYTES = 1024 * 1024 * 1024  # 1GB maximum

        if max_bytes < MIN_MAX_BYTES:
            raise ConfigurationError(
                f"LOG_MAX_BYTES too small: {max_bytes}. "
                f"Minimum: {MIN_MAX_BYTES} (1MB)"
            )

        if max_bytes > MAX_MAX_BYTES:
            self.warnings.append(
                f"LOG_MAX_BYTES is very large: {max_bytes / 1024 / 1024:.1f}MB. "
                f"Consider using a smaller value for better rotation."
            )

        # Validate backup_count
        if backup_count < 0:
            raise ConfigurationError(
                f"LOG_BACKUP_COUNT must be non-negative: {backup_count}"
            )

        if backup_count > 100:
            self.warnings.append(
                f"LOG_BACKUP_COUNT is very high: {backup_count}. "
                f"This may consume significant disk space."
            )

        return max_bytes, backup_count

    def validate_all(
        self,
        require_api_key: bool = True,
        check_disk_space: bool = True
    ) -> Dict[str, any]:
        """
        Run all validation checks.

        Args:
            require_api_key: Whether to require API key configuration
            check_disk_space: Whether to check disk space

        Returns:
            Dictionary with validation results

        Raises:
            ConfigurationError: If any validation fails

        Example:
            >>> validator = ConfigValidator()
            >>> results = validator.validate_all()
            >>> print(f"Validation passed with {len(results['warnings'])} warnings")
        """
        # Clear previous results
        self.warnings.clear()
        self.errors.clear()

        results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'config': {}
        }

        try:
            # Validate log level
            results['config']['log_level'] = self.validate_log_level()

            # Validate log format
            results['config']['log_format'] = self.validate_log_format()

            # Validate log directory
            log_path = self.validate_log_directory()
            results['config']['log_directory'] = str(log_path)

            # Validate rotation settings
            max_bytes, backup_count = self.validate_rotation_settings()
            results['config']['max_bytes'] = max_bytes
            results['config']['backup_count'] = backup_count

            # Validate disk space
            if check_disk_space:
                free_bytes, free_percent = self.validate_disk_space(str(log_path))
                results['config']['disk_free_bytes'] = free_bytes
                results['config']['disk_free_percent'] = round(free_percent, 2)

            # Validate API key
            if require_api_key:
                api_key = self.validate_api_key(required=True)
                results['config']['api_key_configured'] = bool(api_key)

            # Collect warnings
            results['warnings'] = self.warnings.copy()

            # Log success
            if self.logger:
                self.logger.info(
                    f"Configuration validation passed - "
                    f"Level: {results['config']['log_level']}, "
                    f"Format: {results['config']['log_format']}, "
                    f"Directory: {results['config']['log_directory']}"
                )

                if results['warnings']:
                    for warning in results['warnings']:
                        self.logger.warning(f"Configuration warning: {warning}")

            return results

        except ConfigurationError as e:
            results['valid'] = False
            results['errors'].append(str(e))
            results['warnings'] = self.warnings.copy()

            if self.logger:
                self.logger.error(f"Configuration validation failed: {str(e)}")

            raise


def validate_configuration(
    require_api_key: bool = True,
    check_disk_space: bool = True,
    logger: Optional[logging.Logger] = None
) -> Dict[str, any]:
    """
    Convenience function to validate all configuration.

    Args:
        require_api_key: Whether to require API key configuration
        check_disk_space: Whether to check disk space
        logger: Logger instance for validation messages

    Returns:
        Dictionary with validation results

    Raises:
        ConfigurationError: If validation fails

    Example:
        >>> from modules.observability.config_validator import validate_configuration
        >>> results = validate_configuration()
        >>> print("Configuration is valid!")
    """
    validator = ConfigValidator(logger=logger)
    return validator.validate_all(
        require_api_key=require_api_key,
        check_disk_space=check_disk_space
    )
