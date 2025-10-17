"""
Error Classifier - Intelligent error categorization and handling

Analyzes exceptions to determine error category, severity, and appropriate
recovery strategies for the resilience system.
"""

import re
from typing import Optional, Dict, Any, Type
from .resilience_error import (
    ResilienceError, ErrorCategory, ErrorSeverity,
    TimeoutError, CircuitBreakerError, RateLimitError,
    DatabaseError, ValidationError
)


class ErrorClassifier:
    """
    Classifies errors and determines appropriate handling strategies

    Analyzes exception types and messages to categorize errors,
    assess severity, and determine retry eligibility.
    """

    # Error patterns for classification
    _PATTERNS = {
        ErrorCategory.NETWORK_TIMEOUT: [
            r"timeout",
            r"timed out",
            r"time.*out",
            r"deadline exceeded",
            r"connection timeout"
        ],
        ErrorCategory.CONNECTION_ERROR: [
            r"connection refused",
            r"connection reset",
            r"connection.*failed",
            r"failed to connect",
            r"unable to establish connection"
        ],
        ErrorCategory.NETWORK: [
            r"network",
            r"no route to host",
            r"host.*unreachable"
        ],
        ErrorCategory.API_RATE_LIMIT: [
            r"rate limit",
            r"too many requests",
            r"429"
        ],
        ErrorCategory.API_AUTH_FAILURE: [
            r"401",
            r"403",
            r"unauthorized",
            r"forbidden",
            r"invalid.*credentials",
            r"auth.*failed"
        ],
        ErrorCategory.API_SERVICE_UNAVAILABLE: [
            r"503",
            r"service unavailable",
            r"502",
            r"bad gateway",
            r"500",
            r"internal server error"
        ],
        ErrorCategory.DATABASE_DEADLOCK: [
            r"deadlock",
            r"deadlock detected"
        ],
        ErrorCategory.DATABASE_CONNECTION: [
            r"database connection",
            r"connection pool",
            r"database.*failed"
        ],
        ErrorCategory.DATABASE_TIMEOUT: [
            r"lock timeout",
            r"lock wait timeout",
            r"query timeout"
        ],
        ErrorCategory.DATABASE: [
            r"database",
            r"sql",
            r"postgres",
            r"query.*failed"
        ],
        ErrorCategory.DATABASE_CONSTRAINT_VIOLATION: [
            r"constraint.*violation",
            r"unique.*constraint",
            r"foreign.*key",
            r"integrity.*error"
        ],
        ErrorCategory.DISK_FULL: [
            r"disk.*full",
            r"no space left",
            r"storage.*full",
            r"disk full"
        ],
        ErrorCategory.MEMORY_ERROR: [
            r"memory",
            r"out of memory",
            r"cannot allocate",
            r"system resource exhausted"
        ],
        ErrorCategory.VALIDATION_ERROR: [
            r"validation.*failed",
            r"invalid.*input",
            r"invalid.*format",
            r"invalid.*data",
            r"schema validation failed"
        ],
        ErrorCategory.VALIDATION: [
            r"bad.*request",
            r"400"
        ]
    }

    # Exception type to category mapping
    _TYPE_MAPPING: Dict[Type[Exception], ErrorCategory] = {
        TimeoutError: ErrorCategory.NETWORK_TIMEOUT,
        ConnectionError: ErrorCategory.CONNECTION_ERROR,
        ConnectionRefusedError: ErrorCategory.CONNECTION_ERROR,
        ConnectionResetError: ErrorCategory.CONNECTION_ERROR,
        ValueError: ErrorCategory.VALIDATION_ERROR,
        TypeError: ErrorCategory.VALIDATION_ERROR,
        KeyError: ErrorCategory.VALIDATION_ERROR,
        AttributeError: ErrorCategory.BUSINESS_LOGIC,
        MemoryError: ErrorCategory.MEMORY_ERROR,
    }

    def __init__(self):
        """Initialize error classifier"""
        # Compile regex patterns for efficiency
        self._compiled_patterns = {
            category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for category, patterns in self._PATTERNS.items()
        }

    def classify(
        self,
        error: Exception,
        operation_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ResilienceError:
        """
        Classify an exception into a ResilienceError

        Args:
            error: Exception to classify
            operation_name: Name of the operation that failed
            context: Additional context information

        Returns:
            ResilienceError with appropriate classification
        """
        # If already a ResilienceError, return as-is
        if isinstance(error, ResilienceError):
            return error

        # Handle None error gracefully
        if error is None:
            error = Exception("None error encountered")

        # Determine category
        category = self._determine_category(error)

        # Determine severity
        severity = self._determine_severity(error, category)

        # Create ResilienceError with appropriate classification
        return ResilienceError(
            operation_name=operation_name,
            original_error=error,
            error_category=category,
            error_severity=severity,
            context=context or {}
        )

    def _determine_category(self, error: Exception) -> ErrorCategory:
        """
        Determine error category from exception

        Args:
            error: Exception to categorize

        Returns:
            Error category
        """
        # Check type mapping first
        error_type = type(error)
        if error_type in self._TYPE_MAPPING:
            return self._TYPE_MAPPING[error_type]

        # Check error message against patterns
        # Order matters! Check more specific patterns before generic ones
        error_message = str(error).lower()

        # Define priority order for pattern matching (most specific first)
        priority_categories = [
            # Database-specific categories first (before generic connection errors)
            ErrorCategory.DATABASE_DEADLOCK,
            ErrorCategory.DATABASE_CONNECTION,
            ErrorCategory.DATABASE_TIMEOUT,
            ErrorCategory.DATABASE_CONSTRAINT_VIOLATION,
            ErrorCategory.DATABASE,
            # API-specific categories
            ErrorCategory.API_AUTH_FAILURE,
            ErrorCategory.API_RATE_LIMIT,
            ErrorCategory.API_SERVICE_UNAVAILABLE,
            # Network-specific categories (after database)
            ErrorCategory.NETWORK_TIMEOUT,
            ErrorCategory.CONNECTION_ERROR,
            # Then generic categories
            ErrorCategory.VALIDATION_ERROR,
            ErrorCategory.NETWORK,
            ErrorCategory.TIMEOUT,
            ErrorCategory.VALIDATION,
            ErrorCategory.DISK_FULL,
            ErrorCategory.MEMORY_ERROR,
        ]

        # Check priority categories first
        for category in priority_categories:
            if category in self._compiled_patterns:
                for pattern in self._compiled_patterns[category]:
                    if pattern.search(error_message):
                        return category

        # Check remaining categories
        for category, patterns in self._compiled_patterns.items():
            if category not in priority_categories:
                for pattern in patterns:
                    if pattern.search(error_message):
                        return category

        # Default to unknown
        return ErrorCategory.UNKNOWN

    def _determine_severity(
        self,
        error: Exception,
        category: ErrorCategory
    ) -> ErrorSeverity:
        """
        Determine error severity

        Args:
            error: Exception
            category: Error category

        Returns:
            Error severity level
        """
        # Critical severities
        if category in [
            ErrorCategory.DISK_FULL,
            ErrorCategory.MEMORY_ERROR,
            ErrorCategory.DATA_INCONSISTENCY,
            ErrorCategory.API_AUTH_FAILURE,
            ErrorCategory.AUTHENTICATION
        ]:
            return ErrorSeverity.CRITICAL

        # High severities
        if category in [
            ErrorCategory.DATABASE,
            ErrorCategory.DATABASE_CONNECTION,
            ErrorCategory.DATABASE_DEADLOCK,
            ErrorCategory.DEADLOCK,
            ErrorCategory.SYSTEM
        ]:
            return ErrorSeverity.HIGH

        # Medium severities
        if category in [
            ErrorCategory.NETWORK,
            ErrorCategory.NETWORK_TIMEOUT,
            ErrorCategory.CONNECTION_ERROR,
            ErrorCategory.TIMEOUT,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.API_RATE_LIMIT,
            ErrorCategory.API_ERROR,
            ErrorCategory.API_SERVICE_UNAVAILABLE
        ]:
            return ErrorSeverity.MEDIUM

        # Low severities
        if category in [
            ErrorCategory.VALIDATION,
            ErrorCategory.VALIDATION_ERROR,
            ErrorCategory.BUSINESS_LOGIC
        ]:
            return ErrorSeverity.LOW

        # Default
        return ErrorSeverity.MEDIUM

    def _is_retry_eligible(
        self,
        error: Exception,
        category: ErrorCategory
    ) -> bool:
        """
        Determine if error is eligible for retry

        Args:
            error: Exception
            category: Error category

        Returns:
            True if retry is appropriate
        """
        # Never retry these categories
        non_retryable = [
            ErrorCategory.VALIDATION,
            ErrorCategory.VALIDATION_ERROR,
            ErrorCategory.API_AUTH_FAILURE,
            ErrorCategory.AUTHENTICATION,
            ErrorCategory.PERMISSION_DENIED,
            ErrorCategory.CONSTRAINT_VIOLATION,
            ErrorCategory.DATABASE_CONSTRAINT_VIOLATION,
            ErrorCategory.BUSINESS_LOGIC,
            ErrorCategory.CONFIGURATION
        ]

        if category in non_retryable:
            return False

        # Retry these categories
        retryable = [
            ErrorCategory.NETWORK,
            ErrorCategory.NETWORK_TIMEOUT,
            ErrorCategory.CONNECTION_ERROR,
            ErrorCategory.TIMEOUT,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.API_RATE_LIMIT,
            ErrorCategory.API_SERVICE_UNAVAILABLE,
            ErrorCategory.DEADLOCK,
            ErrorCategory.DATABASE_DEADLOCK,
            ErrorCategory.DATABASE_CONNECTION,
            ErrorCategory.DATABASE_TIMEOUT,
            ErrorCategory.CONNECTION
        ]

        if category in retryable:
            return True

        # Default: retry unless it's clearly a logic error
        error_message = str(error).lower()
        non_retryable_keywords = [
            "invalid",
            "illegal",
            "bad request",
            "not found",
            "permission denied"
        ]

        for keyword in non_retryable_keywords:
            if keyword in error_message:
                return False

        return True

    def get_retry_strategy(
        self,
        error: ResilienceError
    ) -> Dict[str, Any]:
        """
        Get recommended retry strategy for error

        Args:
            error: Classified resilience error

        Returns:
            Dict with retry strategy parameters
        """
        if not error.retry_eligible:
            return {
                "max_attempts": 0,
                "base_delay": 0,
                "exponential_backoff": False
            }

        # Rate limit errors need longer delays
        if error.error_category in [ErrorCategory.RATE_LIMIT, ErrorCategory.API_RATE_LIMIT]:
            retry_after = error.context.get("retry_after_seconds", 60)
            return {
                "max_attempts": 3,
                "base_delay": retry_after,
                "exponential_backoff": False,
                "max_delay": retry_after * 2
            }

        # Deadlock errors need immediate retry
        if error.error_category in [ErrorCategory.DEADLOCK, ErrorCategory.DATABASE_DEADLOCK]:
            return {
                "max_attempts": 5,
                "base_delay": 0.1,
                "exponential_backoff": True,
                "max_delay": 5.0
            }

        # Network/timeout errors use exponential backoff
        if error.error_category in [
            ErrorCategory.NETWORK,
            ErrorCategory.NETWORK_TIMEOUT,
            ErrorCategory.CONNECTION_ERROR,
            ErrorCategory.TIMEOUT
        ]:
            return {
                "max_attempts": 3,
                "base_delay": 1.0,
                "exponential_backoff": True,
                "max_delay": 30.0
            }

        # Database errors
        if error.error_category in [
            ErrorCategory.DATABASE,
            ErrorCategory.DATABASE_CONNECTION,
            ErrorCategory.DATABASE_TIMEOUT
        ]:
            return {
                "max_attempts": 3,
                "base_delay": 2.0,
                "exponential_backoff": True,
                "max_delay": 60.0
            }

        # Default strategy
        return {
            "max_attempts": 3,
            "base_delay": 1.0,
            "exponential_backoff": True,
            "max_delay": 30.0
        }

    def should_alert(self, error: ResilienceError) -> bool:
        """
        Determine if error requires immediate alerting

        Args:
            error: Classified resilience error

        Returns:
            True if alert should be sent
        """
        # Always alert on critical errors
        if error.error_severity == ErrorSeverity.CRITICAL:
            return True

        # Alert on high severity if not retry-eligible
        if error.error_severity == ErrorSeverity.HIGH and not error.retry_eligible:
            return True

        # Alert on authentication failures
        if error.error_category in [ErrorCategory.AUTHENTICATION, ErrorCategory.API_AUTH_FAILURE]:
            return True

        return False
