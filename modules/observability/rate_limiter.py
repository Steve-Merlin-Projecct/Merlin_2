"""
Rate Limiting for Monitoring API

Implements token bucket algorithm for rate limiting to protect monitoring
endpoints from abuse and ensure fair resource allocation.

Features:
- Token bucket algorithm for smooth rate limiting
- Per-API-key tracking
- Configurable limits and time windows
- Automatic cleanup of expired buckets
- Thread-safe implementation
- Returns standard HTTP 429 with Retry-After header
"""

import time
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app


@dataclass
class TokenBucket:
    """
    Token bucket for rate limiting.

    Implements the token bucket algorithm where tokens are added at a constant
    rate and removed when requests are made. When the bucket is empty, requests
    are rate limited.

    Attributes:
        capacity: Maximum number of tokens (burst size)
        tokens: Current number of tokens available
        refill_rate: Tokens added per second
        last_refill: Last time tokens were added
    """
    capacity: int
    tokens: float
    refill_rate: float
    last_refill: float


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.

    Tracks rate limits per API key and automatically refills tokens over time.
    Thread-safe for concurrent request handling.

    Example:
        >>> limiter = RateLimiter(requests_per_minute=60)
        >>> allowed, retry_after = limiter.is_allowed('api_key_123')
        >>> if not allowed:
        ...     print(f"Rate limited. Retry after {retry_after} seconds")
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None,
        cleanup_interval_minutes: int = 60
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute per API key
            burst_size: Maximum burst size (defaults to requests_per_minute)
            cleanup_interval_minutes: How often to clean up expired buckets
        """
        self.requests_per_minute = requests_per_minute
        self.capacity = burst_size or requests_per_minute
        self.refill_rate = requests_per_minute / 60.0  # Tokens per second

        # Dictionary to store token buckets per API key
        self.buckets: Dict[str, TokenBucket] = {}

        # Lock for thread-safe access
        self.lock = threading.Lock()

        # Track last cleanup time
        self.last_cleanup = time.time()
        self.cleanup_interval = cleanup_interval_minutes * 60  # Convert to seconds

    def _get_or_create_bucket(self, key: str) -> TokenBucket:
        """
        Get existing bucket or create a new one for the given key.

        Args:
            key: API key or identifier

        Returns:
            TokenBucket for this key
        """
        current_time = time.time()

        if key not in self.buckets:
            # Create new bucket with full capacity
            self.buckets[key] = TokenBucket(
                capacity=self.capacity,
                tokens=self.capacity,
                refill_rate=self.refill_rate,
                last_refill=current_time
            )

        return self.buckets[key]

    def _refill_bucket(self, bucket: TokenBucket) -> None:
        """
        Refill tokens in the bucket based on elapsed time.

        Args:
            bucket: Token bucket to refill
        """
        current_time = time.time()
        time_elapsed = current_time - bucket.last_refill

        # Calculate tokens to add
        tokens_to_add = time_elapsed * bucket.refill_rate

        # Update bucket
        bucket.tokens = min(bucket.capacity, bucket.tokens + tokens_to_add)
        bucket.last_refill = current_time

    def _cleanup_old_buckets(self) -> None:
        """
        Remove buckets that haven't been used recently to prevent memory leaks.

        Only runs periodically based on cleanup_interval.
        """
        current_time = time.time()

        # Only cleanup periodically
        if current_time - self.last_cleanup < self.cleanup_interval:
            return

        # Remove buckets that haven't been accessed in 2x cleanup interval
        expiry_threshold = current_time - (self.cleanup_interval * 2)

        keys_to_remove = [
            key for key, bucket in self.buckets.items()
            if bucket.last_refill < expiry_threshold
        ]

        for key in keys_to_remove:
            del self.buckets[key]

        self.last_cleanup = current_time

    def is_allowed(self, key: str, tokens: int = 1) -> Tuple[bool, Optional[int]]:
        """
        Check if a request should be allowed based on rate limit.

        Args:
            key: API key or identifier to check
            tokens: Number of tokens to consume (default: 1)

        Returns:
            Tuple of (allowed: bool, retry_after: Optional[int])
            - allowed: True if request should be allowed
            - retry_after: Seconds until next token available (None if allowed)

        Example:
            >>> allowed, retry_after = limiter.is_allowed('api_key_123')
            >>> if not allowed:
            ...     print(f"Wait {retry_after} seconds")
        """
        with self.lock:
            # Periodic cleanup
            self._cleanup_old_buckets()

            # Get or create bucket for this key
            bucket = self._get_or_create_bucket(key)

            # Refill tokens
            self._refill_bucket(bucket)

            # Check if we have enough tokens
            if bucket.tokens >= tokens:
                bucket.tokens -= tokens
                return True, None
            else:
                # Calculate retry-after time
                tokens_needed = tokens - bucket.tokens
                retry_after = int(tokens_needed / bucket.refill_rate) + 1
                return False, retry_after

    def get_stats(self, key: str) -> Optional[Dict[str, any]]:
        """
        Get current rate limit statistics for a key.

        Args:
            key: API key or identifier

        Returns:
            Dictionary with rate limit stats or None if key not found

        Example:
            >>> stats = limiter.get_stats('api_key_123')
            >>> print(f"Remaining: {stats['remaining']}/{stats['capacity']}")
        """
        with self.lock:
            if key not in self.buckets:
                return None

            bucket = self._get_or_create_bucket(key)
            self._refill_bucket(bucket)

            return {
                'capacity': bucket.capacity,
                'remaining': int(bucket.tokens),
                'refill_rate_per_second': bucket.refill_rate,
                'requests_per_minute': self.requests_per_minute,
                'next_refill_in': 1.0 / bucket.refill_rate if bucket.refill_rate > 0 else 0
            }

    def reset(self, key: Optional[str] = None) -> None:
        """
        Reset rate limits for a specific key or all keys.

        Args:
            key: API key to reset (None to reset all)

        Example:
            >>> limiter.reset('api_key_123')  # Reset specific key
            >>> limiter.reset()  # Reset all keys
        """
        with self.lock:
            if key is None:
                self.buckets.clear()
            elif key in self.buckets:
                del self.buckets[key]


# Global rate limiter instance
_default_rate_limiter = None


def get_default_rate_limiter() -> RateLimiter:
    """
    Get the global default rate limiter instance.

    Returns:
        Default RateLimiter instance
    """
    global _default_rate_limiter
    if _default_rate_limiter is None:
        _default_rate_limiter = RateLimiter(requests_per_minute=60)
    return _default_rate_limiter


def init_rate_limiter(
    app=None,
    requests_per_minute: int = 60,
    burst_size: Optional[int] = None
) -> RateLimiter:
    """
    Initialize rate limiter and attach to Flask app.

    Args:
        app: Flask application instance (optional)
        requests_per_minute: Maximum requests per minute
        burst_size: Maximum burst size (defaults to requests_per_minute)

    Returns:
        Initialized RateLimiter instance

    Example:
        >>> app = Flask(__name__)
        >>> limiter = init_rate_limiter(app, requests_per_minute=120)
    """
    limiter = RateLimiter(requests_per_minute=requests_per_minute, burst_size=burst_size)
    if app is not None:
        app.rate_limiter = limiter
    return limiter


def rate_limit(
    rate_limiter: Optional[RateLimiter] = None,
    get_key_func=None,
    skip_auth_check: bool = False
):
    """
    Decorator to apply rate limiting to Flask endpoints.

    Args:
        rate_limiter: RateLimiter instance to use (uses default if None)
        get_key_func: Function to extract rate limit key from request (default: uses API key)
        skip_auth_check: Skip authentication requirement (for public endpoints)

    Returns:
        Decorated function with rate limiting

    Example:
        >>> @app.route('/api/endpoint')
        >>> @rate_limit()
        >>> def my_endpoint():
        ...     return jsonify({'status': 'ok'})

        >>> # Custom key function
        >>> @rate_limit(get_key_func=lambda: request.remote_addr)
        >>> def public_endpoint():
        ...     return jsonify({'status': 'ok'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get rate limiter instance
            limiter = rate_limiter or getattr(current_app, 'rate_limiter', None) or get_default_rate_limiter()

            # Determine rate limit key
            if get_key_func:
                key = get_key_func()
            else:
                # Default: use API key from header or query param
                key = request.headers.get('X-Monitoring-Key') or request.args.get('api_key')

                # If no API key and auth check not skipped, require it
                if not key and not skip_auth_check:
                    return jsonify({
                        'error': 'Unauthorized',
                        'message': 'API key required for rate limiting'
                    }), 401

                # Fall back to IP address if no key
                if not key:
                    key = request.remote_addr or 'anonymous'

            # Check rate limit
            allowed, retry_after = limiter.is_allowed(key)

            if not allowed:
                # Get current stats for response headers
                stats = limiter.get_stats(key)

                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please retry after {retry_after} seconds.',
                    'retry_after': retry_after,
                    'limit': limiter.requests_per_minute,
                    'window': '1 minute'
                })

                response.status_code = 429
                response.headers['Retry-After'] = str(retry_after)
                response.headers['X-RateLimit-Limit'] = str(limiter.requests_per_minute)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(int(time.time() + retry_after))

                return response

            # Add rate limit headers to response
            stats = limiter.get_stats(key)
            if stats:
                response = f(*args, **kwargs)

                # Add rate limit headers if response is a tuple or Response object
                if isinstance(response, tuple):
                    response_obj, status_code = response[0], response[1] if len(response) > 1 else 200
                    if hasattr(response_obj, 'headers'):
                        response_obj.headers['X-RateLimit-Limit'] = str(stats['capacity'])
                        response_obj.headers['X-RateLimit-Remaining'] = str(stats['remaining'])
                        return response
                elif hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(stats['capacity'])
                    response.headers['X-RateLimit-Remaining'] = str(stats['remaining'])

                return response

            return f(*args, **kwargs)

        return decorated_function
    return decorator
