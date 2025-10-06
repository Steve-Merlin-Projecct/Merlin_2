#!/usr/bin/env python3
"""
Gmail integration enhancements for improved robustness
Based on production testing results and identified improvement areas
"""

import os
import re
import time
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


class EmailValidator:
    """Enhanced email validation and sanitization"""

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address format"""
        if not email or not isinstance(email, str):
            return False

        # RFC 5322 compliant email regex (simplified)
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        # Basic checks
        if len(email) > 254:  # RFC 5321 limit
            return False

        if ".." in email:  # Consecutive dots not allowed
            return False

        if email.startswith(".") or email.endswith("."):
            return False

        return re.match(pattern, email) is not None

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email address"""
        if not email:
            return ""

        # Remove whitespace and convert to lowercase
        email = email.strip().lower()

        # Remove any newlines or carriage returns (injection prevention)
        email = email.replace("\n", "").replace("\r", "")

        return email

    @staticmethod
    def validate_subject(subject: str) -> Dict[str, Any]:
        """Validate and sanitize email subject"""
        if subject is None:
            subject = "(No Subject)"

        subject = str(subject)

        # Remove newlines and carriage returns (injection prevention)
        subject = subject.replace("\n", " ").replace("\r", " ")

        # Trim excessive length (RFC 2822 recommends 78 chars per line)
        if len(subject) > 200:
            subject = subject[:197] + "..."

        return {"valid": True, "sanitized_subject": subject, "warnings": []}


