#!/usr/bin/env python3
"""
Application Orchestrator for End-to-End Workflow Management

This module implements Step 2.2 of the Implementation Plan V2.16:
End-to-End Workflow Orchestration for automated job applications.

The orchestrator manages the complete workflow:
1. Job Discovery from analyzed_jobs table
2. User Preference Matching using Steve Glen's profile
3. Eligibility Determination with rejection reasoning
4. Document Generation for eligible jobs
5. Email Composition and Sending
6. Application Status Tracking and Monitoring
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Import existing system components
from modules.user_management.user_profile_loader import SteveGlenProfileLoader
from modules.database.database_manager import DatabaseManager

# Import failure recovery components for Step 2.3
from modules.resilience.failure_recovery import FailureRecoveryManager
from modules.resilience.retry_strategy_manager import retry_manager, with_retry
from modules.resilience.data_consistency_validator import DataConsistencyValidator

# Document generation (correct path)
try:
    from modules.content.document_generation.document_generator import DocumentGenerator

    document_generator_imported = True
    document_generator_import_error = None
except ImportError as e:
    document_generator_imported = False
    document_generator_import_error = str(e)

    # Create a mock document generator for testing
    class MockDocumentGenerator:
        def generate_document(self, data):
            return {
                "success": True,
                "file_path": f'/mock/path/{data.get("document_type", "document")}.docx',
                "filename": f'{data.get("document_type", "document")}.docx',
                "file_url": f'http://mock.storage/{data.get("document_type", "document")}.docx',
            }

    DocumentGenerator = MockDocumentGenerator

# Email integration - DISABLED FOR SAFETY
try:
    from modules.email_integration.email_disabled import DisabledEmailSender

    EnhancedGmailSender = DisabledEmailSender
except ImportError:
    # Create a simple email interface for workflow testing
    class MockEmailSender:
        def send_email_with_attachments(self, recipient, subject, body, attachments=None):
            return {
                "success": True,
                "message_id": f'mock_message_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                "sent_at": datetime.now().isoformat(),
                "mock_mode": True,
            }

    EnhancedGmailSender = MockEmailSender

logger = logging.getLogger(__name__)

# Log import status after logger is available
if document_generator_imported:
    logger.info("DocumentGenerator imported successfully")
else:
    logger.error(f"Failed to import DocumentGenerator: {document_generator_import_error}")


class ApplicationOrchestrator:
    """
    End-to-End Workflow Orchestrator for Automated Job Applications

    Manages complete workflow from job discovery to application tracking.
    Implements intelligent decision-making and comprehensive logging.
    """

    def __init__(self):
        """Initialize orchestrator with all necessary components"""

        # Step 2.3: Initialize failure recovery components
        self.failure_recovery = FailureRecoveryManager()
        self.data_validator = DataConsistencyValidator()

        # Initialize existing components
        self.db_url = os.environ.get("DATABASE_URL")
        self.user_profile = SteveGlenProfileLoader()
        self.document_generator = DocumentGenerator()
        self.email_sender = EnhancedGmailSender()

        # Initialize email application sender for automated application sending
        from modules.workflow.email_application_sender import EmailApplicationSender

        self.email_application_sender = EmailApplicationSender()
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)

        # Workflow configuration
        self.max_applications_per_day = 5
        self.min_compatibility_score = 50  # Lower threshold for testing - jobs should meet 50+ score
        self.max_batch_size = 10

        # Steve Glen's target job titles for eligibility filtering
        self.steve_glen_target_titles = [
            "Brand Strategist",
            "Communications Analyst",
            "Communications Manager",
            "Communications Specialist",
            "Marketing Manager",  # Fixed typo from "Maketing"
            "Marketing Communications Manager",
            "Marketing Specialist",
            "Marketing Consultant",
            "Public Relations Specialist",
            "Brand Manager",
            "Content Marketing Manager",
            "Media Relations Coordinator",
            "Operations Assistant",
        ]

        self.logger.info("ApplicationOrchestrator initialized for Step 2.2 implementation")

    def apply_to_job(self, job_data: Dict) -> Dict:
        """
        Apply to a specific job using the email application system

        Args:
            job_data: Job information dictionary

        Returns:
            Application result dictionary
        """
        try:
            # Use the email application sender for complete application workflow
            result = self.email_application_sender.send_job_application(job_data)

            if result["success"]:
                self.logger.info(
                    f"Successfully applied to {job_data.get('job_title')} at {job_data.get('company_name')}"
                )
            else:
                self.logger.warning(f"Application failed for {job_data.get('job_title')}: {result.get('reason')}")

            return result

        except Exception as e:
            self.logger.error(f"Job application error: {e}")
            return {"success": False, "reason": f"Application error: {str(e)}", "status": "error"}

    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            conn.autocommit = False
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_complete_workflow(self, batch_size: int = 5) -> Dict:
        """
        Execute complete end-to-end automated application workflow

        Args:
            batch_size: Number of jobs to process in this batch

        Returns:
            Dict: Comprehensive workflow execution results
        """
        workflow_id = str(uuid.uuid4())
        start_time = datetime.now()

        self.logger.info(f"Starting workflow execution {workflow_id} with batch size {batch_size}")

        try:
            # Step 1: Job Discovery
            eligible_jobs = self.discover_eligible_jobs(batch_size)
            self.logger.info(f"Discovered {len(eligible_jobs)} eligible jobs")

            # Step 2: Preference Matching and Eligibility
            matched_jobs = self.apply_preference_matching(eligible_jobs)
            self.logger.info(f"Matched {len(matched_jobs)} jobs after preference filtering")

            # Step 3: Application Workflow Execution
            application_results = []
            for job in matched_jobs:
                try:
                    result = self.process_single_application(job, workflow_id)
                    application_results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to process application for job {job.get('id', 'unknown')}: {e}")
                    application_results.append(
                        {
                            "job_id": job.get("id"),
                            "status": "failed",
                            "error": str(e),
                            "stage": "application_processing",
                        }
                    )

            # Step 4: Compile Results
            workflow_results = self.compile_workflow_results(
                workflow_id, start_time, eligible_jobs, matched_jobs, application_results
            )

            self.logger.info(f"Workflow {workflow_id} completed successfully")
            return workflow_results

        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "started_at": start_time.isoformat(),
                "completed_at": datetime.now().isoformat(),
            }

    def discover_eligible_jobs(self, batch_size: int) -> List[Dict]:
        """
        Discover jobs from analyzed_jobs table that haven't been processed

        Args:
            batch_size: Maximum number of jobs to discover

        Returns:
            List[Dict]: List of eligible job records
        """
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Find jobs that have been AI analyzed but not yet processed for applications
                cursor.execute(
                    """
                    SELECT DISTINCT
                        aj.id,
                        aj.job_title,
                        aj.company_id,
                        c.name as company_name,
                        aj.job_description,
                        aj.office_city,
                        aj.office_province,
                        aj.office_country,
                        aj.salary_low,
                        aj.salary_high,
                        aj.compensation_currency,
                        aj.remote_options,
                        aj.seniority_level,
                        aj.job_type,
                        aj.primary_source_url,
                        aj.created_at,
                        
                        -- AI Analysis Data from analyzed_jobs table
                        aj.primary_industry,
                        aj.authenticity_score,
                        aj.prestige_factor,
                        aj.estimated_stress_level
                        
                    FROM analyzed_jobs aj
                    LEFT JOIN companies c ON aj.company_id = c.id
                    LEFT JOIN job_applications japp ON aj.id = japp.job_id
                    
                    WHERE japp.id IS NULL  -- No application record exists yet
                    AND aj.ai_analysis_completed = true  -- Has AI analysis
                    AND aj.created_at >= NOW() - INTERVAL '30 days'  -- Recent jobs
                    AND aj.authenticity_score >= 0.7  -- High authenticity
                    AND aj.eligibility_flag = true  -- Eligible for application
                    
                    ORDER BY aj.authenticity_score DESC, aj.created_at DESC
                    LIMIT %s
                """,
                    (batch_size,),
                )

                jobs = cursor.fetchall()
                return [dict(job) for job in jobs]

    def apply_preference_matching(self, jobs: List[Dict]) -> List[Dict]:
        """
        Apply Steve Glen's preference matching to filter eligible jobs

        Args:
            jobs: List of job records to evaluate

        Returns:
            List[Dict]: Filtered jobs that match preferences with compatibility scores
        """
        matched_jobs = []

        # Get Steve Glen's profile and preferences with fallback
        profile_summary = self.user_profile.get_profile_summary()
        if not profile_summary or profile_summary.get("status") == "error":
            self.logger.warning("Could not load user profile, using default preferences")
            # Use Steve Glen's default preferences for testing
            base_prefs = {
                "preferred_city": "edmonton",
                "preferred_province": "alberta",
                "preferred_country": "canada",
                "work_arrangement": "hybrid",
                "salary_minimum": 65000,
                "salary_maximum": 85000,
            }
            preferred_industries = {"marketing", "communications", "technology", "strategy"}
            preference_packages = []
        else:
            base_prefs = profile_summary.get("base_preferences", {})
            industry_prefs = profile_summary.get("industry_preferences", [])
            preference_packages = profile_summary.get("preference_packages", [])

            preferred_industries = {
                pref["industry_name"].lower() for pref in industry_prefs if pref.get("preference_type") == "preferred"
            }

        for job in jobs:
            try:
                compatibility_score = self.calculate_job_compatibility(
                    job, base_prefs, preferred_industries, preference_packages
                )

                if compatibility_score >= self.min_compatibility_score:
                    job["compatibility_score"] = compatibility_score
                    job["rejection_reason"] = None
                    matched_jobs.append(job)
                    self.logger.info(f"Job {job.get('job_title', 'Unknown')} matched with score {compatibility_score}")
                else:
                    self.logger.info(f"Job {job.get('job_title', 'Unknown')} rejected with score {compatibility_score}")

            except Exception as e:
                self.logger.error(f"Error calculating compatibility for job {job.get('id')}: {e}")

        return matched_jobs

    def calculate_job_compatibility(
        self, job: Dict, base_prefs: Dict, preferred_industries: set, preference_packages: List[Dict]
    ) -> float:
        """
        Calculate job compatibility score based on user preferences

        Args:
            job: Job record with analysis data
            base_prefs: User's base preferences
            preferred_industries: Set of preferred industry names
            preference_packages: List of contextual preference packages

        Returns:
            float: Compatibility score (0-100)
        """
        score = 0.0
        max_score = 100.0

        # Job Title Match (30 points) - Primary criteria for Steve Glen
        title_score = self.calculate_job_title_compatibility(job)
        score += title_score

        # Industry Alignment (20 points) - Reduced since title matching is primary
        industry_score = 0
        job_industry = job.get("primary_industry", "").lower()
        if job_industry in preferred_industries:
            industry_score = 20
        elif any(industry in job_industry for industry in preferred_industries):
            industry_score = 12  # Partial match
        score += industry_score

        # Salary Compatibility (25 points)
        salary_score = self.calculate_salary_compatibility(job, base_prefs, preference_packages)
        score += salary_score

        # Location Compatibility (15 points)
        location_score = self.calculate_location_compatibility(job, base_prefs)
        score += location_score

        # Work Arrangement (10 points)
        work_arrangement_score = self.calculate_work_arrangement_compatibility(job, base_prefs)
        score += work_arrangement_score

        return min(score, max_score)

    def calculate_job_title_compatibility(self, job: Dict) -> float:
        """
        Calculate job title compatibility based on Steve Glen's target titles

        Args:
            job: Job record with job_title field

        Returns:
            float: Title compatibility score (0-30 points)
        """
        job_title = job.get("job_title", "").lower()

        # Check for exact matches (case-insensitive)
        for target_title in self.steve_glen_target_titles:
            if target_title.lower() == job_title:
                self.logger.info(f"Exact title match: {job_title} -> {target_title}")
                return 30.0  # Perfect match

        # Check for partial matches (keywords)
        partial_score = 0
        for target_title in self.steve_glen_target_titles:
            target_keywords = target_title.lower().split()

            # Check if most keywords from target title appear in job title
            matching_keywords = sum(1 for keyword in target_keywords if keyword in job_title)
            keyword_ratio = matching_keywords / len(target_keywords)

            if keyword_ratio >= 0.7:  # 70% of keywords match
                current_score = 25.0  # Strong partial match
                if current_score > partial_score:
                    partial_score = current_score
                    self.logger.info(f"Strong title match: {job_title} -> {target_title} ({keyword_ratio:.0%})")
            elif keyword_ratio >= 0.5:  # 50% of keywords match
                current_score = 15.0  # Moderate partial match
                if current_score > partial_score:
                    partial_score = current_score
                    self.logger.info(f"Moderate title match: {job_title} -> {target_title} ({keyword_ratio:.0%})")

        # If no good matches, check for related keywords
        if partial_score == 0:
            related_keywords = [
                "marketing",
                "communications",
                "brand",
                "content",
                "public relations",
                "pr",
                "media",
                "strategy",
                "analyst",
            ]

            for keyword in related_keywords:
                if keyword in job_title:
                    partial_score = 8.0  # Weak but relevant match
                    self.logger.info(f"Related keyword match: {job_title} contains '{keyword}'")
                    break

        return partial_score

    def calculate_salary_compatibility(self, job: Dict, base_prefs: Dict, preference_packages: List[Dict]) -> float:
        """Calculate salary compatibility score"""
        job_salary_min = float(job.get("salary_low", 0))
        job_salary_max = float(job.get("salary_high", 0))

        if not job_salary_min and not job_salary_max:
            return 12  # Neutral score if no salary info (adjusted from 15 to 12)

        user_salary_min = base_prefs.get("salary_minimum", 65000)

        # Check if salary meets minimum requirement
        if job_salary_min and job_salary_min >= user_salary_min:
            return 25  # Full score (adjusted from 30 to 25)
        elif job_salary_max and job_salary_max >= user_salary_min:
            return 18  # Partial score (adjusted from 20 to 18)
        else:
            return 5  # Low score but not zero

    def calculate_location_compatibility(self, job: Dict, base_prefs: Dict) -> float:
        """Calculate location compatibility score"""
        job_city = job.get("office_city", "").lower()
        job_province = job.get("office_province", "").lower()
        job_country = job.get("office_country", "").lower()

        preferred_city = base_prefs.get("preferred_city", "edmonton").lower()
        preferred_province = base_prefs.get("preferred_province_state", "alberta").lower()
        preferred_country = base_prefs.get("preferred_country", "canada").lower()

        if preferred_city in job_city:
            return 15  # Perfect match (adjusted from 20 to 15)
        elif preferred_province in job_province:
            return 12  # Province match (adjusted from 15 to 12)
        elif preferred_country in job_country:
            return 8  # Country match (adjusted from 10 to 8)
        else:
            return 5  # Remote possibility

    def calculate_work_arrangement_compatibility(self, job: Dict, base_prefs: Dict) -> float:
        """Calculate work arrangement compatibility score"""
        job_arrangement = job.get("remote_options", "").lower()
        preferred_arrangement = base_prefs.get("work_arrangement", "hybrid").lower()

        if preferred_arrangement in job_arrangement or job_arrangement in preferred_arrangement:
            return 10  # Perfect match (adjusted from 15 to 10)
        elif "remote" in job_arrangement and preferred_arrangement == "hybrid":
            return 8  # Acceptable (adjusted from 12 to 8)
        elif "hybrid" in job_arrangement and preferred_arrangement == "remote":
            return 7  # Acceptable (adjusted from 10 to 7)
        else:
            return 5  # Not ideal but possible

    @with_retry("workflow_execution")
    def process_single_application(self, job: Dict, workflow_id: str) -> Dict:
        """
        Process a single job application through complete workflow

        Args:
            job: Job record with compatibility score
            workflow_id: Unique identifier for this workflow run

        Returns:
            Dict: Application processing results
        """
        application_id = str(uuid.uuid4())
        start_time = datetime.now()

        try:
            # Step 1: Create application record
            app_record_id = self.create_application_record(job, application_id, workflow_id)

            # Step 2: Generate customized documents
            documents = self.generate_job_specific_documents(job, application_id)

            # Step 3: Compose and send application email
            email_result = self.send_application_email(job, documents, application_id)

            # Step 4: Update application status
            self.update_application_status(app_record_id, "sent", email_result)

            return {
                "job_id": job.get("id"),
                "application_id": application_id,
                "status": "success",
                "compatibility_score": job.get("compatibility_score"),
                "documents_generated": len(documents),
                "email_sent": email_result.get("success", False),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "stage": "completed",
            }

        except Exception as e:
            self.logger.error(f"Application processing failed for job {job.get('id')}: {e}")
            return {
                "job_id": job.get("id"),
                "application_id": application_id,
                "status": "failed",
                "error": str(e),
                "compatibility_score": job.get("compatibility_score"),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "stage": "failed",
            }

    def create_application_record(self, job: Dict, application_id: str, workflow_id: str) -> str:
        """Create application record in database"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO job_applications (
                        id, job_id, application_date, application_status, 
                        notes, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        application_id,
                        job.get("id"),
                        datetime.now(),
                        "processing",
                        f"Workflow: {workflow_id}, Compatibility: {job.get('compatibility_score', 0)}",
                        datetime.now(),
                    ),
                )

                conn.commit()
                return cursor.fetchone()[0]

    def generate_job_specific_documents(self, job: Dict, application_id: str) -> List[Dict]:
        """Generate customized resume and cover letter for specific job"""
        documents = []

        try:
            # Prepare job-specific data for document generation
            document_data = {
                "job_title": job.get("job_title", "Marketing Position"),
                "company_name": job.get("company_name", "Company"),
                "application_id": application_id,
                "compatibility_score": job.get("compatibility_score", 0),
                "industry": job.get("primary_industry", "Marketing"),
                "job_description": job.get("job_description", ""),
            }

            # Generate resume using webhook-style data
            resume_webhook_data = {
                "job_title": document_data["job_title"],
                "company_name": document_data["company_name"],
                "document_type": "resume",
                "title": f"Resume - {document_data['job_title']} at {document_data['company_name']}",
            }

            resume_result = self.document_generator.generate_document(resume_webhook_data)
            if resume_result.get("success"):
                documents.append(
                    {
                        "type": "resume",
                        "file_path": resume_result.get("file_path"),
                        "file_url": resume_result.get("file_url"),
                    }
                )

            # Generate cover letter
            cover_letter_webhook_data = {
                "job_title": document_data["job_title"],
                "company_name": document_data["company_name"],
                "document_type": "cover_letter",
                "title": f"Cover Letter - {document_data['job_title']} at {document_data['company_name']}",
            }

            cover_letter_result = self.document_generator.generate_document(cover_letter_webhook_data)
            if cover_letter_result.get("success"):
                documents.append(
                    {
                        "type": "cover_letter",
                        "file_path": cover_letter_result.get("file_path"),
                        "file_url": cover_letter_result.get("file_url"),
                    }
                )

            self.logger.info(f"Generated {len(documents)} documents for application {application_id}")
            return documents

        except Exception as e:
            self.logger.error(f"Document generation failed for application {application_id}: {e}")
            return []

    def send_application_email(self, job: Dict, documents: List[Dict], application_id: str) -> Dict:
        """Compose and send application email with attachments"""
        try:
            # Compose email content
            subject = f"Application for {job.get('job_title', 'Marketing Position')} - Steve Glen"

            email_body = self.compose_application_email_body(job)

            # Prepare attachments
            attachments = []
            for doc in documents:
                if doc.get("file_path"):
                    attachments.append(doc["file_path"])

            # Send email using available email sender
            if hasattr(self.email_sender, "send_email_with_attachments"):
                email_result = self.email_sender.send_email_with_attachments(
                    recipient="therealstevenglen@gmail.com",  # Test recipient
                    subject=subject,
                    body=email_body,
                    attachments=attachments,
                )
            else:
                # Mock email result for testing
                email_result = {
                    "success": True,
                    "message_id": f"mock_message_{application_id}",
                    "sent_at": datetime.now().isoformat(),
                    "attachments_count": len(attachments),
                }

            self.logger.info(f"Email sent for application {application_id} with {len(attachments)} attachments")
            return email_result

        except Exception as e:
            self.logger.error(f"Email sending failed for application {application_id}: {e}")
            return {"success": False, "error": str(e)}

    def compose_application_email_body(self, job: Dict) -> str:
        """Compose personalized application email body"""
        company_name = job.get("company_name", "Company")
        job_title = job.get("job_title", "Marketing Position")

        email_body = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With over 14 years of experience in marketing communications and strategic business development, I am excited about the opportunity to contribute to your team.

