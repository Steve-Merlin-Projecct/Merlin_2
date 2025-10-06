"""
Link Tracking Security Controls

Provides comprehensive security controls for the link tracking system including
input validation, URL validation, rate limiting, and security monitoring.

Version: 2.16.5
Date: July 28, 2025
"""

import re
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, quote
import logging
from functools import wraps
from flask import request, jsonify, g
import ipaddress

logger = logging.getLogger(__name__)


class SecurityControls:
    """
    Comprehensive security controls for link tracking system
    """

    def __init__(self):
        self.rate_limit_storage = {}  # In production, use Redis
        self.blocked_ips = set()
        self.allowed_domains = {
            "linkedin.com",
            "www.linkedin.com",
            "calendly.com",
            "www.calendly.com",
            "indeed.com",
            "ca.indeed.com",
            "www.indeed.com",
            "github.com",
            "www.github.com",
            "company.com",
            "careers.company.com",  # Add specific company domains
        }
        self.max_url_length = 2000
        self.max_description_length = 500

    def validate_tracking_id(self, tracking_id: str) -> Tuple[bool, str]:
        """
        Validate tracking ID format and content.

        Args:
            tracking_id: The tracking identifier to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not tracking_id:
            return False, "Tracking ID is required"

        if not isinstance(tracking_id, str):
            return False, "Tracking ID must be a string"

        if len(tracking_id) < 5 or len(tracking_id) > 100:
            return False, "Tracking ID length must be between 5 and 100 characters"

        # Pattern: lt_ followed by 16 hex characters
        pattern = r"^lt_[a-f0-9]{16}$"
        if not re.match(pattern, tracking_id):
            return False, "Invalid tracking ID format"

        # Additional entropy check
        hex_part = tracking_id[3:]  # Remove 'lt_' prefix
        if len(set(hex_part)) < 4:  # Ensure sufficient entropy
            return False, "Tracking ID has insufficient entropy"

        return True, ""

    def validate_url(self, url: str, allow_internal: bool = False) -> Tuple[bool, str]:
        """
        Validate URL for security and policy compliance.

        Args:
            url: The URL to validate
            allow_internal: Whether to allow internal URLs

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL is required"

        if not isinstance(url, str):
            return False, "URL must be a string"

        if len(url) > self.max_url_length:
            return False, f"URL length exceeds maximum of {self.max_url_length} characters"

        # Basic URL format validation
        try:
            parsed = urlparse(url)
        except Exception:
            return False, "Invalid URL format"

        if not parsed.scheme:
            return False, "URL must include protocol (http/https)"

        if parsed.scheme not in ["http", "https"]:
            return False, "URL must use HTTP or HTTPS protocol"

        if not parsed.netloc:
            return False, "URL must include domain"

        # Check for suspicious patterns
        suspicious_patterns = [
            "javascript:",
            "data:",
            "vbscript:",
            "file:",
            "about:",
            "chrome:",
            "resource:",
            "moz-extension:",
        ]

        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                return False, f"URL contains suspicious pattern: {pattern}"

        # Domain validation
        domain = parsed.netloc.lower()

        # Remove port if present
        if ":" in domain:
            domain = domain.split(":")[0]

        # Check against allowed domains (if not allowing all)
        if not allow_internal and domain not in self.allowed_domains:
            return False, f"Domain '{domain}' is not in allowed domains list"

        # Check for IP addresses (suspicious for job applications)
        try:
            ipaddress.ip_address(domain)
            return False, "Direct IP addresses not allowed"
        except ValueError:
            pass  # Not an IP, which is good

        # Check for suspicious subdomains
        suspicious_subdomains = ["phishing", "malware", "spam", "fake"]
        for subdomain in suspicious_subdomains:
            if subdomain in domain:
                return False, f"Suspicious subdomain detected: {subdomain}"

        return True, ""

    def validate_link_function(self, link_function: str) -> Tuple[bool, str]:
        """
        Validate link function category.

        Args:
            link_function: The link function to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not link_function:
            return False, "Link function is required"

        if not isinstance(link_function, str):
            return False, "Link function must be a string"

        allowed_functions = {
            "LinkedIn",
            "Calendly",
            "Company_Website",
            "Apply_Now",
            "Job_Posting",
            "Portfolio",
            "GitHub",
            "Resume",
            "Cover_Letter",
            "References",
            "Contact",
        }

        if link_function not in allowed_functions:
            return False, f"Invalid link function. Allowed: {', '.join(allowed_functions)}"

        return True, ""

    def validate_link_type(self, link_type: str) -> Tuple[bool, str]:
        """
        Validate link type category.

        Args:
            link_type: The link type to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not link_type:
            return False, "Link type is required"

        if not isinstance(link_type, str):
            return False, "Link type must be a string"

        allowed_types = {
            "profile",
            "job_posting",
            "application",
            "networking",
            "document",
            "external",
            "internal",
            "contact",
        }

        if link_type not in allowed_types:
            return False, f"Invalid link type. Allowed: {', '.join(allowed_types)}"

        return True, ""

    def validate_uuid(self, uuid_str: str, field_name: str) -> Tuple[bool, str]:
        """
        Validate UUID format.

        Args:
            uuid_str: The UUID string to validate
            field_name: Field name for error messages

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not uuid_str:
            return True, ""  # UUIDs are optional in most cases

        if not isinstance(uuid_str, str):
            return False, f"{field_name} must be a string"

        # UUID pattern: 8-4-4-4-12 hex digits
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        if not re.match(uuid_pattern, uuid_str.lower()):
            return False, f"Invalid {field_name} format"

        return True, ""

    def sanitize_input(self, input_str: str, max_length: int = 1000) -> str:
        """
        Sanitize string input for safe storage and display.

        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not input_str or not isinstance(input_str, str):
            return ""

        # Trim to max length
        sanitized = input_str[:max_length]

        # Remove null bytes and control characters
        sanitized = "".join(char for char in sanitized if ord(char) >= 32 or char in "\t\n\r")

        # Remove potentially dangerous characters for SQL injection
        dangerous_chars = ["<", ">", '"', "'", "&", "\x00"]
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")

        return sanitized.strip()

    def generate_secure_tracking_id(self) -> str:
        """
        Generate cryptographically secure tracking ID.

        Returns:
            Secure tracking identifier
        """
        # Use secrets module for cryptographically secure random generation
        random_bytes = secrets.token_bytes(16)
        hex_string = random_bytes.hex()

        # Add timestamp-based component for uniqueness (but not predictability)
        time_component = hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]

        # Combine and hash to ensure unpredictability
        combined = f"{hex_string}{time_component}"
        final_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]

        return f"lt_{final_hash}"

    def check_rate_limit(self, key: str, limit: int, window: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limits.

        Args:
            key: Rate limiting key (IP, API key, etc.)
            limit: Maximum requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        current_time = time.time()

        # Clean old entries
        if key in self.rate_limit_storage:
            self.rate_limit_storage[key] = [
                timestamp for timestamp in self.rate_limit_storage[key] if current_time - timestamp < window
            ]
        else:
            self.rate_limit_storage[key] = []

        # Check current count
        current_count = len(self.rate_limit_storage[key])

        rate_limit_info = {
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "reset_time": current_time + window,
            "window": window,
        }

        if current_count >= limit:
            logger.warning(f"Rate limit exceeded for key: {key}")
            return False, rate_limit_info

        # Add current request
        self.rate_limit_storage[key].append(current_time)
        rate_limit_info["remaining"] -= 1

        return True, rate_limit_info

    def get_client_ip(self, request) -> str:
        """
        Get client IP address considering proxy headers.

        Args:
            request: Flask request object

        Returns:
            Client IP address
        """
        # Check proxy headers in order of preference
        if request.headers.get("X-Forwarded-For"):
            # Get the first IP in the chain (original client)
            ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
        elif request.headers.get("X-Real-IP"):
            ip = request.headers.get("X-Real-IP")
        elif request.headers.get("CF-Connecting-IP"):  # Cloudflare
            ip = request.headers.get("CF-Connecting-IP")
        else:
            ip = request.remote_addr

        # Validate IP format
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            logger.warning(f"Invalid IP address detected: {ip}")
            return request.remote_addr or "0.0.0.0"

    def is_blocked_ip(self, ip: str) -> bool:
        """
        Check if IP address is blocked.

        Args:
            ip: IP address to check

        Returns:
            True if IP is blocked
        """
        return ip in self.blocked_ips

    def block_ip(self, ip: str, reason: str = "Security violation"):
        """
        Block an IP address.

        Args:
            ip: IP address to block
            reason: Reason for blocking
        """
        self.blocked_ips.add(ip)
        logger.warning(f"Blocked IP {ip}: {reason}")

    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """
        Log security-related events.

        Args:
            event_type: Type of security event
            details: Event details
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        """
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "source_ip": details.get("ip_address", "unknown"),
        }

        log_method = getattr(logger, severity.lower(), logger.info)
        log_method(f"Security Event [{event_type}]: {details}")

        # In production, send to SIEM or security monitoring system
        # self.send_to_siem(log_entry)


