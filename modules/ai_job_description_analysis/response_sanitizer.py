"""
Response Sanitization Layer - Defense Layer 6
Sanitizes LLM responses before database storage to prevent malicious data persistence

This is the LAST line of defense if all other layers fail:
- Layer 1: Input sanitization (job descriptions)
- Layer 2: Prompt-embedded security tokens
- Layer 3: Round-trip token validation
- Layer 4: Hash-and-replace prompt protection
- Layer 5: Output structure validation
- Layer 6: Response sanitization (THIS MODULE) ← Final safeguard

Purpose: Even if prompt injection succeeds, prevent malicious payloads from:
- SQL injection (though we use parameterized queries)
- XSS attacks (sanitize HTML/JS in text fields)
- Command injection (strip shell metacharacters)
- Path traversal (sanitize file paths)
- Data exfiltration (detect and block suspicious URLs)
"""

import re
import html
import logging
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ResponseSanitizer:
    """
    Sanitizes LLM response data before database storage
    Defense-in-depth: Final layer to prevent malicious data persistence
    """

    def __init__(self):
        # SQL injection patterns (even though we use parameterized queries)
        self.sql_injection_patterns = [
            r"(?i)(union\s+select)",
            r"(?i)(drop\s+table)",
            r"(?i)(delete\s+from)",
            r"(?i)(insert\s+into)",
            r"(?i)(update\s+\w+\s+set)",
            r"(?i)(exec\s*\()",
            r"(?i)(execute\s+immediate)",
            r"(?i)(xp_cmdshell)",
            r"--\s*$",  # SQL comment
            r"/\*.*\*/",  # SQL block comment
        ]

        # Command injection patterns
        self.command_injection_patterns = [
            r"[;&|`$()]",  # Shell metacharacters
            r"\$\(",  # Command substitution
            r"`.*`",  # Backticks
            r">\s*/",  # Output redirection to system paths
        ]

        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",  # Event handlers (onclick, onerror, etc.)
            r"<iframe",
            r"<embed",
            r"<object",
        ]

        # Path traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",  # Parent directory
            r"\.\.",
            r"%2e%2e",  # URL-encoded ..
            r"\.\.\\",  # Windows path traversal
        ]

        # Suspicious URL patterns (potential data exfiltration)
        self.suspicious_url_patterns = [
            r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",  # Raw IP addresses
            r"https?://[a-z0-9-]+\.(?:ngrok|localtunnel|serveo)\.io",  # Tunneling services
            r"https?://[a-z0-9-]+\.(?:duckdns|no-ip)\.org",  # Dynamic DNS
        ]

        # Fields that should NEVER contain URLs (security-sensitive)
        self.url_prohibited_fields = {
            "skill_name",
            "industry",
            "sub_industry",
            "job_function",
            "seniority_level",
            "job_title",
            "company_name",
            "department",
        }

        # Fields that can contain URLs but need validation
        self.url_allowed_fields = {
            "application_link",
            "application_email",
            "company_website",
        }

        # Maximum safe string length (prevent DoS via huge strings)
        self.max_string_length = 10000

    def sanitize_analysis_result(
        self, result: Dict, job_id: str
    ) -> tuple[Dict, List[str]]:
        """
        Sanitize entire analysis result before database storage

        Args:
            result: Raw analysis result from LLM
            job_id: Job ID for logging

        Returns:
            Tuple of (sanitized_result, warnings)
        """
        warnings = []
        sanitized_result = {}

        try:
            # Sanitize each field recursively
            for key, value in result.items():
                sanitized_value, field_warnings = self._sanitize_field(
                    key, value, job_id, path=key
                )
                sanitized_result[key] = sanitized_value
                warnings.extend(field_warnings)

            # Log warnings if any
            if warnings:
                logger.warning(
                    f"⚠️ Response sanitization warnings for job {job_id}: {len(warnings)} issues found"
                )
                for warning in warnings[:5]:  # Log first 5 warnings
                    logger.warning(f"  - {warning}")

            return sanitized_result, warnings

        except Exception as e:
            logger.error(f"Response sanitization failed for job {job_id}: {e}")
            # Return original result but log critical error
            warnings.append(f"CRITICAL: Sanitization failed: {str(e)}")
            return result, warnings

    def _sanitize_field(
        self, key: str, value: Any, job_id: str, path: str
    ) -> tuple[Any, List[str]]:
        """
        Recursively sanitize a field value

        Args:
            key: Field name
            value: Field value
            job_id: Job ID for logging
            path: Full path to field (for nested objects)

        Returns:
            Tuple of (sanitized_value, warnings)
        """
        warnings = []

        # Handle None
        if value is None:
            return None, warnings

        # Handle strings
        if isinstance(value, str):
            return self._sanitize_string(key, value, job_id, path)

        # Handle lists
        if isinstance(value, list):
            sanitized_list = []
            for i, item in enumerate(value):
                sanitized_item, item_warnings = self._sanitize_field(
                    key, item, job_id, f"{path}[{i}]"
                )
                sanitized_list.append(sanitized_item)
                warnings.extend(item_warnings)
            return sanitized_list, warnings

        # Handle dictionaries (nested objects)
        if isinstance(value, dict):
            sanitized_dict = {}
            for nested_key, nested_value in value.items():
                sanitized_nested, nested_warnings = self._sanitize_field(
                    nested_key, nested_value, job_id, f"{path}.{nested_key}"
                )
                sanitized_dict[nested_key] = sanitized_nested
                warnings.extend(nested_warnings)
            return sanitized_dict, warnings

        # Handle primitives (int, float, bool)
        return value, warnings

    def _sanitize_string(
        self, key: str, value: str, job_id: str, path: str
    ) -> tuple[str, List[str]]:
        """
        Sanitize a string value with multiple security checks

        Args:
            key: Field name
            value: String value
            job_id: Job ID for logging
            path: Full path to field

        Returns:
            Tuple of (sanitized_value, warnings)
        """
        warnings = []
        original_value = value

        # Check 1: Length limit (prevent DoS)
        if len(value) > self.max_string_length:
            value = value[: self.max_string_length]
            warnings.append(
                f"{path}: String truncated from {len(original_value)} to {self.max_string_length} chars"
            )

        # Check 2: SQL injection patterns
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                warnings.append(
                    f"{path}: SQL injection pattern detected: {pattern} - STRIPPED"
                )
                value = re.sub(pattern, "[REMOVED]", value, flags=re.IGNORECASE)

        # Check 3: Command injection patterns
        for pattern in self.command_injection_patterns:
            if re.search(pattern, value):
                warnings.append(
                    f"{path}: Command injection pattern detected - STRIPPED"
                )
                value = re.sub(pattern, "", value)

        # Check 4: XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                warnings.append(f"{path}: XSS pattern detected - ESCAPED")
                value = html.escape(value)
                break  # Only escape once

        # Check 5: Path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, value):
                warnings.append(f"{path}: Path traversal pattern detected - STRIPPED")
                value = re.sub(pattern, "", value)

        # Check 6: URL validation
        if key in self.url_prohibited_fields:
            # These fields should NEVER contain URLs
            if re.search(r"https?://", value, re.IGNORECASE):
                warnings.append(
                    f"{path}: Unauthorized URL detected in prohibited field - STRIPPED"
                )
                value = re.sub(r"https?://[^\s]+", "[URL_REMOVED]", value)

        elif key in self.url_allowed_fields:
            # These fields can have URLs but validate them
            urls = re.findall(r"https?://[^\s]+", value)
            for url in urls:
                if self._is_suspicious_url(url):
                    warnings.append(
                        f"{path}: Suspicious URL detected: {url[:50]}... - STRIPPED"
                    )
                    value = value.replace(url, "[SUSPICIOUS_URL_REMOVED]")

        # Check 7: Null byte injection
        if "\x00" in value:
            warnings.append(f"{path}: Null byte detected - STRIPPED")
            value = value.replace("\x00", "")

        # Check 8: Unicode control characters (potential for bypassing filters)
        control_chars = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
        if control_chars.search(value):
            warnings.append(f"{path}: Control characters detected - STRIPPED")
            value = control_chars.sub("", value)

        return value, warnings

    def _is_suspicious_url(self, url: str) -> bool:
        """
        Check if URL is suspicious (potential data exfiltration)

        Args:
            url: URL to check

        Returns:
            True if URL is suspicious
        """
        try:
            # Check against suspicious patterns
            for pattern in self.suspicious_url_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return True

            # Parse URL and check domain
            parsed = urlparse(url)

            # Block localhost/internal IPs
            if parsed.hostname in ["localhost", "127.0.0.1", "0.0.0.0"]:
                return True

            # Block private IP ranges
            if parsed.hostname:
                if parsed.hostname.startswith(
                    ("10.", "172.16.", "192.168.")
                ):  # Private IPs
                    return True

            return False

        except Exception:
            # If URL parsing fails, consider it suspicious
            return True

    def get_sanitization_report(self, warnings: List[str]) -> Dict:
        """
        Generate sanitization report for security monitoring

        Args:
            warnings: List of warnings from sanitization

        Returns:
            Report dictionary
        """
        return {
            "total_warnings": len(warnings),
            "sql_injection_attempts": sum(
                1 for w in warnings if "SQL injection" in w
            ),
            "command_injection_attempts": sum(
                1 for w in warnings if "Command injection" in w
            ),
            "xss_attempts": sum(1 for w in warnings if "XSS" in w),
            "path_traversal_attempts": sum(
                1 for w in warnings if "Path traversal" in w
            ),
            "suspicious_urls": sum(1 for w in warnings if "Suspicious URL" in w),
            "unauthorized_urls": sum(1 for w in warnings if "Unauthorized URL" in w),
            "warnings": warnings[:10],  # First 10 warnings
        }


# Singleton instance
_sanitizer = None


def get_sanitizer() -> ResponseSanitizer:
    """Get singleton sanitizer instance"""
    global _sanitizer
    if _sanitizer is None:
        _sanitizer = ResponseSanitizer()
    return _sanitizer


def sanitize_response(result: Dict, job_id: str) -> tuple[Dict, List[str]]:
    """
    Convenience function to sanitize response

    Args:
        result: Raw analysis result
        job_id: Job ID

    Returns:
        Tuple of (sanitized_result, warnings)
    """
    sanitizer = get_sanitizer()
    return sanitizer.sanitize_analysis_result(result, job_id)
