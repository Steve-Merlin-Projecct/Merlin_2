#!/usr/bin/env python3
"""
Test Steve Glen Job Title Eligibility Integration

Validates that the user eligibility module correctly matches Steve Glen's
target job titles and assigns appropriate compatibility scores.
"""

import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_steve_glen_job_title_matching():
    """Test the job title matching implementation"""
    print("=" * 70)
    print("STEVE GLEN JOB TITLE ELIGIBILITY TEST")
    print("=" * 70)
    
    try:
        from modules.workflow.application_orchestrator import ApplicationOrchestrator
        orchestrator = ApplicationOrchestrator()
        
        # Test job scenarios with Steve Glen's target titles
        test_jobs = [
            {
                'id': 'test-1',
                'job_title': 'Marketing Manager',
                'primary_industry': 'marketing',
                'salary_low': 70000,
                'salary_high': 85000,
                'office_city': 'Edmonton',
                'office_province': 'Alberta',
                'office_country': 'Canada',
                'remote_options': 'hybrid',
                'authenticity_score': 0.9,
                'prestige_factor': 7
            },
            {
                'id': 'test-2', 
                'job_title': 'Communications Specialist',
                'primary_industry': 'communications',
                'salary_low': 65000,
                'salary_high': 75000,
                'office_city': 'Calgary',
                'office_province': 'Alberta', 
                'office_country': 'Canada',
                'remote_options': 'remote',
                'authenticity_score': 0.85,
                'prestige_factor': 6
            },
            {
                'id': 'test-3',
                'job_title': 'Brand Strategist',
                'primary_industry': 'marketing',
                'salary_low': 75000,
                'salary_high': 90000,
                'office_city': 'Toronto',
                'office_province': 'Ontario',
                'office_country': 'Canada',
                'remote_options': 'remote',
                'authenticity_score': 0.92,
                'prestige_factor': 8
            },
            {
                'id': 'test-4',
                'job_title': 'Senior Marketing Communications Manager',
                'primary_industry': 'marketing',
                'salary_low': 80000,
                'salary_high': 100000,
                'office_city': 'Vancouver',
                'office_province': 'British Columbia',
                'office_country': 'Canada',
                'remote_options': 'hybrid',
                'authenticity_score': 0.88,
                'prestige_factor': 9
            },
            {
                'id': 'test-5',
                'job_title': 'Software Developer',  # Should score lower
                'primary_industry': 'technology',
                'salary_low': 85000,
                'salary_high': 105000,
                'office_city': 'Edmonton',
                'office_province': 'Alberta',
                'office_country': 'Canada',
                'remote_options': 'hybrid',
                'authenticity_score': 0.9,
                'prestige_factor': 7
            }
        ]
        
        # Test Steve Glen's base preferences
        base_preferences = {
            'preferred_city': 'edmonton',
            'preferred_province_state': 'alberta',
            'preferred_country': 'canada',
            'work_arrangement': 'hybrid',
            'salary_minimum': 65000
        }
        
        preferred_industries = {'marketing', 'communications', 'strategy'}
        preference_packages = []
        
        print("\n📋 Testing Job Title Compatibility:")
        print("-" * 50)
        
        results = []
        for job in test_jobs:
            # Test title matching specifically
            title_score = orchestrator.calculate_job_title_compatibility(job)
            
            # Calculate overall compatibility
            total_score = orchestrator.calculate_job_compatibility(
                job, base_preferences, preferred_industries, preference_packages
            )
            
            results.append({
                'job_title': job['job_title'],
                'title_score': title_score,
                'total_score': total_score,
                'meets_threshold': total_score >= orchestrator.min_compatibility_score
            })
            
            status = "✅ ELIGIBLE" if total_score >= orchestrator.min_compatibility_score else "❌ REJECTED"
            print(f"{job['job_title']:<35} | Title: {title_score:4.1f} | Total: {total_score:5.1f} | {status}")
        
        # Test preference matching workflow
        print(f"\n🔍 Testing Complete Preference Matching Workflow:")
        print("-" * 50)
        
        matched_jobs = orchestrator.apply_preference_matching(test_jobs)
        
        print(f"Input jobs: {len(test_jobs)}")
        print(f"Matched jobs: {len(matched_jobs)}")
        print(f"Success rate: {len(matched_jobs)/len(test_jobs)*100:.1f}%")
        
        print(f"\n📊 Matched Jobs Details:")
        for job in matched_jobs:
            print(f"  • {job['job_title']} (Score: {job['compatibility_score']:.1f})")
        
        # Validate Steve Glen's target titles are in the system
        print(f"\n🎯 Steve Glen's Target Titles:")
        print("-" * 50)
        for i, title in enumerate(orchestrator.steve_glen_target_titles, 1):
            print(f"{i:2d}. {title}")
        
        # Summary
        print(f"\n📈 ELIGIBILITY TEST SUMMARY:")
        print("=" * 50)
        
        target_jobs = [r for r in results if r['title_score'] >= 15]  # Jobs with good title matches
        eligible_jobs = [r for r in results if r['meets_threshold']]
        
        print(f"Total test jobs: {len(results)}")
        print(f"Target title matches: {len(target_jobs)} ({len(target_jobs)/len(results)*100:.1f}%)")
        print(f"Overall eligible: {len(eligible_jobs)} ({len(eligible_jobs)/len(results)*100:.1f}%)")
        print(f"Target titles configured: {len(orchestrator.steve_glen_target_titles)}")
        print(f"Minimum compatibility threshold: {orchestrator.min_compatibility_score}")
        
        # Validate that target job titles score well
        target_title_success = all(
            r['meets_threshold'] for r in results 
            if any(target.lower() in r['job_title'].lower() 
                  for target in orchestrator.steve_glen_target_titles[:5])  # Check first 5 target titles
        )
        
        if target_title_success:
            print(f"\n✅ SUCCESS: Steve Glen's target job titles are properly prioritized!")
        else:
            print(f"\n⚠️  WARNING: Some target job titles may not meet eligibility threshold")
        
        return {
            'total_jobs': len(results),
            'target_matches': len(target_jobs),
            'eligible_jobs': len(eligible_jobs),
            'target_titles_count': len(orchestrator.steve_glen_target_titles),
            'success': target_title_success
        }
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return {'success': False, 'error': str(e)}

def main():
    """Run the Steve Glen job eligibility test"""
    test_results = test_steve_glen_job_title_matching()
    
    if test_results.get('success'):
        print(f"\n🎉 STEVE GLEN JOB ELIGIBILITY INTEGRATION: SUCCESSFUL")
    else:
        print(f"\n💥 STEVE GLEN JOB ELIGIBILITY INTEGRATION: FAILED")
        if 'error' in test_results:
            print(f"Error: {test_results['error']}")

if __name__ == "__main__":
    main()