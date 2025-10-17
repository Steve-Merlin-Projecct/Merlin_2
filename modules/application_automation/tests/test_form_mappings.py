"""
Tests for Form Mappings

Validates form mapping JSON files for correctness and completeness.
"""

import pytest
import json
from pathlib import Path


class TestIndeedFormMappings:
    """Test suite for Indeed form mappings"""

    @pytest.fixture
    def mappings(self):
        """Load Indeed form mappings"""
        mappings_path = (
            Path(__file__).parent.parent / "form_mappings" / "indeed.json"
        )
        with open(mappings_path, "r") as f:
            return json.load(f)

    def test_mappings_structure(self, mappings):
        """Test basic mapping structure"""
        assert "platform" in mappings
        assert mappings["platform"] == "indeed"
        assert "version" in mappings
        assert "form_types" in mappings
        assert "detection_strategy" in mappings

    def test_form_types_present(self, mappings):
        """Test required form types are present"""
        form_types = mappings["form_types"]
        assert "standard_indeed_apply" in form_types
        assert "indeed_quick_apply" in form_types

    def test_standard_form_fields(self, mappings):
        """Test standard form has required fields"""
        standard_form = mappings["form_types"]["standard_indeed_apply"]
        fields = standard_form["fields"]

        required_fields = [
            "full_name",
            "email",
            "resume",
        ]

        for field in required_fields:
            assert field in fields, f"Missing required field: {field}"
            assert "selectors" in fields[field]
            assert len(fields[field]["selectors"]) > 0
            assert "type" in fields[field]

    def test_field_selectors_valid(self, mappings):
        """Test all field selectors are valid CSS selectors"""
        for form_type, form_config in mappings["form_types"].items():
            fields = form_config.get("fields", {})
            for field_name, field_config in fields.items():
                selectors = field_config.get("selectors", [])
                assert len(selectors) > 0, f"{form_type}.{field_name} has no selectors"

                for selector in selectors:
                    assert isinstance(selector, str)
                    assert len(selector) > 0

    def test_submit_button_defined(self, mappings):
        """Test submit button is defined for each form type"""
        for form_type, form_config in mappings["form_types"].items():
            assert "submit_button" in form_config
            assert "selectors" in form_config["submit_button"]
            assert len(form_config["submit_button"]["selectors"]) > 0

    def test_detection_strategy(self, mappings):
        """Test detection strategy is valid"""
        detection = mappings["detection_strategy"]
        assert "priority_order" in detection
        assert "detection_timeout_ms" in detection
        assert isinstance(detection["priority_order"], list)
        assert len(detection["priority_order"]) > 0
        assert isinstance(detection["detection_timeout_ms"], int)

    def test_confirmation_indicators(self, mappings):
        """Test confirmation indicators are defined"""
        standard_form = mappings["form_types"]["standard_indeed_apply"]
        assert "confirmation_indicators" in standard_form

        indicators = standard_form["confirmation_indicators"]
        assert "success_messages" in indicators
        assert "success_selectors" in indicators
        assert "url_patterns" in indicators

        assert len(indicators["success_messages"]) > 0
        assert len(indicators["success_selectors"]) > 0
        assert len(indicators["url_patterns"]) > 0

    def test_field_types_valid(self, mappings):
        """Test field types are valid"""
        valid_types = [
            "text",
            "email",
            "tel",
            "url",
            "file",
            "file_or_text",
            "text_or_select",
            "button",
        ]

        for form_type, form_config in mappings["form_types"].items():
            fields = form_config.get("fields", {})
            for field_name, field_config in fields.items():
                field_type = field_config.get("type")
                assert (
                    field_type in valid_types
                ), f"Invalid field type: {field_type} in {form_type}.{field_name}"

    def test_required_flag_present(self, mappings):
        """Test required flag is present for critical fields"""
        standard_form = mappings["form_types"]["standard_indeed_apply"]
        fields = standard_form["fields"]

        # Resume should be required
        assert fields["resume"].get("required") is True

        # Email and full_name should be required
        assert fields["full_name"].get("required") is True
        assert fields["email"].get("required") is True
