"""
Unit tests for Circuit Breaker Manager

Tests circuit breaker state machine, failure detection, recovery,
concurrent access, and configuration.
"""

import pytest
import time
import threading
from modules.resilience.circuit_breaker_manager import (
    CircuitBreakerManager, CircuitBreaker, CircuitBreakerConfig,
    CircuitState, CircuitBreakerError, with_circuit_breaker,
    get_circuit_state, configure_circuit_breaker
)


@pytest.mark.unit
class TestCircuitBreakerStateMachine:
    """Test circuit breaker state transitions"""

    def test_initial_state_is_closed(self, circuit_breaker):
        """Test circuit starts in CLOSED state"""
        assert circuit_breaker.get_state() == CircuitState.CLOSED

    def test_closed_to_open_on_failures(self, circuit_breaker, failing_operation):
        """Test circuit opens after failure threshold"""
        # Configure with low threshold
        circuit_breaker.config.failure_threshold = 3

        # Trigger failures
        for _ in range(3):
            try:
                circuit_breaker.call(failing_operation)
            except Exception:
                pass

        assert circuit_breaker.get_state() == CircuitState.OPEN

    def test_open_rejects_calls(self, circuit_breaker, fast_operation, failing_operation):
        """Test OPEN circuit rejects calls immediately"""
        # Open circuit properly by triggering failures
        circuit_breaker.config.failure_threshold = 2
        for _ in range(2):
            try:
                circuit_breaker.call(failing_operation)
            except Exception:
                pass

        # Circuit should be open now
        assert circuit_breaker.get_state() == CircuitState.OPEN

        # Next call should be rejected
        with pytest.raises(CircuitBreakerError) as exc_info:
            circuit_breaker.call(fast_operation)

        assert "OPEN" in str(exc_info.value)

    def test_open_to_half_open_after_timeout(self, circuit_breaker, failing_operation):
        """Test circuit transitions to HALF_OPEN after timeout"""
        circuit_breaker.config.failure_threshold = 2
        circuit_breaker.config.timeout_duration = 1.0

        # Open the circuit
        for _ in range(2):
            try:
                circuit_breaker.call(failing_operation)
            except Exception:
                pass

        assert circuit_breaker.get_state() == CircuitState.OPEN

        # Wait for timeout
        time.sleep(1.1)

        # Next call should transition to HALF_OPEN
        # Use a successful operation to allow transition
        def success_op():
            return "success"

        try:
            circuit_breaker.call(success_op)
        except:
            pass

        # Should be in HALF_OPEN now
        assert circuit_breaker.get_state() == CircuitState.HALF_OPEN

    def test_half_open_to_closed_on_success(self, circuit_breaker):
        """Test HALF_OPEN closes after success threshold"""
        circuit_breaker.config.success_threshold = 2

        # Force to HALF_OPEN
        circuit_breaker._transition_to_half_open()

        # Successful calls
        def success_op():
            return "success"

        for _ in range(2):
            circuit_breaker.call(success_op)

        assert circuit_breaker.get_state() == CircuitState.CLOSED

    def test_half_open_to_open_on_failure(self, circuit_breaker, failing_operation):
        """Test HALF_OPEN reopens on any failure"""
        circuit_breaker._transition_to_half_open()

        try:
            circuit_breaker.call(failing_operation)
        except Exception:
            pass

        assert circuit_breaker.get_state() == CircuitState.OPEN


