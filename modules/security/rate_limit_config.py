"""
Rate Limiting Configuration for Job Application System

Defines rate limit tiers, memory management settings, and analytics configuration
for the Flask-Limiter based API protection system.

Version: 1.0.0
Created: 2025-10-11
"""

import os
from typing import Dict, Any

# ============================================================================
# RATE LIMIT TIERS
# ============================================================================

RATE_LIMIT_TIERS: Dict[str, Dict[str, str]] = {
    # Expensive operations - protect costs (Gemini AI ~$0.001/req, Apify ~$0.10-$0.50/scrape)
    "expensive": {
        "ai_analysis": "10/minute;50/hour;200/day",
        "job_scraping": "5/hour;20/day",
        "batch_ai_processing": "5/minute;20/hour",
        "ai_usage_intensive": "10/minute;30/hour;100/day",
    },
    # Moderate operations - balance performance and cost
    "moderate": {
        "document_generation": "20/minute;200/hour",
        "email_send": "10/minute;100/hour",
        "db_write": "50/minute;500/hour",
        "workflow_orchestration": "20/minute;100/hour",
        "content_analysis": "30/minute;300/hour",
    },
    # Cheap operations - generous limits for reads
    "cheap": {
        "db_read": "200/minute",
        "dashboard": "500/minute",
        "analytics": "100/minute",
        "status_check": "1000/minute",
    },
    # Default for unspecified endpoints
    "default": "100/minute",
}


# ============================================================================
# MEMORY MANAGEMENT
# ============================================================================

# Cleanup configuration
CLEANUP_INTERVAL_SECONDS = 60  # Run cleanup every minute
MAX_MEMORY_MB = 50  # Maximum memory for rate limit storage
ALERT_THRESHOLD_MB = 40  # Alert when usage exceeds this
CRITICAL_THRESHOLD_MB = 45  # Critical alert threshold

# Storage configuration
STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")  # Default to in-memory
STORAGE_OPTIONS = {
    "memory": {
        "per_method": False,  # Don't differentiate GET vs POST in same endpoint
    }
}

# Key expiration (Flask-Limiter handles this automatically based on window)
# But we track it for monitoring
DEFAULT_KEY_TTL_SECONDS = 3600  # Keys auto-expire after 1 hour max


# ============================================================================
# ANALYTICS & MONITORING
# ============================================================================

# Query logging configuration
ENABLE_QUERY_LOGGING = os.getenv("ENABLE_QUERY_LOGGING", "true").lower() == "true"
QUERY_LOG_SAMPLE_RATE = float(os.getenv("QUERY_LOG_SAMPLE_RATE", "1.0"))  # Log 100% of queries
CACHE_ANALYSIS_LOOKBACK_MINUTES = 1440  # 24 hours for cache analysis

# Rate limit violation logging
ENABLE_VIOLATION_LOGGING = os.getenv("ENABLE_VIOLATION_LOGGING", "true").lower() == "true"
VIOLATION_BATCH_SIZE = 10  # Batch database writes for performance
VIOLATION_FLUSH_INTERVAL_SECONDS = 60  # Flush batch every 60 seconds

# Performance tracking
TRACK_PERFORMANCE_OVERHEAD = os.getenv("TRACK_PERFORMANCE_OVERHEAD", "true").lower() == "true"
MAX_OVERHEAD_MS = 5  # Alert if rate limit check takes >5ms


# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# IP detection configuration
USE_X_FORWARDED_FOR = True  # Trust X-Forwarded-For header (behind proxy)
TRUST_CLOUDFLARE_HEADERS = True  # Trust CF-Connecting-IP if present

# Fail closed configuration
FAIL_CLOSED_ON_ERROR = True  # Block requests if rate limiter fails (protects costs)
EXEMPT_ENDPOINTS = [
    "/health",  # Always allow health checks
    "/",  # Root endpoint (service info)
]

# Header configuration
ADD_HEADERS = True  # Include X-RateLimit-* headers in responses
HEADERS_ENABLED = [
    "X-RateLimit-Limit",
    "X-RateLimit-Remaining",
    "X-RateLimit-Reset",
]


# ============================================================================
# ENDPOINT SPECIFIC OVERRIDES
# ============================================================================

