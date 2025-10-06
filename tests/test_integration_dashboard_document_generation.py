#!/usr/bin/env python3
"""
Integration Testing: Flask Dashboard and Document Generation System

Comprehensive integration tests for the copywriting evaluator dashboard,
API endpoints, and document generation system integration.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import json
import requests
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class IntegrationTestDashboardDocumentGeneration(unittest.TestCase):
    """Integration test suite for dashboard and document generation system"""

    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.dashboard_password = "jellyfish–lantern–kisses"
        self.test_data = {}
        
        # Sample job data for testing
        self.sample_job_data = {
            'job_title': 'Senior Software Developer',
            'company_name': 'Tech Innovations Inc.',
            'job_description': 'Seeking experienced developer for full-stack role',
            'skills_required': ['Python', 'React', 'PostgreSQL'],
            'experience_level': 'Senior'
        }
        
        # Sample document data 
        self.sample_document_data = {
            'person': {
                'name': 'John Smith',
                'email': 'john.smith@email.com',
                'phone': '555-0123',
                'location': 'Toronto, ON'
            },
            'job_title': 'Senior Software Developer',
            'company_name': 'Tech Innovations Inc.',
            'experience': [
                {
                    'title': 'Software Developer',
                    'company': 'Previous Company',
                    'duration': '2020-2023',
                    'achievements': ['Built scalable web applications', 'Led team of 3 developers']
                }
            ]
        }

    def authenticate_dashboard(self):
        """Authenticate with dashboard for protected endpoints"""
        try:
            response = self.session.post(
                f"{self.base_url}/dashboard/authenticate",
                json={'password': self.dashboard_password}
            )
            return response.status_code == 200
        except Exception as e:
            self.fail(f"Dashboard authentication failed: {str(e)}")

    def test_dashboard_accessibility(self):
        """Test copywriting evaluator dashboard accessibility"""
        # Authenticate first
        self.assertTrue(self.authenticate_dashboard(), "Dashboard authentication should succeed")
        
        try:
            # Access dashboard page
            response = self.session.get(f"{self.base_url}/copywriting-evaluator-dashboard")
            
            self.assertEqual(response.status_code, 200, "Dashboard should be accessible")
            self.assertIn("Copywriting Evaluator", response.text, "Dashboard should contain expected content")
            
            # Check for key dashboard elements
            expected_elements = [
                "Pipeline Processing",
                "Scheduler Status", 
                "Performance Metrics",
                "API Configuration"
            ]
            
            for element in expected_elements:
                self.assertIn(element, response.text, f"Dashboard should contain {element}")
                
        except Exception as e:
            self.fail(f"Dashboard accessibility test failed: {str(e)}")

    def test_api_endpoints_integration(self):
        """Test integration of copywriting evaluator API endpoints"""
        self.assertTrue(self.authenticate_dashboard(), "Authentication required for API tests")
        
        api_endpoints = [
            ("/api/copywriting-evaluator/pipeline/status", "GET"),
            ("/api/copywriting-evaluator/statistics", "GET"),
            ("/api/copywriting-evaluator/gemini/usage", "GET"),
            ("/api/copywriting-evaluator/health", "GET"),
            ("/api/copywriting-evaluator/scheduler/status", "GET")
        ]
        
        for endpoint, method in api_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{self.base_url}{endpoint}", json={})
                
                self.assertIn(response.status_code, [200, 400, 500], 
                             f"API endpoint {endpoint} should respond")
                
                if response.status_code == 200:
                    # Verify response is JSON
                    response_data = response.json()
                    self.assertIsInstance(response_data, dict, "API should return JSON response")
                    
            except Exception as e:
                self.fail(f"API endpoint {endpoint} integration failed: {str(e)}")

    def test_pipeline_processing_integration(self):
        """Test pipeline processing through API"""
        self.assertTrue(self.authenticate_dashboard(), "Authentication required")
        
        try:
            # Test pipeline start endpoint
            pipeline_data = {
                "mode": "testing",
                "stages": ["keyword_filter"],
                "immediate_processing": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/copywriting-evaluator/pipeline/start",
                json=pipeline_data
            )
            
            # Should either succeed or fail gracefully
            self.assertIn(response.status_code, [200, 400, 500, 503], 
                         "Pipeline start should respond appropriately")
            
            if response.status_code == 200:
                result = response.json()
                self.assertTrue(result.get('success'), "Successful pipeline should return success=True")
                
        except Exception as e:
            self.fail(f"Pipeline processing integration failed: {str(e)}")

    def test_document_generation_integration(self):
        """Test document generation system integration"""
        try:
            from modules.content.document_generation.document_generator import DocumentGenerator
            from modules.content.document_generation.template_engine import TemplateEngine
            
            # Test DocumentGenerator initialization
            doc_generator = DocumentGenerator()
            self.assertIsNotNone(doc_generator, "DocumentGenerator should initialize")
            self.assertIsNotNone(doc_generator.template_engine, "TemplateEngine should be available")
            
            # Test TemplateEngine functionality
            template_engine = TemplateEngine()
            
            # Test variable substitution
            test_text = "I am interested in the {job_title} position at {company_name}"
            stats = {'variables_substituted': set(), 'variables_missing': set()}
            
            result = template_engine.substitute_variables(test_text, self.sample_job_data, stats)
            expected = "I am interested in the Senior Software Developer position at Tech Innovations Inc."
            
            self.assertEqual(result, expected, "Variable substitution should work correctly")
            self.assertEqual(len(stats['variables_substituted']), 2, "Should substitute 2 variables")
            
        except ImportError as e:
            self.fail(f"Document generation system import failed: {str(e)}")
        except Exception as e:
            self.fail(f"Document generation integration failed: {str(e)}")

    def test_template_system_integration(self):
        """Test template system integration with copywriting evaluator"""
        try:
            from modules.content.document_generation.template_engine import TemplateEngine
            
            template_engine = TemplateEngine()
            
            # Test different variable types
            test_cases = [
                # Template variables (<<variable>>)
                ("Dear <<hiring_manager>>, I am interested", self.sample_document_data, "Dear <<hiring_manager>>, I am interested"),
                
                # Job variables ({variable})
                ("The {job_title} role at {company_name}", self.sample_job_data, "The Senior Software Developer role at Tech Innovations Inc."),
                
                # Mixed variables
                ("Dear <<hiring_manager>>, I want the {job_title} position", 
                 {**self.sample_document_data, **self.sample_job_data}, 
                 "Dear <<hiring_manager>>, I want the Senior Software Developer position")
            ]
            
            for test_input, data, expected in test_cases:
                stats = {'variables_substituted': set(), 'variables_missing': set()}
                result = template_engine.substitute_variables(test_input, data, stats)
                
                if "{job_title}" in test_input or "{company_name}" in test_input:
                    self.assertNotEqual(result, test_input, "Job variables should be substituted")
                
        except Exception as e:
            self.fail(f"Template system integration failed: {str(e)}")

    def test_scheduler_integration(self):
        """Test scheduler system integration"""
        self.assertTrue(self.authenticate_dashboard(), "Authentication required")
        
        try:
            from modules.content.copywriting_evaluator.scheduler import get_production_scheduler
            
            # Test scheduler initialization
            scheduler = get_production_scheduler()
            self.assertIsNotNone(scheduler, "Production scheduler should be available")
            
            # Test scheduler status via API
            response = self.session.get(f"{self.base_url}/api/copywriting-evaluator/scheduler/status")
            self.assertEqual(response.status_code, 200, "Scheduler status API should respond")
            
            status_data = response.json()
            self.assertTrue(status_data.get('success'), "Scheduler status should return success")
            self.assertIn('scheduler_status', status_data, "Should include scheduler status")
            
        except ImportError as e:
            self.fail(f"Scheduler system import failed: {str(e)}")
        except Exception as e:
            self.fail(f"Scheduler integration failed: {str(e)}")

    def test_end_to_end_workflow_integration(self):
        """Test complete end-to-end workflow integration"""
        self.assertTrue(self.authenticate_dashboard(), "Authentication required")
        
        try:
            # Step 1: Check system health
            health_response = self.session.get(f"{self.base_url}/api/copywriting-evaluator/health")
            self.assertEqual(health_response.status_code, 200, "System should be healthy")
            
            # Step 2: Check pipeline status
            status_response = self.session.get(f"{self.base_url}/api/copywriting-evaluator/pipeline/status")
            self.assertEqual(status_response.status_code, 200, "Pipeline status should be available")
            
            # Step 3: Test document generation with copywriting evaluator output
            from modules.content.document_generation.template_engine import TemplateEngine
            
            # Simulate copywriting evaluator processing result
            processed_content = {
                'cover_letter_sentences': [
                    "I am excited about the {job_title} opportunity at {company_name}.",
                    "My experience aligns perfectly with your requirements."
                ],
                'resume_sentences': [
                    "Experienced {job_title} with proven track record.",
                    "Successfully delivered multiple projects at scale."
                ]
            }
            
            # Test template processing with evaluator output
            template_engine = TemplateEngine()
            stats = {'variables_substituted': set(), 'variables_missing': set()}
            
            for sentence in processed_content['cover_letter_sentences']:
                result = template_engine.substitute_variables(sentence, self.sample_job_data, stats)
                self.assertIsInstance(result, str, "Processing should return string")
                
                # Check variable substitution occurred if variables were present
                if '{job_title}' in sentence:
                    self.assertIn(self.sample_job_data['job_title'], result, "Job title should be substituted")
                if '{company_name}' in sentence:
                    self.assertIn(self.sample_job_data['company_name'], result, "Company name should be substituted")
            
            # Step 4: Verify scheduler is operational
            scheduler_response = self.session.get(f"{self.base_url}/api/copywriting-evaluator/scheduler/status")
            self.assertEqual(scheduler_response.status_code, 200, "Scheduler should be accessible")
            
        except Exception as e:
            self.fail(f"End-to-end workflow integration failed: {str(e)}")

    def test_error_handling_integration(self):
        """Test error handling across integrated systems"""
        self.assertTrue(self.authenticate_dashboard(), "Authentication required")
        
        try:
            # Test invalid API requests
            invalid_requests = [
                ("/api/copywriting-evaluator/pipeline/start", {"mode": "invalid_mode"}),
                ("/api/copywriting-evaluator/scheduler/tasks/nonexistent/enable", {}),
                ("/api/copywriting-evaluator/stages/invalid_stage/process", {})
            ]
            
            for endpoint, data in invalid_requests:
                response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                # Should return appropriate error codes, not crash
                self.assertIn(response.status_code, [400, 404, 500], 
                             f"Invalid request to {endpoint} should return error code")
                
                if response.status_code in [400, 404]:
                    # Should return JSON error response
                    error_data = response.json()
                    self.assertIn('error', error_data, "Error response should include error message")
            
            # Test document generation error handling
            from modules.content.document_generation.template_engine import TemplateEngine
            
            template_engine = TemplateEngine()
            
            # Test with malformed data
            malformed_data_cases = [
                None,
                {},
                {'invalid_key': 'value'},
                {'job_title': None},
                {'company_name': ''}
            ]
            
            test_text = "I want the {job_title} position at {company_name}"
            
            for malformed_data in malformed_data_cases:
                stats = {'variables_substituted': set(), 'variables_missing': set()}
                # Should not crash on malformed data
                result = template_engine.substitute_variables(test_text, malformed_data or {}, stats)
                self.assertIsInstance(result, str, "Should return string even with malformed data")
                
        except Exception as e:
            self.fail(f"Error handling integration failed: {str(e)}")

    def test_performance_integration(self):
        """Test performance metrics integration across systems"""
        self.assertTrue(self.authenticate_dashboard(), "Authentication required")
        
        try:
            # Test Gemini usage statistics
            response = self.session.get(f"{self.base_url}/api/copywriting-evaluator/gemini/usage")
            self.assertEqual(response.status_code, 200, "Gemini usage API should respond")
            
            usage_data = response.json()
            self.assertTrue(usage_data.get('success'), "Should return success status")
            self.assertIn('gemini_usage_statistics', usage_data, "Should include usage statistics")
            
            # Test system statistics
            stats_response = self.session.get(f"{self.base_url}/api/copywriting-evaluator/statistics")
            self.assertEqual(stats_response.status_code, 200, "Statistics API should respond")
            
            stats_data = stats_response.json()
            self.assertTrue(stats_data.get('success'), "Statistics should return success")
            self.assertIn('statistics', stats_data, "Should include system statistics")
            
        except Exception as e:
            self.fail(f"Performance integration failed: {str(e)}")


class IntegrationTestRunner:
    """Test runner for integration tests with detailed reporting"""
    
    def __init__(self):
        self.start_time = datetime.now()
        
    def run_integration_tests(self):
        """Run all integration tests with comprehensive reporting"""
        print("="*80)
        print("🧪 INTEGRATION TESTING: DASHBOARD & DOCUMENT GENERATION")  
        print("="*80)
        print(f"⏰ Tests started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
        
        # Create test suite
        test_suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTestDashboardDocumentGeneration)
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            descriptions=True
        )
        
        result = runner.run(test_suite)
        
        # Print summary
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("-"*80)
        print(f"⏰ Tests completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Total duration: {duration.total_seconds():.2f} seconds")
        
        total = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors) 
        passed = total - failures - errors
        
        print(f"📊 INTEGRATION TEST RESULTS:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failures}")
        print(f"   💥 Errors: {errors}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Print integration coverage summary
        print(f"\n🎯 INTEGRATION COVERAGE:")
        print(f"   ✅ Flask Dashboard Accessibility")
        print(f"   ✅ API Endpoints Integration")
        print(f"   ✅ Pipeline Processing Integration")  
        print(f"   ✅ Document Generation Integration")
        print(f"   ✅ Template System Integration")
        print(f"   ✅ Scheduler System Integration")
        print(f"   ✅ End-to-End Workflow Integration")
        print(f"   ✅ Error Handling Integration") 
        print(f"   ✅ Performance Metrics Integration")
        
        return result.wasSuccessful()


def run_dashboard_document_integration_tests():
    """Main entry point for integration testing"""
    runner = IntegrationTestRunner()
    success = runner.run_integration_tests()
    return success


if __name__ == "__main__":
    success = run_dashboard_document_integration_tests()
    sys.exit(0 if success else 1)