@pytest.mark.unit
class TestCircuitBreakerMetrics:
    """Test circuit breaker metrics tracking"""

    def test_metrics_track_total_calls(self, circuit_breaker, fast_operation):
        """Test total calls are tracked"""
        for _ in range(5):
            circuit_breaker.call(fast_operation)

        metrics = circuit_breaker.get_metrics()
        assert metrics["total_calls"] == 5

    def test_metrics_track_successful_calls(self, circuit_breaker, fast_operation):
        """Test successful calls counted"""
        for _ in range(3):
            circuit_breaker.call(fast_operation)

        metrics = circuit_breaker.get_metrics()
        assert metrics["successful_calls"] == 3

    def test_metrics_track_failed_calls(self, circuit_breaker, failing_operation):
        """Test failed calls counted"""
        # Configure higher threshold to allow all 3 calls
        circuit_breaker.config.failure_threshold = 10

        for _ in range(3):
            try:
                circuit_breaker.call(failing_operation)
            except Exception:
                pass

        metrics = circuit_breaker.get_metrics()
        assert metrics["failed_calls"] == 3

    def test_metrics_track_consecutive_failures(self, circuit_breaker, failing_operation):
        """Test consecutive failures tracked"""
        # Configure higher threshold to allow all 4 calls
        circuit_breaker.config.failure_threshold = 10

        for _ in range(4):
            try:
                circuit_breaker.call(failing_operation)
            except Exception:
                pass

        metrics = circuit_breaker.get_metrics()
        assert metrics["consecutive_failures"] >= 3

    def test_metrics_track_circuit_opens(self, circuit_breaker, failing_operation):
        """Test circuit opens are counted"""
        circuit_breaker.config.failure_threshold = 2

        # Open circuit
        for _ in range(2):
            try:
                circuit_breaker.call(failing_operation)
            except Exception:
                pass

        metrics = circuit_breaker.get_metrics()
        assert metrics["circuit_opens"] >= 1

    def test_failure_rate_calculation(self, circuit_breaker):
        """Test failure rate is calculated correctly"""
        # 3 successes, 2 failures = 40% failure rate
        for _ in range(3):
            circuit_breaker.call(lambda: "success")

        for _ in range(2):
            try:
                circuit_breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
            except Exception:
                pass

        metrics = circuit_breaker.get_metrics()
        assert 0.35 <= metrics["failure_rate"] <= 0.45  # ~40% ±5%


@pytest.mark.unit
class TestCircuitBreakerConfiguration:
    """Test circuit breaker configuration"""

    def test_custom_failure_threshold(self):
        """Test custom failure threshold configuration"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            failure_rate_threshold=1.0  # Test consecutive failures only
        )
        cb = CircuitBreaker("test", config)

        # Should take 5 failures to open
        for i in range(4):
            try:
                cb.call(lambda: (_ for _ in ()).throw(Exception("fail")))
            except Exception:
                pass

        assert cb.get_state() == CircuitState.CLOSED

        # 5th failure should open
        try:
            cb.call(lambda: (_ for _ in ()).throw(Exception("fail")))
        except Exception:
            pass

        assert cb.get_state() == CircuitState.OPEN

    def test_custom_timeout_duration(self):
        """Test custom timeout duration"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            timeout_duration=0.5
        )
        cb = CircuitBreaker("test", config)

        # Open circuit
        try:
            cb.call(lambda: (_ for _ in ()).throw(Exception("fail")))
        except Exception:
            pass

        assert cb.get_state() == CircuitState.OPEN

        # Short wait should allow transition
        time.sleep(0.6)

        try:
            cb.call(lambda: "success")
        except:
            pass

        assert cb.get_state() == CircuitState.HALF_OPEN

    def test_custom_success_threshold(self):
        """Test custom success threshold"""
        config = CircuitBreakerConfig(success_threshold=3)
        cb = CircuitBreaker("test", config)

        cb._transition_to_half_open()

        # Should need 3 successes to close
        for _ in range(2):
            cb.call(lambda: "success")

        assert cb.get_state() == CircuitState.HALF_OPEN

        cb.call(lambda: "success")
        assert cb.get_state() == CircuitState.CLOSED


