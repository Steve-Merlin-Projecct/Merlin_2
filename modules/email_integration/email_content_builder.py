#!/usr/bin/env python3
"""
Email Content Builder Module

Builds complete email content from job application package data.
Maps job data fields to email components (subject, body, metadata, attachments).

Features:
- Intelligent content mapping from job data
- Dynamic subject line generation
- Professional email body composition
- Attachment metadata and filename generation
- Email metadata enrichment (Message-ID, references, threading)
- Support for both direct applications and fallback notifications
"""

import os
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from modules.email_integration.signature_generator import get_signature_generator

logger = logging.getLogger(__name__)


class EmailContentBuilder:
    """
    Builds email content from job application package data

    Maps structured job data to all email components:
    - Subject line (with optional reference ID)
    - Email body (personalized with job details)
    - Attachments (resume + cover letter with proper filenames)
    - Email metadata (headers, threading info)
    """

    def __init__(self):
        """Initialize email content builder"""
        # Load user configuration
        self.user_email = os.getenv("USER_EMAIL_ADDRESS", "your.email@gmail.com")
        self.display_name = os.getenv("USER_DISPLAY_NAME", "Steve Glen")
        self.use_html = os.getenv("EMAIL_USE_HTML", "true").lower() == "true"
        self.include_reference_id = os.getenv("EMAIL_INCLUDE_REFERENCE_ID", "false").lower() == "true"

        # Initialize signature generator
        self.signature_generator = get_signature_generator()

    def build_email_package(self, job_data: Dict, generated_documents: Dict) -> Dict:
        """
        Build complete email package from job data and generated documents

        Args:
            job_data: Job information from analyzed_jobs table
            generated_documents: Dictionary with resume and cover letter paths

        Returns:
            Complete email package dictionary:
            {
                'recipient': str,
                'subject': str,
                'body': str,
                'body_html': str (if HTML enabled),
                'attachments': List[Dict],
                'metadata': Dict,
                'is_fallback': bool
            }
        """
        try:
            # Extract key job information
            job_info = self._extract_job_info(job_data)

            # Determine recipient
            recipient = self._determine_recipient(job_data)
            is_fallback = recipient == self.user_email

            # Build subject line
            subject = self._build_subject_line(job_info, is_fallback)

            # Build email body
            if is_fallback:
                body = self._build_fallback_email_body(job_data, job_info)
            else:
                body = self._build_application_email_body(job_data, job_info)

            # Build HTML version if enabled
            body_html = self._build_html_body(body) if self.use_html else None

            # Build attachments list
            attachments = self._build_attachments_list(job_info, generated_documents)

            # Build email metadata
            metadata = self._build_email_metadata(job_data, job_info)

            return {
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "body_html": body_html,
                "attachments": attachments,
                "metadata": metadata,
                "is_fallback": is_fallback,
                "job_id": job_data.get("id"),
                "job_title": job_info["job_title"],
                "company_name": job_info["company_name"],
            }

        except Exception as e:
            logger.error(f"Failed to build email package: {e}")
            raise

    def _extract_job_info(self, job_data: Dict) -> Dict:
        """
        Extract and normalize job information from job_data

        Args:
            job_data: Raw job data dictionary

        Returns:
            Normalized job info dictionary
        """
        return {
            "job_id": job_data.get("id"),
            "job_title": job_data.get("job_title", "Position"),
            "company_name": job_data.get("company_name", "Company"),
            "company_id": job_data.get("company_id"),
            "location": self._format_location(job_data),
            "salary_range": self._format_salary_range(job_data),
            "posted_date": self._format_date(job_data.get("posted_date")),
            "source_url": job_data.get("source_url", ""),
            "application_email": job_data.get("application_email"),
            "job_description": job_data.get("job_description", ""),
            # Analysis/matching scores
            "compatibility_score": job_data.get("compatibility_score", 0),
            "title_compatibility_score": job_data.get("title_compatibility_score", 0),
            "primary_industry": job_data.get("primary_industry", "N/A"),
            "location_match": job_data.get("location_match", True),
            # Additional metadata
            "hiring_manager_name": job_data.get("hiring_manager_name"),
            "job_type": job_data.get("job_type", "Full-time"),
            "experience_level": job_data.get("experience_level"),
        }

    def _format_location(self, job_data: Dict) -> str:
        """Format job location from components"""
        city = job_data.get("office_city", "")
        province = job_data.get("office_province", "")
        country = job_data.get("office_country", "")

        parts = [p for p in [city, province, country] if p]
        return ", ".join(parts) if parts else "Location not specified"

    def _format_salary_range(self, job_data: Dict) -> str:
        """Format salary range for display"""
        salary_low = job_data.get("salary_low")
        salary_high = job_data.get("salary_high")

        if salary_low and salary_high:
            return f"${salary_low:,} - ${salary_high:,}"
        elif salary_low:
            return f"${salary_low:,}+"
        else:
            return "Not specified"

    def _format_date(self, date_value) -> str:
        """Format date for display"""
        if not date_value:
            return "N/A"

        if isinstance(date_value, str):
            try:
                date_obj = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                return date_obj.strftime("%Y-%m-%d")
            except:
                return date_value
        elif isinstance(date_value, datetime):
            return date_value.strftime("%Y-%m-%d")
        else:
            return str(date_value)

    def _determine_recipient(self, job_data: Dict) -> str:
        """
        Determine email recipient (job email or fallback to user)

        Args:
            job_data: Job information

        Returns:
            Email address to send to
        """
        # Check for explicit application email
        application_email = job_data.get("application_email")
        if application_email and "@" in application_email:
            return application_email.strip()

        # Try to extract from job description
        job_description = job_data.get("job_description", "")
        extracted_email = self._extract_email_from_text(job_description)
        if extracted_email:
            return extracted_email

        # Fallback to user's own email
        logger.info(f"No application email found for job {job_data.get('id')}, using fallback")
        return self.user_email

    def _extract_email_from_text(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        if not text:
            return None

        # Email regex
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)

        if not emails:
            return None

        # Filter out common non-application emails
        skip_domains = ["example.com", "test.com", "noreply", "no-reply"]
        filtered_emails = [e for e in emails if not any(skip in e.lower() for skip in skip_domains)]

        if not filtered_emails:
            return None

        # Prioritize HR/careers/jobs emails
        priority_keywords = ["hr", "career", "job", "recruit", "hiring", "talent"]
        for email in filtered_emails:
            if any(keyword in email.lower() for keyword in priority_keywords):
                return email

        return filtered_emails[0]

    def _build_subject_line(self, job_info: Dict, is_fallback: bool) -> str:
        """
        Build email subject line

        Args:
            job_info: Job information dictionary
            is_fallback: Whether this is a fallback email

        Returns:
            Email subject line
        """
        job_title = job_info["job_title"]
        company_name = job_info["company_name"]

        if is_fallback:
            subject = f"Job Application Opportunity: {job_title} at {company_name}"
        else:
            if self.include_reference_id:
                # Generate reference ID: YYYYMMDD-NNN
                ref_id = self._generate_reference_id(job_info["job_id"])
                subject = f"Application #{ref_id}: {job_title} - {self.display_name}"
            else:
                subject = f"Application for {job_title} Position - {self.display_name}"

        return subject

    def _generate_reference_id(self, job_id: Optional[int]) -> str:
        """Generate tracking reference ID"""
        date_part = datetime.now().strftime("%Y%m%d")
        id_part = f"{job_id:03d}" if job_id else "001"
        return f"{date_part}-{id_part}"

    def _build_application_email_body(self, job_data: Dict, job_info: Dict) -> str:
        """
        Build email body for direct job application

        Args:
            job_data: Full job data
            job_info: Extracted job info

        Returns:
            Email body text
        """
        # Get greeting (personalized if hiring manager name available)
        greeting = self._build_greeting(job_info.get("hiring_manager_name"))

        # Get signature
        signature = self.signature_generator.generate_plain_text_signature()

        # Build professional email body
        body = f"""{greeting}

I am writing to express my strong interest in the {job_info['job_title']} position at {job_info['company_name']}. With over 14 years of experience in marketing communications and strategic business development, I am excited about the opportunity to contribute to your team's success.

Key highlights of my background include:

• 14+ years of progressive experience in marketing communications and business strategy at Odvod Media/Edify Magazine
• Proven track record in digital marketing, content strategy, and cross-functional team leadership
• Strong analytical skills with experience in business intelligence and data-driven decision making
• Bachelor of Business Administration from the University of Alberta
• Expertise in marketing automation, strategic communications, and stakeholder engagement

I am particularly drawn to this opportunity because of {job_info['company_name']}'s reputation for innovation and excellence. My experience in developing comprehensive marketing strategies and driving measurable business results aligns well with the requirements outlined in your job posting.

I have attached my resume and cover letter for your review. I would welcome the opportunity to discuss how my background and enthusiasm can contribute to your team's objectives.

Thank you for your time and consideration. I look forward to hearing from you.

{signature}"""

        return body

    def _build_fallback_email_body(self, job_data: Dict, job_info: Dict) -> str:
        """
        Build email body for fallback notification (sent to user)

        Args:
            job_data: Full job data
            job_info: Extracted job info

        Returns:
            Email body text
        """
        user_first_name = self.display_name.split()[0]

        body = f"""Subject: Job Application Opportunity - {job_info['job_title']} at {job_info['company_name']}

{user_first_name},

I've identified a potential job opportunity that matches your preferences and qualifications:

Job Title: {job_info['job_title']}
Company: {job_info['company_name']}
Location: {job_info['location']}
Salary Range: {job_info['salary_range']}
Posted Date: {job_info['posted_date']}

Job Source: {job_info['source_url']}

The position appears to be a strong match based on:
• Job title compatibility: {job_info['title_compatibility_score']}/30 points
• Overall compatibility score: {job_info['compatibility_score']}/100 points
• Industry alignment: {job_info['primary_industry']}
• Location preference match: {'Yes' if job_info['location_match'] else 'No'}

Application documents have been prepared and are attached:
- Tailored resume for this position
- Customized cover letter highlighting relevant experience

Since no direct application email was found in the job posting, you'll need to apply through the original job source or find the appropriate contact information.

Original job posting: {job_info['source_url']}

Best regards,
Automated Job Application System"""

        return body

    def _build_greeting(self, hiring_manager_name: Optional[str]) -> str:
        """Build personalized greeting if hiring manager name available"""
        if hiring_manager_name:
            # Extract first name if full name provided
            first_name = hiring_manager_name.split()[0]
            return f"Dear {first_name},"
        else:
            return "Dear Hiring Manager,"

    def _build_html_body(self, plain_text_body: str) -> str:
        """
        Convert plain text body to enhanced plain text HTML

        Args:
            plain_text_body: Plain text email body

        Returns:
            HTML version with clickable links and subtle formatting
        """
        # Escape HTML special characters
        html_body = plain_text_body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Convert URLs to clickable links
        url_pattern = r"(https?://[^\s]+)"
        html_body = re.sub(url_pattern, r'<a href="\1" style="color: #0066cc;">\1</a>', html_body)

        # Convert email addresses to clickable mailto links
        email_pattern = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        html_body = re.sub(email_pattern, r'<a href="mailto:\1" style="color: #0066cc;">\1</a>', html_body)

        # Wrap in HTML structure
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6; max-width: 650px; margin: 0; padding: 20px;">
    <div style="white-space: pre-wrap;">{html_body}</div>
