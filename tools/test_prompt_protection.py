#!/usr/bin/env python3
"""Test prompt protection system"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import (
    create_tier1_core_prompt,
)


def test_protection():
    print("🧪 Testing prompt protection system...\n")

    # Initialize analyzer (includes security manager)
    try:
        analyzer = GeminiJobAnalyzer()
    except ValueError as e:
        print(f"⚠️  Skipping test: {e}")
        print("   Set GEMINI_API_KEY environment variable to run tests")
        return

    # Create sample job
    sample_jobs = [
        {
            "id": "test_job_1",
            "title": "Software Engineer",
            "description": "Test job description for protection testing. " * 30,
        }
    ]

    # Test 1: Generate prompt through analyzer (should pass validation)
    print("Test 1: Normal prompt generation...")
    try:
        prompt = analyzer._create_batch_analysis_prompt(sample_jobs)
        print("✅ Normal generation passed\n")
    except Exception as e:
        print(f"❌ Normal generation failed: {e}\n")
        return

    # Test 2: Manually modify prompt (simulate agent tampering)
    print("Test 2: Simulating agent tampering...")
    tampered_prompt = create_tier1_core_prompt(sample_jobs)
    tampered_prompt = tampered_prompt.replace("CRITICAL SECURITY", "MODIFIED BY AGENT")

    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name="tier1_core_prompt",
        current_prompt=tampered_prompt,
        change_source="agent",
        canonical_prompt_getter=lambda: create_tier1_core_prompt(sample_jobs),
    )

    if was_replaced:
        print("✅ Tampered prompt was detected and replaced\n")
    else:
        print("❌ Tampering was NOT detected!\n")

    # Test 3: User modification (should update hash)
    print("Test 3: Simulating user modification...")
    user_modified_prompt = create_tier1_core_prompt(sample_jobs)
    user_modified_prompt = user_modified_prompt.replace(
        "CRITICAL SECURITY", "UPDATED BY USER"
    )

    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name="tier1_core_prompt",
        current_prompt=user_modified_prompt,
        change_source="user",
        canonical_prompt_getter=lambda: create_tier1_core_prompt(sample_jobs),
    )

    if not was_replaced:
        print("✅ User modification was allowed (hash updated)\n")
    else:
        print("❌ User modification was incorrectly replaced!\n")

    # Test 4: Verify hash registry exists
    print("Test 4: Checking hash registry...")
    from pathlib import Path

    registry_file = Path("storage/prompt_hashes.json")
    if registry_file.exists():
        print("✅ Hash registry exists at storage/prompt_hashes.json\n")
    else:
        print("⚠️  Hash registry not found (will be created on first use)\n")

    print("🎉 All tests completed")


if __name__ == "__main__":
    test_protection()
