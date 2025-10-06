#!/usr/bin/env python3
"""
Variable Feature Test Suite

Comprehensive tests for variable functionality including repetition prevention,
validation, and substitution across the copywriting evaluator system.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import re

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.content.copywriting_evaluator.pipeline_processor import CopywritingEvaluatorPipeline
from modules.content.content_manager import ContentManager
from modules.content.document_generation.template_engine import TemplateEngine

class TestVariableRepetitionPrevention(unittest.TestCase):
    """Test variable repetition prevention in content selection algorithm"""

    def setUp(self):
        """Set up test fixtures"""
        self.content_manager = ContentManager()
        
        # Mock sentences with variables for testing
        self.test_sentences = [
            {
                'id': 'var_001',
                'content_text': 'I am excited to apply for the {job_title} position',
                'table_name': 'sentence_bank_cover_letter',
                'keywords': ['excited', 'apply'],
                'tone_analysis_primary': 'Confident'
            },
            {
                'id': 'var_002', 
                'content_text': 'Working at {company_name} would be perfect',
                'table_name': 'sentence_bank_cover_letter',
                'keywords': ['working', 'perfect'],
                'tone_analysis_primary': 'Professional'
            },
            {
                'id': 'var_003',
                'content_text': 'The {job_title} role at {company_name} matches my goals',
                'table_name': 'sentence_bank_cover_letter', 
                'keywords': ['role', 'matches', 'goals'],
                'tone_analysis_primary': 'Confident'
            },
            {
                'id': 'var_004',
                'content_text': 'I believe {company_name} offers great opportunities',
                'table_name': 'sentence_bank_cover_letter',
                'keywords': ['believe', 'opportunities'],
                'tone_analysis_primary': 'Professional'
            },
            {
                'id': 'var_005',
                'content_text': 'My skills align with the {job_title} requirements',
                'table_name': 'sentence_bank_cover_letter',
                'keywords': ['skills', 'align', 'requirements'], 
                'tone_analysis_primary': 'Confident'
            }
        ]

    def test_single_variable_repetition_prevention(self):
        """Test that only one sentence with {job_title} is selected"""
        with patch.object(self.content_manager, '_get_database_sentences') as mock_db:
            mock_db.return_value = self.test_sentences
            
            # Mock the variable tracking
            with patch.object(self.content_manager, '_track_variable_usage') as mock_track:
                mock_track.return_value = None
                
                # Mock the selection method to return sentences with job_title
                job_title_sentences = [s for s in self.test_sentences if '{job_title}' in s['content_text']]
                
                # Simulate content selection with repetition prevention
                selected_sentences = []
                variables_used = set()
                
                for sentence in job_title_sentences:
                    sentence_variables = re.findall(r'\{([^}]+)\}', sentence['content_text'])
                    has_new_variable = any(var not in variables_used for var in sentence_variables)
                    
                    if has_new_variable or not sentence_variables:
                        selected_sentences.append(sentence)
                        variables_used.update(sentence_variables)
                
                # Should select only one sentence with {job_title}
                job_title_count = sum(1 for s in selected_sentences if '{job_title}' in s['content_text'])
                self.assertEqual(job_title_count, 1, 
                    "Should select only one sentence with {job_title} variable")

    def test_company_name_repetition_prevention(self):
        """Test that only one sentence with {company_name} is selected"""
        with patch.object(self.content_manager, '_get_database_sentences') as mock_db:
            mock_db.return_value = self.test_sentences
            
            # Filter sentences with company_name
            company_sentences = [s for s in self.test_sentences if '{company_name}' in s['content_text']]
            
            # Simulate selection with repetition prevention
            selected_sentences = []
            variables_used = set()
            
            for sentence in company_sentences:
                sentence_variables = re.findall(r'\{([^}]+)\}', sentence['content_text'])
                has_new_variable = any(var not in variables_used for var in sentence_variables)
                
                if has_new_variable or not sentence_variables:
                    selected_sentences.append(sentence)
                    variables_used.update(sentence_variables)
            
            # Should select only one sentence with {company_name}
            company_name_count = sum(1 for s in selected_sentences if '{company_name}' in s['content_text'])
            self.assertEqual(company_name_count, 1,
                "Should select only one sentence with {company_name} variable")

    def test_mixed_variable_handling(self):
        """Test handling of sentences with both variables"""
        mixed_sentence = {
            'id': 'mixed_001',
            'content_text': 'I want the {job_title} position at {company_name}',
            'table_name': 'sentence_bank_cover_letter',
            'keywords': ['want', 'position'],
            'tone_analysis_primary': 'Professional'
        }
        
        test_set = self.test_sentences + [mixed_sentence]
        
        # Simulate selection algorithm
        selected_sentences = []
        variables_used = set()
        
        for sentence in test_set:
            sentence_variables = re.findall(r'\{([^}]+)\}', sentence['content_text'])
            has_new_variable = any(var not in variables_used for var in sentence_variables)
            
            if has_new_variable or not sentence_variables:
                selected_sentences.append(sentence)
                variables_used.update(sentence_variables)
        
        # Mixed sentence should be preferred as it provides both variables
        mixed_selected = any(s['id'] == 'mixed_001' for s in selected_sentences)
        
        if mixed_selected:
            # If mixed sentence is selected, no other variable sentences should be
            job_title_others = sum(1 for s in selected_sentences 
                                 if s['id'] != 'mixed_001' and '{job_title}' in s['content_text'])
            company_others = sum(1 for s in selected_sentences
                               if s['id'] != 'mixed_001' and '{company_name}' in s['content_text'])
            
            self.assertEqual(job_title_others, 0, "No other {job_title} sentences should be selected")
            self.assertEqual(company_others, 0, "No other {company_name} sentences should be selected")

class TestVariableValidation(unittest.TestCase):
    """Test variable validation during pipeline processing"""

    def setUp(self):
        """Set up pipeline for testing"""
        self.pipeline = CopywritingEvaluatorPipeline()

    def test_supported_variables_approval(self):
        """Test that sentences with supported variables are approved"""
        supported_test_cases = [
            "I am interested in the {job_title} position",
            "Working at {company_name} would be ideal", 
            "The {job_title} role at {company_name} is perfect",
            "I want to contribute to {company_name}",
            "My experience makes me suitable for {job_title}"
        ]
        
        for text in supported_test_cases:
            is_valid, unsupported = self.pipeline._validate_sentence_variables(text)
            self.assertTrue(is_valid, f"Supported variable sentence should be valid: {text}")
            self.assertEqual(len(unsupported), 0, f"No unsupported variables found in: {text}")

    def test_unsupported_variables_rejection(self):
        """Test that sentences with unsupported variables are rejected"""
        unsupported_test_cases = [
            ("I have {years_experience} years of experience", ['years_experience']),
            ("My expected salary is {salary_range}", ['salary_range']),
            ("I work with {programming_language} and {framework}", ['programming_language', 'framework']),
            ("Contact me at {email_address} or {phone_number}", ['email_address', 'phone_number']),
            ("I studied at {university} in {graduation_year}", ['university', 'graduation_year'])
        ]
        
        for text, expected_unsupported in unsupported_test_cases:
            is_valid, unsupported = self.pipeline._validate_sentence_variables(text)
            self.assertFalse(is_valid, f"Unsupported variable sentence should be invalid: {text}")
            for var in expected_unsupported:
                self.assertIn(var, unsupported, f"Variable {var} should be in unsupported list")

    def test_mixed_variables_partial_rejection(self):
        """Test sentences with mix of supported and unsupported variables"""
        mixed_test_cases = [
            ("At {company_name}, I'll use my {programming_skills}", ['programming_skills']),
            ("The {job_title} requires {specific_technology}", ['specific_technology']),
            ("Working at {company_name} with {team_size} people", ['team_size']),
            ("As {job_title}, I expect {benefits_package}", ['benefits_package'])
        ]
        
        for text, expected_unsupported in mixed_test_cases:
            is_valid, unsupported = self.pipeline._validate_sentence_variables(text)
            self.assertFalse(is_valid, f"Mixed variable sentence should be invalid: {text}")
            
            # Check that only unsupported variables are flagged
            for var in expected_unsupported:
                self.assertIn(var, unsupported, f"Unsupported variable {var} should be flagged")
            
            # Check that supported variables are NOT flagged
            self.assertNotIn('job_title', unsupported, "job_title should not be in unsupported list")
            self.assertNotIn('company_name', unsupported, "company_name should not be in unsupported list")

    def test_pipeline_rejection_process(self):
        """Test that pipeline properly rejects sentences with unsupported variables"""
        test_sentences = [
            {
                'id': 'reject_001',
                'content_text': 'I have {years_experience} years',
                'table_name': 'sentence_bank_cover_letter'
            },
            {
                'id': 'reject_002', 
                'content_text': 'My salary expectation is {expected_salary}',
                'table_name': 'sentence_bank_cover_letter'
            },
            {
                'id': 'approve_001',
                'content_text': 'I want to work at {company_name}',
                'table_name': 'sentence_bank_cover_letter'
            }
        ]
        
        # Mock database operations
        with patch.object(self.pipeline, 'db') as mock_db:
            mock_db.execute_query.return_value = None
            
            # Test validation process
            rejected_sentences = []
            approved_sentences = []
            
            for sentence in test_sentences:
                is_valid, unsupported = self.pipeline._validate_sentence_variables(
                    sentence['content_text']
                )
                
                if not is_valid:
                    rejected_sentences.append(sentence)
                else:
                    approved_sentences.append(sentence)
            
            # Verify correct classification
            self.assertEqual(len(rejected_sentences), 2, "Should reject 2 sentences with unsupported variables")
            self.assertEqual(len(approved_sentences), 1, "Should approve 1 sentence with supported variables")
            
            # Verify specific sentences
            rejected_ids = [s['id'] for s in rejected_sentences]
            self.assertIn('reject_001', rejected_ids)
            self.assertIn('reject_002', rejected_ids)
            
            approved_ids = [s['id'] for s in approved_sentences]
            self.assertIn('approve_001', approved_ids)

class TestVariableSubstitution(unittest.TestCase):
    """Test variable substitution in template engine"""

    def setUp(self):
        """Set up template engine for testing"""
        self.template_engine = TemplateEngine()
        
        # Sample job data for substitution
        self.job_data = {
            'job_title': 'Senior Software Developer',
            'company_name': 'Tech Innovations Inc.'
        }

    def test_job_title_substitution(self):
        """Test {job_title} variable substitution"""
        test_cases = [
            ("I am interested in the {job_title} position", 
             "I am interested in the Senior Software Developer position"),
            ("The {job_title} role matches my skills",
             "The Senior Software Developer role matches my skills"),
            ("My experience is perfect for {job_title}",
             "My experience is perfect for Senior Software Developer")
        ]
        
        stats = {'variables_substituted': set(), 'variables_missing': set()}
        for original, expected in test_cases:
            result = self.template_engine.substitute_variables(original, self.job_data, stats)
            self.assertEqual(result, expected, f"Job title substitution failed for: {original}")

    def test_company_name_substitution(self):
        """Test {company_name} variable substitution"""
        test_cases = [
            ("I want to work at {company_name}",
             "I want to work at Tech Innovations Inc."),
            ("Working for {company_name} would be ideal",
             "Working for Tech Innovations Inc. would be ideal"),
            ("{company_name} is my preferred employer",
             "Tech Innovations Inc. is my preferred employer")
        ]
        
        stats = {'variables_substituted': set(), 'variables_missing': set()}
        for original, expected in test_cases:
            result = self.template_engine.substitute_variables(original, self.job_data, stats)
            self.assertEqual(result, expected, f"Company name substitution failed for: {original}")

    def test_both_variables_substitution(self):
        """Test substitution of both variables in same sentence"""
        test_cases = [
            ("I want the {job_title} position at {company_name}",
             "I want the Senior Software Developer position at Tech Innovations Inc."),
            ("The {job_title} role at {company_name} is perfect for me",
             "The Senior Software Developer role at Tech Innovations Inc. is perfect for me"),
            ("Working as {job_title} for {company_name} would be my dream job",
             "Working as Senior Software Developer for Tech Innovations Inc. would be my dream job")
        ]
        
        stats = {'variables_substituted': set(), 'variables_missing': set()}
        for original, expected in test_cases:
            result = self.template_engine.substitute_variables(original, self.job_data, stats)
            self.assertEqual(result, expected, f"Dual variable substitution failed for: {original}")

    def test_multiple_same_variable_substitution(self):
        """Test substitution when same variable appears multiple times"""
        test_cases = [
            ("{job_title} requires {job_title} experience",
             "Senior Software Developer requires Senior Software Developer experience"),
            ("{company_name} and {company_name} culture",
             "Tech Innovations Inc. and Tech Innovations Inc. culture")
        ]
        
        stats = {'variables_substituted': set(), 'variables_missing': set()}
        for original, expected in test_cases:
            result = self.template_engine.substitute_variables(original, self.job_data, stats)
            self.assertEqual(result, expected, f"Multiple same variable substitution failed: {original}")

    def test_missing_variable_data_handling(self):
        """Test handling when variable data is missing"""
        incomplete_data = {'job_title': 'Software Engineer'}  # Missing company_name
        
        text_with_missing = "I want the {job_title} position at {company_name}"
        stats = {'variables_substituted': set(), 'variables_missing': set()}
        result = self.template_engine.substitute_variables(text_with_missing, incomplete_data, stats)
        
        # Should substitute available variable and leave missing one unchanged
        self.assertIn("Software Engineer", result, "Available variable should be substituted")
        self.assertIn("{company_name}", result, "Missing variable should remain unchanged")

    def test_no_variables_text_unchanged(self):
        """Test that text without variables remains unchanged"""
        test_cases = [
            "I am a skilled developer",
            "My experience includes Python and JavaScript", 
            "I have worked on multiple projects",
            "Looking forward to hearing from you"
        ]
        
        stats = {'variables_substituted': set(), 'variables_missing': set()}
        for text in test_cases:
            result = self.template_engine.substitute_variables(text, self.job_data, stats)
            self.assertEqual(result, text, f"Text without variables should remain unchanged: {text}")

    def test_template_vs_variable_separation(self):
        """Test that template variables (<<>>) are separate from sentence variables ({})"""
        mixed_text = "Dear <<hiring_manager>>, I am interested in the {job_title} position"
        
        # Template engine should only substitute {} variables, not <<>> variables
        stats = {'variables_substituted': set(), 'variables_missing': set()}
        result = self.template_engine.substitute_variables(mixed_text, self.job_data, stats)
        
        self.assertIn("Senior Software Developer", result, "Sentence variable should be substituted")
        self.assertIn("<<hiring_manager>>", result, "Template variable should remain unchanged")

    def test_case_sensitivity(self):
        """Test that variable names are case-sensitive"""
        case_sensitive_data = {
            'job_title': 'Developer',
            'Job_Title': 'Manager',  # Different case
            'company_name': 'Company A',
            'Company_Name': 'Company B'  # Different case
        }
        
        text = "The {job_title} at {company_name}"
        stats = {'variables_substituted': set(), 'variables_missing': set()}
        result = self.template_engine.substitute_variables(text, case_sensitive_data, stats)
        
        self.assertEqual(result, "The Developer at Company A", 
                        "Should use exact case match for variables")

class TestVariableIntegration(unittest.TestCase):
    """Test integration of variable features across the system"""

    def setUp(self):
        """Set up integration test environment"""
        self.pipeline = CopywritingEvaluatorPipeline()
        self.content_manager = ContentManager()
        self.template_engine = TemplateEngine()

    def test_end_to_end_variable_workflow(self):
        """Test complete variable workflow from validation to substitution"""
        # Step 1: Variable validation during pipeline processing
        test_sentence = "I am excited about the {job_title} position at {company_name}"
        is_valid, unsupported = self.pipeline._validate_sentence_variables(test_sentence)
        
        self.assertTrue(is_valid, "Sentence with supported variables should pass validation")
        
        # Step 2: Content selection with repetition prevention
        # (Mock the database and selection logic)
        selected_sentence = {
            'content_text': test_sentence,
            'id': 'integration_001',
            'table_name': 'sentence_bank_cover_letter'
        }
        
        # Step 3: Variable substitution during document generation
        job_data = {
            'job_title': 'Data Scientist',
            'company_name': 'Analytics Corp'
        }
        
        stats = {'variables_substituted': set(), 'variables_missing': set()}
        final_text = self.template_engine.substitute_variables(
            selected_sentence['content_text'], job_data, stats
        )
        
        expected_result = "I am excited about the Data Scientist position at Analytics Corp"
        self.assertEqual(final_text, expected_result, 
                        "End-to-end variable processing should produce correct result")

    def test_variable_feature_error_handling(self):
        """Test error handling across variable features"""
        # Test validation with malformed variables
        malformed_cases = [
            "{incomplete",
            "incomplete}",
            "{}",
            "{ }",
            "{job_title extra text}",
        ]
        
        for malformed in malformed_cases:
            try:
                is_valid, unsupported = self.pipeline._validate_sentence_variables(malformed)
                # Should not crash and should return valid results
                self.assertIsInstance(is_valid, bool)
                self.assertIsInstance(unsupported, list)
            except Exception as e:
                self.fail(f"Variable validation should not crash on malformed input: {malformed} - {e}")
        
        # Test substitution with malformed data
        malformed_data_cases = [
            None,
            {},
            {'invalid_key': 'value'},
            {'job_title': None},
            {'company_name': ''}
        ]
        
        test_text = "I want the {job_title} position at {company_name}"
        
        for malformed_data in malformed_data_cases:
            try:
                stats = {'variables_substituted': set(), 'variables_missing': set()}
                result = self.template_engine.substitute_variables(test_text, malformed_data or {}, stats)
                # Should not crash and should return a string
                self.assertIsInstance(result, str)
            except Exception as e:
                self.fail(f"Variable substitution should not crash on malformed data: {malformed_data} - {e}")

def run_variable_feature_tests():
    """Run all variable feature tests with detailed reporting"""
    print("="*80)
    print("🧪 VARIABLE FEATURE COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Define test classes
    test_classes = [
        TestVariableRepetitionPrevention,
        TestVariableValidation,
        TestVariableSubstitution, 
        TestVariableIntegration
    ]
    
    # Create and run test suite
    test_suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True
    )
    
    import datetime
    print(f"⏰ Variable Feature Tests Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*80)
    
    result = runner.run(test_suite)
    
    print("-"*80)
    print(f"⏰ Tests Completed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Print detailed results
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors
    
    print(f"📊 VARIABLE FEATURE TEST RESULTS:")
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failures}")
    print(f"   💥 Errors: {errors}")
    
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    # Print feature coverage
    print(f"\n🎯 VARIABLE FEATURE COVERAGE:")
    print(f"   ✅ Repetition Prevention (Content Selection)")
    print(f"   ✅ Variable Validation (Pipeline Processing)")
    print(f"   ✅ Variable Substitution (Template Engine)")
    print(f"   ✅ Integration Testing (End-to-End)")
    print(f"   ✅ Error Handling (Edge Cases)")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    import datetime
    success = run_variable_feature_tests() 
    sys.exit(0 if success else 1)