class AttachmentValidator:
    """Enhanced attachment validation and handling"""

    # Gmail attachment size limit (25MB)
    MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024

    # Allowed MIME types (security consideration)
    ALLOWED_MIME_TYPES = {
        "text/plain",
        "text/csv",
        "text/html",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
        "application/x-zip-compressed",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "audio/mpeg",
        "audio/wav",
        "video/mp4",
    }

    @classmethod
    def validate_attachment(cls, file_path: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive attachment validation"""
        result = {
            "valid": False,
            "file_path": file_path,
            "filename": filename or os.path.basename(file_path),
            "size_bytes": 0,
            "mime_type": None,
            "warnings": [],
            "errors": [],
        }

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                result["errors"].append(f"File not found: {file_path}")
                return result

            # Check file size
            file_size = os.path.getsize(file_path)
            result["size_bytes"] = file_size

            if file_size == 0:
                result["errors"].append("File is empty")
                return result

            if file_size > cls.MAX_ATTACHMENT_SIZE:
                result["errors"].append(f"File too large: {file_size / (1024*1024):.1f}MB (limit: 25MB)")
                return result

            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(result["filename"])
            if mime_type is None:
                mime_type = "application/octet-stream"
                result["warnings"].append("Unknown file type, treating as binary")

            result["mime_type"] = mime_type

            # Check if MIME type is allowed
            if mime_type not in cls.ALLOWED_MIME_TYPES:
                result["warnings"].append(f"File type {mime_type} may be blocked by email filters")

            # File size warnings
            if file_size > 10 * 1024 * 1024:  # 10MB
                result["warnings"].append(f"Large file ({file_size / (1024*1024):.1f}MB) may take time to send")

            result["valid"] = True

        except Exception as e:
            result["errors"].append(f"Error validating attachment: {str(e)}")

        return result


class GmailConnectionHealthChecker:
    """Health checking and monitoring for Gmail connection"""

    def __init__(self, oauth_manager):
        self.oauth_manager = oauth_manager

    def check_connection_health(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_status = {
            "overall_healthy": False,
            "oauth_valid": False,
            "service_accessible": False,
            "internet_connected": False,
            "api_quota_ok": False,
            "issues": [],
            "recommendations": [],
        }

        try:
            # Check OAuth status
            oauth_status = self.oauth_manager.get_oauth_status()
            health_status["oauth_valid"] = oauth_status.get("authenticated", False)

            if not health_status["oauth_valid"]:
                health_status["issues"].append("OAuth authentication invalid")
                health_status["recommendations"].append("Re-run OAuth authorization flow")

            # Check internet connectivity
            try:
                import requests

                response = requests.get("https://www.google.com", timeout=10)
                health_status["internet_connected"] = response.status_code == 200
            except Exception:
                health_status["issues"].append("No internet connection")
                health_status["recommendations"].append("Check internet connectivity")

            # Check Gmail service accessibility
            if health_status["oauth_valid"]:
                try:
                    service = self.oauth_manager.get_gmail_service()
                    health_status["service_accessible"] = service is not None

                    # Test API quota with light operation
                    if service:
                        profile = service.users().getProfile(userId="me").execute()
                        health_status["api_quota_ok"] = "emailAddress" in profile

                except Exception as e:
                    health_status["issues"].append(f"Gmail service error: {str(e)}")
                    health_status["recommendations"].append("Check Gmail API credentials and quotas")

            # Determine overall health
            health_status["overall_healthy"] = (
                health_status["oauth_valid"]
                and health_status["service_accessible"]
                and health_status["internet_connected"]
                and health_status["api_quota_ok"]
            )

        except Exception as e:
            health_status["issues"].append(f"Health check error: {str(e)}")

        return health_status


class RetryManager:
    """Retry mechanism with exponential backoff"""

    @staticmethod
    def execute_with_retry(operation, max_retries=3, initial_delay=1, backoff_factor=2):
        """Execute operation with retry logic"""
        last_exception = None

        for attempt in range(max_retries):
            try:
                result = operation()

                # If operation returns a dict with status, check if it's successful
                if isinstance(result, dict) and "status" in result:
                    if result["status"] == "success":
                        return {"success": True, "result": result, "attempts": attempt + 1}
                    elif attempt == max_retries - 1:
                        # Last attempt failed
                        return {
                            "success": False,
                            "result": result,
                            "attempts": attempt + 1,
                            "final_error": result.get("message", "Operation failed"),
                        }
                else:
                    # Operation succeeded
                    return {"success": True, "result": result, "attempts": attempt + 1}

            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                # If not the last attempt, wait before retrying
                if attempt < max_retries - 1:
                    delay = initial_delay * (backoff_factor**attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

        # All attempts failed
        return {
            "success": False,
            "attempts": max_retries,
            "final_error": str(last_exception) if last_exception else "All retry attempts failed",
        }


class EnhancedGmailErrorHandler:
    """Enhanced error handling and logging for Gmail operations"""

    def __init__(self):
        self.setup_error_logging()

    def setup_error_logging(self):
        """Setup comprehensive error logging"""
        # Create logs directory if it doesn't exist
        os.makedirs("storage/logs", exist_ok=True)

        # Setup file handler for Gmail errors
        log_file = "storage/logs/gmail_errors.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.ERROR)

        # Create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s")
        file_handler.setFormatter(formatter)

        # Add handler to Gmail logger
        gmail_logger = logging.getLogger("modules.email_integration")
        gmail_logger.addHandler(file_handler)
        gmail_logger.setLevel(logging.INFO)

    @staticmethod
    def handle_gmail_api_error(error, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle Gmail API specific errors"""
        error_response = {
            "status": "error",
            "error_type": "unknown",
            "message": str(error),
            "user_message": "An error occurred while sending email",
            "retry_recommended": False,
            "context": context or {},
        }

        error_str = str(error).lower()

        # Categorize different types of errors
        if "quota" in error_str or "429" in error_str:
            error_response.update(
                {
                    "error_type": "quota_exceeded",
                    "user_message": "Email sending temporarily limited due to API quotas",
                    "retry_recommended": True,
                    "retry_delay": 300,  # 5 minutes
                }
            )

        elif "invalid to header" in error_str or "invalid email" in error_str:
            error_response.update(
                {
                    "error_type": "invalid_email",
                    "user_message": "Invalid email address provided",
                    "retry_recommended": False,
                }
            )

        elif "attachment too large" in error_str or "message too large" in error_str:
            error_response.update(
                {
                    "error_type": "attachment_too_large",
                    "user_message": "Attachment is too large (Gmail limit: 25MB)",
                    "retry_recommended": False,
                }
            )

        elif "network" in error_str or "connection" in error_str:
            error_response.update(
                {
                    "error_type": "network_error",
                    "user_message": "Network connection issue, please try again",
                    "retry_recommended": True,
                    "retry_delay": 30,
                }
            )

        elif "credentials" in error_str or "unauthorized" in error_str:
            error_response.update(
                {
                    "error_type": "auth_error",
                    "user_message": "Authentication error, please re-authorize Gmail access",
                    "retry_recommended": False,
                }
            )

        # Log the error with context
        logger.error(
            f"Gmail API Error: {error_response['error_type']} - {error_response['message']}", extra={"context": context}
        )

        return error_response


# Factory function to create enhanced Gmail sender
def create_enhanced_gmail_sender(oauth_manager):
    """Create Gmail sender with enhanced error handling and validation"""
    from modules.email_integration.gmail_oauth_official import OfficialGmailSender

    class EnhancedGmailSender(OfficialGmailSender):
        """Gmail sender with enhanced robustness features"""

        def __init__(self, oauth_manager):
            super().__init__(oauth_manager)
            self.validator = EmailValidator()
            self.attachment_validator = AttachmentValidator()
            self.health_checker = GmailConnectionHealthChecker(oauth_manager)
            self.error_handler = EnhancedGmailErrorHandler()
            self.retry_manager = RetryManager()

        def send_job_application_email_enhanced(
            self, to_email: str, subject: str, body: str, attachments: Optional[List[Dict]] = None
        ) -> Dict[str, Any]:
            """Enhanced email sending with comprehensive validation and error handling"""

            # Pre-flight validation
            validation_result = self._validate_email_inputs(to_email, subject, body, attachments)
            if not validation_result["valid"]:
                return validation_result

            # Health check
            health = self.health_checker.check_connection_health()
            if not health["overall_healthy"]:
                return {
                    "status": "error",
                    "error_type": "health_check_failed",
                    "message": "Gmail service not healthy",
                    "health_issues": health["issues"],
                    "recommendations": health["recommendations"],
                }

            # Attempt to send with retry
            def send_operation():
                return super(EnhancedGmailSender, self).send_job_application_email(
                    validation_result["sanitized_email"],
                    validation_result["sanitized_subject"],
                    body,
                    validation_result["validated_attachments"],
                )

            retry_result = self.retry_manager.execute_with_retry(send_operation)

            if retry_result["success"]:
                return retry_result["result"]
            else:
                return self.error_handler.handle_gmail_api_error(
                    retry_result["final_error"],
                    context={"to_email": to_email, "subject": subject[:50], "attempts": retry_result["attempts"]},
                )

        def _validate_email_inputs(
            self, to_email: str, subject: str, body: str, attachments: Optional[List[Dict]] = None
        ) -> Dict[str, Any]:
            """Validate all email inputs"""
            result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "sanitized_email": to_email,
                "sanitized_subject": subject,
                "validated_attachments": attachments,
            }

            # Validate email
            sanitized_email = self.validator.sanitize_email(to_email)
            if not self.validator.is_valid_email(sanitized_email):
                result["valid"] = False
                result["errors"].append(f"Invalid email address: {to_email}")
                return {
                    "status": "error",
                    "error_type": "invalid_email",
                    "message": f"Invalid email address: {to_email}",
                    **result,
                }

            result["sanitized_email"] = sanitized_email

            # Validate subject
            subject_validation = self.validator.validate_subject(subject)
            result["sanitized_subject"] = subject_validation["sanitized_subject"]
            result["warnings"].extend(subject_validation.get("warnings", []))

            # Validate attachments
            if attachments:
                validated_attachments = []
                for attachment in attachments:
                    file_path = attachment.get("path")
                    filename = attachment.get("filename")

                    if file_path:
                        validation = self.attachment_validator.validate_attachment(file_path, filename)

                        if not validation["valid"]:
                            result["valid"] = False
                            result["errors"].extend(validation["errors"])
                            return {
                                "status": "error",
                                "error_type": "invalid_attachment",
                                "message": f"Attachment validation failed: {'; '.join(validation['errors'])}",
                                **result,
                            }

                        result["warnings"].extend(validation.get("warnings", []))
                        validated_attachments.append(attachment)

                result["validated_attachments"] = validated_attachments

            return result

    return EnhancedGmailSender(oauth_manager)


def get_enhanced_gmail_sender(oauth_manager=None):
    """Get enhanced Gmail sender with robustness features"""
    if oauth_manager is None:
        from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager

        oauth_manager = get_gmail_oauth_manager()

    return create_enhanced_gmail_sender(oauth_manager)
