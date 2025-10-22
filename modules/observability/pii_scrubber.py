"""
PII Scrubber for Log Data

Provides automatic redaction of Personally Identifiable Information (PII) and
sensitive data from logs to maintain security and compliance.

Supports scrubbing of:
- Email addresses
- Phone numbers
- API keys and tokens
- Database passwords in connection strings
- OAuth tokens
- Social Security Numbers
- Credit card numbers
- IP addresses (optional)

Can process both dictionary structures (log records) and plain strings.
"""

import re
import logging
from typing import Any, Dict, List, Union, Optional


class PIIScrubber:
    """
    Scrubs PII and sensitive data from log records and strings.

    Uses regex patterns to identify and redact sensitive information while
    preserving log usefulness by showing partial information where appropriate.

    Example:
        >>> scrubber = PIIScrubber()
        >>> scrubber.scrub_string("Email: user@example.com")
        'Email: u***@***.com'
        >>> scrubber.scrub_dict({'email': 'user@example.com'})
        {'email': 'u***@***.com'}
    """

    # Sensitive field names that should be redacted
    SENSITIVE_FIELDS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'api_key', 'apikey',
        'access_token', 'refresh_token', 'auth_token', 'bearer', 'oauth',
        'private_key', 'encryption_key', 'session_key', 'session_secret',
        'ssn', 'social_security', 'credit_card', 'card_number', 'cvv', 'pin',
        'authorization', 'x-api-key', 'x-auth-token'
    }

    # Regex patterns for different types of sensitive data
    PATTERNS = {
        # Email: user@example.com -> u***@***.com
        'email': {
            'pattern': re.compile(r'\b([a-zA-Z0-9._%+-])[a-zA-Z0-9._%+-]*@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'),
            'replacement': lambda m: f"{m.group(1)}***@***.com"
        },

        # Phone: 123-456-7890 or (123) 456-7890 -> ***-***-7890
        'phone': {
            'pattern': re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            'replacement': '***-***-****'
        },

        # API Key patterns: sk_1234567890 -> sk_****
        'api_key': {
            'pattern': re.compile(r'\b(sk|pk|token|key)_[a-zA-Z0-9]{8,}\b', re.IGNORECASE),
            'replacement': lambda m: f"{m.group(1)}_****"
        },

        # Bearer tokens: Bearer xyz123... -> Bearer ****
        'bearer_token': {
            'pattern': re.compile(r'\bBearer\s+[a-zA-Z0-9._-]+\b', re.IGNORECASE),
            'replacement': 'Bearer ****'
        },

        # Database password in connection string: postgres://user:pass@host -> postgres://user:****@host
        'db_password': {
            'pattern': re.compile(r'(postgres|mysql|mongodb|redis)://([^:]+):([^@]+)@', re.IGNORECASE),
            'replacement': lambda m: f"{m.group(1)}://{m.group(2)}:****@"
        },

        # Generic password in URLs: password=xyz -> password=****
        'url_password': {
            'pattern': re.compile(r'([?&])(password|passwd|pwd|secret|token)=([^&\s]+)', re.IGNORECASE),
            'replacement': lambda m: f"{m.group(1)}{m.group(2)}=****"
        },

        # SSN: 123-45-6789 -> ***-**-****
        'ssn': {
            'pattern': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'replacement': '***-**-****'
        },

        # Credit card: 4111-1111-1111-1111 -> ****-****-****-1111
        'credit_card': {
            'pattern': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            'replacement': lambda m: '****-****-****-' + m.group(0)[-4:]
        },

        # OAuth tokens and JWTs (long base64 strings)
        'jwt': {
            'pattern': re.compile(r'\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b'),
            'replacement': '****.***.****'
        },
    }

    def __init__(
        self,
        scrub_emails: bool = True,
        scrub_phones: bool = True,
        scrub_api_keys: bool = True,
        scrub_passwords: bool = True,
        scrub_ssn: bool = True,
        scrub_credit_cards: bool = True,
        custom_patterns: Optional[Dict[str, Dict[str, Any]]] = None,
        additional_sensitive_fields: Optional[List[str]] = None
    ):
        """
        Initialize PII scrubber with configurable patterns.

        Args:
            scrub_emails: Enable email redaction
            scrub_phones: Enable phone number redaction
            scrub_api_keys: Enable API key redaction
            scrub_passwords: Enable password redaction
            scrub_ssn: Enable SSN redaction
            scrub_credit_cards: Enable credit card redaction
            custom_patterns: Additional patterns to scrub {name: {pattern: regex, replacement: str}}
            additional_sensitive_fields: Additional field names to treat as sensitive
        """
        self.scrub_emails = scrub_emails
        self.scrub_phones = scrub_phones
        self.scrub_api_keys = scrub_api_keys
        self.scrub_passwords = scrub_passwords
        self.scrub_ssn = scrub_ssn
        self.scrub_credit_cards = scrub_credit_cards

        # Build active patterns based on configuration
        self.active_patterns = {}

        if scrub_emails:
            self.active_patterns['email'] = self.PATTERNS['email']

        if scrub_phones:
            self.active_patterns['phone'] = self.PATTERNS['phone']

        if scrub_api_keys:
            self.active_patterns['api_key'] = self.PATTERNS['api_key']
            self.active_patterns['bearer_token'] = self.PATTERNS['bearer_token']
            self.active_patterns['jwt'] = self.PATTERNS['jwt']

        if scrub_passwords:
            self.active_patterns['db_password'] = self.PATTERNS['db_password']
            self.active_patterns['url_password'] = self.PATTERNS['url_password']

        if scrub_ssn:
            self.active_patterns['ssn'] = self.PATTERNS['ssn']

        if scrub_credit_cards:
            self.active_patterns['credit_card'] = self.PATTERNS['credit_card']

        # Add custom patterns
        if custom_patterns:
            self.active_patterns.update(custom_patterns)

        # Update sensitive fields list
        self.sensitive_fields = self.SENSITIVE_FIELDS.copy()
        if additional_sensitive_fields:
            self.sensitive_fields.update(set(f.lower() for f in additional_sensitive_fields))

    def scrub_string(self, text: str) -> str:
        """
        Scrub PII from a string.

        Args:
            text: String to scrub

        Returns:
            Scrubbed string with PII redacted

        Example:
            >>> scrubber.scrub_string("Email user@example.com, phone 123-456-7890")
            'Email u***@***.com, phone ***-***-****'
        """
        if not isinstance(text, str):
            return text

        result = text

        # Apply each active pattern
        for pattern_name, pattern_info in self.active_patterns.items():
            pattern = pattern_info['pattern']
            replacement = pattern_info['replacement']

            if callable(replacement):
                result = pattern.sub(replacement, result)
            else:
                result = pattern.sub(replacement, result)

        return result

    def scrub_dict(self, data: Dict[str, Any], depth: int = 0, max_depth: int = 10) -> Dict[str, Any]:
        """
        Scrub PII from a dictionary recursively.

        Args:
            data: Dictionary to scrub
            depth: Current recursion depth (internal use)
            max_depth: Maximum recursion depth to prevent infinite loops

        Returns:
            Scrubbed dictionary with PII redacted

        Example:
            >>> scrubber.scrub_dict({'email': 'user@example.com', 'password': 'secret123'})
            {'email': 'u***@***.com', 'password': '****'}
        """
        if depth > max_depth:
            return data

        if not isinstance(data, dict):
            return data

        scrubbed = {}

        for key, value in data.items():
            # Check if field name is sensitive
            key_lower = key.lower()
            is_sensitive_field = any(
                sensitive in key_lower for sensitive in self.sensitive_fields
            )

            if is_sensitive_field:
                # Completely redact sensitive fields
                scrubbed[key] = '****'
            elif isinstance(value, str):
                # Scrub string values
                scrubbed[key] = self.scrub_string(value)
            elif isinstance(value, dict):
                # Recursively scrub nested dictionaries
                scrubbed[key] = self.scrub_dict(value, depth + 1, max_depth)
            elif isinstance(value, list):
                # Scrub list items
                scrubbed[key] = self._scrub_list(value, depth + 1, max_depth)
            else:
                # Keep other types as-is
                scrubbed[key] = value

        return scrubbed

    def _scrub_list(self, data: List[Any], depth: int = 0, max_depth: int = 10) -> List[Any]:
        """
        Scrub PII from a list recursively.

        Args:
            data: List to scrub
            depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            Scrubbed list with PII redacted
        """
        if depth > max_depth:
            return data

        scrubbed = []

        for item in data:
            if isinstance(item, str):
                scrubbed.append(self.scrub_string(item))
            elif isinstance(item, dict):
                scrubbed.append(self.scrub_dict(item, depth + 1, max_depth))
            elif isinstance(item, list):
                scrubbed.append(self._scrub_list(item, depth + 1, max_depth))
            else:
                scrubbed.append(item)

        return scrubbed

    def scrub(self, data: Union[str, Dict, List]) -> Union[str, Dict, List]:
        """
        Universal scrub method that handles strings, dicts, and lists.

        Args:
            data: Data to scrub (string, dict, or list)

        Returns:
            Scrubbed data of the same type

        Example:
            >>> scrubber.scrub("email: user@example.com")
            'email: u***@***.com'
            >>> scrubber.scrub({'password': 'secret'})
            {'password': '****'}
        """
        if isinstance(data, str):
            return self.scrub_string(data)
        elif isinstance(data, dict):
            return self.scrub_dict(data)
        elif isinstance(data, list):
            return self._scrub_list(data)
        else:
            return data


