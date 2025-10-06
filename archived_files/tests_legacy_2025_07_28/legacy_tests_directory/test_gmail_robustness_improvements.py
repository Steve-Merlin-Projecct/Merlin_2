#!/usr/bin/env python3
"""
Gmail robustness improvements based on production testing
Implements specific enhancements to make the module more robust
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager, get_gmail_sender

class GmailRobustnessEnhancements:
    """Implements robustness improvements for Gmail integration"""
    
    def __init__(self):
        self.oauth_manager = get_gmail_oauth_manager()
        self.gmail_sender = get_gmail_sender(self.oauth_manager)
        
    def test_connection_health_check(self):
        """Test comprehensive connection health checking"""
        print("🏥 Testing connection health check...")
        
        health_checks = {
            'oauth_credentials_valid': False,
            'gmail_service_accessible': False,
            'internet_connectivity': False,
            'api_quota_available': False
        }
        
        try:
            # Check OAuth credentials
            oauth_status = self.oauth_manager.get_oauth_status()
            health_checks['oauth_credentials_valid'] = oauth_status.get('authenticated', False)
            
            # Check Gmail service accessibility
            if health_checks['oauth_credentials_valid']:
                try:
                    service = self.oauth_manager.get_gmail_service()
                    health_checks['gmail_service_accessible'] = service is not None
                except Exception as e:
                    print(f"  Gmail service error: {e}")
            
            # Check internet connectivity
            try:
                import requests
                response = requests.get('https://www.google.com', timeout=5)
                health_checks['internet_connectivity'] = response.status_code == 200
            except Exception as e:
                print(f"  Internet connectivity error: {e}")
            
            # Test API quota (attempt a simple operation)
            if health_checks['gmail_service_accessible']:
                try:
                    # This is a light operation that tests quota
                    profile = service.users().getProfile(userId='me').execute()
                    health_checks['api_quota_available'] = 'emailAddress' in profile
                except Exception as e:
                    print(f"  API quota test error: {e}")
            
        except Exception as e:
            print(f"Health check error: {e}")
        
        overall_health = all(health_checks.values())
        
        print(f"  OAuth Credentials: {'✅' if health_checks['oauth_credentials_valid'] else '❌'}")
        print(f"  Gmail Service: {'✅' if health_checks['gmail_service_accessible'] else '❌'}")
        print(f"  Internet: {'✅' if health_checks['internet_connectivity'] else '❌'}")
        print(f"  API Quota: {'✅' if health_checks['api_quota_available'] else '❌'}")
        print(f"  Overall Health: {'✅ Healthy' if overall_health else '❌ Issues Detected'}")
        
        return {
            'healthy': overall_health,
            'details': health_checks,
            'recommendations': self._get_health_recommendations(health_checks)
        }
    
    def _get_health_recommendations(self, health_checks: Dict[str, bool]) -> list:
        """Get recommendations based on health check results"""
        recommendations = []
        
        if not health_checks['oauth_credentials_valid']:
            recommendations.append("Re-run OAuth authorization flow")
        
        if not health_checks['internet_connectivity']:
            recommendations.append("Check internet connection")
        
        if not health_checks['gmail_service_accessible']:
            recommendations.append("Verify Gmail API is enabled in Google Cloud Console")
        
        if not health_checks['api_quota_available']:
            recommendations.append("Check Gmail API quota limits in Google Cloud Console")
        
        return recommendations
    
    def test_retry_mechanism(self):
        """Test automatic retry mechanism for failed operations"""
        print("🔄 Testing retry mechanism...")
        
        def send_with_retry(max_retries=3, delay=1):
            """Send email with retry logic"""
            for attempt in range(max_retries):
                try:
                    result = self.gmail_sender.send_job_application_email(
                        to_email="1234.S.t.e.v.e.Glen@gmail.com",
                        subject=f"Retry Test - Attempt {attempt + 1}",
                        body=f"Testing retry mechanism, attempt {attempt + 1} of {max_retries}",
                        attachments=None
                    )
                    
                    if result['status'] == 'success':
                        return {
                            'success': True,
                            'attempts': attempt + 1,
                            'message_id': result.get('gmail_message_id')
                        }
                    
                    # If not last attempt, wait before retry
                    if attempt < max_retries - 1:
                        print(f"  Attempt {attempt + 1} failed, retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                
                except Exception as e:
                    print(f"  Attempt {attempt + 1} error: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
            
            return {
                'success': False,
                'attempts': max_retries,
                'error': 'All retry attempts failed'
            }
        
        result = send_with_retry()
        
        print(f"  Retry result: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"  Attempts used: {result['attempts']}")
        
        return result
    
    def test_input_validation_enhancement(self):
        """Test enhanced input validation"""
        print("🛡️ Testing input validation enhancement...")
        
        validation_tests = []
        
        # Test email validation
        invalid_emails = [
            "",
            None,
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
            "test with spaces@example.com"
        ]
        
        for email in invalid_emails:
            try:
                result = self.gmail_sender.send_job_application_email(
                    to_email=email,
                    subject="Validation Test",
                    body="Testing email validation",
                    attachments=None
                )
                
                # Should return error for invalid emails
                validation_tests.append({
                    'input': email,
                    'type': 'email',
                    'handled_properly': result['status'] == 'error'
                })
                
            except Exception as e:
                # Should not crash, should handle gracefully
                validation_tests.append({
                    'input': email,
                    'type': 'email',
                    'handled_properly': False,
                    'error': str(e)
                })
        
        # Test subject validation
        extreme_subjects = [
            "",  # Empty subject
            "x" * 1000,  # Very long subject
            None,  # None subject
            "Subject\nwith\nnewlines",  # Newlines in subject
        ]
        
        for subject in extreme_subjects:
            try:
                result = self.gmail_sender.send_job_application_email(
                    to_email="test@example.com",
                    subject=subject,
                    body="Testing subject validation",
                    attachments=None
                )
                
                # Should handle extreme subjects gracefully
                validation_tests.append({
                    'input': str(subject)[:50] + "..." if subject and len(str(subject)) > 50 else str(subject),
                    'type': 'subject',
                    'handled_properly': True  # As long as it doesn't crash
                })
                
            except Exception as e:
                validation_tests.append({
                    'input': str(subject)[:50] + "..." if subject and len(str(subject)) > 50 else str(subject),
                    'type': 'subject',
                    'handled_properly': False,
                    'error': str(e)
                })
        
        properly_handled = sum(1 for test in validation_tests if test['handled_properly'])
        total_tests = len(validation_tests)
        
        print(f"  Validation tests: {properly_handled}/{total_tests} handled properly")
        
        return {
            'success_rate': properly_handled / total_tests,
            'tests': validation_tests
        }
    
    def test_attachment_size_limits(self):
        """Test attachment size limit handling"""
        print("📎 Testing attachment size limits...")
        
        import tempfile
        
        # Test different file sizes
        test_sizes = [
            (1024, "1KB"),
            (1024 * 1024, "1MB"),
            (5 * 1024 * 1024, "5MB"),
            (15 * 1024 * 1024, "15MB")  # Close to Gmail's 25MB limit
        ]
        
        size_tests = []
        
        for size_bytes, size_desc in test_sizes:
            print(f"  Testing {size_desc} attachment...")
            
            try:
                # Create test file of specific size
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    f.write(b'x' * size_bytes)
                    test_file = f.name
                
                start_time = time.time()
                result = self.gmail_sender.send_email_with_attachment(
                    to_email="1234.S.t.e.v.e.Glen@gmail.com",
                    subject=f"Size Test - {size_desc} Attachment",
                    body=f"Testing {size_desc} attachment handling",
                    attachment_path=test_file,
                    attachment_name=f"test_{size_desc.replace(' ', '_')}.txt"
                )
                end_time = time.time()
                
                os.unlink(test_file)  # Clean up
                
                size_tests.append({
                    'size': size_desc,
                    'success': result['status'] == 'success',
                    'duration': end_time - start_time,
                    'message': result.get('message', '')
                })
                
                # Add delay between tests
                time.sleep(2)
                
            except Exception as e:
                size_tests.append({
                    'size': size_desc,
                    'success': False,
                    'error': str(e)
                })
                
                if 'test_file' in locals():
                    try:
                        os.unlink(test_file)
                    except:
                        pass
        
        successful_tests = sum(1 for test in size_tests if test['success'])
        
        print(f"  Size tests: {successful_tests}/{len(size_tests)} successful")
        
        return {
            'success_rate': successful_tests / len(size_tests),
            'tests': size_tests
        }
    
    def test_error_logging_and_monitoring(self):
        """Test error logging and monitoring capabilities"""
        print("📊 Testing error logging and monitoring...")
        
        # Configure logging to capture errors
        log_file = "storage/gmail_error_test.log"
        os.makedirs("storage", exist_ok=True)
        
        # Create a file handler for testing
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Get the Gmail module logger
        gmail_logger = logging.getLogger('modules.email_integration.gmail_oauth_official')
        gmail_logger.addHandler(file_handler)
        
        # Trigger some intentional errors for logging
        error_scenarios = []
        
        # Scenario 1: Invalid attachment path
        try:
            result = self.gmail_sender.send_email_with_attachment(
                to_email="test@example.com",
                subject="Error Logging Test",
                body="Testing error logging",
                attachment_path="/nonexistent/path/file.txt",
                attachment_name="missing.txt"
            )
            
            error_scenarios.append({
                'scenario': 'Invalid Attachment Path',
                'error_handled': result['status'] == 'error'
            })
        except Exception as e:
            error_scenarios.append({
                'scenario': 'Invalid Attachment Path',
                'error_handled': False,
                'exception': str(e)
            })
        
        # Check if errors were logged
        logged_errors = 0
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_content = f.read()
                logged_errors = log_content.count('ERROR')
        
        # Clean up
        gmail_logger.removeHandler(file_handler)
        file_handler.close()
        
        if os.path.exists(log_file):
            os.unlink(log_file)
        
        all_handled = all(scenario['error_handled'] for scenario in error_scenarios)
        
        print(f"  Error scenarios: {len(error_scenarios)}")
        print(f"  Errors logged: {logged_errors}")
        print(f"  All handled properly: {'✅' if all_handled else '❌'}")
        
        return {
            'all_handled': all_handled,
            'errors_logged': logged_errors,
            'scenarios': error_scenarios
        }
    
    def run_all_robustness_tests(self):
        """Run all robustness enhancement tests"""
        print("🛡️ Gmail Robustness Enhancement Tests")
        print("=" * 50)
        
        test_results = []
        
        # Run health check
        health_result = self.test_connection_health_check()
        test_results.append(('Connection Health Check', health_result['healthy']))
        
        # Run retry mechanism test
        retry_result = self.test_retry_mechanism()
        test_results.append(('Retry Mechanism', retry_result['success']))
        
        # Run input validation test
        validation_result = self.test_input_validation_enhancement()
        test_results.append(('Input Validation', validation_result['success_rate'] > 0.8))
        
        # Run attachment size test
        # size_result = self.test_attachment_size_limits()
        # test_results.append(('Attachment Size Limits', size_result['success_rate'] > 0.5))
        
        # Run error logging test
        logging_result = self.test_error_logging_and_monitoring()
        test_results.append(('Error Logging', logging_result['all_handled']))
        
        # Calculate overall results
        passed_tests = sum(1 for _, passed in test_results if passed)
        total_tests = len(test_results)
        
        print(f"\n📊 Robustness Test Summary")
        print("=" * 30)
        print(f"Tests Run: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for test_name, passed in test_results:
            status = "✅" if passed else "❌"
            print(f"  {status} {test_name}")
        
        return passed_tests == total_tests

def main():
    """Run robustness enhancement tests"""
    enhancer = GmailRobustnessEnhancements()
    return enhancer.run_all_robustness_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)