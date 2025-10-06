#!/usr/bin/env python3
"""
Retry Strategy Manager - Advanced Retry Logic for Step 2.3

Provides configurable retry strategies with intelligent backoff algorithms,
circuit breaker patterns, and adaptive retry policies based on failure patterns.

Features:
- Exponential backoff with jitter
- Circuit breaker pattern for cascading failure prevention
- Adaptive retry policies based on historical success rates
- Failure pattern recognition and strategy adjustment
- Comprehensive retry metrics and analytics
"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures detected, operations blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryMetrics:
    """Metrics for retry operations"""

    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    total_delay_time: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    circuit_state: CircuitState = CircuitState.CLOSED
    circuit_failure_count: int = 0
    circuit_last_failure: Optional[datetime] = None


class AdaptiveRetryStrategy:
    """
    Adaptive retry strategy that adjusts based on historical performance
    """

    def __init__(
        self,
        operation_name: str,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        max_attempts: int = 3,
        exponential_base: float = 2.0,
        jitter_factor: float = 0.1,
    ):
        self.operation_name = operation_name
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_attempts = max_attempts
        self.exponential_base = exponential_base
        self.jitter_factor = jitter_factor

        # Circuit breaker settings
        self.circuit_failure_threshold = 5
        self.circuit_timeout = 60.0  # seconds
        self.circuit_half_open_max_calls = 3

        # Metrics tracking
        self.metrics = RetryMetrics()
        self.recent_failures = []  # Track recent failures for pattern analysis

        self.logger = logging.getLogger(f"{__name__}.{operation_name}")

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """
        Determine if operation should be retried based on current state

        Args:
            attempt: Current attempt number (1-based)
            error: Exception that occurred

        Returns:
            bool: True if retry should be attempted
        """
        # Check circuit breaker state
        if self.metrics.circuit_state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.metrics.circuit_state = CircuitState.HALF_OPEN
                self.logger.info(f"Circuit breaker for {self.operation_name} moving to HALF_OPEN")
            else:
                self.logger.warning(f"Circuit breaker for {self.operation_name} is OPEN - blocking retry")
                return False

        # Check attempt limits
        if attempt >= self.max_attempts:
            return False

        # Check if error type is retryable
        if not self._is_retryable_error(error):
            return False

        return True

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay with exponential backoff and jitter

        Args:
            attempt: Current attempt number (1-based)

        Returns:
            float: Delay in seconds
        """
        # Calculate exponential backoff
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))

        # Apply maximum delay cap
        delay = min(delay, self.max_delay)

        # Add jitter to prevent thundering herd
        jitter = delay * self.jitter_factor * (random.random() * 2 - 1)  # ±jitter_factor
        delay = max(0, delay + jitter)

        return delay

    def record_attempt(self, success: bool, error: Optional[Exception] = None):
        """
        Record the result of an operation attempt

        Args:
            success: Whether the operation succeeded
            error: Exception if operation failed
        """
        now = datetime.now()
        self.metrics.total_attempts += 1

        if success:
            self.metrics.successful_attempts += 1
            self.metrics.last_success = now
            self._handle_success()
        else:
            self.metrics.failed_attempts += 1
            self.metrics.last_failure = now
            self._handle_failure(error)

    def _handle_success(self):
        """Handle successful operation - reset circuit breaker if needed"""
        if self.metrics.circuit_state == CircuitState.HALF_OPEN:
            self.metrics.circuit_state = CircuitState.CLOSED
            self.metrics.circuit_failure_count = 0
            self.logger.info(f"Circuit breaker for {self.operation_name} reset to CLOSED")

        # Clear recent failures on success
        self.recent_failures.clear()

    def _handle_failure(self, error: Optional[Exception]):
        """Handle failed operation - update circuit breaker state"""
        now = datetime.now()
        self.recent_failures.append({"timestamp": now, "error": str(error) if error else "Unknown error"})

        # Keep only recent failures (last 5 minutes)
        cutoff = now - timedelta(minutes=5)
        self.recent_failures = [f for f in self.recent_failures if f["timestamp"] > cutoff]

        # Update circuit breaker
        if self.metrics.circuit_state == CircuitState.CLOSED:
            self.metrics.circuit_failure_count += 1

            if self.metrics.circuit_failure_count >= self.circuit_failure_threshold:
                self.metrics.circuit_state = CircuitState.OPEN
                self.metrics.circuit_last_failure = now
                self.logger.warning(f"Circuit breaker for {self.operation_name} opened due to failures")

        elif self.metrics.circuit_state == CircuitState.HALF_OPEN:
            # Failure in half-open state - return to open
            self.metrics.circuit_state = CircuitState.OPEN
            self.metrics.circuit_last_failure = now
            self.logger.warning(f"Circuit breaker for {self.operation_name} returned to OPEN")

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if not self.metrics.circuit_last_failure:
            return True

        time_since_failure = (datetime.now() - self.metrics.circuit_last_failure).total_seconds()
        return time_since_failure >= self.circuit_timeout

    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable

        Args:
            error: Exception to check

        Returns:
            bool: True if error is retryable
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()

        # Non-retryable errors
        non_retryable_patterns = [
            "authentication",
            "authorization",
            "permission denied",
            "invalid credentials",
            "bad request",
            "not found",
            "malformed",
            "syntax error",
        ]

        for pattern in non_retryable_patterns:
            if pattern in error_str:
                return False

        # Non-retryable error types
        non_retryable_types = ["syntaxerror", "typeerror", "valueerror", "attributeerror"]

        if error_type in non_retryable_types:
            return False

        return True

    def get_success_rate(self) -> float:
        """Calculate current success rate"""
        if self.metrics.total_attempts == 0:
            return 0.0
        return self.metrics.successful_attempts / self.metrics.total_attempts

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        return {
            "operation_name": self.operation_name,
            "total_attempts": self.metrics.total_attempts,
            "successful_attempts": self.metrics.successful_attempts,
            "failed_attempts": self.metrics.failed_attempts,
            "success_rate": self.get_success_rate(),
            "circuit_state": self.metrics.circuit_state.value,
            "circuit_failure_count": self.metrics.circuit_failure_count,
            "last_success": self.metrics.last_success.isoformat() if self.metrics.last_success else None,
            "last_failure": self.metrics.last_failure.isoformat() if self.metrics.last_failure else None,
            "recent_failure_count": len(self.recent_failures),
            "adaptive_settings": {
                "base_delay": self.base_delay,
                "max_delay": self.max_delay,
                "max_attempts": self.max_attempts,
                "exponential_base": self.exponential_base,
                "jitter_factor": self.jitter_factor,
            },
        }


