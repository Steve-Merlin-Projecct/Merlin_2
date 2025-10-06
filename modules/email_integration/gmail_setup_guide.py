"""
Gmail OAuth Setup Guide for Automated Job Application System
Provides step-by-step instructions for configuring Gmail OAuth integration
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class GmailSetupGuide:
    """
    Comprehensive setup guide for Gmail OAuth integration
    Provides step-by-step instructions and validation
    """

    def get_setup_steps(self) -> Dict:
        """
        Get complete Gmail OAuth setup instructions

        Returns:
            Dictionary with step-by-step setup guide
        """

        return {
            "title": "Gmail OAuth 2.0 Setup for Job Application Automation",
            "overview": "This guide will help you configure Gmail OAuth to automatically send job applications via your Gmail account.",
            "requirements": [
                "Google account with Gmail enabled",
                "Google Cloud Console access",
                "Administrator access to this application",
            ],
            "estimated_time": "10-15 minutes",
            "steps": [
                {
                    "step": 1,
                    "title": "Create Google Cloud Project",
                    "description": "Set up a new project in Google Cloud Console",
                    "instructions": [
                        "Go to https://console.cloud.google.com/",
                        'Click "Select a project" → "New Project"',
                        'Enter project name: "Job Application Automation"',
                        'Click "Create"',
                        "Wait for project creation to complete",
                    ],
                    "verification": "Project appears in project selector dropdown",
                },
                {
                    "step": 2,
                    "title": "Enable Gmail API",
                    "description": "Activate Gmail API for your project",
                    "instructions": [
                        'In Google Cloud Console, go to "APIs & Services" → "Library"',
                        'Search for "Gmail API"',
                        'Click on "Gmail API" result',
                        'Click "Enable" button',
                        "Wait for API to be enabled",
                    ],
                    "verification": 'Gmail API shows as "Enabled" in APIs dashboard',
                },
                {
                    "step": 3,
                    "title": "Configure OAuth Consent Screen",
                    "description": "Set up OAuth consent screen for authentication",
                    "instructions": [
                        'Go to "APIs & Services" → "OAuth consent screen"',
                        'Select "External" user type → Click "Create"',
                        "Fill in required fields:",
                        '  - App name: "Job Application Automation"',
                        "  - User support email: [your email]",
                        "  - Developer contact: [your email]",
                        'Click "Save and Continue"',
                        'Skip "Scopes" section → "Save and Continue"',
                        'Add your email as test user → "Save and Continue"',
                        'Review summary → "Back to Dashboard"',
                    ],
                    "verification": 'OAuth consent screen shows "Testing" status',
                },
                {
                    "step": 4,
                    "title": "Create OAuth Credentials",
                    "description": "Generate OAuth 2.0 client credentials",
                    "instructions": [
                        'Go to "APIs & Services" → "Credentials"',
                        'Click "Create Credentials" → "OAuth client ID"',
                        'Select "Web application"',
                        'Enter name: "Job Application System"',
                        "Add Authorized redirect URI:",
                        f"  {self._get_redirect_uri()}",
                        'Click "Create"',
                        "Copy Client ID and Client Secret from popup",
                    ],
                    "verification": "OAuth client appears in credentials list",
                    "important_note": "Save Client ID and Client Secret - you will need them in the next step",
                },
                {
                    "step": 5,
                    "title": "Configure Application",
                    "description": "Set up OAuth credentials in the job application system",
                    "instructions": [
                        "Use the API endpoint to configure credentials:",
                        "POST /api/email/oauth/setup",
                        "Include JSON body with your credentials:",
                        "{",
                        '  "client_id": "your-client-id-here",',
                        '  "client_secret": "your-client-secret-here"',
                        "}",
                        'Verify response shows "success": true',
                    ],
                    "verification": "API returns success status",
                    "api_endpoint": "/api/email/oauth/setup",
                },
                {
                    "step": 6,
                    "title": "Authorize Application",
                    "description": "Grant Gmail access permissions to the application",
                    "instructions": [
                        "Get authorization URL from: GET /api/email/oauth/authorize",
                        "Open the authorization URL in your browser",
                        "Sign in with your Google account",
                        'Click "Allow" to grant Gmail permissions',
                        "You will be redirected back to the application",
                        "Verify authentication is complete",
                    ],
                    "verification": "GET /api/email/oauth/status shows authenticated: true",
                },
                {
                    "step": 7,
                    "title": "Test Email Sending",
                    "description": "Verify Gmail integration with a test email",
                    "instructions": [
                        "Send test email using: POST /api/email/test",
                        'Include JSON body: {"test_email": "your-email@example.com"}',
                        "Check your inbox for test email",
                        "Verify email was sent successfully",
                    ],
                    "verification": "Test email received and API returns success",
                },
            ],
            "troubleshooting": [
                {
                    "issue": "OAuth consent screen not working",
                    "solution": "Ensure you added your email as a test user and app is in Testing mode",
                },
                {
                    "issue": "Redirect URI mismatch error",
                    "solution": f"Verify redirect URI in Google Cloud Console matches: {self._get_redirect_uri()}",
                },
                {"issue": "Token refresh failures", "solution": "Re-authorize the application by repeating step 6"},
                {
                    "issue": "API rate limits",
                    "solution": "Gmail API has generous limits for personal use - check quotas in Google Cloud Console",
                },
            ],
            "security_notes": [
                "Client credentials are stored securely in storage/gmail_credentials.json",
                "Access tokens are automatically refreshed when expired",
                "Only you can access the OAuth consent screen during testing phase",
                "Tokens are encrypted and stored locally - never shared externally",
            ],
            "next_steps": [
                "Configure job application templates",
                "Set up automated workflow scheduling",
                "Test complete job application sending workflow",
            ],
        }

    def _get_redirect_uri(self) -> str:
        """Get the configured OAuth redirect URI"""
        from modules.email_integration.gmail_oauth_official import GmailOAuthConfig

        return GmailOAuthConfig.REDIRECT_URI

    def get_api_endpoints(self) -> Dict:
        """
        Get list of available Gmail OAuth API endpoints

        Returns:
            Dictionary with endpoint information
        """

        return {
            "oauth_endpoints": [
                {
                    "endpoint": "GET /api/email/oauth/status",
                    "description": "Check OAuth authentication status",
                    "auth_required": True,
                    "example_response": {
                        "success": True,
                        "data": {"authenticated": True, "credentials_configured": True, "tokens_available": True},
                    },
                },
                {
                    "endpoint": "POST /api/email/oauth/setup",
                    "description": "Configure OAuth credentials",
                    "auth_required": True,
                    "request_body": {"client_id": "string", "client_secret": "string"},
                    "example_response": {
                        "success": True,
                        "data": {
                            "status": "success",
                            "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
                        },
                    },
                },
                {
                    "endpoint": "GET /api/email/oauth/authorize",
                    "description": "Get OAuth authorization URL",
                    "auth_required": True,
                    "example_response": {
                        "success": True,
                        "data": {
                            "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
                            "instructions": "Visit the authorization URL to grant permissions",
                        },
                    },
                },
                {
                    "endpoint": "GET /api/email/oauth/callback",
                    "description": "OAuth callback handler (called by Google)",
                    "auth_required": False,
                    "note": "This endpoint is called automatically by Google after authorization",
                },
            ],
            "email_endpoints": [
                {
                    "endpoint": "POST /api/email/test",
                    "description": "Send test email to verify Gmail integration",
                    "auth_required": True,
                    "request_body": {"test_email": "string"},
                    "example_response": {
                        "success": True,
                        "data": {"message": "Test email sent successfully", "gmail_message_id": "..."},
                    },
                },
                {
                    "endpoint": "POST /api/email/send-job-application",
                    "description": "Send job application with attachments",
                    "auth_required": True,
                    "request_body": {
                        "to_email": "string",
                        "company_name": "string",
                        "job_title": "string",
                        "applicant_name": "string",
                        "cover_letter_content": "string (optional)",
                        "resume_path": "string (optional)",
                        "cover_letter_path": "string (optional)",
                    },
                    "example_response": {
                        "success": True,
                        "data": {"message": "Job application sent successfully", "gmail_message_id": "..."},
                    },
                },
            ],
        }


def get_setup_guide() -> GmailSetupGuide:
    """Get Gmail setup guide instance"""
    return GmailSetupGuide()
