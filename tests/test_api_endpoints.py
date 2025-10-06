#!/usr/bin/env python3
"""
Quick API Endpoint Testing
Tests specific API endpoints to verify routing and authentication
"""

import requests

def test_endpoint(url, method='GET', data=None, headers=None, expected_status=None):
    """Test a single endpoint and print results"""
    try:
        if method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        status = response.status_code
        print(f"{method} {url}: {status} - {'✅' if (expected_status and status == expected_status) or (not expected_status and status < 400) else '❌'}")
        
        if status == 200:
            try:
                print(f"  Response: {response.json()}")
            except:
                print(f"  Response: {response.text[:100]}...")
        elif status in [401, 403]:
            print(f"  Auth required: {response.text[:100]}...")
        elif status == 404:
            print(f"  Not found: {response.text[:50]}...")
        else:
            print(f"  Error: {response.text[:100]}...")
        print()
        
    except Exception as e:
        print(f"{method} {url}: ERROR - {e}")
        print()

def main():
    base_url = "http://localhost:5000"
    
    print("🔍 Testing API Endpoint Routing")
    print("=" * 50)
    
    # Test basic endpoints
    test_endpoint(f"{base_url}/")
    test_endpoint(f"{base_url}/health")
    test_endpoint(f"{base_url}/dashboard")
    
    # Test API endpoints that should exist
    test_endpoint(f"{base_url}/api/db/health")
    test_endpoint(f"{base_url}/api/link-tracking/health")
    test_endpoint(f"{base_url}/api/ai/usage-stats", expected_status=401)
    test_endpoint(f"{base_url}/api/email/oauth-status", expected_status=401)
    test_endpoint(f"{base_url}/api/user-profile/health", expected_status=401)
    test_endpoint(f"{base_url}/api/workflow/status", expected_status=401)
    
    # Test document generation endpoints
    test_endpoint(f"{base_url}/resume", method='POST', data={'test': 'data'})
    test_endpoint(f"{base_url}/test")
    
    print("=" * 50)
    print("Testing complete")

if __name__ == "__main__":
    main()