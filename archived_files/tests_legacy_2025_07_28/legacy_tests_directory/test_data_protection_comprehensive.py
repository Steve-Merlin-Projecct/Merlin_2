"""
Comprehensive Data Protection Test
Tests integration pipeline to ensure:
1. AI-analyzed jobs aren't overwritten by new raw scrapes
2. Duplicate detection works properly after AI analysis
"""

import os
import sys
import unittest
import requests
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database.database_client import DatabaseClient

class TestDataProtectionComprehensive(unittest.TestCase):
    """Comprehensive test of data protection in integration pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.db_client = DatabaseClient()
        
        # Authenticate with dashboard
        self.session = requests.Session()
        auth_response = self.session.post(
            f"{self.base_url}/dashboard/authenticate",
            json={"password": "jellyfish–lantern–kisses"}
        )
        self.assertEqual(auth_response.status_code, 200, "Authentication failed")
        
    def test_complete_data_protection_workflow(self):
        """Test complete workflow: transfer → analyze → re-transfer → verify protection"""
        print("\n🔒 COMPREHENSIVE DATA PROTECTION WORKFLOW TEST")
        print("=" * 60)
        
        # Step 1: Check initial state
        initial_jobs = self._get_all_jobs()
        initial_analyzed = self._get_analyzed_jobs()
        print(f"📊 Initial state: {len(initial_jobs)} total jobs, {len(initial_analyzed)} analyzed")
        
        # Step 2: Transfer cleaned scrapes to jobs
        print("\n📥 Step 1: Transferring cleaned scrapes to jobs table...")
        transfer_result = self._call_api('POST', '/api/integration/transfer-jobs', {'batch_size': 20})
        print(f"   Transfer result: {transfer_result['statistics']['successful']} jobs transferred")
        
        # Step 3: Get jobs after transfer
        jobs_after_transfer = self._get_all_jobs()
        unanalyzed_jobs = self._get_unanalyzed_jobs()
        print(f"   After transfer: {len(jobs_after_transfer)} total jobs, {len(unanalyzed_jobs)} unanalyzed")
        
        # Step 4: Queue jobs for AI analysis
        if len(unanalyzed_jobs) > 0:
            print(f"\n🧠 Step 2: Queuing {min(5, len(unanalyzed_jobs))} jobs for AI analysis...")
            queue_result = self._call_api('POST', '/api/integration/queue-jobs', {
                'criteria': {'unanalyzed_only': True},
                'priority': 'high',
                'limit': 5
            })
            print(f"   Queue result: {queue_result['statistics']['queued']} jobs queued")
            
            # Step 5: Run AI analysis
            if queue_result['statistics']['queued'] > 0:
                print(f"\n⚡ Step 3: Running AI analysis on queued jobs...")
                analysis_result = self._call_api('POST', '/api/integration/run-analysis', {'max_jobs': 3})
                print(f"   Analysis result: {analysis_result['statistics']['successful']} jobs analyzed")
        
        # Step 6: Get state after analysis
        analyzed_jobs_after = self._get_analyzed_jobs()
        print(f"\n📈 After AI analysis: {len(analyzed_jobs_after)} analyzed jobs")
        
        if len(analyzed_jobs_after) > 0:
            # Step 7: Test protection - simulate new scrapes
            test_job = analyzed_jobs_after[0]
            original_analysis_status = test_job['analysis_completed']
            original_authenticity = test_job.get('is_authentic')
            original_industry = test_job.get('industry')
            
            print(f"\n🛡️  Step 4: Testing protection for job: {test_job['job_title'][:50]}...")
            print(f"   Original analysis status: {original_analysis_status}")
            print(f"   Original authenticity: {original_authenticity}")
            print(f"   Original industry: {original_industry}")
            
            # Simulate new raw scrapes by trying to transfer again
            print(f"\n🔄 Step 5: Simulating new scrapes (re-transfer)...")
            retransfer_result = self._call_api('POST', '/api/integration/transfer-jobs', {'batch_size': 20})
            print(f"   Re-transfer result: {retransfer_result['statistics']['successful']} jobs transferred")
            
            # Verify the analyzed job is preserved
            updated_job = self._get_job_by_id(test_job['id'])
            self.assertIsNotNone(updated_job, "Analyzed job should still exist")
            
            # Check that analysis data is preserved
            self.assertEqual(
                updated_job['analysis_completed'], 
                original_analysis_status,
                "❌ Analysis status should be preserved"
            )
            
            if original_authenticity is not None:
                self.assertEqual(
                    updated_job.get('is_authentic'), 
                    original_authenticity,
                    "❌ Authenticity analysis should be preserved"
                )
            
            if original_industry is not None:
                self.assertEqual(
                    updated_job.get('industry'), 
                    original_industry,
                    "❌ Industry classification should be preserved"
                )
            
            print(f"   ✅ AI analysis data preserved after re-transfer")
        
        # Step 8: Test full pipeline duplicate prevention
        print(f"\n🔄 Step 6: Testing full pipeline duplicate prevention...")
        pipeline_result = self._call_api('POST', '/api/integration/full-pipeline', {
            'transfer_batch_size': 20,
            'analysis_batch_size': 5
        })
        print(f"   Full pipeline: {pipeline_result['pipeline_results']['transfer']['successful']} transferred, "
              f"{pipeline_result['pipeline_results']['analysis']['successful']} analyzed")
        
        # Step 9: Final verification
        final_jobs = self._get_all_jobs()
        final_analyzed = self._get_analyzed_jobs()
        
        print(f"\n📊 Final state: {len(final_jobs)} total jobs, {len(final_analyzed)} analyzed")
        
        # Verify no unexpected job explosion (duplicate prevention working)
        jobs_increase = len(final_jobs) - len(initial_jobs)
        self.assertLessEqual(jobs_increase, 10, "Job count should not increase dramatically")
        
        print(f"   Job count increase: {jobs_increase} (within expected range)")
        print(f"\n✅ DATA PROTECTION TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return True
    
    def _call_api(self, method, endpoint, data=None):
        """Make authenticated API call"""
        url = f"{self.base_url}{endpoint}"
        if method.upper() == 'POST':
            response = self.session.post(url, json=data)
        else:
            response = self.session.get(url)
        
        self.assertEqual(response.status_code, 200, f"API call failed: {endpoint}")
        return response.json()
    
    def _get_all_jobs(self):
        """Get all jobs from database"""
        try:
            from sqlalchemy import text
            with self.db_client.get_session() as session:
                result = session.execute(text("SELECT * FROM jobs"))
                return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            print(f"Error getting all jobs: {e}")
            return []
    
    def _get_analyzed_jobs(self):
        """Get jobs that have been AI analyzed"""
        try:
            from sqlalchemy import text
            with self.db_client.get_session() as session:
                result = session.execute(
                    text("SELECT * FROM jobs WHERE analysis_completed = true")
                )
                return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            print(f"Error getting analyzed jobs: {e}")
            return []
    
    def _get_unanalyzed_jobs(self):
        """Get jobs that haven't been AI analyzed"""
        try:
            from sqlalchemy import text
            with self.db_client.get_session() as session:
                result = session.execute(
                    text("SELECT * FROM jobs WHERE analysis_completed = false OR analysis_completed IS NULL")
                )
                return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            print(f"Error getting unanalyzed jobs: {e}")
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
    unittest.main(verbosity=2)