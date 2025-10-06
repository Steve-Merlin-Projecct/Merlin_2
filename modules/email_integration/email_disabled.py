#!/usr/bin/env python3
"""
Email Sending Disabled Module

This module provides mock email functionality to disable actual email sending
while maintaining the same API interface for testing and development.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class DisabledEmailSender:
    """Mock email sender that prevents actual email transmission"""

    def __init__(self):
        """Initialize disabled email sender"""
        self.enabled = False
        logger.warning("EMAIL SENDING DISABLED - All emails will be mocked")

    def send_job_application_email(
        self, to_email: str, subject: str, body: str, attachments: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Mock job application email sending"""
        logger.info(f"MOCK EMAIL: Would send to {to_email} with subject: {subject[:50]}...")

        return {
            "status": "success",
            "message": "Email sending disabled - mock response",
            "message_id": f'mock_message_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "to_email": to_email,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "attachments_count": len(attachments) if attachments else 0,
            "mock_mode": True,
        }

    def send_job_application_email_enhanced(
        self, to_email: str, subject: str, body: str, attachments: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Mock enhanced job application email sending"""
        logger.info(f"MOCK ENHANCED EMAIL: Would send to {to_email} with subject: {subject[:50]}...")

        return {
            "status": "success",
            "message": "Enhanced email sending disabled - mock response",
            "gmail_message_id": f'mock_enhanced_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "to_email": to_email,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "attachments_count": len(attachments) if attachments else 0,
            "mock_mode": True,
            "enhanced": True,
        }

    def send_email_with_attachments(
        self, recipient: str, subject: str, body: str, attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mock email with attachments sending"""
        logger.info(f"MOCK EMAIL WITH ATTACHMENTS: Would send to {recipient} with subject: {subject[:50]}...")

        return {
            "success": True,
            "message": "Email with attachments sending disabled - mock response",
            "message_id": f'mock_attachment_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "recipient": recipient,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "attachments": attachments or [],
            "mock_mode": True,
        }

    def send_test_email(self, to_email: str = None) -> Dict[str, Any]:
        """Mock test email sending"""
        to_email = to_email or "test@example.com"
        logger.info(f"MOCK TEST EMAIL: Would send test email to {to_email}")

        return {
            "status": "success",
            "message": "Test email sending disabled - mock response",
            "message_id": f'mock_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "to_email": to_email,
            "sent_at": datetime.now().isoformat(),
            "mock_mode": True,
            "test_email": True,
        }


def get_disabled_email_sender():
    """Get disabled email sender instance"""
    return DisabledEmailSender()


# Global flag to control email sending
EMAIL_SENDING_DISABLED = True


def disable_email_sending():
    """Globally disable email sending"""
    global EMAIL_SENDING_DISABLED
    EMAIL_SENDING_DISABLED = True
    logger.warning("Email sending has been globally disabled")


def enable_email_sending():
    """Globally enable email sending"""
    global EMAIL_SENDING_DISABLED
    EMAIL_SENDING_DISABLED = False
    logger.info("Email sending has been globally enabled")


def is_email_sending_disabled():
    """Check if email sending is disabled"""
    return EMAIL_SENDING_DISABLED
