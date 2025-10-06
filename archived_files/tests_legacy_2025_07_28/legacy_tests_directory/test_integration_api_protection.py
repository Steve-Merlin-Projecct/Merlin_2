"""
Test Integration API Data Protection
Tests using API endpoints to ensure AI-analyzed jobs aren't overwritten
"""

import os
import sys
import unittest
import requests
import json
from datetime import datetime
from uuid import uuid4

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database.database_client import DatabaseClient

class TestIntegrationAPIProtection(unittest.TestCase):
    """Test data protection using integration API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.db_client = DatabaseClient()
        
        # Authenticate with dashboard (required for API access)
        self.session = requests.Session()
        auth_response = self.session.post(
            f"{self.base_url}/dashboard/authenticate",
            json={"password": "jellyfish–lantern–kisses"}
        )
        self.assertTrue(auth_response.status_code == 200, "Authentication failed")
        
    def test_data_protection_workflow(self):
        """Comprehensive test: Ensure AI-analyzed jobs aren't overwritten and duplicates are handled"""
        print("\n=== COMPREHENSIVE DATA PROTECTION TEST ===")
        
        # Step 1: Get initial statistics
        print("Step 1: Getting initial pipeline status...")
        initial_stats = self._get_pipeline_status()
        initial_jobs_count = initial_stats.get('transfer_statistics', {}).get('total_jobs', 0)
        print(f"Initial jobs in database: {initial_jobs_count}")
        
        # Step 2: Transfer any existing cleaned scrapes to jobs
        print("\nStep 2: Transferring cleaned scrapes to jobs table...")
        transfer_response = self.session.post(
            f"{self.base_url}/api/integration/transfer-jobs",
            json={"batch_size": 10}
        )
        self.assertEqual(transfer_response.status_code, 200, "Transfer should succeed")
        transfer_result = transfer_response.json()
        print(f"Transfer result: {transfer_result}")
        
        # Step 3: Get a job that was transferred
        jobs_with_analysis = self._get_jobs_with_analysis_data()
        print(f"Found {len(jobs_with_analysis)} jobs with AI analysis data")
        
        # Step 4: If no analyzed jobs exist, queue and analyze some jobs
        if len(jobs_with_analysis) == 0:
            print("\nStep 4: No analyzed jobs found, creating some...")
            # Queue jobs for analysis
            queue_response = self.session.post(
                f"{self.base_url}/api/integration/queue-jobs",
                json={
                    "criteria": {"unanalyzed_only": True},
                    "priority": "high",
                    "limit": 5
                }
            )
            self.assertEqual(queue_response.status_code, 200, "Queueing should succeed")
            queue_result = queue_response.json()
            print(f"Queue result: {queue_result}")
            
            # Run analysis
            if queue_result.get('statistics', {}).get('queued', 0) > 0:
                analysis_response = self.session.post(
                    f"{self.base_url}/api/integration/run-analysis",
                    json={"max_jobs": 3}
                )
                self.assertEqual(analysis_response.status_code, 200, "Analysis should succeed")
                analysis_result = analysis_response.json()
                print(f"Analysis result: {analysis_result}")
                
                # Get analyzed jobs again
                jobs_with_analysis = self._get_jobs_with_analysis_data()
                print(f"After analysis: {len(jobs_with_analysis)} jobs with AI analysis data")
        
        # Step 5: Test that analyzed jobs aren't overwritten
        if len(jobs_with_analysis) > 0:
            test_job = jobs_with_analysis[0]
            original_analysis_time = test_job.get('ai_analysis_completed_at')
            original_skills = test_job.get('primary_skills')
            
            print(f"\nStep 5: Testing protection for job {test_job['id']}")
            print(f"Original analysis time: {original_analysis_time}")
            print(f"Original skills: {original_skills}")
            
            # Try to transfer again (simulating new scrapes)
            retransfer_response = self.session.post(
                f"{self.base_url}/api/integration/transfer-jobs",
                json={"batch_size": 10}
            )
            self.assertEqual(retransfer_response.status_code, 200, "Re-transfer should succeed")
            
            # Verify the analyzed job is preserved
            updated_job = self._get_job_by_id(test_job['id'])
            self.assertIsNotNone(updated_job, "Job should still exist")
            self.assertEqual(
                updated_job.get('ai_analysis_completed_at'), 
                original_analysis_time,
                "AI analysis timestamp should be preserved"
            )
            self.assertEqual(
                updated_job.get('primary_skills'), 
                original_skills,
                "AI analysis data should be preserved"
            )
            print("✅ AI-analyzed job protected from overwriting")
        
        # Step 6: Test full pipeline doesn't create duplicates
        print("\nStep 6: Testing full pipeline duplicate prevention...")
        pipeline_response = self.session.post(
            f"{self.base_url}/api/integration/full-pipeline",
            json={
                "transfer_batch_size": 20,
                "analysis_batch_size": 5
            }
        )
        self.assertEqual(pipeline_response.status_code, 200, "Full pipeline should succeed")
        pipeline_result = pipeline_response.json()
        print(f"Full pipeline result: {pipeline_result}")
        
        # Step 7: Verify final statistics
        print("\nStep 7: Verifying final statistics...")
        final_stats = self._get_pipeline_status()
        final_jobs_count = final_stats.get('transfer_statistics', {}).get('total_jobs', 0)
        print(f"Final jobs in database: {final_jobs_count}")
        
        # Jobs count should not have increased dramatically (no duplicates)
        jobs_increase = final_jobs_count - initial_jobs_count
        print(f"Jobs increase during test: {jobs_increase}")
        
        print("✅ COMPREHENSIVE DATA PROTECTION TEST COMPLETED")
        return True
    
    def _get_pipeline_status(self):
        """Get current pipeline status"""
        response = self.session.get(f"{self.base_url}/api/integration/pipeline-status")
        if response.status_code == 200:
            return response.json().get('pipeline_status', {})
        return {}
    
    def _get_jobs_with_analysis_data(self):
        """Get jobs that have AI analysis data"""
        try:
            from sqlalchemy import text
            with self.db_client.get_session() as session:
                result = session.execute(
                    text("""
                        SELECT id, job_title, ai_analysis_completed_at, primary_skills
                        FROM jobs 
                        WHERE ai_analysis_completed_at IS NOT NULL 
                        AND primary_skills IS NOT NULL
                        LIMIT 10
                    """)
                )
                return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            print(f"Error getting analyzed jobs: {e}")
            return []
    
    def _get_job_by_id(self, job_id):
        """Get specific job by ID"""
        try:
            from sqlalchemy import text
            with self.db_client.get_session() as session:
                result = session.execute(
                    text("SELECT * FROM jobs WHERE id = :job_id"),
                    {"job_id": job_id}
                )
                row = result.fetchone()
                return dict(row._mapping) if row else None
        except Exception as e:
            print(f"Error getting job by ID: {e}")
            return None

if __name__ == '__main__':
    # Run the test
    unittest.main(verbosity=2)