# Decorator functions for API endpoints


def require_api_key(f):
    """Decorator to require API key authentication."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        security = SecurityControls()

        api_key = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not api_key:
            security.log_security_event(
                "AUTH_MISSING_API_KEY", {"ip_address": security.get_client_ip(request)}, "WARNING"
            )
            return jsonify({"error": "API key required"}), 401

        # In production, validate against database
        # For now, use environment variable
        import os

        valid_api_key = os.environ.get("LINK_TRACKING_API_KEY")

        if not valid_api_key or api_key != valid_api_key:
            security.log_security_event(
                "AUTH_INVALID_API_KEY",
                {"ip_address": security.get_client_ip(request), "api_key": api_key[:8] + "..."},
                "WARNING",
            )
            return jsonify({"error": "Invalid API key"}), 401

        return f(*args, **kwargs)

    return decorated_function


def rate_limit(limit: int = 100, window: int = 3600):
    """Decorator to apply rate limiting."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            security = SecurityControls()

            ip = security.get_client_ip(request)

            # Check if IP is blocked
            if security.is_blocked_ip(ip):
                return jsonify({"error": "IP address blocked"}), 403

            # Check rate limit
            allowed, rate_info = security.check_rate_limit(ip, limit, window)

            if not allowed:
                security.log_security_event(
                    "RATE_LIMIT_EXCEEDED", {"ip_address": ip, "limit": limit, "window": window}, "WARNING"
                )

                response = jsonify(
                    {
                        "error": "Rate limit exceeded",
                        "limit": rate_info["limit"],
                        "window": rate_info["window"],
                        "retry_after": rate_info["window"],
                    }
                )
                response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(int(rate_info["reset_time"]))
                response.headers["Retry-After"] = str(rate_info["window"])

                return response, 429

            # Add rate limit headers to response
            response = f(*args, **kwargs)
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(int(rate_info["reset_time"]))

            return response

        return decorated_function

    return decorator


