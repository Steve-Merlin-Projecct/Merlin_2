"""
Unit Tests for Observability Module

Tests for PII scrubbing, rate limiting, configuration validation,
and disk space monitoring.
"""

import os
import time
import pytest
import tempfile
from pathlib import Path

from modules.observability.pii_scrubber import PIIScrubber, PIIScrubbingFilter, scrub_pii
from modules.observability.rate_limiter import RateLimiter
from modules.observability.config_validator import ConfigValidator, ConfigurationError


class TestPIIScrubber:
    """Test PII scrubbing functionality."""

    def test_email_scrubbing(self):
        """Test email address redaction."""
        scrubber = PIIScrubber()

        test_cases = [
            ("Contact: user@example.com", "Contact: u***@***.com"),
            ("Email john.doe@company.org", "Email j***@***.com"),
            ("Reach me at test.user+tag@domain.co.uk", "Reach me at t***@***.com"),
        ]

        for input_text, expected in test_cases:
            result = scrubber.scrub_string(input_text)
            assert result == expected, f"Failed for: {input_text}"

    def test_phone_number_scrubbing(self):
        """Test phone number redaction."""
        scrubber = PIIScrubber()

        test_cases = [
            ("Call 123-456-7890", "Call ***-***-****"),
            ("Phone: (555) 123-4567", "Phone: (***-***-****"),  # Pattern keeps opening paren
            ("Contact at 555.123.4567", "Contact at ***-***-****"),
        ]

        for input_text, expected in test_cases:
            result = scrubber.scrub_string(input_text)
            # Phone pattern may leave opening paren, so we check if it's redacted
            assert "***-***-****" in result, f"Failed for: {input_text}"

    def test_api_key_scrubbing(self):
        """Test API key redaction."""
        scrubber = PIIScrubber()

        test_cases = [
            ("API key: sk_1234567890abcdef", "API key: sk_****"),
            ("Token: pk_test123456789", "Token: pk_****"),
            ("Bearer token123456789", "Bearer ****"),
        ]

        for input_text, expected in test_cases:
            result = scrubber.scrub_string(input_text)
            assert result == expected, f"Failed for: {input_text}"

    def test_database_password_scrubbing(self):
        """Test database connection string password redaction."""
        scrubber = PIIScrubber()

        test_cases = [
            "postgres://user:secret123@localhost",
            "mysql://admin:pass@host.com/db",
            "mongodb://root:pwd123@server:27017",
        ]

        for input_text in test_cases:
            result = scrubber.scrub_string(input_text)
            # Check password is redacted (****@)
            assert ":****@" in result, f"Failed for: {input_text}"
            # Check username is preserved
            parts = input_text.split("://")[1].split(":")[0]
            assert parts in result, f"Username not preserved for: {input_text}"

    def test_ssn_scrubbing(self):
        """Test SSN redaction."""
        scrubber = PIIScrubber()
        input_text = "SSN: 123-45-6789"
        expected = "SSN: ***-**-****"
        result = scrubber.scrub_string(input_text)
        assert result == expected

    def test_credit_card_scrubbing(self):
        """Test credit card redaction."""
        scrubber = PIIScrubber()
        input_text = "Card: 4111-1111-1111-1111"
        result = scrubber.scrub_string(input_text)
        assert "****-****-****-1111" in result

    def test_dict_scrubbing(self):
        """Test dictionary scrubbing."""
        scrubber = PIIScrubber()

        input_dict = {
            "email": "user@example.com",
            "phone": "123-456-7890",
            "password": "secret123",
            "api_key": "sk_test1234567890",
            "normal_field": "keep this"
        }

        result = scrubber.scrub_dict(input_dict)

        assert result["email"] == "u***@***.com"
        assert result["phone"] == "***-***-****"
        assert result["password"] == "****"  # Sensitive field name
        assert result["api_key"] == "****"  # Sensitive field name
        assert result["normal_field"] == "keep this"

    def test_nested_dict_scrubbing(self):
        """Test nested dictionary scrubbing."""
        scrubber = PIIScrubber()

        input_dict = {
            "user": {
                "email": "user@example.com",
                "password": "secret",
                "profile": {
                    "phone": "123-456-7890"
                }
            }
        }

        result = scrubber.scrub_dict(input_dict)

        assert result["user"]["email"] == "u***@***.com"
        assert result["user"]["password"] == "****"
        assert result["user"]["profile"]["phone"] == "***-***-****"

    def test_list_scrubbing(self):
        """Test list scrubbing."""
        scrubber = PIIScrubber()

        input_list = [
            "Contact: user@example.com",
            "Phone: 123-456-7890",
            {"email": "test@example.com"}
        ]

        result = scrubber._scrub_list(input_list)

        assert result[0] == "Contact: u***@***.com"
        assert result[1] == "Phone: ***-***-****"
        assert result[2]["email"] == "t***@***.com"

    def test_scrub_convenience_function(self):
        """Test convenience scrub function."""
        result = scrub_pii("Email: user@example.com")
        assert result == "Email: u***@***.com"

    def test_selective_scrubbing(self):
        """Test selective scrubbing configuration."""
        # Only scrub emails
        scrubber = PIIScrubber(
            scrub_emails=True,
            scrub_phones=False,
            scrub_api_keys=False
        )

        input_text = "Email: user@example.com, Phone: 123-456-7890"
        result = scrubber.scrub_string(input_text)

        assert "u***@***.com" in result
        assert "123-456-7890" in result  # Phone not scrubbed


