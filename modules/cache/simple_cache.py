"""
Simple In-Memory Cache for Dashboard
Lightweight caching layer for single-user dashboard

For single user, this is sufficient. Can upgrade to Redis later if needed.
"""

import time
import logging
from functools import wraps
from typing import Any, Callable, Optional
import hashlib
import json

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Simple in-memory cache with TTL support

    Perfect for single-user dashboard where data freshness is more important than
    distributed caching. Upgrade to Redis only if multi-user or persistence needed.
    """

    def __init__(self):
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key not in self._cache:
            return None

        # Check if expired
        timestamp, ttl = self._timestamps.get(key, (0, 0))
        if time.time() > timestamp + ttl:
            # Expired - remove from cache
            self.delete(key)
            return None

        logger.debug(f"Cache HIT: {key}")
        return self._cache[key]

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set cached value with TTL (default 5 minutes)"""
        self._cache[key] = value
        self._timestamps[key] = (time.time(), ttl)
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")

    def delete(self, key: str):
        """Delete cached value"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        logger.debug(f"Cache DELETE: {key}")

    def clear(self):
        """Clear all cached values"""
        count = len(self._cache)
        self._cache.clear()
        self._timestamps.clear()
        logger.info(f"Cache CLEARED: {count} entries")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        active_entries = sum(
            1
            for key in self._cache
            if time.time() <= self._timestamps.get(key, (0, 0))[0] + self._timestamps.get(key, (0, 0))[1]
        )

        return {
            "total_entries": len(self._cache),
            "active_entries": active_entries,
            "expired_entries": len(self._cache) - active_entries,
        }


# Global cache instance
cache = SimpleCache()


# =================================================================
# CACHE DECORATOR
# =================================================================


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results

    Args:
        ttl: Time-to-live in seconds (default 300 = 5 minutes)
        key_prefix: Prefix for cache key (default: function name)

    Usage:
        @cached(ttl=180, key_prefix="dashboard")
        def get_dashboard_data():
            return expensive_query()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Cache miss - compute value
            logger.debug(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl=ttl)

            return result

        # Add cache control methods to wrapped function
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_stats = lambda: cache.get_stats()

        return wrapper

    return decorator


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict, prefix: str = "") -> str:
    """Generate cache key from function and arguments"""
    # Use function name as base
    key_parts = [prefix or func.__name__]

    # Add args
    if args:
        args_str = "_".join(str(arg) for arg in args)
        key_parts.append(args_str)

    # Add kwargs (sorted for consistency)
    if kwargs:
        kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_parts.append(kwargs_str)

    key = ":".join(key_parts)

    # Hash if too long
    if len(key) > 200:
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return f"{prefix or func.__name__}:{key_hash}"

    return key


# =================================================================
# SPECIALIZED DASHBOARD CACHE FUNCTIONS
# =================================================================


class DashboardCache:
    """
    Specialized cache functions for dashboard data

    Provides convenient methods for caching common dashboard queries
    """

    # Cache TTLs for different data types
    TTL_DASHBOARD_METRICS = 300  # 5 minutes
    TTL_RECENT_APPLICATIONS = 180  # 3 minutes
    TTL_PIPELINE_STATUS = 60  # 1 minute
    TTL_TIMESERIES = 300  # 5 minutes

    @staticmethod
    def get_dashboard_overview():
        """Get cached dashboard overview"""
        return cache.get("dashboard:overview")

    @staticmethod
    def set_dashboard_overview(data: dict):
        """Cache dashboard overview"""
        cache.set("dashboard:overview", data, ttl=DashboardCache.TTL_DASHBOARD_METRICS)

    @staticmethod
    def get_recent_applications():
        """Get cached recent applications"""
        return cache.get("dashboard:recent_applications")

    @staticmethod
    def set_recent_applications(data: list):
        """Cache recent applications"""
        cache.set("dashboard:recent_applications", data, ttl=DashboardCache.TTL_RECENT_APPLICATIONS)

    @staticmethod
    def get_pipeline_status():
        """Get cached pipeline status"""
        return cache.get("dashboard:pipeline_status")

    @staticmethod
    def set_pipeline_status(data: dict):
        """Cache pipeline status"""
        cache.set("dashboard:pipeline_status", data, ttl=DashboardCache.TTL_PIPELINE_STATUS)

    @staticmethod
    def get_timeseries(metric: str, period: str, time_range: str):
        """Get cached timeseries data"""
        key = f"dashboard:timeseries:{metric}:{period}:{time_range}"
        return cache.get(key)

    @staticmethod
    def set_timeseries(metric: str, period: str, time_range: str, data: dict):
        """Cache timeseries data"""
        key = f"dashboard:timeseries:{metric}:{period}:{time_range}"
        cache.set(key, data, ttl=DashboardCache.TTL_TIMESERIES)

    @staticmethod
    def invalidate_all():
        """Invalidate all dashboard cache"""
        cache.clear()
        logger.info("All dashboard cache invalidated")

    @staticmethod
    def invalidate_metrics():
        """Invalidate only metrics cache (on new data)"""
        cache.delete("dashboard:overview")
        cache.delete("dashboard:pipeline_status")
        logger.info("Dashboard metrics cache invalidated")

    @staticmethod
    def invalidate_applications():
        """Invalidate applications cache (on new application)"""
        cache.delete("dashboard:recent_applications")
        logger.info("Recent applications cache invalidated")


# =================================================================
# CACHE WARMING
# =================================================================


def warm_dashboard_cache():
    """
    Warm dashboard cache on startup

    Pre-populate cache with commonly accessed data to avoid
    initial slow loads
    """
    logger.info("Warming dashboard cache...")

    try:
        # Import here to avoid circular dependency
        from modules.dashboard_api_v2 import (
            get_dashboard_overview,
            get_pipeline_status,
        )

        # Warm overview cache
        # Note: This would need to be called with a request context
        # For now, just log the intention
        logger.info("Dashboard cache warming would happen here")
        # In practice: Make internal API calls to populate cache

    except Exception as e:
        logger.error(f"Error warming cache: {e}")


# =================================================================
# CACHE MIDDLEWARE (Flask Integration)
# =================================================================


def add_cache_headers(response, ttl: int = 300):
    """
    Add cache control headers to Flask response

    Args:
        response: Flask response object
        ttl: Cache TTL in seconds

    Returns:
        Modified response with cache headers
    """
    response.headers["Cache-Control"] = f"private, max-age={ttl}"
    response.headers["X-Cache-TTL"] = str(ttl)
    return response


# =================================================================
# USAGE EXAMPLES
# =================================================================

"""
# Example 1: Using decorator
@cached(ttl=180, key_prefix="dashboard")
def get_expensive_data(user_id):
    # Expensive database query
    return query_database(user_id)

# Example 2: Manual caching
data = cache.get("my_key")
if data is None:
    data = expensive_computation()
    cache.set("my_key", data, ttl=300)

# Example 3: Dashboard-specific caching
overview = DashboardCache.get_dashboard_overview()
if overview is None:
    overview = compute_dashboard_overview()
    DashboardCache.set_dashboard_overview(overview)

# Example 4: Cache invalidation on event
from modules.cache.simple_cache import DashboardCache

def on_new_application_created():
    DashboardCache.invalidate_applications()
    DashboardCache.invalidate_metrics()
"""
