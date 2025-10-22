#!/usr/bin/env python3
"""
Direct Gemini API Test Script
==============================

Tests whether sending data to Gemini API returns satisfactory analysis results.
This script bypasses pytest fixtures and directly tests the integration.

Usage:
    python test_gemini_direct.py

Requirements:
    - GEMINI_API_KEY must be set in environment or .env file
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Try to load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, relying on system environment variables")

from tests.fixtures.realistic_job_descriptions import REALISTIC_JOB_DESCRIPTIONS
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer


def test_single_job_analysis():
    """Test analyzing a single job posting"""
    print("=" * 80)
    print("GEMINI API INTEGRATION TEST - SINGLE JOB ANALYSIS")
    print("=" * 80)
    print()

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable not set")
        print()
        print("Please set your Gemini API key:")
        print("  export GEMINI_API_KEY='your-key-here'")
        print()
        print("Or add it to .env file:")
        print("  GEMINI_API_KEY=your-key-here")
        return False

    print(f"✓ API key found (length: {len(api_key)} chars)")
    print()

    # Get test job
    test_job = REALISTIC_JOB_DESCRIPTIONS[0]
    print(f"Test Job: {test_job['title']} at {test_job['company']}")
    print(f"Location: {test_job['location']}")
    print(f"Description length: {len(test_job['description'])} characters")
    print()

    # Initialize analyzer
    print("Initializing GeminiJobAnalyzer...")
    try:
        analyzer = GeminiJobAnalyzer()
        print("✓ Analyzer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return False

    print()

    # Analyze job
    print("Sending job to Gemini API for analysis...")
    print("(This may take 5-15 seconds)")
    print()

    try:
        # Format job for analyzer (expects list of jobs with id, title, description)
        jobs_input = [{
            'id': test_job['id'],  # REQUIRED
            'title': test_job['title'],  # REQUIRED
            'description': test_job['description'],  # REQUIRED (50-15000 chars)
            'company': test_job['company'],  # optional
            'location': test_job.get('location', 'Not specified')  # optional
        }]

        result = analyzer.analyze_jobs_batch(jobs_input)

        print("=" * 80)
        print("✅ SUCCESS - Gemini returned analysis data")
        print("=" * 80)
        print()

        # Display results
        print("ANALYSIS RESULTS:")
        print("-" * 80)

        if isinstance(result, dict):
            # Pretty print the result
            print(json.dumps(result, indent=2, default=str))

            # Extract first job result if results array exists
            job_result = None
            if 'results' in result and len(result['results']) > 0:
                job_result = result['results'][0]
            elif 'analyzed_jobs' in result and len(result['analyzed_jobs']) > 0:
                job_result = result['analyzed_jobs'][0]
            else:
                job_result = result

            # Check for key fields
            print()
            print("DATA QUALITY CHECK:")
            print("-" * 80)

            if job_result:
                # Check structure
                print(f"✓ Response structure: {list(result.keys())}")
                print(f"✓ Job data keys: {list(job_result.keys()) if isinstance(job_result, dict) else 'N/A'}")

                # Check for meaningful content
                if isinstance(job_result, dict):
                    has_data = any(v for v in job_result.values() if v not in [None, '', [], {}])
                    if has_data:
                        print("✓ Response contains meaningful data")
                    else:
                        print("⚠️  Response structure exists but no meaningful data")
                else:
                    print(f"⚠️  Unexpected job result type: {type(job_result)}")
            else:
                print("⚠️  No job results found in response")

            print()
            print("=" * 80)
            return True

        else:
            print(f"⚠️  Unexpected result type: {type(result)}")
            print(f"Result: {result}")
            return False

    except Exception as e:
        print("=" * 80)
        print("❌ FAILURE - Error during analysis")
        print("=" * 80)
        print()
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print()

        # Print full traceback
        import traceback
        print("Full traceback:")
        print("-" * 80)
        traceback.print_exc()

        return False


def test_batch_analysis():
    """Test analyzing multiple jobs"""
    print()
    print("=" * 80)
    print("GEMINI API INTEGRATION TEST - BATCH ANALYSIS (3 JOBS)")
    print("=" * 80)
    print()

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not set (skipping batch test)")
        return False

    # Get test jobs
    test_jobs = REALISTIC_JOB_DESCRIPTIONS[:3]
    print(f"Testing with {len(test_jobs)} jobs:")
    for i, job in enumerate(test_jobs, 1):
        print(f"  {i}. {job['title']} at {job['company']}")
    print()

    # Initialize analyzer
    try:
        analyzer = GeminiJobAnalyzer()
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return False

    # Analyze batch
    print("Sending batch to Gemini API...")
    print("(This may take 15-30 seconds)")
    print()

    try:
        results = analyzer.analyze_jobs_batch(test_jobs)

        print("=" * 80)
        print(f"✅ SUCCESS - Analyzed {len(results)} jobs")
        print("=" * 80)
        print()

        for i, result in enumerate(results, 1):
            print(f"Job {i}: {result.get('job_title', 'Unknown')}")
            print(f"  Status: {'✓ Analyzed' if result else '✗ Failed'}")
            if result:
                print(f"  Fields: {len(result)} data fields returned")

        return True

    except Exception as e:
        print("=" * 80)
        print("❌ FAILURE - Batch analysis error")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    print("Starting Gemini API Integration Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Test single job
    single_success = test_single_job_analysis()

    # Test batch (only if single succeeded)
    batch_success = False
    if single_success:
        batch_success = test_batch_analysis()

    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Single Job Test: {'✅ PASSED' if single_success else '❌ FAILED'}")
    print(f"Batch Test: {'✅ PASSED' if batch_success else '❌ FAILED' if single_success else '⊘ SKIPPED'}")
    print()

    if single_success and batch_success:
        print("🎉 All tests passed! Gemini integration is working correctly.")
        sys.exit(0)
    elif single_success:
        print("⚠️  Single job works, but batch analysis needs attention.")
        sys.exit(1)
    else:
        print("❌ Critical: Single job analysis is not working.")
        sys.exit(1)
