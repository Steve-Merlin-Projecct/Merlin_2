#!/usr/bin/env python3
"""
Comprehensive Security Testing for Link Tracking System

Tests all implemented security controls including authentication, rate limiting,
input validation, SQL injection prevention, and security event logging.

Version: 2.16.5
Date: July 28, 2025
"""

import unittest
import json
import time
import os
from unittest.mock import Mock, patch, MagicMock
import psycopg2
from modules.link_tracking.security_controls import SecurityControls, require_api_key, rate_limit
from modules.link_tracking.secure_link_tracker import SecureLinkTracker
from modules.link_tracking.link_tracking_api import SecureLinkTrackingAPI

class TestSecurityControls(unittest.TestCase):
    """Test security controls implementation."""
    
    def setUp(self):
        """Set up test environment."""
        self.security = SecurityControls()
    
    def test_tracking_id_validation(self):
        """Test tracking ID format validation."""
        # Valid tracking ID
        valid, error = self.security.validate_tracking_id("lt_1234567890abcdef")
        self.assertTrue(valid)
        self.assertEqual(error, "")
        
        # Invalid format
        valid, error = self.security.validate_tracking_id("invalid_id")
        self.assertFalse(valid)
        self.assertIn("Invalid tracking ID format", error)
        
        # Empty tracking ID
        valid, error = self.security.validate_tracking_id("")
        self.assertFalse(valid)
        self.assertIn("Tracking ID is required", error)
        
        # Too short
        valid, error = self.security.validate_tracking_id("lt_123")
        self.assertFalse(valid)
        self.assertIn("Invalid tracking ID format", error)
    
    def test_url_validation(self):
        """Test URL validation and security checks."""
        # Valid URLs
        valid, error = self.security.validate_url("https://linkedin.com/in/user")
        self.assertTrue(valid)
        
        # Invalid protocol
        valid, error = self.security.validate_url("javascript:alert('xss')")
        self.assertFalse(valid)
        self.assertIn("protocol", error)
        
        # No protocol
        valid, error = self.security.validate_url("linkedin.com/user")
        self.assertFalse(valid)
        self.assertIn("must include protocol", error)
        
        # IP address (should be blocked)
        valid, error = self.security.validate_url("http://192.168.1.1/malicious")
        self.assertFalse(valid)
        self.assertIn("Direct IP addresses not allowed", error)
    
    def test_input_sanitization(self):
        """Test input sanitization functionality."""
        # Dangerous characters removal
        dirty_input = "<script>alert('xss')</script>"
        clean = self.security.sanitize_input(dirty_input)
        self.assertNotIn("<", clean)
        self.assertNotIn(">", clean)
        
        # Length limiting
        long_input = "a" * 2000
        clean = self.security.sanitize_input(long_input, max_length=100)
        self.assertEqual(len(clean), 100)
        
        # Control character removal
        control_input = "test\x00\x01\x02"
        clean = self.security.sanitize_input(control_input)
        self.assertEqual(clean, "test")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        test_key = "test_ip_123"
        
        # Should allow requests within limit
        allowed, info = self.security.check_rate_limit(test_key, limit=5, window=60)
        self.assertTrue(allowed)
        self.assertEqual(info['remaining'], 4)
        
        # Fill up the limit
        for i in range(4):
            allowed, info = self.security.check_rate_limit(test_key, limit=5, window=60)
        
        # Should deny when limit exceeded
        allowed, info = self.security.check_rate_limit(test_key, limit=5, window=60)
        self.assertFalse(allowed)
        self.assertEqual(info['remaining'], 0)
    
    def test_secure_id_generation(self):
        """Test secure tracking ID generation."""
        # Generate multiple IDs
        ids = [self.security.generate_secure_tracking_id() for _ in range(100)]
        
        # All should be unique
        self.assertEqual(len(ids), len(set(ids)))
        
        # All should follow correct format
        for tracking_id in ids:
            self.assertTrue(tracking_id.startswith("lt_"))
            self.assertEqual(len(tracking_id), 19)  # lt_ + 16 hex chars
            
            # Validate format
            valid, error = self.security.validate_tracking_id(tracking_id)
            self.assertTrue(valid, f"Generated ID {tracking_id} failed validation: {error}")

