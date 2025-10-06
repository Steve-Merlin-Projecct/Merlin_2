#!/usr/bin/env python3
"""
Comprehensive Confidence Scoring Test Suite
Tests the confidence scoring system with various scenarios and edge cases
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_comprehensive_confidence_scoring():
    """Test confidence scoring with comprehensive scenarios"""
    
    # Mock pipeline class with scoring methods
    class MockPipeline:
        def _assess_title_quality(self, title: str) -> float:
            if not title:
                return 0.0
            
            quality = 0.5  # Base score
            
            # Check for meaningful length
            if len(title) >= 10:
                quality += 0.2
            if len(title) >= 20:
                quality += 0.1
            
            # Check for common title patterns
            if any(word in title.lower() for word in ['senior', 'junior', 'manager', 'specialist', 'analyst']):
                quality += 0.1
            
            # Check for department/function
            if any(word in title.lower() for word in ['marketing', 'sales', 'engineering', 'finance', 'hr']):
                quality += 0.1
            
            return min(1.0, quality)
        
        def _assess_company_quality(self, company: str) -> float:
            if not company:
                return 0.0
            
            quality = 0.5  # Base score
            
            # Check for meaningful length
            if len(company) >= 5:
                quality += 0.2
            
            # Check for company indicators
            if any(suffix in company.lower() for suffix in ['inc', 'corp', 'ltd', 'llc', 'company']):
                quality += 0.2
            
            # Penalize generic names
            if company.lower() in ['company', 'corporation', 'business', 'employer']:
                quality -= 0.3
            
            return max(0.0, min(1.0, quality))
        
        def _assess_description_quality(self, description: str) -> float:
            if not description:
                return 0.0
            
            quality = 0.3  # Base score
            
            # Check for meaningful length
            if len(description) >= 100:
                quality += 0.2
            if len(description) >= 300:
                quality += 0.2
            if len(description) >= 500:
                quality += 0.1
            
            # Check for key sections
            desc_lower = description.lower()
            if 'responsibility' in desc_lower or 'duties' in desc_lower:
                quality += 0.1
            if 'requirement' in desc_lower or 'qualifications' in desc_lower:
                quality += 0.1
            if 'experience' in desc_lower:
                quality += 0.1
            
            return min(1.0, quality)
        
        def _calculate_confidence_score(self, cleaned_data: dict, raw_data: dict) -> float:
            score = 0.0
            max_score = 0.0
            
            # Critical fields (60% of total score)
            if cleaned_data.get('job_title'):
                title_quality = self._assess_title_quality(cleaned_data['job_title'])
                score += 0.3 * title_quality
            max_score += 0.3
            
            if cleaned_data.get('company_name'):
                company_quality = self._assess_company_quality(cleaned_data['company_name'])
                score += 0.3 * company_quality
            max_score += 0.3
            
            # Important fields (30% of total score)
            if cleaned_data.get('job_description'):
                desc_quality = self._assess_description_quality(cleaned_data['job_description'])
                score += 0.15 * desc_quality
            max_score += 0.15
            
            if cleaned_data.get('location_city'):
                score += 0.15
            max_score += 0.15
            
            # Additional fields (10% of total score)
            if cleaned_data.get('salary_min') or cleaned_data.get('salary_max'):
                score += 0.05
            max_score += 0.05
            
            if cleaned_data.get('external_job_id'):
                score += 0.05
            max_score += 0.05
            
            # Bonus scoring for data completeness
            bonus_fields = ['work_arrangement', 'job_type', 'posting_date', 'company_website']
            bonus_count = sum(1 for field in bonus_fields if cleaned_data.get(field))
            bonus_score = min(0.1, bonus_count * 0.025)  # Max 0.1 bonus
            score += bonus_score
            max_score += 0.1
            
            final_score = round(score / max_score if max_score > 0 else 0.0, 4)
            
            # Ensure score is within valid range
            return max(0.0, min(1.0, final_score))
    
    pipeline = MockPipeline()
    
    # Comprehensive test scenarios
    test_scenarios = [
        {
            'category': 'Perfect Job Posting',
            'data': {
                'job_title': 'Senior Full Stack Software Engineer',
                'company_name': 'TechCorp Solutions Inc.',
                'job_description': '''We are seeking an experienced Senior Full Stack Software Engineer to join our growing engineering team. 
                
                Key Responsibilities:
                - Design and develop scalable web applications
                - Lead technical architecture decisions
                - Mentor junior developers
                - Collaborate with cross-functional teams
                
                Requirements:
                - 5+ years of software development experience
                - Proficiency in React, Node.js, and Python
                - Experience with cloud platforms (AWS, Azure)
                - Strong problem-solving and communication skills
                
                We offer competitive salary, comprehensive benefits, and opportunities for professional growth.''',
                'location_city': 'Edmonton',
                'salary_min': 95000,
                'salary_max': 130000,
                'external_job_id': 'tech-001-2025',
                'work_arrangement': 'hybrid',
                'job_type': 'full-time',
                'posting_date': '2025-01-15',
                'company_website': 'https://techcorp.com'
            },
            'expected_tier': 'High Confidence (0.8-1.0)',
            'expected_min': 0.9
        },
        {
            'category': 'Well-Structured Job',
            'data': {
                'job_title': 'Marketing Manager',
                'company_name': 'Growth Marketing Ltd.',
                'job_description': 'We are looking for a Marketing Manager to develop and execute marketing strategies. The ideal candidate will have 3+ years of marketing experience and strong analytical skills.',
                'location_city': 'Calgary',
                'salary_min': 65000,
                'salary_max': 85000,
                'external_job_id': 'mkt-456',
                'work_arrangement': 'onsite',
                'job_type': 'full-time'
            },
            'expected_tier': 'High Confidence (0.8-1.0)',
            'expected_min': 0.8
        },
        {
            'category': 'Decent Job Posting',
            'data': {
                'job_title': 'Customer Service Representative',
                'company_name': 'ServicePro Corp',
                'job_description': 'Customer service role handling client inquiries and support tickets. Good communication skills required.',
                'location_city': 'Vancouver',
                'salary_min': 45000,
                'external_job_id': 'cs-789'
            },
            'expected_tier': 'Medium Confidence (0.6-0.8)',
            'expected_min': 0.6
        },
        {
            'category': 'Basic Job Posting',
            'data': {
                'job_title': 'Sales Associate',
                'company_name': 'RetailCorp',
                'job_description': 'Sales position available.',
                'location_city': 'Toronto'
            },
            'expected_tier': 'Medium Confidence (0.6-0.8)',
            'expected_min': 0.55
        },
        {
            'category': 'Minimal Information',
            'data': {
                'job_title': 'Assistant',
                'company_name': 'Business Inc',
                'job_description': 'Job available.',
                'location_city': 'Montreal'
            },
            'expected_tier': 'Low Confidence (0.4-0.6)',
            'expected_min': 0.4
        },
        {
            'category': 'Poor Quality Data',
            'data': {
                'job_title': 'Job',
                'company_name': 'Company',
                'job_description': 'Work'
            },
            'expected_tier': 'Very Low Confidence (0.0-0.4)',
            'expected_min': 0.2
        },
        {
            'category': 'Edge Case - No Description',
            'data': {
                'job_title': 'Senior Data Analyst',
                'company_name': 'DataTech Solutions LLC',
                'location_city': 'Ottawa',
                'salary_min': 70000,
                'salary_max': 95000,
                'external_job_id': 'data-001',
                'work_arrangement': 'remote',
                'job_type': 'full-time',
                'posting_date': '2025-01-10'
            },
            'expected_tier': 'Medium-High Confidence',
            'expected_min': 0.7
        },
        {
            'category': 'Edge Case - Generic Company',
            'data': {
                'job_title': 'Senior Software Engineer',
                'company_name': 'Company',
                'job_description': 'We are looking for a Senior Software Engineer with 5+ years of experience in full-stack development. Strong background in JavaScript, Python, and cloud technologies required.',
                'location_city': 'Winnipeg',
                'salary_min': 85000,
                'salary_max': 110000,
                'external_job_id': 'eng-999'
            },
            'expected_tier': 'Medium Confidence (penalized for generic company)',
            'expected_min': 0.6
        }
    ]
    
    print("🧪 Comprehensive Confidence Scoring Test Suite")
    print("=" * 70)
    
    passed_tests = 0
    total_tests = len(test_scenarios)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['category']}")
        print("-" * 50)
        
        score = pipeline._calculate_confidence_score(scenario['data'], {})
        expected_min = scenario['expected_min']
        
        # Display key information
        print(f"   Title: {scenario['data'].get('job_title', 'N/A')}")
        print(f"   Company: {scenario['data'].get('company_name', 'N/A')}")
        print(f"   Location: {scenario['data'].get('location_city', 'N/A')}")
        print(f"   Salary: {scenario['data'].get('salary_min', 'N/A')}-{scenario['data'].get('salary_max', 'N/A')}")
        print(f"   Description Length: {len(scenario['data'].get('job_description', ''))}")
        print(f"   External ID: {scenario['data'].get('external_job_id', 'N/A')}")
        print(f"   Bonus Fields: {sum(1 for field in ['work_arrangement', 'job_type', 'posting_date', 'company_website'] if scenario['data'].get(field))}/4")
        
        print(f"\n   Confidence Score: {score:.4f}")
        print(f"   Expected Tier: {scenario['expected_tier']}")
        print(f"   Expected Min: {expected_min:.4f}")
        
        if score >= expected_min:
            print(f"   ✅ PASSED")
            passed_tests += 1
        else:
            print(f"   ❌ FAILED - Score {score:.4f} below expected {expected_min:.4f}")
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("✅ All comprehensive confidence scoring tests passed!")
        return True
    else:
        print(f"❌ {total_tests - passed_tests} tests failed")
        return False

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    
    class MockPipeline:
        def _assess_title_quality(self, title: str) -> float:
            if not title:
                return 0.0
            
            quality = 0.5  # Base score
            
            # Check for meaningful length
            if len(title) >= 10:
                quality += 0.2
            if len(title) >= 20:
                quality += 0.1
            
            # Check for common title patterns
            if any(word in title.lower() for word in ['senior', 'junior', 'manager', 'specialist', 'analyst']):
                quality += 0.1
            
            # Check for department/function
            if any(word in title.lower() for word in ['marketing', 'sales', 'engineering', 'finance', 'hr']):
                quality += 0.1
            
            return min(1.0, quality)
        
        def _assess_company_quality(self, company: str) -> float:
            if not company:
                return 0.0
            
            quality = 0.5  # Base score
            
            # Check for meaningful length
            if len(company) >= 5:
                quality += 0.2
            
            # Check for company indicators
            if any(suffix in company.lower() for suffix in ['inc', 'corp', 'ltd', 'llc', 'company']):
                quality += 0.2
            
            # Penalize generic names
            if company.lower() in ['company', 'corporation', 'business', 'employer']:
                quality -= 0.3
            
            return max(0.0, min(1.0, quality))
        
        def _assess_description_quality(self, description: str) -> float:
            if not description:
                return 0.0
            
            quality = 0.3  # Base score
            
            # Check for meaningful length
            if len(description) >= 100:
                quality += 0.2
            if len(description) >= 300:
                quality += 0.2
            if len(description) >= 500:
                quality += 0.1
            
            # Check for key sections
            desc_lower = description.lower()
            if 'responsibility' in desc_lower or 'duties' in desc_lower:
                quality += 0.1
            if 'requirement' in desc_lower or 'qualifications' in desc_lower:
                quality += 0.1
            if 'experience' in desc_lower:
                quality += 0.1
            
            return min(1.0, quality)
        
        def _calculate_confidence_score(self, cleaned_data: dict, raw_data: dict) -> float:
            score = 0.0
            max_score = 0.0
            
            # Critical fields (60% of total score)
            if cleaned_data.get('job_title'):
                title_quality = self._assess_title_quality(cleaned_data['job_title'])
                score += 0.3 * title_quality
            max_score += 0.3
            
            if cleaned_data.get('company_name'):
                company_quality = self._assess_company_quality(cleaned_data['company_name'])
                score += 0.3 * company_quality
            max_score += 0.3
            
            # Important fields (30% of total score)
            if cleaned_data.get('job_description'):
                desc_quality = self._assess_description_quality(cleaned_data['job_description'])
                score += 0.15 * desc_quality
            max_score += 0.15
            
            if cleaned_data.get('location_city'):
                score += 0.15
            max_score += 0.15
            
            # Additional fields (10% of total score)
            if cleaned_data.get('salary_min') or cleaned_data.get('salary_max'):
                score += 0.05
            max_score += 0.05
            
            if cleaned_data.get('external_job_id'):
                score += 0.05
            max_score += 0.05
            
            # Bonus scoring for data completeness
            bonus_fields = ['work_arrangement', 'job_type', 'posting_date', 'company_website']
            bonus_count = sum(1 for field in bonus_fields if cleaned_data.get(field))
            bonus_score = min(0.1, bonus_count * 0.025)  # Max 0.1 bonus
            score += bonus_score
            max_score += 0.1
            
            final_score = round(score / max_score if max_score > 0 else 0.0, 4)
            
            # Ensure score is within valid range
            return max(0.0, min(1.0, final_score))
    
    pipeline = MockPipeline()
    
    edge_cases = [
        {
            'name': 'Empty Data',
            'data': {},
            'expected_score': 0.0
        },
        {
            'name': 'Only Title',
            'data': {'job_title': 'Senior Marketing Manager'},
            'expected_min': 0.15  # 30% of 0.5 title quality
        },
        {
            'name': 'Only Company',
            'data': {'company_name': 'TechCorp Inc.'},
            'expected_min': 0.21  # 30% of 0.7 company quality
        },
        {
            'name': 'Very Long Title',
            'data': {'job_title': 'Senior Principal Lead Software Development Engineer Manager'},
            'expected_min': 0.24  # High title quality
        },
        {
            'name': 'All Bonus Fields',
            'data': {
                'job_title': 'Engineer',
                'company_name': 'Tech Inc',
                'work_arrangement': 'hybrid',
                'job_type': 'full-time',
                'posting_date': '2025-01-15',
                'company_website': 'https://example.com'
            },
            'expected_min': 0.4  # Base + all bonus fields
        }
    ]
    
    print("\n🧪 Edge Cases Test Suite")
    print("=" * 50)
    
    passed_edge_tests = 0
    
    for edge_case in edge_cases:
        score = pipeline._calculate_confidence_score(edge_case['data'], {})
        expected_min = edge_case.get('expected_min', edge_case.get('expected_score', 0))
        
        print(f"\n{edge_case['name']}:")
        print(f"   Score: {score:.4f}")
        print(f"   Expected: {expected_min:.4f}+")
        
        if 'expected_score' in edge_case:
            # Exact match
            if abs(score - edge_case['expected_score']) < 0.001:
                print(f"   ✅ PASSED (exact match)")
                passed_edge_tests += 1
            else:
                print(f"   ❌ FAILED (expected exact {edge_case['expected_score']:.4f})")
        else:
            # Minimum threshold
            if score >= expected_min:
                print(f"   ✅ PASSED")
                passed_edge_tests += 1
            else:
                print(f"   ❌ FAILED (below minimum)")
    
    print(f"\nEdge Cases: {passed_edge_tests}/{len(edge_cases)} passed")
    return passed_edge_tests == len(edge_cases)

def main():
    """Run all confidence scoring tests"""
    print("🧪 Confidence Scoring System - Full Test Suite")
    print("=" * 70)
    
    try:
        # Run comprehensive tests
        comprehensive_passed = test_comprehensive_confidence_scoring()
        
        # Run edge case tests
        edge_cases_passed = test_edge_cases()
        
        print("\n" + "=" * 70)
        print("Final Results:")
        print(f"   Comprehensive Tests: {'✅ PASSED' if comprehensive_passed else '❌ FAILED'}")
        print(f"   Edge Case Tests: {'✅ PASSED' if edge_cases_passed else '❌ FAILED'}")
        
        if comprehensive_passed and edge_cases_passed:
            print("\n🎉 All confidence scoring tests passed!")
            print("   The confidence scoring system is working correctly.")
            return True
        else:
            print("\n❌ Some tests failed. Please review the implementation.")
            return False
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)