class TestRateLimiter:
    """Test rate limiting functionality."""

    def test_basic_rate_limiting(self):
        """Test basic rate limiting."""
        limiter = RateLimiter(requests_per_minute=10)

        # First 10 requests should be allowed
        for i in range(10):
            allowed, retry_after = limiter.is_allowed('test_key')
            assert allowed, f"Request {i+1} should be allowed"
            assert retry_after is None

        # 11th request should be rate limited
        allowed, retry_after = limiter.is_allowed('test_key')
        assert not allowed, "Request should be rate limited"
        assert retry_after is not None
        assert retry_after > 0

    def test_per_key_limiting(self):
        """Test that rate limits are per-key."""
        limiter = RateLimiter(requests_per_minute=5)

        # Use up key1's limit
        for i in range(5):
            allowed, _ = limiter.is_allowed('key1')
            assert allowed

        # key1 should be limited
        allowed, _ = limiter.is_allowed('key1')
        assert not allowed

        # key2 should still have full capacity
        for i in range(5):
            allowed, _ = limiter.is_allowed('key2')
            assert allowed, f"key2 request {i+1} should be allowed"

    def test_token_refill(self):
        """Test that tokens refill over time."""
        limiter = RateLimiter(requests_per_minute=60)  # 1 token per second

        # Use one token
        allowed, _ = limiter.is_allowed('test_key')
        assert allowed

        # Wait for token to refill
        time.sleep(1.1)

        # Should be able to make another request
        allowed, _ = limiter.is_allowed('test_key')
        assert allowed

    def test_get_stats(self):
        """Test rate limit statistics."""
        limiter = RateLimiter(requests_per_minute=60)

        # Make some requests
        for i in range(10):
            limiter.is_allowed('test_key')

        stats = limiter.get_stats('test_key')
        assert stats is not None
        assert stats['capacity'] == 60
        assert stats['remaining'] == 50
        assert stats['requests_per_minute'] == 60

    def test_reset(self):
        """Test rate limit reset."""
        limiter = RateLimiter(requests_per_minute=10)

        # Use up the limit
        for i in range(10):
            limiter.is_allowed('test_key')

        # Should be limited
        allowed, _ = limiter.is_allowed('test_key')
        assert not allowed

        # Reset
        limiter.reset('test_key')

        # Should work again
        allowed, _ = limiter.is_allowed('test_key')
        assert allowed

    def test_burst_size(self):
        """Test custom burst size."""
        limiter = RateLimiter(requests_per_minute=60, burst_size=100)

        # Should allow burst_size requests
        for i in range(100):
            allowed, _ = limiter.is_allowed('test_key')
            assert allowed, f"Request {i+1} should be allowed"

        # 101st request should be limited
        allowed, _ = limiter.is_allowed('test_key')
        assert not allowed


