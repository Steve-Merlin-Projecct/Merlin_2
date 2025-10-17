"""
Unit Tests for Calendly Integration

Tests the TemplateEngine URL tracking functionality including:
- URL variable detection
- Tracked URL generation
- Job/application context passing
- Caching mechanism
- Error handling and fallbacks
- CandidateProfileManager functionality

Version: 1.0.0
Date: October 9, 2025
"""

import pytest
import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add modules to path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.content.document_generation.template_engine import TemplateEngine
from modules.user_management.candidate_profile_manager import CandidateProfileManager


class TestTemplateEngineURLTracking:
    """Test suite for TemplateEngine URL tracking functionality"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.engine = TemplateEngine(enable_url_tracking=True)
        self.test_job_id = "550e8400-e29b-41d4-a716-446655440000"
        self.test_application_id = "650e8400-e29b-41d4-a716-446655440001"
        self.test_calendly_url = "https://calendly.com/steve-glen/30min"
        self.test_linkedin_url = "https://linkedin.com/in/steve-glen"
        self.test_portfolio_url = "https://steveglen.com"

    def test_url_tracking_enabled_by_default(self):
        """Verify URL tracking is enabled by default"""
        engine = TemplateEngine()
        assert engine.enable_url_tracking is True

    def test_url_tracking_can_be_disabled(self):
        """Verify URL tracking can be disabled via constructor"""
        engine = TemplateEngine(enable_url_tracking=False)
        assert engine.enable_url_tracking is False

    def test_trackable_url_variables_defined(self):
        """Verify trackable URL variables are correctly defined"""
        assert "calendly_url" in self.engine.TRACKABLE_URL_VARIABLES
        assert "linkedin_url" in self.engine.TRACKABLE_URL_VARIABLES
        assert "portfolio_url" in self.engine.TRACKABLE_URL_VARIABLES

    def test_url_variable_to_function_mapping(self):
        """Verify URL variable to function name mapping is correct"""
        assert self.engine.URL_VARIABLE_TO_FUNCTION["calendly_url"] == "Calendly"
        assert self.engine.URL_VARIABLE_TO_FUNCTION["linkedin_url"] == "LinkedIn"
        assert self.engine.URL_VARIABLE_TO_FUNCTION["portfolio_url"] == "Portfolio"

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_calendly_url_variable_detected(self, mock_link_tracker):
        """Verify TemplateEngine detects and processes calendly_url variable"""
        # Setup mock
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.return_value = {
            "tracking_id": "lt_calendly_abc123",
            "redirect_url": "http://localhost:5000/track/lt_calendly_abc123",
        }
        mock_link_tracker.return_value = mock_tracker_instance

        # Test data
        template_text = "Schedule a meeting: <<calendly_url>>"
        data = {"calendly_url": self.test_calendly_url}
        stats = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }

        # Execute
        result = self.engine.substitute_variables(
            template_text,
            data,
            stats,
            job_id=self.test_job_id,
            application_id=self.test_application_id,
        )

        # Verify LinkTracker was called
        mock_tracker_instance.create_tracked_link.assert_called_once()
        call_args = mock_tracker_instance.create_tracked_link.call_args[1]
        assert call_args["original_url"] == self.test_calendly_url
        assert call_args["link_function"] == "Calendly"
        assert call_args["job_id"] == self.test_job_id
        assert call_args["application_id"] == self.test_application_id

        # Verify result contains tracked URL
        assert "http://localhost:5000/track/lt_calendly_abc123" in result

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_linkedin_url_variable_detected(self, mock_link_tracker):
        """Verify TemplateEngine detects and processes linkedin_url variable"""
        # Setup mock
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.return_value = {
            "tracking_id": "lt_linkedin_xyz789",
            "redirect_url": "http://localhost:5000/track/lt_linkedin_xyz789",
        }
        mock_link_tracker.return_value = mock_tracker_instance

        # Test data
        template_text = "View my profile: <<linkedin_url>>"
        data = {"linkedin_url": self.test_linkedin_url}
        stats = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }

        # Execute
        result = self.engine.substitute_variables(
            template_text,
            data,
            stats,
            job_id=self.test_job_id,
            application_id=self.test_application_id,
        )

        # Verify
        assert mock_tracker_instance.create_tracked_link.called
        assert "http://localhost:5000/track/lt_linkedin_xyz789" in result

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_portfolio_url_variable_detected(self, mock_link_tracker):
        """Verify TemplateEngine detects and processes portfolio_url variable"""
        # Setup mock
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.return_value = {
            "tracking_id": "lt_portfolio_def456",
            "redirect_url": "http://localhost:5000/track/lt_portfolio_def456",
        }
        mock_link_tracker.return_value = mock_tracker_instance

        # Test data
        template_text = "Portfolio: <<portfolio_url>>"
        data = {"portfolio_url": self.test_portfolio_url}
        stats = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }

        # Execute
        result = self.engine.substitute_variables(
            template_text, data, stats, self.test_job_id, self.test_application_id
        )

        # Verify
        assert mock_tracker_instance.create_tracked_link.called
        assert "http://localhost:5000/track/lt_portfolio_def456" in result

    def test_non_url_variables_ignored(self):
        """Verify non-URL variables are not sent to LinkTracker"""
        # Test data
        template_text = "Hello <<first_name>> <<last_name>>"
        data = {"first_name": "Steve", "last_name": "Glen"}
        stats = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }

        # Execute
        result = self.engine.substitute_variables(template_text, data, stats)

        # Verify normal substitution occurred
        assert "Hello Steve Glen" == result
        assert "first_name" in stats["variables_substituted"]
        assert "last_name" in stats["variables_substituted"]

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_tracked_url_format(self, mock_link_tracker):
        """Verify tracked URL has correct format with tracking_id"""
        # Setup mock
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.return_value = {
            "tracking_id": "lt_calendly_test123",
            "redirect_url": "http://localhost:5000/track/lt_calendly_test123",
        }
        mock_link_tracker.return_value = mock_tracker_instance

        # Execute
        tracked_url = self.engine._get_tracked_url(
            self.test_calendly_url,
            "Calendly",
            self.test_job_id,
            self.test_application_id,
        )

        # Verify format
        assert tracked_url.startswith("http://localhost:5000/track/")
        assert "lt_calendly_test123" in tracked_url

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_job_id_passed_to_tracker(self, mock_link_tracker):
        """Verify job_id is correctly passed to LinkTracker"""
        # Setup mock
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.return_value = {
            "tracking_id": "lt_test",
            "redirect_url": "http://localhost:5000/track/lt_test",
        }
        mock_link_tracker.return_value = mock_tracker_instance

        # Execute
        self.engine._get_tracked_url(
            self.test_calendly_url,
            "Calendly",
            self.test_job_id,
            self.test_application_id,
        )

        # Verify job_id was passed
        call_kwargs = mock_tracker_instance.create_tracked_link.call_args[1]
        assert call_kwargs["job_id"] == self.test_job_id

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_application_id_passed_to_tracker(self, mock_link_tracker):
        """Verify application_id is correctly passed to LinkTracker"""
        # Setup mock
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.return_value = {
            "tracking_id": "lt_test",
            "redirect_url": "http://localhost:5000/track/lt_test",
        }
        mock_link_tracker.return_value = mock_tracker_instance

        # Execute
        self.engine._get_tracked_url(
            self.test_calendly_url,
            "Calendly",
            self.test_job_id,
            self.test_application_id,
        )

        # Verify application_id was passed
        call_kwargs = mock_tracker_instance.create_tracked_link.call_args[1]
        assert call_kwargs["application_id"] == self.test_application_id

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_link_function_mapping(self, mock_link_tracker):
        """Verify 'calendly_url' maps to 'Calendly' link function"""
        # Setup mock
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.return_value = {
            "tracking_id": "lt_test",
            "redirect_url": "http://localhost:5000/track/lt_test",
        }
        mock_link_tracker.return_value = mock_tracker_instance

        # Execute
        template_text = "<<calendly_url>>"
        data = {"calendly_url": self.test_calendly_url}
        stats = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }

        self.engine.substitute_variables(
            template_text, data, stats, self.test_job_id, self.test_application_id
        )

        # Verify link_function is 'Calendly'
        call_kwargs = mock_tracker_instance.create_tracked_link.call_args[1]
        assert call_kwargs["link_function"] == "Calendly"

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_fallback_on_tracker_failure(self, mock_link_tracker):
        """Verify original URL is used when LinkTracker fails"""
        # Setup mock to raise exception
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.side_effect = Exception(
            "Database connection failed"
        )
        mock_link_tracker.return_value = mock_tracker_instance

        # Execute
        result = self.engine._get_tracked_url(
            self.test_calendly_url,
            "Calendly",
            self.test_job_id,
            self.test_application_id,
        )

        # Verify fallback to original URL
        assert result == self.test_calendly_url

    def test_fallback_on_import_error(self):
        """Verify original URL is used when LinkTracker module is unavailable"""
        # This test verifies the lazy import error handling
        with patch(
            "modules.link_tracking.link_tracker.LinkTracker",
            side_effect=ImportError("Module not found"),
        ):
            result = self.engine._get_tracked_url(
                self.test_calendly_url,
                "Calendly",
                self.test_job_id,
                self.test_application_id,
            )

            # Verify fallback
            assert result == self.test_calendly_url

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_url_cached_on_second_call(self, mock_link_tracker):
        """Verify tracked URL is cached and LinkTracker only called once"""
        # Setup mock
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.return_value = {
            "tracking_id": "lt_cached",
            "redirect_url": "http://localhost:5000/track/lt_cached",
        }
        mock_link_tracker.return_value = mock_tracker_instance

        # First call
        result1 = self.engine._get_tracked_url(
            self.test_calendly_url,
            "Calendly",
            self.test_job_id,
            self.test_application_id,
        )

        # Second call with same parameters
        result2 = self.engine._get_tracked_url(
            self.test_calendly_url,
            "Calendly",
            self.test_job_id,
            self.test_application_id,
        )

        # Verify LinkTracker only called once
        assert mock_tracker_instance.create_tracked_link.call_count == 1

        # Verify both results are the same
        assert result1 == result2
        assert result1 == "http://localhost:5000/track/lt_cached"

    @patch("modules.link_tracking.link_tracker.LinkTracker")
    def test_cache_key_includes_job_context(self, mock_link_tracker):
        """Verify different job_id creates different cache entry"""
        # Setup mock
        mock_tracker_instance = Mock()
        mock_tracker_instance.create_tracked_link.return_value = {
            "tracking_id": "lt_test",
            "redirect_url": "http://localhost:5000/track/lt_test",
        }
        mock_link_tracker.return_value = mock_tracker_instance

        # Call with first job_id
        self.engine._get_tracked_url(
            self.test_calendly_url,
            "Calendly",
            self.test_job_id,
            self.test_application_id,
        )

        # Call with different job_id
        different_job_id = "999e8400-e29b-41d4-a716-446655440099"
        self.engine._get_tracked_url(
            self.test_calendly_url,
            "Calendly",
            different_job_id,
            self.test_application_id,
        )

        # Verify LinkTracker called twice (different cache keys)
        assert mock_tracker_instance.create_tracked_link.call_count == 2

    def test_url_tracking_disabled(self):
        """Verify URL tracking can be disabled and original URLs are used"""
        # Create engine with tracking disabled
        engine = TemplateEngine(enable_url_tracking=False)

        template_text = "Schedule: <<calendly_url>>"
        data = {"calendly_url": self.test_calendly_url}
        stats = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }

        # Execute
        result = engine.substitute_variables(template_text, data, stats)

        # Verify original URL is used (not tracked)
        assert self.test_calendly_url in result
        assert "/track/" not in result


class TestCandidateProfileManager:
    """Test suite for CandidateProfileManager functionality"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.manager = CandidateProfileManager()
        self.test_user_id = "steve_glen"

    @patch("modules.user_management.candidate_profile_manager.psycopg2.connect")
    def test_get_candidate_info_returns_all_fields(self, mock_connect):
        """Verify get_candidate_info returns all required fields"""
        # Setup mock database response
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "first_name": "Steve",
            "last_name": "Glen",
            "email": "1234.s.t.e.v.e.glen@gmail.com",
            "phone_number": "(780) 555-0123",
            "mailing_address": "Edmonton, AB, Canada",
            "calendly_url": "https://calendly.com/steve-glen/30min",
            "linkedin_url": "https://linkedin.com/in/steve-glen",
            "portfolio_url": "https://steveglen.com",
        }
        mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        # Execute
        result = self.manager.get_candidate_info(self.test_user_id)

        # Verify all fields present
        assert result["first_name"] == "Steve"
        assert result["last_name"] == "Glen"
        assert result["email"] == "1234.s.t.e.v.e.glen@gmail.com"
        assert result["phone_number"] == "(780) 555-0123"
        assert result["mailing_address"] == "Edmonton, AB, Canada"
        assert result["calendly_url"] == "https://calendly.com/steve-glen/30min"
        assert result["linkedin_url"] == "https://linkedin.com/in/steve-glen"
        assert result["portfolio_url"] == "https://steveglen.com"

    @patch("modules.user_management.candidate_profile_manager.psycopg2.connect")
    def test_get_calendly_url_returns_correct_value(self, mock_connect):
        """Verify get_calendly_url returns the correct URL"""
        # Setup mock
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "calendly_url": "https://calendly.com/steve-glen/30min"
        }
        mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        # Execute
        result = self.manager.get_calendly_url(self.test_user_id)

        # Verify
        assert result == "https://calendly.com/steve-glen/30min"

    @patch("modules.user_management.candidate_profile_manager.psycopg2.connect")
    def test_get_linkedin_url_returns_correct_value(self, mock_connect):
        """Verify get_linkedin_url returns the correct URL"""
        # Setup mock
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "linkedin_url": "https://linkedin.com/in/steve-glen"
        }
        mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        # Execute
        result = self.manager.get_linkedin_url(self.test_user_id)

        # Verify
        assert result == "https://linkedin.com/in/steve-glen"

    @patch("modules.user_management.candidate_profile_manager.psycopg2.connect")
    def test_get_portfolio_url_returns_correct_value(self, mock_connect):
        """Verify get_portfolio_url returns the correct URL"""
        # Setup mock
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"portfolio_url": "https://steveglen.com"}
        mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        # Execute
        result = self.manager.get_portfolio_url(self.test_user_id)

        # Verify
        assert result == "https://steveglen.com"

    @patch("modules.user_management.candidate_profile_manager.psycopg2.connect")
    def test_user_not_found_returns_defaults(self, mock_connect):
        """Verify default values returned when user not found"""
        # Setup mock to return None (user not found)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        # Execute
        result = self.manager.get_candidate_info("nonexistent_user")

        # Verify defaults returned
        assert result["first_name"] == "Steve"
        assert result["last_name"] == "Glen"
        assert result["email"] == "1234.s.t.e.v.e.glen@gmail.com"

    @patch("modules.user_management.candidate_profile_manager.psycopg2.connect")
    def test_database_error_returns_defaults(self, mock_connect):
        """Verify default values returned when database error occurs"""
        # Setup mock to raise exception
        mock_connect.side_effect = Exception("Database connection failed")

        # Execute
        result = self.manager.get_candidate_info(self.test_user_id)

        # Verify defaults returned (no exception raised)
        assert result["first_name"] == "Steve"
        assert result["calendly_url"] is None

    @patch("modules.user_management.candidate_profile_manager.psycopg2.connect")
    def test_update_calendly_url_success(self, mock_connect):
        """Verify update_calendly_url successfully updates the database"""
        # Setup mock
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1  # One row updated
        mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        # Execute
        result = self.manager.update_calendly_url(
            "https://calendly.com/steve-glen/consultation", self.test_user_id
        )

        # Verify
        assert result is True
        assert mock_cursor.execute.called

    @patch("modules.user_management.candidate_profile_manager.psycopg2.connect")
    def test_update_calendly_url_user_not_found(self, mock_connect):
        """Verify update_calendly_url returns False when user not found"""
        # Setup mock
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0  # No rows updated
        mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        # Execute
        result = self.manager.update_calendly_url(
            "https://calendly.com/steve-glen/consultation", "nonexistent_user"
        )

        # Verify
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