</body>
</html>"""

        return html

    def _build_attachments_list(self, job_info: Dict, generated_documents: Dict) -> List[Dict]:
        """
        Build attachments list with proper filenames and metadata

        Args:
            job_info: Job information
            generated_documents: Dictionary with document paths

        Returns:
            List of attachment dictionaries
        """
        attachments = []

        # Resume attachment
        if generated_documents.get("resume_path"):
            resume_filename = self._generate_attachment_filename(
                document_type="Resume", job_title=job_info["job_title"], company_name=job_info["company_name"]
            )

            attachments.append(
                {
                    "path": generated_documents["resume_path"],
                    "filename": resume_filename,
                    "type": "resume",
                    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                }
            )

        # Cover letter attachment
        if generated_documents.get("cover_letter_path"):
            cover_letter_filename = self._generate_attachment_filename(
                document_type="Cover_Letter", job_title=job_info["job_title"], company_name=job_info["company_name"]
            )

            attachments.append(
                {
                    "path": generated_documents["cover_letter_path"],
                    "filename": cover_letter_filename,
                    "type": "cover_letter",
                    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                }
            )

        return attachments

    def _generate_attachment_filename(self, document_type: str, job_title: str, company_name: str) -> str:
        """
        Generate professional attachment filename

        Format: FirstName_LastName_DocumentType_JobTitle_CompanyName.docx
        Example: Steve_Glen_Resume_Marketing_Manager_ABC_Corp.docx

        Args:
            document_type: Type of document (Resume, Cover_Letter)
            job_title: Job title
            company_name: Company name

        Returns:
            Sanitized filename
        """
        # Get user name components
        name_parts = self.display_name.replace(" ", "_")

        # Sanitize job title and company name
        job_title_clean = self._sanitize_filename_part(job_title)
        company_name_clean = self._sanitize_filename_part(company_name)

        # Build filename
        filename = f"{name_parts}_{document_type}_{job_title_clean}_{company_name_clean}.docx"

        # Ensure filename length is reasonable (max 100 chars)
        if len(filename) > 100:
            # Truncate job title and company name proportionally
            available_chars = 100 - len(f"{name_parts}_{document_type}__.docx")
            job_title_clean = job_title_clean[: available_chars // 2]
            company_name_clean = company_name_clean[: available_chars // 2]
            filename = f"{name_parts}_{document_type}_{job_title_clean}_{company_name_clean}.docx"

        return filename

    def _sanitize_filename_part(self, text: str, max_length: int = 30) -> str:
        """
        Sanitize text for use in filename

        Args:
            text: Text to sanitize
            max_length: Maximum length of sanitized text

        Returns:
            Sanitized text safe for filenames
        """
        # Replace spaces with underscores
        text = text.replace(" ", "_")

        # Remove special characters (keep alphanumeric and underscore)
        text = re.sub(r"[^\w_]", "", text)

        # Remove multiple consecutive underscores
        text = re.sub(r"_+", "_", text)

        # Trim to max length
        if len(text) > max_length:
            text = text[:max_length]

        # Remove leading/trailing underscores
        text = text.strip("_")

        return text or "Document"

    def _build_email_metadata(self, job_data: Dict, job_info: Dict) -> Dict:
        """
        Build email metadata for headers and tracking

        Args:
            job_data: Full job data
            job_info: Extracted job info

        Returns:
            Metadata dictionary
        """
        return {
            "job_id": job_info["job_id"],
            "job_title": job_info["job_title"],
            "company_name": job_info["company_name"],
            "company_id": job_info["company_id"],
            "generated_at": datetime.now().isoformat(),
            "reference_id": self._generate_reference_id(job_info["job_id"]) if self.include_reference_id else None,
            "source_url": job_info["source_url"],
            "compatibility_score": job_info["compatibility_score"],
        }


# Factory function
def get_email_content_builder() -> EmailContentBuilder:
    """Get email content builder instance"""
    return EmailContentBuilder()


if __name__ == "__main__":
    # Demo/testing
    print("Email Content Builder Demo")
    print("=" * 60)

    # Sample job data
    sample_job_data = {
        "id": 12345,
        "job_title": "Senior Marketing Manager",
        "company_name": "Tech Innovations Inc",
        "company_id": 456,
        "office_city": "Toronto",
        "office_province": "Ontario",
        "office_country": "Canada",
        "salary_low": 85000,
        "salary_high": 110000,
        "posted_date": "2025-10-01",
        "source_url": "https://ca.indeed.com/job/12345",
        "application_email": "careers@techinnovations.com",
        "job_description": "We are seeking a Senior Marketing Manager...",
        "compatibility_score": 85,
        "title_compatibility_score": 28,
        "primary_industry": "Technology",
        "location_match": True,
        "hiring_manager_name": "Sarah Johnson",
    }

    sample_documents = {
        "resume_path": "/path/to/resume.docx",
        "cover_letter_path": "/path/to/cover_letter.docx",
    }

    builder = get_email_content_builder()
    email_package = builder.build_email_package(sample_job_data, sample_documents)

    print("\nGenerated Email Package:")
    print("-" * 60)
    print(f"Recipient: {email_package['recipient']}")
    print(f"Subject: {email_package['subject']}")
    print(f"Is Fallback: {email_package['is_fallback']}")
    print(f"\nAttachments: {len(email_package['attachments'])}")
    for att in email_package["attachments"]:
        print(f"  - {att['filename']}")

    print(f"\nBody Preview (first 500 chars):")
    print(email_package["body"][:500])
    print("...")

    print(f"\nMetadata:")
    for key, value in email_package["metadata"].items():
        print(f"  {key}: {value}")
