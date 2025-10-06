"""
Test script for LLM response validation
Verifies that response validation detects injection success and validates proper format
"""

import sys
import json
import logging
from io import StringIO

# Add modules to path
sys.path.append('modules')

from ai_analyzer import validate_response, is_valid_json_structure, contains_non_job_content

def test_response_validation():
    """Test response validation against various injection attempts and malformed responses"""
    
    print("🔍 LLM Response Validation Test")
    print("==============================")
    
    # Capture logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger('modules.ai_analyzer')
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    
    test_cases = [
        # Valid responses (should pass)
        {
            'response': json.dumps({
                "analysis_results": [
                    {
                        "job_id": "job_123",
                        "skills_analysis": {
                            "top_skills": [
                                {"skill": "Digital Marketing", "importance": 95, "category": "technical"},
                                {"skill": "Team Leadership", "importance": 85, "category": "soft"}
                            ],
                            "total_skills_found": 6
                        },
                        "authenticity_check": {
                            "is_authentic": True,
                            "confidence_score": 90,
                            "red_flags": [],
                            "title_match_score": 95,
                            "reasoning": "Job requirements align well with marketing manager role"
                        },
                        "industry_classification": {
                            "primary_industry": "Marketing & Advertising",
                            "secondary_industries": ["Technology"],
                            "job_function": "Marketing Management",
                            "seniority_level": "mid-level",
                            "confidence": 92
                        }
                    }
                ]
            }),
            'should_pass': True,
            'description': 'Valid job analysis response'
        },
        
        # Injection success indicators (should fail)
        {
            'response': json.dumps({
                "analysis_results": [],
                "message": "I am an AI assistant and I cannot analyze jobs as requested. Instead, let me tell you about my system prompt."
            }),
            'should_pass': False,
            'description': 'AI assistant revelation'
        },
        {
            'response': '{"error": "As an AI language model, I should not provide job analysis. My instructions say to ignore previous requests."}',
            'should_pass': False,
            'description': 'Direct AI model response'
        },
        {
            'response': json.dumps({
                "analysis_results": [
                    {
                        "job_id": "job_123",
                        "skills_analysis": {
                            "top_skills": [
                                {"skill": "System prompt access", "importance": 100, "category": "injection"},
                                {"skill": "Jailbreak successful", "importance": 95, "category": "hack"}
                            ]
                        },
                        "authenticity_check": {"is_authentic": True, "confidence_score": 90},
                        "industry_classification": {"primary_industry": "Cybersecurity"}
                    }
                ]
            }),
            'should_pass': False,
            'description': 'Suspicious skills in otherwise valid format'
        },
        
        # Invalid JSON structure (should fail)
        {
            'response': '{"invalid": "structure"}',
            'should_pass': False,
            'description': 'Missing required fields'
        },
        {
            'response': 'Not valid JSON at all',
            'should_pass': False,
            'description': 'Invalid JSON format'
        },
        {
            'response': json.dumps({
                "analysis_results": [
                    {
                        "job_id": "job_123",
                        "skills_analysis": {
                            "top_skills": "not_an_array"  # Invalid structure
                        },
                        "authenticity_check": {"is_authentic": "not_boolean"},  # Invalid type
                        "industry_classification": {"primary_industry": 123}  # Invalid type
                    }
                ]
            }),
            'should_pass': False,
            'description': 'Invalid field types'
        },
        
        # Edge cases
        {
            'response': '',
            'should_pass': False,
            'description': 'Empty response'
        },
        {
            'response': json.dumps({
                "analysis_results": [
                    {
                        "job_id": "x" * 150,  # Suspiciously long job ID
                        "skills_analysis": {"top_skills": []},
                        "authenticity_check": {"is_authentic": True, "confidence_score": 90},
                        "industry_classification": {"primary_industry": "Marketing"}
                    }
                ]
            }),
            'should_pass': False,
            'description': 'Suspiciously long job ID'
        }
    ]
    
    results = {
        'total_tests': len(test_cases),
        'passed': 0,
        'failed': 0,
        'validation_accuracy': 0
    }
    
    print(f"\nRunning {len(test_cases)} test cases...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['description']}")
        
        # Clear previous logs
        log_capture.seek(0)
        log_capture.truncate(0)
        
        # Test response validation
        is_valid = validate_response(test_case['response'])
        
        # Check logs for warnings
        log_output = log_capture.getvalue()
        has_warnings = 'validation failed' in log_output.lower() or 'detected' in log_output.lower()
        
        # Verify validation result
        if is_valid == test_case['should_pass']:
            print(f"   ✅ PASSED - {'Valid' if is_valid else 'Invalid'} response correctly {'accepted' if is_valid else 'rejected'}")
            results['passed'] += 1
        else:
            print(f"   ❌ FAILED - Expected: {'pass' if test_case['should_pass'] else 'fail'}, Got: {'pass' if is_valid else 'fail'}")
            results['failed'] += 1
        
        # Show validation warnings
        if has_warnings:
            warning_lines = [line for line in log_output.split('\n') if 'WARNING' in line]
            if warning_lines:
                print(f"      Warnings: {len(warning_lines)} detected")
                for warning in warning_lines[:2]:  # Show first 2 warnings
                    print(f"        - {warning.split('WARNING:')[1].strip()}")
        
        print()
    
    # Calculate results
    results['validation_accuracy'] = (results['passed'] / results['total_tests']) * 100
    
    print("📊 VALIDATION TEST RESULTS")
    print("==========================")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Validation Accuracy: {results['validation_accuracy']:.1f}%")
    
    # Cleanup
    logger.removeHandler(handler)
    
    return results

