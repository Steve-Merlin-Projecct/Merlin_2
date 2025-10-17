"""
Timeout Manager - Configurable timeout management for operations

Provides centralized timeout configuration and enforcement across
different operation types in the job application system.
"""

import time
import signal
from typing import Dict, Optional, Callable, Any
from enum import Enum
from contextlib import contextmanager
from .resilience_error import TimeoutError as ResilienceTimeoutError

# Re-export TimeoutError for convenience
TimeoutError = ResilienceTimeoutError


class OperationType(Enum):
    """Types of operations with different timeout requirements"""

    # API operations
    API_CALL = "api_call"
    AI_API_CALL = "ai_api_call"
    GEMINI_ANALYSIS = "gemini_analysis"
    BATCH_ANALYSIS = "batch_analysis"

    # Database operations
    DATABASE_QUERY = "database_query"
    DATABASE_WRITE = "database_write"
    DATABASE_TRANSACTION = "database_transaction"

    # Document generation
    DOCUMENT_GENERATION = "document_generation"
    TEMPLATE_PROCESSING = "template_processing"

    # Email operations
    EMAIL_SEND = "email_send"
    EMAIL_BATCH = "email_batch"

    # Scraping operations
    JOB_SCRAPE = "job_scrape"
    BATCH_SCRAPE = "batch_scrape"

    # Workflow operations
    WORKFLOW = "workflow"
    CHECKPOINT = "checkpoint"

    # Generic/Default
    GENERIC = "generic"
    DEFAULT = "default"


class TimeoutConfig:
    """
    Configuration for timeout management

    Maintains default timeouts for different operation types and
    supports custom timeout overrides.
    """

    def __init__(self):
        """Initialize with default timeout values"""
        self._timeouts: Dict[OperationType, float] = {
            # API timeouts (seconds)
            OperationType.API_CALL: 30.0,
            OperationType.AI_API_CALL: 60.0,
            OperationType.GEMINI_ANALYSIS: 120.0,
            OperationType.BATCH_ANALYSIS: 600.0,  # 10 minutes

            # Database timeouts
            OperationType.DATABASE_QUERY: 30.0,
            OperationType.DATABASE_WRITE: 60.0,
            OperationType.DATABASE_TRANSACTION: 120.0,

            # Document generation timeouts
            OperationType.DOCUMENT_GENERATION: 90.0,
            OperationType.TEMPLATE_PROCESSING: 45.0,

            # Email timeouts
            OperationType.EMAIL_SEND: 60.0,
            OperationType.EMAIL_BATCH: 300.0,  # 5 minutes

            # Scraping timeouts
            OperationType.JOB_SCRAPE: 180.0,  # 3 minutes
            OperationType.BATCH_SCRAPE: 900.0,  # 15 minutes

            # Workflow timeouts
            OperationType.WORKFLOW: 1800.0,  # 30 minutes
            OperationType.CHECKPOINT: 10.0,

            # Generic/Default
            OperationType.GENERIC: 60.0,
            OperationType.DEFAULT: 60.0
        }

        # Custom timeout overrides (operation_name -> timeout)
        self._custom_timeouts: Dict[str, float] = {}

    def get_timeout(
        self,
        operation_type: OperationType,
        operation_name: Optional[str] = None
    ) -> float:
        """
        Get timeout for operation type or operation name

        Args:
            operation_type: Type of operation
            operation_name: Specific operation name (overrides operation_type if custom timeout set)

        Returns:
            Timeout in seconds
        """
        # Check for custom timeout by operation name first
        if operation_name and operation_name in self._custom_timeouts:
            return self._custom_timeouts[operation_name]

        return self._timeouts.get(operation_type, self._timeouts[OperationType.DEFAULT])

    def set_timeout(self, operation_type: OperationType, timeout_seconds: float):
        """
        Set timeout for operation type

        Args:
            operation_type: Type of operation
            timeout_seconds: Timeout value in seconds
        """
        if timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")
        self._timeouts[operation_type] = timeout_seconds

    def reset_timeout(self, operation_type: OperationType):
        """Reset timeout to default value"""
        # Re-initialize default for this operation type
        defaults = TimeoutConfig()
        self._timeouts[operation_type] = defaults._timeouts[operation_type]

    def set_custom_timeout(self, key: str, timeout_seconds: float):
        """
        Set custom timeout for specific operation

        Args:
            key: Custom operation identifier
            timeout_seconds: Timeout value in seconds
        """
        if timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")
        self._custom_timeouts[key] = timeout_seconds

    def get_custom_timeout(self, key: str, default: float = 60.0) -> float:
        """
        Get custom timeout

        Args:
            key: Custom operation identifier
            default: Default value if not found

        Returns:
            Timeout in seconds
        """
        return self._custom_timeouts.get(key, default)


# Global timeout configuration instance
timeout_config = TimeoutConfig()


# Global timeout statistics tracking
_timeout_stats = {
    "total_timeouts": 0,
    "operations": {}  # operation_name -> count
}


