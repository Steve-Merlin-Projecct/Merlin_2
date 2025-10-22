#!/usr/bin/env python3
"""
Module: analyze_prompt_and_response.py
Purpose: Analyze Gemini API prompt and response quality for debugging
Created: 2024-09-20
Modified: 2025-10-21
Dependencies: None (standard library only)
Related: modules/ai_job_description_analysis/, register_canonical_prompts.py
Description: Examines prompts sent to Gemini, raw responses received, JSON
             validation issues, and differences between canonical/used prompts.
             Useful for debugging AI integration issues.

Usage:
    python analyze_prompt_and_response.py
"""

import os
import sys
import json
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from tests.fixtures.realistic_job_descriptions import REALISTIC_JOB_DESCRIPTIONS
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer


def analyze_prompt_structure():
    """Analyze the prompt being sent to Gemini"""
    print("=" * 80)
    print("ANALYSIS: PROMPT STRUCTURE")
    print("=" * 80)
    print()

    # Create test job
    test_job = REALISTIC_JOB_DESCRIPTIONS[0]
    test_job['id'] = test_job.get('id', 'test_job_001')

    print("Generating prompt with create_tier1_core_prompt()...")
    prompt = create_tier1_core_prompt([test_job])

    print()
    print("PROMPT STATISTICS:")
    print("-" * 80)
    print(f"Total length: {len(prompt)} characters")
    print(f"Total length: {len(prompt.split())} words")
    print(f"Estimated tokens: ~{len(prompt) // 4}")
    print()

    # Check JSON format instructions
    print("JSON FORMAT INSTRUCTIONS:")
    print("-" * 80)
    if '"security_token":' in prompt:
        print("✅ Includes security_token field in example JSON")
    else:
        print("❌ Missing security_token field in example JSON")

    if '"analysis_results":' in prompt:
        print("✅ Includes analysis_results array in example JSON")
    else:
        print("❌ Missing analysis_results array in example JSON")

    if 'Respond with ONLY the JSON structure' in prompt:
        print("✅ Instructs to return ONLY JSON")
    else:
        print("⚠️  May not clearly specify JSON-only response")

    print()

    # Check for potential issues
    print("POTENTIAL ISSUES:")
    print("-" * 80)

    # Look for unescaped quotes or problematic characters
    issues = []

    if prompt.count('{') != prompt.count('}'):
        issues.append("⚠️  Unbalanced curly braces in prompt")

    if prompt.count('[') != prompt.count(']'):
        issues.append("⚠️  Unbalanced square brackets in prompt")

    # Check if example JSON is valid
    try:
        # Extract the example JSON from prompt
        start = prompt.find('{"security_token":')
        if start != -1:
            # Find the end of the JSON example (before "ANALYSIS GUIDELINES:")
            end = prompt.find('\n\n', start)
            if end != -1:
                example_json = prompt[start:end].strip()
                # Replace placeholder with actual value
                example_json = example_json.replace('"{security_token}"', '"PLACEHOLDER"')
                json.loads(example_json)
                print("✅ Example JSON in prompt is valid")
            else:
                issues.append("⚠️  Cannot find end of example JSON")
        else:
            issues.append("❌ No example JSON found in prompt")
    except json.JSONDecodeError as e:
        issues.append(f"❌ Example JSON in prompt is INVALID: {e}")

    if not issues:
        print("✅ No obvious issues detected")
    else:
        for issue in issues:
            print(issue)

    print()

    # Show sample of prompt
    print("PROMPT PREVIEW (first 1000 chars):")
    print("-" * 80)
    print(prompt[:1000])
    print("...")
    print()

    print("PROMPT PREVIEW (last 500 chars):")
    print("-" * 80)
    print("..." + prompt[-500:])
    print()

    return prompt


