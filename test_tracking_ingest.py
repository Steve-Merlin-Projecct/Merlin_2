"""
Quick test script for Tracking Ingest API

This script tests the tracking ingest API endpoints to ensure they work correctly.
Run this after starting the Flask server.

Usage:
    # Start the server first:
    python app_modular.py

    # Then in another terminal:
    python test_tracking_ingest.py
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"
API_KEY = os.getenv("WEBHOOK_API_KEY", "test-api-key-replace-with-real-key")

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def test_health_check():
    """Test the health check endpoint (no auth required)"""
    print_header("Test 1: Health Check (No Authentication)")

    url = f"{BASE_URL}/api/tracking-ingest/health"

    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print("❌ Health check failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_connection():
    """Test the connection endpoint with API key"""
    print_header("Test 2: Test Connection (With Authentication)")

    url = f"{BASE_URL}/api/tracking-ingest/test"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Connection test passed!")
            return True
        else:
            print("❌ Connection test failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_api_key():
    """Test with invalid API key"""
    print_header("Test 3: Invalid API Key (Should Fail)")

    url = f"{BASE_URL}/api/tracking-ingest/test"
    headers = {
        "X-API-Key": "invalid-key-12345",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 401:
            print("✅ Correctly rejected invalid API key!")
            return True
        else:
            print("❌ Should have rejected invalid API key!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_valid_batch():
    """Test with a valid batch of events"""
    print_header("Test 4: Send Valid Batch")

    url = f"{BASE_URL}/api/tracking-ingest/batch"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    # Create test data
    data = {
        "events": [
            {
                "tracking_id": "test-linkedin-" + datetime.utcnow().strftime("%Y%m%d%H%M%S"),
                "clicked_at": datetime.utcnow().isoformat() + "Z",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 Test Agent",
                "referrer_url": "https://test.example.com",
                "click_source": "test-script",
                "metadata": {
                    "test": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            {
                "tracking_id": "test-calendly-" + datetime.utcnow().strftime("%Y%m%d%H%M%S"),
                "clicked_at": datetime.utcnow().isoformat() + "Z",
                "ip_address": "10.0.0.1",
                "user_agent": "Test Agent v2",
                "click_source": "test-script"
            }
        ]
    }

    try:
        print(f"Sending batch with {len(data['events'])} events...")
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        result = response.json()
        if response.status_code in [200, 207] and result.get('results', {}).get('successful', 0) > 0:
            print("✅ Batch processing successful!")
            return True
        else:
            print("❌ Batch processing failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_batch():
    """Test with invalid batch (missing required fields)"""
    print_header("Test 5: Invalid Batch (Missing Required Fields)")

    url = f"{BASE_URL}/api/tracking-ingest/batch"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    # Missing tracking_id (required field)
    data = {
        "events": [
            {
                "clicked_at": datetime.utcnow().isoformat() + "Z",
                "ip_address": "192.168.1.1"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 400:
            print("✅ Correctly rejected invalid batch!")
            return True
        else:
            print("❌ Should have rejected invalid batch!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_minimal_event():
    """Test with minimal event (only tracking_id)"""
    print_header("Test 6: Minimal Event (Only Required Fields)")

    url = f"{BASE_URL}/api/tracking-ingest/batch"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "events": [
            {
                "tracking_id": "minimal-test-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        result = response.json()
        if response.status_code in [200, 207]:
            print("✅ Minimal event accepted!")
            return True
        else:
            print("❌ Minimal event rejected!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  TRACKING INGEST API TEST SUITE")
    print("=" * 80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}... (showing first 10 chars)")
    print("\nIMPORTANT: Make sure the Flask server is running before running tests!")
    print("  Run: python app_modular.py")
    print()

    results = []

    # Run all tests
    results.append(("Health Check", test_health_check()))
    results.append(("Connection Test", test_connection()))
    results.append(("Invalid API Key", test_invalid_api_key()))
    results.append(("Valid Batch", test_valid_batch()))
    results.append(("Invalid Batch", test_invalid_batch()))
    results.append(("Minimal Event", test_minimal_event()))

    # Print summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
