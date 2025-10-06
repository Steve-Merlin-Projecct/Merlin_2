#!/usr/bin/env python3
"""
Test script for AI Analysis with sample job data
Tests the enhanced AI analysis system with realistic job postings
"""

import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.ai_job_description_analysis.normalized_db_writer import NormalizedAnalysisWriter
from modules.database.database_manager import DatabaseManager

def create_sample_jobs():
    """Create realistic sample job data for testing"""
    
    sample_jobs = [
        {
            "id": "test-job-001",
            "title": "Digital Marketing Manager",
            "company_name": "TechStart Solutions Inc.",
            "description": """
We're seeking an experienced Digital Marketing Manager to lead our marketing efforts and drive growth for our B2B SaaS platform. 

Key Responsibilities:
- Develop and execute comprehensive digital marketing strategies
- Manage PPC campaigns across Google Ads and social media platforms
- Lead content marketing initiatives including blog posts, whitepapers, and case studies
- Collaborate with sales team to generate qualified leads
- Analyze marketing performance using Google Analytics and HubSpot
- Manage marketing automation workflows and email campaigns

Requirements:
- 3-5 years experience in B2B digital marketing
- Proven track record with Google Ads, Facebook Ads, and LinkedIn advertising
- Experience with marketing automation tools (HubSpot, Marketo, or Pardot)
- Strong analytical skills and proficiency in Google Analytics
- Bachelor's degree in Marketing, Business, or related field
- Google Ads and Google Analytics certifications preferred

What We Offer:
- Competitive salary $65,000 - $80,000 CAD
- Comprehensive health and dental benefits
- RRSP matching up to 4%
- Flexible hybrid work arrangement (2-3 days in office)
- Professional development budget of $2,000 annually
- Stock options program

Location: Edmonton, Alberta, Canada (Hybrid - 123 Main Street, Edmonton, AB, Canada)
Travel: Occasional travel to conferences (10-15% of time)

To apply, please send your resume and cover letter to careers@techstartsolutions.ca
Include examples of successful campaigns you've managed.
            """,
            "location": "Edmonton, AB",
            "salary_min": 65000,
            "salary_max": 80000,
            "job_type": "Full-time",
            "work_arrangement": "Hybrid"
        },
        {
            "id": "test-job-002", 
            "title": "Senior Data Scientist",
            "company_name": "AI Innovations Corp",
            "description": """
Join our rapidly growing AI team as a Senior Data Scientist! We're looking for a passionate individual to help build cutting-edge machine learning solutions.

Responsibilities:
- Design and implement machine learning models for predictive analytics
- Work with large datasets using Python, SQL, and cloud platforms
- Collaborate with cross-functional teams to deploy ML solutions
- Mentor junior data scientists and analysts
- Present findings to executive leadership team

Must-Have Qualifications:
- PhD or Master's in Computer Science, Statistics, or related field
- 5+ years experience in machine learning and data science
- Expert-level Python programming skills
- Experience with TensorFlow, PyTorch, or similar ML frameworks
- Strong background in statistics and experimental design
- AWS or GCP cloud platform experience

Preferred Qualifications:
- Experience with MLOps and model deployment
- Publications in top-tier conferences
- Leadership experience managing technical teams

Compensation Package:
- Base salary: $120,000 - $150,000 USD
- Annual bonus up to 20% of base salary
- Equity participation program
- Comprehensive benefits including health, dental, vision
- Unlimited PTO policy
- $5,000 annual learning and development budget

This is a remote-first position open to candidates across North America.
Occasional travel to our San Francisco headquarters required (quarterly team meetings).

Apply at: jobs@aiinnovations.com
Please include a portfolio of your previous ML projects.

We are an equal opportunity employer committed to diversity and inclusion.
            """,
            "location": "Remote (North America)",
            "salary_min": 120000,
            "salary_max": 150000,
            "job_type": "Full-time",
            "work_arrangement": "Remote"
        },
        {
            "id": "test-job-003",
            "title": "Social Media Coordinator - URGENT HIRING!!!",
            "company_name": "QuickCash Marketing Ltd",
            "description": """
🔥🔥🔥 MAKE $5000/WEEK FROM HOME!!! 🔥🔥🔥

Are you tired of your boring 9-5 job? Want to make SERIOUS MONEY working from home?

We're hiring IMMEDIATELY for Social Media Coordinators! NO EXPERIENCE NECESSARY!

What you'll do:
- Post on social media (super easy!)
- Share our amazing products with friends
- Recruit other coordinators to join our team
- Earn commissions on every sale!

Requirements:
- Must be 18+ years old
- Own a smartphone or computer
- Willing to invest $299 starter fee (you'll make this back in your first week!)
- Motivated to succeed and earn BIG MONEY!

Earning Potential:
- $2,000-$5,000 per week GUARANTEED!
- Unlimited earning potential 
- Work your own hours
- Be your own boss!

BONUS: First 10 applicants get our exclusive training program FREE ($500 value)!

To get started, send $299 processing fee via PayPal to: quickcash@fastmoney.biz
Include your full name, address, and phone number.

⚠️ SERIOUS INQUIRIES ONLY - This opportunity won't last long!

Contact us at: hiring@quickcashmarketing.biz
Text "MONEY" to 555-CASH-NOW for instant response!

*Results not typical. Individual results may vary. Investment required.
            """,
            "location": "Work from Home",
            "salary_min": 104000,  # $2000/week * 52 weeks
            "salary_max": 260000,  # $5000/week * 52 weeks
            "job_type": "Contract",
            "work_arrangement": "Remote"
        }
    ]
    
    return sample_jobs

