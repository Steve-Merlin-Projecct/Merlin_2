#!/usr/bin/env python3
"""
Test the enhanced Gmail robustness features
Demonstrates comprehensive error handling, validation, and retry mechanisms
"""

import os
import sys
import tempfile
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager
from modules.email_integration.gmail_enhancements import (
    get_enhanced_gmail_sender,
    EmailValidator,
    AttachmentValidator,
    GmailConnectionHealthChecker,
    RetryManager,
    EnhancedGmailErrorHandler
)

def test_enhanced_gmail_robustness():
    """Test all enhanced Gmail robustness features"""
    print("🛡️ Testing Enhanced Gmail Robustness Features")
    print("=" * 60)
    
    # Get enhanced Gmail sender
    oauth_manager = get_gmail_oauth_manager()
    enhanced_sender = get_enhanced_gmail_sender(oauth_manager)
    
    test_results = []
    
    # Test 1: Email Validation
    print("\n📧 Testing Email Validation...")
    validator = EmailValidator()
    
    test_emails = [
        ("valid@example.com", True),
        ("invalid-email", False),
        ("", False),
        ("test@", False),
        ("test..test@example.com", False),
        ("test with spaces@example.com", False)
    ]
    
    validation_passed = 0
    for email, should_be_valid in test_emails:
        is_valid = validator.is_valid_email(email)
        if is_valid == should_be_valid:
            validation_passed += 1
            print(f"  ✅ {email}: {is_valid} (expected {should_be_valid})")
        else:
            print(f"  ❌ {email}: {is_valid} (expected {should_be_valid})")
    
    test_results.append(("Email Validation", validation_passed == len(test_emails)))
    
    # Test 2: Attachment Validation
    print("\n📎 Testing Attachment Validation...")
    attachment_validator = AttachmentValidator()
    
    # Create test files
    small_file = None
    large_file = None
    
    try:
        # Create small valid file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Small test file content")
            small_file = f.name
        
        # Test small file validation
        small_validation = attachment_validator.validate_attachment(small_file, "test.txt")
        small_file_valid = small_validation['valid']
        print(f"  ✅ Small file validation: {small_file_valid}")
        
        # Test non-existent file
        nonexistent_validation = attachment_validator.validate_attachment("/nonexistent/file.txt")
        nonexistent_invalid = not nonexistent_validation['valid']
        print(f"  ✅ Non-existent file rejection: {nonexistent_invalid}")
        
        attachment_tests_passed = small_file_valid and nonexistent_invalid
        test_results.append(("Attachment Validation", attachment_tests_passed))
        
    finally:
        # Clean up
        if small_file and os.path.exists(small_file):
            os.unlink(small_file)
        if large_file and os.path.exists(large_file):
            os.unlink(large_file)
    
    # Test 3: Connection Health Check
    print("\n🏥 Testing Connection Health Check...")
    health_checker = GmailConnectionHealthChecker(oauth_manager)
    health_result = health_checker.check_connection_health()
    
    print(f"  OAuth Valid: {'✅' if health_result['oauth_valid'] else '❌'}")
    print(f"  Service Accessible: {'✅' if health_result['service_accessible'] else '❌'}")
    print(f"  Internet Connected: {'✅' if health_result['internet_connected'] else '❌'}")
    print(f"  API Quota OK: {'✅' if health_result['api_quota_ok'] else '❌'}")
    print(f"  Overall Health: {'✅' if health_result['overall_healthy'] else '❌'}")
    
    test_results.append(("Connection Health Check", health_result['overall_healthy']))
    
    # Test 4: Enhanced Email Sending with Invalid Input
    print("\n🔧 Testing Enhanced Email Sending Error Handling...")
    
    # Test with invalid email
    invalid_result = enhanced_sender.send_job_application_email_enhanced(
        to_email="invalid-email",
        subject="Test",
        body="Test body",
        attachments=None
    )
    
    invalid_handled = invalid_result['status'] == 'error' and invalid_result['error_type'] == 'invalid_email'
    print(f"  ✅ Invalid email handled: {invalid_handled}")
    
    # Test with valid email (should work)
    valid_result = enhanced_sender.send_job_application_email_enhanced(
        to_email="1234.S.t.e.v.e.Glen@gmail.com",
        subject="Enhanced Gmail Test - Robustness Verification",
        body="This email tests the enhanced Gmail sender with comprehensive validation and error handling.",
        attachments=None
    )
    
    valid_success = valid_result['status'] == 'success'
    print(f"  ✅ Valid email sent: {valid_success}")
    if valid_success:
        print(f"    Message ID: {valid_result.get('gmail_message_id')}")
    
    enhanced_sending_passed = invalid_handled and valid_success
    test_results.append(("Enhanced Email Sending", enhanced_sending_passed))
    
    # Test 5: Error Handler
    print("\n❌ Testing Error Handler...")
    error_handler = EnhancedGmailErrorHandler()
    
    # Test different error types
    test_errors = [
        ("Quota exceeded", "quota_exceeded"),
        ("Invalid To header", "invalid_email"),
        ("Attachment too large", "attachment_too_large"),
        ("Network connection error", "network_error"),
        ("Unauthorized credentials", "auth_error")
    ]
    
    error_handling_passed = 0
    for error_msg, expected_type in test_errors:
        error_response = error_handler.handle_gmail_api_error(Exception(error_msg))
        if error_response['error_type'] == expected_type:
            error_handling_passed += 1
            print(f"  ✅ {error_msg} → {expected_type}")
        else:
            print(f"  ❌ {error_msg} → {error_response['error_type']} (expected {expected_type})")
    
    error_handler_success = error_handling_passed == len(test_errors)
    test_results.append(("Error Handler", error_handler_success))
    
    # Summary
    print(f"\n📊 Enhanced Gmail Robustness Test Summary")
    print("=" * 50)
    
    passed_tests = sum(1 for _, passed in test_results if passed)
    total_tests = len(test_results)
    
    print(f"Tests Run: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for test_name, passed in test_results:
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 All robustness tests passed! Gmail module is highly robust.")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed. Review and improve.")
        return False

if __name__ == "__main__":
    success = test_enhanced_gmail_robustness()
    exit(0 if success else 1)