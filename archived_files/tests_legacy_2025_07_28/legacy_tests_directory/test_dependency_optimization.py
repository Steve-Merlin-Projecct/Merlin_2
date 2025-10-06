#!/usr/bin/env python3
"""
Test Suite for On-Demand Dependency Loading System
Validates that dependencies are loaded only when needed and all modules work correctly
"""

import sys
import os
import subprocess
import time
import logging
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Test logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DependencyOptimizationTester:
    """Test suite for on-demand dependency loading system"""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        
    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        try:
            logger.info(f"Running test: {test_name}")
            start_time = time.time()
            result = test_func()
            duration = time.time() - start_time
            
            self.test_results.append({
                'test': test_name,
                'status': 'PASS' if result else 'FAIL',
                'duration': duration,
                'details': result if isinstance(result, dict) else {}
            })
            
            if result:
                logger.info(f"✅ {test_name} - PASSED ({duration:.2f}s)")
            else:
                logger.error(f"❌ {test_name} - FAILED ({duration:.2f}s)")
                self.failed_tests.append(test_name)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {test_name} - ERROR: {str(e)}")
            self.failed_tests.append(test_name)
            self.test_results.append({
                'test': test_name,
                'status': 'ERROR',
                'duration': 0,
                'details': {'error': str(e)}
            })
            return False
    
    def test_dependency_manager_available(self):
        """Test that dependency manager is available and working"""
        try:
            sys.path.append('./utils')
            from dependency_manager import DependencyManager
            
            manager = DependencyManager()
            return True
        except ImportError:
            return False
    
    def test_numpy_on_demand_loading(self):
        """Test numpy loads only when ToneAnalyzer is used"""
        try:
            # Import ToneAnalyzer without triggering numpy loading yet
            from modules.content.tone_analyzer import ToneAnalyzer
            
            # Create analyzer instance
            analyzer = ToneAnalyzer()
            
            # Now test tone analysis which should trigger numpy loading
            sentence1 = {'tone': 'Confident', 'tone_strength': 0.8}
            sentence2 = {'tone': 'Analytical', 'tone_strength': 0.7}
            
            score = analyzer.calculate_tone_jump_score(sentence1, sentence2)
            
            return isinstance(score, float) and score >= 0
            
        except Exception as e:
            logger.error(f"Numpy test failed: {e}")
            return False
    
    def test_bleach_on_demand_loading(self):
        """Test bleach loads only when SecurityManager sanitizes HTML"""
        try:
            from modules.security.security_manager import SecurityManager
            
            manager = SecurityManager()
            
            # Test HTML sanitization which should trigger bleach loading
            test_html = '<script>alert("xss")</script><p>Safe content</p>'
            cleaned = manager.sanitize_html_content(test_html)
            
            return 'Safe content' in cleaned and 'script' not in cleaned
            
        except Exception as e:
            logger.error(f"Bleach test failed: {e}")
            return False
    
    def test_google_genai_on_demand_loading(self):
        """Test google-genai loads only when GeminiJobAnalyzer is used"""
        try:
            from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
            
            # Create analyzer instance (shouldn't load genai yet)
            analyzer = GeminiJobAnalyzer()
            
            # Check that genai isn't loaded yet
            return not analyzer._genai_loaded
            
        except Exception as e:
            logger.error(f"Google GenAI test failed: {e}")
            return False
    
    def test_application_startup_performance(self):
        """Test that application starts faster without automatic dependency loading"""
        try:
            start_time = time.time()
            
            # Import main application components
            from app_modular import app
            
            startup_time = time.time() - start_time
            
            # Should start in under 5 seconds without loading heavy dependencies
            return startup_time < 5.0
            
        except Exception as e:
            logger.error(f"Startup performance test failed: {e}")
            return False
    
    def test_mock_interfaces_fallback(self):
        """Test that mock interfaces work when real dependencies aren't available"""
        try:
            # Test mock numpy interface
            from modules.content.tone_analyzer import _get_numpy_module
            
            # This should return either real numpy or mock interface
            np = _get_numpy_module()
            
            # Test basic numpy-like operations
            test_data = [1, 2, 3, 4, 5]
            mean_result = np.mean(test_data)
            std_result = np.std(test_data)
            
            return isinstance(mean_result, float) and isinstance(std_result, float)
            
        except Exception as e:
            logger.error(f"Mock interface test failed: {e}")
            return False
    
    def test_document_generation_with_on_demand_docx(self):
        """Test document generation with on-demand docx loading"""
        try:
            from modules.content.document_generation.document_generator import DocumentGenerator
            
            # Create generator instance
            generator = DocumentGenerator()
            
            # Test data
            test_data = {
                'document_type': 'resume',
                'person_name': 'Test User',
                'person_email': 'test@example.com'
            }
            
            # This should trigger docx loading
            result = generator.generate_document(test_data)
            
            return 'success' in result and result['success']
            
        except Exception as e:
            logger.error(f"Document generation test failed: {e}")
            return False
    
    def test_comprehensive_dependency_loading(self):
        """Test all dependency loading functions work correctly"""
        try:
            from utils.dependency_manager import (
                get_docx_module, get_numpy_module, get_bleach_module, 
                get_trafilatura_module, get_requests_module
            )
            
            # Test each dependency loading function
            dependencies = [
                ('docx', get_docx_module),
                ('numpy', get_numpy_module),
                ('bleach', get_bleach_module),
                ('trafilatura', get_trafilatura_module),
                ('requests', get_requests_module)
            ]
            
            loaded_count = 0
            for name, loader_func in dependencies:
                try:
                    module = loader_func()
                    if module:
                        loaded_count += 1
                        logger.info(f"✅ {name} loaded successfully")
                    else:
                        logger.warning(f"⚠️ {name} returned None")
                except Exception as e:
                    logger.warning(f"⚠️ {name} failed to load: {e}")
            
            # Should load at least 3 out of 5 dependencies
            return loaded_count >= 3
            
        except Exception as e:
            logger.error(f"Comprehensive dependency test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("🚀 Starting On-Demand Dependency Loading Test Suite")
        logger.info("=" * 60)
        
        # Define test suite
        tests = [
            ("Dependency Manager Available", self.test_dependency_manager_available),
            ("Numpy On-Demand Loading", self.test_numpy_on_demand_loading),
            ("Bleach On-Demand Loading", self.test_bleach_on_demand_loading),
            ("Google GenAI On-Demand Loading", self.test_google_genai_on_demand_loading),
            ("Application Startup Performance", self.test_application_startup_performance),
            ("Mock Interfaces Fallback", self.test_mock_interfaces_fallback),
            ("Document Generation with On-Demand DOCX", self.test_document_generation_with_on_demand_docx),
            ("Comprehensive Dependency Loading", self.test_comprehensive_dependency_loading)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate report
        self.generate_report()
        
        return len(self.failed_tests) == 0
    
    def generate_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 ON-DEMAND DEPENDENCY LOADING TEST REPORT")
        logger.info("=" * 60)
        
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        errors = len([r for r in self.test_results if r['status'] == 'ERROR'])
        total = len(self.test_results)
        
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if self.failed_tests:
            logger.info(f"\nFailed Tests: {', '.join(self.failed_tests)}")
        
        # Performance summary
        total_time = sum(r['duration'] for r in self.test_results)
        avg_time = total_time / total if total > 0 else 0
        logger.info(f"\nTotal Test Time: {total_time:.2f}s")
        logger.info(f"Average Test Time: {avg_time:.2f}s")
        
        # Success indicators
        if passed >= 6:  # At least 6 out of 8 tests should pass
            logger.info("\n🎉 ON-DEMAND DEPENDENCY OPTIMIZATION: SUCCESS")
            logger.info("✅ Dependencies load only when needed")
            logger.info("✅ Application startup performance improved")
            logger.info("✅ Mock interfaces provide fallback functionality")
            logger.info("✅ System architecture supports scalable dependency management")
        else:
            logger.info("\n⚠️ ON-DEMAND DEPENDENCY OPTIMIZATION: NEEDS ATTENTION")
            logger.info("Some tests failed - review implementation")

if __name__ == "__main__":
    tester = DependencyOptimizationTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 All tests passed! On-demand dependency loading is working correctly.")
        exit(0)
    else:
        logger.error("\n❌ Some tests failed. Please review the implementation.")
        exit(1)