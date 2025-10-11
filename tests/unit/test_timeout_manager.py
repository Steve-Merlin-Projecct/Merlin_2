"""
Unit tests for Timeout Manager

Tests timeout enforcement, configuration, statistics tracking,
and edge cases for the timeout protection system.
"""

import pytest
import time
import threading
from modules.resilience.timeout_manager import (
    TimeoutManager, TimeoutError, OperationType,
    with_timeout, timeout_block, configure_timeout, get_timeout_stats
)


@pytest.mark.unit
class TestTimeoutEnforcement:
    """Test basic timeout enforcement functionality"""

    def test_timeout_triggers_on_slow_operation(self, slow_operation):
        """Test that timeout is enforced when operation exceeds limit"""
        @with_timeout(timeout=1.0, operation_name="slow_test")
        def wrapped_slow_op():
            slow_operation(duration=2.0)

        with pytest.raises(TimeoutError) as exc_info:
            wrapped_slow_op()

        assert "slow_test" in str(exc_info.value)
        assert "1.0" in str(exc_info.value)

    def test_timeout_not_triggered_on_fast_operation(self, fast_operation):
        """Test that fast operations complete without timeout"""
        @with_timeout(timeout=2.0, operation_name="fast_test")
        def wrapped_fast_op():
            return fast_operation()

        result = wrapped_fast_op()
        assert result == "completed"

    def test_timeout_with_operation_type(self):
        """Test timeout using predefined operation types"""
        @with_timeout(OperationType.DATABASE_QUERY, operation_name="db_query")
        def quick_query():
            time.sleep(0.1)
            return "query_result"

        result = quick_query()
        assert result == "query_result"

    def test_timeout_accuracy(self):
        """Test that timeout triggers within acceptable tolerance (±10%)"""
        timeout_value = 0.5

        @with_timeout(timeout=timeout_value, operation_name="accuracy_test")
        def timed_operation():
            time.sleep(1.0)

        start = time.time()
        with pytest.raises(TimeoutError):
            timed_operation()
        elapsed = time.time() - start

        # Allow ±10% tolerance
        assert timeout_value * 0.9 <= elapsed <= timeout_value * 1.1


@pytest.mark.unit
class TestTimeoutConfiguration:
    """Test timeout configuration and customization"""

    def test_default_timeout_for_operation_type(self, timeout_manager):
        """Test that default timeouts are applied correctly"""
        from modules.resilience.timeout_manager import timeout_config

        # AI API should have 60s default
        ai_timeout = timeout_config.get_timeout(OperationType.AI_API_CALL)
        assert ai_timeout == 60.0

        # Database query should have 30s default
        db_timeout = timeout_config.get_timeout(OperationType.DATABASE_QUERY)
        assert db_timeout == 30.0

    def test_custom_timeout_override(self):
        """Test custom timeout value overrides default"""
        @with_timeout(timeout=3.0, operation_name="custom_timeout_test")
        def custom_op():
            time.sleep(0.1)
            return "completed"

        result = custom_op()
        assert result == "completed"

    def test_timeout_configuration_api(self):
        """Test configure_timeout API"""
        configure_timeout(
            operation_type=OperationType.GENERIC,
            timeout=10.0
        )

        from modules.resilience.timeout_manager import timeout_config
        new_timeout = timeout_config.get_timeout(OperationType.GENERIC)
        assert new_timeout == 10.0

    def test_per_operation_name_timeout(self):
        """Test setting timeout for specific operation name"""
        configure_timeout(
            operation_name="special_operation",
            timeout=15.0
        )

        from modules.resilience.timeout_manager import timeout_config
        timeout = timeout_config.get_timeout(
            OperationType.GENERIC,
            operation_name="special_operation"
        )
        assert timeout == 15.0


@pytest.mark.unit
class TestTimeoutContextManager:
    """Test timeout context manager functionality"""

    def test_context_manager_success(self):
        """Test timeout context manager with successful operation"""
        with timeout_block(2.0, "context_test"):
            time.sleep(0.1)
            result = "success"

        assert result == "success"

    def test_context_manager_timeout(self):
        """Test timeout context manager triggers on timeout"""
        with pytest.raises(TimeoutError) as exc_info:
            with timeout_block(0.5, "context_timeout_test"):
                time.sleep(1.0)

        assert "context_timeout_test" in str(exc_info.value)

    def test_context_manager_with_exception(self):
        """Test context manager preserves non-timeout exceptions"""
        with pytest.raises(ValueError):
            with timeout_block(2.0, "exception_test"):
                raise ValueError("Not a timeout")


@pytest.mark.unit
class TestTimeoutStatistics:
    """Test timeout event tracking and statistics"""

    def test_timeout_events_tracked(self):
        """Test that timeout events are recorded"""
        @with_timeout(timeout=0.5, operation_name="stats_test")
        def slow_op():
            time.sleep(1.0)

        # Trigger a timeout
        try:
            slow_op()
        except TimeoutError:
            pass

        stats = get_timeout_stats()
        assert stats["total_timeouts"] > 0
        assert "stats_test" in stats["operations"]

    def test_multiple_timeout_tracking(self):
        """Test tracking multiple timeout events"""
        @with_timeout(timeout=0.3, operation_name="multi_timeout_test")
        def failing_op():
            time.sleep(1.0)

        # Trigger multiple timeouts
        for _ in range(3):
            try:
                failing_op()
            except TimeoutError:
                pass

        stats = get_timeout_stats()
        assert stats["total_timeouts"] >= 3


