"""
Data Fetcher for Application Automation

This module fetches application data from the Flask backend API to populate
job application forms. It retrieves job details, applicant profile information,
and generated documents (resume and cover letter).

Design Principles:
- Secure API communication using API key authentication
- Efficient data retrieval with caching support
- Comprehensive error handling and retry logic
- Type-safe data structures
"""

import os
import logging
import requests
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import time

logger = logging.getLogger(__name__)


@dataclass
class ApplicantProfile:
    """Applicant profile information for form filling"""

    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    years_experience: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin_url": self.linkedin_url,
            "website": self.website,
            "years_experience": self.years_experience,
        }


@dataclass
class JobDetails:
    """Job posting details"""

    job_id: str
    title: str
    company: str
    location: str
    apply_url: str
    description: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "apply_url": self.apply_url,
            "description": self.description,
            "salary_range": self.salary_range,
            "job_type": self.job_type,
        }


@dataclass
class ApplicationDocuments:
    """Generated documents for application"""

    resume_url: Optional[str] = None
    resume_content: Optional[bytes] = None
    cover_letter_url: Optional[str] = None
    cover_letter_content: Optional[bytes] = None

    def has_resume(self) -> bool:
        """Check if resume is available"""
        return bool(self.resume_url or self.resume_content)

    def has_cover_letter(self) -> bool:
        """Check if cover letter is available"""
        return bool(self.cover_letter_url or self.cover_letter_content)


@dataclass
class ApplicationData:
    """Complete application data bundle"""

    applicant: ApplicantProfile
    job: JobDetails
    documents: ApplicationDocuments
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "applicant": self.applicant.to_dict(),
            "job": self.job.to_dict(),
            "documents": {
                "has_resume": self.documents.has_resume(),
                "has_cover_letter": self.documents.has_cover_letter(),
                "resume_url": self.documents.resume_url,
                "cover_letter_url": self.documents.cover_letter_url,
            },
            "metadata": self.metadata,
        }