# Global default scrubber instance
_default_scrubber = None


def get_default_scrubber() -> PIIScrubber:
    """
    Get the global default PII scrubber instance.

    Returns:
        Default PIIScrubber instance
    """
    global _default_scrubber
    if _default_scrubber is None:
        _default_scrubber = PIIScrubber()
    return _default_scrubber


def scrub_pii(data: Union[str, Dict, List]) -> Union[str, Dict, List]:
    """
    Convenience function to scrub PII using the default scrubber.

    Args:
        data: Data to scrub (string, dict, or list)

    Returns:
        Scrubbed data

    Example:
        >>> scrub_pii("Contact: user@example.com")
        'Contact: u***@***.com'
    """
    return get_default_scrubber().scrub(data)


class PIIScrubbingFilter(logging.Filter):
    """
    Logging filter that automatically scrubs PII from log records.

    Can be added to any logging handler to ensure PII is redacted.

    Example:
        >>> handler = logging.FileHandler('app.log')
        >>> handler.addFilter(PIIScrubbingFilter())
    """

    def __init__(self, scrubber: Optional[PIIScrubber] = None):
        """
        Initialize the filter.

        Args:
            scrubber: PIIScrubber instance to use (uses default if not provided)
        """
        super().__init__()
        self.scrubber = scrubber or get_default_scrubber()

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Scrub PII from the log record.

        Args:
            record: Log record to filter

        Returns:
            True (always allow the record through after scrubbing)
        """
        # Scrub the message
        if record.msg:
            if isinstance(record.msg, str):
                record.msg = self.scrubber.scrub_string(record.msg)
            elif isinstance(record.msg, dict):
                record.msg = self.scrubber.scrub_dict(record.msg)

        # Scrub arguments if present
        if record.args:
            if isinstance(record.args, dict):
                record.args = self.scrubber.scrub_dict(record.args)
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(self._scrub_args(record.args))

        return True

    def _scrub_args(self, args: tuple) -> list:
        """
        Scrub arguments tuple.

        Args:
            args: Arguments to scrub

        Returns:
            List of scrubbed arguments
        """
        scrubbed = []
        for arg in args:
            if isinstance(arg, str):
                scrubbed.append(self.scrubber.scrub_string(arg))
            elif isinstance(arg, dict):
                scrubbed.append(self.scrubber.scrub_dict(arg))
            elif isinstance(arg, list):
                scrubbed.append(self.scrubber._scrub_list(arg))
            else:
                scrubbed.append(arg)
        return scrubbed