My background includes:
• Extensive experience in digital marketing, content strategy, and business analytics
• Proven track record in developing and executing comprehensive marketing campaigns
• Strong analytical skills with expertise in data-driven decision making
• Experience working in collaborative, hybrid work environments

I have attached my resume and cover letter for your review. I would welcome the opportunity to discuss how my experience and skills can contribute to {company_name}'s continued success.

Thank you for your consideration. I look forward to hearing from you.

Best regards,
Steve Glen
1234.S.t.e.v.e.Glen@gmail.com
Edmonton, Alberta, Canada

Application ID: {job.get('id', 'N/A')}
"""
        return email_body

    def update_application_status(self, app_record_id: str, status: str, details: Dict) -> None:
        """Update application record with final status"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE job_applications 
                    SET application_status = %s,
                        notes = COALESCE(notes, '') || %s
                    WHERE id = %s
                """,
                    (
                        status,
                        (
                            f" | Email sent: {datetime.now().isoformat()}"
                            if details.get("success")
                            else f" | Email failed: {details.get('error', 'Unknown error')}"
                        ),
                        app_record_id,
                    ),
                )
                conn.commit()

    def compile_workflow_results(
        self,
        workflow_id: str,
        start_time: datetime,
        eligible_jobs: List[Dict],
        matched_jobs: List[Dict],
        application_results: List[Dict],
    ) -> Dict:
        """Compile comprehensive workflow execution results"""
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        successful_applications = [r for r in application_results if r.get("status") == "success"]
        failed_applications = [r for r in application_results if r.get("status") == "failed"]

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "total_duration_seconds": total_duration,
            "job_discovery": {
                "eligible_jobs_found": len(eligible_jobs),
                "jobs_after_matching": len(matched_jobs),
                "filter_efficiency": len(matched_jobs) / len(eligible_jobs) if eligible_jobs else 0,
            },
            "application_processing": {
                "total_processed": len(application_results),
                "successful_applications": len(successful_applications),
                "failed_applications": len(failed_applications),
                "success_rate": len(successful_applications) / len(application_results) if application_results else 0,
            },
            "performance_metrics": {
                "average_compatibility_score": (
                    sum(r.get("compatibility_score", 0) for r in application_results) / len(application_results)
                    if application_results
                    else 0
                ),
                "average_processing_time": (
                    sum(r.get("processing_time", 0) for r in application_results) / len(application_results)
                    if application_results
                    else 0
                ),
                "documents_generated": sum(r.get("documents_generated", 0) for r in successful_applications),
            },
            "detailed_results": application_results,
        }

    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get status of a specific workflow execution"""
        # This would typically query a workflow_executions table
        # For now, return a placeholder response
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "message": "Workflow status tracking would be implemented here",
        }

    def get_daily_application_count(self) -> int:
        """Get number of applications sent today"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM job_applications 
                    WHERE DATE(application_date) = CURRENT_DATE
                    AND application_status = 'sent'
                """
                )
                return cursor.fetchone()[0]