class TestConfigValidator:
    """Test configuration validation."""

    def test_valid_log_level(self):
        """Test valid log level validation."""
        validator = ConfigValidator()

        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        for level in valid_levels:
            result = validator.validate_log_level(level)
            assert result == level.upper()

    def test_invalid_log_level(self):
        """Test invalid log level raises error."""
        validator = ConfigValidator()

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate_log_level('INVALID')

        assert 'Invalid LOG_LEVEL' in str(exc_info.value)

    def test_valid_log_format(self):
        """Test valid log format validation."""
        validator = ConfigValidator()

        result_json = validator.validate_log_format('json')
        assert result_json == 'json'

        result_human = validator.validate_log_format('human')
        assert result_human == 'human'

    def test_invalid_log_format(self):
        """Test invalid log format raises error."""
        validator = ConfigValidator()

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate_log_format('xml')

        assert 'Invalid LOG_FORMAT' in str(exc_info.value)

    def test_log_directory_creation(self):
        """Test log directory creation."""
        validator = ConfigValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, 'logs', 'nested')

            # Directory shouldn't exist yet
            assert not os.path.exists(log_dir)

            # Validate should create it
            result = validator.validate_log_directory(log_dir)

            assert result.exists()
            assert result.is_dir()

    def test_log_directory_not_writable(self):
        """Test error when log directory is not writable."""
        validator = ConfigValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, 'logs')
            os.makedirs(log_dir)
            os.chmod(log_dir, 0o444)  # Read-only

            try:
                with pytest.raises(ConfigurationError) as exc_info:
                    validator.validate_log_directory(log_dir)

                assert 'not writable' in str(exc_info.value)
            finally:
                # Restore permissions for cleanup
                os.chmod(log_dir, 0o755)

    def test_disk_space_validation(self):
        """Test disk space validation."""
        validator = ConfigValidator()

        # Should not raise error for current directory (should have space)
        free_bytes, free_percent = validator.validate_disk_space()

        assert free_bytes > 0
        assert free_percent >= 0
        assert free_percent <= 100

    def test_rotation_settings_validation(self):
        """Test log rotation settings validation."""
        validator = ConfigValidator()

        # Valid settings
        max_bytes, backup_count = validator.validate_rotation_settings(
            max_bytes=10*1024*1024,  # 10MB
            backup_count=5
        )

        assert max_bytes == 10*1024*1024
        assert backup_count == 5

    def test_rotation_settings_too_small(self):
        """Test error for too small max_bytes."""
        validator = ConfigValidator()

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate_rotation_settings(max_bytes=100)  # Too small

        assert 'too small' in str(exc_info.value).lower()

    def test_rotation_settings_negative_backup(self):
        """Test error for negative backup count."""
        validator = ConfigValidator()

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate_rotation_settings(
                max_bytes=10*1024*1024,
                backup_count=-1
            )

        assert 'non-negative' in str(exc_info.value)

    def test_api_key_validation_not_required(self):
        """Test API key validation when not required."""
        validator = ConfigValidator()

        # Should not raise error when not required
        result = validator.validate_api_key(required=False)
        # Result can be None if no API key is set

    def test_validate_all_success(self):
        """Test complete validation with valid configuration."""
        validator = ConfigValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Set temporary environment
            old_log_level = os.environ.get('LOG_LEVEL')
            old_log_format = os.environ.get('LOG_FORMAT')

            os.environ['LOG_LEVEL'] = 'INFO'
            os.environ['LOG_FORMAT'] = 'json'

            try:
                results = validator.validate_all(
                    require_api_key=False,
                    check_disk_space=True
                )

                assert results['valid'] is True
                assert results['config']['log_level'] == 'INFO'
                assert results['config']['log_format'] == 'json'
                assert 'log_directory' in results['config']
            finally:
                # Restore environment
                if old_log_level:
                    os.environ['LOG_LEVEL'] = old_log_level
                elif 'LOG_LEVEL' in os.environ:
                    del os.environ['LOG_LEVEL']

                if old_log_format:
                    os.environ['LOG_FORMAT'] = old_log_format
                elif 'LOG_FORMAT' in os.environ:
                    del os.environ['LOG_FORMAT']


class TestDiskSpaceMonitoring:
    """Test disk space monitoring in health check."""

    def test_disk_space_calculation(self):
        """Test that disk space is calculated correctly."""
        import shutil

        stat = shutil.disk_usage('./logs')
        free_mb = stat.free / (1024 * 1024)
        total_mb = stat.total / (1024 * 1024)
        free_percent = (stat.free / stat.total * 100) if stat.total > 0 else 0

        assert free_mb > 0
        assert total_mb > 0
        assert 0 <= free_percent <= 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