# Endpoints that need special handling
ENDPOINT_OVERRIDES: Dict[str, Dict[str, Any]] = {
    # AI analysis endpoints - strictest limits
    "/api/ai/analyze-jobs": {
        "limit": RATE_LIMIT_TIERS["expensive"]["ai_analysis"],
        "cost_per_request": 0.001,  # $0.001 per Gemini request
        "description": "Gemini AI job analysis",
    },
    "/api/ai/analysis-results/<job_id>": {
        "limit": RATE_LIMIT_TIERS["expensive"]["ai_analysis"],
        "cost_per_request": 0.001,
        "description": "Retrieve AI analysis results",
    },
    # Scraping endpoints - protect Apify costs
    "/api/scrape": {
        "limit": RATE_LIMIT_TIERS["expensive"]["job_scraping"],
        "cost_per_request": 0.30,  # ~$0.30 average per scrape job
        "description": "Apify job scraping",
    },
    "/api/intelligent-scrape": {
        "limit": RATE_LIMIT_TIERS["expensive"]["job_scraping"],
        "cost_per_request": 0.30,
        "description": "Intelligent context-aware scraping",
    },
    # Document generation
    "/resume": {
        "limit": RATE_LIMIT_TIERS["moderate"]["document_generation"],
        "cost_per_request": 0.0,
        "description": "Resume generation from template",
    },
    "/cover-letter": {
        "limit": RATE_LIMIT_TIERS["moderate"]["document_generation"],
        "cost_per_request": 0.0,
        "description": "Cover letter generation",
    },
    # Email endpoints
    "/api/email/send-job-application": {
        "limit": RATE_LIMIT_TIERS["moderate"]["email_send"],
        "cost_per_request": 0.0,
        "description": "Send job application email with attachments",
    },
    # Database operations
    "/api/db/jobs": {
        "limit": RATE_LIMIT_TIERS["cheap"]["db_read"],
        "cost_per_request": 0.0,
        "description": "List/search jobs",
    },
    # Dashboard
    "/dashboard": {
        "limit": RATE_LIMIT_TIERS["cheap"]["dashboard"],
        "cost_per_request": 0.0,
        "description": "Dashboard UI access",
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_limit_for_endpoint(endpoint: str) -> str:
    """
    Get rate limit string for specific endpoint.

    Args:
        endpoint: Endpoint path (e.g., '/api/ai/analyze-jobs')

    Returns:
        Rate limit string (e.g., '10/minute;50/hour')
    """
    if endpoint in ENDPOINT_OVERRIDES:
        return ENDPOINT_OVERRIDES[endpoint]["limit"]
    return RATE_LIMIT_TIERS["default"]


def get_cost_per_request(endpoint: str) -> float:
    """
    Get estimated cost per request for endpoint.

    Args:
        endpoint: Endpoint path

    Returns:
        Cost in USD per request
    """
    if endpoint in ENDPOINT_OVERRIDES:
        return ENDPOINT_OVERRIDES[endpoint].get("cost_per_request", 0.0)
    return 0.0


def calculate_max_daily_cost() -> float:
    """
    Calculate maximum daily cost if all rate limits are hit.

    Returns:
        Maximum daily cost in USD
    """
    total_cost = 0.0
    for endpoint, config in ENDPOINT_OVERRIDES.items():
        limit_str = config["limit"]
        cost = config.get("cost_per_request", 0.0)

        # Parse daily limit (e.g., "5/hour;20/day" -> 20)
        if "/day" in limit_str:
            daily_limit = int(limit_str.split("/day")[0].split(";")[-1])
        elif "/hour" in limit_str:
            # Extract hourly limit and multiply by 24
            hourly_limit = int(limit_str.split("/hour")[0].split(";")[-1])
            daily_limit = hourly_limit * 24
        else:
            # Minute-based limit, multiply by 1440
            minute_limit = int(limit_str.split("/minute")[0])
            daily_limit = minute_limit * 1440

        endpoint_cost = daily_limit * cost
        total_cost += endpoint_cost

    return total_cost


def get_memory_limit_bytes() -> int:
    """
    Get maximum memory limit in bytes.

    Returns:
        Memory limit in bytes
    """
    return MAX_MEMORY_MB * 1024 * 1024


def should_sample_query() -> bool:
    """
    Determine if current query should be logged (sampling).

    Returns:
        True if query should be logged
    """
    import random

    return random.random() < QUERY_LOG_SAMPLE_RATE


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================


def validate_configuration() -> bool:
    """
    Validate rate limiting configuration on startup.

    Returns:
        True if configuration is valid

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate memory limits
    if MAX_MEMORY_MB <= 0:
        raise ValueError("MAX_MEMORY_MB must be positive")
    if ALERT_THRESHOLD_MB >= MAX_MEMORY_MB:
        raise ValueError("ALERT_THRESHOLD_MB must be less than MAX_MEMORY_MB")

    # Validate sample rate
    if not 0.0 <= QUERY_LOG_SAMPLE_RATE <= 1.0:
        raise ValueError("QUERY_LOG_SAMPLE_RATE must be between 0.0 and 1.0")

    # Validate cleanup interval
    if CLEANUP_INTERVAL_SECONDS <= 0:
        raise ValueError("CLEANUP_INTERVAL_SECONDS must be positive")

    return True


# Validate on module import
validate_configuration()


# ============================================================================
# EXPORT CONFIGURATION SUMMARY
# ============================================================================


def get_configuration_summary() -> Dict[str, Any]:
    """
    Get human-readable configuration summary.

    Returns:
        Dictionary with configuration details
    """
    return {
        "storage": {
            "uri": STORAGE_URI,
            "type": "in-memory" if "memory://" in STORAGE_URI else "redis",
            "max_memory_mb": MAX_MEMORY_MB,
        },
        "rate_limits": {
            "expensive_operations": len(
                [k for k, v in ENDPOINT_OVERRIDES.items() if v["limit"] == RATE_LIMIT_TIERS["expensive"]["ai_analysis"]]
            ),
            "moderate_operations": len(
                [
                    k
                    for k, v in ENDPOINT_OVERRIDES.items()
                    if v["limit"] == RATE_LIMIT_TIERS["moderate"]["document_generation"]
                ]
            ),
            "cheap_operations": len(
                [k for k, v in ENDPOINT_OVERRIDES.items() if v["limit"] == RATE_LIMIT_TIERS["cheap"]["db_read"]]
            ),
            "default_limit": RATE_LIMIT_TIERS["default"],
        },
        "cost_protection": {
            "max_daily_cost_usd": round(calculate_max_daily_cost(), 2),
            "fail_closed_on_error": FAIL_CLOSED_ON_ERROR,
        },
        "monitoring": {
            "query_logging_enabled": ENABLE_QUERY_LOGGING,
            "sample_rate": QUERY_LOG_SAMPLE_RATE,
            "violation_logging_enabled": ENABLE_VIOLATION_LOGGING,
        },
        "cleanup": {
            "interval_seconds": CLEANUP_INTERVAL_SECONDS,
            "alert_threshold_mb": ALERT_THRESHOLD_MB,
        },
    }
