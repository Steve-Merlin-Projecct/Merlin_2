#!/usr/bin/env python3
"""
Quick Single Job Test - No user input required
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from tests.fixtures.realistic_job_descriptions import REALISTIC_JOB_DESCRIPTIONS
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer

# Prepare test job
test_job = REALISTIC_JOB_DESCRIPTIONS[0]
test_job['id'] = 'test_job_001'

print("=" * 80)
print("QUICK SINGLE JOB TEST")
print("=" * 80)
print()
print(f"Job: {test_job['title']}")
print(f"Description length: {len(test_job['description'])} chars")
print()

# Create analyzer
analyzer = GeminiJobAnalyzer()

# Make API call
print("Calling Gemini API...")
result = analyzer.analyze_jobs_batch([test_job])

print()
print("=" * 80)
print("RESULT")
print("=" * 80)
print()
print(f"Success: {result.get('success')}")
print(f"Jobs analyzed: {result.get('jobs_analyzed')}")
print(f"Results count: {len(result.get('results', []))}")
print()

if result.get('results'):
    print("✅ Got analysis results!")
    print()
    print("First result structure:")
    first_result = result['results'][0]
    print(f"  Keys: {list(first_result.keys())}")

    # Save full result
    with open("test_single_job_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print()
    print("Full result saved to: test_single_job_result.json")
else:
    print("❌ No results returned")
    print()
    print("Full response:")
    print(json.dumps(result, indent=2))
