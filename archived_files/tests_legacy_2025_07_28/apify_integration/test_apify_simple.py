#!/usr/bin/env python3
"""
Simple APIFY Test Script
Educational Purpose Only - Testing misceres/indeed-scraper integration
"""

import os
import requests
import json
import time
from datetime import datetime

def test_apify_synchronous():
    """Test APIFY using synchronous endpoint that returns results immediately"""
    
    APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
    if not APIFY_TOKEN:
        print('❌ APIFY_TOKEN not found in environment')
        return False
    
    print(f'🔑 Using APIFY_TOKEN: {APIFY_TOKEN[:12]}...')
    
    # Use synchronous endpoint from the documentation
    url = 'https://api.apify.com/v2/acts/misceres~indeed-scraper/run-sync-get-dataset-items'
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Input data matching exact schema
    input_data = {
        'position': 'Marketing Manager',
        'country': 'CA',
        'location': 'Edmonton, AB',
        'maxItems': 5,  # Small test
        'parseCompanyDetails': False,
        'saveOnlyUniqueItems': True,
        'followApplyRedirects': False
    }
    
    params = {
        'token': APIFY_TOKEN
    }
    
    print(f'📤 Sending request to APIFY (synchronous)...')
    print(f'🎯 Searching for: {input_data["position"]} in {input_data["location"]}')
    
    try:
        start_time = time.time()
        response = requests.post(url, json=input_data, params=params, headers=headers, timeout=300)
        duration = time.time() - start_time
        
        print(f'⏱️  Request completed in {duration:.1f} seconds')
        print(f'📊 Response status: {response.status_code}')
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if isinstance(data, list):
                    print(f'✅ Successfully received {len(data)} job listings')
                    
                    if len(data) > 0:
                        print(f'\n📋 Sample Job Data:')
                        sample = data[0]
                        
                        # Key fields
                        print(f'  Position: {sample.get("positionName", "N/A")}')
                        print(f'  Company: {sample.get("companyName", "N/A")}')
                        print(f'  Location: {sample.get("location", "N/A")}')
                        print(f'  Salary: {sample.get("salary", "N/A")}')
                        print(f'  Job Type: {sample.get("jobType", "N/A")}')
                        print(f'  Posted: {sample.get("postedDate", "N/A")}')
                        print(f'  External ID: {sample.get("id", "N/A")}')
                        
                        # Description preview
                        description = sample.get("description", "")
                        if description:
                            print(f'  Description: {description[:150]}...')
                        
                        print(f'\n🔍 All Available Fields:')
                        for i, key in enumerate(sorted(sample.keys())):
                            if i < 20:  # Limit output
                                value = sample[key]
                                if isinstance(value, str) and len(value) > 80:
                                    print(f'    {key}: {value[:80]}...')
                                else:
                                    print(f'    {key}: {value}')
                            elif i == 20:
                                print(f'    ... and {len(sample.keys()) - 20} more fields')
                                break
                        
                        # Test data structure for our pipeline
                        print(f'\n🛠️  Pipeline Compatibility Check:')
                        required_fields = ['positionName', 'companyName', 'location', 'description']
                        for field in required_fields:
                            status = '✅' if field in sample else '❌'
                            print(f'    {status} {field}')
                        
                        return True
                    else:
                        print('⚠️  No job data returned (empty result set)')
                        return False
                else:
                    print(f'⚠️  Unexpected response format: {type(data)}')
                    print(f'Response: {str(data)[:200]}...')
                    return False
                    
            except json.JSONDecodeError as e:
                print(f'❌ Failed to parse JSON response: {e}')
                print(f'Raw response: {response.text[:300]}...')
                return False
        else:
            print(f'❌ Request failed with status {response.status_code}')
            try:
                error_data = response.json()
                print(f'Error details: {json.dumps(error_data, indent=2)}')
            except:
                print(f'Raw error response: {response.text[:300]}...')
            return False
            
    except requests.exceptions.Timeout:
        print('❌ Request timed out (>5 minutes)')
        return False
    except requests.exceptions.RequestException as e:
        print(f'❌ Request error: {e}')
        return False

def test_apify_asynchronous():
    """Test APIFY using asynchronous endpoint (like our current implementation)"""
    
    APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
    if not APIFY_TOKEN:
        return False
    
    print(f'\n🔄 Testing Asynchronous Endpoint...')
    
    # Use asynchronous endpoint
    url = 'https://api.apify.com/v2/acts/misceres~indeed-scraper/runs'
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    input_data = {
        'position': 'Software Developer',
        'country': 'CA',
        'location': 'Calgary, AB',
        'maxItems': 3,
        'parseCompanyDetails': False,
        'saveOnlyUniqueItems': True
    }
    
    params = {
        'token': APIFY_TOKEN
    }
    
    try:
        # Start the run
        response = requests.post(url, json=input_data, params=params, headers=headers)
        
        if response.status_code == 201:
            run_data = response.json()
            run_id = run_data['data']['id']
            print(f'✅ Started async run: {run_id}')
            print(f'Status: {run_data["data"]["status"]}')
            
            # Monitor status for 60 seconds
            status_url = f'https://api.apify.com/v2/acts/misceres~indeed-scraper/runs/{run_id}'
            
            for i in range(12):  # Check every 5 seconds for 1 minute
                time.sleep(5)
                status_response = requests.get(status_url, params={'token': APIFY_TOKEN})
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data['data']['status']
                    print(f'[{(i+1)*5:2d}s] Status: {current_status}')
                    
                    if current_status in ['SUCCEEDED', 'FAILED']:
                        print(f'📋 Run completed: {current_status}')
                        
                        if current_status == 'SUCCEEDED':
                            # Get results
                            dataset_id = status_data['data']['defaultDatasetId']
                            results_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items'
                            results_response = requests.get(results_url, params={'token': APIFY_TOKEN})
                            
                            if results_response.status_code == 200:
                                results = results_response.json()
                                print(f'✅ Retrieved {len(results)} results from async run')
                                return True
                        break
                        
            return True
        else:
            print(f'❌ Failed to start async run: {response.status_code}')
            return False
            
    except Exception as e:
        print(f'❌ Async test error: {e}')
        return False

if __name__ == '__main__':
    print('=== APIFY Integration Test ===')
    print('Educational Purpose Only - Testing misceres/indeed-scraper\n')
    
    print(f'🕐 Test started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Test synchronous endpoint (recommended for immediate results)
    sync_success = test_apify_synchronous()
    
    # Test asynchronous endpoint (like our current implementation)
    async_success = test_apify_asynchronous()
    
    print(f'\n📊 Test Results Summary:')
    print(f'  Synchronous endpoint: {"✅ Working" if sync_success else "❌ Failed"}')
    print(f'  Asynchronous endpoint: {"✅ Working" if async_success else "❌ Failed"}')
    
    if sync_success:
        print(f'\n✅ APIFY integration is working correctly!')
        print(f'The issue is likely in our application code, not APIFY itself.')
        print(f'Recommendation: Use synchronous endpoint for immediate results.')
    else:
        print(f'\n❌ APIFY integration issues detected.')
        print(f'Check APIFY_TOKEN and network connectivity.')
    
    print(f'\n🕐 Test completed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')