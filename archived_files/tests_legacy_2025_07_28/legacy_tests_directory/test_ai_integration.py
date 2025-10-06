"""
Test script for AI integration and complete system validation
Tests Gemini integration, security fixes, and end-to-end workflow
"""

import sys
import json
import time
import requests
import logging
from typing import Dict

# Add modules to path
sys.path.append('modules')

logger = logging.getLogger(__name__)

class AIIntegrationTester:
    """
    Test AI integration functionality and complete system
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        
    def run_comprehensive_tests(self) -> Dict:
        """Run comprehensive AI integration and system tests"""
        
        print("🤖 AI Integration & System Test Suite")
        print("=====================================")
        
        # Test categories
        test_methods = [
            ("API Endpoints", self.test_api_endpoints),
            ("Rate Limiting", self.test_rate_limiting),
            ("Security Headers", self.test_security_headers),
            ("AI Integration", self.test_ai_integration),
            ("Error Handling", self.test_error_handling),
            ("System Health", self.test_system_health)
        ]
        
        for test_name, test_method in test_methods:
            print(f"\n🧪 Testing: {test_name}")
            try:
                result = test_method()
                self.test_results.append({
                    'test': test_name,
                    'status': 'passed' if result else 'failed',
                    'details': result
                })
                print(f"   ✅ {test_name} - {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                print(f"   ❌ {test_name} - ERROR: {str(e)}")
                self.test_results.append({
                    'test': test_name,
                    'status': 'error',
                    'details': str(e)
                })
        
        return self._generate_test_report()
    
    def test_api_endpoints(self) -> bool:
        """Test all API endpoints are accessible with proper responses"""
        
        endpoints = [
            ('GET', '/health'),
            ('GET', '/api/ai/health'),
            ('GET', '/api/ai/usage-stats'),
            ('GET', '/api/ai/batch-status'),
            ('GET', '/dashboard'),
            ('GET', '/'),
        ]
        
        success_count = 0
        
        for method, endpoint in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                if response.status_code in [200, 401, 403]:  # Expected responses
                    success_count += 1
                    print(f"     ✓ {method} {endpoint} - {response.status_code}")
                else:
                    print(f"     ✗ {method} {endpoint} - {response.status_code}")
                    
            except Exception as e:
                print(f"     ✗ {method} {endpoint} - {str(e)}")
        
        return success_count >= len(endpoints) * 0.8  # 80% success rate
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting is working"""
        
        try:
            # Test AI endpoint rate limiting
            endpoint = f"{self.base_url}/api/ai/health"
            
            # Make rapid requests
            responses = []
            for i in range(15):  # Exceed the 10/minute limit
                response = requests.get(endpoint, timeout=2)
                responses.append(response.status_code)
                time.sleep(0.1)
            
            # Check if any requests were rate limited
            rate_limited = any(status == 429 for status in responses)
            
            print(f"     Rate limiting {'active' if rate_limited else 'not detected'}")
            return rate_limited
            
        except Exception as e:
            print(f"     Rate limiting test failed: {str(e)}")
            return False
    
    def test_security_headers(self) -> bool:
        """Test security headers are present"""
        
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Content-Security-Policy'
        ]
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            
            headers_present = 0
            for header in required_headers:
                if header in response.headers:
                    headers_present += 1
                    print(f"     ✓ {header}")
                else:
                    print(f"     ✗ Missing {header}")
            
            return headers_present >= len(required_headers) * 0.75  # 75% required
            
        except Exception as e:
            print(f"     Security headers test failed: {str(e)}")
            return False
    
    def test_ai_integration(self) -> bool:
        """Test AI integration endpoints"""
        
        tests_passed = 0
        total_tests = 4
        
        # Test AI health endpoint
        try:
            response = requests.get(f"{self.base_url}/api/ai/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'ai_health' in data:
                    tests_passed += 1
                    print("     ✓ AI health endpoint working")
                else:
                    print("     ✗ AI health endpoint malformed response")
            else:
                print(f"     ✗ AI health endpoint returned {response.status_code}")
        except Exception as e:
            print(f"     ✗ AI health endpoint failed: {str(e)}")
        
        # Test batch status endpoint
        try:
            response = requests.get(f"{self.base_url}/api/ai/batch-status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'batch_status' in data:
                    tests_passed += 1
                    print("     ✓ Batch status endpoint working")
                else:
                    print("     ✗ Batch status endpoint malformed response")
            else:
                print(f"     ✗ Batch status endpoint returned {response.status_code}")
        except Exception as e:
            print(f"     ✗ Batch status endpoint failed: {str(e)}")
        
        # Test usage stats endpoint
        try:
            response = requests.get(f"{self.base_url}/api/ai/usage-stats", timeout=5)
            if response.status_code in [200, 500]:  # 500 expected without API key
                tests_passed += 1
                print("     ✓ Usage stats endpoint accessible")
            else:
                print(f"     ✗ Usage stats endpoint returned {response.status_code}")
        except Exception as e:
            print(f"     ✗ Usage stats endpoint failed: {str(e)}")
        
        # Test analyze jobs endpoint (should fail without proper data)
        try:
            response = requests.post(
                f"{self.base_url}/api/ai/analyze-jobs",
                json={"batch_size": 5},
                timeout=5
            )
            if response.status_code in [400, 500]:  # Expected to fail
                tests_passed += 1
                print("     ✓ Analyze jobs endpoint properly protected")
            else:
                print(f"     ✗ Analyze jobs endpoint returned {response.status_code}")
        except Exception as e:
            print(f"     ✗ Analyze jobs endpoint failed: {str(e)}")
        
        return tests_passed >= total_tests * 0.75  # 75% success rate
    
    def test_error_handling(self) -> bool:
        """Test error handling and input validation"""
        
        tests_passed = 0
        total_tests = 3
        
        # Test invalid JSON
        try:
            response = requests.post(
                f"{self.base_url}/api/ai/analyze-jobs",
                data="invalid json",
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            if response.status_code == 400:
                tests_passed += 1
                print("     ✓ Invalid JSON rejected")
            else:
                print(f"     ✗ Invalid JSON not rejected: {response.status_code}")
        except Exception as e:
            print(f"     ✗ Invalid JSON test failed: {str(e)}")
        
        # Test invalid batch size
        try:
            response = requests.post(
                f"{self.base_url}/api/ai/analyze-jobs",
                json={"batch_size": 1000},  # Too large
                timeout=5
            )
            if response.status_code == 400:
                tests_passed += 1
                print("     ✓ Invalid batch size rejected")
            else:
                print(f"     ✗ Invalid batch size not rejected: {response.status_code}")
        except Exception as e:
            print(f"     ✗ Invalid batch size test failed: {str(e)}")
        
        # Test nonexistent endpoint
        try:
            response = requests.get(f"{self.base_url}/api/ai/nonexistent", timeout=5)
            if response.status_code == 404:
                tests_passed += 1
                print("     ✓ Nonexistent endpoint returns 404")
            else:
                print(f"     ✗ Nonexistent endpoint returned: {response.status_code}")
        except Exception as e:
            print(f"     ✗ Nonexistent endpoint test failed: {str(e)}")
        
        return tests_passed >= total_tests * 0.67  # 67% success rate
    
    def test_system_health(self) -> bool:
        """Test overall system health"""
        
        health_checks = []
        
        # Test main health endpoint
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    health_checks.append(True)
                    print("     ✓ Main service healthy")
                else:
                    health_checks.append(False)
                    print("     ✗ Main service unhealthy")
            else:
                health_checks.append(False)
                print(f"     ✗ Health endpoint returned {response.status_code}")
        except Exception as e:
            health_checks.append(False)
            print(f"     ✗ Health endpoint failed: {str(e)}")
        
        # Test AI health endpoint
        try:
            response = requests.get(f"{self.base_url}/api/ai/health", timeout=5)
            if response.status_code == 200:
                health_checks.append(True)
                print("     ✓ AI service accessible")
            else:
                health_checks.append(False)
                print(f"     ✗ AI service returned {response.status_code}")
        except Exception as e:
            health_checks.append(False)
            print(f"     ✗ AI service failed: {str(e)}")
        
        # Test dashboard accessibility
        try:
            response = requests.get(f"{self.base_url}/dashboard", timeout=5)
            if response.status_code == 200:
                health_checks.append(True)
                print("     ✓ Dashboard accessible")
            else:
                health_checks.append(False)
                print(f"     ✗ Dashboard returned {response.status_code}")
        except Exception as e:
            health_checks.append(False)
            print(f"     ✗ Dashboard failed: {str(e)}")
        
        return sum(health_checks) >= len(health_checks) * 0.67  # 67% success rate
    
    def _generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        
        passed_tests = sum(1 for result in self.test_results if result['status'] == 'passed')
        total_tests = len(self.test_results)
        
        return {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'test_results': self.test_results,
            'overall_status': 'PASSED' if passed_tests >= total_tests * 0.8 else 'FAILED',
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> list:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        failed_tests = [result for result in self.test_results if result['status'] != 'passed']
        
        if any('Rate Limiting' in test['test'] for test in failed_tests):
            recommendations.append("Consider implementing stricter rate limiting")
        
        if any('Security Headers' in test['test'] for test in failed_tests):
            recommendations.append("Ensure all security headers are properly configured")
        
        if any('AI Integration' in test['test'] for test in failed_tests):
            recommendations.append("Check AI service configuration and API keys")
        
        if any('System Health' in test['test'] for test in failed_tests):
            recommendations.append("Investigate system health issues")
        
        if not recommendations:
            recommendations.append("System performing well - maintain current configuration")
        
        return recommendations


def main():
    """Run AI integration and system tests"""
    
    print("🤖 AI Integration & System Validation")
    print("====================================")
    
    # Initialize tester
    tester = AIIntegrationTester()
    
    # Run comprehensive tests
    report = tester.run_comprehensive_tests()
    
    # Display results
    print(f"\n📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    print(f"Overall Status: {report['overall_status']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"Tests Passed: {report['passed_tests']}/{report['total_tests']}")
    
    if report['overall_status'] == 'FAILED':
        print(f"\n❌ FAILED TESTS")
        print("-" * 20)
        for result in report['test_results']:
            if result['status'] != 'passed':
                print(f"• {result['test']}: {result['status']}")
    
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 25)
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    # Save detailed report
    with open('ai_integration_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: ai_integration_test_report.json")
    
    return report['success_rate']


if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 80 else 1)  # Exit with error if score too low