def validate_input(f):
    """Decorator to validate common input fields."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        security = SecurityControls()

        if request.method in ["POST", "PUT", "PATCH"]:
            data = request.get_json()

            if not data:
                return jsonify({"error": "Request body required"}), 400

            # Validate common fields
            errors = []

            if "original_url" in data:
                valid, error = security.validate_url(data["original_url"])
                if not valid:
                    errors.append(f"original_url: {error}")

            if "link_function" in data:
                valid, error = security.validate_link_function(data["link_function"])
                if not valid:
                    errors.append(f"link_function: {error}")

            if "link_type" in data:
                valid, error = security.validate_link_type(data["link_type"])
                if not valid:
                    errors.append(f"link_type: {error}")

            if "job_id" in data and data["job_id"]:
                valid, error = security.validate_uuid(data["job_id"], "job_id")
                if not valid:
                    errors.append(f"job_id: {error}")

            if "application_id" in data and data["application_id"]:
                valid, error = security.validate_uuid(data["application_id"], "application_id")
                if not valid:
                    errors.append(f"application_id: {error}")

            if errors:
                security.log_security_event(
                    "INPUT_VALIDATION_FAILED",
                    {"ip_address": security.get_client_ip(request), "errors": errors, "data_keys": list(data.keys())},
                    "WARNING",
                )
                return jsonify({"error": "Validation failed", "details": errors}), 400

        return f(*args, **kwargs)

    return decorated_function
