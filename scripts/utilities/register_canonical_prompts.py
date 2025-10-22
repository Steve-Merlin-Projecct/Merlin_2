#!/usr/bin/env python3
"""
Module: register_canonical_prompts.py
Purpose: Register canonical prompt hashes for AI prompt validation system
Created: 2024-09-22
Modified: 2025-10-21
Dependencies: modules.ai_job_description_analysis.prompt_validation_systems
Related: modules/ai_job_description_analysis/prompts/, analyze_prompt_and_response.py
Description: Calculates and registers canonical hashes for all tier prompts
             (tier1, tier2, tier3) in the hash registry for System 1 validation.
             Ensures prompt integrity and detects unauthorized modifications.

Usage:
    python register_canonical_prompts.py
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ai_job_description_analysis.prompt_validation_systems import (
    PromptValidationSystem1
)


def register_all_prompts():
    """Register canonical hashes for all tier prompts."""

    system1 = PromptValidationSystem1()

    prompts_to_register = [
        {
            'name': 'tier1_core_prompt',
            'file': 'modules/ai_job_description_analysis/prompts/tier1_core_prompt.py',
            'description': 'Tier 1 Core Analysis - Essential job data extraction'
        },
        {
            'name': 'tier2_enhanced_prompt',
            'file': 'modules/ai_job_description_analysis/prompts/tier2_enhanced_prompt.py',
            'description': 'Tier 2 Enhanced Analysis - Risk assessment and cultural fit'
        },
        {
            'name': 'tier3_strategic_prompt',
            'file': 'modules/ai_job_description_analysis/prompts/tier3_strategic_prompt.py',
            'description': 'Tier 3 Strategic Analysis - Application preparation guidance'
        }
    ]

    print("="*80)
    print("REGISTERING CANONICAL PROMPT HASHES")
    print("="*80 + "\n")

    for prompt_info in prompts_to_register:
        print(f"📝 Processing: {prompt_info['name']}")
        print(f"   Description: {prompt_info['description']}")
        print(f"   File: {prompt_info['file']}")

        file_path = os.path.join(
            os.path.dirname(__file__),
            prompt_info['file']
        )

        if not os.path.exists(file_path):
            print(f"   ❌ File not found: {file_path}\n")
            continue

        # Extract template
        template = system1.extract_prompt_template(file_path)
        if template is None:
            print(f"   ❌ Could not extract template\n")
            continue

        print(f"   ✅ Template extracted ({len(template)} chars)")

        # Calculate hash
        template_hash = system1.calculate_template_hash(template)
        print(f"   ✅ Hash calculated: {template_hash[:32]}...")

        # Register in canonical hashes
        system1.canonical_hashes[prompt_info['name']] = {
            'hash': template_hash,
            'registered_at': datetime.now().isoformat(),
            'last_validated': datetime.now().isoformat(),
            'description': prompt_info['description'],
            'file_path': prompt_info['file']
        }

        print(f"   ✅ Registered in canonical hash registry\n")

    # Save all hashes
    system1._save_canonical_hashes()

    print("="*80)
    print("CANONICAL HASH REGISTRY")
    print("="*80 + "\n")

    for name, data in system1.canonical_hashes.items():
        print(f"📌 {name}:")
        print(f"   Hash: {data['hash'][:64]}...")
        print(f"   Registered: {data.get('registered_at', 'Unknown')}")
        print(f"   Description: {data.get('description', 'N/A')}")
        print()

    print("="*80)
    print(f"✅ Successfully registered {len(system1.canonical_hashes)} canonical prompts")
    print(f"   Registry saved to: {system1.hash_registry_path}")
    print("="*80)


if __name__ == "__main__":
    register_all_prompts()
