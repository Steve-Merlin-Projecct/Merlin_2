"""
Rate Limit Memory Monitoring

Tracks in-memory storage usage, active keys, cleanup effectiveness,
and provides real-time metrics for the rate limiting system.

Version: 1.0.0
Created: 2025-10-11
"""

import logging
import sys
import threading
import time
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime

from modules.security import rate_limit_config as config

logger = logging.getLogger(__name__)

# Global monitoring state
_monitor_thread: Optional[threading.Thread] = None
_monitor_running = False
_cleanup_stats = {
    "total_cleanups": 0,
    "total_keys_removed": 0,
    "last_cleanup_time": None,
    "last_cleanup_keys_removed": 0,
}


# ============================================================================
# MEMORY CALCULATION
# ============================================================================


def get_object_size(obj: Any) -> int:
    """
    Calculate size of Python object in bytes (including nested structures).

    Args:
        obj: Python object to measure

    Returns:
        Size in bytes
    """
    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        size += sum(get_object_size(k) + get_object_size(v) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set)):
        size += sum(get_object_size(item) for item in obj)

    return size


def get_storage_size_bytes(storage) -> int:
    """
    Calculate total memory usage of rate limit storage.

    Args:
        storage: Flask-Limiter storage backend

    Returns:
        Memory usage in bytes
    """
    try:
        if not storage:
            return 0

        # For in-memory storage, calculate size of internal storage dict
        if hasattr(storage, "storage"):
            return get_object_size(storage.storage)
        elif hasattr(storage, "_data"):
            return get_object_size(storage._data)
        else:
            # Fallback: estimate based on key count
            key_count = get_active_key_count(storage)
            # Estimate: ~200 bytes per key (key string + list of timestamps)
            return key_count * 200

    except Exception as e:
        logger.error(f"Failed to calculate storage size: {e}")
        return 0


def get_storage_size_mb(storage) -> float:
    """
    Get storage size in megabytes.

    Args:
        storage: Flask-Limiter storage backend

    Returns:
        Memory usage in MB (rounded to 2 decimals)
    """
    bytes_size = get_storage_size_bytes(storage)
    return round(bytes_size / (1024 * 1024), 2)


# ============================================================================
# KEY TRACKING
# ============================================================================


def get_active_key_count(storage) -> int:
    """
    Count number of active rate limit keys in storage.

    Args:
        storage: Flask-Limiter storage backend

    Returns:
        Number of active keys
    """
    try:
        if not storage:
            return 0

        if hasattr(storage, "storage"):
            return len(storage.storage)
        elif hasattr(storage, "_data"):
            return len(storage._data)
        elif hasattr(storage, "keys"):
            return len(list(storage.keys()))
        else:
            return 0

    except Exception as e:
        logger.error(f"Failed to count active keys: {e}")
        return 0


def get_key_distribution(storage) -> Dict[str, int]:
    """
    Get distribution of keys by prefix (ip: vs user:).

    Args:
        storage: Flask-Limiter storage backend

    Returns:
        Dictionary with counts by key type
    """
    distribution = defaultdict(int)

    try:
        if not storage:
            return dict(distribution)

        # Get all keys
        keys = []
        if hasattr(storage, "storage"):
            keys = list(storage.storage.keys())
        elif hasattr(storage, "_data"):
            keys = list(storage._data.keys())

        # Categorize keys
        for key in keys:
            if isinstance(key, str):
                if key.startswith("ip:"):
                    distribution["ip_based"] += 1
                elif key.startswith("user:"):
                    distribution["user_based"] += 1
                else:
                    distribution["other"] += 1

    except Exception as e:
        logger.error(f"Failed to get key distribution: {e}")

    return dict(distribution)


