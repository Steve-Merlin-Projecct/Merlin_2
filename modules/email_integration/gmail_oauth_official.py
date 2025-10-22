"""
Module: gmail_oauth_official.py
Purpose: Official Gmail OAuth 2.0 integration for sending job application emails
Created: 2024-09-15
Modified: 2025-10-21
Dependencies: google-auth-oauthlib, google-api-python-client
Related: email_api.py, gmail_setup_guide.py, email_content_builder.py
Description: Implements OAuth 2.0 flow using official Google Workspace libraries.
             Handles authentication, token refresh, email sending with attachments,
             and RFC-compliant MIME message formatting. Follows Google's official
             documentation patterns from developers.google.com/workspace/gmail.
"""

import os
import json
import logging
import base64
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from email.message import EmailMessage

# Google OAuth and API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    GOOGLE_LIBRARIES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Google libraries not available: {e}")
    GOOGLE_LIBRARIES_AVAILABLE = False

logger = logging.getLogger(__name__)


class GmailOAuthConfig:
    """
    Configuration for Gmail OAuth integration
    Following Google's official documentation patterns
    """

    # Gmail API scopes for sending emails
    SCOPES = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.compose"]

    # Storage paths
    STORAGE_DIR = "storage"
    CREDENTIALS_FILE = "storage/gmail_credentials.json"
    TOKEN_FILE = "storage/gmail_token.json"

    # OAuth redirect URI for web applications - must match Google Cloud Console config
    REDIRECT_URI = "http://localhost"