class DataFetcher:
    """
    Fetches application data from Flask backend API

    This class handles all communication with the Flask API to retrieve
    applicant profiles, job details, and generated documents. It implements
    retry logic, caching, and secure authentication.
    """

    def __init__(
        self,
        api_base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize data fetcher

        Args:
            api_base_url: Base URL of Flask API (e.g., 'https://api.example.com')
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_base_url = api_base_url or os.environ.get("FLASK_API_URL", "http://localhost:5000")
        self.api_key = api_key or os.environ.get("WEBHOOK_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.api_key:
            raise ValueError("API key is required (WEBHOOK_API_KEY environment variable)")

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": self.api_key, "Content-Type": "application/json"})

        logger.info(f"DataFetcher initialized with API base URL: {self.api_base_url}")

    def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated API request with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/api/jobs/123')
            params: Query parameters
            json_data: JSON request body

        Returns:
            Response data as dictionary

        Raises:
            Exception: If request fails after all retries
        """
        url = f"{self.api_base_url}{endpoint}"

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"API request: {method} {url} (attempt {attempt + 1}/{self.max_retries})")

                response = self.session.request(
                    method=method, url=url, params=params, json=json_data, timeout=self.timeout
                )

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    raise Exception(f"Request timeout after {self.max_retries} attempts")

            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code in [500, 502, 503, 504] and attempt < self.max_retries - 1:
                    time.sleep(2**attempt)
                else:
                    raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2**attempt)
                else:
                    raise Exception(f"Request failed after {self.max_retries} attempts: {e}")

    def fetch_job_details(self, job_id: str) -> JobDetails:
        """
        Fetch job posting details

        Args:
            job_id: Unique job identifier

        Returns:
            JobDetails object with job information

        Raises:
            Exception: If job not found or API error
        """
        logger.info(f"Fetching job details for job_id: {job_id}")

        response = self._make_request("GET", f"/api/database/jobs/{job_id}")

        if not response.get("success"):
            raise Exception(f"Failed to fetch job details: {response.get('error')}")

        job_data = response.get("data", {})

        return JobDetails(
            job_id=job_data.get("job_id", job_id),
            title=job_data.get("title", ""),
            company=job_data.get("company", ""),
            location=job_data.get("location", ""),
            apply_url=job_data.get("apply_url", ""),
            description=job_data.get("description"),
            salary_range=self._format_salary(job_data.get("salary_low"), job_data.get("salary_high")),
            job_type=job_data.get("job_type"),
        )

    def fetch_applicant_profile(self, profile_id: Optional[str] = None) -> ApplicantProfile:
        """
        Fetch applicant profile information

        Args:
            profile_id: Optional profile ID (defaults to primary profile)

        Returns:
            ApplicantProfile object with applicant information

        Raises:
            Exception: If profile not found or API error
        """
        logger.info(f"Fetching applicant profile (profile_id: {profile_id or 'default'})")

        endpoint = f"/api/user-profile/{profile_id}" if profile_id else "/api/user-profile/primary"
        response = self._make_request("GET", endpoint)

        if not response.get("success"):
            raise Exception(f"Failed to fetch applicant profile: {response.get('error')}")

        profile_data = response.get("data", {})

        return ApplicantProfile(
            full_name=profile_data.get("full_name", ""),
            email=profile_data.get("email", ""),
            phone=profile_data.get("phone"),
            location=profile_data.get("location"),
            linkedin_url=profile_data.get("linkedin_url"),
            website=profile_data.get("website"),
            years_experience=profile_data.get("years_experience"),
        )

    def fetch_documents(self, application_id: str) -> ApplicationDocuments:
        """
        Fetch generated documents (resume and cover letter)

        Args:
            application_id: Application ID for which documents were generated

        Returns:
            ApplicationDocuments object with document URLs/content

        Raises:
            Exception: If documents not found or API error
        """
        logger.info(f"Fetching documents for application_id: {application_id}")

        response = self._make_request("GET", f"/api/documents/application/{application_id}")

        if not response.get("success"):
            raise Exception(f"Failed to fetch documents: {response.get('error')}")

        docs_data = response.get("data", {})

        # Fetch document URLs
        resume_url = docs_data.get("resume_url")
        cover_letter_url = docs_data.get("cover_letter_url")

        # Optionally download document content
        resume_content = None
        cover_letter_content = None

        if resume_url:
            try:
                resume_content = self._download_document(resume_url)
            except Exception as e:
                logger.warning(f"Failed to download resume: {e}")

        if cover_letter_url:
            try:
                cover_letter_content = self._download_document(cover_letter_url)
            except Exception as e:
                logger.warning(f"Failed to download cover letter: {e}")

        return ApplicationDocuments(
            resume_url=resume_url,
            resume_content=resume_content,
            cover_letter_url=cover_letter_url,
            cover_letter_content=cover_letter_content,
        )

    def fetch_application_data(self, job_id: str, application_id: Optional[str] = None) -> ApplicationData:
        """
        Fetch complete application data bundle

        This is the main method that retrieves all data needed for form filling.

        Args:
            job_id: Job posting ID to apply for
            application_id: Optional application ID (for tracking)

        Returns:
            ApplicationData object with all required information

        Raises:
            Exception: If data fetching fails
        """
        logger.info(f"Fetching complete application data for job_id: {job_id}")

        try:
            # Fetch all required data
            job_details = self.fetch_job_details(job_id)
            applicant_profile = self.fetch_applicant_profile()

            # Fetch documents if application_id provided
            documents = ApplicationDocuments()
            if application_id:
                try:
                    documents = self.fetch_documents(application_id)
                except Exception as e:
                    logger.warning(f"Failed to fetch documents: {e}")

            # Metadata
            metadata = {
                "fetched_at": datetime.utcnow().isoformat(),
                "job_id": job_id,
                "application_id": application_id,
            }

            return ApplicationData(
                applicant=applicant_profile, job=job_details, documents=documents, metadata=metadata
            )

        except Exception as e:
            logger.error(f"Failed to fetch application data: {e}")
            raise Exception(f"Failed to fetch application data: {e}")

    def _download_document(self, document_url: str) -> bytes:
        """
        Download document content from URL

        Args:
            document_url: URL of document to download

        Returns:
            Document content as bytes

        Raises:
            Exception: If download fails
        """
        logger.debug(f"Downloading document from: {document_url}")

        response = self.session.get(document_url, timeout=self.timeout)
        response.raise_for_status()

        return response.content

    def _format_salary(self, salary_low: Optional[int], salary_high: Optional[int]) -> Optional[str]:
        """
        Format salary range as string

        Args:
            salary_low: Low end of salary range
            salary_high: High end of salary range

        Returns:
            Formatted salary string (e.g., "$80,000 - $100,000")
        """
        if not salary_low and not salary_high:
            return None

        if salary_low and salary_high and salary_low != salary_high:
            return f"${salary_low:,} - ${salary_high:,}"
        elif salary_low:
            return f"${salary_low:,}"
        elif salary_high:
            return f"${salary_high:,}"

        return None

    def close(self):
        """Close session and cleanup resources"""
        self.session.close()
        logger.debug("DataFetcher session closed")
