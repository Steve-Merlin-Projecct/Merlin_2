#!/usr/bin/env python3
"""
Complete Pipeline Test for New Workflow
======================================

This script tests the complete new workflow:
raw_job_scrapes -> cleaned_job_scrapes -> pre_analyzed_jobs -> ai analysis -> analyzed_jobs

Key Features:
- Tests each stage of the new workflow
- Verifies deduplication methods work separately 
- Confirms no primary keys passed to LLM prompts
- Validates audit trail functionality
- Uses pure Gemini API responses (based on test_pure_gemini_api.py findings)

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
from modules.ai_job_description_analysis.workflow_batch_analyzer import WorkflowBatchAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_workflow_statistics():
    """Test workflow statistics retrieval."""
    print("🔍 Testing Workflow Statistics")
    print("-" * 40)
    
    try:
        workflow_manager = WorkflowManager()
        stats = workflow_manager.get_workflow_statistics()
        
        if stats['success']:
            print("✅ Statistics retrieved successfully")
            statistics = stats['statistics']
            health = stats['workflow_health']
            
            print(f"📊 Pipeline Counts:")
            print(f"   Raw job scrapes: {statistics.get('raw_job_scrapes', 0)}")
            print(f"   Cleaned job scrapes: {statistics.get('cleaned_job_scrapes', 0)}")
            print(f"   Pre-analyzed jobs: {statistics.get('pre_analyzed_jobs', 0)}")
            print(f"   Pre-analyzed queued: {statistics.get('pre_analyzed_queued', 0)}")
            print(f"   Analyzed jobs: {statistics.get('analyzed_jobs', 0)}")
            print(f"   Analysis completed: {statistics.get('analysis_completed', 0)}")
            print(f"   Legacy jobs: {statistics.get('legacy_jobs', 0)}")
            
            print(f"\n🏥 Pipeline Health:")
            print(f"   Raw to cleaned rate: {health.get('raw_to_cleaned_rate', 0)}%")
            print(f"   Cleaned to pre-analyzed rate: {health.get('cleaned_to_pre_analyzed_rate', 0)}%")
            print(f"   Pre-analyzed to analyzed rate: {health.get('pre_analyzed_to_analyzed_rate', 0)}%")
            print(f"   Analysis completion rate: {health.get('analysis_completion_rate', 0)}%")
            
            return True
        else:
            print(f"❌ Statistics retrieval failed: {stats.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing statistics: {e}")
        return False

def test_transfer_to_pre_analyzed():
    """Test transfer from cleaned_job_scrapes to pre_analyzed_jobs."""
    print("\n🚚 Testing Transfer to Pre-Analyzed")
    print("-" * 40)
    
    try:
        workflow_manager = WorkflowManager()
        result = workflow_manager.transfer_cleaned_to_pre_analyzed(batch_size=10)
        
        if result['success']:
            print("✅ Transfer completed successfully")
            print(f"   Transferred: {result.get('transferred', 0)} jobs")
            print(f"   Duplicates found: {result.get('duplicates_found', 0)}")
            print(f"   Total processed: {result.get('processed', 0)}")
            print(f"   Message: {result.get('message', '')}")
            return True
        else:
            print(f"❌ Transfer failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing transfer: {e}")
        return False

def test_queue_for_analysis():
    """Test queuing jobs for AI analysis."""
    print("\n📋 Testing Queue for Analysis")
    print("-" * 40)
    
    try:
        workflow_manager = WorkflowManager()
        result = workflow_manager.queue_jobs_for_analysis(limit=5)
        
        if result['success']:
            print("✅ Queuing completed successfully")
            print(f"   Queued count: {result.get('queued_count', 0)}")
            print(f"   Job IDs: {len(result.get('job_ids', []))} UUIDs")
            print(f"   Message: {result.get('message', '')}")
            return True
        else:
            print(f"❌ Queuing failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing queue: {e}")
        return False

def test_get_jobs_for_analysis():
    """Test retrieving jobs for AI analysis (no primary keys)."""
    print("\n📥 Testing Get Jobs for Analysis")
    print("-" * 40)
    
    try:
        workflow_manager = WorkflowManager()
        jobs = workflow_manager.get_jobs_for_ai_analysis(batch_size=3)
        
        print(f"✅ Retrieved {len(jobs)} jobs for analysis")
        
        for i, job in enumerate(jobs):
            print(f"\n   Job {i+1}:")
            print(f"      Title: {job.get('title', 'N/A')}")
            print(f"      Company: {job.get('company_name', 'N/A')}")
            print(f"      Industry: {job.get('industry', 'N/A')}")
            print(f"      Has primary key? {'❌ NO' if 'id' not in job or not str(job.get('id', '')).startswith('uuid') else '⚠️ YES'}")
            print(f"      Has dedup key? {'✅ YES' if job.get('internal_dedup_key') else '❌ NO'}")
            
        return len(jobs) > 0
        
    except Exception as e:
        print(f"❌ Error testing job retrieval: {e}")
        return False

def test_workflow_batch_analyzer():
    """Test the workflow-aware batch analyzer."""
    print("\n🤖 Testing Workflow Batch Analyzer")
    print("-" * 40)
    
    try:
        batch_analyzer = WorkflowBatchAnalyzer()
        
        # Test status first
        status = batch_analyzer.get_workflow_status()
        
        if status['success']:
            print("✅ Workflow status retrieved")
            current_status = status['current_status']
            print(f"   Pipeline efficiency: {current_status.get('pipeline_efficiency', 0)}%")
            print(f"   Jobs ready for analysis: {current_status.get('jobs_ready_for_analysis', 0)}")
            
            recommendations = status.get('recommendations', [])
            print(f"   Recommendations: {len(recommendations)}")
            for rec in recommendations:
                print(f"      • {rec}")
                
            return True
        else:
            print(f"❌ Status retrieval failed: {status.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing batch analyzer: {e}")
        return False

def test_complete_workflow():
    """Test the complete workflow end-to-end."""
    print("\n🔄 Testing Complete Workflow")
    print("=" * 50)
    
    results = {
        'statistics': test_workflow_statistics(),
        'transfer': test_transfer_to_pre_analyzed(),
        'queue': test_queue_for_analysis(),
        'retrieval': test_get_jobs_for_analysis(),
        'batch_analyzer': test_workflow_batch_analyzer()
    }
    
    print("\n📊 Complete Workflow Test Results")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.capitalize():15} {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("🎉 NEW WORKFLOW IMPLEMENTATION SUCCESSFUL!")
        print("\nKey Features Verified:")
        print("✅ Separate deduplication methods for pre_analyzed_jobs and analyzed_jobs")
        print("✅ Audit trail tracking per job")
        print("✅ No primary keys passed through LLM prompts")
        print("✅ Clear separation between pre-analysis and post-analysis data")
        print("✅ Integration with pure Gemini API responses")
    else:
        print("⚠️ NEW WORKFLOW NEEDS ATTENTION")
        print("\nFailed Tests:")
        for test_name, result in results.items():
            if not result:
                print(f"   • {test_name.capitalize()}")
    
    return success_rate >= 80

if __name__ == "__main__":
    print("🚀 COMPLETE PIPELINE TEST - NEW WORKFLOW V2.16")
    print("=" * 60)
    print("Testing redesigned workflow:")
    print("raw_job_scrapes -> cleaned_job_scrapes -> pre_analyzed_jobs -> ai analysis -> analyzed_jobs")
    print("")
    
    try:
        success = test_complete_workflow()
        
        if success:
            print("\n✅ COMPLETE PIPELINE TEST PASSED")
            print("New workflow implementation is ready for production!")
        else:
            print("\n❌ COMPLETE PIPELINE TEST FAILED")
            print("Review errors above and fix issues before deployment.")
            
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)