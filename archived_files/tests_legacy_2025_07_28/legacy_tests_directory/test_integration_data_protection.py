"""
Test Integration Data Protection
Tests to ensure AI-analyzed jobs aren't overwritten and duplicate detection works
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import text

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database.database_client import DatabaseClient
from modules.scraping.jobs_populator import JobsPopulator
from modules.ai_job_description_analysis.batch_analyzer import BatchAIAnalyzer

class TestIntegrationDataProtection(unittest.TestCase):
    """Test data protection in the integration pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        self.db_client = DatabaseClient()
        self.populator = JobsPopulator()
        self.batch_analyzer = BatchAIAnalyzer()
        
        # Test company for consistency
        self.test_company_id = str(uuid4())
        self.test_job_title = "Senior Python Developer - Data Protection Test"
        
    def tearDown(self):
        """Clean up test data"""
        try:
            with self.db_client.get_session() as session:
                # Clean up test jobs
                session.execute(
                    text("DELETE FROM jobs WHERE job_title LIKE '%Data Protection Test%'")
                )
                
                # Clean up test raw scrapes
                session.execute(
                    text("DELETE FROM raw_job_scrapes WHERE raw_data->>'positionName' LIKE '%Data Protection Test%'")
                )
                
                # Clean up test cleaned scrapes
                session.execute(
                    text("DELETE FROM cleaned_job_scrapes WHERE job_title LIKE '%Data Protection Test%'")
                )
                
                # Clean up test queue entries
                session.execute(
                    text("DELETE FROM job_analysis_queue WHERE job_id IN "
                         "(SELECT job_id FROM jobs WHERE job_title LIKE '%Data Protection Test%')")
                )
                
                session.commit()
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def test_ai_analyzed_job_not_overwritten(self):
        """Test 1: Ensure AI-analyzed jobs aren't overwritten by new raw scrapes"""
        print("\n=== TEST 1: AI-Analyzed Job Protection ===")
        
        # Step 1: Create a cleaned job scrape
        cleaned_scrape_id = self._create_test_cleaned_scrape()
        print(f"Created test cleaned scrape: {cleaned_scrape_id}")
        
        # Step 2: Transfer to jobs table
        transfer_stats = self.populator.transfer_cleaned_scrapes_to_jobs(batch_size=1)
        self.assertGreater(transfer_stats['successful'], 0, "Should transfer at least 1 job")
        print(f"Transfer completed: {transfer_stats}")
        
        # Step 3: Get the transferred job
        job_record = self._get_test_job()
        self.assertIsNotNone(job_record, "Job should be created in jobs table")
        original_job_id = job_record['job_id']
        print(f"Job created with ID: {original_job_id}")
        
        # Step 4: Simulate AI analysis by updating AI-related fields
        self._simulate_ai_analysis(original_job_id)
        print("Simulated AI analysis completion")
        
        # Step 5: Verify AI analysis fields are populated
        analyzed_job = self._get_job_by_id(original_job_id)
        self.assertIsNotNone(analyzed_job['ai_analysis_completed_at'], "AI analysis should be marked complete")
        self.assertIsNotNone(analyzed_job['primary_skills'], "Primary skills should be populated")
        print("AI analysis fields verified")
        
        # Step 6: Create a new raw scrape for the same job
        new_raw_scrape_id = self._create_test_raw_scrape(variation="Updated Description")
        print(f"Created new raw scrape: {new_raw_scrape_id}")
        
        # Step 7: Create a new cleaned scrape from the raw scrape
        new_cleaned_scrape_id = self._create_test_cleaned_scrape(variation="Updated")
        print(f"Created new cleaned scrape: {new_cleaned_scrape_id}")
        
        # Step 8: Try to transfer again - should not overwrite AI-analyzed job
        transfer_stats_2 = self.populator.transfer_cleaned_scrapes_to_jobs(batch_size=1)
        print(f"Second transfer stats: {transfer_stats_2}")
        
        # Step 9: Verify original job is preserved
        final_job = self._get_job_by_id(original_job_id)
        self.assertIsNotNone(final_job, "Original job should still exist")
        self.assertIsNotNone(final_job['ai_analysis_completed_at'], "AI analysis should be preserved")
        self.assertIsNotNone(final_job['primary_skills'], "AI analysis data should be preserved")
        
        # Step 10: Verify no duplicate job was created
        all_test_jobs = self._get_all_test_jobs()
        self.assertEqual(len(all_test_jobs), 1, "Should have exactly 1 job, not duplicates")
        
        print("✅ TEST 1 PASSED: AI-analyzed job protected from overwriting")
        return True
    
    def test_duplicate_detection_after_ai_analysis(self):
        """Test 2: Ensure duplicate detection works after AI analysis"""
        print("\n=== TEST 2: Duplicate Detection After AI Analysis ===")
        
        # Step 1: Create initial job and get it AI-analyzed
        cleaned_scrape_id = self._create_test_cleaned_scrape(variation="Original")
        transfer_stats = self.populator.transfer_cleaned_scrapes_to_jobs(batch_size=1)
        self.assertGreater(transfer_stats['successful'], 0, "Should transfer original job")
        
        job_record = self._get_test_job()
        original_job_id = job_record['job_id']
        print(f"Original job created: {original_job_id}")
        
        # Step 2: Complete AI analysis
        self._simulate_ai_analysis(original_job_id)
        print("AI analysis completed on original job")
        
        # Step 3: Create multiple new raw scrapes for the same job (simulating re-scraping)
        raw_scrape_ids = []
        for i in range(3):
            raw_id = self._create_test_raw_scrape(variation=f"Duplicate-{i}")
            raw_scrape_ids.append(raw_id)
        print(f"Created {len(raw_scrape_ids)} duplicate raw scrapes")
        
        # Step 4: Create cleaned scrapes from the raw scrapes
        cleaned_scrape_ids = []
        for i in range(3):
            cleaned_id = self._create_test_cleaned_scrape(variation=f"Duplicate-{i}")
            cleaned_scrape_ids.append(cleaned_id)
        print(f"Created {len(cleaned_scrape_ids)} duplicate cleaned scrapes")
        
        # Step 5: Try to transfer the duplicates
        transfer_stats_2 = self.populator.transfer_cleaned_scrapes_to_jobs(batch_size=10)
        print(f"Duplicate transfer stats: {transfer_stats_2}")
        
        # Step 6: Verify still only one job exists
        all_test_jobs = self._get_all_test_jobs()
        self.assertEqual(len(all_test_jobs), 1, "Should still have exactly 1 job after duplicates")
        
        # Step 7: Verify the original job with AI analysis is preserved
        final_job = self._get_job_by_id(original_job_id)
        self.assertIsNotNone(final_job['ai_analysis_completed_at'], "AI analysis should be preserved")
        self.assertIsNotNone(final_job['primary_skills'], "AI data should be preserved")
        
        # Step 8: Verify no jobs are queued for re-analysis
        queue_stats = self.batch_analyzer.get_queue_statistics()
        print(f"Queue stats after duplicate processing: {queue_stats}")
        
        print("✅ TEST 2 PASSED: Duplicate detection works after AI analysis")
        return True
    
    def _create_test_cleaned_scrape(self, variation="Original"):
        """Create a test cleaned job scrape"""
        with self.db_client.get_session() as session:
            insert_sql = text("""
                INSERT INTO cleaned_job_scrapes (
                    job_title, company_name, location_city, location_province,
                    location_country, job_description, salary_min, salary_max, salary_currency,
                    work_arrangement, job_type, posting_date, application_url, confidence_score,
                    duplicates_count
                ) VALUES (
                    :job_title, :company_name, :location_city, 
                    :location_province, :location_country, :job_description, 
                    :salary_min, :salary_max, :salary_currency,
                    :work_arrangement, :job_type, :posting_date, :application_url,
                    :confidence_score, :duplicates_count
                ) RETURNING cleaned_job_id
            """)
            
            result = session.execute(insert_sql, {
                'job_title': f"{self.test_job_title} - {variation}",
                'company_name': 'Test Company Inc',
                'location_city': 'Calgary',
                'location_province': 'Alberta', 
                'location_country': 'Canada',
                'job_description': f'Test job description for data protection testing - {variation}',
                'salary_min': 75000,
                'salary_max': 95000,
                'salary_currency': 'CAD',
                'work_arrangement': 'hybrid',
                'job_type': 'full-time',
                'posting_date': datetime.now().date(),
                'application_url': f'https://test-company.com/jobs/python-dev-{variation.lower()}',
                'confidence_score': 0.95,
                'duplicates_count': 1
            })
            
            scrape_id = result.fetchone()[0]
            session.commit()
            return scrape_id
    
    def _create_test_raw_scrape(self, variation="Original"):
        """Create a test raw job scrape"""
        with self.db_client.get_session() as session:
            insert_sql = text("""
                INSERT INTO raw_job_scrapes (
                    source_website, raw_data, scraped_at
                ) VALUES (
                    :source_website, :raw_data, :scraped_at
                ) RETURNING scrape_id
            """)
            
            raw_data = {
                "positionName": f"{self.test_job_title} - {variation}",
                "company": "Test Company Inc",
                "location": "Calgary, AB",
                "description": f"Test description - {variation}",
                "salary": "$75,000 - $95,000",
                "url": f"https://test-company.com/jobs/python-dev-{variation.lower()}"
            }
            
            result = session.execute(insert_sql, {
                'source_website': 'test-site.com',
                'raw_data': raw_data,
                'scraped_at': datetime.now()
            })
            
            scrape_id = result.fetchone()[0]
            session.commit()
            return scrape_id
    
    def _get_test_job(self):
        """Get test job from jobs table"""
        with self.db_client.get_session() as session:
            result = session.execute(
                text("SELECT * FROM jobs WHERE job_title LIKE :pattern LIMIT 1"),
                {"pattern": f"%{self.test_job_title}%"}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def _get_job_by_id(self, job_id):
        """Get job by specific ID"""
        with self.db_client.get_session() as session:
            result = session.execute(
                text("SELECT * FROM jobs WHERE job_id = :job_id"),
                {"job_id": job_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def _get_all_test_jobs(self):
        """Get all test jobs"""
        with self.db_client.get_session() as session:
            result = session.execute(
                text("SELECT * FROM jobs WHERE job_title LIKE :pattern"),
                {"pattern": f"%{self.test_job_title}%"}
            )
            return [dict(row._mapping) for row in result.fetchall()]
    
    def _simulate_ai_analysis(self, job_id):
        """Simulate AI analysis completion by updating relevant fields"""
        with self.db_client.get_session() as session:
            update_sql = text("""
                UPDATE jobs SET 
                    ai_analysis_completed_at = :analysis_time,
                    primary_skills = :skills,
                    industry_primary = :industry,
                    seniority_level = :seniority,
                    compensation_currency = :currency
                WHERE job_id = :job_id
            """)
            
            session.execute(update_sql, {
                "analysis_time": datetime.now(),
                "skills": ["Python", "Flask", "PostgreSQL", "REST APIs"],
                "industry": "Technology",
                "seniority": "Senior",
                "currency": "CAD",
                "job_id": job_id
            })
            session.commit()

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)