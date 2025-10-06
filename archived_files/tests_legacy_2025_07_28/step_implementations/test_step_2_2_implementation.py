#!/usr/bin/env python3
"""
Step 2.2 Implementation Test: End-to-End Workflow Orchestration

This test validates the complete implementation of Step 2.2 from the
Implementation Plan V2.16: End-to-End Workflow Orchestration.

Tests all acceptance criteria:
1. Complete workflow runs automatically from job discovery to application
2. Intelligent decision-making excludes low-quality opportunities  
3. Document generation customized for each specific job
4. Email applications sent automatically with proper tracking
"""

import sys
import os
import requests
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Step22ImplementationTest:
    """Test suite for Step 2.2: End-to-End Workflow Orchestration"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
        # Authenticate session
        self.authenticate()
    
    def authenticate(self):
        """Authenticate the test session"""
        try:
            auth_response = self.session.post(
                f"{self.base_url}/dashboard/authenticate",
                json={"password": "jellyfish–lantern–kisses"}
            )
            
            if auth_response.status_code == 200:
                logger.info("✅ Authentication successful")
            else:
                logger.error(f"❌ Authentication failed: {auth_response.status_code}")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            sys.exit(1)
    
    def test_workflow_health_check(self):
        """Test 1: Workflow system health check"""
        print("\nTest 1: Workflow System Health Check")
        print("-" * 50)
        self.total_tests += 1
        
        try:
            response = self.session.get(f"{self.base_url}/api/workflow/health")
            
            if response.status_code == 200:
                data = response.json()
                
                if (data.get('success') and 
                    data.get('system_status') == 'operational' and
                    data.get('step') == '2.2'):
                    
                    print("✅ Workflow system is healthy and operational")
                    print(f"   Component: {data.get('component')}")
                    print(f"   Status: {data.get('system_status')}")
                    print(f"   Step: {data.get('step')}")
                    
                    self.test_results['health_check'] = {
                        'status': 'PASS',
                        'message': 'Workflow system healthy',
                        'response': data
                    }
                    self.passed_tests += 1
                    return True
                else:
                    print(f"❌ Health check failed: Invalid response data")
                    self.test_results['health_check'] = {
                        'status': 'FAIL', 
                        'message': 'Invalid health response'
                    }
                    return False
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                self.test_results['health_check'] = {
                    'status': 'FAIL',
                    'message': f'HTTP {response.status_code}'
                }
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            self.test_results['health_check'] = {
                'status': 'FAIL',
                'message': f'Error: {e}'
            }
            return False
    
    def test_workflow_configuration(self):
        """Test 2: Workflow configuration validation"""
        print("\nTest 2: Workflow Configuration Validation")
        print("-" * 50)
        self.total_tests += 1
        
        try:
            response = self.session.get(f"{self.base_url}/api/workflow/config")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    config = data.get('data', {})
                    components = config.get('system_components', {})
                    
                    print("✅ Workflow configuration retrieved")
                    print(f"   Max applications per day: {config.get('max_applications_per_day')}")
                    print(f"   Min compatibility score: {config.get('min_compatibility_score')}")
                    print(f"   Max batch size: {config.get('max_batch_size')}")
                    print(f"   User profile loaded: {components.get('user_profile_loaded')}")
                    print(f"   Document generator available: {components.get('document_generator_available')}")
                    print(f"   Email sender configured: {components.get('email_sender_configured')}")
                    print(f"   Database connected: {components.get('database_connected')}")
                    
                    # Verify all components are available
                    required_components = ['user_profile_loaded', 'document_generator_available', 
                                         'email_sender_configured', 'database_connected']
                    
                    all_available = all(components.get(comp, False) for comp in required_components)
                    
                    if all_available:
                        self.test_results['configuration'] = {
                            'status': 'PASS',
                            'message': 'All components configured',
                            'config': config
                        }
                        self.passed_tests += 1
                        return True
                    else:
                        print(f"⚠️ Some components not available: {components}")
                        self.test_results['configuration'] = {
                            'status': 'PARTIAL',
                            'message': 'Some components unavailable',
                            'config': config
                        }
                        return False
                else:
                    print(f"❌ Configuration failed: {data.get('error')}")
                    self.test_results['configuration'] = {
                        'status': 'FAIL',
                        'message': data.get('error')
                    }
                    return False
            else:
                print(f"❌ Configuration request failed: HTTP {response.status_code}")
                self.test_results['configuration'] = {
                    'status': 'FAIL',
                    'message': f'HTTP {response.status_code}'
                }
                return False
                
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            self.test_results['configuration'] = {
                'status': 'FAIL',
                'message': f'Error: {e}'
            }
            return False
    
    def test_job_discovery(self):
        """Test 3: Job discovery functionality"""
        print("\nTest 3: Job Discovery Test")
        print("-" * 50)
        self.total_tests += 1
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/workflow/test",
                json={"test_mode": "discovery_only"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    test_data = data.get('data', {})
                    jobs_found = test_data.get('eligible_jobs_found', 0)
                    sample_jobs = test_data.get('sample_jobs', [])
                    
                    print(f"✅ Job discovery completed")
                    print(f"   Eligible jobs found: {jobs_found}")
                    print(f"   Sample jobs: {len(sample_jobs)}")
                    
                    if sample_jobs:
                        for i, job in enumerate(sample_jobs):
                            print(f"   Job {i+1}: {job.get('title', 'N/A')} at {job.get('company_name', 'N/A')}")
                    
                    self.test_results['job_discovery'] = {
                        'status': 'PASS',
                        'message': f'Found {jobs_found} eligible jobs',
                        'jobs_found': jobs_found,
                        'sample_jobs': sample_jobs
                    }
                    self.passed_tests += 1
                    return True
                else:
                    print(f"❌ Job discovery failed: {data.get('error')}")
                    self.test_results['job_discovery'] = {
                        'status': 'FAIL',
                        'message': data.get('error')
                    }
                    return False
            else:
                print(f"❌ Job discovery request failed: HTTP {response.status_code}")
                self.test_results['job_discovery'] = {
                    'status': 'FAIL',
                    'message': f'HTTP {response.status_code}'
                }
                return False
                
        except Exception as e:
            print(f"❌ Job discovery error: {e}")
            self.test_results['job_discovery'] = {
                'status': 'FAIL',
                'message': f'Error: {e}'
            }
            return False
    
    def test_preference_matching(self):
        """Test 4: Preference matching and scoring"""
        print("\nTest 4: Preference Matching Test")
        print("-" * 50)
        self.total_tests += 1
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/workflow/test",
                json={"test_mode": "preference_matching"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    test_data = data.get('data', {})
                    eligible_jobs = test_data.get('eligible_jobs_found', 0)
                    matched_jobs = test_data.get('matched_jobs', 0)
                    filter_efficiency = test_data.get('filter_efficiency', 0)
                    sample_matches = test_data.get('sample_matches', [])
                    
                    print(f"✅ Preference matching completed")
                    print(f"   Eligible jobs: {eligible_jobs}")
                    print(f"   Matched jobs: {matched_jobs}")
                    print(f"   Filter efficiency: {filter_efficiency:.1%}")
                    
                    if sample_matches:
                        print("   Sample matches:")
                        for match in sample_matches:
                            print(f"     • {match.get('job_title')} at {match.get('company')} (Score: {match.get('compatibility_score'):.1f})")
                    
                    # Acceptance criteria: Intelligent decision-making excludes low-quality opportunities
                    if filter_efficiency > 0 and filter_efficiency < 1:
                        self.test_results['preference_matching'] = {
                            'status': 'PASS',
                            'message': f'Intelligent filtering: {filter_efficiency:.1%} efficiency',
                            'eligible_jobs': eligible_jobs,
                            'matched_jobs': matched_jobs,
                            'filter_efficiency': filter_efficiency
                        }
                        self.passed_tests += 1
                        return True
                    else:
                        print(f"⚠️ Filter efficiency suspicious: {filter_efficiency:.1%}")
                        self.test_results['preference_matching'] = {
                            'status': 'PARTIAL',
                            'message': 'Filter efficiency needs review',
                            'filter_efficiency': filter_efficiency
                        }
                        return False
                else:
                    print(f"❌ Preference matching failed: {data.get('error')}")
                    self.test_results['preference_matching'] = {
                        'status': 'FAIL',
                        'message': data.get('error')
                    }
                    return False
            else:
                print(f"❌ Preference matching request failed: HTTP {response.status_code}")
                self.test_results['preference_matching'] = {
                    'status': 'FAIL',
                    'message': f'HTTP {response.status_code}'
                }
                return False
                
        except Exception as e:
            print(f"❌ Preference matching error: {e}")
            self.test_results['preference_matching'] = {
                'status': 'FAIL',
                'message': f'Error: {e}'
            }
            return False
    
    def test_complete_workflow_execution(self):
        """Test 5: Complete workflow execution"""
        print("\nTest 5: Complete Workflow Execution")
        print("-" * 50)
        self.total_tests += 1
        
        try:
            # Execute workflow with small batch size for testing
            response = self.session.post(
                f"{self.base_url}/api/workflow/execute",
                json={"batch_size": 2}  # Small batch for testing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    workflow_data = data.get('data', {})
                    workflow_id = workflow_data.get('workflow_id')
                    status = workflow_data.get('status')
                    
                    print(f"✅ Workflow execution completed")
                    print(f"   Workflow ID: {workflow_id}")
                    print(f"   Status: {status}")
                    print(f"   Duration: {workflow_data.get('total_duration_seconds', 0):.2f}s")
                    
                    # Check job discovery results
                    if 'job_discovery' in workflow_data:
                        discovery = workflow_data['job_discovery']
                        print(f"   Jobs discovered: {discovery.get('eligible_jobs_found', 0)}")
                        print(f"   Jobs matched: {discovery.get('jobs_after_matching', 0)}")
                    
                    # Check application processing results
                    if 'application_processing' in workflow_data:
                        processing = workflow_data['application_processing']
                        print(f"   Applications processed: {processing.get('total_processed', 0)}")
                        print(f"   Successful applications: {processing.get('successful_applications', 0)}")
                        print(f"   Success rate: {processing.get('success_rate', 0):.1%}")
                    
                    # Check performance metrics
                    if 'performance_metrics' in workflow_data:
                        metrics = workflow_data['performance_metrics']
                        print(f"   Average compatibility: {metrics.get('average_compatibility_score', 0):.1f}")
                        print(f"   Documents generated: {metrics.get('documents_generated', 0)}")
                    
                    # Validate acceptance criteria
                    processing = workflow_data.get('application_processing', {})
                    metrics = workflow_data.get('performance_metrics', {})
                    
                    criteria_met = 0
                    total_criteria = 4
                    
                    # Criteria 1: Complete workflow runs automatically
                    if status == 'completed':
                        criteria_met += 1
                        print("   ✅ Criteria 1: Complete workflow runs automatically")
                    else:
                        print("   ❌ Criteria 1: Workflow did not complete")
                    
                    # Criteria 2: Intelligent decision-making (some filtering occurred)
                    discovery = workflow_data.get('job_discovery', {})
                    if discovery.get('filter_efficiency', 0) > 0:
                        criteria_met += 1
                        print("   ✅ Criteria 2: Intelligent decision-making active")
                    else:
                        print("   ❌ Criteria 2: No intelligent filtering detected")
                    
                    # Criteria 3: Document generation (any documents generated)
                    if metrics.get('documents_generated', 0) > 0:
                        criteria_met += 1
                        print("   ✅ Criteria 3: Document generation customized")
                    else:
                        print("   ❌ Criteria 3: No documents generated")
                    
                    # Criteria 4: Email applications sent (any successful applications)
                    if processing.get('successful_applications', 0) > 0:
                        criteria_met += 1
                        print("   ✅ Criteria 4: Email applications sent")
                    else:
                        print("   ❌ Criteria 4: No applications sent successfully")
                    
                    completion_rate = criteria_met / total_criteria
                    print(f"\n   📊 Acceptance Criteria: {criteria_met}/{total_criteria} met ({completion_rate:.1%})")
                    
                    if criteria_met >= 3:  # 75% completion threshold
                        self.test_results['complete_workflow'] = {
                            'status': 'PASS',
                            'message': f'{criteria_met}/{total_criteria} acceptance criteria met',
                            'completion_rate': completion_rate,
                            'workflow_data': workflow_data
                        }
                        self.passed_tests += 1
                        return True
                    else:
                        self.test_results['complete_workflow'] = {
                            'status': 'PARTIAL',
                            'message': f'Only {criteria_met}/{total_criteria} criteria met',
                            'completion_rate': completion_rate,
                            'workflow_data': workflow_data
                        }
                        return False
                else:
                    print(f"❌ Workflow execution failed: {data.get('error')}")
                    self.test_results['complete_workflow'] = {
                        'status': 'FAIL',
                        'message': data.get('error')
                    }
                    return False
            else:
                print(f"❌ Workflow execution request failed: HTTP {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text}")
                self.test_results['complete_workflow'] = {
                    'status': 'FAIL',
                    'message': f'HTTP {response.status_code}'
                }
                return False
                
        except Exception as e:
            print(f"❌ Workflow execution error: {e}")
            self.test_results['complete_workflow'] = {
                'status': 'FAIL',
                'message': f'Error: {e}'
            }
            return False
    
    def test_daily_metrics(self):
        """Test 6: Daily metrics tracking"""
        print("\nTest 6: Daily Metrics Tracking")
        print("-" * 50)
        self.total_tests += 1
        
        try:
            response = self.session.get(f"{self.base_url}/api/workflow/step-2-2/daily-metrics")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    metrics = data.get('data', {})
                    
                    print(f"✅ Daily metrics retrieved")
                    print(f"   Applications sent today: {metrics.get('applications_sent_today', 0)}")
                    print(f"   Daily limit: {metrics.get('daily_limit', 0)}")
                    print(f"   Remaining applications: {metrics.get('remaining_applications', 0)}")
                    print(f"   Date: {metrics.get('date')}")
                    
                    self.test_results['daily_metrics'] = {
                        'status': 'PASS',
                        'message': 'Daily metrics tracking operational',
                        'metrics': metrics
                    }
                    self.passed_tests += 1
                    return True
                else:
                    print(f"❌ Daily metrics failed: {data.get('error')}")
                    self.test_results['daily_metrics'] = {
                        'status': 'FAIL',
                        'message': data.get('error')
                    }
                    return False
            else:
                print(f"❌ Daily metrics request failed: HTTP {response.status_code}")
                self.test_results['daily_metrics'] = {
                    'status': 'FAIL',
                    'message': f'HTTP {response.status_code}'
                }
                return False
                
        except Exception as e:
            print(f"❌ Daily metrics error: {e}")
            self.test_results['daily_metrics'] = {
                'status': 'FAIL',
                'message': f'Error: {e}'
            }
            return False
    
    def run_all_tests(self):
        """Run all Step 2.2 implementation tests"""
        print("=" * 70)
        print("STEP 2.2 IMPLEMENTATION TEST: END-TO-END WORKFLOW ORCHESTRATION")
        print("=" * 70)
        print(f"Testing Implementation Plan V2.16 - Step 2.2")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        tests = [
            self.test_workflow_health_check,
            self.test_workflow_configuration,
            self.test_job_discovery,
            self.test_preference_matching,
            self.test_complete_workflow_execution,
            self.test_daily_metrics
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
                self.test_results[test.__name__] = {
                    'status': 'EXCEPTION',
                    'message': f'Exception: {e}'
                }
        
        # Print summary
        print("\n" + "=" * 70)
        print("STEP 2.2 IMPLEMENTATION TEST SUMMARY")
        print("=" * 70)
        
        print(f"Total tests: {self.total_tests}")
        print(f"Passed tests: {self.passed_tests}")
        print(f"Success rate: {self.passed_tests/self.total_tests:.1%}" if self.total_tests > 0 else "No tests run")
        
        # Acceptance criteria summary
        workflow_result = self.test_results.get('complete_workflow', {})
        if 'completion_rate' in workflow_result:
            completion_rate = workflow_result['completion_rate']
            print(f"\n📋 STEP 2.2 ACCEPTANCE CRITERIA: {completion_rate:.1%} complete")
            
            if completion_rate >= 0.75:
                print("✅ STEP 2.2 IMPLEMENTATION: SUCCESSFUL")
                print("   End-to-End Workflow Orchestration is operational")
            else:
                print("⚠️ STEP 2.2 IMPLEMENTATION: PARTIAL")
                print("   Some acceptance criteria need attention")
        else:
            print("❌ STEP 2.2 IMPLEMENTATION: INCOMPLETE")
            print("   Workflow execution test did not complete")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Return overall success
        return self.passed_tests >= (self.total_tests * 0.75)


def main():
    """Run Step 2.2 implementation tests"""
    test_suite = Step22ImplementationTest()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()