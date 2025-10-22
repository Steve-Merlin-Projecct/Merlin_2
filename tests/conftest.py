"""
Module: conftest.py
Purpose: Pytest configuration and shared fixtures for test suite
Created: 2024-08-29
Modified: 2025-10-21
Dependencies: pytest, unittest.mock, modules.resilience
Related: test_end_to_end_workflow.py, test_system_verification.py, tests/
Description: Provides common test fixtures for resilience components (timeout manager,
             circuit breaker, error classifier), mock dependencies, test configuration,
             and project path setup. Handles conditional imports with availability flags
             for resilience modules.
"""

import pytest
import time
import sys
import os
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import resilience components (conditionally)
try:
    from modules.resilience.timeout_manager import TimeoutManager, timeout_config
    from modules.resilience.circuit_breaker_manager import (
        CircuitBreakerManager, CircuitBreaker, CircuitBreakerConfig
    )
    from modules.resilience.error_classifier import ErrorClassifier
    from modules.resilience.resilience_error import ResilienceError, ErrorCategory, ErrorSeverity
    RESILIENCE_AVAILABLE = True
except ImportError:
    RESILIENCE_AVAILABLE = False
    TimeoutManager = None
    timeout_config = None
    CircuitBreakerManager = None
    CircuitBreaker = None
    CircuitBreakerConfig = None
    ErrorClassifier = None
    ResilienceError = None
    ErrorCategory = None
    ErrorSeverity = None


# ===== Resilience Component Fixtures =====

@pytest.fixture
def timeout_manager():
    """Provide fresh timeout manager instance"""
    if not RESILIENCE_AVAILABLE:
        pytest.skip("Resilience modules not available")
    return TimeoutManager()


@pytest.fixture
def circuit_breaker_manager():
    """Provide fresh circuit breaker manager instance"""
    if not RESILIENCE_AVAILABLE:
        pytest.skip("Resilience modules not available")
    return CircuitBreakerManager()


@pytest.fixture
def circuit_breaker():
    """Provide standalone circuit breaker for testing"""
    if not RESILIENCE_AVAILABLE:
        pytest.skip("Resilience modules not available")
    config = CircuitBreakerConfig(
        failure_threshold=3,
        timeout_duration=5.0,
        success_threshold=2,
        failure_rate_threshold=1.0  # Disable rate-based opening for unit tests
    )
    return CircuitBreaker("test_service", config)


@pytest.fixture
def error_classifier():
    """Provide error classifier instance"""
    if not RESILIENCE_AVAILABLE:
        pytest.skip("Resilience modules not available")
    return ErrorClassifier()


# ===== Mock External Dependencies =====

@pytest.fixture
def mock_requests(mocker):
    """Mock requests library for HTTP calls"""
    mock_post = mocker.patch('requests.post')
    mock_get = mocker.patch('requests.get')
    return {
        'post': mock_post,
        'get': mock_get
    }


@pytest.fixture
def mock_database(mocker):
    """Mock database connection and session"""
    mock_engine = mocker.patch('sqlalchemy.create_engine')
    mock_session = MagicMock()
    mock_engine.return_value.SessionLocal.return_value = mock_session
    return mock_session


@pytest.fixture
def mock_gemini_api(mocker):
    """Mock Gemini API responses"""
    mock_post = mocker.patch('requests.post')

    # Default successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '{"analysis_results": []}'
                }]
            }
        }],
        "usage": {"totalTokenCount": 100}
    }
    mock_post.return_value = mock_response

    return mock_post


@pytest.fixture
def mock_gmail_api(mocker):
    """Mock Gmail API service"""
    mock_service = MagicMock()
    mock_service.users().messages().send().execute.return_value = {
        "id": "msg_12345",
        "threadId": "thread_67890"
    }
    return mock_service


# ===== Test Error Scenarios =====

@pytest.fixture
def network_errors():
    """Provide network error test cases"""
    return [
        ConnectionRefusedError("Connection refused"),
        ConnectionResetError("Connection reset by peer"),
        TimeoutError("Request timed out"),
        Exception("Connection timeout"),
        Exception("Network unreachable"),
    ]


@pytest.fixture
def api_errors():
    """Provide API error test cases"""
    return [
        Exception("429 Too Many Requests"),
        Exception("503 Service Unavailable"),
        Exception("500 Internal Server Error"),
        Exception("502 Bad Gateway"),
        Exception("401 Unauthorized"),
        Exception("403 Forbidden"),
    ]


@pytest.fixture
def database_errors():
    """Provide database error test cases"""
    return [
        Exception("Deadlock detected"),
        Exception("Lock timeout"),
        Exception("Connection pool exhausted"),
        Exception("Query timeout exceeded"),
        Exception("Database connection failed"),
        Exception("Unique constraint violation"),
    ]


# ===== Test Utilities =====

@pytest.fixture
def slow_operation():
    """Provide slow operation for timeout testing"""
    def operation(duration: float = 2.0):
        time.sleep(duration)
        return "completed"
    return operation


@pytest.fixture
def fast_operation():
    """Provide fast operation for timeout testing"""
    def operation():
        return "completed"
    return operation


@pytest.fixture
def failing_operation():
    """Provide operation that always fails"""
    def operation(error_type=Exception, error_message="Operation failed"):
        raise error_type(error_message)
    return operation


@pytest.fixture
def intermittent_operation():
    """Provide operation that fails N times then succeeds"""
    class IntermittentOp:
        def __init__(self, fail_times=2):
            self.fail_times = fail_times
            self.attempts = 0

        def __call__(self):
            self.attempts += 1
            if self.attempts <= self.fail_times:
                raise Exception(f"Attempt {self.attempts} failed")
            return f"Success after {self.attempts} attempts"

    return IntermittentOp


# ===== Test Markers =====

def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests across multiple components"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers", "chaos: Chaos engineering and failure scenario tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take more than 1 second"
    )
    config.addinivalue_line(
        "markers", "requires_api: Tests that need external API access"
    )


# ===== Cleanup Fixtures =====

@pytest.fixture(autouse=True)
def reset_resilience_state():
    """Reset resilience system state between tests"""
    yield
    # Reset timeout configuration (only if resilience modules available)
    if RESILIENCE_AVAILABLE and timeout_config:
        for op_type in timeout_config._timeouts:
            timeout_config.reset_timeout(op_type)
        # Clear custom timeouts
        timeout_config._custom_timeouts.clear()


@pytest.fixture
def capture_logs(caplog):
    """Capture and provide log records"""
    import logging
    caplog.set_level(logging.INFO)
    return caplog


# ===== Performance Testing Fixtures =====

@pytest.fixture
def benchmark_data():
    """Provide data for benchmark comparisons"""
    return {
        "baseline_latency_ms": 100,
        "target_overhead_percent": 5.0,
        "sample_size": 1000
    }


@pytest.fixture
def load_generator():
    """Provide simple load generator for testing"""
    import threading
    import queue

    class LoadGenerator:
        def __init__(self):
            self.results = queue.Queue()

        def run(self, func, num_requests, num_threads=10):
            def worker():
                try:
                    result = func()
                    self.results.put({"status": "success", "result": result})
                except Exception as e:
                    self.results.put({"status": "error", "error": str(e)})

            threads = []
            for _ in range(num_requests):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()

                # Control concurrency
                if len(threads) >= num_threads:
                    threads[0].join()
                    threads.pop(0)

            # Wait for remaining threads
            for thread in threads:
                thread.join()

            # Collect results
            results = []
            while not self.results.empty():
                results.append(self.results.get())

            return results

    return LoadGenerator()
