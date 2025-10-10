#!/usr/bin/env python3
"""
Test script for Sentence Variation Generator

Usage:
    python test_sentence_variation.py
"""

import json
import requests

# Test seed sentences for Marketing Automation Manager position
SEED_SENTENCES = [
    {
        "content_text": "Led comprehensive rebranding initiative for 14-year-old media company, modernizing visual identity and messaging strategy",
        "tone": "Confident",
        "category": "Leadership",
        "intended_document": "resume",
        "position_label": "Marketing Automation Manager",
        "matches_job_skill": "Brand Management"
    },
    {
        "content_text": "Managed editorial calendar and content distribution across multiple digital platforms, increasing engagement 35%",
        "tone": "Confident",
        "category": "Achievement",
        "intended_document": "resume",
        "position_label": "Marketing Automation Manager",
        "matches_job_skill": "Content Marketing"
    },
    {
        "content_text": "Your company's innovative approach to marketing automation immediately caught my attention",
        "tone": "Curious",
        "category": "Opening",
        "intended_document": "cover_letter",
        "position_label": "Marketing Automation Manager",
        "matches_job_skill": "Marketing Automation"
    }
]


def test_generate_variations():
    """Test the sentence variation generation endpoint"""

    url = "http://localhost:5000/api/sentence-variations/generate"

    payload = {
        "seed_sentences": SEED_SENTENCES,
        "variations_per_seed": 5,  # Generate 5 variations per seed for testing
        "target_position": "Marketing Automation Manager",
        "output_format": "json"
    }

    print("Testing Sentence Variation Generator API")
    print("=" * 60)
    print(f"\nSending {len(SEED_SENTENCES)} seed sentences...")
    print(f"Requesting 5 variations per seed")
    print(f"Target position: Marketing Automation Manager\n")

    try:
        response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()

            print("✓ SUCCESS!")
            print(f"\nGenerated {len(result['variations'])} total variations")
            print(f"\nStats:")
            print(f"  - Total seeds: {result['stats']['total_seeds']}")
            print(f"  - Variations per seed: {result['stats']['variations_per_seed']}")
            print(f"  - Total generated: {result['stats']['total_generated']}")
            print(f"  - Successful: {result['stats']['successful_seeds']}")
            print(f"  - Failed: {result['stats']['failed_seeds']}")

            print(f"\n{'=' * 60}")
            print("SAMPLE VARIATIONS (First 3):")
            print('=' * 60)

            for i, variation in enumerate(result['variations'][:3], 1):
                print(f"\n{i}. {variation['content_text']}")
                print(f"   Tone: {variation['tone']} (Strength: {variation['tone_strength']})")
                print(f"   Category: {variation['category']}")
                print(f"   Length: {variation['length']}")
                print(f"   Seed: {variation['seed_sentence'][:60]}...")

            # Save full results to file
            with open('variation_results.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n✓ Full results saved to variation_results.json")

            return True

        else:
            print(f"✗ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to Flask server")
        print("Make sure the server is running: flask run or python app_modular.py")
        return False

    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False


def test_health_check():
    """Test the health check endpoint"""

    url = "http://localhost:5000/api/sentence-variations/health"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print("\nHealth Check:")
            print(f"  Status: {result['status']}")
            print(f"  Gemini Configured: {result['gemini_configured']}")
            print(f"  Model: {result['model']}")
            return True
        else:
            print(f"\n✗ Health check failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"\n✗ Health check error: {str(e)}")
        return False


def test_csv_output():
    """Test CSV format output"""

    url = "http://localhost:5000/api/sentence-variations/generate"

    payload = {
        "seed_sentences": [SEED_SENTENCES[0]],  # Just one seed for CSV test
        "variations_per_seed": 3,
        "target_position": "Marketing Automation Manager",
        "output_format": "csv"
    }

    print("\n" + "=" * 60)
    print("Testing CSV Output Format")
    print("=" * 60)

    try:
        response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            csv_content = response.text

            # Save to file
            with open('variations_output.csv', 'w') as f:
                f.write(csv_content)

            print("✓ CSV generated successfully")
            print(f"✓ Saved to variations_output.csv")
            print(f"\nFirst 500 characters:")
            print(csv_content[:500])

            return True
        else:
            print(f"✗ CSV generation failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ CSV test error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SENTENCE VARIATION GENERATOR TEST SUITE")
    print("=" * 60)

    # Run tests
    health_ok = test_health_check()

    if health_ok:
        json_ok = test_generate_variations()
        csv_ok = test_csv_output()

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Health Check: {'✓ PASS' if health_ok else '✗ FAIL'}")
        print(f"JSON Output:  {'✓ PASS' if json_ok else '✗ FAIL'}")
        print(f"CSV Output:   {'✓ PASS' if csv_ok else '✗ FAIL'}")
        print("=" * 60)
    else:
        print("\n✗ Health check failed - skipping other tests")
        print("Please ensure:")
        print("  1. Flask server is running")
        print("  2. GEMINI_API_KEY is set in .env file")