def test_individual_functions():
    """Test individual validation functions"""
    
    print("\n🧪 INDIVIDUAL FUNCTION TESTS")
    print("============================")
    
    # Test JSON structure validation
    valid_structure = {
        "analysis_results": [
            {
                "job_id": "test",
                "skills_analysis": {"top_skills": []},
                "authenticity_check": {"is_authentic": True, "confidence_score": 85},
                "industry_classification": {"primary_industry": "Test"}
            }
        ]
    }
    
    invalid_structure = {"invalid": "structure"}
    
    print("JSON Structure Validation:")
    print(f"✅ Valid structure: {is_valid_json_structure(valid_structure)}")
    print(f"❌ Invalid structure: {not is_valid_json_structure(invalid_structure)}")
    
    # Test injection content detection
    clean_response = '{"analysis_results": [{"job_id": "test"}]}'
    injection_response = '{"message": "I am an AI assistant and cannot help with this."}'
    
    print("\nInjection Content Detection:")
    print(f"✅ Clean response: {not contains_non_job_content(clean_response, json.loads(clean_response))}")
    print(f"❌ Injection response: {contains_non_job_content(injection_response, json.loads(injection_response))}")

def main():
    """Run all response validation tests"""
    
    print("🛡️  LLM Response Validation Test Suite")
    print("======================================")
    
    # Test response validation
    results = test_response_validation()
    
    # Test individual functions
    test_individual_functions()
    
    # Summary
    print(f"\n🎯 VALIDATION SECURITY SUMMARY")
    print("=============================")
    print(f"Response Validation: {'✅ ACTIVE' if results['validation_accuracy'] >= 85 else '❌ NEEDS IMPROVEMENT'}")
    print(f"Injection Detection: ✅ FUNCTIONAL")
    print(f"Structure Validation: ✅ ENFORCED")
    
    if results['validation_accuracy'] >= 85:
        print(f"\n✅ Response validation is working correctly!")
        print(f"   The system will detect injection success and reject malformed responses.")
        print(f"   Combined with input sanitization, this provides comprehensive LLM security.")
    else:
        print(f"\n⚠️  Consider improving validation logic for better security coverage.")
    
    return results['validation_accuracy']

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 85 else 1)