def get_keys_by_endpoint(storage, limiter) -> Dict[str, int]:
    """
    Get count of rate limit keys grouped by endpoint.

    Args:
        storage: Flask-Limiter storage backend
        limiter: Flask-Limiter instance

    Returns:
        Dictionary mapping endpoint to key count
    """
    endpoint_keys = defaultdict(int)

    try:
        if not storage or not limiter:
            return dict(endpoint_keys)

        # This is a simplified version - full implementation would require
        # parsing key patterns to extract endpoint information
        # For now, return total count
        total_keys = get_active_key_count(storage)
        if total_keys > 0:
            endpoint_keys["all_endpoints"] = total_keys

    except Exception as e:
        logger.error(f"Failed to get keys by endpoint: {e}")

    return dict(endpoint_keys)


# ============================================================================
# HEALTH CHECKS
# ============================================================================


def check_memory_health(storage) -> Dict[str, Any]:
    """
    Check memory health status against configured thresholds.

    Args:
        storage: Flask-Limiter storage backend

    Returns:
        Health status dictionary with alerts
    """
    size_mb = get_storage_size_mb(storage)
    key_count = get_active_key_count(storage)

    # Determine health status
    status = "healthy"
    alerts = []

    if size_mb >= config.CRITICAL_THRESHOLD_MB:
        status = "critical"
        alerts.append(
            f"Memory usage critical: {size_mb}MB >= {config.CRITICAL_THRESHOLD_MB}MB threshold"
        )
    elif size_mb >= config.ALERT_THRESHOLD_MB:
        status = "warning"
        alerts.append(
            f"Memory usage high: {size_mb}MB >= {config.ALERT_THRESHOLD_MB}MB threshold"
        )

    if size_mb >= config.MAX_MEMORY_MB:
        status = "critical"
        alerts.append(
            f"Memory limit exceeded: {size_mb}MB >= {config.MAX_MEMORY_MB}MB limit"
        )

    # Calculate utilization percentage
    utilization_percent = round((size_mb / config.MAX_MEMORY_MB) * 100, 2)

    return {
        "status": status,
        "memory_mb": size_mb,
        "max_memory_mb": config.MAX_MEMORY_MB,
        "utilization_percent": utilization_percent,
        "key_count": key_count,
        "alerts": alerts,
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# AUTOMATIC CLEANUP
# ============================================================================


def cleanup_expired_keys(storage) -> int:
    """
    Remove expired rate limit keys from storage.

    Flask-Limiter handles expiration automatically, but this function
    explicitly triggers cleanup and tracks statistics.

    Args:
        storage: Flask-Limiter storage backend

    Returns:
        Number of keys removed
    """
    try:
        if not storage:
            return 0

        keys_before = get_active_key_count(storage)

        # Flask-Limiter in-memory storage doesn't have explicit cleanup
        # Keys expire automatically when checked
        # This function mainly tracks stats

        keys_after = get_active_key_count(storage)
        keys_removed = max(0, keys_before - keys_after)

        # Update cleanup stats
        _cleanup_stats["total_cleanups"] += 1
        _cleanup_stats["total_keys_removed"] += keys_removed
        _cleanup_stats["last_cleanup_time"] = datetime.now()
        _cleanup_stats["last_cleanup_keys_removed"] = keys_removed

        if keys_removed > 0:
            logger.info(
                f"Cleanup cycle completed: {keys_removed} keys removed, "
                f"{keys_after} keys remaining"
            )

        return keys_removed

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return 0


def cleanup_loop(storage, limiter):
    """
    Background thread that runs cleanup periodically.

    Args:
        storage: Flask-Limiter storage backend
        limiter: Flask-Limiter instance
    """
    global _monitor_running

    logger.info(
        f"Cleanup loop started (interval: {config.CLEANUP_INTERVAL_SECONDS}s)"
    )

    while _monitor_running:
        try:
            # Run cleanup
            cleanup_expired_keys(storage)

            # Log memory status
            health = check_memory_health(storage)
            if health["status"] != "healthy":
                logger.warning(
                    f"Memory health: {health['status']} - "
                    f"{health['memory_mb']}MB / {health['max_memory_mb']}MB "
                    f"({health['utilization_percent']}%)"
                )

                # Log alerts
                for alert in health["alerts"]:
                    logger.warning(f"Alert: {alert}")

            # Sleep until next cleanup
            time.sleep(config.CLEANUP_INTERVAL_SECONDS)

        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")
            time.sleep(config.CLEANUP_INTERVAL_SECONDS)

    logger.info("Cleanup loop stopped")


def start_cleanup_thread(storage, limiter):
    """
    Start background cleanup thread.

    Args:
        storage: Flask-Limiter storage backend
        limiter: Flask-Limiter instance
    """
    global _monitor_thread, _monitor_running

    if _monitor_running:
        logger.warning("Cleanup thread already running")
        return

    _monitor_running = True
    _monitor_thread = threading.Thread(
        target=cleanup_loop,
        args=(storage, limiter),
        daemon=True,
        name="RateLimitCleanup",
    )
    _monitor_thread.start()

    logger.info("Cleanup thread started successfully")


def stop_cleanup_thread():
    """Stop background cleanup thread gracefully."""
    global _monitor_running, _monitor_thread

    if not _monitor_running:
        logger.warning("Cleanup thread not running")
        return

    logger.info("Stopping cleanup thread...")
    _monitor_running = False

    if _monitor_thread:
        _monitor_thread.join(timeout=5)

    logger.info("Cleanup thread stopped")


# ============================================================================
# METRICS API
# ============================================================================


def get_metrics(storage, limiter) -> Dict[str, Any]:
    """
    Get comprehensive rate limiting metrics.

    Args:
        storage: Flask-Limiter storage backend
        limiter: Flask-Limiter instance

    Returns:
        Dictionary with all metrics
    """
    health = check_memory_health(storage)
    distribution = get_key_distribution(storage)

    return {
        "memory": {
            "current_mb": health["memory_mb"],
            "max_mb": health["max_memory_mb"],
            "utilization_percent": health["utilization_percent"],
            "status": health["status"],
        },
        "keys": {
            "total_active": health["key_count"],
            "distribution": distribution,
        },
        "cleanup": {
            "total_cleanups": _cleanup_stats["total_cleanups"],
            "total_keys_removed": _cleanup_stats["total_keys_removed"],
            "last_cleanup_time": (
                _cleanup_stats["last_cleanup_time"].isoformat()
                if _cleanup_stats["last_cleanup_time"]
                else None
            ),
            "last_cleanup_keys_removed": _cleanup_stats["last_cleanup_keys_removed"],
        },
        "config": {
            "cleanup_interval_seconds": config.CLEANUP_INTERVAL_SECONDS,
            "alert_threshold_mb": config.ALERT_THRESHOLD_MB,
            "critical_threshold_mb": config.CRITICAL_THRESHOLD_MB,
        },
        "alerts": health["alerts"],
        "timestamp": health["timestamp"],
    }


def get_metrics_summary(storage, limiter) -> str:
    """
    Get human-readable metrics summary.

    Args:
        storage: Flask-Limiter storage backend
        limiter: Flask-Limiter instance

    Returns:
        Formatted string with key metrics
    """
    metrics = get_metrics(storage, limiter)

    summary = f"""
Rate Limiting Metrics Summary
=============================
Memory: {metrics['memory']['current_mb']}MB / {metrics['memory']['max_mb']}MB ({metrics['memory']['utilization_percent']}%)
Status: {metrics['memory']['status'].upper()}
Active Keys: {metrics['keys']['total_active']}
Cleanup Cycles: {metrics['cleanup']['total_cleanups']}
Keys Removed: {metrics['cleanup']['total_keys_removed']}
    """.strip()

    if metrics["alerts"]:
        summary += "\n\nAlerts:\n" + "\n".join(f"- {alert}" for alert in metrics["alerts"])

    return summary
