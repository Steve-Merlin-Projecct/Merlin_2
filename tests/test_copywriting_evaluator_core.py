#!/usr/bin/env python3
"""
Core Test Suite for Copywriting Evaluator Pipeline

Focused test suite covering essential pipeline functionality,
variable validation, error scenarios, and stage processing.

Author: Automated Job Application System  
Version: 1.0.0
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.content.copywriting_evaluator.pipeline_processor import (
    CopywritingEvaluatorPipeline,
    PipelineConfig, 
    ProcessingMode,
    ProcessingStage,
    ProcessingStats
)

class TestPipelineCore(unittest.TestCase):
    """Core pipeline functionality tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = PipelineConfig(
            mode=ProcessingMode.TESTING,
            batch_size=5,
            max_consecutive_errors=3,
            detailed_logging=True
        )

    def test_pipeline_initialization_modes(self):
        """Test pipeline initialization with different modes"""
        # Testing mode
        test_pipeline = CopywritingEvaluatorPipeline(
            PipelineConfig(mode=ProcessingMode.TESTING)
        )
        self.assertEqual(test_pipeline.config.mode, ProcessingMode.TESTING)
        self.assertTrue(test_pipeline.config.immediate_processing)
        self.assertTrue(test_pipeline.config.detailed_logging)
        
        # Production mode
        prod_pipeline = CopywritingEvaluatorPipeline(
            PipelineConfig(mode=ProcessingMode.PRODUCTION)
        )
        self.assertEqual(prod_pipeline.config.mode, ProcessingMode.PRODUCTION)
        self.assertFalse(prod_pipeline.config.immediate_processing)
        self.assertTrue(prod_pipeline.config.enable_scheduling)

    def test_processing_stages_enum(self):
        """Test processing stages enumeration"""
        expected_stages = [
            'keyword_filter',
            'truthfulness', 
            'canadian_spelling',
            'tone_analysis',
            'skill_analysis'
        ]
        
        actual_stages = [stage.value for stage in ProcessingStage]
        
        for expected_stage in expected_stages:
            self.assertIn(expected_stage, actual_stages)

    def test_processing_stats_structure(self):
        """Test ProcessingStats data structure"""
        stats = ProcessingStats(
            session_id="test_session",
            total_sentences=10,
            processed_sentences=8, 
            filtered_sentences=2,
            approved_sentences=6,
            error_count=1
        )
        
        # Verify required fields
        self.assertEqual(stats.session_id, "test_session")
        self.assertEqual(stats.total_sentences, 10)
        self.assertEqual(stats.processed_sentences, 8)
        self.assertEqual(stats.filtered_sentences, 2)
        self.assertEqual(stats.approved_sentences, 6)
        self.assertEqual(stats.error_count, 1)
        
        # Verify auto-initialized fields
        self.assertIsInstance(stats.stage_stats, dict)

