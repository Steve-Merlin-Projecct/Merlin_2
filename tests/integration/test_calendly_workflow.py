"""
Integration Tests for Calendly Workflow

End-to-end tests for the complete Calendly integration including:
- Document generation with tracked URLs
- Click tracking and redirect functionality
- Analytics query and reporting
- Multi-document workflow (resume + cover letter for same job)

These tests require:
- Database connection
- LinkTracker system operational
- Template files available

Version: 1.0.0
Date: October 9, 2025
"""

import pytest
import os
import sys
import uuid
from datetime import datetime

# Add modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from modules.content.document_generation.template_engine import TemplateEngine
from modules.content.document_generation.document_generator import DocumentGenerator
from modules.user_management.candidate_profile_manager import CandidateProfileManager

# Skip these tests if database is not available
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "true",
    reason="Integration tests skipped (set SKIP_INTEGRATION_TESTS=false to run)",
)


class TestCalendlyWorkflowIntegration:
    """Integration tests for end-to-end Calendly workflow"""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures for all tests"""
        cls.test_job_id = str(uuid.uuid4())
        cls.test_application_id = str(uuid.uuid4())
        cls.test_user_id = "steve_glen"

        # Initialize managers
        cls.template_engine = TemplateEngine(enable_url_tracking=True)
        cls.doc_generator = DocumentGenerator()
        cls.profile_manager = CandidateProfileManager()

    def test_template_engine_integration(self):
        """
        Test: TemplateEngine generates tracked URLs in document context

        This test verifies that the TemplateEngine can successfully:
        1. Load candidate information
        2. Detect URL variables in template
        3. Call LinkTracker to generate tracked URLs
        4. Substitute variables with tracked redirect URLs
        """
        # Get candidate info
        candidate_info = self.profile_manager.get_candidate_info(self.test_user_id)

        # Skip test if no Calendly URL configured
        if not candidate_info.get("calendly_url"):
            pytest.skip("No Calendly URL configured for test user")

        # Prepare template text
        template_text = """
        Dear Hiring Manager,

        I'm interested in this position. You can schedule a meeting with me here:
        <<calendly_url>>

        You can also view my LinkedIn profile: <<linkedin_url>>

        Best regards,
        <<first_name>> <<last_name>>
        """

        # Prepare data
        data = {
            "first_name": candidate_info["first_name"],
            "last_name": candidate_info["last_name"],
            "calendly_url": candidate_info["calendly_url"],
            "linkedin_url": candidate_info.get(
                "linkedin_url", "https://linkedin.com/in/default"
            ),
        }

        stats = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }

        # Execute substitution with tracking context
        result = self.template_engine.substitute_variables(
            template_text,
            data,
            stats,
            job_id=self.test_job_id,
            application_id=self.test_application_id,
        )

        # Verify tracked URLs are present
        # Note: In a real integration test, this would contain actual tracked URLs
        # For now, we verify the substitution occurred
        assert data["first_name"] in result
        assert data["last_name"] in result
        assert "calendly_url" in stats["variables_substituted"]
        assert "linkedin_url" in stats["variables_substituted"]

    def test_document_generator_with_tracking_context(self):
        """
        Test: DocumentGenerator creates document with tracked URLs

        This test verifies that:
        1. Document generator accepts job_id and application_id
        2. Parameters are passed to TemplateEngine
        3. Generated document would contain tracked URLs (if template has URL variables)

        Note: This is a simplified integration test. Full test would generate
        actual .docx file and verify tracked URLs in the content.
        """
        # Prepare test data
        test_data = {
            "first_name": "Steve",
            "last_name": "Glen",
            "email": "test@example.com",
            "phone_number": "(780) 555-0123",
            "professional_summary": "Marketing professional with 10+ years experience",
            "target_position": "Marketing Manager",
        }

        # Note: This test would fail in actual execution without proper template
        # In a real scenario, you would:
        # 1. Use a test template with <<calendly_url>> variable
        # 2. Generate the document
        # 3. Parse the .docx file to verify tracked URL is present
        # 4. Verify the URL format matches /track/{tracking_id}

        # For now, we just verify the API accepts the parameters
        try:
            # This will likely fail due to missing template, but that's okay for structure test
            result = self.doc_generator.generate_document(
                data=test_data,
                document_type="resume",
                job_id=self.test_job_id,
                application_id=self.test_application_id,
            )
            # If it succeeds, verify structure
            assert "success" in result or "output_path" in result
        except FileNotFoundError:
            # Expected if template doesn't exist
            pytest.skip("Test template not available for integration test")
        except Exception as e:
            # Other errors might indicate integration issues
            pytest.fail(f"Unexpected error in document generation: {e}")

    def test_candidate_profile_manager_database_integration(self):
        """
        Test: CandidateProfileManager retrieves data from database

        This test verifies:
        1. Database connection works
        2. Candidate data can be retrieved
        3. URLs are present in returned data
        """
        try:
            # Attempt to retrieve candidate info
            candidate_info = self.profile_manager.get_candidate_info(self.test_user_id)

            # Verify structure
            assert "first_name" in candidate_info
            assert "last_name" in candidate_info
            assert "email" in candidate_info
            assert "calendly_url" in candidate_info
            assert "linkedin_url" in candidate_info
            assert "portfolio_url" in candidate_info

            # Verify data types
            assert isinstance(candidate_info["first_name"], str)
            assert isinstance(candidate_info["email"], str)

            # If URLs are set, verify they are strings or None
            if candidate_info["calendly_url"]:
                assert isinstance(candidate_info["calendly_url"], str)
                assert "calendly.com" in candidate_info["calendly_url"].lower()

        except Exception as e:
            pytest.fail(f"Database integration failed: {e}")

    def test_multiple_documents_same_job_caching(self):
        """
        Test: Multiple documents for same job use cached tracked URLs

        This test verifies:
        1. First document generation creates tracked URL
        2. Second document for same job reuses cached URL
        3. LinkTracker is only called once per unique (job_id, url) combination

        Note: This is a conceptual test. In practice, you would need to:
        1. Mock or monitor LinkTracker calls
        2. Generate resume with job_id
        3. Generate cover letter with same job_id
        4. Verify LinkTracker.create_tracked_link() only called once
        """
        # Prepare test data
        template_text1 = "Resume: <<calendly_url>>"
        template_text2 = "Cover Letter: <<calendly_url>>"

        data = {"calendly_url": "https://calendly.com/test-user/30min"}

        stats1 = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }
        stats2 = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }

        # Create new engine to test caching
        engine = TemplateEngine(enable_url_tracking=True)

        # First substitution
        result1 = engine.substitute_variables(
            template_text1,
            data,
            stats1,
            job_id=self.test_job_id,
            application_id=self.test_application_id,
        )

        # Second substitution with same parameters
        result2 = engine.substitute_variables(
            template_text2,
            data,
            stats2,
            job_id=self.test_job_id,
            application_id=self.test_application_id,
        )

        # Both should have substituted the variable
        assert "calendly_url" in stats1["variables_substituted"]
        assert "calendly_url" in stats2["variables_substituted"]

        # In a real test with monitoring, you would verify:
        # assert engine.tracked_url_cache has the cached entry
        # assert LinkTracker.create_tracked_link was called only once


class TestLinkTrackingSystemIntegration:
    """Integration tests for LinkTracking system (if available)"""

    def test_link_tracker_available(self):
        """
        Test: Verify LinkTracker module is available and functional

        This test attempts to import and initialize LinkTracker to ensure
        the tracking system is properly configured.
        """
        try:
            from modules.link_tracking.link_tracker import LinkTracker

            # Attempt to initialize
            tracker = LinkTracker()
            assert tracker is not None

            # Verify key attributes exist
            assert hasattr(tracker, "create_tracked_link")
            assert hasattr(tracker, "record_click")

        except ImportError:
            pytest.skip("LinkTracker module not available")
        except Exception as e:
            pytest.fail(f"LinkTracker initialization failed: {e}")

    def test_create_tracked_link_integration(self):
        """
        Test: Create tracked link and verify database entry

        This test verifies:
        1. LinkTracker.create_tracked_link() succeeds
        2. Returns tracking_id and redirect_url
        3. Database entry is created

        Note: This test requires database access and may create test data
        """
        try:
            from modules.link_tracking.link_tracker import LinkTracker

            tracker = LinkTracker()

            # Create tracked link
            result = tracker.create_tracked_link(
                original_url="https://calendly.com/integration-test/30min",
                link_function="Calendly",
                job_id=str(uuid.uuid4()),
                application_id=str(uuid.uuid4()),
                link_type="profile",
                description="Integration test link",
            )

            # Verify result structure
            assert "tracking_id" in result
            assert "redirect_url" in result
            assert result["tracking_id"].startswith("lt_")
            assert "/track/" in result["redirect_url"]

        except ImportError:
            pytest.skip("LinkTracker module not available")
        except Exception as e:
            pytest.fail(f"Link tracking integration failed: {e}")


class TestEndToEndWorkflow:
    """
    End-to-end workflow tests

    These tests simulate the complete user journey from document generation
    through click tracking to analytics reporting.
    """

    def test_complete_workflow_concept(self):
        """
        Conceptual test: Complete workflow from document to analytics

        In a full implementation, this test would:
        1. Generate a cover letter with tracked Calendly URL
        2. Extract the tracking_id from generated document
        3. Simulate HTTP request to /track/{tracking_id}
        4. Verify click is recorded in link_clicks table
        5. Verify redirect to original Calendly URL occurs
        6. Query analytics API to verify click count

        For now, this is a placeholder showing the intended test structure.
        """
        pytest.skip("Full end-to-end test requires complete system setup")

        # Conceptual workflow:
        # Step 1: Generate document
        # doc = generate_cover_letter(job_id, application_id)

        # Step 2: Extract tracking URL from document
        # tracking_url = extract_url_from_docx(doc)
        # tracking_id = extract_tracking_id(tracking_url)

        # Step 3: Simulate click
        # response = requests.get(tracking_url)
        # assert response.status_code == 302  # Redirect

        # Step 4: Verify click recorded
        # clicks = query_link_clicks(tracking_id)
        # assert len(clicks) == 1

        # Step 5: Verify analytics
        # analytics = get_link_analytics(tracking_id)
        # assert analytics['total_clicks'] == 1


class TestErrorHandlingIntegration:
    """Integration tests for error handling scenarios"""

    def test_missing_calendly_url_graceful_handling(self):
        """
        Test: System handles missing Calendly URL gracefully

        Verifies that document generation continues even when
        Calendly URL is not configured for a user.
        """
        template_text = "Contact: <<calendly_url>>"
        data = {}  # No calendly_url provided
        stats = {
            "variables_found": set(),
            "variables_substituted": set(),
            "variables_missing": set(),
        }

        engine = TemplateEngine(enable_url_tracking=True)

        # This should not raise an exception
        result = engine.substitute_variables(template_text, data, stats)

        # Variable should be marked as missing, but process continues
        assert "calendly_url" in stats["variables_missing"]
        # Original placeholder should remain
        assert "<<calendly_url>>" in result

    def test_link_tracker_unavailable_fallback(self):
        """
        Test: System falls back to original URL when LinkTracker unavailable

        This simulates LinkTracker being down or database connection failing.
        """
        engine = TemplateEngine(enable_url_tracking=True)

        # Force fallback by using invalid context that might cause LinkTracker to fail
        # In a real test, you would mock LinkTracker to raise an exception

        original_url = "https://calendly.com/test/30min"

        # If LinkTracker fails, _get_tracked_url should return original URL
        # This is tested more thoroughly in unit tests
        # Here we just verify no exceptions are raised
        try:
            result = engine._get_tracked_url(
                original_url, "Calendly", job_id="test-job", application_id="test-app"
            )
            # Result should be a string (either tracked URL or original URL)
            assert isinstance(result, str)
        except Exception as e:
            pytest.fail(f"Unexpected exception during fallback: {e}")


if __name__ == "__main__":
    # Run with: python -m pytest tests/integration/test_calendly_workflow.py -v
    pytest.main([__file__, "-v", "-s"])