class RetryStrategyManager:
    """
    Central manager for retry strategies across the application

    Provides strategy registration, execution, and analytics for retry operations.
    Maintains adaptive strategies that improve based on historical performance.
    """

    def __init__(self):
        """Initialize the retry strategy manager"""
        self.strategies: Dict[str, AdaptiveRetryStrategy] = {}
        self.logger = logging.getLogger(__name__)

        # Register default strategies for common operations
        self._register_default_strategies()

    def _register_default_strategies(self):
        """Register default retry strategies for common operations"""

        # Database operations - moderate retry with longer delays
        self.register_strategy(
            "database_operation", base_delay=2.0, max_delay=30.0, max_attempts=4, exponential_base=1.8
        )

        # API calls - conservative retry with respectful delays
        self.register_strategy("api_call", base_delay=5.0, max_delay=120.0, max_attempts=3, exponential_base=2.0)

        # Document generation - limited retry with quick recovery
        self.register_strategy(
            "document_generation", base_delay=1.0, max_delay=10.0, max_attempts=2, exponential_base=2.0
        )

        # Email operations - patient retry with longer intervals
        self.register_strategy(
            "email_operation", base_delay=10.0, max_delay=300.0, max_attempts=3, exponential_base=2.5
        )

        # Network operations - aggressive retry for transient issues
        self.register_strategy(
            "network_operation", base_delay=1.0, max_delay=60.0, max_attempts=5, exponential_base=2.0, jitter_factor=0.2
        )

    def register_strategy(self, operation_name: str, **kwargs) -> AdaptiveRetryStrategy:
        """
        Register a new retry strategy

        Args:
            operation_name: Unique name for the operation
            **kwargs: Strategy configuration parameters

        Returns:
            AdaptiveRetryStrategy: Configured strategy instance
        """
        strategy = AdaptiveRetryStrategy(operation_name, **kwargs)
        self.strategies[operation_name] = strategy
        self.logger.info(f"Registered retry strategy for {operation_name}")
        return strategy

    def execute_with_retry(self, operation_name: str, operation_func: Callable, *args, **kwargs) -> Any:
        """
        Execute operation with appropriate retry strategy

        Args:
            operation_name: Name of operation for strategy selection
            operation_func: Function to execute
            *args: Arguments for operation_func
            **kwargs: Keyword arguments for operation_func

        Returns:
            Any: Result of successful operation

        Raises:
            Exception: If operation fails after all retries
        """
        strategy = self.strategies.get(operation_name)
        if not strategy:
            # Create default strategy for unknown operations
            strategy = self.register_strategy(operation_name)

        last_error = None

        for attempt in range(1, strategy.max_attempts + 1):
            try:
                # Execute operation
                result = operation_func(*args, **kwargs)

                # Record success
                strategy.record_attempt(success=True)

                if attempt > 1:
                    self.logger.info(f"Operation {operation_name} succeeded on attempt {attempt}")

                return result

            except Exception as e:
                last_error = e

                # Record failure
                strategy.record_attempt(success=False, error=e)

                # Check if should retry
                if not strategy.should_retry(attempt, e):
                    self.logger.error(f"Operation {operation_name} failed - not retryable: {e}")
                    break

                if attempt >= strategy.max_attempts:
                    self.logger.error(f"Operation {operation_name} failed after {attempt} attempts")
                    break

                # Calculate delay and wait
                delay = strategy.get_delay(attempt)
                strategy.metrics.total_delay_time += delay

                self.logger.warning(
                    f"Operation {operation_name} failed (attempt {attempt}), retrying in {delay:.1f}s: {e}"
                )
                time.sleep(delay)

        # All retries exhausted
        if last_error:
            raise last_error
        else:
            raise Exception(f"Operation {operation_name} failed without specific error")

    def get_strategy_metrics(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for specific strategy or all strategies

        Args:
            operation_name: Optional specific strategy name

        Returns:
            Dict: Strategy metrics
        """
        if operation_name:
            strategy = self.strategies.get(operation_name)
            if strategy:
                return strategy.get_metrics_summary()
            else:
                return {"error": f"Strategy {operation_name} not found"}

        # Return metrics for all strategies
        return {
            "strategies": {name: strategy.get_metrics_summary() for name, strategy in self.strategies.items()},
            "summary": {
                "total_strategies": len(self.strategies),
                "overall_success_rate": self._calculate_overall_success_rate(),
                "most_reliable_strategy": self._get_most_reliable_strategy(),
                "most_problematic_strategy": self._get_most_problematic_strategy(),
            },
        }

    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate across all strategies"""
        total_attempts = sum(s.metrics.total_attempts for s in self.strategies.values())
        total_successes = sum(s.metrics.successful_attempts for s in self.strategies.values())

        if total_attempts == 0:
            return 0.0

        return total_successes / total_attempts

    def _get_most_reliable_strategy(self) -> Optional[str]:
        """Find the most reliable strategy based on success rate"""
        best_strategy = None
        best_rate = 0.0

        for name, strategy in self.strategies.items():
            if strategy.metrics.total_attempts >= 5:  # Minimum attempts for reliability
                rate = strategy.get_success_rate()
                if rate > best_rate:
                    best_rate = rate
                    best_strategy = name

        return best_strategy

    def _get_most_problematic_strategy(self) -> Optional[str]:
        """Find the most problematic strategy based on failure rate"""
        worst_strategy = None
        worst_rate = 1.0

        for name, strategy in self.strategies.items():
            if strategy.metrics.total_attempts >= 5:  # Minimum attempts for analysis
                rate = strategy.get_success_rate()
                if rate < worst_rate:
                    worst_rate = rate
                    worst_strategy = name

        return worst_strategy

    def reset_strategy_metrics(self, operation_name: str):
        """Reset metrics for a specific strategy"""
        strategy = self.strategies.get(operation_name)
        if strategy:
            strategy.metrics = RetryMetrics()
            strategy.recent_failures.clear()
            self.logger.info(f"Reset metrics for strategy {operation_name}")
        else:
            self.logger.warning(f"Strategy {operation_name} not found for metrics reset")

    def optimize_strategy(self, operation_name: str):
        """
        Optimize strategy parameters based on historical performance

        Args:
            operation_name: Strategy to optimize
        """
        strategy = self.strategies.get(operation_name)
        if not strategy or strategy.metrics.total_attempts < 10:
            return  # Need sufficient data for optimization

        success_rate = strategy.get_success_rate()

        # Adjust parameters based on performance
        if success_rate < 0.5:
            # Poor performance - increase delays and attempts
            strategy.base_delay = min(strategy.base_delay * 1.5, 10.0)
            strategy.max_attempts = min(strategy.max_attempts + 1, 6)
            self.logger.info(f"Optimized strategy {operation_name} for poor performance")

        elif success_rate > 0.9:
            # Excellent performance - can be more aggressive
            strategy.base_delay = max(strategy.base_delay * 0.8, 0.5)
            self.logger.info(f"Optimized strategy {operation_name} for excellent performance")


# Global retry strategy manager instance
retry_manager = RetryStrategyManager()


def with_retry(operation_name: str = "default_operation"):
    """
    Decorator for automatic retry functionality

    Args:
        operation_name: Name to identify the operation for retry strategy

    Returns:
        Decorated function with retry capability
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return retry_manager.execute_with_retry(operation_name, func, *args, **kwargs)

        return wrapper

    return decorator