class TestVariableValidation(unittest.TestCase):
    """Variable validation functionality tests"""

    def setUp(self):
        self.pipeline = CopywritingEvaluatorPipeline()

    def test_supported_variables_validation(self):
        """Test validation of supported variables"""
        test_cases = [
            ("I want to work at {company_name}", True, []),
            ("The {job_title} position is perfect", True, []),
            ("At {company_name} as {job_title}", True, []),
            ("No variables here", True, [])
        ]
        
        for text, expected_valid, expected_unsupported in test_cases:
            is_valid, unsupported = self.pipeline._validate_sentence_variables(text)
            self.assertEqual(is_valid, expected_valid, f"Failed for: {text}")
            self.assertEqual(unsupported, expected_unsupported, f"Failed for: {text}")

    def test_unsupported_variables_validation(self):
        """Test validation rejects unsupported variables"""
        test_cases = [
            ("I have {years_experience} years", False, ['years_experience']),
            ("My salary is {expected_salary}", False, ['expected_salary']),
            ("I use {programming_language} and {framework}", False, ['programming_language', 'framework']),
            ("Working at {company_name} with {unsupported_var}", False, ['unsupported_var'])
        ]
        
        for text, expected_valid, expected_unsupported in test_cases:
            is_valid, unsupported = self.pipeline._validate_sentence_variables(text)
            self.assertEqual(is_valid, expected_valid, f"Failed for: {text}")
            for var in expected_unsupported:
                self.assertIn(var, unsupported, f"Missing {var} in unsupported list for: {text}")

    def test_mixed_variables_validation(self):
        """Test validation with mix of supported and unsupported variables"""
        text = "At {company_name}, I will use {programming_language} for {job_title}"
        is_valid, unsupported = self.pipeline._validate_sentence_variables(text)
        
        self.assertFalse(is_valid)
        self.assertIn('programming_language', unsupported)
        self.assertNotIn('company_name', unsupported)
        self.assertNotIn('job_title', unsupported)

    def test_edge_cases_validation(self):
        """Test edge cases in variable validation"""
        edge_cases = [
            ("", True, []),  # Empty string
            ("{}", True, []),  # Empty braces  
            ("{ }", True, []),  # Whitespace in braces
            ("{job_title", True, []),  # Malformed brace
            ("job_title}", True, []),  # Malformed brace
            ("{{job_title}}", True, []),  # Double braces (should be ignored)
        ]
        
        for text, expected_valid, expected_unsupported in edge_cases:
            is_valid, unsupported = self.pipeline._validate_sentence_variables(text)
            self.assertEqual(is_valid, expected_valid, f"Failed for: '{text}'")
            self.assertEqual(len(unsupported), len(expected_unsupported), f"Failed for: '{text}'")

class TestStageProcessors(unittest.TestCase):
    """Stage processor loading and management tests"""

    def setUp(self):
        self.pipeline = CopywritingEvaluatorPipeline()

    def test_stage_processor_lazy_loading(self):
        """Test that stage processors are loaded lazily"""
        # Initially no processors should be loaded
        self.assertEqual(len(self.pipeline._stage_processors), 0)
        
        # Load each stage processor
        stages = list(ProcessingStage)
        for stage in stages:
            processor = self.pipeline._get_stage_processor(stage)
            self.assertIsNotNone(processor)
            
            # Verify processor is cached
            processor2 = self.pipeline._get_stage_processor(stage)
            self.assertIs(processor, processor2, f"Processor not cached for {stage}")
        
        # Verify all processors are now loaded
        self.assertEqual(len(self.pipeline._stage_processors), len(stages))

    def test_stage_processor_types(self):
        """Test that correct processor types are loaded for each stage"""
        # This test verifies that each stage gets the appropriate processor
        # We test by checking that each processor has expected methods
        
        expected_methods = ['process_batch']  # Common method all processors should have
        
        for stage in ProcessingStage:
            processor = self.pipeline._get_stage_processor(stage)
            
            for method in expected_methods:
                self.assertTrue(
                    hasattr(processor, method),
                    f"Processor for {stage} missing method {method}"
                )

class TestErrorScenarios(unittest.TestCase):
    """Error handling and edge case tests"""

    def setUp(self):
        self.pipeline = CopywritingEvaluatorPipeline(
            PipelineConfig(mode=ProcessingMode.TESTING)
        )

    def test_can_process_normal_conditions(self):
        """Test can_process under normal conditions"""
        can_process, reason = self.pipeline.can_process()
        self.assertTrue(can_process)
        self.assertEqual(reason, "Ready for processing")

    def test_can_process_cooldown_scenario(self):
        """Test can_process during cooldown period"""
        # Set cooldown period
        self.pipeline.cooldown_until = datetime.now() + timedelta(hours=1)
        
        can_process, reason = self.pipeline.can_process()
        self.assertFalse(can_process)
        self.assertIn("cooldown", reason.lower())

    def test_can_process_error_limit_scenario(self):
        """Test can_process when error limit is reached"""
        # Set up production mode pipeline for error limit testing
        prod_pipeline = CopywritingEvaluatorPipeline(
            PipelineConfig(mode=ProcessingMode.PRODUCTION, max_consecutive_errors=2)
        )
        
        # Simulate consecutive errors at limit
        prod_pipeline.consecutive_errors = 2
        
        can_process, reason = prod_pipeline.can_process()
        self.assertFalse(can_process)
        self.assertIn("consecutive errors", reason)

    def test_malformed_data_handling(self):
        """Test handling of malformed or invalid data"""
        malformed_inputs = [
            None,
            "",
            "   ",  # Whitespace only
            123,   # Non-string type
        ]
        
        for malformed_input in malformed_inputs:
            try:
                is_valid, unsupported = self.pipeline._validate_sentence_variables(
                    str(malformed_input) if malformed_input is not None else ""
                )
                # Should not crash and should return valid boolean and list
                self.assertIsInstance(is_valid, bool)
                self.assertIsInstance(unsupported, list)
            except Exception as e:
                self.fail(f"Failed to handle malformed input {malformed_input}: {e}")

