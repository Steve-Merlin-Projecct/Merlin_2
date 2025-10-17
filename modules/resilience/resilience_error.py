"""
Resilience Error Classes - Custom exceptions for the resilience system

Provides structured error types for different failure categories and severities,
enabling intelligent error handling and recovery strategies.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class ErrorCategory(Enum):
    """Categories of errors for classification and handling"""

    # Network and connectivity errors
    NETWORK = "network"
    NETWORK_TIMEOUT = "network_timeout"
    TIMEOUT = "timeout"
    CONNECTION = "connection"
    CONNECTION_ERROR = "connection_error"
    DNS_ERROR = "dns_error"

    # API and service errors
    API_ERROR = "api_error"
    API_RATE_LIMIT = "api_rate_limit"
    API_QUOTA_EXCEEDED = "api_quota_exceeded"
    API_AUTH_FAILURE = "api_auth_failure"
    API_SERVICE_UNAVAILABLE = "api_service_unavailable"
    RATE_LIMIT = "rate_limit"
    QUOTA_EXCEEDED = "quota_exceeded"
    AUTHENTICATION = "authentication"

    # Database errors
    DATABASE = "database"
    DATABASE_CONNECTION = "database_connection"
    DATABASE_TIMEOUT = "database_timeout"
    DATABASE_DEADLOCK = "database_deadlock"
    DATABASE_CONSTRAINT_VIOLATION = "database_constraint_violation"
    DEADLOCK = "deadlock"
    CONSTRAINT_VIOLATION = "constraint_violation"

    # Resource errors
    RESOURCE_EXHAUSTED = "resource_exhausted"
    DISK_FULL = "disk_full"
    MEMORY_ERROR = "memory_error"

    # Business logic errors
    VALIDATION = "validation"
    VALIDATION_ERROR = "validation_error"
    BUSINESS_LOGIC = "business_logic"
    DATA_INCONSISTENCY = "data_inconsistency"
    PERMISSION_DENIED = "permission_denied"

    # System errors
    SYSTEM = "system"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for error classification"""

    INFO = "info"         # Informational, no immediate action required
    LOW = "low"           # Low priority, no immediate action required
    MEDIUM = "medium"     # Warning, may require attention
    HIGH = "high"         # Error, requires intervention
    CRITICAL = "critical" # Critical failure, immediate action required


