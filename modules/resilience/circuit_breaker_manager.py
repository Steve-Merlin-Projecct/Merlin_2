#!/usr/bin/env python3
"""
Circuit Breaker Manager - Prevents cascading failures in distributed systems

Implements the Circuit Breaker pattern to protect services from cascading failures.
When a service fails repeatedly, the circuit "opens" to prevent additional requests,
giving the failing service time to recover.

Circuit States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service failing, requests blocked immediately
- HALF_OPEN: Testing if service recovered, limited requests allowed

Features:
- Automatic state transitions based on failure thresholds
- Per-service circuit breaker configuration
- Manual circuit breaker control
- Circuit state monitoring and metrics
- Graceful degradation support
"""

import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
import functools


logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states following the standard pattern"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures detected, blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerError(Exception):
    """
    Exception raised when circuit breaker is open

    Indicates service is currently unavailable due to repeated failures.
    Clients should implement fallback or degraded functionality.
    """

    def __init__(self, service_name: str, circuit_state: CircuitState,
                last_failure_time: Optional[datetime] = None):
        self.service_name = service_name
        self.circuit_state = circuit_state
        self.last_failure_time = last_failure_time
        self.timestamp = datetime.now()

        message = (
            f"Circuit breaker OPEN for service '{service_name}'. "
            f"Service temporarily unavailable."
        )
        if last_failure_time:
            time_since_failure = (datetime.now() - last_failure_time).total_seconds()
            message += f" Last failure: {time_since_failure:.1f}s ago"

        super().__init__(message)


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for a circuit breaker instance

    Defines thresholds and timing for state transitions.
    """
    # Failure threshold to open circuit
    failure_threshold: int = 5  # Number of failures before opening
    failure_rate_threshold: float = 0.5  # Failure rate (0.0-1.0) to trigger opening
    minimum_calls_for_rate: int = 10  # Minimum calls before checking failure rate

    # Success threshold to close circuit from half-open
    success_threshold: int = 3  # Consecutive successes needed to close

    # Timing configuration
    timeout_duration: float = 60.0  # Seconds before trying half-open from open
    half_open_timeout: float = 30.0  # Seconds to wait in half-open before reopening

    # Half-open state configuration
    half_open_max_calls: int = 3  # Maximum calls allowed in half-open state

    # Monitoring window
    window_duration: float = 60.0  # Seconds for failure rate calculation

    # Manual override
    manual_override: Optional[CircuitState] = None  # Force specific state


@dataclass
class CircuitBreakerMetrics:
    """Metrics tracked by circuit breaker for monitoring and decision-making"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_change_time: datetime = field(default_factory=datetime.now)
    half_open_calls: int = 0
    circuit_opens: int = 0  # Number of times circuit opened
    circuit_closes: int = 0  # Number of times circuit closed


