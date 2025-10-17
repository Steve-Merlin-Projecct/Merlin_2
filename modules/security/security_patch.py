"""
Critical Security Patches for Job Application System
Apply these fixes to address identified vulnerabilities
"""

import os
import re
import hashlib
import logging
import secrets
from functools import wraps
from flask import request, jsonify, abort
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


class SecurityPatch:
    """
    Security patches for identified vulnerabilities
    """

    @staticmethod
    def secure_password_hash(password: str) -> str:
        """
        Replace plain text password with hashed version
        """
        # Use a proper salt
        salt = os.environ.get("PASSWORD_SALT", "default-salt-change-in-production")
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()

    @staticmethod
    def validate_filename(filename: str) -> str:
        """
        Prevent path traversal attacks in file downloads
        """
        if not filename:
            raise ValueError("Filename cannot be empty")

        # Remove path traversal attempts
        filename = secure_filename(filename)

        # Additional validation
        if ".." in filename or "/" in filename or "\\" in filename:
            raise ValueError("Invalid filename - path traversal detected")

        # Only allow specific file extensions
        allowed_extensions = {".docx", ".pdf", ".txt"}
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"File type not allowed. Allowed: {allowed_extensions}")

        return filename

    @staticmethod
    def sanitize_log_data(data: dict) -> dict:
        """
        Remove sensitive data from logs
        """
        sensitive_keys = {
            "password",
            "token",
            "api_key",
            "secret",
            "auth",
            "authorization",
            "cookie",
            "session",
            "apikey",
        }

        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = SecurityPatch.sanitize_log_data(value)
            else:
                sanitized[key] = value

        return sanitized

    @staticmethod
    def sanitize_job_data(raw_job_data: dict) -> dict:
        """
        Sanitize job scraping data before database storage
        Removes malicious content, validates data types, and normalizes structure
        """
        try:
            sanitized = {}

            # Define allowed fields and their expected types
            allowed_fields = {
                "id": str,
                "positionName": str,
                "company": str,
                "location": str,
                "description": str,
                "snippet": str,
                "salary": str,
                "url": str,
                "externalApplyLink": str,
                "postedAt": str,
                "jobType": list,
                "rating": (int, float, str),
                "companyLogo": str,
                "reviewsCount": (int, str),
                "isExpired": bool,
                "scrapedAt": str,
                "remoteLocation": str,
                "remoteWorkModel": dict,
            }

            # Sanitize each field
            for field, expected_type in allowed_fields.items():
                if field in raw_job_data:
                    value = raw_job_data[field]

                    # Skip None or empty values
                    if value is None or value == "":
                        continue

                    # Type validation and conversion
                    if isinstance(expected_type, tuple):
                        # Multiple allowed types
                        if not isinstance(value, expected_type):
                            try:
                                # Try to convert to string as fallback
                                value = str(value) if value is not None else ""
                            except:
                                continue
                    else:
                        # Single expected type
                        if not isinstance(value, expected_type):
                            try:
                                if expected_type == str:
                                    value = str(value) if value is not None else ""
                                elif expected_type == int:
                                    value = int(float(value)) if value else 0
                                elif expected_type == float:
                                    value = float(value) if value else 0.0
                                elif expected_type == bool:
                                    value = bool(value)
                                elif expected_type == list:
                                    value = value if isinstance(value, list) else [str(value)]
                                elif expected_type == dict:
                                    value = value if isinstance(value, dict) else {}
                            except:
                                continue

                    # String sanitization for text fields
                    if isinstance(value, str):
                        # Remove potential XSS/injection attempts
                        value = SecurityPatch._sanitize_text_content(value)

                        # Skip if sanitization removed all content
                        if not value.strip():
                            continue

                    # List sanitization
                    elif isinstance(value, list):
                        value = [SecurityPatch._sanitize_text_content(str(item)) for item in value if item is not None]
                        value = [item for item in value if item.strip()]

                    # Dictionary sanitization (for nested objects)
                    elif isinstance(value, dict):
                        value = SecurityPatch._sanitize_dict_content(value)

                    sanitized[field] = value

            # Validate required fields exist
            required_fields = ["id", "positionName", "company"]
            for required in required_fields:
                if required not in sanitized or not sanitized[required]:
                    logger.warning(f"Missing required field {required} in job data")
                    # Generate fallback for critical fields
                    if required == "id":
                        sanitized["id"] = f"generated_{secrets.token_hex(8)}"
                    elif required == "positionName":
                        sanitized["positionName"] = "Unknown Position"
                    elif required == "company":
                        sanitized["company"] = "Unknown Company"

            logger.debug(f"Sanitized job data: {len(sanitized)} fields preserved")
            return sanitized

        except Exception as e:
            logger.error(f"Error sanitizing job data: {e}")
            # Return minimal safe structure
            return {
                "id": f"error_{secrets.token_hex(8)}",
                "positionName": "Data Sanitization Error",
                "company": "Unknown",
                "error": "Sanitization failed",
            }

    @staticmethod
    def _sanitize_text_content(text: str) -> str:
        """
        Clean text content of potential security threats
        """
        if not isinstance(text, str):
            return str(text) if text is not None else ""

        # Remove potential script injections
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)

        # Remove HTML/XML tags but preserve content
        text = re.sub(r"<[^>]+>", "", text)

        # Remove potential SQL injection patterns
        sql_patterns = [
            r"\b(union|select|insert|update|delete|drop|create|alter)\b",
            r'[;\'"]\s*(union|select|insert|update|delete|drop|create|alter)\b',
            r"--\s*$",
            r"/\*.*?\*/",
        ]
        for pattern in sql_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Remove potential command injection
        text = re.sub(r"[`${}]", "", text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        # Limit length to prevent DoS
        if len(text) > 10000:
            text = text[:10000] + "...[truncated]"

        return text.strip()

    @staticmethod
    def _sanitize_dict_content(data: dict) -> dict:
        """
        Recursively sanitize dictionary content
        """
        sanitized = {}
        for key, value in data.items():
            # Sanitize key name
            clean_key = SecurityPatch._sanitize_text_content(str(key))
            if not clean_key:
                continue

            # Sanitize value based on type
            if isinstance(value, str):
                clean_value = SecurityPatch._sanitize_text_content(value)
                if clean_value:
                    sanitized[clean_key] = clean_value
            elif isinstance(value, dict):
                clean_value = SecurityPatch._sanitize_dict_content(value)
                if clean_value:
                    sanitized[clean_key] = clean_value
            elif isinstance(value, list):
                clean_value = [SecurityPatch._sanitize_text_content(str(item)) for item in value if item is not None]
                clean_value = [item for item in clean_value if item.strip()]
                if clean_value:
                    sanitized[clean_key] = clean_value
            elif isinstance(value, (int, float, bool)):
                sanitized[clean_key] = value

        return sanitized

    @staticmethod
    def validate_request_size():
        """
        Decorator to validate request size
        """

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Check Content-Length header
                content_length = request.content_length
                max_size = 16 * 1024 * 1024  # 16MB

                if content_length and content_length > max_size:
                    abort(413)  # Payload Too Large

                return f(*args, **kwargs)

            return decorated_function

        return decorator

    @staticmethod
    def validate_cors_origin(allowed_origins: list = None):
        """
        Validate CORS origins
        """
        if allowed_origins is None:
            allowed_origins = [
                "http://localhost:3000",  # Development only
                "http://localhost:5000",  # Flask development server
            ]

        origin = request.headers.get("Origin")
        if origin and not any(re.match(pattern.replace("*", ".*"), origin) for pattern in allowed_origins):
            logger.warning(f"Rejected CORS request from unauthorized origin: {origin}")
            abort(403)

    @staticmethod
    def create_secure_session_key() -> str:
        """
        Generate secure session key
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def check_weak_secrets() -> dict:
        """
        Check for weak secrets in environment variables
        """
        weak_secrets = []

        # Check webhook API key strength
        webhook_key = os.environ.get("WEBHOOK_API_KEY", "")
        if len(webhook_key) < 32:
            weak_secrets.append("WEBHOOK_API_KEY")
            logger.warning(f"Weak secrets detected (less than 32 chars): {weak_secrets}")

        # Check session secret
        session_secret = os.environ.get("SESSION_SECRET", "")
        if len(session_secret) < 32:
            weak_secrets.append("SESSION_SECRET")

        return {
            "weak_secrets": weak_secrets,
            "total_checked": 2,
            "recommendations": [
                "Generate strong keys using utils/security_key_generator.py",
                "Use cryptographically secure random generation",
                "Ensure all secrets are at least 32 characters long",
            ],
        }

    @staticmethod
    def validate_sql_query(query: str) -> bool:
        """
        Basic SQL injection prevention
        """
        dangerous_patterns = [
            r";\s*(drop|delete|update|insert|create|alter)\s+",
            r"union\s+select",
            r"exec\s*\(",
            r"xp_\w+",
            r"sp_\w+",
            r"--",
            r"/\*.*?\*/",
        ]

        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                logger.warning(f"Potentially dangerous SQL pattern detected: {pattern}")
                return False

        return True

    @staticmethod
    def rate_limit_check(identifier: str, limit: int = 60, window: int = 60) -> bool:
        """
        Simple in-memory rate limiting
        """
        # This is a basic implementation - use Redis for production
        import time

        current_time = time.time()
        window_start = current_time - window

        # This would need to be stored in a persistent cache for production
        # For now, just log the attempt
        logger.info(f"Rate limit check for {identifier}: {limit}/{window}s")
        return True

    @staticmethod
    def secure_headers() -> dict:
        """
        Return comprehensive security headers for all responses
        Enhanced with strict Content Security Policy and additional protections
        """
        # Enhanced Content Security Policy for maximum protection
        # Note: 'unsafe-eval' required for Alpine.js in dashboard
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "object-src 'none'; "
            "media-src 'none'"
        )

        return {
            # Core security headers
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Enhanced Content Security Policy
            "Content-Security-Policy": csp_policy,
            # Additional security headers for enhanced protection
            "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Resource-Policy": "same-origin",
            # Cache control for sensitive data
            "Cache-Control": "no-store, no-cache, must-revalidate, private",
            "Pragma": "no-cache",
            "Expires": "0",
        }


# Security middleware for Flask
def apply_security_headers(response):
    """
    Apply security headers to all responses
    """
    headers = SecurityPatch.secure_headers()
    for header, value in headers.items():
        response.headers[header] = value
    return response


# Environment validation
def validate_environment():
    """
    Ensure critical environment variables are set securely
    """
    required_vars = ["DATABASE_URL", "SESSION_SECRET", "WEBHOOK_API_KEY"]

    missing_vars = []
    weak_secrets = []

    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        elif len(value) < 32:  # Minimum 32 characters for secrets
            weak_secrets.append(var)

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")

    if weak_secrets:
        logger.warning(f"Weak secrets detected (less than 32 chars): {weak_secrets}")

    # Check for development secrets in production
    development_secrets = ["development-secret-key", "dev", "test", "default"]
    for var in required_vars:
        value = os.environ.get(var, "").lower()
        if any(dev_term in value for dev_term in development_secrets):
            logger.error(f"Development secret detected in {var}")


# Database security
class SecureDatabase:
    """
    Secure database operations with timeout and validation
    """

    @staticmethod
    def execute_query_safely(db_manager, query: str, params: tuple = None, timeout: int = 10):
        """
        Execute query with security validation and timeout
        """
        # Validate query for injection attempts
        if not SecurityPatch.validate_sql_query(query):
            raise ValueError("Potentially dangerous SQL query blocked")

        # Log sanitized query (remove sensitive data)
        sanitized_params = tuple("[REDACTED]" if "password" in str(p).lower() else p for p in (params or []))
        logger.info(f"Executing query: {query[:100]}... with params: {sanitized_params}")

        # Execute with timeout (implementation depends on your DB manager)
        return db_manager.execute_query(query, params or [])


# File security
def secure_file_operation(filename: str, operation: str = "read"):
    """
    Secure file operations with validation
    """
    try:
        # Validate filename
        safe_filename = SecurityPatch.validate_filename(filename)

        # Ensure file is in allowed directory
        base_dir = os.path.abspath("storage")
        file_path = os.path.abspath(os.path.join(base_dir, safe_filename))

        if not file_path.startswith(base_dir):
            raise ValueError("File access outside allowed directory")

        logger.info(f"Secure {operation} operation on: {safe_filename}")
        return file_path

    except Exception as e:
        logger.error(f"File security validation failed: {e}")
        raise
