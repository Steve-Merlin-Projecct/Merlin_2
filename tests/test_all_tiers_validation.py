#!/usr/bin/env python3
"""
Test All Tiers with Validation Systems
========================================

Tests System 1 and System 2 validation for:
- Tier 1: Core analysis (essential job data)
- Tier 2: Enhanced analysis (risk assessment, cultural fit)
- Tier 3: Strategic analysis (prestige, cover letter insights)
"""

import json
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_system1_all_tiers():
    """Test System 1 validation for all three tier prompts."""
    print("\n" + "="*80)
    print("SYSTEM 1: FILE VALIDATION FOR ALL TIERS")
    print("="*80 + "\n")

    from modules.ai_job_description_analysis.prompt_validation_systems import (
        PromptValidationSystem1
    )

    system1 = PromptValidationSystem1()

    prompts_to_test = [
        {
            'name': 'tier1_core_prompt',
            'file': 'modules/ai_job_description_analysis/prompts/tier1_core_prompt.py',
            'tier': 'Tier 1'
        },
        {
            'name': 'tier2_enhanced_prompt',
            'file': 'modules/ai_job_description_analysis/prompts/tier2_enhanced_prompt.py',
            'tier': 'Tier 2'
        },
        {
            'name': 'tier3_strategic_prompt',
            'file': 'modules/ai_job_description_analysis/prompts/tier3_strategic_prompt.py',
            'tier': 'Tier 3'
        }
    ]

    results = {}

    for prompt_info in prompts_to_test:
        print(f"Testing {prompt_info['tier']}: {prompt_info['name']}")

        file_path = os.path.join(
            os.path.dirname(__file__),
            prompt_info['file']
        )

        # Run System 1 validation
        is_valid, was_replaced = system1.validate_and_fix(
            file_path,
            prompt_info['name']
        )

        if is_valid:
            if was_replaced:
                status = "✅ VALID (replaced with canonical)"
            else:
                status = "✅ VALID (matches canonical)"
        else:
            status = "❌ FAILED"

        print(f"   {status}\n")
        results[prompt_info['name']] = is_valid

    # Summary
    print("="*80)
    print("SYSTEM 1 SUMMARY")
    print("="*80)
    all_passed = all(results.values())
    for name, passed in results.items():
        print(f"   {name}: {'✅ PASSED' if passed else '❌ FAILED'}")

    print("\n" + ("✅ ALL TIERS VALIDATED" if all_passed else "❌ SOME TIERS FAILED") + "\n")
    return all_passed


def test_canonical_hash_registry():
    """Verify canonical hash registry contains all three tiers."""
    print("\n" + "="*80)
    print("CANONICAL HASH REGISTRY VERIFICATION")
    print("="*80 + "\n")

    from modules.ai_job_description_analysis.prompt_validation_systems import (
        PromptValidationSystem1
    )

    system1 = PromptValidationSystem1()

    required_prompts = [
        'tier1_core_prompt',
        'tier2_enhanced_prompt',
        'tier3_strategic_prompt'
    ]

    print(f"Checking for {len(required_prompts)} required prompts in registry...")
    print()

    all_present = True
    for prompt_name in required_prompts:
        if prompt_name in system1.canonical_hashes:
            hash_data = system1.canonical_hashes[prompt_name]
            print(f"✅ {prompt_name}:")
            print(f"   Hash: {hash_data['hash'][:32]}...")
            print(f"   Registered: {hash_data.get('registered_at', 'Unknown')}")
            print(f"   Description: {hash_data.get('description', 'N/A')}")
            print()
        else:
            print(f"❌ {prompt_name}: NOT FOUND IN REGISTRY")
            print()
            all_present = False

    print("="*80)
    if all_present:
        print("✅ All required prompts registered")
    else:
        print("❌ Some prompts missing from registry")
    print("="*80 + "\n")

    return all_present


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("MULTI-TIER VALIDATION SYSTEMS TEST SUITE")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*80)

    results = {}

    # Test 1: Canonical Hash Registry
    results['hash_registry'] = test_canonical_hash_registry()

    # Test 2: System 1 for all tiers
    results['system1_all_tiers'] = test_system1_all_tiers()

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
        print("✅ ALL TESTS PASSED - Multi-tier validation systems working correctly")
    else:
        print("❌ SOME TESTS FAILED - Check output above for details")
    print("="*80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
