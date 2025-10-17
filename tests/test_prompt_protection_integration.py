#!/usr/bin/env python3
"""Integration tests for prompt protection system"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import (
    create_tier1_core_prompt,
)


@pytest.fixture
def analyzer():
    """Create analyzer instance (requires GEMINI_API_KEY)"""
    try:
        return GeminiJobAnalyzer()
    except ValueError:
        pytest.skip("GEMINI_API_KEY not set")


@pytest.fixture
def sample_jobs():
    """Sample job data for testing"""
    return [
        {
            "id": "test_1",
            "title": "Test Engineer",
            "description": "Test description for integration testing. " * 50,
        }
    ]


def test_analyzer_has_security_manager(analyzer):
    """Test that analyzer initializes with security manager"""
    assert hasattr(analyzer, "security_mgr")
    assert analyzer.security_mgr is not None


def test_prompt_validation_on_generation(analyzer, sample_jobs):
    """Test that prompts are validated when generated"""
    # This should trigger validation
    prompt = analyzer._create_batch_analysis_prompt(sample_jobs)

    # Prompt should be validated and returned
    assert prompt is not None
    assert len(prompt) > 100
    assert "SECURITY TOKEN" in prompt


def test_agent_tampering_detection(analyzer, sample_jobs):
    """Test that agent tampering is detected and replaced"""
    # Generate canonical prompt
    canonical_prompt = create_tier1_core_prompt(sample_jobs)

    # Simulate tampering
    tampered_prompt = canonical_prompt.replace("SECURITY TOKEN", "TAMPERED TOKEN")

    # Validate (should be replaced)
    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name="tier1_core_prompt",
        current_prompt=tampered_prompt,
        change_source="agent",
        canonical_prompt_getter=lambda: create_tier1_core_prompt(sample_jobs),
    )

    assert was_replaced is True
    assert "TAMPERED TOKEN" not in validated_prompt
    assert "SECURITY TOKEN" in validated_prompt


def test_user_modification_allowed(analyzer, sample_jobs):
    """Test that user modifications are allowed (hash updated)"""
    # Generate canonical prompt
    canonical_prompt = create_tier1_core_prompt(sample_jobs)

    # Simulate user modification
    user_modified_prompt = canonical_prompt.replace(
        "SECURITY TOKEN", "USER MODIFIED TOKEN"
    )

    # Validate as user change (should update hash)
    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name="tier1_core_prompt",
        current_prompt=user_modified_prompt,
        change_source="user",
        canonical_prompt_getter=lambda: create_tier1_core_prompt(sample_jobs),
    )

    assert was_replaced is False
    assert "USER MODIFIED TOKEN" in validated_prompt


def test_tier2_protection(analyzer):
    """Test that Tier 2 prompts are also protected"""
    tier2_jobs = [
        {
            "job_data": {
                "id": "test_1",
                "title": "Test",
                "description": "Test. " * 50,
            },
            "tier1_results": {
                "structured_data": {"skill_requirements": {"skills": []}},
                "classification": {"industry": "Tech", "seniority_level": "Mid"},
                "authenticity_check": {"credibility_score": 8},
            },
        }
    ]

    # Import tier2 prompt
    from modules.ai_job_description_analysis.prompts.tier2_enhanced_prompt import (
        create_tier2_enhanced_prompt,
    )

    canonical_prompt = create_tier2_enhanced_prompt(tier2_jobs)
    tampered_prompt = canonical_prompt.replace("SECURITY TOKEN", "TAMPERED")

    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name="tier2_enhanced_prompt",
        current_prompt=tampered_prompt,
        change_source="agent",
        canonical_prompt_getter=lambda: create_tier2_enhanced_prompt(tier2_jobs),
    )

    assert was_replaced is True
    assert "TAMPERED" not in validated_prompt


def test_tier3_protection(analyzer):
    """Test that Tier 3 prompts are also protected"""
    tier3_jobs = [
        {
            "job_data": {
                "id": "test_1",
                "title": "Test",
                "description": "Test. " * 50,
            },
            "tier1_results": {
                "structured_data": {"skill_requirements": {"skills": []}},
                "classification": {"industry": "Tech", "seniority_level": "Mid"},
                "authenticity_check": {"credibility_score": 8},
            },
            "tier2_results": {
                "stress_level_analysis": {"estimated_stress_level": 5},
                "red_flags": {"unrealistic_expectations": {"detected": False}},
                "implicit_requirements": {"unstated_skills": []},
            },
        }
    ]

    # Import tier3 prompt
    from modules.ai_job_description_analysis.prompts.tier3_strategic_prompt import (
        create_tier3_strategic_prompt,
    )

    canonical_prompt = create_tier3_strategic_prompt(tier3_jobs)
    tampered_prompt = canonical_prompt.replace("SECURITY TOKEN", "TAMPERED")

    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name="tier3_strategic_prompt",
        current_prompt=tampered_prompt,
        change_source="agent",
        canonical_prompt_getter=lambda: create_tier3_strategic_prompt(tier3_jobs),
    )

    assert was_replaced is True
    assert "TAMPERED" not in validated_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