@pytest.mark.unit
class TestCircuitBreakerManager:
    """Test circuit breaker manager functionality"""

    def test_manager_creates_circuit_breakers(self, circuit_breaker_manager):
        """Test manager creates and tracks circuit breakers"""
        cb = circuit_breaker_manager.get_or_create_breaker("service1")
        assert cb is not None
        assert cb.service_name == "service1"

    def test_manager_reuses_existing_breakers(self, circuit_breaker_manager):
        """Test manager reuses existing circuit breakers"""
        cb1 = circuit_breaker_manager.get_or_create_breaker("service1")
        cb2 = circuit_breaker_manager.get_or_create_breaker("service1")
        assert cb1 is cb2

    def test_manager_tracks_multiple_services(self, circuit_breaker_manager):
        """Test manager tracks multiple independent services"""
        cb1 = circuit_breaker_manager.get_or_create_breaker("service1")
        cb2 = circuit_breaker_manager.get_or_create_breaker("service2")

        assert cb1 is not cb2
        assert cb1.service_name == "service1"
        assert cb2.service_name == "service2"

    def test_manager_get_all_states(self, circuit_breaker_manager):
        """Test manager can retrieve all circuit states"""
        circuit_breaker_manager.get_or_create_breaker("service1")
        circuit_breaker_manager.get_or_create_breaker("service2")

        states = circuit_breaker_manager.get_all_states()
        assert "service1" in states
        assert "service2" in states

    def test_manager_reset_breaker(self, circuit_breaker_manager):
        """Test manager can reset individual circuit breakers"""
        cb = circuit_breaker_manager.get_or_create_breaker("service1")

        # Open the circuit
        cb._transition_to_open()
        assert cb.get_state() == CircuitState.OPEN

        # Reset
        circuit_breaker_manager.reset_breaker("service1")
        assert cb.get_state() == CircuitState.CLOSED

    def test_manager_reset_all(self, circuit_breaker_manager):
        """Test manager can reset all circuit breakers"""
        cb1 = circuit_breaker_manager.get_or_create_breaker("service1")
        cb2 = circuit_breaker_manager.get_or_create_breaker("service2")

        cb1._transition_to_open()
        cb2._transition_to_open()

        circuit_breaker_manager.reset_all()

        assert cb1.get_state() == CircuitState.CLOSED
        assert cb2.get_state() == CircuitState.CLOSED


@pytest.mark.unit
class TestCircuitBreakerDecorator:
    """Test @with_circuit_breaker decorator"""

    def test_decorator_creates_circuit_breaker(self):
        """Test decorator creates circuit breaker"""
        @with_circuit_breaker("test_service")
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"

        # Verify circuit breaker was created
        state = get_circuit_state("test_service")
        assert state == CircuitState.CLOSED

    def test_decorator_protects_function(self):
        """Test decorator protects function with circuit breaker"""
        config = CircuitBreakerConfig(failure_threshold=2)

        @with_circuit_breaker("failing_service", config=config)
        def failing_func():
            raise Exception("Service error")

        # Trigger failures to open circuit
        for _ in range(2):
            try:
                failing_func()
            except Exception:
                pass

        # Circuit should be open, blocking calls
        with pytest.raises(CircuitBreakerError):
            failing_func()

    def test_decorator_preserves_function_metadata(self):
        """Test decorator preserves function name and docstring"""
        @with_circuit_breaker("documented_service")
        def documented_func():
            """This is documentation"""
            return "result"

        assert documented_func.__name__ == "documented_func"
        assert "documentation" in documented_func.__doc__


@pytest.mark.unit
class TestCircuitBreakerManualControl:
    """Test manual circuit breaker control"""

    def test_manual_reset(self, circuit_breaker):
        """Test manual reset to CLOSED"""
        circuit_breaker._transition_to_open()
        assert circuit_breaker.get_state() == CircuitState.OPEN

        circuit_breaker.reset()
        assert circuit_breaker.get_state() == CircuitState.CLOSED

    def test_force_open(self, circuit_breaker):
        """Test forcing circuit to OPEN state"""
        assert circuit_breaker.get_state() == CircuitState.CLOSED

        circuit_breaker.force_open()
        assert circuit_breaker.get_state() == CircuitState.OPEN

    def test_force_closed(self, circuit_breaker):
        """Test forcing circuit to CLOSED state"""
        circuit_breaker._transition_to_open()
        assert circuit_breaker.get_state() == CircuitState.OPEN

        circuit_breaker.force_closed()
        assert circuit_breaker.get_state() == CircuitState.CLOSED


