"""
Security Configuration for Job Scraping System
Defines security settings, rate limits, and access controls
"""

# API Security Settings
API_SECURITY = {
    "apify": {
        "rate_limit_per_hour": 100,
        "max_concurrent_requests": 5,
        "timeout_seconds": 30,
        "retry_attempts": 3,
        "cost_alert_threshold": 50.00,  # USD
    },
    "database": {"max_query_time_seconds": 10, "max_connections": 20, "connection_timeout": 5},
}

# Data Validation Rules
DATA_VALIDATION = {
    "job_description": {
        "max_length": 50000,
        "min_length": 10,
        "forbidden_patterns": [
            r"<script.*?>",
            r"javascript:",
            r"vbscript:",
            r"onload=",
            r"onclick=",
            r"eval\(",
            r"document\.write",
        ],
    },
    "company_name": {"max_length": 300, "forbidden_chars": ["<", ">", '"', "'", "&", ";"]},
    "location": {
        "max_length": 200,
        "allowed_countries": ["CA", "US", "UK", "AU"],
        "valid_formats": [
            r"^[A-Za-z\s,.-]+,\s*[A-Z]{2}$",  # City, Province
            r"^[A-Za-z\s,.-]+,\s*[A-Z]{2},\s*[A-Z]{2,3}$",  # City, Province, Country
        ],
    },
}

# Rate Limiting Configuration
RATE_LIMITS = {
    "scraping": {"requests_per_hour": 100, "requests_per_day": 1000, "burst_limit": 10},
    "database": {"writes_per_minute": 500, "reads_per_minute": 2000},
    "api_endpoints": {"general": {"per_minute": 60}, "scraping": {"per_hour": 50}, "data_export": {"per_day": 10}},
}

# Security Headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
}

# Allowed File Types and Sizes
FILE_SECURITY = {
    "upload": {"allowed_extensions": [".docx", ".pdf", ".txt"], "max_size_mb": 10, "scan_for_malware": True},
    "download": {
        "allowed_types": ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
        "virus_scan_enabled": False,  # Set to True in production
    },
}

# Database Access Control
DATABASE_SECURITY = {
    "readonly_user": {
        "allowed_tables": ["cleaned_job_scrapes", "jobs", "job_content_analysis", "content_library"],
        "forbidden_tables": ["users", "user_job_preferences", "document_jobs", "security_logs", "raw_job_scrapes"],
        "max_query_time": 10,
        "max_rows_returned": 1000,
    },
    "scraper_user": {
        "allowed_operations": ["INSERT", "SELECT"],
        "allowed_tables": ["raw_job_scrapes", "cleaned_job_scrapes", "jobs"],
        "rate_limit_per_minute": 100,
    },
}

# Logging and Monitoring
LOGGING_CONFIG = {
    "security_events": {
        "enabled": True,
        "log_level": "INFO",
        "retention_days": 90,
        "alert_on": ["rate_limit_exceeded", "invalid_token", "suspicious_activity", "injection_attempt"],
    },
    "audit_trail": {
        "enabled": True,
        "include_requests": True,
        "include_responses": False,  # Sensitive data
        "retention_days": 365,
    },
}

# Alert Thresholds
ALERT_THRESHOLDS = {
    "cost_monitoring": {"daily_spend_limit": 2.50, "monthly_spend_limit": 50.00, "alert_at_percentage": 80},
    "performance": {"api_response_time_ms": 5000, "database_query_time_ms": 2000, "error_rate_percentage": 5},
    "security": {"failed_requests_per_hour": 50, "suspicious_patterns_per_day": 10, "large_data_dumps": 5000},  # rows
}

# Environment-Specific Settings
ENVIRONMENT_CONFIG = {
    "development": {
        "debug_logging": True,
        "security_level": "relaxed",
        "rate_limits_enforced": False,
        "api_validation_strict": False,
    },
    "production": {
        "debug_logging": False,
        "security_level": "strict",
        "rate_limits_enforced": True,
        "api_validation_strict": True,
        "malware_scanning": True,
    },
}
