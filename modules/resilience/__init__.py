"""
Resilience Module - Failure Recovery and Retry Mechanisms

This module provides comprehensive failure recovery capabilities for the
automated job application system, implementing Step 2.3 of Implementation Plan V2.16.

Key Components:
- FailureRecoveryManager: Central coordinator for error handling and recovery
- RetryStrategyManager: Configurable retry strategies for different failure types
- WorkflowCheckpointManager: Checkpoint and resume capabilities
- ErrorClassifier: Intelligent error categorization and handling
- DataConsistencyValidator: Data integrity validation and correction
"""

__version__ = "2.16.3"
__all__ = [
    "FailureRecoveryManager",
    "RetryStrategyManager",
    "WorkflowCheckpointManager",
    "ErrorClassifier",
    "DataConsistencyValidator",
]
