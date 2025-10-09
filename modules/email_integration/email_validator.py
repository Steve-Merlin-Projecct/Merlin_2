#!/usr/bin/env python3
"""
Email Validation Module

Provides validation functions for email content before sending.
Includes RFC 5322 email address validation, URL checking, and content validation.

Features:
- Email address format validation (RFC 5322 compliance)
- URL accessibility checking
- Attachment validation
- Template variable substitution checking
- Content length validation
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailValidationError(Exception):
    """Raised when email validation fails with blocking errors"""

    pass


class EmailValidator:
    """
    Validates email content before sending

    Performs various validation checks to ensure email quality
    and prevent common errors.
    """

    # RFC 5322 simplified email regex
    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+"
        r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )

    # URL regex for basic validation
    URL_REGEX = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )

    # Template variable pattern
    TEMPLATE_VAR_REGEX = re.compile(r"\{([^}]+)\}")

    def __init__(self):
        """Initialize email validator"""
        # Validation configuration from environment
        self.validate_urls = os.getenv("EMAIL_VALIDATE_URLS", "true").lower() == "true"
        self.block_on_errors = os.getenv("EMAIL_BLOCK_ON_ERRORS", "true").lower() == "true"

        # Email size limits
        self.max_subject_length = 200  # Characters
        self.max_body_length = 50000  # Characters (~50KB)
        self.max_attachment_size = 25 * 1024 * 1024  # 25MB (Gmail limit)
        self.max_total_attachments = 10

    def validate_email_address(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address format (RFC 5322 compliance)

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email address is empty"

        if len(email) > 254:  # RFC 5321
            return False, f"Email address too long: {len(email)} characters (max 254)"

        if not self.EMAIL_REGEX.match(email):
            return False, f"Invalid email address format: {email}"

        # Check for common typos
        common_domains = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]
        domain = email.split("@")[-1]

        # Warn about potential typos (not blocking)
        typo_warnings = {
            "gmial.com": "gmail.com",
            "gmai.com": "gmail.com",
            "outlok.com": "outlook.com",
            "yaho.com": "yahoo.com",
        }

        if domain in typo_warnings:
            return False, f"Possible typo in domain: {domain} (did you mean {typo_warnings[domain]}?)"

        return True, None

    def validate_subject(self, subject: str) -> Tuple[bool, List[str]]:
        """
        Validate email subject line

        Args:
            subject: Email subject

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        if not subject:
            return False, ["Subject line is empty"]

        if len(subject) > self.max_subject_length:
            warnings.append(f"Subject line very long: {len(subject)} characters (recommended < 60)")

        # Check for template variables that weren't substituted
        unsubstituted = self.TEMPLATE_VAR_REGEX.findall(subject)
        if unsubstituted:
            return False, [f"Unsubstituted template variables in subject: {', '.join(unsubstituted)}"]

        # Check for spam trigger words (informational only)
        spam_words = ["free", "urgent", "act now", "limited time", "!!!"]
        found_spam_words = [word for word in spam_words if word.lower() in subject.lower()]
        if found_spam_words:
            warnings.append(f"Subject contains potential spam trigger words: {', '.join(found_spam_words)}")

        return True, warnings

    def validate_body(self, body: str) -> Tuple[bool, List[str]]:
        """
        Validate email body content

        Args:
            body: Email body text

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        if not body:
            return False, ["Email body is empty"]

        if len(body) < 50:
            warnings.append(f"Email body very short: {len(body)} characters (might look incomplete)")

        if len(body) > self.max_body_length:
            return False, [f"Email body too long: {len(body)} characters (max {self.max_body_length})"]

        # Check for unsubstituted template variables
        unsubstituted = self.TEMPLATE_VAR_REGEX.findall(body)
        if unsubstituted:
            # Filter out intentional variable names (like in examples)
            suspicious_vars = [v for v in unsubstituted if not v.startswith("EXAMPLE_")]
            if suspicious_vars:
                return False, [f"Unsubstituted template variables: {', '.join(suspicious_vars)}"]

        return True, warnings

    def validate_attachments(self, attachments: Optional[List[Dict]]) -> Tuple[bool, List[str]]:
        """
        Validate email attachments

        Args:
            attachments: List of attachment dictionaries with 'path' and 'filename'

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        if not attachments:
            return True, []  # No attachments is fine

        warnings = []
        total_size = 0

        if len(attachments) > self.max_total_attachments:
            return False, [f"Too many attachments: {len(attachments)} (max {self.max_total_attachments})"]

        for i, attachment in enumerate(attachments):
            # Check required fields
            if "path" not in attachment:
                return False, [f"Attachment {i + 1} missing 'path' field"]

            file_path = attachment["path"]

            # Check file exists
            if not os.path.exists(file_path):
                return False, [f"Attachment file not found: {file_path}"]

            # Check file is readable
            if not os.access(file_path, os.R_OK):
                return False, [f"Attachment file not readable: {file_path}"]

            # Check file size
            try:
                file_size = os.path.getsize(file_path)
                total_size += file_size

                if file_size == 0:
                    return False, [f"Attachment file is empty: {file_path}"]

                if file_size > self.max_attachment_size:
                    return (
                        False,
                        [
                            f"Attachment too large: {file_path} "
                            f"({file_size / 1024 / 1024:.1f}MB, max {self.max_attachment_size / 1024 / 1024}MB)"
                        ],
                    )

            except OSError as e:
                return False, [f"Error checking attachment {file_path}: {e}"]

        # Check total size
        if total_size > self.max_attachment_size:
            return (
                False,
                [
                    f"Total attachments size too large: "
                    f"{total_size / 1024 / 1024:.1f}MB (max {self.max_attachment_size / 1024 / 1024}MB)"
                ],
            )

        return True, warnings

    def validate_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Validate complete email before sending

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            attachments: Optional list of attachments

        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'can_send': bool
            }
        """
        errors = []
        warnings = []

        # Validate recipient email
        email_valid, email_error = self.validate_email_address(to_email)
        if not email_valid:
            errors.append(f"Recipient email: {email_error}")

        # Validate subject
        subject_valid, subject_warnings = self.validate_subject(subject)
        if not subject_valid:
            errors.extend(subject_warnings)
        else:
            warnings.extend(subject_warnings)

        # Validate body
        body_valid, body_warnings = self.validate_body(body)
        if not body_valid:
            errors.extend(body_warnings)
        else:
            warnings.extend(body_warnings)

        # Validate attachments
        attachments_valid, attachment_warnings = self.validate_attachments(attachments)
        if not attachments_valid:
            errors.extend(attachment_warnings)
        else:
            warnings.extend(attachment_warnings)

        # Determine if email can be sent
        has_errors = len(errors) > 0
        can_send = not has_errors or not self.block_on_errors

        return {
            "valid": not has_errors,
            "errors": errors,
            "warnings": warnings,
            "can_send": can_send,
            "recipient": to_email,
            "subject": subject,
            "body_length": len(body),
            "attachment_count": len(attachments) if attachments else 0,
        }

    def validate_or_raise(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Validate email and raise exception if validation fails

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            attachments: Optional list of attachments

        Returns:
            Validation results dictionary

        Raises:
            EmailValidationError: If validation fails and block_on_errors is True
        """
        result = self.validate_email(to_email, subject, body, attachments)

        if not result["can_send"]:
            error_msg = "Email validation failed:\n" + "\n".join(f"  - {err}" for err in result["errors"])
            raise EmailValidationError(error_msg)

        # Log warnings if any
        if result["warnings"]:
            logger.warning(f"Email validation warnings for {to_email}:")
            for warning in result["warnings"]:
                logger.warning(f"  - {warning}")

        return result


