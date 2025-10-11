"""
Unit tests for Resilience Error

Tests error wrapping, correlation tracking, error chains, serialization,
and retryability logic.
"""

import pytest
from datetime import datetime
from modules.resilience.resilience_error import (
    ResilienceError, ErrorCategory, ErrorSeverity, wrap_error
)


@pytest.mark.unit
class TestResilienceErrorCreation:
    """Test ResilienceError creation and initialization"""

    def test_basic_error_creation(self):
        """Test creating basic ResilienceError"""
        original = Exception("Test error")
        error = ResilienceError(
            operation_name="test_op",
            original_error=original,
            error_category=ErrorCategory.NETWORK_TIMEOUT,
            error_severity=ErrorSeverity.MEDIUM
        )

        assert error.operation_name == "test_op"
        assert error.original_error is original
        assert error.error_category == ErrorCategory.NETWORK_TIMEOUT
        assert error.error_severity == ErrorSeverity.MEDIUM
        assert error.attempt_number == 1

    def test_correlation_id_generated(self):
        """Test correlation ID is automatically generated"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("Test"),
        )

        assert error.correlation_id is not None
        assert len(error.correlation_id) > 0
        assert error.correlation_id.startswith("err_")

    def test_custom_correlation_id(self):
        """Test providing custom correlation ID"""
        custom_id = "custom_correlation_id"
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("Test"),
            correlation_id=custom_id
        )

        assert error.correlation_id == custom_id

    def test_timestamp_recorded(self):
        """Test timestamp is recorded on creation"""
        before = datetime.now()
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("Test")
        )
        after = datetime.now()

        assert before <= error.timestamp <= after

    def test_context_preserved(self):
        """Test context dictionary is preserved"""
        context = {"key": "value", "count": 42}
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("Test"),
            context=context
        )

        assert error.context == context
        assert error.context["key"] == "value"
        assert error.context["count"] == 42


@pytest.mark.unit
class TestErrorChaining:
    """Test error chain tracking for retry scenarios"""

    def test_parent_error_tracking(self):
        """Test tracking parent error in chain"""
        original = Exception("Original error")
        first_error = ResilienceError(
            operation_name="test_op",
            original_error=original,
            attempt_number=1
        )

        second_error = ResilienceError(
            operation_name="test_op",
            original_error=original,
            attempt_number=2,
            parent_error=first_error
        )

        assert second_error.parent_error is first_error
        assert second_error.attempt_number == 2

    def test_error_chain_depth(self):
        """Test building deep error chains"""
        original = Exception("Test error")
        current_error = None

        for i in range(1, 5):
            current_error = ResilienceError(
                operation_name="retry_op",
                original_error=original,
                attempt_number=i,
                parent_error=current_error
            )

        # Walk back through chain
        depth = 0
        error = current_error
        while error is not None:
            depth += 1
            error = error.parent_error

        assert depth == 4
        assert current_error.attempt_number == 4


@pytest.mark.unit
class TestRetryabilityLogic:
    """Test retryability determination"""

    def test_network_timeout_retryable(self):
        """Test network timeout errors are retryable"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=TimeoutError("Timeout"),
            error_category=ErrorCategory.NETWORK_TIMEOUT
        )

        assert error.is_retryable() is True

    def test_connection_error_retryable(self):
        """Test connection errors are retryable"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=ConnectionError("Connection failed"),
            error_category=ErrorCategory.CONNECTION_ERROR
        )

        assert error.is_retryable() is True

    def test_api_rate_limit_retryable(self):
        """Test rate limit errors are retryable"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("429 Too Many Requests"),
            error_category=ErrorCategory.API_RATE_LIMIT
        )

        assert error.is_retryable() is True

    def test_auth_failure_not_retryable(self):
        """Test auth failures are not retryable"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("401 Unauthorized"),
            error_category=ErrorCategory.API_AUTH_FAILURE
        )

        assert error.is_retryable() is False

    def test_validation_error_not_retryable(self):
        """Test validation errors are not retryable"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=ValueError("Invalid input"),
            error_category=ErrorCategory.VALIDATION_ERROR
        )

        assert error.is_retryable() is False

    def test_permission_denied_not_retryable(self):
        """Test permission denied not retryable"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=PermissionError("Access denied"),
            error_category=ErrorCategory.PERMISSION_DENIED
        )

        assert error.is_retryable() is False


@pytest.mark.unit
class TestErrorSerialization:
    """Test error serialization to dict"""

    def test_to_dict_basic(self):
        """Test basic to_dict serialization"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("Test error"),
            error_category=ErrorCategory.NETWORK_TIMEOUT,
            error_severity=ErrorSeverity.MEDIUM
        )

        error_dict = error.to_dict()

        assert error_dict["operation_name"] == "test_op"
        assert error_dict["error_category"] == "network_timeout"
        assert error_dict["error_severity"] == "medium"
        assert error_dict["correlation_id"] == error.correlation_id
        assert "timestamp" in error_dict

    def test_to_dict_includes_context(self):
        """Test context is included in serialization"""
        context = {"key": "value"}
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("Test"),
            context=context
        )

        error_dict = error.to_dict()
        assert "context" in error_dict
        assert error_dict["context"]["key"] == "value"

    def test_to_dict_includes_original_error_info(self):
        """Test original error information included"""
        original = ValueError("Invalid input")
        error = ResilienceError(
            operation_name="test_op",
            original_error=original
        )

        error_dict = error.to_dict()
        assert "original_error" in error_dict
        assert "Invalid input" in str(error_dict["original_error"])