class CircuitBreaker:
    """
    Individual circuit breaker instance for a service

    Tracks service health and manages state transitions automatically.
    """

    def __init__(self, service_name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker for a service

        Args:
            service_name: Unique identifier for the service
            config: Circuit breaker configuration (uses defaults if not provided)
        """
        self.service_name = service_name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self._lock = threading.RLock()  # Thread-safe state management

        logger.info(f"Circuit breaker initialized for '{service_name}' in CLOSED state")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function

        Returns:
            Result of function execution

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original exception from function if circuit allows call
        """
        with self._lock:
            # Check if manual override is set
            if self.config.manual_override:
                self.state = self.config.manual_override
                logger.info(f"Manual override: {self.service_name} set to {self.state.value}")

            current_state = self.state

        # State-specific behavior
        if current_state == CircuitState.OPEN:
            # Check if enough time has passed to try half-open
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                # Circuit still open, reject call
                raise CircuitBreakerError(
                    self.service_name, self.state, self.metrics.last_failure_time
                )

        elif current_state == CircuitState.HALF_OPEN:
            # Check if we've exceeded half-open call limit
            if self.metrics.half_open_calls >= self.config.half_open_max_calls:
                logger.warning(
                    f"Half-open call limit reached for '{self.service_name}', reopening circuit"
                )
                self._transition_to_open()
                raise CircuitBreakerError(self.service_name, self.state, self.metrics.last_failure_time)

        # Attempt to execute the function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure(e)
            raise

    def _on_success(self):
        """Handle successful function execution"""
        with self._lock:
            self.metrics.total_calls += 1
            self.metrics.successful_calls += 1
            self.metrics.consecutive_successes += 1
            self.metrics.consecutive_failures = 0
            self.metrics.last_success_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                self.metrics.half_open_calls += 1

                # Check if we have enough consecutive successes to close
                if self.metrics.consecutive_successes >= self.config.success_threshold:
                    self._transition_to_closed()

    def _on_failure(self, exception: Exception):
        """Handle failed function execution"""
        with self._lock:
            self.metrics.total_calls += 1
            self.metrics.failed_calls += 1
            self.metrics.consecutive_failures += 1
            self.metrics.consecutive_successes = 0
            self.metrics.last_failure_time = datetime.now()

            logger.warning(
                f"Circuit breaker failure in '{self.service_name}': {str(exception)} "
                f"(consecutive: {self.metrics.consecutive_failures})"
            )

            if self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open state reopens the circuit
                logger.warning(f"Failure in half-open state for '{self.service_name}', reopening")
                self._transition_to_open()

            elif self.state == CircuitState.CLOSED:
                # Check if we should open the circuit
                if self._should_open():
                    self._transition_to_open()

    def _should_open(self) -> bool:
        """Determine if circuit should transition to open state"""
        # Check consecutive failure threshold
        if self.metrics.consecutive_failures >= self.config.failure_threshold:
            return True

        # Check failure rate threshold (only after minimum calls)
        if self.metrics.total_calls >= self.config.minimum_calls_for_rate:
            failure_rate = self.metrics.failed_calls / self.metrics.total_calls
            if failure_rate >= self.config.failure_rate_threshold:
                return True

        return False

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try half-open state"""
        if not self.metrics.last_failure_time:
            return True

        time_since_open = (datetime.now() - self.metrics.state_change_time).total_seconds()
        return time_since_open >= self.config.timeout_duration

    def _transition_to_open(self):
        """Transition circuit to OPEN state"""
        with self._lock:
            self.state = CircuitState.OPEN
            self.metrics.state_change_time = datetime.now()
            self.metrics.circuit_opens += 1

            logger.warning(
                f"Circuit breaker OPENED for '{self.service_name}' "
                f"(failures: {self.metrics.consecutive_failures}, "
                f"failure_rate: {self._get_failure_rate():.2%})"
            )

    def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state"""
        with self._lock:
            self.state = CircuitState.HALF_OPEN
            self.metrics.state_change_time = datetime.now()
            self.metrics.half_open_calls = 0
            self.metrics.consecutive_successes = 0

            logger.info(f"Circuit breaker HALF_OPEN for '{self.service_name}', testing recovery")

    def _transition_to_closed(self):
        """Transition circuit to CLOSED state"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.metrics.state_change_time = datetime.now()
            self.metrics.consecutive_failures = 0
            self.metrics.half_open_calls = 0
            self.metrics.circuit_closes += 1

            logger.info(
                f"Circuit breaker CLOSED for '{self.service_name}', service recovered "
                f"(successes: {self.metrics.consecutive_successes})"
            )

    def _get_failure_rate(self) -> float:
        """Calculate current failure rate"""
        if self.metrics.total_calls == 0:
            return 0.0
        return self.metrics.failed_calls / self.metrics.total_calls

    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        with self._lock:
            return self.state

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        with self._lock:
            return {
                "service_name": self.service_name,
                "state": self.state.value,
                "total_calls": self.metrics.total_calls,
                "successful_calls": self.metrics.successful_calls,
                "failed_calls": self.metrics.failed_calls,
                "consecutive_failures": self.metrics.consecutive_failures,
                "consecutive_successes": self.metrics.consecutive_successes,
                "failure_rate": self._get_failure_rate(),
                "last_failure": self.metrics.last_failure_time.isoformat()
                if self.metrics.last_failure_time else None,
                "last_success": self.metrics.last_success_time.isoformat()
                if self.metrics.last_success_time else None,
                "circuit_opens": self.metrics.circuit_opens,
                "circuit_closes": self.metrics.circuit_closes,
                "state_change_time": self.metrics.state_change_time.isoformat(),
            }

    def reset(self):
        """Manually reset circuit breaker to CLOSED state"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.metrics = CircuitBreakerMetrics()
            logger.info(f"Circuit breaker manually reset for '{self.service_name}'")

    def force_open(self):
        """Manually force circuit breaker to OPEN state"""
        with self._lock:
            self._transition_to_open()
            logger.warning(f"Circuit breaker manually opened for '{self.service_name}'")

    def force_closed(self):
        """Manually force circuit breaker to CLOSED state"""
        with self._lock:
            self._transition_to_closed()
            logger.info(f"Circuit breaker manually closed for '{self.service_name}'")


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers across different services

    Provides centralized circuit breaker creation, monitoring, and control.
    """

    def __init__(self):
        """Initialize circuit breaker manager"""
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._configs: Dict[str, CircuitBreakerConfig] = {}
        self._lock = threading.RLock()
        logger.info("Circuit Breaker Manager initialized")

    def get_or_create_breaker(self, service_name: str,
                              config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """
        Get existing circuit breaker or create new one

        Args:
            service_name: Unique service identifier
            config: Optional configuration (uses default if not provided)

        Returns:
            CircuitBreaker instance for the service
        """
        with self._lock:
            if service_name not in self._breakers:
                breaker_config = config or self._configs.get(service_name) or CircuitBreakerConfig()
                self._breakers[service_name] = CircuitBreaker(service_name, breaker_config)
                logger.info(f"Created new circuit breaker for '{service_name}'")

            return self._breakers[service_name]

    def configure_service(self, service_name: str, config: CircuitBreakerConfig):
        """
        Configure circuit breaker for a service

        If breaker already exists, configuration takes effect on next reset.
        """
        with self._lock:
            self._configs[service_name] = config
            logger.info(f"Circuit breaker configured for '{service_name}'")

    def execute_with_breaker(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            service_name: Service identifier
            func: Function to execute
            *args, **kwargs: Arguments for function

        Returns:
            Result of function execution

        Raises:
            CircuitBreakerError: If circuit is open
        """
        breaker = self.get_or_create_breaker(service_name)
        return breaker.call(func, *args, **kwargs)

    def get_all_states(self) -> Dict[str, CircuitState]:
        """Get states of all circuit breakers"""
        with self._lock:
            return {name: breaker.get_state() for name, breaker in self._breakers.items()}

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers"""
        with self._lock:
            return {name: breaker.get_metrics() for name, breaker in self._breakers.items()}

    def reset_breaker(self, service_name: str):
        """Manually reset a circuit breaker"""
        with self._lock:
            if service_name in self._breakers:
                self._breakers[service_name].reset()

    def reset_all(self):
        """Reset all circuit breakers"""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()
            logger.info("All circuit breakers reset")


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()


def with_circuit_breaker(service_name: str, config: Optional[CircuitBreakerConfig] = None) -> Callable:
    """
    Decorator to protect function with circuit breaker

    Usage:
        @with_circuit_breaker("external_api")
        def call_external_api(data):
            # This call is protected by circuit breaker
            return requests.post(api_url, json=data)

    Args:
        service_name: Unique service identifier
        config: Optional circuit breaker configuration

    Returns:
        Decorated function with circuit breaker protection
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if config:
                circuit_breaker_manager.configure_service(service_name, config)
            return circuit_breaker_manager.execute_with_breaker(service_name, func, *args, **kwargs)
        return wrapper
    return decorator


def get_circuit_state(service_name: str) -> Optional[CircuitState]:
    """Get current state of a circuit breaker"""
    breaker = circuit_breaker_manager._breakers.get(service_name)
    return breaker.get_state() if breaker else None


def get_all_circuit_states() -> Dict[str, CircuitState]:
    """Get states of all circuit breakers"""
    return circuit_breaker_manager.get_all_states()


def configure_circuit_breaker(service_name: str, **kwargs):
    """
    Configure circuit breaker for a service

    Args:
        service_name: Service identifier
        **kwargs: Configuration parameters (failure_threshold, timeout_duration, etc.)
    """
    config = CircuitBreakerConfig(**kwargs)
    circuit_breaker_manager.configure_service(service_name, config)


# Example usage
if __name__ == "__main__":
    import time

    print("Circuit Breaker Manager Test")
    print("=" * 60)

    # Configure circuit breaker for test service
    configure_circuit_breaker(
        "test_service",
        failure_threshold=3,
        timeout_duration=5.0,
        success_threshold=2
    )

    # Test function that fails
    call_count = [0]

    @with_circuit_breaker("test_service")
    def unreliable_service():
        call_count[0] += 1
        print(f"  Call #{call_count[0]}")

        # Fail first 5 calls, then succeed
        if call_count[0] <= 5:
            raise Exception("Service unavailable")
        return "success"

    # Test circuit breaker behavior
    print("\n1. Testing failure detection and circuit opening:")
    for i in range(7):
        try:
            result = unreliable_service()
            print(f"  ✓ Call {i + 1}: {result}")
        except CircuitBreakerError as e:
            print(f"  ⚠ Call {i + 1}: Circuit OPEN - {e}")
        except Exception as e:
            print(f"  ✗ Call {i + 1}: Failed - {e}")

        time.sleep(0.5)

    print("\n2. Waiting for circuit to attempt half-open...")
    time.sleep(5)

    print("\n3. Testing recovery through half-open state:")
    for i in range(5):
        try:
            result = unreliable_service()
            print(f"  ✓ Call {i + 1}: {result}")
        except CircuitBreakerError as e:
            print(f"  ⚠ Call {i + 1}: Circuit OPEN - {e}")
        except Exception as e:
            print(f"  ✗ Call {i + 1}: Failed - {e}")

        time.sleep(0.5)

    print("\n4. Circuit breaker metrics:")
    metrics = circuit_breaker_manager.get_all_metrics()
    for service, stats in metrics.items():
        print(f"\n  Service: {service}")
        print(f"  State: {stats['state']}")
        print(f"  Total calls: {stats['total_calls']}")
        print(f"  Successful: {stats['successful_calls']}")
        print(f"  Failed: {stats['failed_calls']}")
        print(f"  Failure rate: {stats['failure_rate']:.1%}")
        print(f"  Circuit opens: {stats['circuit_opens']}")
        print(f"  Circuit closes: {stats['circuit_closes']}")

    print("\n✅ Circuit Breaker Manager test complete")