def test_ai_analysis():
    """Test the AI analysis system with sample data"""
    
    print("🧪 Testing AI Analysis System with Sample Data")
    print("=" * 60)
    
    # Create sample jobs
    sample_jobs = create_sample_jobs()
    
    try:
        # Initialize components
        print("📊 Initializing AI analyzer and database connection...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Initialize AI analyzer
        ai_analyzer = GeminiJobAnalyzer()
        
        # Initialize normalized writer
        normalized_writer = NormalizedAnalysisWriter(db_manager)
        
        print(f"✅ Components initialized successfully")
        print(f"📝 Testing with {len(sample_jobs)} sample jobs")
        
        # Test each job individually for detailed output
        for i, job in enumerate(sample_jobs, 1):
            print(f"\n🔍 Testing Job {i}: {job['title']}")
            print(f"   Company: {job['company_name']}")
            print(f"   Location: {job['location']}")
            
            try:
                # Analyze single job
                analysis_response = ai_analyzer.analyze_jobs_batch([job])
                
                if analysis_response and analysis_response.get('success') and analysis_response.get('results'):
                    analysis_results = analysis_response['results']
                    result = analysis_results[0]
                    
                    print(f"   ✅ Analysis completed successfully")
                    print(f"   📊 Analysis sections found:")
                    
                    # Check key sections
                    sections = [
                        'authenticity_check',
                        'classification', 
                        'structured_data',
                        'stress_level_analysis',
                        'red_flags',
                        'cover_letter_insight'
                    ]
                    
                    for section in sections:
                        if section in result:
                            print(f"      ✓ {section}")
                        else:
                            print(f"      ✗ {section} (missing)")
                    
                    # Show key analysis insights
                    auth_check = result.get('authenticity_check', {})
                    if auth_check:
                        print(f"   🔍 Authenticity: {auth_check.get('is_authentic')} - {auth_check.get('reasoning', 'No reasoning')[:100]}...")
                    
                    classification = result.get('classification', {})
                    if classification:
                        print(f"   🏢 Industry: {classification.get('sub_industry')} | Function: {classification.get('job_function')}")
                    
                    # Check compensation currency
                    structured_data = result.get('structured_data', {})
                    compensation = structured_data.get('compensation', {})
                    if compensation:
                        currency = compensation.get('compensation_currency', 'Not specified')
                        total_comp = compensation.get('est_total_compensation', 'Not estimated')
                        print(f"   💰 Compensation: {total_comp} {currency}")
                    
                    # Check office location parsing
                    work_arrangement = structured_data.get('work_arrangement', {})
                    office_location = work_arrangement.get('office_location', 'Not specified')
                    print(f"   📍 Office Location: {office_location}")
                    
                    # Check cover letter insight
                    cover_letter = result.get('cover_letter_insight', {})
                    pain_point = cover_letter.get('employer_pain_point', {})
                    if pain_point:
                        print(f"   💡 Pain Point: {pain_point.get('pain_point', 'Not identified')[:80]}...")
                    
                    # Test database storage
                    print(f"   💾 Testing database storage...")
                    storage_stats = normalized_writer.save_analysis_results([result])
                    print(f"   📊 Storage results: {storage_stats}")
                    
                else:
                    print(f"   ❌ Analysis failed - no results returned")
                    
            except Exception as e:
                print(f"   ❌ Error analyzing job: {str(e)}")
        
        print(f"\n🎉 Testing completed!")
        print(f"📈 Check the jobs table and normalized tables for stored results")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_analysis()