@pytest.mark.unit
class TestWrapErrorFunction:
    """Test wrap_error convenience function"""

    def test_wrap_error_basic(self):
        """Test basic error wrapping"""
        original = Exception("Test error")
        wrapped = wrap_error(
            operation_name="test_op",
            error=original,
            category=ErrorCategory.NETWORK_TIMEOUT,
            severity=ErrorSeverity.MEDIUM
        )

        assert isinstance(wrapped, ResilienceError)
        assert wrapped.original_error is original
        assert wrapped.error_category == ErrorCategory.NETWORK_TIMEOUT

    def test_wrap_error_with_context(self):
        """Test wrapping with context"""
        context = {"retry_count": 3}
        wrapped = wrap_error(
            operation_name="test_op",
            error=Exception("Test"),
            context=context
        )

        assert wrapped.context["retry_count"] == 3

    def test_wrap_already_wrapped_error(self):
        """Test wrapping already wrapped error returns same"""
        original = ResilienceError(
            operation_name="original_op",
            original_error=Exception("Test")
        )

        wrapped = wrap_error(
            operation_name="new_op",
            error=original
        )

        # Should return original since it's already wrapped
        assert wrapped is original


@pytest.mark.unit
class TestErrorMessageFormatting:
    """Test error message formatting"""

    def test_string_representation(self):
        """Test string representation of error"""
        error = ResilienceError(
            operation_name="test_operation",
            original_error=Exception("Original message"),
            error_category=ErrorCategory.NETWORK_TIMEOUT
        )

        error_str = str(error)
        assert "test_operation" in error_str
        assert error.correlation_id in error_str
        assert "Original message" in error_str

    def test_repr_includes_key_info(self):
        """Test repr includes key information"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("Test"),
            error_category=ErrorCategory.API_RATE_LIMIT
        )

        error_repr = repr(error)
        assert "ResilienceError" in error_repr
        assert error.correlation_id in error_repr


@pytest.mark.unit
class TestErrorCategories:
    """Test error category enumeration"""

    def test_all_network_categories_exist(self):
        """Test network-related categories"""
        assert hasattr(ErrorCategory, "NETWORK_TIMEOUT")
        assert hasattr(ErrorCategory, "CONNECTION_ERROR")
        assert hasattr(ErrorCategory, "DNS_ERROR")

    def test_all_api_categories_exist(self):
        """Test API-related categories"""
        assert hasattr(ErrorCategory, "API_RATE_LIMIT")
        assert hasattr(ErrorCategory, "API_QUOTA_EXCEEDED")
        assert hasattr(ErrorCategory, "API_AUTH_FAILURE")
        assert hasattr(ErrorCategory, "API_SERVICE_UNAVAILABLE")

    def test_all_database_categories_exist(self):
        """Test database-related categories"""
        assert hasattr(ErrorCategory, "DATABASE_CONNECTION")
        assert hasattr(ErrorCategory, "DATABASE_TIMEOUT")
        assert hasattr(ErrorCategory, "DATABASE_DEADLOCK")
        assert hasattr(ErrorCategory, "DATABASE_CONSTRAINT_VIOLATION")

    def test_category_values_are_strings(self):
        """Test category values are lowercase strings"""
        assert ErrorCategory.NETWORK_TIMEOUT.value == "network_timeout"
        assert ErrorCategory.API_RATE_LIMIT.value == "api_rate_limit"


@pytest.mark.unit
class TestErrorSeverities:
    """Test error severity enumeration"""

    def test_all_severities_exist(self):
        """Test all severity levels exist"""
        assert hasattr(ErrorSeverity, "CRITICAL")
        assert hasattr(ErrorSeverity, "HIGH")
        assert hasattr(ErrorSeverity, "MEDIUM")
        assert hasattr(ErrorSeverity, "LOW")
        assert hasattr(ErrorSeverity, "INFO")

    def test_severity_values(self):
        """Test severity values are lowercase strings"""
        assert ErrorSeverity.CRITICAL.value == "critical"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.LOW.value == "low"


@pytest.mark.unit
class TestErrorEdgeCases:
    """Test edge cases and special scenarios"""

    def test_none_context(self):
        """Test handling None context"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("Test"),
            context=None
        )

        assert error.context == {}

    def test_empty_operation_name(self):
        """Test empty operation name"""
        error = ResilienceError(
            operation_name="",
            original_error=Exception("Test")
        )

        assert error.operation_name == ""

    def test_very_long_error_message(self):
        """Test handling very long error messages"""
        long_message = "Error: " + "x" * 100000
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception(long_message)
        )

        assert isinstance(error, ResilienceError)

    def test_unicode_in_error(self):
        """Test unicode characters in error"""
        error = ResilienceError(
            operation_name="test_op",
            original_error=Exception("Error: 中文 émojis 🔥")
        )

        error_dict = error.to_dict()
        assert "Error" in str(error_dict)

    def test_nested_exception(self):
        """Test nested exception chains"""
        try:
            try:
                raise ValueError("Inner")
            except ValueError as e:
                raise Exception("Outer") from e
        except Exception as outer:
            error = ResilienceError(
                operation_name="nested_op",
                original_error=outer
            )
            assert isinstance(error, ResilienceError)
            assert error.original_error is outer


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
