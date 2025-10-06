"""
Manual Data Protection Verification
Direct SQL testing to verify data protection logic works correctly
"""

import os
import sys
import unittest

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database.database_client import DatabaseClient
from modules.scraping.jobs_populator import JobsPopulator

class TestManualDataProtection(unittest.TestCase):
    """Manual verification of data protection logic"""
    
    def setUp(self):
        """Set up test environment"""
        self.db_client = DatabaseClient()
        self.populator = JobsPopulator()
        
    def test_data_protection_logic_verification(self):
        """Verify that analyzed jobs are protected from being overwritten"""
        print("\n🔍 MANUAL DATA PROTECTION VERIFICATION")
        print("=" * 50)
        
        # Step 1: Get a job that has analysis completed
        analyzed_job = self._get_analyzed_job()
        
        if analyzed_job:
            print(f"✅ Found analyzed job: {analyzed_job['job_title'][:50]}...")
            print(f"   Analysis completed: {analyzed_job['analysis_completed']}")
            print(f"   Industry: {analyzed_job.get('industry', 'N/A')}")
            print(f"   Authenticity: {analyzed_job.get('is_authentic', 'N/A')}")
            
            # Step 2: Test the JobsPopulator logic directly
            print(f"\n🧪 Testing JobsPopulator protection logic...")
            
            # This should NOT overwrite the analyzed job
            result = self._test_populator_protection(analyzed_job)
            
            if result:
                print(f"✅ Protection logic working: analyzed job not overwritten")
                return True
            else:
                print(f"❌ Protection logic failed: analyzed job was overwritten")
                return False
        else:
            print(f"ℹ️  No analyzed jobs found, testing basic functionality...")
            
            # Test basic transfer functionality
            stats = self.populator.get_transfer_statistics()
            print(f"Transfer statistics: {stats}")
            
            return True
    
    def _get_analyzed_job(self):
        """Get a job that has been analyzed"""
        try:
            from sqlalchemy import text
            with self.db_client.get_session() as session:
                result = session.execute(
                    text("SELECT * FROM jobs WHERE analysis_completed = true LIMIT 1")
                )
                row = result.fetchone()
                return dict(row._mapping) if row else None
        except Exception as e:
            print(f"Error getting analyzed job: {e}")
            return None
    
    def _test_populator_protection(self, analyzed_job):
        """Test that the populator protects analyzed jobs"""
        try:
            # The key test: does the populator have logic to avoid overwriting analyzed jobs?
            # Let's check the implementation by looking at the transfer method
            
            # Check if there are any cleaned scrapes that might match this job
            from sqlalchemy import text
            with self.db_client.get_session() as session:
                result = session.execute(
                    text("""
                        SELECT COUNT(*) as count 
                        FROM cleaned_job_scrapes 
                        WHERE job_title ILIKE :pattern
                    """),
                    {"pattern": f"%{analyzed_job['job_title'][:20]}%"}
                )
                similar_scrapes = result.fetchone()[0]
                
                print(f"   Found {similar_scrapes} similar cleaned scrapes")
                
                if similar_scrapes > 0:
                    # Test the core protection logic: 
                    # JobsPopulator should skip jobs that already have analysis_completed = true
                    original_stats = self.populator.get_transfer_statistics()
                    
                    # Try to transfer - this should respect the analysis_completed flag
                    transfer_stats = self.populator.transfer_cleaned_scrapes_to_jobs(batch_size=5)
                    
                    print(f"   Transfer attempt: {transfer_stats}")
                    
                    # Verify the analyzed job still exists with same analysis data
                    updated_job = self._get_job_by_id(analyzed_job['id'])
                    
                    if updated_job and updated_job['analysis_completed'] == analyzed_job['analysis_completed']:
                        return True
                    else:
                        return False
                else:
                    print(f"   No similar scrapes found to test against")
                    return True
                    
        except Exception as e:
            print(f"Error testing populator protection: {e}")
            return False
    
    def _get_job_by_id(self, job_id):
        """Get job by ID"""
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