class TestSecureLinkTracker(unittest.TestCase):
    """Test secure link tracker implementation."""
    
    def setUp(self):
        """Set up test environment."""
        self.tracker = SecureLinkTracker()
    
    @patch('modules.link_tracking.secure_link_tracker.psycopg2.connect')
    def test_create_tracked_link_sql_injection_prevention(self, mock_connect):
        """Test SQL injection prevention in link creation."""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        # Mock cursor response
        mock_cursor.fetchone.return_value = {
            'tracking_id': 'lt_1234567890abcdef',
            'redirect_url': 'https://test.com/track/lt_1234567890abcdef',
            'created_at': Mock()
        }
        
        # Attempt SQL injection in original_url
        malicious_url = "https://evil.com'; DROP TABLE link_tracking; --"
        
        try:
            result = self.tracker.create_tracked_link(
                original_url=malicious_url,
                link_function="LinkedIn",
                client_ip="192.168.1.1"
            )
            
            # Should fail validation before reaching database
            self.fail("Should have failed URL validation")
            
        except ValueError as e:
            # Should catch validation error
            self.assertIn("Invalid URL", str(e))
        
        # Verify cursor.execute was called with parameterized query
        if mock_cursor.execute.called:
            args, kwargs = mock_cursor.execute.call_args
            query = args[0]
            params = args[1]
            
            # Query should use %s placeholders
            self.assertIn("%s", query)
            # Parameters should be passed separately
            self.assertIsInstance(params, tuple)
    
    def test_input_validation_in_create_link(self):
        """Test comprehensive input validation."""
        # Invalid URL
        with self.assertRaises(ValueError):
            self.tracker.create_tracked_link(
                original_url="not_a_url",
                link_function="LinkedIn"
            )
        
        # Invalid link function
        with self.assertRaises(ValueError):
            self.tracker.create_tracked_link(
                original_url="https://linkedin.com",
                link_function="InvalidFunction"
            )
        
        # Invalid UUID format
        with self.assertRaises(ValueError):
            self.tracker.create_tracked_link(
                original_url="https://linkedin.com",
                link_function="LinkedIn", 
                job_id="invalid_uuid"
            )

class TestSecurityIntegration(unittest.TestCase):
    """Test security integration and API endpoints."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = SecureLinkTrackingAPI()
    
    @patch.dict(os.environ, {'LINK_TRACKING_API_KEY': 'test_api_key_12345'})
    def test_api_authentication(self):
        """Test API key authentication."""
        # Mock Flask request
        with patch('modules.link_tracking.security_controls.request') as mock_request:
            mock_request.headers.get.return_value = 'Bearer test_api_key_12345'
            
            # Should pass authentication
            @require_api_key
            def test_endpoint():
                return "success"
            
            result = test_endpoint()
            self.assertEqual(result, "success")
    
    def test_comprehensive_validation_flow(self):
        """Test complete validation flow."""
        test_data = {
            "original_url": "https://linkedin.com/in/testuser",
            "link_function": "LinkedIn",
            "link_type": "profile",
            "description": "Test link"
        }
        
        # Mock client IP
        client_ip = "192.168.1.100"
        
        # Should validate all fields successfully
        with patch.object(self.api.link_tracker, 'create_tracked_link') as mock_create:
            mock_create.return_value = {
                'tracking_id': 'lt_1234567890abcdef',
                'redirect_url': 'https://test.com/track/lt_1234567890abcdef',
                'link_function': 'LinkedIn',
                'created_at': '2025-07-28T00:00:00'
            }
            
            result, status_code = self.api.create_tracked_link(test_data, client_ip)
            
            self.assertEqual(status_code, 201)
            self.assertIn('tracking_id', result)
            
            # Verify security logging was called
            mock_create.assert_called_once_with(
                original_url=test_data['original_url'],
                link_function=test_data['link_function'],
                job_id=None,
                application_id=None,
                link_type=test_data['link_type'],
                description=test_data['description'],
                client_ip=client_ip
            )

class TestSecurityEventLogging(unittest.TestCase):
    """Test security event logging functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.security = SecurityControls()
    
    def test_security_event_logging(self):
        """Test security event logging."""
        with patch('modules.link_tracking.security_controls.logger') as mock_logger:
            # Log a security event
            self.security.log_security_event(
                'TEST_EVENT',
                {'test_field': 'test_value', 'ip': '192.168.1.1'},
                'WARNING'
            )
            
            # Verify logging was called
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            self.assertIn('TEST_EVENT', call_args)
            self.assertIn('test_value', call_args)
    
    def test_ip_blocking(self):
        """Test IP blocking functionality."""
        test_ip = "192.168.1.100"
        
        # IP should not be blocked initially
        self.assertFalse(self.security.is_blocked_ip(test_ip))
        
        # Block the IP
        self.security.block_ip(test_ip, "Test blocking")
        
        # IP should now be blocked
        self.assertTrue(self.security.is_blocked_ip(test_ip))

def run_security_tests():
    """Run comprehensive security test suite."""
    print("🔒 Running Link Tracking Security Tests...")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestSecurityControls,
        TestSecureLinkTracker, 
        TestSecurityIntegration,
        TestSecurityEventLogging
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        passed_tests += result.testsRun - len(result.failures) - len(result.errors)
        failed_tests += len(result.failures) + len(result.errors)
        
        if result.failures:
            print(f"❌ Failures in {test_class.__name__}:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print(f"🚨 Errors in {test_class.__name__}:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("🔒 SECURITY TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("✅ ALL SECURITY TESTS PASSED!")
        print("🛡️  Link tracking system security validated")
        return True
    else:
        print(f"❌ {failed_tests} SECURITY TESTS FAILED!")
        print("🚨 Security issues detected - review and fix before deployment")
        return False

if __name__ == "__main__":
    success = run_security_tests()
    exit(0 if success else 1)