class OfficialGmailOAuthManager:
    """
    Gmail OAuth manager using official Google libraries
    Implements patterns from developers.google.com/workspace/gmail/api/quickstart/python
    """

    def __init__(self):
        self.config = GmailOAuthConfig()
        self.credentials = None
        self.service = None

        # Ensure storage directory exists
        Path(self.config.STORAGE_DIR).mkdir(exist_ok=True)

        # Load existing credentials if available
        self._load_existing_credentials()

    def _load_existing_credentials(self) -> bool:
        """
        Load existing OAuth credentials from token file
        Following Google's official token handling pattern
        """

        if not GOOGLE_LIBRARIES_AVAILABLE:
            logger.error("Google libraries not available for OAuth")
            return False

        try:
            if os.path.exists(self.config.TOKEN_FILE):
                self.credentials = Credentials.from_authorized_user_file(self.config.TOKEN_FILE, self.config.SCOPES)

                # Check if credentials are valid
                if self.credentials and self.credentials.valid:
                    logger.info("Valid OAuth credentials loaded from token file")
                    return True

                # Try to refresh expired credentials
                elif self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        self.credentials.refresh(Request())
                        self._save_credentials()
                        logger.info("OAuth credentials refreshed successfully")
                        return True
                    except Exception as refresh_error:
                        logger.warning(f"Failed to refresh credentials: {refresh_error}")
                        return False

            return False

        except Exception as e:
            logger.error(f"Failed to load existing credentials: {e}")
            return False

    def _save_credentials(self) -> bool:
        """
        Save OAuth credentials to token file
        Following Google's official credential storage pattern
        """

        try:
            if self.credentials:
                with open(self.config.TOKEN_FILE, "w") as token_file:
                    token_file.write(self.credentials.to_json())
                logger.info("OAuth credentials saved to token file")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            return False

    def setup_oauth_credentials(self, client_id: str, client_secret: str) -> Dict:
        """
        Setup OAuth credentials using Google Cloud Console client ID and secret
        Creates the credentials.json file needed for OAuth flow
        """

        try:
            # Create credentials configuration following Google's format
            credentials_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost"],
                }
            }

            # Save credentials configuration
            with open(self.config.CREDENTIALS_FILE, "w") as f:
                json.dump(credentials_config, f, indent=2)

            logger.info("OAuth credentials configuration saved")

            return {
                "status": "success",
                "message": "OAuth credentials configured successfully",
                "next_step": "Run OAuth authorization flow",
            }

        except Exception as e:
            logger.error(f"Failed to setup OAuth credentials: {e}")
            return {"status": "error", "message": f"Failed to setup credentials: {str(e)}"}

    def get_authorization_url(self) -> Dict:
        """
        Get OAuth authorization URL using Google's official flow
        Following developers.google.com/workspace/gmail/api/quickstart patterns
        """

        if not GOOGLE_LIBRARIES_AVAILABLE:
            return {"status": "error", "message": "Google OAuth libraries not available"}

        try:
            if not os.path.exists(self.config.CREDENTIALS_FILE):
                return {"status": "error", "message": "OAuth credentials not configured. Run setup first."}

            # Create OAuth flow using Google's official library
            flow = InstalledAppFlow.from_client_secrets_file(self.config.CREDENTIALS_FILE, self.config.SCOPES)

            # Set the redirect URI for web applications
            flow.redirect_uri = self.config.REDIRECT_URI

            # For web applications, we'll use run_local_server with a specific port
            # This follows Google's recommended pattern for web apps
            authorization_url, _ = flow.authorization_url(access_type="offline", include_granted_scopes="true")

            # Store flow state for callback
            self._flow = flow

            return {
                "status": "success",
                "authorization_url": authorization_url,
                "message": "Visit the authorization URL to grant Gmail permissions",
            }

        except Exception as e:
            logger.error(f"Failed to get authorization URL: {e}")
            return {"status": "error", "message": f"Authorization URL generation failed: {str(e)}"}

    def complete_oauth_flow(self, authorization_code: str = None) -> Dict:
        """
        Complete OAuth flow using authorization code or local server
        Following Google's official OAuth completion pattern
        """

        if not GOOGLE_LIBRARIES_AVAILABLE:
            return {"status": "error", "message": "Google OAuth libraries not available"}

        try:
            if not hasattr(self, "_flow"):
                # Create new flow if needed
                if not os.path.exists(self.config.CREDENTIALS_FILE):
                    return {"status": "error", "message": "OAuth credentials not configured"}

                self._flow = InstalledAppFlow.from_client_secrets_file(self.config.CREDENTIALS_FILE, self.config.SCOPES)

            # Complete OAuth flow
            if authorization_code:
                # Manual authorization code flow - set redirect URI first
                self._flow.redirect_uri = self.config.REDIRECT_URI
                self._flow.fetch_token(code=authorization_code)
            else:
                # Run local server for automatic flow (development mode)
                self.credentials = self._flow.run_local_server(port=8080)

            self.credentials = self._flow.credentials

            # Save credentials for future use
            self._save_credentials()

            logger.info("OAuth flow completed successfully")

            return {"status": "success", "message": "OAuth authorization completed successfully", "authenticated": True}

        except Exception as e:
            logger.error(f"Failed to complete OAuth flow: {e}")
            return {"status": "error", "message": f"OAuth flow completion failed: {str(e)}"}

    def get_oauth_status(self) -> Dict:
        """
        Get current OAuth authentication status
        """

        status = {
            "authenticated": False,
            "credentials_configured": os.path.exists(self.config.CREDENTIALS_FILE),
            "tokens_available": os.path.exists(self.config.TOKEN_FILE),
            "google_libraries_available": GOOGLE_LIBRARIES_AVAILABLE,
            "needs_setup": False,
            "needs_authorization": False,
            "token_valid": False,
        }

        if not GOOGLE_LIBRARIES_AVAILABLE:
            status["needs_setup"] = True
            status["message"] = "Google OAuth libraries not installed"
            return status

        if not status["credentials_configured"]:
            status["needs_setup"] = True
            status["message"] = "OAuth credentials not configured"
            return status

        if not status["tokens_available"]:
            status["needs_authorization"] = True
            status["message"] = "OAuth authorization required"
            return status

        # Check token validity
        if self.credentials:
            status["token_valid"] = self.credentials.valid
            status["authenticated"] = self.credentials.valid

            if not self.credentials.valid:
                if self.credentials.expired and self.credentials.refresh_token:
                    status["message"] = "Token expired but can be refreshed"
                else:
                    status["needs_authorization"] = True
                    status["message"] = "Token invalid - re-authorization required"
            else:
                status["message"] = "OAuth authentication active"

        return status

    def is_authenticated(self) -> bool:
        """Check if currently authenticated with valid credentials"""
        return self.credentials is not None and self.credentials.valid

    def get_gmail_service(self):
        """
        Get authenticated Gmail API service
        Following Google's official service creation pattern
        """

        if not GOOGLE_LIBRARIES_AVAILABLE:
            raise Exception("Google API libraries not available")

        if not self.is_authenticated():
            raise Exception("Not authenticated - OAuth flow required")

        try:
            if not self.service:
                self.service = build("gmail", "v1", credentials=self.credentials)
                logger.info("Gmail API service created successfully")

            return self.service

        except Exception as e:
            logger.error(f"Failed to create Gmail service: {e}")
            raise Exception(f"Gmail service creation failed: {str(e)}")


