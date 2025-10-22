"""
Centralized Logging Configuration

Provides structured logging with consistent formatting, log levels, and output handling
across all application modules. Supports both development and production environments.

Features:
- Async logging with QueueHandler for non-blocking I/O
- Rotating file handlers for automatic log rotation
- JSON structured logging for production
- Human-readable colored output for development
- PII scrubbing for sensitive data protection
- Separate error log files
- Automatic old log cleanup
- Graceful shutdown handling
"""

import logging
import logging.handlers
import sys
import json
import os
import atexit
from datetime import datetime
from typing import Optional, Dict, Any
from queue import Queue
from pythonjsonlogger import jsonlogger

# Import PII scrubber
from .pii_scrubber import PIIScrubbingFilter, PIIScrubber


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


# Global queue listener for async logging
_queue_listener = None
_log_queue = None


def configure_logging(
    level: str = "INFO",
    format_type: str = "human",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    log_dir: Optional[str] = None,
    enable_file_rotation: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB default
    backup_count: int = 5,
    enable_async_logging: bool = True,
    enable_pii_scrubbing: bool = True,
    queue_size: int = 10000
) -> None:
    """
    Configure application-wide logging settings with rotating file handlers.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Output format ('human' for development, 'json' for production)
        log_file: Optional file path for log output (deprecated, use log_dir instead)
        enable_console: Whether to output logs to console
        log_dir: Directory for log files (default: './logs')
        enable_file_rotation: Enable rotating file handlers
        max_bytes: Maximum size of each log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        enable_async_logging: Use async logging with QueueHandler (default: True)
        enable_pii_scrubbing: Enable PII scrubbing filter (default: True)
        queue_size: Maximum queue size for async logging (default: 10000)

    Example:
        >>> # Development setup
        >>> configure_logging(level='DEBUG', format_type='human')

        >>> # Production setup with rotation and async logging
        >>> configure_logging(
        ...     level='INFO',
        ...     format_type='json',
        ...     log_dir='/var/log/merlin',
        ...     max_bytes=50*1024*1024,  # 50MB
        ...     backup_count=10,
        ...     enable_async_logging=True,
        ...     enable_pii_scrubbing=True
        ... )
    """
    global _queue_listener, _log_queue
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

    # Create PII scrubber if enabled
    pii_filter = None
    if enable_pii_scrubbing:
        pii_filter = PIIScrubbingFilter()

    # List of handlers for async logging
    handlers_list = []

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        if pii_filter:
            console_handler.addFilter(pii_filter)
        handlers_list.append(console_handler)

    # Determine log directory
    if log_dir:
        log_directory = log_dir
    elif log_file:
        # Extract directory from log_file for backward compatibility
        log_directory = os.path.dirname(log_file) or './logs'
    else:
        log_directory = './logs'

    # Create log directory if it doesn't exist
    os.makedirs(log_directory, exist_ok=True)

    # File handlers with rotation
    if enable_file_rotation:
        # Main application log (all levels)
        app_log_path = os.path.join(log_directory, 'app.log')
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        app_handler.setLevel(log_level)
        # Always use JSON format for file output
        app_handler.setFormatter(StructuredFormatter('%(timestamp)s %(level)s %(name)s %(message)s'))
        if pii_filter:
            app_handler.addFilter(pii_filter)
        handlers_list.append(app_handler)

        # Error log (ERROR and above only)
        error_log_path = os.path.join(log_directory, 'error.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter('%(timestamp)s %(level)s %(name)s %(message)s'))
        if pii_filter:
            error_handler.addFilter(pii_filter)
        handlers_list.append(error_handler)

    elif log_file:
        # Legacy single file handler (no rotation)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(StructuredFormatter('%(timestamp)s %(level)s %(name)s %(message)s'))
        if pii_filter:
            file_handler.addFilter(pii_filter)
        handlers_list.append(file_handler)

    # Setup async logging with QueueHandler if enabled
    if enable_async_logging and handlers_list:
        # Create queue with max size to prevent memory issues
        _log_queue = Queue(maxsize=queue_size)

        # Create QueueHandler for root logger
        queue_handler = logging.handlers.QueueHandler(_log_queue)
        queue_handler.setLevel(log_level)
        root_logger.addHandler(queue_handler)

        # Create QueueListener with actual handlers
        # QueueListener runs in separate thread and does I/O
        _queue_listener = logging.handlers.QueueListener(
            _log_queue,
            *handlers_list,
            respect_handler_level=True
        )

        # Start the listener
        _queue_listener.start()

        # Register shutdown handler
        atexit.register(shutdown_logging)

    else:
        # Direct handlers (synchronous logging)
        for handler in handlers_list:
            root_logger.addHandler(handler)

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)
    logging.getLogger('google.auth').setLevel(logging.WARNING)

    # Validate configuration if config_validator is available
    try:
        from .config_validator import validate_configuration
        validate_configuration(require_api_key=False, check_disk_space=True, logger=root_logger)
    except Exception as e:
        root_logger.warning(f"Configuration validation skipped: {e}")

    # Log configuration
    root_logger.info(
        f"Logging configured - Level: {level}, Format: {format_type}, "
        f"Console: {enable_console}, Log Dir: {log_directory if enable_file_rotation else 'N/A'}, "
        f"Rotation: {enable_file_rotation}, Max Size: {max_bytes / 1024 / 1024:.1f}MB, "
        f"Backups: {backup_count}, Async: {enable_async_logging}, PII Scrubbing: {enable_pii_scrubbing}"
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


def shutdown_logging():
    """
    Gracefully shutdown async logging system.

    Stops the queue listener and ensures all pending log records are flushed.
    This function is automatically registered with atexit when async logging is enabled.

    Example:
        >>> shutdown_logging()  # Manually shutdown (usually automatic via atexit)
    """
    global _queue_listener, _log_queue

    if _queue_listener is not None:
        try:
            # Stop the listener (waits for queue to empty)
            _queue_listener.stop()
            _queue_listener = None
            _log_queue = None
        except Exception as e:
            # Use print since logging may not work during shutdown
            print(f"Error shutting down logging: {e}", file=sys.stderr)


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
