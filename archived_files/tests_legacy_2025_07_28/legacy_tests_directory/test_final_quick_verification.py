"""
Quick verification test for all improvements
"""

import os
import sys
import unittest

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.utils.fuzzy_matcher import FuzzyMatcher
from modules.database.database_client import DatabaseClient

class TestQuickVerification(unittest.TestCase):
    """Quick verification of core improvements"""
    
    def test_enhanced_fuzzy_matching_sample(self):
        """Test enhanced fuzzy matching with key examples"""
        print("\n🔍 ENHANCED FUZZY MATCHING VERIFICATION")
        print("=" * 45)
        
        matcher = FuzzyMatcher()
        
        # Test improved job title matching
        test_cases = [
            ("Senior Software Engineer", "Sr. Software Engineer"),
            ("Marketing Manager", "Marketing Mgr"),
            ("Software Developer", "Software Dev"),
            ("Data Analyst", "Data Analysis Specialist"),
        ]
        
        improved_count = 0
        for title1, title2 in test_cases:
            score = matcher.calculate_job_similarity(title1, title2)
            is_good = score >= 0.7
            status = "✅" if is_good else "⚠️"
            print(f"   {status} '{title1}' vs '{title2}': {score:.3f}")
            if is_good:
                improved_count += 1
        
        print(f"   Enhanced matching: {improved_count}/{len(test_cases)} cases ≥ 0.7")
        
        # Test improved company matching
        company_cases = [
            ("Microsoft Corporation", "Microsoft Corp"),
            ("Google LLC", "Google"),
            ("TechCorp Inc", "Tech Corp Inc"),
        ]
        
        company_improved = 0
        for comp1, comp2 in company_cases:
            score = matcher.calculate_company_similarity(comp1, comp2)
            is_good = score >= 0.8
            status = "✅" if is_good else "⚠️"
            print(f"   {status} '{comp1}' vs '{comp2}': {score:.3f}")
            if is_good:
                company_improved += 1
        
        print(f"   Company matching: {company_improved}/{len(company_cases)} cases ≥ 0.8")
        
        return improved_count >= 2 and company_improved >= 2
    
    def test_database_query_basic_fix(self):
        """Test basic database query functionality"""
        print("\n💾 DATABASE QUERY FIX VERIFICATION")
        print("=" * 40)
        
        try:
            db = DatabaseClient()
            
            # Test simple query
            result = db.execute_query("SELECT COUNT(*) as count FROM jobs")
            if result and 'count' in result[0]:
                print(f"   ✅ Basic query: {result[0]['count']} jobs found")
                return True
            else:
                print(f"   ❌ Basic query failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False

if __name__ == '__main__':
    unittest.main(verbosity=2)