class TimeoutManager:
    """
    Manager for timeout enforcement

    Provides context managers and decorators for enforcing timeouts
    on operations using signal-based or polling-based approaches.
    """

    def __init__(self, config: Optional[TimeoutConfig] = None):
        """
        Initialize timeout manager

        Args:
            config: Timeout configuration (uses global if not provided)
        """
        self.config = config or timeout_config

    @contextmanager
    def timeout_context(
        self,
        operation_type: OperationType = OperationType.DEFAULT,
        timeout_seconds: Optional[float] = None,
        operation_name: Optional[str] = None
    ):
        """
        Context manager for timeout enforcement

        Args:
            operation_type: Type of operation
            timeout_seconds: Override timeout (uses configured timeout if None)
            operation_name: Name of the operation for tracking

        Raises:
            ResilienceTimeoutError: If operation exceeds timeout

        Example:
            with timeout_manager.timeout_context(OperationType.API_CALL, operation_name="api_call"):
                result = make_api_call()
        """
        timeout = timeout_seconds or self.config.get_timeout(operation_type)
        op_name = operation_name or operation_type.value
        start_time = time.time()

        def timeout_handler(signum, frame):
            global _timeout_stats
            elapsed = time.time() - start_time

            # Update statistics
            _timeout_stats["total_timeouts"] += 1
            _timeout_stats["operations"][op_name] = _timeout_stats["operations"].get(op_name, 0) + 1

            raise ResilienceTimeoutError(
                operation_name=op_name,
                timeout_seconds=timeout,
                message=f"Operation timed out after {elapsed:.2f} seconds",
                context={"operation_type": operation_type.value, "elapsed": elapsed}
            )

        # Set up signal-based timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))

        try:
            yield
        finally:
            # Cancel timeout and restore old handler
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    def with_timeout(
        self,
        operation_type: OperationType = OperationType.DEFAULT,
        timeout_seconds: Optional[float] = None
    ):
        """
        Decorator for timeout enforcement

        Args:
            operation_type: Type of operation
            timeout_seconds: Override timeout

        Example:
            @timeout_manager.with_timeout(OperationType.DATABASE_QUERY)
            def query_database():
                return db.execute(query)
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                with self.timeout_context(operation_type, timeout_seconds):
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    def check_timeout(
        self,
        start_time: float,
        operation_type: OperationType = OperationType.DEFAULT,
        timeout_seconds: Optional[float] = None
    ):
        """
        Check if operation has exceeded timeout (polling-based)

        Args:
            start_time: Operation start time (from time.time())
            operation_type: Type of operation
            timeout_seconds: Override timeout

        Raises:
            ResilienceTimeoutError: If operation has exceeded timeout

        Example:
            start = time.time()
            while not done:
                timeout_manager.check_timeout(start, OperationType.API_CALL)
                # do work
        """
        timeout = timeout_seconds or self.config.get_timeout(operation_type)
        elapsed = time.time() - start_time

        if elapsed > timeout:
            raise ResilienceTimeoutError(
                f"Operation exceeded timeout of {timeout}s (elapsed: {elapsed:.2f}s)",
                timeout_seconds=timeout,
                context={"operation_type": operation_type.value, "elapsed": elapsed}
            )

    def get_remaining_time(
        self,
        start_time: float,
        operation_type: OperationType = OperationType.DEFAULT,
        timeout_seconds: Optional[float] = None
    ) -> float:
        """
        Get remaining time before timeout

        Args:
            start_time: Operation start time
            operation_type: Type of operation
            timeout_seconds: Override timeout

        Returns:
            Remaining seconds (0 if already timed out)
        """
        timeout = timeout_seconds or self.config.get_timeout(operation_type)
        elapsed = time.time() - start_time
        remaining = timeout - elapsed
        return max(0.0, remaining)


# Global timeout manager instance
_global_timeout_manager = TimeoutManager()


# Module-level convenience functions
def with_timeout(
    timeout: Optional[float] = None,
    operation_type: OperationType = OperationType.DEFAULT,
    operation_name: Optional[str] = None
):
    """
    Decorator for timeout enforcement

    Args:
        timeout: Timeout in seconds (None to use default for operation_type)
        operation_type: Type of operation
        operation_name: Name of operation for tracking

    Returns:
        Decorator function

    Example:
        @with_timeout(timeout=2.0, operation_name="my_function")
        def my_function():
            # function code
            pass
    """
    def decorator(func: Callable) -> Callable:
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            with _global_timeout_manager.timeout_context(
                operation_type=operation_type,
                timeout_seconds=timeout,
                operation_name=op_name
            ):
                return func(*args, **kwargs)
        return wrapper
    return decorator


@contextmanager
def timeout_block(
    timeout: float,
    operation_name: str,
    operation_type: OperationType = OperationType.DEFAULT
):
    """
    Context manager for timeout enforcement

    Args:
        timeout: Timeout in seconds
        operation_name: Name of operation
        operation_type: Type of operation

    Example:
        with timeout_block(2.0, "my_operation"):
            # operation code
            pass
    """
    with _global_timeout_manager.timeout_context(
        operation_type=operation_type,
        timeout_seconds=timeout,
        operation_name=operation_name
    ):
        yield


def configure_timeout(
    operation_type: Optional[OperationType] = None,
    operation_name: Optional[str] = None,
    timeout: float = 60.0
):
    """
    Configure timeout for operation type or specific operation name

    Args:
        operation_type: Type of operation (mutually exclusive with operation_name)
        operation_name: Specific operation name (mutually exclusive with operation_type)
        timeout: Timeout value in seconds

    Raises:
        ValueError: If neither or both operation_type and operation_name are specified
    """
    if operation_type is not None and operation_name is not None:
        raise ValueError("Cannot specify both operation_type and operation_name")

    if operation_type is None and operation_name is None:
        raise ValueError("Must specify either operation_type or operation_name")

    if operation_type is not None:
        timeout_config.set_timeout(operation_type, timeout)
    else:
        timeout_config.set_custom_timeout(operation_name, timeout)


def get_timeout_stats() -> Dict[str, Any]:
    """
    Get timeout statistics

    Returns:
        Dictionary with timeout statistics including total count and per-operation counts
    """
    return dict(_timeout_stats)