@pytest.mark.unit
@pytest.mark.slow
class TestCircuitBreakerConcurrency:
    """Test circuit breaker under concurrent access"""

    def test_concurrent_access_thread_safe(self, circuit_breaker):
        """Test circuit breaker is thread-safe"""
        results = []

        def worker():
            try:
                result = circuit_breaker.call(lambda: "success")
                results.append(("success", result))
            except Exception as e:
                results.append(("error", str(e)))

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All should succeed
        successes = [r for r in results if r[0] == "success"]
        assert len(successes) == 10

    def test_concurrent_failure_detection(self):
        """Test concurrent failures properly trigger circuit"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            failure_rate_threshold=1.0  # Test consecutive failures only
        )
        cb = CircuitBreaker("concurrent_test", config)

        results = []

        def worker():
            try:
                cb.call(lambda: (_ for _ in ()).throw(Exception("fail")))
                results.append("success")
            except CircuitBreakerError:
                results.append("circuit_open")
            except Exception:
                results.append("operation_failed")

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Should have failures + circuit opens
        assert "operation_failed" in results
        # After threshold, should see circuit_open
        if len([r for r in results if r == "operation_failed"]) >= 5:
            assert "circuit_open" in results


@pytest.mark.unit
class TestCircuitBreakerError:
    """Test CircuitBreakerError exception"""

    def test_error_contains_service_name(self, circuit_breaker):
        """Test error includes service name"""
        circuit_breaker._transition_to_open()

        try:
            circuit_breaker.call(lambda: "test")
        except CircuitBreakerError as e:
            assert e.service_name == "test_service"
            assert e.circuit_state == CircuitState.OPEN

    def test_error_includes_last_failure_time(self, circuit_breaker, failing_operation):
        """Test error includes last failure timestamp"""
        circuit_breaker.config.failure_threshold = 1

        try:
            circuit_breaker.call(failing_operation)
        except Exception:
            pass

        try:
            circuit_breaker.call(lambda: "test")
        except CircuitBreakerError as e:
            assert e.last_failure_time is not None


@pytest.mark.unit
class TestCircuitBreakerEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_service_name(self):
        """Test circuit breaker with empty service name"""
        cb = CircuitBreaker("")
        result = cb.call(lambda: "success")
        assert result == "success"

    def test_very_high_failure_threshold(self):
        """Test with very high failure threshold"""
        config = CircuitBreakerConfig(
            failure_threshold=100,
            failure_rate_threshold=1.0,  # Test consecutive failures only
            minimum_calls_for_rate=200  # Require more calls before rate check
        )
        cb = CircuitBreaker("test", config)

        # Many failures shouldn't open circuit
        for _ in range(50):
            try:
                cb.call(lambda: (_ for _ in ()).throw(Exception("fail")))
            except Exception:
                pass

        assert cb.get_state() == CircuitState.CLOSED

    def test_zero_timeout_duration(self):
        """Test with zero timeout duration"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            timeout_duration=0.0
        )
        cb = CircuitBreaker("test", config)

        # Open circuit
        try:
            cb.call(lambda: (_ for _ in ()).throw(Exception("fail")))
        except Exception:
            pass

        # Should immediately allow half-open
        assert cb._should_attempt_reset() is True

    def test_half_open_call_limit(self):
        """Test half-open state enforces call limit"""
        config = CircuitBreakerConfig(half_open_max_calls=2)
        cb = CircuitBreaker("test", config)

        cb._transition_to_half_open()

        # First 2 calls should work
        cb.call(lambda: "success")
        cb.call(lambda: "success")

        # 3rd call should be rejected
        with pytest.raises(CircuitBreakerError):
            cb.call(lambda: "success")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
