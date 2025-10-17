#!/usr/bin/env python3
"""Unit tests for response sanitization layer"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.ai_job_description_analysis.response_sanitizer import (
    ResponseSanitizer,
    get_sanitizer,
    sanitize_response,
)


@pytest.fixture
def sanitizer():
    """Get sanitizer instance"""
    return get_sanitizer()


def test_sql_injection_detection(sanitizer):
    """Test SQL injection pattern detection and removal"""
    result = {
        "job_id": "test_1",
        "skill_name": "Python'; DROP TABLE jobs; --",
        "company_name": "TechCorp UNION SELECT * FROM users",
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_1")

    # Check sanitization
    assert "[REMOVED]" in sanitized["skill_name"]
    assert "[REMOVED]" in sanitized["company_name"]

    # Check warnings
    assert len(warnings) >= 2
    assert any("SQL injection" in w for w in warnings)


def test_command_injection_detection(sanitizer):
    """Test command injection pattern detection and removal"""
    result = {
        "job_id": "test_2",
        "company_name": "TechCorp; rm -rf /",
        "location": "New York | cat /etc/passwd",
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_2")

    # Check sanitization (metacharacters stripped)
    assert ";" not in sanitized["company_name"]
    assert "|" not in sanitized["location"]

    # Check warnings
    assert len(warnings) >= 2
    assert any("Command injection" in w for w in warnings)


def test_xss_detection(sanitizer):
    """Test XSS pattern detection and HTML escaping"""
    result = {
        "job_id": "test_3",
        "job_description": "Great job! <script>alert('xss')</script>",
        "requirements": "Experience with <iframe src='evil.com'>",
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_3")

    # Check HTML escaping
    assert "&lt;script&gt;" in sanitized["job_description"]
    assert "&lt;iframe" in sanitized["requirements"]

    # Check warnings
    assert len(warnings) >= 2
    assert any("XSS" in w for w in warnings)


def test_path_traversal_detection(sanitizer):
    """Test path traversal pattern detection and removal"""
    result = {
        "job_id": "test_4",
        "company_location": "../../etc/passwd",
        "file_path": "..\\..\\windows\\system32",
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_4")

    # Check sanitization (../ stripped)
    assert "../" not in sanitized["company_location"]
    assert "..\\" not in sanitized["file_path"]

    # Check warnings
    assert len(warnings) >= 2
    assert any("Path traversal" in w for w in warnings)


def test_unauthorized_url_detection(sanitizer):
    """Test unauthorized URL detection in prohibited fields"""
    result = {
        "job_id": "test_5",
        "skill_name": "Python https://attacker.com/exfil",
        "industry": "Tech http://evil.com",
        "job_title": "Developer https://malware.com",
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_5")

    # Check URL removal
    assert "[URL_REMOVED]" in sanitized["skill_name"]
    assert "[URL_REMOVED]" in sanitized["industry"]
    assert "[URL_REMOVED]" in sanitized["job_title"]

    # Check warnings
    assert len(warnings) >= 3
    assert any("Unauthorized URL" in w for w in warnings)


def test_suspicious_url_detection(sanitizer):
    """Test suspicious URL detection in allowed fields"""
    result = {
        "job_id": "test_6",
        "application_link": "https://192.168.1.1/jobs",
        "company_website": "http://attacker.ngrok.io",
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_6")

    # Check suspicious URL removal
    assert "[SUSPICIOUS_URL_REMOVED]" in sanitized["application_link"]
    assert "[SUSPICIOUS_URL_REMOVED]" in sanitized["company_website"]

    # Check warnings
    assert len(warnings) >= 2
    assert any("Suspicious URL" in w for w in warnings)


def test_legitimate_url_allowed(sanitizer):
    """Test that legitimate URLs in allowed fields are preserved"""
    result = {
        "job_id": "test_7",
        "application_link": "https://careers.google.com/jobs/123",
        "company_website": "https://techcorp.com",
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_7")

    # Check URLs preserved
    assert "careers.google.com" in sanitized["application_link"]
    assert "techcorp.com" in sanitized["company_website"]

    # Should have no warnings for legitimate URLs
    assert len(warnings) == 0


def test_null_byte_injection(sanitizer):
    """Test null byte detection and removal"""
    result = {
        "job_id": "test_8",
        "skill_name": "Python\x00JavaScript",
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_8")

    # Check null byte removed
    assert "\x00" not in sanitized["skill_name"]
    assert "PythonJavaScript" in sanitized["skill_name"]

    # Check warning
    assert len(warnings) >= 1
    assert any("Null byte" in w for w in warnings)


def test_length_limit(sanitizer):
    """Test string length limit enforcement"""
    result = {
        "job_id": "test_9",
        "job_description": "A" * 15000,  # Exceeds 10,000 limit
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_9")

    # Check truncation
    assert len(sanitized["job_description"]) == 10000

    # Check warning
    assert len(warnings) >= 1
    assert any("truncated" in w for w in warnings)


def test_nested_object_sanitization(sanitizer):
    """Test recursive sanitization of nested objects"""
    result = {
        "job_id": "test_10",
        "structured_data": {
            "skill_requirements": {
                "skills": [
                    {"skill_name": "Python'; DROP TABLE jobs; --"},
                    {"skill_name": "JavaScript<script>alert('xss')</script>"},
                ]
            }
        },
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_10")

    # Check nested sanitization
    skills = sanitized["structured_data"]["skill_requirements"]["skills"]
    assert "[REMOVED]" in skills[0]["skill_name"]
    assert "&lt;script&gt;" in skills[1]["skill_name"]

    # Check warnings for nested fields
    assert len(warnings) >= 2


def test_clean_data_no_warnings(sanitizer):
    """Test that clean data passes through without warnings"""
    result = {
        "job_id": "test_11",
        "job_title": "Senior Python Developer",
        "company_name": "TechCorp Inc.",
        "skills": ["Python", "JavaScript", "SQL"],
        "salary": 120000,
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_11")

    # Check no modifications
    assert sanitized["job_title"] == result["job_title"]
    assert sanitized["company_name"] == result["company_name"]
    assert sanitized["skills"] == result["skills"]

    # Should have no warnings
    assert len(warnings) == 0


def test_convenience_function():
    """Test convenience function works correctly"""
    result = {
        "job_id": "test_12",
        "skill_name": "Python'; DROP TABLE jobs;",
    }

    sanitized, warnings = sanitize_response(result, "test_12")

    # Check sanitization works
    assert "[REMOVED]" in sanitized["skill_name"]
    assert len(warnings) > 0


def test_sanitization_report(sanitizer):
    """Test sanitization report generation"""
    warnings = [
        "field1: SQL injection pattern detected",
        "field2: SQL injection pattern detected",
        "field3: Command injection pattern detected",
        "field4: XSS pattern detected",
        "field5: Suspicious URL detected",
    ]

    report = sanitizer.get_sanitization_report(warnings)

    # Check report structure
    assert report["total_warnings"] == 5
    assert report["sql_injection_attempts"] == 2
    assert report["command_injection_attempts"] == 1
    assert report["xss_attempts"] == 1
    assert report["suspicious_urls"] == 1


def test_multiple_attacks_in_single_field(sanitizer):
    """Test detection of multiple attack types in single field"""
    result = {
        "job_id": "test_13",
        "description": "Job'; DROP TABLE users; -- <script>alert('xss')</script> ../../etc/passwd",
    }

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test_13")

    # Should detect multiple attack types
    assert len(warnings) >= 3  # SQL, XSS, path traversal
    assert any("SQL injection" in w for w in warnings)
    assert any("XSS" in w for w in warnings)
    assert any("Path traversal" in w for w in warnings)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
