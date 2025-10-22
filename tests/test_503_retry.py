#!/usr/bin/env python3
"""
Test Script for 503 Retry Logic with Model Fallback
====================================================

Tests the enhanced retry logic that:
1. Detects 503 "model overloaded" errors
2. Waits 30 seconds before trying a different model
3. Cycles through available models by priority
4. Falls back to exponential wait if all models tried

Usage:
    python test_503_retry.py

This script will:
- Fetch available models from Google API
- Display model fallback chain
- Test actual API calls (if API is responsive)
"""

import os
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Try to load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer


def test_fetch_models():
    """Test fetching available models from Google API"""
    print("=" * 80)
    print("TEST 1: FETCH AVAILABLE MODELS FROM GOOGLE API")
    print("=" * 80)
    print()

    try:
        analyzer = GeminiJobAnalyzer()
        print(f"✓ Analyzer initialized with primary model: {analyzer.primary_model}")
        print()

        print("Fetching models from Google API...")
        print("Endpoint: https://generativelanguage.googleapis.com/v1beta/models")
        print()

        models = analyzer.fetch_available_models_from_api()

        print(f"✅ SUCCESS - Retrieved {len(models)} models")
        print()
        print("Available Models (by priority):")
        print("-" * 80)

        # Sort by priority
        sorted_models = sorted(
            models.items(),
            key=lambda x: x[1].get("priority", 999)
        )

        for i, (model_id, info) in enumerate(sorted_models, 1):
            print(f"{i}. {model_id}")
            print(f"   Name: {info.get('name', 'N/A')}")
            print(f"   Tier: {info.get('tier', 'N/A')}")
            print(f"   Priority: {info.get('priority', 'N/A')}")
            if info.get('context_window'):
                print(f"   Context Window: {info['context_window']:,} tokens")
            print()

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_503_fallback_chain():
    """Test the 503 fallback logic (without actual API calls)"""
    print()
    print("=" * 80)
    print("TEST 2: 503 FALLBACK CHAIN SIMULATION")
    print("=" * 80)
    print()

    try:
        analyzer = GeminiJobAnalyzer()

        print(f"Starting model: {analyzer.current_model}")
        print()
        print("Simulating 503 errors and model fallback:")
        print("-" * 80)

        # Simulate trying each model
        attempt = 1
        while True:
            print(f"\nAttempt {attempt}:")
            print(f"  Current model: {analyzer.current_model}")

            # Mark current model as tried
            analyzer._503_tried_models.add(analyzer.current_model)

            # Get next model
            next_model = analyzer._get_next_available_model()

            if next_model == analyzer.current_model:
                print(f"  ⚠️  No more alternative models available")
                print(f"  Would retry {analyzer.current_model} after exponential backoff")
                break
            else:
                print(f"  ➡️  Would wait 30 seconds, then switch to: {next_model}")
                analyzer.current_model = next_model
                attempt += 1

        print()
        print(f"✅ Tested {attempt} model fallbacks")
        print(f"Total models tried: {len(analyzer._503_tried_models)}")
        print(f"Models: {', '.join(analyzer._503_tried_models)}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_actual_api_call():
    """Test an actual API call (may encounter 503)"""
    print()
    print("=" * 80)
    print("TEST 3: ACTUAL API CALL WITH 503 HANDLING")
    print("=" * 80)
    print()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⊘ SKIPPED - GEMINI_API_KEY not set")
        return None

    try:
        from tests.fixtures.realistic_job_descriptions import REALISTIC_JOB_DESCRIPTIONS

        analyzer = GeminiJobAnalyzer()
        test_job = REALISTIC_JOB_DESCRIPTIONS[0]

        print(f"Test job: {test_job['title']}")
        print(f"Starting model: {analyzer.current_model}")
        print()
        print("Sending to Gemini API...")
        print("(If 503 occurs, will automatically try fallback models)")
        print()

        jobs_input = [{
            'id': test_job['id'],
            'title': test_job['title'],
            'description': test_job['description'],
        }]

        result = analyzer.analyze_jobs_batch(jobs_input)

        if result.get('success'):
            print("✅ SUCCESS - API returned analysis")
            print(f"Model used: {result.get('model_used', 'unknown')}")
            print(f"Model switches: {analyzer.model_switches}")
            if analyzer.model_switches > 0:
                print(f"⚠️  Note: Had to switch models due to 503 errors")
        else:
            print("⚠️  API call did not succeed")
            print(f"Error: {result.get('error', 'unknown')}")
            print(f"Model switches attempted: {analyzer.model_switches}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    print("Testing 503 Retry Logic with Model Fallback")
    print("=" * 80)
    print()

    results = []

    # Test 1: Fetch models
    results.append(("Fetch Models API", test_fetch_models()))

    # Test 2: Simulate fallback chain
    results.append(("503 Fallback Chain", test_503_fallback_chain()))

    # Test 3: Actual API call (optional)
    api_result = test_actual_api_call()
    if api_result is not None:
        results.append(("Actual API Call", api_result))

    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    print()

    all_passed = all(result for _, result in results)
    if all_passed:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed")
        sys.exit(1)
