"""
Test script for the job scraping pipeline
Tests the flow from raw scrapes to cleaned/deduplicated records
"""

import json
import logging
from datetime import datetime
from modules.scraping.scrape_pipeline import ScrapeDataPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pipeline():
    """Test the complete scraping pipeline"""
    pipeline = ScrapeDataPipeline()
    
    # Sample raw job data (similar to what Apify returns)
    sample_jobs = [
        {
            "id": "12345",
            "positionName": "Marketing Manager",
            "companyName": "Tech Innovators Inc.",
            "location": "Edmonton, AB, Canada",
            "salary": "$75,000 - $85,000 annually",
            "description": "Lead marketing initiatives for innovative tech products. Remote work available.",
            "descriptionHTML": "<p>Lead marketing initiatives for innovative tech products. <strong>Remote work available.</strong></p>",
            "companyLogo": "https://example.com/logo.png",
            "reviewsCount": 45,
            "rating": 4.2,
            "jobType": ["Full-time"],
            "postedAt": "2025-01-04T00:00:00Z",
            "isExpired": False,
            "externalApplyLink": "https://ca.indeed.com/viewjob?jk=12345"
        },
        {
            "id": "67890",
            "positionName": "Digital Marketing Specialist",
            "companyName": "Creative Solutions Ltd.",
            "location": "Calgary, AB",
            "salary": "65000-75000 CAD per year",
            "description": "Drive digital marketing campaigns and social media strategy. Hybrid work arrangement.",
            "companyName": "Creative Solutions Ltd.",
            "jobType": ["Full-time", "Permanent"],
            "postedAt": "2025-01-03T00:00:00Z",
            "isExpired": False,
            "externalApplyLink": "https://ca.indeed.com/viewjob?jk=67890"
        },
        # Duplicate job (same external ID)
        {
            "id": "12345",
            "positionName": "Marketing Manager - Updated",
            "companyName": "Tech Innovators Inc.",
            "location": "Edmonton, Alberta, Canada",
            "salary": "$75,000 - $85,000 CAD annually",
            "description": "Lead marketing initiatives for innovative tech products. Remote work available. Updated posting.",
            "postedAt": "2025-01-04T12:00:00Z",
            "isExpired": False,
            "externalApplyLink": "https://ca.indeed.com/viewjob?jk=12345"
        }
    ]
    
    print("Testing Job Scraping Pipeline")
    print("=" * 50)
    
    # Step 1: Insert raw scrapes
    print("\n1. Inserting raw scrape data...")
    scrape_ids = []
    
    for i, job_data in enumerate(sample_jobs):
        source_url = job_data.get('externalApplyLink', f'https://ca.indeed.com/viewjob?jk={job_data.get("id", i)}')
        
        scrape_id = pipeline.insert_raw_scrape(
            source_website='indeed.ca',
            source_url=source_url,
            raw_data=job_data,
            scraper_used='test-scraper',
            scraper_run_id='test-run-001',
            user_agent='TestPipeline/1.0'
        )
        
        scrape_ids.append(scrape_id)
        print(f"   Inserted raw scrape: {scrape_id}")
    
    # Step 2: Process raw scrapes to cleaned
    print("\n2. Processing raw scrapes to cleaned records...")
    results = pipeline.process_raw_scrapes_to_cleaned(batch_size=10)
    
    print(f"   Processed: {results['processed']}")
    print(f"   New cleaned records: {results['cleaned_created']}")
    print(f"   Duplicates merged: {results['duplicates_merged']}")
    
    # Step 3: Get pipeline statistics
    print("\n3. Pipeline Statistics:")
    stats = pipeline.get_pipeline_stats()
    
    for key, value in stats.items():
        if isinstance(value, float) and key != 'processing_rate':
            value = round(value, 4)
        print(f"   {key}: {value}")
    
    # Step 4: Verify data integrity
    print("\n4. Data Integrity Check:")
    
    # Check that raw data was stored correctly
    db = pipeline.db
    raw_count = db.execute_query("SELECT COUNT(*) as count FROM raw_job_scrapes WHERE scraper_run_id = %s", ('test-run-001',))
    print(f"   Raw scrapes stored: {raw_count[0]['count'] if raw_count else 0}")
    
    # Check that cleaned data was created
    cleaned_count = db.execute_query("SELECT COUNT(*) as count FROM cleaned_job_scrapes")
    print(f"   Cleaned records created: {cleaned_count[0]['count'] if cleaned_count else 0}")
    
    # Check for duplicates handling
    duplicate_info = db.execute_query("""
        SELECT external_job_id, duplicates_count, array_length(original_scrape_ids, 1) as scrape_count
        FROM cleaned_job_scrapes 
        WHERE duplicates_count > 1
    """)
    
    if duplicate_info:
        print(f"   Duplicate handling verified:")
        for dup in duplicate_info:
            print(f"     Job ID {dup['external_job_id']}: {dup['duplicates_count']} duplicates, {dup['scrape_count']} raw scrapes")
    
    # Step 5: Sample cleaned data
    print("\n5. Sample Cleaned Data:")
    sample_cleaned = db.execute_query("""
        SELECT job_title, company_name, location_city, location_province, 
               salary_min, salary_max, work_arrangement, confidence_score,
               duplicates_count
        FROM cleaned_job_scrapes 
        LIMIT 3
    """)
    
    if sample_cleaned:
        for job in sample_cleaned:
            print(f"   Job: {job['job_title']} at {job['company_name']}")
            print(f"     Location: {job['location_city']}, {job['location_province']}")
            print(f"     Salary: ${job['salary_min']:,} - ${job['salary_max']:,}" if job['salary_min'] else "     Salary: Not specified")
            print(f"     Work: {job['work_arrangement']}")
            print(f"     Confidence: {job['confidence_score']}")
            print(f"     Duplicates: {job['duplicates_count']}")
            print()
    
    print("Pipeline test completed successfully!")
    return True