class OfficialGmailSender:
    """
    Gmail email sending using official Google API client
    Implements patterns from developers.google.com/workspace/gmail/api/guides/sending
    """

    def __init__(self, oauth_manager: OfficialGmailOAuthManager):
        self.oauth_manager = oauth_manager

        # Load user configuration from environment
        self.user_email = os.getenv("USER_EMAIL_ADDRESS", "your.email@gmail.com")
        self.display_name = os.getenv("USER_DISPLAY_NAME", "Steve Glen")

    def send_job_application_email(
        self, to_email: str, subject: str, body: str, attachments: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Send job application email using Gmail API
        Following Google's official email sending patterns
        """

        try:
            # Get authenticated Gmail service
            service = self.oauth_manager.get_gmail_service()

            # Create email message using Google's recommended EmailMessage class
            message = EmailMessage()
            message.set_content(body)

            # Set headers with display name
            message["From"] = f'"{self.display_name}" <{self.user_email}>'
            message["To"] = to_email
            message["Reply-To"] = f'"{self.display_name}" <{self.user_email}>'
            message["Subject"] = subject

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    file_path = attachment.get("path")
                    filename = attachment.get("filename")

                    if file_path and filename and Path(file_path).exists():
                        try:
                            with open(file_path, "rb") as f:
                                file_data = f.read()

                            # Detect MIME type
                            import mimetypes

                            mime_type, _ = mimetypes.guess_type(filename)
                            if mime_type is None:
                                mime_type = "application/octet-stream"

                            main_type, sub_type = mime_type.split("/", 1)

                            message.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=filename)

                            logger.info(f"Added attachment: {filename}")

                        except Exception as attach_error:
                            logger.warning(f"Failed to attach {filename}: {attach_error}")

            # Encode message as required by Gmail API
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send using Gmail API
            send_message = {"raw": raw_message}
            result = service.users().messages().send(userId="me", body=send_message).execute()

            logger.info(f"Email sent successfully: {result.get('id')}")

            return {
                "status": "success",
                "message": "Email sent successfully",
                "gmail_message_id": result.get("id"),
                "thread_id": result.get("threadId"),
            }

        except HttpError as http_error:
            logger.error(f"Gmail API HTTP error: {http_error}")
            return {"status": "error", "message": f"Gmail API error: {http_error}", "error_type": "http_error"}

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"status": "error", "message": f"Email sending failed: {str(e)}", "error_type": "general_error"}

    def send_email_with_attachment(
        self, to_email: str, subject: str, body: str, attachment_path: str, attachment_name: str = None
    ) -> Dict:
        """
        Send an email with attachment using Gmail API

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            attachment_path: Path to the attachment file
            attachment_name: Name for the attachment (optional, uses filename if not provided)

        Returns:
            Dict with status, message, and gmail_message_id if successful
        """

        # Convert single attachment to list format for existing method
        if not attachment_name:
            attachment_name = os.path.basename(attachment_path)

        attachments = [{"path": attachment_path, "filename": attachment_name}]

        return self.send_job_application_email(to_email, subject, body, attachments)

    def send_test_email(self, test_email: str) -> Dict:
        """
        Send test email to verify Gmail integration
        """

        test_subject = "Job Application System - Gmail Integration Test"
        test_body = f"""
This is a test email from your Automated Job Application System.

Gmail OAuth integration is working correctly using Google's official libraries!

Features verified:
✓ OAuth 2.0 authentication with google-auth-oauthlib
✓ Gmail API service with google-api-python-client
✓ Professional email sending via Gmail API
✓ Official Google Workspace patterns
✓ Configurable user contact information

Email Configuration:
• Display Name: {self.display_name}
• Email Address: {self.user_email}
• From Header: "{self.display_name}" <{self.user_email}>

Your job application automation is ready to send personalized applications.

---
Automated Job Application System v4.2.0
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S MT")}
Using Official Google Workspace Libraries
        """

        return self.send_job_application_email(
            to_email=test_email, subject=test_subject, body=test_body, attachments=None
        )


# Factory functions for dependency injection
def get_official_gmail_oauth_manager() -> OfficialGmailOAuthManager:
    """Get official Gmail OAuth manager instance"""
    return OfficialGmailOAuthManager()


def get_official_gmail_sender(oauth_manager: Optional[OfficialGmailOAuthManager] = None) -> OfficialGmailSender:
    """Get official Gmail sender instance"""
    if oauth_manager is None:
        oauth_manager = get_official_gmail_oauth_manager()
    return OfficialGmailSender(oauth_manager)


# Compatibility aliases for existing code
def get_gmail_oauth_manager() -> OfficialGmailOAuthManager:
    """Compatibility alias for existing code"""
    return get_official_gmail_oauth_manager()


def get_gmail_sender(oauth_manager: Optional[OfficialGmailOAuthManager] = None) -> OfficialGmailSender:
    """Compatibility alias for existing code"""
    return get_official_gmail_sender(oauth_manager)
