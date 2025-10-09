#!/usr/bin/env python3
"""
Email Application Sender Module

Handles automated job application email sending with the following features:
- Email composition with job-specific content or boilerplate
- Resume and cover letter attachment handling
- Recipient determination (job email vs. therealstevenglen@gmail.com)
- 6-day waiting period enforcement with deadline checking
- Integration with existing email infrastructure

Business Rules:
1. Wait 6 days after job posting/discovery before sending
2. Do not send if submission deadline has passed
3. Send to job email if available, otherwise to therealstevenglen@gmail.com
4. Include original job source link when sending to fallback email
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor

# Import email integration - DISABLED FOR SAFETY
try:
    from modules.email_integration.email_disabled import DisabledEmailSender, is_email_sending_disabled

    _email_available = True
    # Always use disabled email sender to prevent accidental emails
    EnhancedGmailSender = DisabledEmailSender
except ImportError:
    _email_available = False

    # Mock email sender for testing
    class MockEmailSender:
        def send_email_with_attachments(self, recipient, subject, body, attachments=None):
            return {
                "success": True,
                "message_id": f'mock_message_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                "sent_at": datetime.now().isoformat(),
                "mock_mode": True,
            }

    EnhancedGmailSender = MockEmailSender

# Import document generation
try:
    from modules.content.document_generation.document_generator import DocumentGenerator

    _doc_gen_available = True
except ImportError:
    _doc_gen_available = False

    class MockDocumentGenerator:
        def generate_document(self, data):
            return {
                "success": True,
                "file_path": f'/mock/path/{data.get("document_type", "document")}.docx',
                "filename": f'{data.get("document_type", "document")}.docx',
            }

    DocumentGenerator = MockDocumentGenerator

from modules.database.database_manager import DatabaseManager
from modules.email_integration.signature_generator import get_signature_generator
from modules.email_integration.email_content_builder import get_email_content_builder
from modules.email_integration.email_validator import get_email_validator

logger = logging.getLogger(__name__)


class EmailApplicationSender:
    """
    Manages automated email sending for job applications

    Handles the complete email application workflow including:
    - Timing validation (6-day wait, deadline checking)
    - Recipient determination and email composition
    - Document attachment and content generation
    - Email delivery and tracking
    """

    def __init__(self):
        """Initialize email application sender"""
        self.db_manager = DatabaseManager()
        self.email_sender = EnhancedGmailSender()
        self.document_generator = DocumentGenerator()
        self.db_url = os.environ.get("DATABASE_URL")

        # Email signature generator
        self.signature_generator = get_signature_generator()

        # Email content builder
        self.content_builder = get_email_content_builder()

        # Email validator
        self.email_validator = get_email_validator()

        # Email configuration from environment
        self.user_email = os.getenv("USER_EMAIL_ADDRESS", "your.email@gmail.com")
        self.display_name = os.getenv("USER_DISPLAY_NAME", "Steve Glen")
        self.fallback_email = self.user_email  # Send to self if no job email found
        self.waiting_period_days = 6

        # Steve Glen's application content
        self.default_subject_templates = {
            "with_job_email": "Application for {job_title} Position - Steve Glen",
            "fallback_email": "Job Application Opportunity: {job_title} at {company_name}",
        }

        self.default_email_body_templates = {
            "with_job_email": self._get_professional_email_template(),
            "fallback_email": self._get_fallback_email_template(),
        }

        logger.info("EmailApplicationSender initialized for job application automation")

    def _get_professional_email_template(self) -> str:
        """Get professional email template for direct job applications"""
        # Get signature from generator (plain text version)
        signature = self.signature_generator.generate_plain_text_signature()

        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {{job_title}} position at {{company_name}}. With over 14 years of experience in marketing communications and strategic business development, I am excited about the opportunity to contribute to your team's success.

Key highlights of my background include:

• 14+ years of progressive experience in marketing communications and business strategy at Odvod Media/Edify Magazine
• Proven track record in digital marketing, content strategy, and cross-functional team leadership
• Strong analytical skills with experience in business intelligence and data-driven decision making
• Bachelor of Business Administration from the University of Alberta
• Expertise in marketing automation, strategic communications, and stakeholder engagement

I am particularly drawn to this opportunity because of {{company_name}}'s reputation for innovation and excellence. My experience in developing comprehensive marketing strategies and driving measurable business results aligns well with the requirements outlined in your job posting.

I have attached my resume and cover letter for your review. I would welcome the opportunity to discuss how my background and enthusiasm can contribute to your team's objectives.

Thank you for your time and consideration. I look forward to hearing from you.

{signature}"""

    def _get_fallback_email_template(self) -> str:
        """Get email template for fallback sending to user's own email"""
        user_first_name = self.display_name.split()[0]  # Get first name

        return f"""Subject: Job Application Opportunity - {{job_title}} at {{company_name}}

{user_first_name},

I've identified a potential job opportunity that matches your preferences and qualifications:

Job Title: {{job_title}}
Company: {{company_name}}
Location: {{job_location}}
Salary Range: {{salary_range}}
Posted Date: {{posted_date}}

Job Source: {{job_source_url}}

The position appears to be a strong match based on:
• Job title compatibility: {{title_compatibility_score}}/30 points
• Overall compatibility score: {{overall_compatibility_score}}/100 points
• Industry alignment: {{primary_industry}}
• Location preference match: {{location_match}}

Application documents have been prepared and are attached:
- Tailored resume for this position
- Customized cover letter highlighting relevant experience

Since no direct application email was found in the job posting, you'll need to apply through the original job source or find the appropriate contact information.

Original job posting: {{job_source_url}}

Best regards,
Automated Job Application System"""

    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def extract_email_from_job_description(
        self, job_description: str, application_email: Optional[str] = None
    ) -> Optional[str]:
        """
        Extract email address from job description or use provided application_email

        Args:
            job_description: Job description text to search for emails
            application_email: Pre-extracted email from database

        Returns:
            Email address if found, None otherwise
        """
        # First check if we have a pre-extracted email
        if application_email and "@" in application_email:
            logger.info(f"Using pre-extracted application email: {application_email}")
            return application_email.strip()

        if not job_description:
            return None

        # Email regex pattern - matches common email formats
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, job_description)

        if emails:
            # Filter out common non-application emails
            filtered_emails = []
            skip_domains = ["example.com", "test.com", "noreply", "no-reply"]

            for email in emails:
                email_lower = email.lower()
                if not any(skip in email_lower for skip in skip_domains):
                    filtered_emails.append(email)

            if filtered_emails:
                # Prefer HR, careers, or jobs related emails
                priority_keywords = ["hr", "career", "job", "recruit", "hiring", "talent"]
                for email in filtered_emails:
                    email_lower = email.lower()
                    if any(keyword in email_lower for keyword in priority_keywords):
                        logger.info(f"Found priority application email: {email}")
                        return email

                # Return first valid email if no priority match
                logger.info(f"Found application email: {filtered_emails[0]}")
                return filtered_emails[0]

        logger.info("No application email found in job description")
        return None

    def check_sending_eligibility(self, job_data: Dict) -> Tuple[bool, str]:
        """
        Check if a job application is eligible for sending

        Args:
            job_data: Job information dictionary

        Returns:
            Tuple of (is_eligible, reason)
        """
        current_time = datetime.now()

        # Get job posting/discovery date
        posted_date = job_data.get("posted_date")
        created_at = job_data.get("created_at")

        # Use posted_date if available, otherwise use created_at (discovery date)
        reference_date = posted_date or created_at

        if not reference_date:
            return False, "No posting or discovery date available"

        # Convert to datetime if it's a string
        if isinstance(reference_date, str):
            try:
                reference_date = datetime.fromisoformat(reference_date.replace("Z", "+00:00"))
            except ValueError:
                return False, f"Invalid date format: {reference_date}"
        elif reference_date is None:
            return False, "No posting or discovery date available"

        # Check 6-day waiting period
        wait_until = reference_date + timedelta(days=self.waiting_period_days)
        if current_time < wait_until:
            days_remaining = (wait_until - current_time).days
            return (
                False,
                f"Still in waiting period. {days_remaining} days remaining until {wait_until.strftime('%Y-%m-%d')}",
            )

        # Check submission deadline
        deadline = job_data.get("submission_deadline")
        if deadline:
            if isinstance(deadline, str):
                try:
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                except ValueError:
                    logger.warning(f"Invalid deadline format: {deadline}")
                    deadline = None

            if deadline and current_time > deadline:
                return False, f"Submission deadline has passed: {deadline.strftime('%Y-%m-%d %H:%M')}"

        return True, "Eligible for sending"

    def prepare_application_documents(self, job_data: Dict) -> Dict[str, Optional[str]]:
        """
        Generate or prepare application documents (resume and cover letter)

        Args:
            job_data: Job information for document customization

        Returns:
            Dictionary with document file paths
        """
        documents = {
            "resume_path": None,
            "cover_letter_path": None,
            "resume_filename": None,
            "cover_letter_filename": None,
        }

        try:
            # Prepare data for document generation
            job_title = job_data.get("job_title", "Position")
            company_name = job_data.get("company_name", "Company")

            # Generate resume
            resume_data = {
                "document_type": "resume",
                "job_title": job_title,
                "company_name": company_name,
                "full_name": self.display_name,
                "professional_summary": f"Marketing communications professional with 14+ years of experience, seeking {job_title} role",
                "phone": os.getenv("USER_PHONE", "(780) 555-0123"),
                "email": self.user_email,
                "address": os.getenv("USER_LOCATION", "Edmonton, Alberta, Canada"),
                "target_job_title": job_title,
                "target_company": company_name,
            }

            resume_result = self.document_generator.generate_document(resume_data)
            if resume_result.get("success"):
                documents["resume_path"] = resume_result.get("file_path")
                documents["resume_filename"] = resume_result.get("filename")
                logger.info(f"Resume generated: {documents['resume_filename']}")

            # Generate cover letter
            cover_letter_data = {
                "document_type": "cover_letter",
                "job_title": job_title,
                "company_name": company_name,
                "full_name": self.display_name,
                "target_job_title": job_title,
                "target_company": company_name,
                "professional_summary": f"Experienced marketing professional applying for {job_title} at {company_name}",
            }

            cover_letter_result = self.document_generator.generate_document(cover_letter_data)
            if cover_letter_result.get("success"):
                documents["cover_letter_path"] = cover_letter_result.get("file_path")
                documents["cover_letter_filename"] = cover_letter_result.get("filename")
                logger.info(f"Cover letter generated: {documents['cover_letter_filename']}")

        except Exception as e:
            logger.error(f"Document generation error: {e}")

        return documents

    def compose_email_content(self, job_data: Dict, recipient_email: str) -> Tuple[str, str]:
        """
        Compose email subject and body based on recipient type

        Args:
            job_data: Job information
            recipient_email: Email address of recipient

        Returns:
            Tuple of (subject, body)
        """
        job_title = job_data.get("job_title", "Position")
        company_name = job_data.get("company_name", "Company")

        # Determine if this is direct application or fallback
        is_fallback = recipient_email == self.fallback_email

        if is_fallback:
            # Fallback email to therealstevenglen@gmail.com
            subject_template = self.default_subject_templates["fallback_email"]
            body_template = self.default_email_body_templates["fallback_email"]

            # Additional data for fallback template
            job_location = f"{job_data.get('office_city', '')}, {job_data.get('office_province', '')}, {job_data.get('office_country', '')}"
            salary_low = job_data.get("salary_low", 0)
            salary_high = job_data.get("salary_high", 0)
            salary_range = f"${salary_low:,} - ${salary_high:,}" if salary_low and salary_high else "Not specified"

            posted_date = job_data.get("posted_date", job_data.get("created_at", ""))
            if isinstance(posted_date, datetime):
                posted_date = posted_date.strftime("%Y-%m-%d")

            job_source_url = job_data.get("source_url", "https://ca.indeed.com/")

            subject = subject_template.format(job_title=job_title, company_name=company_name)

            body = body_template.format(
                job_title=job_title,
                company_name=company_name,
                job_location=job_location.strip(", "),
                salary_range=salary_range,
                posted_date=posted_date,
                job_source_url=job_source_url,
                title_compatibility_score=job_data.get("title_compatibility_score", "N/A"),
                overall_compatibility_score=job_data.get("compatibility_score", "N/A"),
                primary_industry=job_data.get("primary_industry", "N/A"),
                location_match=job_data.get("location_match", "Yes"),
            )
        else:
            # Direct application to job email
            subject_template = self.default_subject_templates["with_job_email"]
            body_template = self.default_email_body_templates["with_job_email"]

            subject = subject_template.format(job_title=job_title, company_name=company_name)

            body = body_template.format(job_title=job_title, company_name=company_name)

        return subject, body

    def send_job_application(self, job_data: Dict) -> Dict:
        """
        Send job application email with all required components

        Uses EmailContentBuilder for intelligent content mapping and EmailValidator
        for pre-send validation.

        Args:
            job_data: Complete job information from analyzed_jobs table

        Returns:
            Dictionary with sending results
        """
        try:
            # Check sending eligibility (timing constraints)
            is_eligible, eligibility_reason = self.check_sending_eligibility(job_data)
            if not is_eligible:
                return {"success": False, "reason": eligibility_reason, "status": "not_eligible"}

            # Prepare application documents (resume + cover letter)
            documents = self.prepare_application_documents(job_data)

            # Build complete email package using content builder
            email_package = self.content_builder.build_email_package(job_data, documents)

            # Validate email before sending
            validation_result = self.email_validator.validate_email(
                to_email=email_package["recipient"],
                subject=email_package["subject"],
                body=email_package["body"],
                attachments=email_package["attachments"],
            )

            # Check validation results
            if not validation_result["can_send"]:
                logger.error(f"Email validation failed for job {job_data.get('id')}: {validation_result['errors']}")
                return {
                    "success": False,
                    "reason": f"Email validation failed: {', '.join(validation_result['errors'])}",
                    "status": "validation_failed",
                    "validation_errors": validation_result["errors"],
                }

            # Log validation warnings (non-blocking)
            if validation_result["warnings"]:
                logger.warning(f"Email validation warnings for job {job_data.get('id')}: {validation_result['warnings']}")

            # Send email with properly formatted attachments
            email_result = self.email_sender.send_email_with_attachments(
                recipient=email_package["recipient"],
                subject=email_package["subject"],
                body=email_package["body"],
                attachments=email_package["attachments"],
            )

            if email_result.get("success"):
                # Update job application status in database
                self._update_application_status(job_data["id"], "sent", email_result, email_package)

                return {
                    "success": True,
                    "recipient": email_package["recipient"],
                    "subject": email_package["subject"],
                    "message_id": email_result.get("message_id"),
                    "sent_at": email_result.get("sent_at"),
                    "attachments_count": len(email_package["attachments"]),
                    "is_fallback": email_package["is_fallback"],
                    "validation_warnings": validation_result.get("warnings", []),
                    "metadata": email_package["metadata"],
                }
            else:
                return {
                    "success": False,
                    "reason": email_result.get("error", "Email sending failed"),
                    "status": "email_failed",
                }

        except Exception as e:
            logger.error(f"Job application sending error: {e}", exc_info=True)
            return {"success": False, "reason": f"Application sending error: {str(e)}", "status": "error"}

    def _update_application_status(self, job_id: str, status: str, email_result: Dict, email_package: Dict = None):
        """
        Update job application status in database with email metadata

        Args:
            job_id: Job ID
            status: Application status
            email_result: Result from email sender
            email_package: Email package with metadata (optional)
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                # Extract metadata from email package if available
                recipient = email_package["recipient"] if email_package else None
                subject = email_package["subject"] if email_package else None

                # Update or insert application record
                cursor.execute(
                    """
                    INSERT INTO job_applications (job_id, status, email_sent_at, email_message_id, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (job_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        email_sent_at = EXCLUDED.email_sent_at,
                        email_message_id = EXCLUDED.email_message_id,
                        updated_at = CURRENT_TIMESTAMP
                """,
                    (job_id, status, email_result.get("sent_at"), email_result.get("message_id"), datetime.now()),
                )

                conn.commit()
                logger.info(f"Updated application status for job {job_id}: {status} (recipient: {recipient})")

        except Exception as e:
            logger.error(f"Failed to update application status: {e}")

    def process_eligible_applications(self, limit: int = 5) -> Dict:
        """
        Process multiple eligible job applications

        Args:
            limit: Maximum number of applications to process

        Returns:
            Processing summary
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                # Get eligible jobs that haven't been applied to yet
                cursor.execute(
                    """
                    SELECT j.*, c.name as company_name
                    FROM analyzed_jobs j
                    LEFT JOIN companies c ON j.company_id = c.id
                    LEFT JOIN job_applications ja ON j.id = ja.job_id
                    WHERE ja.job_id IS NULL 
                        AND j.compatibility_score >= 50
                        AND j.created_at <= %s
                    ORDER BY j.compatibility_score DESC, j.created_at ASC
                    LIMIT %s
                """,
                    (datetime.now() - timedelta(days=self.waiting_period_days), limit),
                )

                eligible_jobs = cursor.fetchall()

                results = {"processed": 0, "sent": 0, "failed": 0, "not_eligible": 0, "details": []}

                for job in eligible_jobs:
                    job_dict = dict(job)
                    result = self.send_job_application(job_dict)

                    results["processed"] += 1
                    if result["success"]:
                        results["sent"] += 1
                    elif result.get("status") == "not_eligible":
                        results["not_eligible"] += 1
                    else:
                        results["failed"] += 1

                    results["details"].append(
                        {
                            "job_id": job_dict["id"],
                            "job_title": job_dict.get("job_title"),
                            "company_name": job_dict.get("company_name"),
                            "result": result,
                        }
                    )

                logger.info(
                    f"Processed {results['processed']} applications: {results['sent']} sent, {results['failed']} failed, {results['not_eligible']} not eligible"
                )
                return results

        except Exception as e:
            logger.error(f"Batch application processing error: {e}")
            return {"processed": 0, "sent": 0, "failed": 0, "not_eligible": 0, "error": str(e)}