def test_data_cleaning():
    """Test specific data cleaning functions"""
    pipeline = ScrapeDataPipeline()
    
    print("\nTesting Data Cleaning Functions")
    print("=" * 50)
    
    # Test location parsing
    locations = [
        "Edmonton, AB, Canada",
        "Calgary, Alberta",
        "Toronto, ON",
        "Remote",
        "Vancouver, BC, Canada"
    ]
    
    print("\nLocation Parsing:")
    for loc in locations:
        parsed = pipeline._parse_location(loc)
        print(f"   '{loc}' -> City: {parsed['location_city']}, Province: {parsed['location_province']}")
    
    # Test salary parsing
    salaries = [
        "$75,000 - $85,000 annually",
        "65000-75000 CAD per year",
        "$25/hour",
        "120k - 150k USD",
        "Competitive salary"
    ]
    
    print("\nSalary Parsing:")
    for sal in salaries:
        parsed = pipeline._parse_salary(sal)
        print(f"   '{sal}' -> ${parsed['salary_min']:,} - ${parsed['salary_max']:,} {parsed['salary_currency']} {parsed['salary_period']}" 
              if parsed['salary_min'] else f"   '{sal}' -> No salary extracted")
    
    # Test work arrangement inference
    descriptions = [
        "Remote work available with flexible hours",
        "Hybrid work environment, 3 days in office",
        "On-site position in downtown office",
        "Work from home opportunity",
        "Flexible work arrangements"
    ]
    
    print("\nWork Arrangement Inference:")
    for desc in descriptions:
        arrangement = pipeline._infer_work_arrangement(desc, "")
        print(f"   '{desc[:40]}...' -> {arrangement}")
    
    return True

def main():
    """Run all pipeline tests"""
    try:
        print("Job Scraping Pipeline Test Suite")
        print("=" * 60)
        
        # Test data cleaning functions
        test_data_cleaning()
        
        # Test complete pipeline
        test_pipeline()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\nTest failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()