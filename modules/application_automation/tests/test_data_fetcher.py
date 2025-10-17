"""
Unit Tests for Data Fetcher

Tests for fetching application data from Flask API.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from modules.application_automation.data_fetcher import (
    DataFetcher,
    ApplicantProfile,
    JobDetails,
    ApplicationDocuments,
    ApplicationData,
)


class TestDataFetcher:
    """Test suite for DataFetcher class"""

    @pytest.fixture
    def mock_session(self):
        """Mock requests session"""
        with patch("modules.application_automation.data_fetcher.requests.Session") as mock:
            session = MagicMock()
            mock.return_value = session
            yield session

    @pytest.fixture
    def data_fetcher(self, mock_session):
        """Create DataFetcher instance with mocked session"""
        with patch.dict("os.environ", {"WEBHOOK_API_KEY": "test_key"}):
            fetcher = DataFetcher(api_base_url="http://test.com", api_key="test_key")
            fetcher.session = mock_session
            return fetcher

    def test_initialization(self):
        """Test DataFetcher initialization"""
        with patch.dict("os.environ", {"WEBHOOK_API_KEY": "test_key"}):
            fetcher = DataFetcher(api_base_url="http://test.com", api_key="test_key")
            assert fetcher.api_base_url == "http://test.com"
            assert fetcher.api_key == "test_key"
            assert fetcher.timeout == 30
            assert fetcher.max_retries == 3

    def test_initialization_missing_api_key(self):
        """Test initialization fails without API key"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                DataFetcher()

    def test_fetch_job_details_success(self, data_fetcher, mock_session):
        """Test successful job details fetching"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "job_id": "job_123",
                "title": "Software Engineer",
                "company": "Test Company",
                "location": "Remote",
                "apply_url": "https://example.com/apply",
                "description": "Test description",
                "salary_low": 80000,
                "salary_high": 100000,
                "job_type": "Full-time",
            },
        }
        mock_response.raise_for_status = Mock()
        mock_session.request.return_value = mock_response

        result = data_fetcher.fetch_job_details("job_123")

        assert isinstance(result, JobDetails)
        assert result.job_id == "job_123"
        assert result.title == "Software Engineer"
        assert result.company == "Test Company"
        assert result.salary_range == "$80,000 - $100,000"

    def test_fetch_applicant_profile_success(self, data_fetcher, mock_session):
        """Test successful applicant profile fetching"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "location": "New York, NY",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "website": "https://johndoe.com",
                "years_experience": "5",
            },
        }
        mock_response.raise_for_status = Mock()
        mock_session.request.return_value = mock_response

        result = data_fetcher.fetch_applicant_profile()

        assert isinstance(result, ApplicantProfile)
        assert result.full_name == "John Doe"
        assert result.email == "john@example.com"
        assert result.phone == "123-456-7890"

    def test_format_salary_range(self, data_fetcher):
        """Test salary formatting"""
        assert data_fetcher._format_salary(80000, 100000) == "$80,000 - $100,000"
        assert data_fetcher._format_salary(80000, 80000) == "$80,000"
        assert data_fetcher._format_salary(80000, None) == "$80,000"
        assert data_fetcher._format_salary(None, 100000) == "$100,000"
        assert data_fetcher._format_salary(None, None) is None

    def test_fetch_application_data_success(self, data_fetcher, mock_session):
        """Test fetching complete application data"""
        # Mock job details response
        job_response = Mock()
        job_response.json.return_value = {
            "success": True,
            "data": {
                "job_id": "job_123",
                "title": "Software Engineer",
                "company": "Test Company",
                "location": "Remote",
                "apply_url": "https://example.com/apply",
            },
        }
        job_response.raise_for_status = Mock()

        # Mock profile response
        profile_response = Mock()
        profile_response.json.return_value = {
            "success": True,
            "data": {"full_name": "John Doe", "email": "john@example.com"},
        }
        profile_response.raise_for_status = Mock()

        mock_session.request.side_effect = [job_response, profile_response]

        result = data_fetcher.fetch_application_data("job_123", "app_456")

        assert isinstance(result, ApplicationData)
        assert result.job.job_id == "job_123"
        assert result.applicant.full_name == "John Doe"
        assert result.metadata["job_id"] == "job_123"
        assert result.metadata["application_id"] == "app_456"


class TestApplicantProfile:
    """Test suite for ApplicantProfile dataclass"""

    def test_to_dict(self):
        """Test conversion to dictionary"""
        profile = ApplicantProfile(
            full_name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            location="New York",
        )

        result = profile.to_dict()

        assert result["full_name"] == "John Doe"
        assert result["email"] == "john@example.com"
        assert result["phone"] == "123-456-7890"
        assert result["location"] == "New York"


class TestJobDetails:
    """Test suite for JobDetails dataclass"""

    def test_to_dict(self):
        """Test conversion to dictionary"""
        job = JobDetails(
            job_id="job_123",
            title="Software Engineer",
            company="Test Company",
            location="Remote",
            apply_url="https://example.com/apply",
        )

        result = job.to_dict()

        assert result["job_id"] == "job_123"
        assert result["title"] == "Software Engineer"
        assert result["company"] == "Test Company"


class TestApplicationDocuments:
    """Test suite for ApplicationDocuments dataclass"""

    def test_has_resume(self):
        """Test resume availability check"""
        docs = ApplicationDocuments(resume_url="https://example.com/resume.pdf")
        assert docs.has_resume() is True

        docs = ApplicationDocuments(resume_content=b"resume data")
        assert docs.has_resume() is True

        docs = ApplicationDocuments()
        assert docs.has_resume() is False

    def test_has_cover_letter(self):
        """Test cover letter availability check"""
        docs = ApplicationDocuments(cover_letter_url="https://example.com/cover.pdf")
        assert docs.has_cover_letter() is True

        docs = ApplicationDocuments(cover_letter_content=b"cover letter data")
        assert docs.has_cover_letter() is True

        docs = ApplicationDocuments()
        assert docs.has_cover_letter() is False
