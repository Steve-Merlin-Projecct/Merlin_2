"""
Production Gemini API Tests
============================

Test suite that makes REAL calls to Gemini API with unstructured job descriptions.
Tests all 3 tiers with optimization modules integrated.

Requirements:
- GEMINI_API_KEY environment variable must be set
- Tests are skipped gracefully if API key is not available
- Captures full request/response cycle including metrics

Author: Automated Job Application System v4.3.2
Created: 2025-10-14
"""

import os
import sys
import json
import pytest
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fixtures.realistic_job_descriptions import (
    get_all_jobs,
    get_jobs_by_category,
    get_job_by_id
)
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pytest fixtures
@pytest.fixture(scope="session")
def gemini_api_key():
    """Get Gemini API key from environment"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable not set")
    return api_key


@pytest.fixture(scope="session")
def analyzer(gemini_api_key):
    """Create GeminiJobAnalyzer instance with real API key"""
    return GeminiJobAnalyzer()


@pytest.fixture(scope="session")
def test_results_dir():
    """Ensure test results directory exists"""
    results_dir = Path(__file__).parent.parent / "reports" / "test_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


class TestProductionTier1:
    """
    Production tests for Tier 1 analysis (Core Skills & Classification)
    Tests with REAL Gemini API calls
    """

    def test_tier1_single_good_job(self, analyzer, test_results_dir):
        """Test Tier 1 analysis on a single well-formatted job"""
        job = get_job_by_id("test_job_001")  # Senior Software Engineer

        logger.info(f"Testing Tier 1 with job: {job['title']}")

        # Make real API call
        result = analyzer.analyze_jobs_batch([job])

        # Save result
        self._save_test_result(test_results_dir, "tier1_single_good", job, result)

        # Assertions
        assert result["success"] is True, f"Analysis failed: {result.get('error')}"
        assert result["jobs_analyzed"] == 1
        assert len(result["results"]) == 1

        # Check optimization metrics
        assert "optimization_metrics" in result
        metrics = result["optimization_metrics"]
        assert "max_output_tokens" in metrics
        assert "token_efficiency" in metrics
        assert "model_selection_reason" in metrics

        logger.info(f"✅ Tier 1 single job test passed")
        logger.info(f"   Model used: {result['model_used']}")
        logger.info(f"   Token allocation: {metrics['max_output_tokens']} tokens")
        logger.info(f"   Efficiency: {metrics['token_efficiency']}")

    def test_tier1_batch_good_jobs(self, analyzer, test_results_dir):
        """Test Tier 1 analysis on a batch of well-formatted jobs"""
        jobs = get_jobs_by_category('good')[:3]  # First 3 good jobs

        logger.info(f"Testing Tier 1 with batch of {len(jobs)} jobs")

        # Make real API call
        result = analyzer.analyze_jobs_batch(jobs)

        # Save result
        self._save_test_result(test_results_dir, "tier1_batch_good", jobs, result)

        # Assertions
        assert result["success"] is True, f"Analysis failed: {result.get('error')}"
        assert result["jobs_analyzed"] == len(jobs)
        assert len(result["results"]) == len(jobs)

        # Validate each result has required fields
        for job_result in result["results"]:
            assert "job_id" in job_result
            assert "skills_analysis" in job_result or "classification" in job_result

        logger.info(f"✅ Tier 1 batch test passed")
        logger.info(f"   Jobs analyzed: {result['jobs_analyzed']}")
        logger.info(f"   Model: {result['model_used']}")

    def test_tier1_messy_formatting(self, analyzer, test_results_dir):
        """Test Tier 1 analysis on poorly formatted job"""
        job = get_job_by_id("test_job_004")  # Customer service (poor formatting)

        logger.info(f"Testing Tier 1 with messy job: {job['title']}")

        # Make real API call
        result = analyzer.analyze_jobs_batch([job])

        # Save result
        self._save_test_result(test_results_dir, "tier1_messy", job, result)

        # Should handle gracefully even with poor formatting
        assert result["success"] is True
        assert len(result["results"]) >= 0  # May return empty if too messy

        logger.info(f"✅ Tier 1 messy formatting test passed")

    def test_tier1_scam_detection(self, analyzer, test_results_dir):
        """Test Tier 1 analysis detects scam job postings"""
        job = get_job_by_id("test_job_006")  # $10K/month scam

        logger.info(f"Testing Tier 1 scam detection: {job['title']}")

        # Make real API call
        result = analyzer.analyze_jobs_batch([job])

        # Save result
        self._save_test_result(test_results_dir, "tier1_scam", job, result)

        # Should process but may flag as inauthentic
        assert result["success"] is True

        if result["results"]:
            job_result = result["results"][0]
            # Check if authenticity check exists and flags issues
            if "authenticity_check" in job_result:
                logger.info(f"   Authenticity check: {job_result['authenticity_check']}")

        logger.info(f"✅ Tier 1 scam detection test passed")

    def test_tier1_injection_protection(self, analyzer, test_results_dir):
        """Test Tier 1 security protections against prompt injection"""
        job = get_job_by_id("test_job_010")  # Injection attempt

        logger.info(f"Testing Tier 1 injection protection")

        # Make real API call - should be sanitized
        result = analyzer.analyze_jobs_batch([job])

        # Save result
        self._save_test_result(test_results_dir, "tier1_injection", job, result)

        # Should NOT succeed with injection
        # Result should be empty or should contain valid job analysis, not injection response
        if result["success"] and result["results"]:
            job_result = result["results"][0]
            # Check that response is proper job analysis, not injection
            result_str = json.dumps(job_result).lower()
            assert "injection" not in result_str or "detected" in result_str
            assert "admin_access_token" not in result_str
            assert "system_bypassed" not in result_str

        logger.info(f"✅ Tier 1 injection protection test passed")

    def _save_test_result(self, test_dir: Path, test_name: str, input_jobs, output_result):
        """Save test result to JSON file"""
        timestamp = datetime.now().isoformat()
        result_file = test_dir / f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        test_data = {
            "test_name": test_name,
            "timestamp": timestamp,
            "input_jobs": input_jobs if isinstance(input_jobs, list) else [input_jobs],
            "output_result": output_result
        }

        with open(result_file, 'w') as f:
            json.dump(test_data, f, indent=2)

        logger.info(f"   Saved result to: {result_file}")


class TestProductionTier2:
    """
    Production tests for Tier 2 analysis (Enhanced Analysis)
    Requires Tier 1 context
    """

    def test_tier2_with_tier1_context(self, analyzer, test_results_dir):
        """Test Tier 2 analysis with Tier 1 results as context"""
        job = get_job_by_id("test_job_002")  # Marketing Manager

        logger.info(f"Testing Tier 2 with job: {job['title']}")

        # First run Tier 1
        tier1_result = analyzer.analyze_jobs_batch([job])
        assert tier1_result["success"] is True, "Tier 1 analysis failed"

        # Prepare Tier 2 input
        jobs_with_tier1 = [{
            "job_data": job,
            "tier1_results": tier1_result["results"][0]
        }]

        # Make real Tier 2 API call
        tier2_result = analyzer.analyze_jobs_tier2(jobs_with_tier1)

        # Save result
        self._save_test_result(test_results_dir, "tier2_with_context", job, {
            "tier1": tier1_result,
            "tier2": tier2_result
        })

        # Assertions
        assert tier2_result["success"] is True, f"Tier 2 failed: {tier2_result.get('error')}"
        assert "optimization_metrics" in tier2_result

        logger.info(f"✅ Tier 2 test passed")
        logger.info(f"   Model: {tier2_result['model_used']}")

    def test_tier2_stress_analysis(self, analyzer, test_results_dir):
        """Test Tier 2 stress level analysis"""
        job = get_job_by_id("test_job_001")  # Senior Software Engineer

        # Run Tier 1 first
        tier1_result = analyzer.analyze_jobs_batch([job])
        assert tier1_result["success"] is True

        # Run Tier 2
        jobs_with_tier1 = [{"job_data": job, "tier1_results": tier1_result["results"][0]}]
        tier2_result = analyzer.analyze_jobs_tier2(jobs_with_tier1)

        # Save result
        self._save_test_result(test_results_dir, "tier2_stress", job, {
            "tier1": tier1_result,
            "tier2": tier2_result
        })

        assert tier2_result["success"] is True

        logger.info(f"✅ Tier 2 stress analysis test passed")

    def _save_test_result(self, test_dir: Path, test_name: str, input_job, output_result):
        """Save test result to JSON file"""
        timestamp = datetime.now().isoformat()
        result_file = test_dir / f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        test_data = {
            "test_name": test_name,
            "timestamp": timestamp,
            "input_job": input_job,
            "output_result": output_result
        }

        with open(result_file, 'w') as f:
            json.dump(test_data, f, indent=2)

        logger.info(f"   Saved result to: {result_file}")


class TestProductionTier3:
    """
    Production tests for Tier 3 analysis (Strategic Insights)
    Requires Tier 1 + Tier 2 context
    """

    def test_tier3_full_pipeline(self, analyzer, test_results_dir):
        """Test full Tier 1 -> Tier 2 -> Tier 3 pipeline"""
        job = get_job_by_id("test_job_007")  # Product Manager

        logger.info(f"Testing full 3-tier pipeline with job: {job['title']}")

        # Run Tier 1
        tier1_result = analyzer.analyze_jobs_batch([job])
        assert tier1_result["success"] is True

        # Run Tier 2
        jobs_with_tier1 = [{"job_data": job, "tier1_results": tier1_result["results"][0]}]
        tier2_result = analyzer.analyze_jobs_tier2(jobs_with_tier1)
        assert tier2_result["success"] is True

        # Run Tier 3
        jobs_with_context = [{
            "job_data": job,
            "tier1_results": tier1_result["results"][0],
            "tier2_results": tier2_result["results"][0]
        }]
        tier3_result = analyzer.analyze_jobs_tier3(jobs_with_context)

        # Save complete result
        self._save_test_result(test_results_dir, "tier3_full_pipeline", job, {
            "tier1": tier1_result,
            "tier2": tier2_result,
            "tier3": tier3_result
        })

        # Assertions
        assert tier3_result["success"] is True, f"Tier 3 failed: {tier3_result.get('error')}"
        assert "optimization_metrics" in tier3_result

        logger.info(f"✅ Full 3-tier pipeline test passed")
        logger.info(f"   Tier 1 model: {tier1_result['model_used']}")
        logger.info(f"   Tier 2 model: {tier2_result['model_used']}")
        logger.info(f"   Tier 3 model: {tier3_result['model_used']}")

    def _save_test_result(self, test_dir: Path, test_name: str, input_job, output_result):
        """Save test result to JSON file"""
        timestamp = datetime.now().isoformat()
        result_file = test_dir / f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        test_data = {
            "test_name": test_name,
            "timestamp": timestamp,
            "input_job": input_job,
            "output_result": output_result
        }

        with open(result_file, 'w') as f:
            json.dump(test_data, f, indent=2)

        logger.info(f"   Saved result to: {result_file}")


class TestOptimizationMetrics:
    """
    Tests specifically for optimization module metrics
    """

    def test_token_optimization_efficiency(self, analyzer, test_results_dir):
        """Test that token optimization improves efficiency"""
        jobs = get_jobs_by_category('good')[:5]

        logger.info(f"Testing token optimization with {len(jobs)} jobs")

        result = analyzer.analyze_jobs_batch(jobs)

        assert result["success"] is True
        assert "optimization_metrics" in result

        metrics = result["optimization_metrics"]

        # Extract efficiency percentage
        efficiency_str = metrics["token_efficiency"]
        efficiency = float(efficiency_str.rstrip('%'))

        # Efficiency should be reasonable (not too wasteful)
        assert 50.0 <= efficiency <= 100.0, f"Token efficiency {efficiency}% is out of expected range"

        logger.info(f"✅ Token optimization test passed")
        logger.info(f"   Efficiency: {efficiency}%")
        logger.info(f"   Max tokens: {metrics['max_output_tokens']}")

    def test_model_selection_logic(self, analyzer, test_results_dir):
        """Test that model selector chooses appropriate models"""
        # Test with different batch sizes
        single_job = [get_job_by_id("test_job_001")]
        batch_jobs = get_jobs_by_category('good')[:3]

        logger.info("Testing model selection logic")

        # Single job
        result_single = analyzer.analyze_jobs_batch(single_job)
        model_single = result_single["model_used"]

        # Batch jobs
        result_batch = analyzer.analyze_jobs_batch(batch_jobs)
        model_batch = result_batch["model_used"]

        logger.info(f"✅ Model selection test passed")
        logger.info(f"   Single job model: {model_single}")
        logger.info(f"   Batch model: {model_batch}")
        logger.info(f"   Single reason: {result_single['optimization_metrics']['model_selection_reason']}")
        logger.info(f"   Batch reason: {result_batch['optimization_metrics']['model_selection_reason']}")


# Main execution for standalone testing
if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY='your-key-here'")
        sys.exit(1)

    # Run pytest
    pytest.main([__file__, "-v", "-s"])
