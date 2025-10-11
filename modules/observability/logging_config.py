"""
Centralized Logging Configuration

Provides structured logging with consistent formatting, log levels, and output handling
across all application modules. Supports both development and production environments.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pythonjsonlogger import jsonlogger


class StructuredFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds standard fields to all log records.

    Automatically includes:
    - Timestamp (ISO 8601 format)
    - Log level
    - Logger name
    - Message
    - Request context (if available)
    - Exception info (if present)
    """

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """
        Add custom fields to the log record.

        Args:
            log_record: Dictionary to be converted to JSON
            record: Original LogRecord object
            message_dict: Dictionary from the log message
        """
        super(StructuredFormatter, self).add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'

        # Add log level
        log_record['level'] = record.levelname

        # Add logger name
        log_record['logger'] = record.name

        # Add source location
        log_record['source'] = {
            'file': record.pathname,
            'line': record.lineno,
            'function': record.funcName
        }

        # Add request context if available (from RequestContext)
        from .context import get_request_context
        context = get_request_context()
        if context:
            log_record['request'] = {
                'correlation_id': context.correlation_id,
                'method': context.method,
                'path': context.path,
                'user_id': context.user_id,
                'ip_address': context.ip_address
            }

        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info) if record.exc_info else None
            }


class HumanReadableFormatter(logging.Formatter):
    """
    Human-readable formatter for development environments.

    Provides colorized output with clear structure for easy debugging.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors and structure.

        Args:
            record: Log record to format

        Returns:
            Formatted log string
        """
        # Get color for level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Build base message
        message = f"{color}{record.levelname:8}{reset} {timestamp} [{record.name}] {record.getMessage()}"

        # Add request context if available
        from .context import get_request_context
        context = get_request_context()
        if context:
            message += f" | correlation_id={context.correlation_id} path={context.path}"

        # Add exception if present
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)

        return message


def configure_logging(
    level: str = "INFO",
    format_type: str = "human",
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """
    Configure application-wide logging settings.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Output format ('human' for development, 'json' for production)
        log_file: Optional file path for log output
        enable_console: Whether to output logs to console

    Example:
        >>> # Development setup
        >>> configure_logging(level='DEBUG', format_type='human')

        >>> # Production setup
        >>> configure_logging(level='INFO', format_type='json', log_file='/var/log/app.log')
    """
    # Convert level string to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Choose formatter
    if format_type == 'json':
        formatter = StructuredFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = HumanReadableFormatter()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        # Always use JSON format for file output
        file_handler.setFormatter(StructuredFormatter('%(timestamp)s %(level)s %(name)s %(message)s'))
        root_logger.addHandler(file_handler)

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)
    logging.getLogger('google.auth').setLevel(logging.WARNING)

    # Log configuration
    root_logger.info(
        f"Logging configured - Level: {level}, Format: {format_type}, "
        f"Console: {enable_console}, File: {log_file or 'disabled'}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    This is the recommended way to get loggers throughout the application.
    It ensures consistent naming and configuration.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that adds extra context to all log messages.

    Useful for adding module-specific or operation-specific context.

    Example:
        >>> base_logger = get_logger(__name__)
        >>> logger = LoggerAdapter(base_logger, {'module': 'scraping', 'job_id': 123})
        >>> logger.info("Processing job")  # Automatically includes module and job_id
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message to add extra context.

        Args:
            msg: Log message
            kwargs: Additional keyword arguments

        Returns:
            Tuple of (message, kwargs) with extra context added
        """
        # Merge extra context
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra

        return msg, kwargs
