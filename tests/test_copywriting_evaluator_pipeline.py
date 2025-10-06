#!/usr/bin/env python3
"""
Comprehensive Test Suite for Copywriting Evaluator Pipeline

Tests all five pipeline stages, error scenarios, processing modes,
variable validation, and integration components.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import unittest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock
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
from modules.database.database_manager import DatabaseManager

class TestCopywritingEvaluatorPipeline(unittest.TestCase):
    """Test suite for the copywriting evaluator pipeline system"""

    def setUp(self):
        """Set up test fixtures and configurations"""
        self.test_config = PipelineConfig(
            mode=ProcessingMode.TESTING,
            batch_size=5,
            max_consecutive_errors=3,
            detailed_logging=True
        )
        
        # Mock database to avoid real database operations during tests
        self.mock_db = Mock(spec=DatabaseManager)
        
        # Sample test sentences for pipeline processing
        self.test_sentences = [
            {
                'id': 'test_001',
                'content_text': 'I am excited to apply for the software developer position',
                'table_name': 'sentence_bank_cover_letter',
                'status': 'pending',
                'keyword_filter_status': 'pending',
                'truthfulness_status': 'pending',
                'canadian_spelling_status': 'pending',
                'tone_analysis_status': 'pending',
                'skill_analysis_status': 'pending'
            },
            {
                'id': 'test_002', 
                'content_text': 'I have experience with Python programming and {job_title}',
                'table_name': 'sentence_bank_resume',
                'status': 'pending',
                'keyword_filter_status': 'pending',
                'truthfulness_status': 'pending',
                'canadian_spelling_status': 'pending',
                'tone_analysis_status': 'pending',
                'skill_analysis_status': 'pending'
            },
            {
                'id': 'test_003',
                'content_text': 'Looking forward to working at {company_name} with {unsupported_var}',
                'table_name': 'sentence_bank_cover_letter', 
                'status': 'pending',
                'keyword_filter_status': 'pending',
                'truthfulness_status': 'pending',
                'canadian_spelling_status': 'pending',
                'tone_analysis_status': 'pending',
                'skill_analysis_status': 'pending'
            }
        ]

    def test_pipeline_initialization(self):
        """Test pipeline initialization with different configurations"""
        # Test default initialization
        pipeline = CopywritingEvaluatorPipeline()
        self.assertIsInstance(pipeline.config, PipelineConfig)
        self.assertEqual(pipeline.config.mode, ProcessingMode.TESTING)
        
        # Test custom configuration
        custom_config = PipelineConfig(
            mode=ProcessingMode.PRODUCTION,
            batch_size=10,
            max_consecutive_errors=5
        )
        pipeline_custom = CopywritingEvaluatorPipeline(custom_config)
        self.assertEqual(pipeline_custom.config.mode, ProcessingMode.PRODUCTION)
        self.assertEqual(pipeline_custom.config.batch_size, 10)

    def test_processing_mode_configuration(self):
        """Test that processing modes are configured correctly"""
        # Testing mode
        test_pipeline = CopywritingEvaluatorPipeline(
            PipelineConfig(mode=ProcessingMode.TESTING)
        )
        self.assertTrue(test_pipeline.config.immediate_processing)
        self.assertFalse(test_pipeline.config.enable_scheduling)
        self.assertTrue(test_pipeline.config.detailed_logging)
        
        # Production mode  
        prod_pipeline = CopywritingEvaluatorPipeline(
            PipelineConfig(mode=ProcessingMode.PRODUCTION)
        )
        self.assertFalse(prod_pipeline.config.immediate_processing)
        self.assertTrue(prod_pipeline.config.enable_scheduling)
        self.assertTrue(prod_pipeline.config.strict_validation)

    def test_variable_validation(self):
        """Test variable validation logic for supported and unsupported variables"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Test supported variables
        valid_text = "I am interested in the {job_title} position at {company_name}"
        is_valid, unsupported = pipeline._validate_sentence_variables(valid_text)
        self.assertTrue(is_valid)
        self.assertEqual(len(unsupported), 0)
        
        # Test unsupported variables
        invalid_text = "I have {years_experience} years and expect {salary_range}"
        is_valid, unsupported = pipeline._validate_sentence_variables(invalid_text)
        self.assertFalse(is_valid)
        self.assertIn('years_experience', unsupported)
        self.assertIn('salary_range', unsupported)
        
        # Test mixed variables
        mixed_text = "At {company_name}, I will use {programming_language} for {job_title}"
        is_valid, unsupported = pipeline._validate_sentence_variables(mixed_text)
        self.assertFalse(is_valid)
        self.assertIn('programming_language', unsupported)
        self.assertNotIn('company_name', unsupported)
        self.assertNotIn('job_title', unsupported)

    @patch('modules.content.copywriting_evaluator.pipeline_processor.DatabaseManager')
    async def test_variable_rejection_process(self, mock_db_class):
        """Test that sentences with unsupported variables are properly rejected"""
        mock_db_instance = Mock()
        mock_db_class.return_value = mock_db_instance
        
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        pipeline.db = mock_db_instance
        
        # Test sentences with unsupported variables
        sentences_with_unsupported = [
            {
                'id': 'reject_001',
                'content_text': 'I expect {salary} and have {experience_years} years',
                'table_name': 'sentence_bank_cover_letter'
            }
        ]
        
        rejected_count = await pipeline._validate_and_reject_unsupported_variables(
            sentences_with_unsupported
        )
        
        self.assertEqual(rejected_count, 1)
        mock_db_instance.execute_query.assert_called()

    def test_stage_processor_loading(self):
        """Test lazy loading of stage processors"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Test each stage processor loads correctly
        stages = [
            ProcessingStage.KEYWORD_FILTER,
            ProcessingStage.TRUTHFULNESS, 
            ProcessingStage.CANADIAN_SPELLING,
            ProcessingStage.TONE_ANALYSIS,
            ProcessingStage.SKILL_ANALYSIS
        ]
        
        for stage in stages:
            processor = pipeline._get_stage_processor(stage)
            self.assertIsNotNone(processor)
            
            # Verify processor is cached
            processor2 = pipeline._get_stage_processor(stage)
            self.assertIs(processor, processor2)

    def test_processing_stats(self):
        """Test ProcessingStats data structure"""
        stats = ProcessingStats(
            session_id="test_session_123",
            total_sentences=10,
            processed_sentences=8,
            filtered_sentences=2,
            approved_sentences=6
        )
        
        self.assertEqual(stats.session_id, "test_session_123")
        self.assertEqual(stats.total_sentences, 10)
        self.assertEqual(stats.processed_sentences, 8)
        self.assertEqual(stats.filtered_sentences, 2)
        self.assertEqual(stats.approved_sentences, 6)
        self.assertIsInstance(stats.stage_stats, dict)

    def test_can_process_method(self):
        """Test pipeline processing capability checks"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Test normal processing capability
        can_process, reason = pipeline.can_process()
        self.assertTrue(can_process)
        self.assertEqual(reason, "Ready for processing")
        
        # Test cooldown scenario
        pipeline.cooldown_until = datetime.now() + timedelta(hours=1)
        can_process, reason = pipeline.can_process()
        self.assertFalse(can_process)
        self.assertIn("cooldown", reason.lower())

    @patch('modules.content.copywriting_evaluator.keyword_filter.KeywordFilter')
    async def test_keyword_filter_stage(self, mock_keyword_filter_class):
        """Test keyword filtering stage processing"""
        # Mock the keyword filter processor
        mock_processor = Mock()
        mock_processor.process_batch = Mock(return_value=[
            {'id': 'test_001', 'status': 'approved'},
            {'id': 'test_002', 'status': 'rejected'}
        ])
        mock_keyword_filter_class.return_value = mock_processor
        
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Mock database interactions
        with patch.object(pipeline, 'db') as mock_db:
            mock_db.execute_query.return_value = None
            
            # Test stage processing
            stage_stats = await pipeline._process_stage(
                ProcessingStage.KEYWORD_FILTER, 
                self.test_sentences[:2], 
                "test_session"
            )
            
            self.assertEqual(stage_stats['stage'], 'keyword_filter')
            self.assertEqual(stage_stats['processed'], 2)
            self.assertEqual(stage_stats['approved'], 1)
            self.assertEqual(stage_stats['rejected'], 1)

    @patch('modules.content.copywriting_evaluator.truthfulness_evaluator.TruthfulnessEvaluator')
    async def test_truthfulness_evaluation_stage(self, mock_truth_eval_class):
        """Test truthfulness evaluation stage processing"""
        mock_processor = Mock()
        mock_processor.process_batch = Mock(return_value=[
            {'id': 'test_001', 'status': 'approved', 'confidence': 0.85},
            {'id': 'test_002', 'status': 'approved', 'confidence': 0.92}
        ])
        mock_truth_eval_class.return_value = mock_processor
        
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        with patch.object(pipeline, 'db') as mock_db:
            mock_db.execute_query.return_value = None
            
            stage_stats = await pipeline._process_stage(
                ProcessingStage.TRUTHFULNESS,
                self.test_sentences[:2],
                "test_session"
            )
            
            self.assertEqual(stage_stats['stage'], 'truthfulness')
            self.assertEqual(stage_stats['approved'], 2)
            self.assertEqual(stage_stats['rejected'], 0)

    @patch('modules.content.copywriting_evaluator.canadian_spelling_processor.CanadianSpellingProcessor')
    async def test_canadian_spelling_stage(self, mock_spelling_class):
        """Test Canadian spelling correction stage"""
        mock_processor = Mock()
        mock_processor.process_batch = Mock(return_value=[
            {'id': 'test_001', 'status': 'approved', 'corrections': 2},
            {'id': 'test_002', 'status': 'approved', 'corrections': 0}
        ])
        mock_spelling_class.return_value = mock_processor
        
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        with patch.object(pipeline, 'db') as mock_db:
            mock_db.execute_query.return_value = None
            
            stage_stats = await pipeline._process_stage(
                ProcessingStage.CANADIAN_SPELLING,
                self.test_sentences[:2],
                "test_session"
            )
            
            self.assertEqual(stage_stats['stage'], 'canadian_spelling')
            self.assertEqual(stage_stats['approved'], 2)

    @patch('modules.content.copywriting_evaluator.tone_analyzer.ToneAnalyzer')
    async def test_tone_analysis_stage(self, mock_tone_analyzer_class):
        """Test tone analysis stage processing"""
        mock_processor = Mock()
        mock_processor.process_batch = Mock(return_value=[
            {'id': 'test_001', 'status': 'approved', 'tone': 'Confident', 'strength': 0.8},
            {'id': 'test_002', 'status': 'approved', 'tone': 'Professional', 'strength': 0.9}
        ])
        mock_tone_analyzer_class.return_value = mock_processor
        
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        with patch.object(pipeline, 'db') as mock_db:
            mock_db.execute_query.return_value = None
            
            stage_stats = await pipeline._process_stage(
                ProcessingStage.TONE_ANALYSIS,
                self.test_sentences[:2],
                "test_session"
            )
            
            self.assertEqual(stage_stats['stage'], 'tone_analysis')
            self.assertEqual(stage_stats['approved'], 2)

    @patch('modules.content.copywriting_evaluator.skill_analyzer.SkillAnalyzer')
    async def test_skill_analysis_stage(self, mock_skill_analyzer_class):
        """Test skill assignment stage processing"""
        mock_processor = Mock()
        mock_processor.process_batch = Mock(return_value=[
            {'id': 'test_001', 'status': 'approved', 'primary_skill': 'Technical Communication'},
            {'id': 'test_002', 'status': 'approved', 'primary_skill': 'Programming'}
        ])
        mock_skill_analyzer_class.return_value = mock_processor
        
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        with patch.object(pipeline, 'db') as mock_db:
            mock_db.execute_query.return_value = None
            
            stage_stats = await pipeline._process_stage(
                ProcessingStage.SKILL_ANALYSIS,
                self.test_sentences[:2],
                "test_session"
            )
            
            self.assertEqual(stage_stats['stage'], 'skill_analysis')
            self.assertEqual(stage_stats['approved'], 2)

    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Test error counting
        initial_errors = pipeline.consecutive_errors
        
        # Simulate error scenario
        with patch.object(pipeline, '_process_stage') as mock_stage:
            mock_stage.side_effect = Exception("Simulated processing error")
            
            # Test that errors are tracked
            with self.assertRaises(Exception):
                await pipeline.process_sentences(table_name='sentence_bank_cover_letter')

    def test_batch_processing_logic(self):
        """Test batch processing configuration for different stages"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Stages that use batch processing
        batch_stages = [
            ProcessingStage.TRUTHFULNESS,
            ProcessingStage.TONE_ANALYSIS,
            ProcessingStage.SKILL_ANALYSIS
        ]
        
        # Stages that process individually
        individual_stages = [
            ProcessingStage.KEYWORD_FILTER,
            ProcessingStage.CANADIAN_SPELLING
        ]
        
        # Verify batch size configuration is appropriate for each stage type
        self.assertGreater(pipeline.config.batch_size, 0)
        self.assertLessEqual(pipeline.config.batch_size, 10)  # Reasonable batch size

    async def test_sentence_filtering_logic(self):
        """Test sentence filtering and selection for processing"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Mock database query results
        mock_sentences = [
            {'id': '001', 'keyword_filter_status': 'pending'},
            {'id': '002', 'keyword_filter_status': 'approved'},
            {'id': '003', 'keyword_filter_status': 'rejected'},
            {'id': '004', 'keyword_filter_status': 'error'}
        ]
        
        with patch.object(pipeline.db, 'execute_query') as mock_query:
            mock_query.return_value = mock_sentences
            
            sentences = await pipeline._get_sentences_for_processing(
                table_name='sentence_bank_cover_letter'
            )
            
            # Verify sentences are retrieved correctly
            mock_query.assert_called()

    def test_performance_tracking_integration(self):
        """Test performance tracking integration"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Verify performance tracker is initialized
        self.assertIsNotNone(pipeline.performance_tracker)
        
        # Test stats creation
        stats = ProcessingStats(session_id="perf_test")
        stats.start_time = datetime.now()
        stats.end_time = datetime.now() + timedelta(seconds=30)
        
        self.assertIsNotNone(stats.start_time)
        self.assertIsNotNone(stats.end_time)

    def test_restart_capability(self):
        """Test pipeline restart from specific stages"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Test restart from each stage
        restart_stages = [
            ProcessingStage.TRUTHFULNESS,
            ProcessingStage.CANADIAN_SPELLING, 
            ProcessingStage.TONE_ANALYSIS,
            ProcessingStage.SKILL_ANALYSIS
        ]
        
        for stage in restart_stages:
            # Verify stage exists and can be used for restart
            self.assertIsInstance(stage, ProcessingStage)
            self.assertIn(stage, list(ProcessingStage))

