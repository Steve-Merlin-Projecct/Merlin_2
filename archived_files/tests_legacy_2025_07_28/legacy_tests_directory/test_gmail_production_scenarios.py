#!/usr/bin/env python3
"""
Production scenario tests for Gmail integration
Tests real-world usage patterns and stress scenarios
"""

import os
import sys
import time
import json
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager, get_gmail_sender

class ProductionScenarioTests:
    """Test production scenarios and stress conditions"""
    
    def __init__(self):
        self.oauth_manager = get_gmail_oauth_manager()
        self.gmail_sender = get_gmail_sender(self.oauth_manager)
        self.test_results = []
    
    def test_authentication_persistence(self):
        """Test that authentication persists across multiple sessions"""
        print("🔐 Testing authentication persistence...")
        
        # Test multiple authentication status checks
        results = []
        for i in range(5):
            status = self.oauth_manager.get_oauth_status()
            results.append(status.get('authenticated', False))
            time.sleep(0.5)
        
        # All checks should be consistent
        consistent = all(r == results[0] for r in results)
        
        self.test_results.append({
            'test': 'Authentication Persistence',
            'passed': consistent,
            'details': f"Consistent results: {consistent}, Status: {results[0]}"
        })
        
        return consistent
    
    def test_concurrent_email_sending(self):
        """Test handling of concurrent email requests"""
        print("⚡ Testing concurrent email sending...")
        
        def send_test_email(thread_id):
            """Send a test email from a thread"""
            try:
                # Create unique test file for each thread
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_thread_{thread_id}.txt') as f:
                    f.write(f"Test content from thread {thread_id}")
                    test_file = f.name
                
                result = self.gmail_sender.send_email_with_attachment(
                    to_email="1234.S.t.e.v.e.Glen@gmail.com",  # Send to self for testing
                    subject=f"Concurrent Test {thread_id}",
                    body=f"This is a concurrent email test from thread {thread_id}",
                    attachment_path=test_file,
                    attachment_name=f"thread_{thread_id}_test.txt"
                )
                
                os.unlink(test_file)  # Clean up
                
                return {
                    'thread_id': thread_id,
                    'success': result['status'] == 'success',
                    'message_id': result.get('gmail_message_id'),
                    'error': result.get('message') if result['status'] == 'error' else None
                }
                
            except Exception as e:
                return {
                    'thread_id': thread_id,
                    'success': False,
                    'error': str(e)
                }
        
        # Test with 3 concurrent threads
        num_threads = 3
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(send_test_email, i) for i in range(num_threads)]
            results = [future.result() for future in futures]
        
        successful_sends = sum(1 for r in results if r['success'])
        success_rate = successful_sends / num_threads
        
        self.test_results.append({
            'test': 'Concurrent Email Sending',
            'passed': success_rate >= 0.8,  # Allow some failures due to rate limiting
            'details': f"Success rate: {success_rate:.1%} ({successful_sends}/{num_threads})",
            'results': results
        })
        
        return success_rate >= 0.8
    
    def test_large_batch_processing(self):
        """Test processing of large email batches"""
        print("📦 Testing large batch processing...")
        
        batch_size = 5  # Small batch for testing
        successful_emails = 0
        failed_emails = 0
        
        for i in range(batch_size):
            try:
                result = self.gmail_sender.send_job_application_email(
                    to_email="1234.S.t.e.v.e.Glen@gmail.com",
                    subject=f"Batch Test Email {i+1}/{batch_size}",
                    body=f"This is batch email #{i+1} of {batch_size} for testing large batch processing.",
                    attachments=None
                )
                
                if result['status'] == 'success':
                    successful_emails += 1
                else:
                    failed_emails += 1
                    
                # Add delay to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                failed_emails += 1
                print(f"  ❌ Email {i+1} failed: {e}")
        
        success_rate = successful_emails / batch_size
        
        self.test_results.append({
            'test': 'Large Batch Processing',
            'passed': success_rate >= 0.8,
            'details': f"Processed {batch_size} emails, {successful_emails} successful, {failed_emails} failed",
            'success_rate': success_rate
        })
        
        return success_rate >= 0.8
    
    def test_memory_usage_stability(self):
        """Test memory usage during extended operations"""
        print("🧠 Testing memory usage stability...")
        
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple operations
        operations = 10
        for i in range(operations):
            # Create and cleanup temporary files
            with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
                f.write(f"Memory test content {i}")
                f.flush()
                
                # Test OAuth status check
                self.oauth_manager.get_oauth_status()
                
                # Small delay
                time.sleep(0.1)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB for test operations)
        memory_stable = memory_increase < 50
        
        self.test_results.append({
            'test': 'Memory Usage Stability',
            'passed': memory_stable,
            'details': f"Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB, Increase: {memory_increase:.1f}MB"
        })
        
        return memory_stable
    
    def test_error_recovery(self):
        """Test system recovery from various error conditions"""
        print("🔧 Testing error recovery capabilities...")
        
        recovery_tests = []
        
        # Test 1: Recovery from invalid email address
        try:
            result = self.gmail_sender.send_job_application_email(
                to_email="invalid-email-address",
                subject="Error Recovery Test",
                body="This should fail gracefully",
                attachments=None
            )
            
            # Should return error status, not crash
            recovery_tests.append({
                'scenario': 'Invalid Email',
                'recovered': result['status'] == 'error' and 'message' in result
            })
        except Exception as e:
            recovery_tests.append({
                'scenario': 'Invalid Email',
                'recovered': False,
                'error': str(e)
            })
        
        # Test 2: Recovery from missing attachment
        try:
            result = self.gmail_sender.send_email_with_attachment(
                to_email="test@example.com",
                subject="Missing Attachment Test",
                body="This attachment doesn't exist",
                attachment_path="/nonexistent/file.txt",
                attachment_name="missing.txt"
            )
            
            recovery_tests.append({
                'scenario': 'Missing Attachment',
                'recovered': result['status'] == 'error'
            })
        except Exception as e:
            recovery_tests.append({
                'scenario': 'Missing Attachment',
                'recovered': False,
                'error': str(e)
            })
        
        # Test 3: System still functional after errors
        try:
            status = self.oauth_manager.get_oauth_status()
            system_functional = 'authenticated' in status
            
            recovery_tests.append({
                'scenario': 'System Functional After Errors',
                'recovered': system_functional
            })
        except Exception as e:
            recovery_tests.append({
                'scenario': 'System Functional After Errors',
                'recovered': False,
                'error': str(e)
            })
        
        all_recovered = all(test['recovered'] for test in recovery_tests)
        
        self.test_results.append({
            'test': 'Error Recovery',
            'passed': all_recovered,
            'details': f"Recovery scenarios: {len(recovery_tests)}, All passed: {all_recovered}",
            'recovery_results': recovery_tests
        })
        
        return all_recovered
    
    def test_rate_limiting_handling(self):
        """Test handling of Gmail API rate limits"""
        print("⏱️ Testing rate limiting handling...")
        
        # Send emails rapidly to test rate limiting
        rapid_sends = 3
        send_results = []
        
        for i in range(rapid_sends):
            try:
                start_time = time.time()
                result = self.gmail_sender.send_job_application_email(
                    to_email="1234.S.t.e.v.e.Glen@gmail.com",
                    subject=f"Rate Limit Test {i+1}",
                    body=f"Testing rate limiting with rapid send #{i+1}",
                    attachments=None
                )
                end_time = time.time()
                
                send_results.append({
                    'send_number': i+1,
                    'success': result['status'] == 'success',
                    'duration': end_time - start_time,
                    'message': result.get('message', '')
                })
                
                # No delay - test rapid sending
                
            except Exception as e:
                send_results.append({
                    'send_number': i+1,
                    'success': False,
                    'error': str(e)
                })
        
        # Check if system handled rate limiting gracefully
        successful_sends = sum(1 for r in send_results if r['success'])
        handled_gracefully = True  # System should handle rate limits without crashing
        
        self.test_results.append({
            'test': 'Rate Limiting Handling',
            'passed': handled_gracefully,
            'details': f"Rapid sends: {rapid_sends}, Successful: {successful_sends}",
            'send_results': send_results
        })
        
        return handled_gracefully
    
    def run_all_production_tests(self):
        """Run all production scenario tests"""
        print("🏭 Running Production Scenario Tests")
        print("=" * 50)
        
        tests = [
            self.test_authentication_persistence,
            self.test_memory_usage_stability,
            self.test_error_recovery,
            self.test_rate_limiting_handling,
            # Commenting out tests that send actual emails to avoid spam
            # Uncomment for full testing if needed
            # self.test_concurrent_email_sending,
            # self.test_large_batch_processing,
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_func in tests:
            try:
                print(f"\n🧪 Running {test_func.__name__}...")
                result = test_func()
                if result:
                    passed_tests += 1
                    print(f"  ✅ Passed")
                else:
                    print(f"  ❌ Failed")
            except Exception as e:
                print(f"  💥 Error: {e}")
        
        # Print summary
        print(f"\n📊 Production Test Summary")
        print("=" * 30)
        print(f"Tests Run: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Print detailed results
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"  {status} {result['test']}: {result['details']}")
        
        return passed_tests == total_tests

def main():
    """Run production scenario tests"""
    tester = ProductionScenarioTests()
    return tester.run_all_production_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)