def test_actual_api_call_with_inspection():
    """Make actual API call and inspect the raw response"""
    print("=" * 80)
    print("ANALYSIS: ACTUAL API CALL & RESPONSE")
    print("=" * 80)
    print()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⊘ SKIPPED - GEMINI_API_KEY not set")
        return None

    # Prepare test job
    test_job = REALISTIC_JOB_DESCRIPTIONS[0]
    test_job['id'] = test_job.get('id', 'test_job_001')

    print(f"Test job: {test_job['title']}")
    print()

    # Create analyzer and prompt
    analyzer = GeminiJobAnalyzer()

    # Get the actual prompt that will be sent
    prompt = analyzer._create_batch_analysis_prompt([test_job])

    print("SENDING TO GEMINI:")
    print("-" * 80)
    print(f"Prompt length: {len(prompt)} chars (~{len(prompt)//4} tokens)")
    print(f"Model: {analyzer.current_model}")
    print()

    # Make direct API request to inspect raw response
    try:
        import requests

        api_url = f"{analyzer.base_url}/v1beta/models/{analyzer.current_model}:generateContent?key={analyzer.api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 1,
                "topP": 0.8,
                "maxOutputTokens": 4096,  # Current default
                "responseMimeType": "application/json",
            },
        }

        print("Making API request...")
        response = requests.post(api_url, json=payload, timeout=30)

        print(f"Response status: {response.status_code}")
        print()

        if response.status_code == 200:
            raw_response = response.json()

            # Save raw response
            with open("gemini_raw_response.json", "w") as f:
                json.dump(raw_response, f, indent=2)
            print("✅ Raw response saved to: gemini_raw_response.json")
            print()

            # Extract the actual text response
            try:
                content = raw_response.get("candidates", [{}])[0].get("content", {})
                text = content.get("parts", [{}])[0].get("text", "")

                print("RESPONSE ANALYSIS:")
                print("-" * 80)
                print(f"Response length: {len(text)} characters")
                print()

                # Try to parse as JSON
                print("JSON VALIDATION:")
                print("-" * 80)
                try:
                    parsed = json.loads(text)
                    print("✅ Response is valid JSON")
                    print()
                    print("Response structure:")
                    print(f"  Top-level keys: {list(parsed.keys())}")

                    if "analysis_results" in parsed:
                        results = parsed["analysis_results"]
                        print(f"  Analysis results count: {len(results)}")
                        if results:
                            print(f"  First result keys: {list(results[0].keys())}")

                    # Save parsed response
                    with open("gemini_parsed_response.json", "w") as f:
                        json.dump(parsed, f, indent=2)
                    print()
                    print("✅ Parsed response saved to: gemini_parsed_response.json")

                except json.JSONDecodeError as e:
                    print(f"❌ JSON PARSE ERROR: {e}")
                    print()
                    print("ERROR DETAILS:")
                    print(f"  Line: {e.lineno}")
                    print(f"  Column: {e.colno}")
                    print(f"  Position: {e.pos}")
                    print()

                    # Show context around error
                    if e.pos:
                        start = max(0, e.pos - 200)
                        end = min(len(text), e.pos + 200)
                        print("CONTEXT AROUND ERROR:")
                        print("-" * 80)
                        print(text[start:e.pos] + " <<< ERROR HERE >>> " + text[e.pos:end])
                        print()

                    # Save problematic response for inspection
                    with open("gemini_malformed_response.txt", "w") as f:
                        f.write(text)
                    print("❌ Malformed response saved to: gemini_malformed_response.txt")
                    print()

                # Show sample
                print("RESPONSE PREVIEW (first 1000 chars):")
                print("-" * 80)
                print(text[:1000])
                print("...")
                print()

                if len(text) > 1000:
                    print("RESPONSE PREVIEW (last 500 chars):")
                    print("-" * 80)
                    print("..." + text[-500:])
                    print()

            except Exception as e:
                print(f"❌ Error extracting response text: {e}")

        elif response.status_code == 503:
            print("⚠️  Model overloaded (503) - try again later")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()


def compare_prompt_hashes():
    """Compare hash of canonical vs actual prompt"""
    print("=" * 80)
    print("ANALYSIS: PROMPT HASH COMPARISON")
    print("=" * 80)
    print()

    test_job = REALISTIC_JOB_DESCRIPTIONS[0]
    test_job['id'] = 'test_job_001'

    # Generate prompt twice
    prompt1 = create_tier1_core_prompt([test_job])
    prompt2 = create_tier1_core_prompt([test_job])

    hash1 = hashlib.sha256(prompt1.encode()).hexdigest()[:12]
    hash2 = hashlib.sha256(prompt2.encode()).hexdigest()[:12]

    print("HASH COMPARISON:")
    print("-" * 80)
    print(f"First generation:  {hash1}")
    print(f"Second generation: {hash2}")
    print()

    if hash1 == hash2:
        print("✅ Hashes are IDENTICAL - prompt is deterministic")
    else:
        print("⚠️  Hashes are DIFFERENT - prompt contains random elements")
        print()
        print("REASON: Security token is randomly generated per call")
        print("This is why hash mismatch warnings appear!")
        print()
        print("IMPLICATION:")
        print("  The security manager cannot detect 'unauthorized changes'")
        print("  because every prompt has a different hash due to random token.")


if __name__ == "__main__":
    print()
    print("GEMINI PROMPT & RESPONSE ANALYSIS")
    print("=" * 80)
    print()

    # Part 1: Analyze prompt structure
    prompt = analyze_prompt_structure()

    # Part 2: Compare hashes
    compare_prompt_hashes()

    # Part 3: Make actual API call and inspect response
    print()
    input("Press ENTER to make actual Gemini API call (or Ctrl+C to skip)...")
    print()
    test_actual_api_call_with_inspection()

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Files generated:")
    print("  - gemini_raw_response.json (if successful)")
    print("  - gemini_parsed_response.json (if valid JSON)")
    print("  - gemini_malformed_response.txt (if JSON invalid)")
    print()