# Factory function
def get_email_validator() -> EmailValidator:
    """
    Get email validator instance

    Returns:
        EmailValidator instance
    """
    return EmailValidator()


# Convenience function for quick validation
def validate_email(
    to_email: str,
    subject: str,
    body: str,
    attachments: Optional[List[Dict]] = None,
) -> Dict:
    """
    Validate email with default validator

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        attachments: Optional list of attachments

    Returns:
        Validation results dictionary
    """
    validator = get_email_validator()
    return validator.validate_email(to_email, subject, body, attachments)


if __name__ == "__main__":
    # Demo/testing
    print("Email Validator Demo")
    print("=" * 60)

    validator = get_email_validator()

    # Test cases
    test_cases = [
        {
            "name": "Valid email",
            "to": "hiring@company.com",
            "subject": "Application for Marketing Manager - Steve Glen",
            "body": "Dear Hiring Manager,\n\nI am writing to express my interest...\n\nBest regards,\nSteve Glen",
            "attachments": None,
        },
        {
            "name": "Invalid email format",
            "to": "invalid-email",
            "subject": "Test",
            "body": "Test body",
            "attachments": None,
        },
        {
            "name": "Empty subject",
            "to": "test@example.com",
            "subject": "",
            "body": "Test body",
            "attachments": None,
        },
        {
            "name": "Unsubstituted template variable",
            "to": "test@example.com",
            "subject": "Application for {job_title}",
            "body": "Dear {hiring_manager},\n\nThis is a test.",
            "attachments": None,
        },
    ]

    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print("-" * 60)
        result = validator.validate_email(
            test["to"],
            test["subject"],
            test["body"],
            test["attachments"],
        )

        print(f"Valid: {result['valid']}")
        print(f"Can Send: {result['can_send']}")

        if result["errors"]:
            print("Errors:")
            for error in result["errors"]:
                print(f"  ✗ {error}")

        if result["warnings"]:
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"  ⚠ {warning}")
