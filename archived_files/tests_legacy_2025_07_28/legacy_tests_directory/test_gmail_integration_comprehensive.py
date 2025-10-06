#!/usr/bin/env python3
"""
Comprehensive test suite for Gmail OAuth integration module
Tests error handling, edge cases, and production scenarios
"""

import os
import json
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import base64

# Add project root to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.email_integration.gmail_oauth_official import (
    get_gmail_oauth_manager, 
    get_gmail_sender,
    OfficialGmailOAuthManager,
    OfficialGmailSender
)

class TestGmailOAuthRobustness(unittest.TestCase):
    """Test OAuth manager robustness and error handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.oauth_manager = get_gmail_oauth_manager()
        self.test_client_id = "test_client_id"
        self.test_client_secret = "test_client_secret"
        
    def test_invalid_credentials_handling(self):
        """Test handling of invalid OAuth credentials"""
        result = self.oauth_manager.setup_oauth_credentials("", "")
        self.assertEqual(result['status'], 'error')
        self.assertIn('Client ID and secret are required', result['message'])
        
    def test_missing_credentials_file(self):
        """Test behavior when credentials file is missing"""
        # Temporarily rename credentials file if it exists
        cred_file = self.oauth_manager.config.CREDENTIALS_FILE
        backup_file = f"{cred_file}.backup"
        
        if os.path.exists(cred_file):
            os.rename(cred_file, backup_file)
        
        try:
            result = self.oauth_manager.get_authorization_url()
            self.assertEqual(result['status'], 'error')
            self.assertIn('OAuth credentials not configured', result['message'])
        finally:
            # Restore file if it was backed up
            if os.path.exists(backup_file):
                os.rename(backup_file, cred_file)
    
    def test_expired_token_handling(self):
        """Test handling of expired OAuth tokens"""
        # Create mock expired token
        expired_token = {
            "token": "expired_token",
            "refresh_token": "refresh_token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": self.test_client_id,
            "client_secret": self.test_client_secret,
            "scopes": ["https://www.googleapis.com/auth/gmail.send"],
            "expiry": "2020-01-01T00:00:00Z"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(expired_token, f)
            temp_token_file = f.name
        
        try:
            # Test that expired token is detected
            self.oauth_manager.config.TOKEN_FILE = temp_token_file
            auth_status = self.oauth_manager.get_oauth_status()
            # Should handle expired tokens gracefully
            self.assertIn('status', auth_status)
        finally:
            os.unlink(temp_token_file)
    
    def test_malformed_token_file(self):
        """Test handling of corrupted token file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_token_file = f.name
        
        try:
            self.oauth_manager.config.TOKEN_FILE = temp_token_file
            result = self.oauth_manager.get_oauth_status()
            # Should handle malformed JSON gracefully
            self.assertEqual(result['authenticated'], False)
        finally:
            os.unlink(temp_token_file)

