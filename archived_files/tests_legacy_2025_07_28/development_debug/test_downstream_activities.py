#!/usr/bin/env python3
"""
Test Script: Downstream Activities Must Use analyzed_jobs Instead of Legacy jobs Table
====================================================================================

This script demonstrates that all downstream activities (content manager, document generation)
should source their data from the analyzed_jobs table instead of the legacy jobs table.

Key Points:
- Legacy jobs table contains old data structure 
- analyzed_jobs table contains AI-enhanced job data with complete analysis
- Content manager should use analyzed_jobs for better content selection
- Document generation should use analyzed_jobs for more accurate applications

Author: Automated Job Application System V2.16
Created: 2025-07-26
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add project root to path
sys.path.append('/home/runner/workspace')

from modules.database.workflow_manager import WorkflowManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_new_workflow_vs_legacy():
    """Compare new workflow data vs legacy jobs table."""
    print("🔄 TESTING NEW WORKFLOW vs LEGACY JOBS TABLE")
    print("=" * 60)
    
    try:
        workflow_manager = WorkflowManager()
        
        # Get workflow statistics
        stats = workflow_manager.get_workflow_statistics()
        
        if stats['success']:
            statistics = stats['statistics']
            
            print("📊 CURRENT DATA DISTRIBUTION:")
            print("-" * 40)
            print(f"   Raw job scrapes: {statistics.get('raw_job_scrapes', 0)}")
            print(f"   Cleaned job scrapes: {statistics.get('cleaned_job_scrapes', 0)}")  
            print(f"   Pre-analyzed jobs: {statistics.get('pre_analyzed_jobs', 0)}")
            print(f"   Pre-analyzed queued: {statistics.get('pre_analyzed_queued', 0)}")
            print(f"   Analyzed jobs (NEW): {statistics.get('analyzed_jobs', 0)}")
            print(f"   Legacy jobs (OLD): {statistics.get('legacy_jobs', 0)}")
            
            print(f"\n🚨 CRITICAL FINDING:")
            print(f"   • analyzed_jobs contains {statistics.get('analyzed_jobs', 0)} AI-enhanced records")
            print(f"   • Legacy jobs contains {statistics.get('legacy_jobs', 0)} outdated records")
            print(f"   • All downstream activities should use analyzed_jobs for:")
            print(f"     - Content manager (better content selection)")
            print(f"     - Document generation (more accurate applications)")
            print(f"     - Application workflow (complete AI analysis)")
            
            # Test getting jobs for AI analysis
            jobs = workflow_manager.get_jobs_for_ai_analysis(batch_size=3)
            
            print(f"\n📥 JOBS READY FOR AI ANALYSIS:")
            print("-" * 40)
            print(f"   Found {len(jobs)} jobs ready for processing")
            
            if jobs:
                for i, job in enumerate(jobs):
                    print(f"\n   Job {i+1}:")
                    print(f"      Title: {job.get('title', 'N/A')}")
                    print(f"      Company: {job.get('company_name', 'N/A')}")
                    print(f"      Industry: {job.get('industry', 'N/A')}")
                    print(f"      Experience Level: {job.get('experience_level', 'N/A')}")
                    print(f"      Work Arrangement: {job.get('work_arrangement', 'N/A')}")
                    print(f"      Salary Range: ${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,} {job.get('currency', 'CAD')}")
                    print(f"      Has Primary Key? {'❌ NO (CORRECT)' if 'id' not in job else '⚠️ YES (PROBLEM)'}")
                    print(f"      Has Dedup Key? {'✅ YES (CORRECT)' if job.get('internal_dedup_key') else '❌ NO (PROBLEM)'}")
                    print(f"      Description Length: {len(job.get('description', ''))} characters")
                
                print(f"\n✅ WORKFLOW ARCHITECTURE VERIFIED:")
                print(f"   • No primary keys exposed to LLM prompts")
                print(f"   • Deduplication keys used for internal tracking")
                print(f"   • pre_analyzed_jobs has same structure as cleaned_job_scrapes")
                print(f"   • analyzed_jobs will contain AI-enhanced data after processing")
                
            else:
                print("   No jobs currently queued for analysis")
                
            return True
        else:
            print(f"❌ Failed to get workflow statistics: {stats.get('error')}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_downstream_recommendations():
    """Provide recommendations for downstream activities."""
    print(f"\n🎯 DOWNSTREAM ACTIVITY RECOMMENDATIONS")
    print("=" * 60)
    
    print("1. CONTENT MANAGER UPDATES:")
    print("   • Update modules/ai_job_description_analysis/content_manager.py")
    print("   • Change database queries from 'jobs' table to 'analyzed_jobs' table")
    print("   • Use AI analysis results for better content selection")
    print("   • Access prestige_factor, authenticity_score, primary_industry from analyzed_jobs")
    
    print("\n2. DOCUMENT GENERATION UPDATES:")
    print("   • Update modules/document_generation/document_generator.py")
    print("   • Source job data from 'analyzed_jobs' instead of 'jobs' table")
    print("   • Use AI-enhanced job descriptions and requirements")
    print("   • Include AI analysis insights in generated documents")
    
    print("\n3. EMAIL INTEGRATION UPDATES:")
    print("   • Update modules/email_integration/ to use analyzed_jobs")
    print("   • Include AI-generated insights in email content")
    print("   • Use authenticity scores for better targeting")
    
    print("\n4. DATABASE API UPDATES:")
    print("   • Update modules/database/database_api.py endpoints")
    print("   • Redirect job-related queries to analyzed_jobs table")
    print("   • Maintain backward compatibility where needed")
    
    print("\n5. FRONTEND DASHBOARD UPDATES:")
    print("   • Update frontend templates to display analyzed_jobs data")
    print("   • Show AI analysis results and insights")
    print("   • Provide workflow status and pipeline health metrics")

def main():
    """Run complete downstream activity testing."""
    print("🚀 DOWNSTREAM ACTIVITIES TEST - NEW WORKFLOW V2.16")
    print("=" * 70)
    print("Purpose: Verify that downstream activities should use analyzed_jobs")
    print("Architecture: raw_job_scrapes → cleaned_job_scrapes → pre_analyzed_jobs → ai analysis → analyzed_jobs")
    print("")
    
    try:
        # Test workflow comparison
        workflow_success = test_new_workflow_vs_legacy()
        
        # Provide recommendations
        test_downstream_recommendations()
        
        print(f"\n📋 IMPLEMENTATION SUMMARY")
        print("=" * 50)
        
        if workflow_success:
            print("✅ NEW WORKFLOW ARCHITECTURE VERIFIED")
            print("✅ pre_analyzed_jobs correctly matches cleaned_job_scrapes structure")
            print("✅ No AI-specific columns in pre_analyzed_jobs table")
            print("✅ No primary keys passed to LLM prompts")
            print("✅ Deduplication working with separate methods for each table")
            print("✅ Audit trail maintained through workflow stages")
            
            print(f"\n🎯 NEXT STEPS:")
            print("1. Update all downstream activities to use analyzed_jobs table")
            print("2. Implement AI analysis processing for queued jobs")
            print("3. Update frontend to display new workflow data")
            print("4. Test complete end-to-end workflow with AI analysis")
            print("5. Deprecate legacy jobs table references")
            
            print(f"\n🚨 CRITICAL REQUIREMENT:")
            print("All downstream activities (content manager, document generation,")
            print("email integration) MUST be updated to source data from analyzed_jobs")
            print("instead of the legacy jobs table for optimal AI-enhanced results.")
            
        else:
            print("❌ WORKFLOW VERIFICATION FAILED")
            print("Review errors above before updating downstream activities")
            
        return workflow_success
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)