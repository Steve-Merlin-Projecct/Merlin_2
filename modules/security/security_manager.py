"""
Security Manager for Job Scraping System
Handles API security, input validation, and data sanitization

This module uses bleach for HTML sanitization and XSS prevention.
Bleach is loaded on-demand to avoid unnecessary startup overhead.
"""

import os
import re
import json
import time
import hashlib
import logging
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from modules.database.database_manager import DatabaseManager


# On-demand bleach loading - only install when HTML sanitization is needed
def _get_bleach_module():
    """Get bleach module with on-demand installation"""
    try:
        # Add utils directory to path for dependency manager
        utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "utils")
        if utils_path not in sys.path:
            sys.path.append(utils_path)

        from dependency_manager import get_bleach_module

        return get_bleach_module()
    except ImportError as e:
        logging.warning(f"bleach not available for HTML sanitization: {e}")

        # Create a minimal bleach-like interface for basic sanitization
        class MockBleach:
            """
            Minimal bleach-like interface for basic sanitization when bleach is unavailable
            Provides essential HTML cleaning functions for security purposes
            """

            def clean(self, text, tags=None, attributes=None, strip=False):
                """
                Basic HTML tag removal - not as comprehensive as bleach

                Args:
                    text: Text to clean
                    tags: Allowed tags (ignored in mock implementation)
                    attributes: Allowed attributes (ignored in mock implementation)
                    strip: Whether to strip tags (always strips in mock)

                Returns:
                    str: Cleaned text with HTML tags removed
                """
                if not text:
                    return text
                # Remove basic HTML tags
                clean_text = re.sub(r"<[^>]+>", "", str(text))
                return clean_text.strip()

        logging.info("Using mock bleach interface for basic sanitization")
        return MockBleach()


# Initialize bleach module (with lazy loading)
bleach = None


def _ensure_bleach_loaded():
    """Ensure bleach is loaded when needed"""
    global bleach
    if bleach is None:
        bleach = _get_bleach_module()
        logging.info("bleach loaded for HTML sanitization")
    return bleach


logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Comprehensive security manager for job scraping operations
    """

    def __init__(self):
        """Initialize security manager"""
        self.db_manager = DatabaseManager()
        self.rate_limits = {
            "apify_requests_per_hour": 100,
            "database_writes_per_minute": 500,
            "max_job_description_length": 50000,
        }

    def validate_apify_token(self, token: str) -> bool:
        """
        Validate Apify API token format and permissions

        Args:
            token: API token to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not token:
            return False

        # Check token format (Apify tokens are typically 32-40 chars)
        if not re.match(r"^[a-zA-Z0-9_-]{32,40}$", token):
            logger.warning("Invalid Apify token format")
            return False

        # Optional: Test token with minimal API call
        try:
            import requests

            response = requests.get(
                "https://api.apify.com/v2/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False

    def check_rate_limit(self, operation: str, identifier: str) -> bool:
        """
        Check if operation is within rate limits

        Args:
            operation: Type of operation (e.g., 'apify_request', 'database_write')
            identifier: Unique identifier for rate limiting

        Returns:
            bool: True if within limits, False if rate limited
        """
        current_time = datetime.now()

        # Check database for recent operations
        if operation == "apify_request":
            recent_requests = self.db_manager.execute_query(
                """
                SELECT COUNT(*) as count 
                FROM raw_job_scrapes 
                WHERE scrape_timestamp > %s
            """,
                (current_time - timedelta(hours=1),),
            )

            if recent_requests and recent_requests[0]["count"] >= self.rate_limits["apify_requests_per_hour"]:
                logger.warning(f"Rate limit exceeded for {operation}: {identifier}")
                return False

        return True

    def sanitize_job_data(self, raw_data: Dict) -> Dict:
        """
        Sanitize scraped job data to prevent injection attacks

        Args:
            raw_data: Raw job data from scraper

        Returns:
            Dict: Sanitized job data
        """
        sanitized = {}

        # Define allowed fields and their types
        allowed_fields = {
            "id": str,
            "positionName": str,
            "companyName": str,
            "location": str,
            "salary": str,
            "description": str,
            "descriptionHTML": str,
            "companyLogo": str,
            "reviewsCount": int,
            "rating": float,
            "jobType": list,
            "postedAt": str,
            "isExpired": bool,
            "externalApplyLink": str,
        }

        for field, expected_type in allowed_fields.items():
            if field in raw_data:
                value = raw_data[field]

                # Type validation
                if expected_type == str and isinstance(value, str):
                    # Sanitize string content
                    sanitized[field] = self._sanitize_string(value)
                elif expected_type == int and isinstance(value, (int, float)):
                    sanitized[field] = int(value)
                elif expected_type == float and isinstance(value, (int, float)):
                    sanitized[field] = float(value)
                elif expected_type == bool:
                    sanitized[field] = bool(value)
                elif expected_type == list and isinstance(value, list):
                    # Sanitize list items
                    sanitized[field] = [self._sanitize_string(str(item)) for item in value]
                else:
                    logger.warning(f"Type mismatch for field {field}: expected {expected_type}, got {type(value)}")

        return sanitized

    def _sanitize_string(self, text: str) -> str:
        """
        Sanitize string content to prevent XSS and injection attacks

        Args:
            text: Raw string to sanitize

        Returns:
            str: Sanitized string
        """
        if not isinstance(text, str):
            return str(text)

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Limit length
        if len(text) > self.rate_limits["max_job_description_length"]:
            text = text[: self.rate_limits["max_job_description_length"]] + "..."

        # Remove potentially dangerous HTML/script content
        # Ensure bleach is loaded when HTML sanitization is needed
        bleach = _ensure_bleach_loaded()
        text = bleach.clean(text, tags=["p", "br", "strong", "em", "ul", "ol", "li"], strip=True)

        # Remove SQL injection patterns
        sql_patterns = [
            r"(union|select|insert|update|delete|drop|create|alter)\s+",
            r'[\'";]',
            r"--",
            r"/\*.*?\*/",
            r"xp_\w+",
            r"sp_\w+",
        ]

        for pattern in sql_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        return text

    def validate_search_params(self, params: Dict) -> bool:
        """
        Validate search parameters to prevent abuse

        Args:
            params: Search parameters dictionary

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["position", "location", "country"]

        # Check required fields
        for field in required_fields:
            if field not in params or not params[field]:
                logger.warning(f"Missing required field: {field}")
                return False

        # Validate field lengths
        max_lengths = {"position": 100, "location": 100, "country": 5}

        for field, max_len in max_lengths.items():
            if len(str(params.get(field, ""))) > max_len:
                logger.warning(f"Field {field} exceeds maximum length {max_len}")
                return False

        # Validate country code
        allowed_countries = ["CA", "US", "UK", "AU"]
        if params.get("country") not in allowed_countries:
            logger.warning(f"Invalid country code: {params.get('country')}")
            return False

        return True

    def generate_request_signature(self, params: Dict) -> str:
        """
        Generate unique signature for request deduplication

        Args:
            params: Request parameters

        Returns:
            str: Unique signature hash
        """
        # Create deterministic string from params
        param_string = json.dumps(params, sort_keys=True)

        # Add timestamp (rounded to hour for deduplication)
        timestamp = datetime.now().strftime("%Y-%m-%d-%H")
        combined = f"{param_string}_{timestamp}"

        # Generate SHA256 hash
        return hashlib.sha256(combined.encode()).hexdigest()

    def log_security_event(self, event_type: str, details: Dict):
        """
        Log security-related events for monitoring

        Args:
            event_type: Type of security event
            details: Event details
        """
        security_log = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "user_agent": os.environ.get("HTTP_USER_AGENT", "Unknown"),
            "ip_address": os.environ.get("HTTP_X_FORWARDED_FOR", "Unknown"),
        }

        logger.info(f"Security event: {json.dumps(security_log)}")

        # Store in database for monitoring
        try:
            self.db_manager.execute_query(
                """
                INSERT INTO security_logs (event_type, details, created_at)
                VALUES (%s, %s, %s)
            """,
                (event_type, json.dumps(security_log), datetime.now()),
            )
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
