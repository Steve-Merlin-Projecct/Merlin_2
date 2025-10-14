#!/usr/bin/env python3
"""Update prompt hash after intentional user modification"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.ai_job_description_analysis.prompt_security_manager import (
    PromptSecurityManager,
)
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import (
    create_tier1_core_prompt,
)
from modules.ai_job_description_analysis.prompts.tier2_enhanced_prompt import (
    create_tier2_enhanced_prompt,
)
from modules.ai_job_description_analysis.prompts.tier3_strategic_prompt import (
    create_tier3_strategic_prompt,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/update_prompt_hash.py <prompt_name>")
        print()
        print("Available prompts:")
        print("  - tier1_core_prompt")
        print("  - tier2_enhanced_prompt")
        print("  - tier3_strategic_prompt")
        return

    prompt_name = sys.argv[1]
    security_mgr = PromptSecurityManager()

    # Sample data for prompt generation
    sample_jobs = [
        {
            "id": "update",
            "title": "Update",
            "description": "Update prompt hash. " * 20,
        }
    ]

    # Generate current version of prompt
    if prompt_name == "tier1_core_prompt":
        current_prompt = create_tier1_core_prompt(sample_jobs)
    elif prompt_name == "tier2_enhanced_prompt":
        tier2_jobs = [{"job_data": sample_jobs[0], "tier1_results": {}}]
        current_prompt = create_tier2_enhanced_prompt(tier2_jobs)
    elif prompt_name == "tier3_strategic_prompt":
        tier3_jobs = [
            {
                "job_data": sample_jobs[0],
                "tier1_results": {},
                "tier2_results": {},
            }
        ]
        current_prompt = create_tier3_strategic_prompt(tier3_jobs)
    else:
        print(f"❌ Unknown prompt: {prompt_name}")
        return

    # Register as user modification
    print(f"Updating hash for: {prompt_name}")
    security_mgr.register_prompt(prompt_name, current_prompt, change_source="user")
    print("✅ Hash updated successfully")


if __name__ == "__main__":
    main()
