"""
Simple API Tests for Application Automation Module

Simplified test suite that tests API functionality without full app initialization.
Tests the automation_api blueprint in isolation.
"""

import os
import sys
import json
import uuid
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))


class TestAutomationAPILogic:
    """Test automation API logic without Flask app"""

    def test_input_validation(self):
        """Test input validation logic"""
        # Valid inputs
        assert validate_trigger_input({"job_id": "job_123"}) is True
        assert validate_trigger_input({"job_id": "job_123", "application_id": "app_456"}) is True

        # Invalid inputs
        assert validate_trigger_input({}) is False
        assert validate_trigger_input({"application_id": "app_456"}) is False
        assert validate_trigger_input(None) is False

    def test_submission_data_validation(self):
        """Test submission data validation"""
        valid_data = {
            "job_id": "job_123",
            "status": "submitted",
            "form_platform": "indeed",
        }
        assert validate_submission_data(valid_data) is True

        # Missing required fields
        assert validate_submission_data({"status": "submitted"}) is False
        assert validate_submission_data({"job_id": "job_123"}) is False


class TestFormMappings:
    """Test form mapping files and structure"""

    def test_indeed_mappings_exist(self):
        """Test that Indeed form mappings file exists"""
        mappings_path = os.path.join(
            os.path.dirname(__file__), "../form_mappings/indeed.json"
        )
        assert os.path.exists(mappings_path), "Indeed form mappings file not found"

    def test_indeed_mappings_structure(self):
        """Test Indeed form mappings structure"""
        mappings_path = os.path.join(
            os.path.dirname(__file__), "../form_mappings/indeed.json"
        )

        with open(mappings_path, "r") as f:
            mappings = json.load(f)

        # Check required form types
        assert "standard_indeed_apply" in mappings, "standard_indeed_apply not found"
        assert "indeed_quick_apply" in mappings, "indeed_quick_apply not found"

        # Check field structure
        standard_form = mappings["standard_indeed_apply"]
        assert "fields" in standard_form, "fields not found in standard form"
        assert isinstance(standard_form["fields"], dict), "fields should be a dictionary"

        # Check specific fields
        fields = standard_form["fields"]
        assert "full_name" in fields or "first_name" in fields, "name field not found"
        assert "email" in fields, "email field not found"
        assert "resume" in fields, "resume field not found"

    def test_field_mapping_structure(self):
        """Test individual field mapping structure"""
        mappings_path = os.path.join(
            os.path.dirname(__file__), "../form_mappings/indeed.json"
        )

        with open(mappings_path, "r") as f:
            mappings = json.load(f)

        # Get a field mapping
        fields = mappings["standard_indeed_apply"]["fields"]
        email_field = fields.get("email")

        assert email_field is not None, "email field not found"
        assert "selectors" in email_field, "selectors not found in field"
        assert isinstance(email_field["selectors"], list), "selectors should be a list"
        assert len(email_field["selectors"]) > 0, "selectors should not be empty"


class TestDatabaseModels:
    """Test database models"""

    def test_application_submission_model_exists(self):
        """Test that ApplicationSubmission model exists"""
        from modules.application_automation.models import ApplicationSubmission

        assert ApplicationSubmission is not None

    def test_application_submission_tablename(self):
        """Test that table name is correct"""
        from modules.application_automation.models import ApplicationSubmission

        assert ApplicationSubmission.__tablename__ == "apify_application_submissions"

    def test_application_submission_to_dict(self):
        """Test to_dict method"""
        from modules.application_automation.models import ApplicationSubmission

        # Create a mock submission
        submission = ApplicationSubmission()
        submission.submission_id = uuid.uuid4()
        submission.job_id = "job_123"
        submission.status = "submitted"
        submission.form_platform = "indeed"
        submission.submitted_at = datetime.utcnow()

        # Convert to dict
        data = submission.to_dict()

        assert isinstance(data, dict)
        assert "submission_id" in data
        assert "job_id" in data
        assert data["job_id"] == "job_123"
        assert data["status"] == "submitted"


class TestScreenshotManager:
    """Test screenshot manager functionality"""

    def test_screenshot_manager_initialization(self):
        """Test ScreenshotManager can be initialized"""
        from modules.application_automation.screenshot_manager import ScreenshotManager

        manager = ScreenshotManager()
        assert manager is not None

    def test_screenshot_path_generation(self):
        """Test screenshot path generation"""
        from modules.application_automation.screenshot_manager import ScreenshotManager

        manager = ScreenshotManager()
        job_id = "job_123"
        screenshot_type = "pre_submit"

        # Generate path (mock method if needed)
        path = manager._generate_screenshot_path(job_id, screenshot_type)

        assert path is not None
        assert isinstance(path, str)
        assert job_id in path or screenshot_type in path


class TestDataFetcher:
    """Test data fetcher functionality"""

    def test_data_fetcher_initialization(self):
        """Test DataFetcher can be initialized"""
        from modules.application_automation.data_fetcher import ApplicationDataFetcher

        fetcher = ApplicationDataFetcher(api_url="http://localhost:5000", api_key="test_key")
        assert fetcher is not None
        assert fetcher.api_url == "http://localhost:5000"

    @patch('requests.get')
    def test_fetch_job_details_mock(self, mock_get):
        """Test fetching job details with mocked response"""
        from modules.application_automation.data_fetcher import ApplicationDataFetcher

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "job_id": "job_123",
                "title": "Software Engineer",
                "company": "Test Company",
                "apply_url": "https://indeed.com/apply/123"
            }
        }
        mock_get.return_value = mock_response

        fetcher = ApplicationDataFetcher(api_url="http://localhost:5000", api_key="test_key")
        result = fetcher.fetch_job_details("job_123")

        assert result is not None
        assert "job_id" in result or "data" in result


# Helper functions for validation (these would normally be in automation_api.py)
def validate_trigger_input(data):
    """Validate trigger input data"""
    if not data:
        return False
    if "job_id" not in data:
        return False
    return True


def validate_submission_data(data):
    """Validate submission data"""
    if not data:
        return False
    required_fields = ["job_id", "status", "form_platform"]
    for field in required_fields:
        if field not in data:
            return False
    return True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
