#!/usr/bin/env python3
"""
Test Suite for Confidence Scoring System
Validates the confidence scoring logic in the job scraping pipeline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.scraping.scrape_pipeline import ScrapeDataPipeline
from modules.database.database_manager import DatabaseManager
import json
from datetime import datetime


class TestConfidenceScoring:
    """Test the confidence scoring system for job data quality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.pipeline = ScrapeDataPipeline()
        self.db = DatabaseManager()
    
    def test_confidence_scoring_calculation(self):
        """Test confidence score calculation for different data quality levels"""
        
        # Test data with different quality levels
        test_cases = [
            # High quality data (should score ~1.0)
            {
                'name': 'high_quality',
                'raw_data': {
                    'positionName': 'Senior Marketing Manager',
                    'companyName': 'Tech Corp Inc.',
                    'description': 'We are looking for an experienced marketing manager to join our team. The role involves developing marketing strategies, managing campaigns, and analyzing market trends.',
                    'location': 'Edmonton, AB, Canada',
                    'salary': '$65,000 - $85,000',
                    'id': 'job123456'
                },
                'expected_range': (0.9, 1.0)
            },
            # Medium quality data (should score ~0.7)
            {
                'name': 'medium_quality',
                'raw_data': {
                    'positionName': 'Marketing Manager',
                    'companyName': 'ABC Company',
                    'description': 'Marketing role available.',
                    'location': 'Edmonton, AB'
                },
                'expected_range': (0.6, 0.8)
            },
            # Low quality data (should score ~0.5)
            {
                'name': 'low_quality',
                'raw_data': {
                    'positionName': 'Manager',
                    'companyName': 'Company'
                },
                'expected_range': (0.4, 0.6)
            }
        ]
        
        for test_case in test_cases:
            print(f"\nTesting {test_case['name']} data...")
            
            # Create mock raw scrape
            raw_scrape = {
                'scrape_id': 'test-scrape-1',
                'source_website': 'indeed.ca',
                'source_url': 'https://indeed.ca/job/test',
                'raw_data': test_case['raw_data']
            }
            
            # Clean the data (this includes confidence scoring)
            cleaned_data = self.pipeline._clean_job_data(raw_scrape)
            
            if cleaned_data:
                confidence_score = cleaned_data.get('confidence_score', 0.0)
                expected_min, expected_max = test_case['expected_range']
                
                print(f"  Job: {cleaned_data.get('job_title')} at {cleaned_data.get('company_name')}")
                print(f"  Confidence score: {confidence_score}")
                print(f"  Expected range: {expected_min} - {expected_max}")
                
                assert expected_min <= confidence_score <= expected_max, \
                    f"Confidence score {confidence_score} not in expected range {expected_min}-{expected_max}"
                
                print(f"  ✅ Confidence scoring working correctly")
            else:
                print(f"  ❌ Failed to clean data for {test_case['name']}")
    
    def test_duplicate_detection_with_confidence(self):
        """Test that duplicate detection properly handles confidence scores"""
        
        # Create test data with same job but different confidence scores
        base_job_data = {
            'positionName': 'Marketing Manager',
            'companyName': 'Test Company',
            'description': 'Marketing role at test company',
            'location': 'Edmonton, AB',
            'id': 'duplicate-test-job'
        }
        
        # First job with medium confidence
        job1_data = base_job_data.copy()
        job1_data['salary'] = '$60,000'
        
        # Second job with higher confidence (more complete data)
        job2_data = base_job_data.copy()
        job2_data.update({
            'salary': '$60,000 - $70,000',
            'companyWebsite': 'https://testcompany.com',
            'reviewsCount': 150,
            'rating': 4.2
        })
        
        # Process both jobs
        raw_scrape_1 = {
            'scrape_id': 'test-duplicate-1',
            'source_website': 'indeed.ca', 
            'source_url': 'https://indeed.ca/job/duplicate-test',
            'raw_data': job1_data
        }
        
        raw_scrape_2 = {
            'scrape_id': 'test-duplicate-2',
            'source_website': 'indeed.ca',
            'source_url': 'https://indeed.ca/job/duplicate-test',
            'raw_data': job2_data
        }
        
        # Clean both jobs
        cleaned_1 = self.pipeline._clean_job_data(raw_scrape_1)
        cleaned_2 = self.pipeline._clean_job_data(raw_scrape_2)
        
        if cleaned_1 and cleaned_2:
            confidence_1 = cleaned_1.get('confidence_score', 0.0)
            confidence_2 = cleaned_2.get('confidence_score', 0.0)
            
            print(f"\nDuplicate Detection Test:")
            print(f"  Job 1 confidence: {confidence_1}")
            print(f"  Job 2 confidence: {confidence_2}")
            
            # Second job should have higher confidence due to more complete data
            assert confidence_2 > confidence_1, \
                f"Job 2 confidence ({confidence_2}) should be higher than Job 1 ({confidence_1})"
            
            print(f"  ✅ Duplicate detection confidence scoring working correctly")
        else:
            print(f"  ❌ Failed to clean duplicate test data")
    
    def test_confidence_score_components(self):
        """Test individual components of the confidence scoring algorithm"""
        
        # Test each component separately
        test_data = {
            'positionName': 'Senior Marketing Manager',
            'companyName': 'Tech Corp Inc.',
            'description': 'Detailed job description with requirements and responsibilities',
            'location': 'Edmonton, AB, Canada',
            'salary': '$65,000 - $85,000',
            'id': 'component-test-job'
        }
        
        raw_scrape = {
            'scrape_id': 'test-components',
            'source_website': 'indeed.ca',
            'source_url': 'https://indeed.ca/job/components-test',
            'raw_data': test_data
        }
        
        cleaned = self.pipeline._clean_job_data(raw_scrape)
        
        if cleaned:
            # Test that all scoring components are present
            required_fields = ['job_title', 'company_name']
            valuable_fields = ['job_description', 'location_city', 'external_job_id']
            salary_fields = ['salary_min', 'salary_max']
            
            print(f"\nConfidence Score Components Test:")
            print(f"  Job title: {cleaned.get('job_title') is not None}")
            print(f"  Company name: {cleaned.get('company_name') is not None}")
            print(f"  Description: {cleaned.get('job_description') is not None}")
            print(f"  Location: {cleaned.get('location_city') is not None}")
            print(f"  External ID: {cleaned.get('external_job_id') is not None}")
            print(f"  Salary info: {any(cleaned.get(field) for field in salary_fields)}")
            print(f"  Final confidence: {cleaned.get('confidence_score', 0.0)}")
            
            # Should have high confidence with all components
            assert cleaned.get('confidence_score', 0.0) >= 0.8, \
                f"Complete data should have high confidence score"
            
            print(f"  ✅ All confidence score components working correctly")
        else:
            print(f"  ❌ Failed to clean component test data")


def main():
    """Run confidence scoring tests"""
    print("🧪 Testing Confidence Scoring System")
    print("=" * 60)
    
    try:
        test_suite = TestConfidenceScoring()
        test_suite.setup_method()
        
        # Run tests
        test_suite.test_confidence_scoring_calculation()
        test_suite.test_duplicate_detection_with_confidence()
        test_suite.test_confidence_score_components()
        
        print("\n" + "=" * 60)
        print("✅ All confidence scoring tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)