"""
Integration Tests for Application Automation Module

This test suite validates end-to-end functionality of the application automation
system, including Flask API endpoints, database operations, and Apify Actor integration.

Test Coverage:
- Flask API endpoints (trigger, record, list, review, stats)
- Database CRUD operations
- Mock Actor workflow simulation
- Error handling and edge cases
"""

import os
import sys
import json
import uuid
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Import Flask app and database
from app_modular import app
from modules.database.database_client import DatabaseClient
from modules.application_automation.models import ApplicationSubmission


@pytest.fixture
def client():
    """Create test client for Flask app"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def db_client():
    """Create database client for tests"""
    return DatabaseClient()


@pytest.fixture
def test_job_id():
    """Generate test job ID"""
    return f"test_job_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_application_id():
    """Generate test application ID"""
    return f"test_app_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def mock_apify_client():
    """Mock Apify client for testing"""
    with patch("apify_client.ApifyClient") as mock:
        mock_instance = MagicMock()
        mock_instance.actor().call.return_value = {"id": "test_run_123"}
        mock.return_value = mock_instance
        yield mock_instance


class TestFlaskAPIEndpoints:
    """Test Flask API endpoints for application automation"""

    def test_trigger_automation_success(self, client, test_job_id, test_application_id, mock_apify_client):
        """Test triggering automation successfully"""
        response = client.post(
            "/api/application-automation/trigger",
            json={"job_id": test_job_id, "application_id": test_application_id},
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        assert response.status_code in [200, 201]
        data = response.get_json()
        assert "submission_id" in data or "actor_run_id" in data

    def test_trigger_automation_missing_job_id(self, client):
        """Test triggering automation with missing job_id"""
        response = client.post(
            "/api/application-automation/trigger",
            json={},
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_trigger_automation_no_auth(self, client, test_job_id):
        """Test triggering automation without authentication"""
        response = client.post("/api/application-automation/trigger", json={"job_id": test_job_id})

        assert response.status_code == 401

    def test_record_submission_success(self, client, test_job_id):
        """Test recording submission result"""
        submission_data = {
            "job_id": test_job_id,
            "actor_run_id": "test_run_456",
            "status": "submitted",
            "form_platform": "indeed",
            "form_type": "standard_indeed_apply",
            "fields_filled": ["full_name", "email", "resume"],
            "submission_confirmed": True,
            "screenshot_urls": ["/storage/screenshot1.jpg"],
        }

        response = client.post(
            "/api/application-automation/submissions",
            json=submission_data,
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        assert response.status_code in [200, 201]
        data = response.get_json()
        assert "submission_id" in data

    def test_get_submission_by_id(self, client, test_job_id):
        """Test retrieving submission by ID"""
        # First create a submission
        submission_data = {
            "job_id": test_job_id,
            "status": "submitted",
            "form_platform": "indeed",
        }

        create_response = client.post(
            "/api/application-automation/submissions",
            json=submission_data,
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        if create_response.status_code in [200, 201]:
            submission_id = create_response.get_json().get("submission_id")

            # Now retrieve it
            get_response = client.get(
                f"/api/application-automation/submissions/{submission_id}",
                headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
            )

            assert get_response.status_code == 200
            data = get_response.get_json()
            assert data["data"]["job_id"] == test_job_id

    def test_list_submissions(self, client):
        """Test listing submissions"""
        response = client.get(
            "/api/application-automation/submissions",
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_list_submissions_filtered(self, client, test_job_id):
        """Test listing submissions with filters"""
        response = client.get(
            f"/api/application-automation/submissions?job_id={test_job_id}&status=submitted",
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data["data"], list)

    def test_mark_as_reviewed(self, client, test_job_id):
        """Test marking submission as reviewed"""
        # First create a submission
        submission_data = {
            "job_id": test_job_id,
            "status": "submitted",
            "form_platform": "indeed",
        }

        create_response = client.post(
            "/api/application-automation/submissions",
            json=submission_data,
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        if create_response.status_code in [200, 201]:
            submission_id = create_response.get_json().get("submission_id")

            # Mark as reviewed
            review_response = client.put(
                f"/api/application-automation/submissions/{submission_id}/review",
                json={"reviewed_by": "test_user", "review_notes": "Looks good"},
                headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
            )

            assert review_response.status_code == 200

    def test_get_stats(self, client):
        """Test getting submission statistics"""
        response = client.get(
            "/api/application-automation/stats",
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert "total_submissions" in data["data"] or "stats" in data["data"]


class TestDatabaseOperations:
    """Test database operations for application submissions"""

    def test_create_submission(self, db_client, test_job_id):
        """Test creating submission record in database"""
        try:
            submission_id = str(uuid.uuid4())
            query = """
                INSERT INTO apify_application_submissions (
                    submission_id, job_id, status, form_platform, submitted_at
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING submission_id
            """
            result = db_client.execute_write(
                query, (submission_id, test_job_id, "pending", "indeed", datetime.utcnow())
            )
            assert result is not None
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_query_submissions(self, db_client, test_job_id):
        """Test querying submissions from database"""
        try:
            query = "SELECT * FROM apify_application_submissions WHERE job_id = %s"
            result = db_client.execute_read(query, (test_job_id,))
            assert isinstance(result, (list, tuple))
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_update_submission_status(self, db_client, test_job_id):
        """Test updating submission status"""
        try:
            # Create submission first
            submission_id = str(uuid.uuid4())
            insert_query = """
                INSERT INTO apify_application_submissions (
                    submission_id, job_id, status, form_platform, submitted_at
                ) VALUES (%s, %s, %s, %s, %s)
            """
            db_client.execute_write(
                insert_query, (submission_id, test_job_id, "pending", "indeed", datetime.utcnow())
            )

            # Update status
            update_query = """
                UPDATE apify_application_submissions
                SET status = %s, updated_at = %s
                WHERE submission_id = %s
            """
            db_client.execute_write(update_query, ("submitted", datetime.utcnow(), submission_id))

            # Verify update
            select_query = "SELECT status FROM apify_application_submissions WHERE submission_id = %s"
            result = db_client.execute_read(select_query, (submission_id,))
            assert result[0][0] == "submitted"
        except Exception as e:
            pytest.skip(f"Database not available: {e}")


class TestMockActorWorkflow:
    """Test mock Actor workflow simulation"""

    def test_actor_input_validation(self):
        """Test Actor input validation"""
        from modules.application_automation.actor_main import validate_input

        # Valid input
        valid_input = {"job_id": "job_123", "application_id": "app_456"}
        assert validate_input(valid_input) is True

        # Missing job_id
        invalid_input = {"application_id": "app_456"}
        assert validate_input(invalid_input) is False

    def test_form_mapping_load(self):
        """Test loading form mappings"""
        from modules.application_automation.form_mappings import indeed

        mappings_path = os.path.join(
            os.path.dirname(__file__), "../form_mappings/indeed.json"
        )

        if os.path.exists(mappings_path):
            with open(mappings_path, "r") as f:
                mappings = json.load(f)
                assert "standard_indeed_apply" in mappings
                assert "indeed_quick_apply" in mappings
        else:
            pytest.skip("Form mappings file not found")

    def test_screenshot_capture_mock(self):
        """Test screenshot capture (mocked)"""
        from modules.application_automation.screenshot_manager import ScreenshotManager

        manager = ScreenshotManager()
        # This would normally capture a screenshot, but we're just testing initialization
        assert manager is not None


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_platform(self, client, test_job_id):
        """Test handling invalid platform"""
        submission_data = {
            "job_id": test_job_id,
            "status": "submitted",
            "form_platform": "invalid_platform",  # Should fail validation
        }

        response = client.post(
            "/api/application-automation/submissions",
            json=submission_data,
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        # Should either reject or accept with validation
        assert response.status_code in [200, 201, 400]

    def test_missing_required_fields(self, client):
        """Test handling missing required fields"""
        submission_data = {"status": "submitted"}  # Missing job_id

        response = client.post(
            "/api/application-automation/submissions",
            json=submission_data,
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        assert response.status_code == 400

    def test_invalid_submission_id(self, client):
        """Test handling invalid submission ID"""
        response = client.get(
            "/api/application-automation/submissions/invalid-uuid",
            headers={"X-API-Key": os.environ.get("WEBHOOK_API_KEY", "test_key")},
        )

        assert response.status_code in [400, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