@pytest.mark.unit
class TestTimeoutEdgeCases:
    """Test edge cases and error conditions"""

    def test_zero_timeout(self):
        """Test behavior with zero timeout"""
        @with_timeout(timeout=0.0, operation_name="zero_timeout")
        def instant_timeout():
            return "should not reach"

        # Zero timeout should immediately timeout
        with pytest.raises(TimeoutError):
            instant_timeout()

    def test_very_long_timeout(self):
        """Test that very long timeouts don't interfere with fast operations"""
        @with_timeout(timeout=3600.0, operation_name="long_timeout")
        def fast_op():
            return "completed"

        result = fast_op()
        assert result == "completed"

    def test_timeout_with_nested_operations(self):
        """Test timeout behavior with nested function calls"""
        @with_timeout(timeout=2.0, operation_name="outer")
        def outer_op():
            @with_timeout(timeout=1.0, operation_name="inner")
            def inner_op():
                time.sleep(0.5)
                return "inner_complete"

            return inner_op()

        result = outer_op()
        assert result == "inner_complete"

    def test_timeout_on_already_failed_operation(self):
        """Test timeout doesn't mask other exceptions"""
        @with_timeout(timeout=2.0, operation_name="failing_op")
        def failing_op():
            raise ValueError("Operation failed before timeout")

        with pytest.raises(ValueError) as exc_info:
            failing_op()

        assert "Operation failed before timeout" in str(exc_info.value)

    def test_timeout_cleanup_no_resource_leak(self):
        """Test that timeout doesn't leak resources"""
        @with_timeout(timeout=0.5, operation_name="cleanup_test")
        def leaky_op():
            time.sleep(1.0)

        # Run multiple times to detect resource leaks
        for _ in range(10):
            try:
                leaky_op()
            except TimeoutError:
                pass

        # If we get here without hanging, cleanup is working


@pytest.mark.unit
class TestTimeoutDecorator:
    """Test decorator-specific functionality"""

    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring"""
        @with_timeout(timeout=2.0)
        def documented_function():
            """This is a documented function"""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert "documented function" in documented_function.__doc__

    def test_decorator_with_args_and_kwargs(self):
        """Test decorator works with function arguments"""
        @with_timeout(timeout=2.0, operation_name="args_test")
        def function_with_args(a, b, c=10):
            return a + b + c

        result = function_with_args(1, 2, c=3)
        assert result == 6

    def test_decorator_returns_value(self):
        """Test that decorated function returns values correctly"""
        @with_timeout(timeout=2.0, operation_name="return_test")
        def returning_function():
            return {"status": "success", "value": 42}

        result = returning_function()
        assert result["status"] == "success"
        assert result["value"] == 42


@pytest.mark.unit
@pytest.mark.slow
class TestTimeoutConcurrency:
    """Test timeout behavior under concurrent execution"""

    def test_concurrent_timeout_tracking(self):
        """Test that multiple threads can timeout independently"""
        @with_timeout(timeout=0.5, operation_name="concurrent_test")
        def concurrent_op():
            time.sleep(1.0)

        results = []

        def worker():
            try:
                concurrent_op()
                results.append("success")
            except TimeoutError:
                results.append("timeout")

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All should timeout
        assert results.count("timeout") == 5

    def test_timeout_thread_safety(self):
        """Test timeout manager is thread-safe"""
        @with_timeout(timeout=1.0, operation_name="thread_safety")
        def thread_safe_op(duration):
            time.sleep(duration)
            return "completed"

        results = []

        def worker(duration):
            try:
                result = thread_safe_op(duration)
                results.append(("success", result))
            except TimeoutError:
                results.append(("timeout", None))

        threads = []
        for i in range(10):
            # Mix of fast and slow operations
            duration = 0.1 if i % 2 == 0 else 2.0
            thread = threading.Thread(target=worker, args=(duration,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have mix of successes and timeouts
        successes = [r for r in results if r[0] == "success"]
        timeouts = [r for r in results if r[0] == "timeout"]

        assert len(successes) > 0
        assert len(timeouts) > 0


@pytest.mark.unit
class TestTimeoutErrorClass:
    """Test TimeoutError exception class"""

    def test_timeout_error_contains_operation_name(self):
        """Test TimeoutError includes operation name"""
        @with_timeout(timeout=0.5, operation_name="error_test")
        def timeout_op():
            time.sleep(1.0)

        try:
            timeout_op()
        except TimeoutError as e:
            assert e.operation_name == "error_test"
            assert e.timeout_seconds == 0.5
            assert e.context is not None

    def test_timeout_error_serialization(self):
        """Test TimeoutError can be serialized"""
        @with_timeout(timeout=0.5, operation_name="serialize_test")
        def timeout_op():
            time.sleep(1.0)

        try:
            timeout_op()
        except TimeoutError as e:
            error_dict = e.to_dict()
            assert error_dict["error_type"] == "timeout"
            assert error_dict["operation_name"] == "serialize_test"
            assert error_dict["timeout_seconds"] == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