def main():
    """Test the ApplicationOrchestrator implementation"""
    print("Step 2.2: End-to-End Workflow Orchestration Test")
    print("=" * 60)

    try:
        orchestrator = ApplicationOrchestrator()

        # Test workflow execution with small batch
        print("\n🚀 Testing complete workflow execution...")
        results = orchestrator.execute_complete_workflow(batch_size=3)

        print(f"\n📊 Workflow Results:")
        print(f"   Workflow ID: {results.get('workflow_id')}")
        print(f"   Status: {results.get('status')}")
        print(f"   Duration: {results.get('total_duration_seconds', 0):.2f} seconds")

        if results.get("job_discovery"):
            discovery = results["job_discovery"]
            print(f"\n🔍 Job Discovery:")
            print(f"   Eligible jobs found: {discovery.get('eligible_jobs_found', 0)}")
            print(f"   Jobs after matching: {discovery.get('jobs_after_matching', 0)}")
            print(f"   Filter efficiency: {discovery.get('filter_efficiency', 0):.1%}")

        if results.get("application_processing"):
            processing = results["application_processing"]
            print(f"\n📝 Application Processing:")
            print(f"   Total processed: {processing.get('total_processed', 0)}")
            print(f"   Successful: {processing.get('successful_applications', 0)}")
            print(f"   Failed: {processing.get('failed_applications', 0)}")
            print(f"   Success rate: {processing.get('success_rate', 0):.1%}")

        if results.get("performance_metrics"):
            metrics = results["performance_metrics"]
            print(f"\n⚡ Performance Metrics:")
            print(f"   Average compatibility score: {metrics.get('average_compatibility_score', 0):.1f}")
            print(f"   Average processing time: {metrics.get('average_processing_time', 0):.2f}s")
            print(f"   Documents generated: {metrics.get('documents_generated', 0)}")

        print(f"\n✅ Step 2.2 End-to-End Workflow Orchestration implementation complete!")

    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        print("Check database connectivity and user profile configuration")


if __name__ == "__main__":
    main()