class ResilienceError(Exception):
    """
    Base exception class for resilience system errors

    Provides structured error information including category, severity,
    retry eligibility, and additional context for intelligent error handling.

    Attributes:
        operation_name: Name of the operation that failed
        original_error: Original exception that was wrapped
        error_category: Error category for classification
        error_severity: Error severity level
        context: Additional context information
        correlation_id: Unique identifier for error tracking
        timestamp: When the error occurred
        attempt_number: Retry attempt number (1-indexed)
        parent_error: Previous error in retry chain
    """

    def __init__(
        self,
        operation_name: str,
        original_error: Exception,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        error_severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        attempt_number: int = 1,
        parent_error: Optional['ResilienceError'] = None
    ):
        """
        Initialize resilience error

        Args:
            operation_name: Name of the operation that failed
            original_error: Original exception that was wrapped
            error_category: Error category for classification
            error_severity: Severity level of the error
            context: Additional context information
            correlation_id: Unique identifier for tracking (auto-generated if not provided)
            timestamp: Error timestamp (auto-generated if not provided)
            attempt_number: Retry attempt number (1-indexed)
            parent_error: Previous error in retry chain
        """
        super().__init__(str(original_error))
        self.operation_name = operation_name
        self.original_error = original_error
        self.error_category = error_category
        self.error_severity = error_severity
        self.context = context or {}
        self.correlation_id = correlation_id or f"err_{uuid.uuid4().hex[:12]}"
        self.timestamp = timestamp or datetime.now()
        self.attempt_number = attempt_number
        self.parent_error = parent_error

        # Legacy attributes for backward compatibility
        self.message = str(original_error)
        self.category = error_category
        self.severity = error_severity
        self.retry_eligible = self._determine_retry_eligible()

    def _determine_retry_eligible(self) -> bool:
        """
        Determine if this error is eligible for retry based on category

        Returns:
            True if the error can be retried
        """
        # Non-retryable categories
        non_retryable_categories = [
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

        return self.error_category not in non_retryable_categories

    def is_retryable(self) -> bool:
        """
        Check if this error is eligible for retry

        Returns:
            True if the operation can be retried
        """
        return self.retry_eligible

    def __str__(self) -> str:
        """String representation of the error"""
        parts = [
            f"[{self.operation_name}]",
            f"{self.correlation_id}:",
            f"{self.error_category.value.upper()}",
            f"[{self.error_severity.value}]",
            str(self.original_error)
        ]

        return " ".join(parts)

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"ResilienceError("
            f"operation='{self.operation_name}', "
            f"correlation_id='{self.correlation_id}', "
            f"category={self.error_category.value}, "
            f"severity={self.error_severity.value}, "
            f"retryable={self.retry_eligible}"
            f")"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization"""
        return {
            "error_type": self.__class__.__name__,
            "operation_name": self.operation_name,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "error_category": self.error_category.value,
            "error_severity": self.error_severity.value,
            "retry_eligible": self.retry_eligible,
            "attempt_number": self.attempt_number,
            "context": self.context,
            "original_error": str(self.original_error) if self.original_error else None,
            "message": str(self.original_error)
        }


class TimeoutError(ResilienceError):
    """Error raised when an operation exceeds its timeout"""

    def __init__(
        self,
        operation_name: str = "unknown_operation",
        timeout_seconds: Optional[float] = None,
        **kwargs
    ):
        # Create a builtin TimeoutError as the original error
        message = kwargs.pop("message", "Operation timed out")
        if timeout_seconds:
            message = f"{message} (timeout: {timeout_seconds}s)"

        original_error = kwargs.pop("original_error", __builtins__["TimeoutError"](message))

        context = kwargs.get("context", {})
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        kwargs["context"] = context

        super().__init__(
            operation_name=operation_name,
            original_error=original_error,
            error_category=ErrorCategory.NETWORK_TIMEOUT,
            error_severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

        # Store timeout_seconds for easy access
        self.timeout_seconds = timeout_seconds


class CircuitBreakerError(ResilienceError):
    """Error raised when circuit breaker is open"""

    def __init__(
        self,
        message: str = "Circuit breaker is open",
        circuit_name: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if circuit_name:
            context["circuit_name"] = circuit_name
        kwargs["context"] = context

        super().__init__(
            message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            retry_eligible=False,
            **kwargs
        )


class RateLimitError(ResilienceError):
    """Error raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if retry_after:
            context["retry_after_seconds"] = retry_after
        kwargs["context"] = context

        super().__init__(
            message,
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            retry_eligible=True,
            **kwargs
        )


class DatabaseError(ResilienceError):
    """Error raised for database-related failures"""

    def __init__(
        self,
        message: str = "Database operation failed",
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            retry_eligible=True,
            **kwargs
        )


class ValidationError(ResilienceError):
    """Error raised for validation failures"""

    def __init__(
        self,
        message: str = "Validation failed",
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            retry_eligible=False,
            **kwargs
        )


def wrap_error(
    operation_name: str,
    error: Exception,
    category: Optional[ErrorCategory] = None,
    severity: Optional[ErrorSeverity] = None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> ResilienceError:
    """
    Convenience function to wrap an exception in ResilienceError

    Args:
        operation_name: Name of the operation that failed
        error: Exception to wrap
        category: Error category (optional)
        severity: Error severity (optional)
        context: Additional context information
        **kwargs: Additional arguments for ResilienceError

    Returns:
        ResilienceError wrapping the original exception

    Note:
        If error is already a ResilienceError, returns it unchanged
    """
    # If already a ResilienceError, return as-is
    if isinstance(error, ResilienceError):
        return error

    # Build kwargs for ResilienceError
    resilience_kwargs = {
        "operation_name": operation_name,
        "original_error": error,
        "context": context or {}
    }

    if category is not None:
        resilience_kwargs["error_category"] = category

    if severity is not None:
        resilience_kwargs["error_severity"] = severity

    # Merge any additional kwargs
    resilience_kwargs.update(kwargs)

    return ResilienceError(**resilience_kwargs)
