#!/usr/bin/env python3
"""
Test script for System 1 and System 2 validation workflows
============================================================

This script tests:
- System 1: File modification validation (hash → compare → replace)
- System 2: Runtime execution workflow (validate → token → send → verify)
"""

import json
import logging
import os
import sys
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_system1():
    """Test System 1: File modification validation"""
    print("\n" + "="*80)
    print("TESTING SYSTEM 1: FILE MODIFICATION VALIDATION")
    print("="*80 + "\n")

    try:
        from modules.ai_job_description_analysis.prompt_validation_systems import (
            PromptValidationSystem1
        )

        system1 = PromptValidationSystem1()

        # Test extracting prompt template
        prompt_file = os.path.join(
            os.path.dirname(__file__),
            "modules/ai_job_description_analysis/prompts/tier1_core_prompt.py"
        )

        print(f"📁 Testing prompt file: {prompt_file}")

        # Step 1: Extract template
        print("\n🔍 Step 1.A: Extracting prompt template...")
        template = system1.extract_prompt_template(prompt_file)
        if template:
            print(f"✅ Template extracted, length: {len(template)} chars")
            print(f"   First 100 chars: {template[:100]}...")
        else:
            print("❌ Failed to extract template")
            return False

        # Step 2: Calculate hash
        print("\n🔍 Step 1.B: Calculating template hash...")
        current_hash = system1.calculate_template_hash(template)
        print(f"✅ Current hash: {current_hash[:32]}...")

        # Step 3: Validate and fix
        print("\n🔍 Step 1.C: Running validation and fix...")
        is_valid, was_replaced = system1.validate_and_fix(prompt_file, "tier1_core_prompt")

        if is_valid:
            if was_replaced:
                print("✅ Validation successful - prompt was replaced with canonical")
            else:
                print("✅ Validation successful - prompt matches canonical")
        else:
            print("❌ Validation failed")
            return False

        print("\n✅ SYSTEM 1 TEST PASSED")
        return True

    except Exception as e:
        print(f"\n❌ SYSTEM 1 TEST FAILED: {e}")
        logger.exception("System 1 test error")
        return False


def test_system2():
    """Test System 2: Runtime execution workflow"""
    print("\n" + "="*80)
    print("TESTING SYSTEM 2: RUNTIME EXECUTION WORKFLOW")
    print("="*80 + "\n")

    try:
        from modules.ai_job_description_analysis.prompt_validation_systems import (
            PromptValidationSystem2
        )

        system2 = PromptValidationSystem2()

        # Create test job
        test_job = {
            'id': 'test_job_002',
            'title': 'Python Developer',
            'description': """
                We are looking for a Python Developer to join our team.

                Responsibilities:
                - Write clean, maintainable Python code
                - Develop REST APIs using FastAPI
                - Work with PostgreSQL databases
                - Participate in code reviews

                Requirements:
                - 3+ years Python experience
                - Experience with FastAPI or similar frameworks
                - SQL database knowledge
                - Git version control

                Benefits:
                - Competitive salary
                - Remote work options
                - Health insurance
            """,
            'company': 'TechStartup Inc',
            'location': 'Remote'
        }

        prompt_file = os.path.join(
            os.path.dirname(__file__),
            "modules/ai_job_description_analysis/prompts/tier1_core_prompt.py"
        )

        print("📋 Test job: Python Developer at TechStartup Inc")
        print("\n🚀 Starting System 2 workflow...")

        # Execute complete workflow
        result = system2.execute_workflow(
            jobs=[test_job],
            prompt_file_path=prompt_file,
            prompt_name="tier1_core_prompt"
        )

        # Check results
        print("\n📊 Workflow Results:")
        print(f"   Success: {result['success']}")
        print(f"   Steps completed: {len(result['steps_completed'])}")

        for step in result['steps_completed']:
            print(f"   ✅ {step}")

        if result['errors']:
            print(f"\n⚠️ Errors encountered:")
            for error in result['errors']:
                print(f"   - {error}")

        if result['success']:
            print("\n✅ SYSTEM 2 TEST PASSED")
            if result['data']:
                print(f"   Analyzed {len(result['data'])} jobs successfully")
                # Show sample of results
                if result['data'] and len(result['data']) > 0:
                    first_result = result['data'][0]
                    print(f"\n   Sample result for job {first_result.get('job_id')}:")
                    if 'authenticity_check' in first_result:
                        print(f"   - Authenticity: {first_result['authenticity_check'].get('is_authentic')}")
                    if 'classification' in first_result:
                        print(f"   - Industry: {first_result['classification'].get('industry')}")
                    if 'structured_data' in first_result:
                        print(f"   - Job Type: {first_result['structured_data'].get('job_type')}")
            return True
        else:
            print("\n❌ SYSTEM 2 TEST FAILED")
            return False

    except Exception as e:
        print(f"\n❌ SYSTEM 2 TEST FAILED: {e}")
        logger.exception("System 2 test error")
        return False


def test_integration():
    """Test both systems working together"""
    print("\n" + "="*80)
    print("INTEGRATION TEST: USING BOTH SYSTEMS VIA AI ANALYZER")
    print("="*80 + "\n")

    try:
        from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer

        analyzer = GeminiJobAnalyzer()

        # Create test job
        test_job = {
            'id': 'test_job_003',
            'title': 'Full Stack Developer',
            'description': """
                Join our innovative team as a Full Stack Developer!

                What you'll do:
                - Build modern web applications using React and Node.js
                - Design and implement RESTful APIs
                - Work with MongoDB and PostgreSQL databases
                - Collaborate with UX designers and product managers

                What we're looking for:
                - 5+ years full stack development experience
                - Strong JavaScript/TypeScript skills
                - Experience with React, Node.js, and Express
                - Database design and optimization skills
                - Excellent communication skills

                What we offer:
                - Salary: $120,000 - $150,000
                - Stock options
                - Flexible work schedule
                - Professional development budget
            """,
            'company': 'Innovation Labs',
            'location': 'San Francisco, CA (Hybrid)'
        }

        print("📋 Test job: Full Stack Developer at Innovation Labs")
        print("\n🔄 Calling analyzer.analyze_jobs_batch()...")

        # Call analyze_jobs_batch which should use System 2
        result = analyzer.analyze_jobs_batch([test_job])

        print("\n📊 Analysis Results:")
        print(f"   Success: {result.get('success')}")
        print(f"   Workflow used: {result.get('workflow', 'Unknown')}")
        print(f"   Jobs analyzed: {result.get('jobs_analyzed', 0)}")

        if result.get('steps_completed'):
            print("\n   System 2 steps completed:")
            for step in result['steps_completed']:
                print(f"   ✅ {step}")

        if result.get('success'):
            print("\n✅ INTEGRATION TEST PASSED")
            return True
        else:
            print(f"\n❌ INTEGRATION TEST FAILED: {result.get('error')}")
            return False

    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        logger.exception("Integration test error")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("PROMPT VALIDATION SYSTEMS TEST SUITE")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*80)

    results = {
        'system1': False,
        'system2': False,
        'integration': False
    }

    # Test System 1
    results['system1'] = test_system1()

    # Test System 2
    results['system2'] = test_system2()

    # Test Integration
    results['integration'] = test_integration()

    # Summary
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80 + "\n")

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name.upper()}: {status}")

    all_passed = all(results.values())
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())