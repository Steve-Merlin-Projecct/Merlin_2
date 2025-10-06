#!/usr/bin/env python3
"""
End-to-End Workflow Testing for Automated Job Application System

This script tests the complete workflow from job discovery through 
application submission to verify all system components work together.

Version: 2.16.5
Date: July 28, 2025
"""

import os
import sys
import json
import uuid
import time
import requests
import traceback
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class EndToEndWorkflowTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.test_results = []
        self.test_data = {}
        
        # Configure session for dashboard authentication
        self.dashboard_password = "jellyfish–lantern–kisses"
        
        print("🚀 Starting End-to-End Workflow Testing")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    def authenticate_dashboard(self):
        """Authenticate with dashboard for protected endpoints"""
        try:
            response = self.session.post(
                f"{self.base_url}/dashboard/authenticate",
                json={'password': self.dashboard_password}
            )
            
            if response.status_code == 200:
                self.log_test("Dashboard Authentication", True, "Successfully authenticated")
                return True
            else:
                self.log_test("Dashboard Authentication", False, 
                            f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Authentication", False, f"Exception: {str(e)}")
            return False

    def test_system_health(self):
        """Test system health and basic connectivity"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_test("System Health Check", True, 
                            f"System healthy - Version: {health_data.get('version', 'unknown')}")
                return True
            else:
                self.log_test("System Health Check", False, 
                            f"Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("System Health Check", False, f"Connection failed: {str(e)}")
            return False

    def test_database_connectivity(self):
        """Test database connectivity and basic operations"""
        try:
            # Try to access database statistics
            response = self.session.get(f"{self.base_url}/api/db/stats/applications")
            
            if response.status_code == 200:
                stats = response.json()
                self.log_test("Database Connectivity", True, 
                            f"Database accessible - Applications: {stats.get('total_applications', 0)}")
                return True
            elif response.status_code == 401:
                # Try with API key if available
                api_key = os.environ.get('WEBHOOK_API_KEY')
                if api_key:
                    headers = {'Authorization': f'Bearer {api_key}'}
                    response = requests.get(f"{self.base_url}/api/db/stats/applications", 
                                          headers=headers)
                    if response.status_code == 200:
                        stats = response.json()
                        self.log_test("Database Connectivity", True, 
                                    f"Database accessible with API key")
                        return True
                
                self.log_test("Database Connectivity", False, "Authentication required")
                return False
            else:
                self.log_test("Database Connectivity", False, 
                            f"Database query failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Connectivity", False, f"Database error: {str(e)}")
            return False

    def test_security_framework(self):
        """Test security framework and authentication"""
        try:
            # Test protected endpoint without authentication
            response = requests.get(f"{self.base_url}/api/link-tracking/analytics/test123")
            
            if response.status_code == 401:
                self.log_test("Security Framework", True, 
                            "Protected endpoints properly require authentication")
                return True
            else:
                self.log_test("Security Framework", False, 
                            f"Security bypass detected: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Security Framework", False, f"Security test error: {str(e)}")
            return False

    def test_link_tracking_system(self):
        """Test link tracking creation and analytics"""
        try:
            # Test link creation with API key
            api_key = os.environ.get('LINK_TRACKING_API_KEY', 'test-key-for-workflow-testing')
            headers = {'X-API-Key': api_key}
            
            link_data = {
                'url': 'https://example.com/test-job-posting',
                'function': 'Job_Posting',
                'metadata': {
                    'job_id': str(uuid.uuid4()),
                    'company_name': 'Test Company',
                    'position': 'Software Engineer'
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/link-tracking/create",
                headers=headers,
                json=link_data
            )
            
            if response.status_code == 201:
                tracking_data = response.json()
                tracking_id = tracking_data.get('tracking_id')
                self.test_data['tracking_id'] = tracking_id
                
                self.log_test("Link Tracking Creation", True, 
                            f"Link created: {tracking_id}")
                
                # Test analytics retrieval
                analytics_response = requests.get(
                    f"{self.base_url}/api/link-tracking/analytics/{tracking_id}",
                    headers=headers
                )
                
                if analytics_response.status_code == 200:
                    self.log_test("Link Analytics", True, 
                                "Analytics data retrieved successfully")
                    return True
                else:
                    self.log_test("Link Analytics", False, 
                                f"Analytics failed: {analytics_response.status_code}")
                    return False
                    
            else:
                self.log_test("Link Tracking Creation", False, 
                            f"Link creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Link Tracking System", False, f"Link tracking error: {str(e)}")
            return False

    def test_document_generation(self):
        """Test document generation system"""
        try:
            # Test resume generation
            document_data = {
                'job_id': str(uuid.uuid4()),
                'template': 'harvard_mcs',
                'customizations': {
                    'highlight_skills': ['Python', 'Flask', 'PostgreSQL'],
                    'target_keywords': ['software', 'engineer', 'backend']
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/documents/resume",
                json=document_data
            )
            
            if response.status_code == 200:
                doc_data = response.json()
                document_id = doc_data.get('document_id')
                self.test_data['document_id'] = document_id
                
                self.log_test("Document Generation", True, 
                            f"Resume generated: {document_id}")
                return True
            elif response.status_code == 401:
                self.log_test("Document Generation", False, 
                            "Authentication required for document generation")
                return False
            else:
                self.log_test("Document Generation", False, 
                            f"Document generation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Document Generation", False, f"Document error: {str(e)}")
            return False

    def test_ai_analysis_integration(self):
        """Test AI job analysis integration"""
        try:
            # Test AI usage statistics
            response = self.session.get(f"{self.base_url}/api/ai/usage-stats")
            
            if response.status_code == 200:
                usage_data = response.json()
                self.log_test("AI Analysis Integration", True, 
                            f"AI system accessible - Daily usage: {usage_data.get('current_usage', {}).get('requests_today', 0)}")
                return True
            elif response.status_code == 401:
                self.log_test("AI Analysis Integration", False, 
                            "Authentication required for AI endpoints")
                return False
            else:
                self.log_test("AI Analysis Integration", False, 
                            f"AI system error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI Analysis Integration", False, f"AI error: {str(e)}")
            return False

    def test_email_integration(self):
        """Test email integration and OAuth status"""
        try:
            # Test OAuth status
            response = self.session.get(f"{self.base_url}/api/email/oauth/status")
            
            if response.status_code == 200:
                oauth_data = response.json()
                status = oauth_data.get('status', 'unknown')
                email = oauth_data.get('email', 'unknown')
                
                self.log_test("Email Integration", True, 
                            f"OAuth status: {status}, Email: {email}")
                return True
            elif response.status_code == 401:
                self.log_test("Email Integration", False, 
                            "Authentication required for email endpoints")
                return False
            else:
                self.log_test("Email Integration", False, 
                            f"Email system error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Email Integration", False, f"Email error: {str(e)}")
            return False

    def test_user_preferences_system(self):
        """Test user preferences and profile management"""
        try:
            # Test Steve Glen profile access
            response = self.session.get(f"{self.base_url}/api/user-profile/steve-glen")
            
            if response.status_code == 200:
                profile_data = response.json()
                user_name = profile_data.get('user', {}).get('name', 'unknown')
                packages = len(profile_data.get('preference_packages', []))
                
                self.log_test("User Preferences System", True, 
                            f"Profile loaded: {user_name}, Packages: {packages}")
                return True
            elif response.status_code == 401:
                self.log_test("User Preferences System", False, 
                            "Authentication required for profile endpoints")
                return False
            else:
                self.log_test("User Preferences System", False, 
                            f"Profile system error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Preferences System", False, f"Profile error: {str(e)}")
            return False

    def test_workflow_orchestration(self):
        """Test complete workflow orchestration"""
        try:
            # Create a test job workflow
            workflow_data = {
                'job_id': str(uuid.uuid4()),
                'auto_send': False,
                'review_required': True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/workflow/process-application",
                json=workflow_data
            )
            
            if response.status_code == 200:
                workflow_result = response.json()
                workflow_id = workflow_result.get('workflow_id')
                steps = len(workflow_result.get('steps', []))
                
                self.log_test("Workflow Orchestration", True, 
                            f"Workflow created: {workflow_id}, Steps: {steps}")
                return True
            elif response.status_code == 401:
                self.log_test("Workflow Orchestration", False, 
                            "Authentication required for workflow endpoints")
                return False
            else:
                self.log_test("Workflow Orchestration", False, 
                            f"Workflow error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Workflow Orchestration", False, f"Workflow error: {str(e)}")
            return False

    def test_redirect_functionality(self):
        """Test link redirect functionality"""
        try:
            tracking_id = self.test_data.get('tracking_id')
            if not tracking_id:
                self.log_test("Redirect Functionality", False, 
                            "No tracking ID available for redirect test")
                return False
            
            # Test redirect (don't follow redirects to avoid external calls)
            response = requests.get(
                f"{self.base_url}/r/{tracking_id}",
                allow_redirects=False
            )
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location')
                self.log_test("Redirect Functionality", True, 
                            f"Redirect working: {redirect_url}")
                return True
            else:
                self.log_test("Redirect Functionality", False, 
                            f"Redirect failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Redirect Functionality", False, f"Redirect error: {str(e)}")
            return False

    def test_frontend_accessibility(self):
        """Test frontend dashboard accessibility"""
        try:
            # Test dashboard login page
            response = requests.get(f"{self.base_url}/dashboard")
            
            if response.status_code == 200 and "login" in response.text.lower():
                self.log_test("Frontend Dashboard", True, 
                            "Dashboard login page accessible")
                
                # Test authenticated dashboard access
                dashboard_response = self.session.get(f"{self.base_url}/dashboard")
                if dashboard_response.status_code == 200:
                    self.log_test("Dashboard Authentication", True, 
                                "Authenticated dashboard accessible")
                    return True
                else:
                    self.log_test("Dashboard Authentication", False, 
                                f"Dashboard access failed: {dashboard_response.status_code}")
                    return False
            else:
                self.log_test("Frontend Dashboard", False, 
                            f"Dashboard not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Frontend Accessibility", False, f"Frontend error: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run all end-to-end tests"""
        print("🔍 Running Comprehensive End-to-End Tests\n")
        
        test_functions = [
            self.test_system_health,
            self.authenticate_dashboard,
            self.test_database_connectivity,
            self.test_security_framework,
            self.test_link_tracking_system,
            self.test_document_generation,
            self.test_ai_analysis_integration,
            self.test_email_integration,
            self.test_user_preferences_system,
            self.test_workflow_orchestration,
            self.test_redirect_functionality,
            self.test_frontend_accessibility
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                result = test_func()
                if result:
                    passed_tests += 1
                print()  # Add spacing between tests
            except Exception as e:
                print(f"❌ FAIL {test_func.__name__}: Unexpected error: {str(e)}")
                print()
        
        return passed_tests, total_tests

    def generate_test_report(self, passed_tests, total_tests):
        """Generate comprehensive test report"""
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("="*70)
        print("📊 END-TO-END WORKFLOW TEST REPORT")
        print("="*70)
        print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print()
        
        print("📋 Test Results Summary:")
        print("-" * 50)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print()
        print("🔍 System Status Assessment:")
        print("-" * 50)
        
        if success_rate >= 90:
            print("🟢 EXCELLENT: System is fully operational and production-ready")
        elif success_rate >= 75:
            print("🟡 GOOD: System is mostly functional with minor issues")
        elif success_rate >= 50:
            print("🟠 FAIR: System has significant issues requiring attention")
        else:
            print("🔴 POOR: System has critical failures requiring immediate attention")
        
        print()
        print("💡 Recommendations:")
        print("-" * 50)
        
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("Priority fixes needed:")
            for failed in failed_tests:
                print(f"  • Fix {failed['test']}: {failed['message']}")
        else:
            print("  • All systems operational - ready for production use")
            print("  • Consider implementing security enhancements for 9.0/10 rating")
            print("  • Monitor system performance and user feedback")
        
        print()
        print("🔗 Next Steps:")
        print("-" * 50)
        print("  1. Address any failed test components")
        print("  2. Review security assessment recommendations")
        print("  3. Validate with actual job application workflow")
        print("  4. Consider load testing for production deployment")
        
        return {
            'success_rate': success_rate,
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'detailed_results': self.test_results,
            'system_status': 'operational' if success_rate >= 75 else 'needs_attention'
        }

def main():
    """Main test execution"""
    tester = EndToEndWorkflowTester()
    
    try:
        passed_tests, total_tests = tester.run_comprehensive_tests()
        report = tester.generate_test_report(passed_tests, total_tests)
        
        # Save detailed report
        with open('test_results_end_to_end_workflow.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: test_results_end_to_end_workflow.json")
        
        # Return appropriate exit code
        sys.exit(0 if report['success_rate'] >= 75 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()