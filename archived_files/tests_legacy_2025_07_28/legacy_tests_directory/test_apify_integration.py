"""
Test script for Apify Indeed scraper integration
Run this to verify the integration works before going live

EDUCATIONAL PURPOSE ONLY:
This test script is designed for educational and research purposes only.
All scraping activities must comply with website Terms of Service and applicable laws.
Use responsibly for learning automation and job search concepts.
"""

import os
import json
from modules.job_scraper_apify import ApifyJobScraper

def test_apify_connection():
    """Test basic Apify API connection"""
    print("Testing Apify connection...")
    
    try:
        # Check if API token is available
        if not os.environ.get('APIFY_TOKEN'):
            print("❌ APIFY_TOKEN not found in environment variables")
            print("Please add your Apify API token to Replit Secrets")
            return False
        
        scraper = ApifyJobScraper()
        print("✅ Apify scraper initialized successfully")
        
        # Test URL generation
        search_url = scraper.create_search_url(
            job_title="Marketing Manager",
            location="Edmonton, AB",
            country="CA"
        )
        print(f"✅ Search URL generated: {search_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_small_scrape():
    """Test scraping a small number of jobs"""
    print("\nTesting job scraping (this may take 1-2 minutes)...")
    
    try:
        scraper = ApifyJobScraper()
        
        # Test with minimal search to avoid costs
        search_configs = [{
            'job_title': 'Marketing',
            'location': 'Edmonton, AB',
            'country': 'CA'
        }]
        
        print("Starting scrape run...")
        run_id = scraper.start_scraping_run(search_configs)
        print(f"✅ Scrape run started: {run_id}")
        
        print("Waiting for completion...")
        success = scraper.wait_for_completion(run_id, max_wait_minutes=5)
        
        if success:
            jobs = scraper.get_scraped_data(run_id)
            print(f"✅ Successfully scraped {len(jobs)} jobs")
            
            if jobs:
                # Show sample job data
                sample_job = jobs[0]
                print(f"Sample job: {sample_job.get('positionName', 'N/A')} at {sample_job.get('company', 'N/A')}")
            
            return True
        else:
            print("❌ Scrape run failed or timed out")
            return False
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return False

def test_data_transformation():
    """Test data transformation with sample data"""
    print("\nTesting data transformation...")
    
    # Sample job data from Apify (based on their documentation)
    sample_raw_job = {
        "positionName": "Marketing Manager",
        "company": "Sample Company",
        "location": "Edmonton, AB",
        "jobkey": "test123",
        "extractedSalary": {
            "min": 65000,
            "max": 85000,
            "type": "yearly"
        },
        "jobType": ["Full-time"],
        "postedAt": "Today",
        "url": "https://ca.indeed.com/viewjob?jk=test123",
        "rating": 4.2,
        "snippet": "We are looking for an experienced marketing manager..."
    }
    
    try:
        scraper = ApifyJobScraper()
        transformed_job = scraper.transform_job_data(sample_raw_job)
        
        print("✅ Data transformation successful")
        print(f"Transformed job: {transformed_job['title']} at {transformed_job['company']}")
        print(f"Salary range: ${transformed_job['salary_low']} - ${transformed_job['salary_high']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in data transformation: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Apify Integration Test Suite")
    print("=" * 40)
    
    tests = [
        ("Connection Test", test_apify_connection),
        ("Data Transformation Test", test_data_transformation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    # Only run scraping test if basic tests pass and user confirms
    if all(result for _, result in results):
        print("\n⚠️  Do you want to run a live scraping test?")
        print("This will use a small amount of your Apify credits (~$0.25)")
        response = input("Enter 'yes' to proceed: ").lower().strip()
        
        if response == 'yes':
            print("\n🧪 Running Live Scraping Test...")
            scrape_result = test_small_scrape()
            results.append(("Live Scraping Test", scrape_result))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Your Apify integration is ready.")
        print("\nNext steps:")
        print("1. Add APIFY_TOKEN to your Replit Secrets")
        print("2. Test with your actual job search criteria")
        print("3. Monitor usage on your Apify dashboard")
    else:
        print("\n⚠️  Some tests failed. Check the errors above and:")
        print("1. Verify your APIFY_TOKEN is correct")
        print("2. Check your Apify account has sufficient credits")
        print("3. Review the integration documentation")

if __name__ == "__main__":
    main()