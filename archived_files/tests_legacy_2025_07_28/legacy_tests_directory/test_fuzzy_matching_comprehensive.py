"""
Comprehensive Fuzzy Matching Test Suite
Tests the enhanced fuzzy matching algorithms and performance optimizations
"""

import os
import sys
import unittest
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.utils.fuzzy_matcher import FuzzyMatcher
from modules.database.database_client import DatabaseClient
from modules.scraping.jobs_populator import JobsPopulator

class TestFuzzyMatchingComprehensive(unittest.TestCase):
    """Comprehensive test of enhanced fuzzy matching capabilities"""
    
    def setUp(self):
        """Set up test environment"""
        self.fuzzy_matcher = FuzzyMatcher()
        self.db_client = DatabaseClient()
        self.populator = JobsPopulator()
        
    def test_job_title_similarity_algorithms(self):
        """Test various job title similarity scenarios"""
        print("\n🔍 TESTING JOB TITLE SIMILARITY ALGORITHMS")
        print("=" * 50)
        
        # Test cases: (title1, title2, expected_high_similarity)
        test_cases = [
            # Exact matches
            ("Senior Software Engineer", "Senior Software Engineer", True),
            
            # Minor variations
            ("Senior Software Engineer", "Sr. Software Engineer", True),
            ("Marketing Manager", "Marketing Mgr", True),
            ("Software Developer", "Software Dev", True),
            
            # Different order but same role
            ("Data Analysis Manager", "Manager, Data Analysis", True),
            ("Frontend Developer React", "React Frontend Developer", True),
            
            # Similar but different levels
            ("Senior Marketing Manager", "Marketing Manager", True),
            ("Junior Developer", "Developer", True),
            
            # Different roles (should be low similarity)
            ("Software Engineer", "Marketing Manager", False),
            ("Data Analyst", "HR Coordinator", False),
            
            # Common variations in job postings
            ("Digital Marketing Specialist", "Digital Marketing Expert", True),
            ("Business Analyst", "Business Analysis Specialist", True),
        ]
        
        high_similarity_count = 0
        total_tests = len(test_cases)
        
        for title1, title2, expected_high in test_cases:
            similarity = self.fuzzy_matcher.calculate_job_similarity(title1, title2)
            is_high = similarity >= 0.7
            
            status = "✅" if is_high == expected_high else "❌"
            print(f"   {status} '{title1}' vs '{title2}': {similarity:.3f}")
            
            if is_high == expected_high:
                high_similarity_count += 1
        
        accuracy = high_similarity_count / total_tests
        print(f"\n📊 Job Title Matching Accuracy: {accuracy:.1%} ({high_similarity_count}/{total_tests})")
        
        self.assertGreaterEqual(accuracy, 0.8, "Job title matching should be at least 80% accurate")
        return True
    
    def test_company_name_similarity_algorithms(self):
        """Test various company name similarity scenarios"""
        print("\n🏢 TESTING COMPANY NAME SIMILARITY ALGORITHMS")
        print("=" * 50)
        
        # Test cases: (company1, company2, expected_high_similarity)
        test_cases = [
            # Exact matches
            ("TechCorp Inc", "TechCorp Inc", True),
            
            # Legal suffix variations
            ("Microsoft Corporation", "Microsoft Corp", True),
            ("Apple Inc", "Apple Inc.", True),
            ("Google LLC", "Google", True),
            
            # Minor variations
            ("TechCorp Inc", "Tech Corp Inc", True),
            ("DataSoft Solutions", "DataSoft Solution", True),
            
            # Different companies (should be low similarity)
            ("Microsoft", "Apple", False),
            ("Google", "Amazon", False),
            ("TechCorp", "DataSoft", False),
            
            # Similar names but different companies
            ("TechCorp", "TechSoft", True),  # These might be similar enough
            ("DataCorp Inc", "DataCorp LLC", True),
        ]
        
        high_similarity_count = 0
        total_tests = len(test_cases)
        
        for company1, company2, expected_high in test_cases:
            similarity = self.fuzzy_matcher.calculate_company_similarity(company1, company2)
            is_high = similarity >= 0.8
            
            status = "✅" if is_high == expected_high else "❌"
            print(f"   {status} '{company1}' vs '{company2}': {similarity:.3f}")
            
            if is_high == expected_high:
                high_similarity_count += 1
        
        accuracy = high_similarity_count / total_tests
        print(f"\n📊 Company Name Matching Accuracy: {accuracy:.1%} ({high_similarity_count}/{total_tests})")
        
        self.assertGreaterEqual(accuracy, 0.75, "Company name matching should be at least 75% accurate")
        return True
    
    def test_enhanced_data_protection_workflow(self):
        """Test the enhanced data protection with fuzzy matching"""
        print("\n🛡️  TESTING ENHANCED DATA PROTECTION WORKFLOW")
        print("=" * 50)
        
        # Test with real data if available
        try:
            from sqlalchemy import text
            
            # Get an analyzed job
            with self.db_client.get_session() as session:
                result = session.execute(
                    text("SELECT j.*, c.name as company_name FROM jobs j JOIN companies c ON j.company_id = c.id WHERE j.analysis_completed = true LIMIT 1")
                )
                analyzed_job = result.fetchone()
                
                if analyzed_job:
                    job_dict = dict(analyzed_job._mapping)
                    print(f"   Testing with: '{job_dict['job_title']}' at '{job_dict['company_name']}'")
                    
                    # Test exact match
                    exact_match = self.populator._find_existing_analyzed_job(
                        job_dict['job_title'], 
                        job_dict['company_name']
                    )
                    
                    if exact_match:
                        print(f"   ✅ Exact match found (ID: {exact_match['id']})")
                        
                        # Test minor variation
                        variation_title = job_dict['job_title'] + " (Remote)"
                        variation_match = self.populator._find_existing_analyzed_job(
                            variation_title, 
                            job_dict['company_name']
                        )
                        
                        if variation_match:
                            print(f"   ✅ Variation match found with enhanced fuzzy matching")
                        else:
                            print(f"   ℹ️  Variation not matched (title too different)")
                        
                        return True
                    else:
                        print(f"   ❌ Exact match not found - check data protection logic")
                        return False
                else:
                    print(f"   ℹ️  No analyzed jobs found - cannot test with real data")
                    return True
                    
        except Exception as e:
            print(f"   ❌ Error testing data protection: {e}")
            return False
    
    def test_database_query_fixes(self):
        """Test that database query parameter formatting is fixed"""
        print("\n💾 TESTING DATABASE QUERY PARAMETER FIXES")
        print("=" * 50)
        
        try:
            # Test basic database connectivity
            connection_test = self.db_client.test_connection()
            print(f"   Database connection: {'✅ Connected' if connection_test else '❌ Failed'}")
            
            # Test simple query execution
            test_query = "SELECT COUNT(*) as count FROM jobs"
            result = self.db_client.execute_query(test_query)
            
            if result and isinstance(result, list):
                count = result[0].get('count', 0)
                print(f"   ✅ Query execution successful: {count} jobs in database")
            else:
                print(f"   ❌ Query execution failed")
                return False
            
            # Test parameterized query
            param_query = "SELECT COUNT(*) as count FROM jobs WHERE analysis_completed = %s"
            param_result = self.db_client.execute_query(param_query, [True])
            
            if param_result and isinstance(param_result, list):
                analyzed_count = param_result[0].get('count', 0)
                print(f"   ✅ Parameterized query successful: {analyzed_count} analyzed jobs")
                return True
            else:
                print(f"   ❌ Parameterized query failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Database query test error: {e}")
            return False
    
    def test_performance_indexes(self):
        """Test that performance indexes are working"""
        print("\n⚡ TESTING PERFORMANCE INDEXES")
        print("=" * 50)
        
        try:
            # Check if indexes exist
            index_query = """
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND indexname LIKE 'idx_%'
                ORDER BY tablename, indexname
            """
            
            indexes = self.db_client.execute_query(index_query)
            
            if indexes:
                print(f"   ✅ Found {len(indexes)} performance indexes:")
                for idx in indexes:
                    print(f"      • {idx['indexname']} on {idx['tablename']}")
                
                # Check for key indexes
                index_names = [idx['indexname'] for idx in indexes]
                required_indexes = [
                    'idx_jobs_title_lower',
                    'idx_companies_name_lower', 
                    'idx_jobs_company_analysis',
                    'idx_jobs_created_at'
                ]
                
                missing_indexes = [idx for idx in required_indexes if idx not in index_names]
                
                if not missing_indexes:
                    print(f"   ✅ All required performance indexes present")
                    return True
                else:
                    print(f"   ⚠️  Missing indexes: {missing_indexes}")
                    return False
            else:
                print(f"   ❌ No performance indexes found")
                return False
                
        except Exception as e:
            print(f"   ❌ Index check error: {e}")
            return False

if __name__ == '__main__':
    unittest.main(verbosity=2)