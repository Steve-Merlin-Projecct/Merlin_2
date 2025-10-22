"""
Database Utility Functions and Decorators

Provides reusable utilities for database operations including retry logic,
error handling decorators, and common database patterns.

Author: Automated Job Application System
Created: 2025-10-21
"""

import logging
import time
from functools import wraps
from typing import Callable, Any
from sqlalchemy.exc import (
    SQLAlchemyError,
    OperationalError,
    IntegrityError,
    DBAPIError
)

logger = logging.getLogger(__name__)


def retry_on_deadlock(max_retries: int = 3, base_delay: float = 0.1):
    """
    Decorator to retry database operations on deadlock detection.

    Uses exponential backoff to avoid thundering herd problems.
    Retries only on specific deadlock/lock timeout errors.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 0.1)

    Returns:
        Decorated function with deadlock retry logic

    Example:
        @retry_on_deadlock(max_retries=3)
        def update_job_status(job_id, status):
            # Database update operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except (OperationalError, DBAPIError) as e:
                    error_msg = str(e).lower()

                    # Check if this is a deadlock or lock timeout error
                    is_deadlock = any(keyword in error_msg for keyword in [
                        'deadlock',
                        'lock timeout',
                        'lock wait timeout',
                        'could not obtain lock'
                    ])

                    if is_deadlock and attempt < max_retries - 1:
                        # Calculate exponential backoff delay
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"Deadlock detected in {func.__name__}, "
                            f"attempt {attempt + 1}/{max_retries}, "
                            f"retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                        last_exception = e
                        continue
                    else:
                        # Not a deadlock or max retries reached
                        raise

                except SQLAlchemyError:
                    # Don't retry on other SQLAlchemy errors
                    raise

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def handle_duplicate_key(skip_on_duplicate: bool = True, log_level: str = "warning"):
    """
    Decorator to handle duplicate key constraint violations gracefully.

    Args:
        skip_on_duplicate: If True, returns None on duplicate. If False, re-raises (default: True)
        log_level: Logging level for duplicate detection ("debug", "info", "warning", "error")

    Returns:
        Decorated function with duplicate key handling

    Example:
        @handle_duplicate_key(skip_on_duplicate=True)
        def create_job(job_data):
            # Insert operation that might violate unique constraint
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)

            except IntegrityError as e:
                error_msg = str(e).lower()

                # Check if this is a duplicate key violation
                is_duplicate = any(keyword in error_msg for keyword in [
                    'duplicate key',
                    'unique constraint',
                    'duplicate entry',
                    'uniqueviolation'
                ])

                if is_duplicate:
                    log_func = getattr(logger, log_level, logger.warning)
                    log_func(
                        f"Duplicate key constraint in {func.__name__}: {e}"
                    )

                    if skip_on_duplicate:
                        return None
                    else:
                        raise
                else:
                    # Not a duplicate key error, re-raise
                    raise

        return wrapper
    return decorator


def log_query_performance(slow_query_threshold: float = 1.0):
    """
    Decorator to log query performance and warn on slow queries.

    Args:
        slow_query_threshold: Threshold in seconds to consider a query slow (default: 1.0)

    Returns:
        Decorated function with performance logging

    Example:
        @log_query_performance(slow_query_threshold=0.5)
        def get_complex_report(filters):
            # Complex query operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                if execution_time > slow_query_threshold:
                    logger.warning(
                        f"Slow query detected in {func.__name__}: "
                        f"{execution_time:.2f}s (threshold: {slow_query_threshold}s)"
                    )
                else:
                    logger.debug(
                        f"Query {func.__name__} completed in {execution_time:.2f}s"
                    )

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Query {func.__name__} failed after {execution_time:.2f}s: {e}"
                )
                raise

        return wrapper
    return decorator


def combine_decorators(*decorators):
    """
    Helper to combine multiple decorators in the correct order.

    Args:
        *decorators: Variable number of decorator functions

    Returns:
        Combined decorator

    Example:
        @combine_decorators(
            retry_on_deadlock(max_retries=3),
            handle_duplicate_key(skip_on_duplicate=True),
            log_query_performance(slow_query_threshold=1.0)
        )
        def complex_database_operation(data):
            pass
    """
    def decorator(func: Callable) -> Callable:
        for dec in reversed(decorators):
            func = dec(func)
        return func
    return decorator


class DatabaseErrorResponse:
    """
    Standardized error response object for database operations.

    Provides consistent error reporting across all database methods.
    """

    @staticmethod
    def success(data: Any = None, message: str = "Operation successful") -> dict:
        """
        Create a success response.

        Args:
            data: Operation result data
            message: Success message

        Returns:
            Standardized success response dict
        """
        return {
            "success": True,
            "data": data,
            "message": message,
            "error": None,
            "error_code": None
        }

    @staticmethod
    def error(
        error: Exception,
        error_code: str = "DB_ERROR",
        message: str = None,
        data: Any = None
    ) -> dict:
        """
        Create an error response.

        Args:
            error: Exception that occurred
            error_code: Standardized error code
            message: Human-readable error message
            data: Any partial data if applicable

        Returns:
            Standardized error response dict
        """
        return {
            "success": False,
            "data": data,
            "message": message or str(error),
            "error": str(error),
            "error_code": error_code
        }

    @staticmethod
    def not_found(resource: str = "Resource", data: Any = None) -> dict:
        """
        Create a not found response.

        Args:
            resource: Resource type that was not found
            data: Any partial data if applicable

        Returns:
            Standardized not found response dict
        """
        return {
            "success": False,
            "data": data,
            "message": f"{resource} not found",
            "error": "Not found",
            "error_code": "NOT_FOUND"
        }