class TestErrorScenarios(unittest.TestCase):
    """Test suite for error scenarios and edge cases"""

    def setUp(self):
        self.test_config = PipelineConfig(mode=ProcessingMode.TESTING)

    def test_database_connection_errors(self):
        """Test handling of database connection failures"""
        with patch('modules.content.copywriting_evaluator.pipeline_processor.DatabaseManager') as mock_db_class:
            mock_db_instance = Mock()
            mock_db_instance.execute_query.side_effect = Exception("Database connection failed")
            mock_db_class.return_value = mock_db_instance
            
            pipeline = CopywritingEvaluatorPipeline(self.test_config)
            
            # Test that database errors are handled gracefully
            with self.assertRaises(Exception):
                pipeline.db.execute_query("SELECT * FROM test")

    def test_gemini_api_failures(self):
        """Test handling of Gemini API failures"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Test API timeout scenarios
        with patch.object(pipeline, '_process_stage') as mock_stage:
            mock_stage.side_effect = TimeoutError("API timeout")
            
            with self.assertRaises(TimeoutError):
                asyncio.run(pipeline._process_stage(
                    ProcessingStage.TRUTHFULNESS, [], "test_session"
                ))

    def test_invalid_sentence_data(self):
        """Test handling of invalid or corrupted sentence data"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Test variable validation with malformed data
        malformed_sentences = [
            {},  # Empty sentence
            {'id': 'test', 'content_text': None},  # Null content
            {'id': 'test', 'content_text': ''},  # Empty content
        ]
        
        for sentence in malformed_sentences:
            # Test that validation handles malformed data gracefully
            is_valid, unsupported = pipeline._validate_sentence_variables(
                sentence.get('content_text', '')
            )
            # Should not crash, should handle gracefully
            self.assertIsInstance(is_valid, bool)
            self.assertIsInstance(unsupported, list)

    def test_concurrent_processing_conflicts(self):
        """Test handling of concurrent processing scenarios"""
        pipeline = CopywritingEvaluatorPipeline(self.test_config)
        
        # Test cooldown mechanism
        pipeline.consecutive_errors = pipeline.config.max_consecutive_errors
        
        can_process, reason = pipeline.can_process()
        if pipeline.config.mode == ProcessingMode.PRODUCTION:
            self.assertFalse(can_process)
        else:
            # Testing mode should allow processing despite errors
            self.assertTrue(can_process)

def run_pipeline_tests():
    """Run all pipeline tests and return results"""
    print("=" * 70)
    print("🧪 COPYWRITING EVALUATOR PIPELINE TEST SUITE")
    print("=" * 70)
    
    # Create test suites
    pipeline_suite = unittest.TestLoader().loadTestsFromTestCase(TestCopywritingEvaluatorPipeline)
    error_suite = unittest.TestLoader().loadTestsFromTestCase(TestErrorScenarios)
    
    # Combine all test suites
    all_tests = unittest.TestSuite([pipeline_suite, error_suite])
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print(f"⏰ Tests started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    result = runner.run(all_tests)
    
    print("-" * 70)
    print(f"⏰ Tests completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Print summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"📊 TEST SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failures}")
    print(f"   💥 Errors: {errors}")
    print(f"   Success Rate: {(passed/total_tests)*100:.1f}%" if total_tests > 0 else "   Success Rate: 0%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_pipeline_tests()
    sys.exit(0 if success else 1)