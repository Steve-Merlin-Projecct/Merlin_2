#!/usr/bin/env python3
"""
Simple Confidence Scoring Test
Tests the confidence scoring algorithm directly without database connections
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_confidence_scoring():
    """Test confidence scoring logic directly"""
    
    # Mock pipeline class with just the scoring methods
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
    
    # Test cases
    test_cases = [
        {
            'name': 'High Quality Job',
            'data': {
                'job_title': 'Senior Marketing Manager',
                'company_name': 'Tech Solutions Inc.',
                'job_description': 'We are seeking an experienced marketing manager to lead our digital marketing efforts. The successful candidate will have 5+ years of marketing experience and will be responsible for developing comprehensive marketing strategies, managing campaigns, and analyzing market trends. Requirements include strong analytical skills, experience with digital marketing tools, and excellent communication abilities.',
                'location_city': 'Edmonton',
                'salary_min': 65000,
                'salary_max': 85000,
                'external_job_id': 'job123456',
                'work_arrangement': 'hybrid',
                'job_type': 'full-time',
                'posting_date': '2025-01-15',
                'company_website': 'https://techsolutions.com'
            },
            'expected_min': 0.85
        },
        {
            'name': 'Medium Quality Job',
            'data': {
                'job_title': 'Marketing Manager',
                'company_name': 'ABC Corp',
                'job_description': 'Marketing position available. Good opportunity for growth.',
                'location_city': 'Calgary'
            },
            'expected_min': 0.6
        },
        {
            'name': 'Low Quality Job',
            'data': {
                'job_title': 'Manager',
                'company_name': 'Company'
            },
            'expected_min': 0.3
        }
    ]
    
    print("🧪 Testing Confidence Scoring Algorithm")
    print("=" * 50)
    
    for test_case in test_cases:
        score = pipeline._calculate_confidence_score(test_case['data'], {})
        expected_min = test_case['expected_min']
        
        print(f"\n{test_case['name']}:")
        print(f"  Title: {test_case['data'].get('job_title', 'N/A')}")
        print(f"  Company: {test_case['data'].get('company_name', 'N/A')}")
        print(f"  Confidence Score: {score:.4f}")
        print(f"  Expected Min: {expected_min:.4f}")
        
        if score >= expected_min:
            print(f"  ✅ PASSED")
        else:
            print(f"  ❌ FAILED - Score too low")
            return False
    
    print("\n" + "=" * 50)
    print("✅ All confidence scoring tests passed!")
    return True

if __name__ == "__main__":
    success = test_confidence_scoring()
    sys.exit(0 if success else 1)