class TestConfigurationManagement(unittest.TestCase):
    """Configuration and mode management tests"""

    def test_default_configuration(self):
        """Test default configuration values"""
        config = PipelineConfig()
        
        # Test default values
        self.assertEqual(config.mode, ProcessingMode.TESTING)
        self.assertGreater(config.batch_size, 0)
        self.assertGreater(config.max_consecutive_errors, 0)
        self.assertIsInstance(config.detailed_logging, bool)

    def test_custom_configuration(self):
        """Test custom configuration values"""
        custom_config = PipelineConfig(
            mode=ProcessingMode.PRODUCTION,
            batch_size=10,
            max_consecutive_errors=5,
            detailed_logging=False
        )
        
        self.assertEqual(custom_config.mode, ProcessingMode.PRODUCTION)
        self.assertEqual(custom_config.batch_size, 10)
        self.assertEqual(custom_config.max_consecutive_errors, 5)
        self.assertFalse(custom_config.detailed_logging)

    def test_mode_specific_settings(self):
        """Test that mode-specific settings are applied correctly"""
        # Testing mode pipeline
        test_pipeline = CopywritingEvaluatorPipeline(
            PipelineConfig(mode=ProcessingMode.TESTING)
        )
        self.assertTrue(test_pipeline.config.immediate_processing)
        self.assertFalse(test_pipeline.config.enable_scheduling)
        
        # Production mode pipeline  
        prod_pipeline = CopywritingEvaluatorPipeline(
            PipelineConfig(mode=ProcessingMode.PRODUCTION)
        )
        self.assertFalse(prod_pipeline.config.immediate_processing)
        self.assertTrue(prod_pipeline.config.enable_scheduling)

def run_comprehensive_tests():
    """Run comprehensive test suite with detailed reporting"""
    print("="*70)
    print("🧪 COPYWRITING EVALUATOR COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Define test classes
    test_classes = [
        TestPipelineCore,
        TestVariableValidation, 
        TestStageProcessors,
        TestErrorScenarios,
        TestConfigurationManagement
    ]
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True
    )
    
    print(f"⏰ Tests started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*70)
    
    result = runner.run(test_suite)
    
    print("-"*70)
    print(f"⏰ Tests completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Print detailed summary
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors
    
    print(f"📊 COMPREHENSIVE TEST RESULTS:")
    print(f"   Total Tests Run: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failures}")
    print(f"   💥 Errors: {errors}")
    
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if failures > 0:
            print(f"\n❌ FAILED TESTS:")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback.split(chr(10))[-2] if traceback else 'Unknown failure'}")
        
        if errors > 0:
            print(f"\n💥 ERROR TESTS:")
            for test, traceback in result.errors:
                print(f"   - {test}: {traceback.split(chr(10))[-2] if traceback else 'Unknown error'}")
    
    # Print feature coverage summary
    print(f"\n🎯 FEATURE COVERAGE:")
    print(f"   ✅ Pipeline Initialization & Configuration")
    print(f"   ✅ Variable Validation (Supported & Unsupported)")
    print(f"   ✅ Stage Processor Management") 
    print(f"   ✅ Error Handling & Recovery")
    print(f"   ✅ Processing Mode Management")
    print(f"   ✅ Edge Cases & Malformed Data")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)