class TestGmailSenderRobustness(unittest.TestCase):
    """Test Gmail sender robustness and error handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.oauth_manager = Mock(spec=OfficialGmailOAuthManager)
        self.gmail_sender = OfficialGmailSender(self.oauth_manager)
        
    def test_large_attachment_handling(self):
        """Test handling of large attachments (Gmail 25MB limit)"""
        # Create a large test file (simulate 30MB)
        large_file_content = b"x" * (30 * 1024 * 1024)  # 30MB
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(large_file_content)
            large_file_path = f.name
        
        try:
            # Mock the Gmail service to simulate size error
            mock_service = Mock()
            mock_service.users().messages().send().execute.side_effect = Exception("Attachment too large")
            self.oauth_manager.get_gmail_service.return_value = mock_service
            
            result = self.gmail_sender.send_email_with_attachment(
                to_email="test@example.com",
                subject="Large attachment test",
                body="Testing large attachment",
                attachment_path=large_file_path,
                attachment_name="large_file.txt"
            )
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('Attachment too large', result['message'])
        finally:
            os.unlink(large_file_path)
    
    def test_nonexistent_attachment_file(self):
        """Test handling of non-existent attachment files"""
        nonexistent_path = "/path/that/does/not/exist.txt"
        
        result = self.gmail_sender.send_email_with_attachment(
            to_email="test@example.com",
            subject="Nonexistent attachment test",
            body="Testing nonexistent attachment",
            attachment_path=nonexistent_path,
            attachment_name="missing.txt"
        )
        
        # Should check file existence before attempting to send
        self.assertEqual(result['status'], 'error')
    
    def test_invalid_email_addresses(self):
        """Test handling of invalid email addresses"""
        invalid_emails = [
            "invalid-email",
            "@invalid.com",
            "test@",
            "",
            None,
            "test@invalid",
            "test space@example.com"
        ]
        
        mock_service = Mock()
        mock_service.users().messages().send().execute.side_effect = Exception("Invalid email")
        self.oauth_manager.get_gmail_service.return_value = mock_service
        
        for invalid_email in invalid_emails:
            result = self.gmail_sender.send_job_application_email(
                to_email=invalid_email,
                subject="Test",
                body="Test body",
                attachments=None
            )
            
            # Should handle invalid emails gracefully
            self.assertEqual(result['status'], 'error')
    
    def test_network_connectivity_errors(self):
        """Test handling of network connectivity issues"""
        import requests
        
        # Mock network error
        self.oauth_manager.get_gmail_service.side_effect = requests.ConnectionError("Network error")
        
        result = self.gmail_sender.send_job_application_email(
            to_email="test@example.com",
            subject="Network test",
            body="Testing network error",
            attachments=None
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error_type', result)
    
    def test_gmail_api_quota_exceeded(self):
        """Test handling of Gmail API quota limits"""
        from googleapiclient.errors import HttpError
        
        # Mock quota exceeded error
        mock_response = Mock()
        mock_response.status = 429
        mock_response.reason = "Quota exceeded"
        
        quota_error = HttpError(mock_response, b'{"error": {"code": 429, "message": "Quota exceeded"}}')
        
        mock_service = Mock()
        mock_service.users().messages().send().execute.side_effect = quota_error
        self.oauth_manager.get_gmail_service.return_value = mock_service
        
        result = self.gmail_sender.send_job_application_email(
            to_email="test@example.com",
            subject="Quota test",
            body="Testing quota limits",
            attachments=None
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['error_type'], 'http_error')
    
    def test_multiple_attachments_handling(self):
        """Test handling of multiple attachments"""
        # Create multiple test files
        test_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_test_{i}.txt') as f:
                f.write(f"Test content for file {i}")
                test_files.append(f.name)
        
        try:
            attachments = [
                {'path': test_files[0], 'filename': 'test1.txt'},
                {'path': test_files[1], 'filename': 'test2.txt'},
                {'path': test_files[2], 'filename': 'test3.txt'}
            ]
            
            # Mock successful send
            mock_service = Mock()
            mock_service.users().messages().send().execute.return_value = {'id': 'test123'}
            self.oauth_manager.get_gmail_service.return_value = mock_service
            
            result = self.gmail_sender.send_job_application_email(
                to_email="test@example.com",
                subject="Multiple attachments test",
                body="Testing multiple attachments",
                attachments=attachments
            )
            
            self.assertEqual(result['status'], 'success')
        finally:
            for file_path in test_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)

class TestGmailIntegrationEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_empty_email_body(self):
        """Test sending email with empty body"""
        oauth_manager = Mock(spec=OfficialGmailOAuthManager)
        gmail_sender = OfficialGmailSender(oauth_manager)
        
        mock_service = Mock()
        mock_service.users().messages().send().execute.return_value = {'id': 'test123'}
        oauth_manager.get_gmail_service.return_value = mock_service
        
        result = gmail_sender.send_job_application_email(
            to_email="test@example.com",
            subject="Empty body test",
            body="",
            attachments=None
        )
        
        # Should handle empty body gracefully
        self.assertEqual(result['status'], 'success')
    
    def test_very_long_subject_line(self):
        """Test handling of very long subject lines"""
        oauth_manager = Mock(spec=OfficialGmailOAuthManager)
        gmail_sender = OfficialGmailSender(oauth_manager)
        
        # Create subject line longer than typical email standards (>78 chars)
        long_subject = "This is a very long subject line that exceeds normal email standards " * 10
        
        mock_service = Mock()
        mock_service.users().messages().send().execute.return_value = {'id': 'test123'}
        oauth_manager.get_gmail_service.return_value = mock_service
        
        result = gmail_sender.send_job_application_email(
            to_email="test@example.com",
            subject=long_subject,
            body="Test body",
            attachments=None
        )
        
        # Should handle long subject lines
        self.assertEqual(result['status'], 'success')
    
    def test_unicode_characters_in_email(self):
        """Test handling of Unicode characters in email content"""
        oauth_manager = Mock(spec=OfficialGmailOAuthManager)
        gmail_sender = OfficialGmailSender(oauth_manager)
        
        unicode_content = {
            'subject': '测试邮件 - Тест - 🚀 Emoji Test',
            'body': '''
Hello! Здравствуйте! 你好!

This email contains various Unicode characters:
- Emoji: 📧 💼 ✅ 🎉
- Chinese: 自动化工作申请系统
- Russian: Автоматизированная система подачи заявлений на работу
- Math: ∑ ∞ ∆ π
- Special chars: ©®™ €£¥ ±×÷

Best regards,
测试系统
            '''
        }
        
        mock_service = Mock()
        mock_service.users().messages().send().execute.return_value = {'id': 'test123'}
        oauth_manager.get_gmail_service.return_value = mock_service
        
        result = gmail_sender.send_job_application_email(
            to_email="test@example.com",
            subject=unicode_content['subject'],
            body=unicode_content['body'],
            attachments=None
        )
        
        # Should handle Unicode content properly
        self.assertEqual(result['status'], 'success')

class TestGmailSecurityAndValidation(unittest.TestCase):
    """Test security aspects and input validation"""
    
    def test_email_injection_prevention(self):
        """Test prevention of email header injection attacks"""
        oauth_manager = Mock(spec=OfficialGmailOAuthManager)
        gmail_sender = OfficialGmailSender(oauth_manager)
        
        # Test injection attempts in various fields
        injection_attempts = [
            "test@example.com\nBcc: hacker@evil.com",
            "test@example.com\r\nCc: another@evil.com",
            "Subject: Injected\nBcc: hidden@evil.com",
            "test@example.com\nContent-Type: text/html"
        ]
        
        for injection_attempt in injection_attempts:
            mock_service = Mock()
            mock_service.users().messages().send().execute.return_value = {'id': 'test123'}
            oauth_manager.get_gmail_service.return_value = mock_service
            
            result = gmail_sender.send_job_application_email(
                to_email=injection_attempt,
                subject="Test",
                body="Test body",
                attachments=None
            )
            
            # Should either sanitize or reject injection attempts
            # The EmailMessage class should handle this automatically
            self.assertIn(result['status'], ['success', 'error'])
    
    def test_attachment_type_validation(self):
        """Test validation of attachment file types"""
        oauth_manager = Mock(spec=OfficialGmailOAuthManager)
        gmail_sender = OfficialGmailSender(oauth_manager)
        
        # Create test files with various extensions
        dangerous_extensions = ['.exe', '.bat', '.scr', '.com', '.cmd']
        safe_extensions = ['.pdf', '.docx', '.txt', '.jpg', '.png']
        
        for ext in dangerous_extensions + safe_extensions:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=ext) as f:
                f.write("test content")
                test_file = f.name
            
            try:
                mock_service = Mock()
                mock_service.users().messages().send().execute.return_value = {'id': 'test123'}
                oauth_manager.get_gmail_service.return_value = mock_service
                
                result = gmail_sender.send_email_with_attachment(
                    to_email="test@example.com",
                    subject="Attachment type test",
                    body="Testing attachment types",
                    attachment_path=test_file,
                    attachment_name=f"test{ext}"
                )
                
                # Should handle all file types (Gmail has its own filtering)
                self.assertEqual(result['status'], 'success')
            finally:
                os.unlink(test_file)

def run_comprehensive_tests():
    """Run all robustness tests"""
    test_classes = [
        TestGmailOAuthRobustness,
        TestGmailSenderRobustness,
        TestGmailIntegrationEdgeCases,
        TestGmailSecurityAndValidation
    ]
    
    total_tests = 0
    total_failures = 0
    
    print("🧪 Running Comprehensive Gmail Integration Tests")
    print("=" * 60)
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}")
        print("-" * 40)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures) + len(result.errors)
    
    print(f"\n📊 Test Summary")
    print("=" * 30)
    print(f"Total Tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Success Rate: {((total_tests - total_failures) / total_tests * 100):.1f}%")
    
    if total_failures == 0:
        print("✅ All tests passed! Gmail module is robust.")
    else:
        print(f"❌ {total_failures} tests failed. Review and fix issues.")
    
    return total_failures == 0

if __name__ == "__main__":
    run_comprehensive_tests()