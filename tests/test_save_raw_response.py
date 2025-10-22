#!/usr/bin/env python3
"""
Test that saves raw Gemini response for inspection
"""

import os
import sys
import json
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from tests.fixtures.realistic_job_descriptions import REALISTIC_JOB_DESCRIPTIONS
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt

# Prepare test job
test_job = REALISTIC_JOB_DESCRIPTIONS[0]
test_job['id'] = 'test_job_001'

print("=" * 80)
print("SAVE RAW GEMINI RESPONSE TEST")
print("=" * 80)
print()

# Create prompt
prompt = create_tier1_core_prompt([test_job])
print(f"Prompt length: {len(prompt)} chars (~{len(prompt)//4} tokens)")
print()

# API configuration
api_key = os.environ.get("GEMINI_API_KEY")
base_url = "https://generativelanguage.googleapis.com"
model = "gemini-2.0-flash-001"

# Make API call
api_endpoint = f"{base_url}/v1beta/models/{model}:generateContent?key={api_key}"

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "temperature": 0.1,
        "topK": 1,
        "topP": 0.8,
        "maxOutputTokens": 3000,  # Reduced limit
        "responseMimeType": "application/json",
    },
}

print("Making API request...")
response = requests.post(api_endpoint, json=payload, timeout=60)

print(f"Response status: {response.status_code}")
print()

if response.status_code == 200:
    raw_response = response.json()

    # Save full raw response
    with open("raw_gemini_response.json", "w") as f:
        json.dump(raw_response, f, indent=2)
    print("✅ Full raw response saved to: raw_gemini_response.json")
    print()

    # Extract text
    try:
        text = raw_response["candidates"][0]["content"]["parts"][0]["text"]

        print(f"Response text length: {len(text)} chars")
        print()

        # Save text separately
        with open("raw_gemini_response_text.txt", "w") as f:
            f.write(text)
        print("✅ Response text saved to: raw_gemini_response_text.txt")
        print()

        # Try to parse as JSON
        try:
            parsed = json.loads(text)
            print("✅ Response is valid JSON!")
            print()
            print(f"Top-level keys: {list(parsed.keys())}")

        except json.JSONDecodeError as e:
            print(f"❌ JSON PARSE ERROR: {e}")
            print()
            print(f"Error at line {e.lineno}, column {e.colno}, position {e.pos}")
            print()

            # Show context around error
            if e.pos:
                start = max(0, e.pos - 200)
                end = min(len(text), e.pos + 200)
                print("CONTEXT AROUND ERROR:")
                print("-" * 80)
                print(text[start:e.pos] + " <<< ERROR HERE >>> " + text[e.pos:end])
                print()

        # Show first and last 500 chars
        print("RESPONSE PREVIEW (first 500 chars):")
        print("-" * 80)
        print(text[:500])
        print()

        if len(text) > 500:
            print("RESPONSE PREVIEW (last 500 chars):")
            print("-" * 80)
            print(text[-500:])
            print()

    except Exception as e:
        print(f"❌ Error extracting text: {e}")

else:
    print(f"❌ API Error: {response.status_code}")
    print(response.text)
