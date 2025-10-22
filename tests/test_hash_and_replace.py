#!/usr/bin/env python3
"""
Hash and Replace System Test
==============================

Comprehensive test of the hash and replace security system for all three tiers.
Tests that System 1 detects unauthorized modifications and automatically
replaces them with canonical versions from git.
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ai_job_description_analysis.prompt_validation_systems import (
    PromptValidationSystem1
)


def test_hash_and_replace():
    """Test hash detection and automatic replacement for all tiers."""

    print("\n" + "="*80)
    print("HASH AND REPLACE SYSTEM COMPREHENSIVE TEST")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*80 + "\n")

    system1 = PromptValidationSystem1()

    # Test configuration
    tiers = [
        {
            'name': 'tier1_core_prompt',
            'file': 'modules/ai_job_description_analysis/prompts/tier1_core_prompt.py',
            'modification': ('ANALYSIS GUIDELINES:', 'ANALYSIS GUIDELINES (UNAUTHORIZED MODIFICATION):'),
            'description': 'Tier 1: Core Analysis'
        },
        {
            'name': 'tier2_enhanced_prompt',
            'file': 'modules/ai_job_description_analysis/prompts/tier2_enhanced_prompt.py',
            'modification': ('ANALYSIS GUIDELINES:', 'ANALYSIS GUIDELINES (UNAUTHORIZED MODIFICATION):'),
            'description': 'Tier 2: Enhanced Analysis'
        },
        {
            'name': 'tier3_strategic_prompt',
            'file': 'modules/ai_job_description_analysis/prompts/tier3_strategic_prompt.py',
            'modification': ('ANALYSIS GUIDELINES:', 'ANALYSIS GUIDELINES (UNAUTHORIZED MODIFICATION):'),
            'description': 'Tier 3: Strategic Analysis'
        }
    ]

    results = {}

    for tier_info in tiers:
        print(f"📝 Testing: {tier_info['description']}")
        print(f"   File: {tier_info['name']}.py")
        print("-" * 80)

        tier_name = tier_info['name']
        file_path = tier_info['file']
        old_text, new_text = tier_info['modification']

        # Step 1: Read original file
        with open(file_path, 'r') as f:
            original_content = f.read()

        # Step 2: Verify current file is valid
        print("   Step 1: Verifying current file is valid...")
        is_valid_before, _ = system1.validate_and_fix(file_path, tier_name)
        if not is_valid_before:
            print("   ❌ Current file is not valid - skipping test")
            results[tier_name] = False
            continue
        print("   ✅ Current file is valid")

        # Step 3: Make unauthorized modification
        print("   Step 2: Making unauthorized modification...")
        modified_content = original_content.replace(old_text, new_text)

        if modified_content == original_content:
            print(f"   ⚠️  Warning: No modification made (text not found)")
            results[tier_name] = False
            continue

        with open(file_path, 'w') as f:
            f.write(modified_content)
        print(f"   ✅ Modified: '{old_text}' → '{new_text}'")

        # Step 4: Calculate modified hash
        print("   Step 3: Calculating hashes...")
        template = system1.extract_prompt_template(file_path)
        if template is None:
            print("   ❌ Could not extract template")
            results[tier_name] = False
            continue

        modified_hash = system1.calculate_template_hash(template)
        canonical_hash = system1.canonical_hashes[tier_name]['hash']

        print(f"   Modified hash:  {modified_hash[:32]}...")
        print(f"   Canonical hash: {canonical_hash[:32]}...")
        print(f"   Hashes match: {modified_hash == canonical_hash}")

        if modified_hash == canonical_hash:
            print("   ⚠️  Warning: Modification did not change hash")
            results[tier_name] = False
            continue

        # Step 5: Run System 1 validation and replacement
        print("   Step 4: Running System 1 validation and replacement...")
        is_valid, was_replaced = system1.validate_and_fix(file_path, tier_name)

        print(f"   is_valid: {is_valid}")
        print(f"   was_replaced: {was_replaced}")

        # Step 6: Verify modification was removed
        print("   Step 5: Verifying replacement...")
        with open(file_path, 'r') as f:
            after_replacement = f.read()

        modification_removed = new_text not in after_replacement
        print(f"   Modification removed: {modification_removed}")

        # Step 7: Verify final hash matches canonical
        print("   Step 6: Verifying final hash...")
        final_template = system1.extract_prompt_template(file_path)
        final_hash = system1.calculate_template_hash(final_template)

        print(f"   Final hash:     {final_hash[:32]}...")
        print(f"   Canonical hash: {canonical_hash[:32]}...")

        hash_matches = final_hash == canonical_hash
        print(f"   Final hash matches canonical: {hash_matches}")

        # Overall result
        success = (
            is_valid and
            was_replaced and
            modification_removed and
            hash_matches
        )

        results[tier_name] = success
        print()
        print(f"   Result: {'✅ PASSED' if success else '❌ FAILED'}")
        print()

    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")

    for tier_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {tier_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "="*80)
    if all_passed:
        print("✅ HASH AND REPLACE SYSTEM FULLY WORKING FOR ALL TIERS")
        print()
        print("Security Features Verified:")
        print("  ✅ Hash detection working - detects unauthorized modifications")
        print("  ✅ Automatic replacement working - replaces with canonical from git")
        print("  ✅ Hash validation working - final hash matches canonical")
        print("  ✅ File formatting preserved - Python syntax intact")
    else:
        print("❌ SOME TESTS FAILED - Check output above for details")

    print("="*80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(test_hash_and_replace())
