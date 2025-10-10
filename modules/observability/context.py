"""
Request Context Management

Provides thread-safe context propagation for request tracing and correlation.
Enables automatic context injection into logs and tracking across async operations.
"""

import uuid
from typing import Optional
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime


# Thread-safe context variable for storing request context
_request_context: ContextVar[Optional['RequestContext']] = ContextVar('request_context', default=None)


@dataclass
class RequestContext:
    """
    Request context containing correlation and tracing information.

    Attributes:
        correlation_id: Unique identifier for request correlation across services
        method: HTTP method (GET, POST, etc.)
        path: Request path
        user_id: Authenticated user ID (if available)
        ip_address: Client IP address
        start_time: Request start timestamp
        metadata: Additional custom metadata
    """
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: Optional[str] = None
    path: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

    def duration_ms(self) -> float:
        """
        Calculate request duration in milliseconds.

        Returns:
            Duration in milliseconds since request start
        """
        delta = datetime.utcnow() - self.start_time
        return delta.total_seconds() * 1000

    def to_dict(self) -> dict:
        """
        Convert context to dictionary.

        Returns:
            Dictionary representation of context
        """
        return {
            'correlation_id': self.correlation_id,
            'method': self.method,
            'path': self.path,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'duration_ms': self.duration_ms(),
            'metadata': self.metadata
        }


def get_request_context() -> Optional[RequestContext]:
    """
    Get the current request context.

    Returns:
        Current RequestContext or None if not set

    Example:
        >>> context = get_request_context()
        >>> if context:
        ...     print(f"Correlation ID: {context.correlation_id}")
    """
    return _request_context.get()


def set_request_context(context: RequestContext) -> None:
    """
    Set the current request context.

    Args:
        context: RequestContext to set

    Example:
        >>> from flask import request
        >>> context = RequestContext(
        ...     method=request.method,
        ...     path=request.path,
        ...     ip_address=request.remote_addr
        ... )
        >>> set_request_context(context)
    """
    _request_context.set(context)


def clear_request_context() -> None:
    """
    Clear the current request context.

    Should be called at the end of request processing.
    """
    _request_context.set(None)


def create_request_context(
    method: Optional[str] = None,
    path: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    correlation_id: Optional[str] = None,
    **metadata
) -> RequestContext:
    """
    Create and set a new request context.

    Args:
        method: HTTP method
        path: Request path
        user_id: User ID
        ip_address: Client IP
        correlation_id: Existing correlation ID (generates new if not provided)
        **metadata: Additional metadata

    Returns:
        Created RequestContext

    Example:
        >>> context = create_request_context(
        ...     method='POST',
        ...     path='/api/jobs',
        ...     user_id='user123',
        ...     operation='job_scraping'
        ... )
    """
    context = RequestContext(
        correlation_id=correlation_id or str(uuid.uuid4()),
        method=method,
        path=path,
        user_id=user_id,
        ip_address=ip_address,
        metadata=metadata
    )
    set_request_context(context)
    return context
