"""
Gmail OAuth Integration for Automated Job Application System
Handles OAuth 2.0 authentication and email sending via Gmail API
"""

import logging
import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class GmailOAuthConfig:
    """Configuration for Gmail OAuth integration"""

    # OAuth 2.0 configuration
    SCOPES = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.compose"]

    # File paths for OAuth credentials
    CREDENTIALS_FILE = "storage/gmail_credentials.json"
    TOKEN_FILE = "storage/gmail_token.json"

    # OAuth endpoints
    OAUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

    # Application information
    REDIRECT_URI = "http://localhost:8080/gmail/oauth/callback"


class GmailOAuthManager:
    """
    Manages Gmail OAuth 2.0 authentication and token management

    This class handles:
    1. OAuth 2.0 authorization flow
    2. Token storage and refresh
    3. Gmail API authentication
    """

    def __init__(self):
        self.config = GmailOAuthConfig()
        self.credentials = None
        self.token = None

        # Ensure storage directory exists
        storage_dir = Path("storage")
        storage_dir.mkdir(exist_ok=True)

    def setup_oauth_credentials(self, client_id: str, client_secret: str) -> Dict:
        """
        Setup OAuth credentials from Google Cloud Console

        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret

        Returns:
            Setup status and next steps
        """

        credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": self.config.REDIRECT_URI,
            "scopes": self.config.SCOPES,
        }

        try:
            # Save credentials securely
            with open(self.config.CREDENTIALS_FILE, "w") as f:
                json.dump(credentials, f, indent=2)

            logger.info("Gmail OAuth credentials saved successfully")

            return {
                "status": "success",
                "message": "OAuth credentials configured",
                "next_step": "initiate_oauth_flow",
                "authorization_url": self._build_authorization_url(credentials),
            }

        except Exception as e:
            logger.error(f"Failed to setup OAuth credentials: {e}")
            return {"status": "error", "message": f"Failed to setup credentials: {str(e)}"}

    def _build_authorization_url(self, credentials: Dict) -> str:
        """Build OAuth authorization URL"""

        import urllib.parse

        params = {
            "client_id": credentials["client_id"],
            "redirect_uri": credentials["redirect_uri"],
            "scope": " ".join(credentials["scopes"]),
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
        }

        query_string = urllib.parse.urlencode(params)
        return f"{self.config.OAUTH_ENDPOINT}?{query_string}"

    def exchange_code_for_tokens(self, authorization_code: str) -> Dict:
        """
        Exchange authorization code for access and refresh tokens

        Args:
            authorization_code: Code received from OAuth callback

        Returns:
            Token exchange result
        """

        try:
            # Load credentials
            with open(self.config.CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)

            # Ensure requests is available
            if not self._ensure_requests_loaded():
                return {"status": "error", "message": "requests module not available"}

            import requests

            # Exchange code for tokens
            token_data = {
                "client_id": credentials["client_id"],
                "client_secret": credentials["client_secret"],
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": credentials["redirect_uri"],
            }

            response = requests.post(self.config.TOKEN_ENDPOINT, data=token_data)

            if response.status_code == 200:
                tokens = response.json()

                # Save tokens securely
                with open(self.config.TOKEN_FILE, "w") as f:
                    json.dump(tokens, f, indent=2)

                logger.info("Gmail OAuth tokens obtained successfully")

                return {"status": "success", "message": "OAuth authentication completed", "tokens": tokens}
            else:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return {"status": "error", "message": f"Token exchange failed: {response.status_code}"}

        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            return {"status": "error", "message": f"Token exchange failed: {str(e)}"}

    def _ensure_requests_loaded(self) -> bool:
        """Ensure requests module is available"""
        try:
            import requests

            return True
        except ImportError:
            return False

    def refresh_access_token(self) -> Dict:
        """
        Refresh expired access token using refresh token

        Returns:
            Token refresh result
        """

        try:
            # Load current tokens
            with open(self.config.TOKEN_FILE, "r") as f:
                tokens = json.load(f)

            # Load credentials
            with open(self.config.CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)

            if not self._ensure_requests_loaded():
                return {"status": "error", "message": "requests module not available"}

            import requests

            # Refresh token request
            refresh_data = {
                "client_id": credentials["client_id"],
                "client_secret": credentials["client_secret"],
                "refresh_token": tokens["refresh_token"],
                "grant_type": "refresh_token",
            }

            response = requests.post(self.config.TOKEN_ENDPOINT, data=refresh_data)

            if response.status_code == 200:
                new_tokens = response.json()

                # Update tokens (preserve refresh token if not provided)
                if "refresh_token" not in new_tokens:
                    new_tokens["refresh_token"] = tokens["refresh_token"]

                # Save updated tokens
                with open(self.config.TOKEN_FILE, "w") as f:
                    json.dump(new_tokens, f, indent=2)

                logger.info("Gmail access token refreshed successfully")

                return {"status": "success", "message": "Access token refreshed", "tokens": new_tokens}
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return {"status": "error", "message": f"Token refresh failed: {response.status_code}"}

        except Exception as e:
            logger.error(f"Failed to refresh access token: {e}")
            return {"status": "error", "message": f"Token refresh failed: {str(e)}"}

    def get_valid_token(self) -> Optional[str]:
        """
        Get a valid access token (refresh if necessary)

        Returns:
            Valid access token or None if unable to obtain
        """

        try:
            # Check if token file exists
            if not os.path.exists(self.config.TOKEN_FILE):
                logger.warning("No OAuth tokens found - authentication required")
                return None

            # Load current tokens
            with open(self.config.TOKEN_FILE, "r") as f:
                tokens = json.load(f)

            # Check if token needs refresh (simplified check)
            # In production, check expiry time properly
            access_token = tokens.get("access_token")

            if not access_token:
                # Try to refresh
                refresh_result = self.refresh_access_token()
                if refresh_result["status"] == "success":
                    return refresh_result["tokens"]["access_token"]
                return None

            return access_token

        except Exception as e:
            logger.error(f"Failed to get valid token: {e}")
            return None

    def is_authenticated(self) -> bool:
        """Check if Gmail OAuth is properly authenticated"""

        try:
            return (
                os.path.exists(self.config.CREDENTIALS_FILE)
                and os.path.exists(self.config.TOKEN_FILE)
                and self.get_valid_token() is not None
            )
        except Exception:
            return False

    def get_oauth_status(self) -> Dict:
        """Get current OAuth authentication status"""

        status = {
            "authenticated": False,
            "credentials_configured": os.path.exists(self.config.CREDENTIALS_FILE),
            "tokens_available": os.path.exists(self.config.TOKEN_FILE),
            "needs_setup": False,
            "needs_authorization": False,
        }

        if not status["credentials_configured"]:
            status["needs_setup"] = True
            status["next_step"] = "setup_oauth_credentials"
        elif not status["tokens_available"]:
            status["needs_authorization"] = True
            status["next_step"] = "initiate_oauth_flow"
        else:
            status["authenticated"] = self.is_authenticated()
            if not status["authenticated"]:
                status["needs_authorization"] = True
                status["next_step"] = "refresh_tokens"

        return status


class GmailSender:
    """
    Gmail email sending functionality
    Uses authenticated Gmail API to send job application emails
    """

    def __init__(self, oauth_manager: GmailOAuthManager):
        self.oauth_manager = oauth_manager
        self.gmail_api_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"

    def send_job_application_email(
        self, to_email: str, subject: str, body: str, attachments: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Send job application email with attachments via Gmail API

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content
            attachments: List of attachment dictionaries with 'path' and 'filename'

        Returns:
            Send result status
        """

        try:
            # Get valid access token
            access_token = self.oauth_manager.get_valid_token()
            if not access_token:
                return {"status": "error", "message": "No valid access token available. OAuth authentication required."}

            # Create email message
            email_message = self._create_email_message(to_email, subject, body, attachments)
            if not email_message:
                return {"status": "error", "message": "Failed to create email message"}

            # Send via Gmail API
            return self._send_via_gmail_api(email_message, access_token)

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"status": "error", "message": f"Email sending failed: {str(e)}"}

    def _create_email_message(
        self, to_email: str, subject: str, body: str, attachments: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """
        Create RFC 2822 compliant email message with attachments

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content
            attachments: List of attachment dictionaries

        Returns:
            Base64 encoded email message or None if creation fails
        """

        try:
            import email.mime.multipart
            import email.mime.text
            import email.mime.base
            import email.encoders
            import base64
            from pathlib import Path

            # Create multipart message
            msg = email.mime.multipart.MIMEMultipart()
            msg["To"] = to_email
            msg["Subject"] = subject

            # Add body
            msg.attach(email.mime.text.MIMEText(body, "plain"))

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    file_path = attachment.get("path")
                    filename = attachment.get("filename")

                    if not file_path or not filename:
                        logger.warning(f"Invalid attachment: {attachment}")
                        continue

                    if not Path(file_path).exists():
                        logger.warning(f"Attachment file not found: {file_path}")
                        continue

                    try:
                        with open(file_path, "rb") as f:
                            attachment_data = f.read()

                        # Create attachment
                        part = email.mime.base.MIMEBase("application", "octet-stream")
                        part.set_payload(attachment_data)
                        email.encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
                        msg.attach(part)

                        logger.info(f"Added attachment: {filename}")

                    except Exception as e:
                        logger.error(f"Failed to attach file {file_path}: {e}")
                        continue

            # Convert to base64 encoded string for Gmail API
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
            return raw_message

        except Exception as e:
            logger.error(f"Failed to create email message: {e}")
            return None

    def _send_via_gmail_api(self, raw_message: str, access_token: str) -> Dict:
        """
        Send email via Gmail API

        Args:
            raw_message: Base64 encoded email message
            access_token: Valid OAuth access token

        Returns:
            Send result status
        """

        try:
            # Ensure requests is available
            if not self.oauth_manager._ensure_requests_loaded():
                return {"status": "error", "message": "requests module not available for API calls"}

            import requests

            # Prepare API request
            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

            payload = {"raw": raw_message}

            # Send request to Gmail API
            response = requests.post(self.gmail_api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get("id", "unknown")

                logger.info(f"Email sent successfully: {message_id}")

                return {
                    "status": "success",
                    "message": "Email sent successfully",
                    "gmail_message_id": message_id,
                    "thread_id": response_data.get("threadId"),
                    "label_ids": response_data.get("labelIds", []),
                }

            elif response.status_code == 401:
                # Token expired - try to refresh
                logger.warning("Access token expired, attempting refresh")
                refresh_result = self.oauth_manager.refresh_access_token()

                if refresh_result["status"] == "success":
                    # Retry with new token
                    return self._send_via_gmail_api(raw_message, refresh_result["tokens"]["access_token"])
                else:
                    return {
                        "status": "error",
                        "message": "Access token expired and refresh failed. Re-authentication required.",
                    }

            else:
                logger.error(f"Gmail API error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"Gmail API error: {response.status_code}",
                    "details": response.text,
                }

        except Exception as e:
            logger.error(f"Failed to send via Gmail API: {e}")
            return {"status": "error", "message": f"API request failed: {str(e)}"}

    def send_test_email(self, test_email: str) -> Dict:
        """
        Send a test email to verify Gmail integration

        Args:
            test_email: Email address to send test to

        Returns:
            Test result status
        """

        test_subject = "Job Application System - Gmail Integration Test"
        test_body = """
This is a test email from your Automated Job Application System.

Gmail OAuth integration is working correctly!

Features verified:
✓ OAuth 2.0 authentication
✓ Access token management
✓ Email sending via Gmail API
✓ Professional email formatting

Your job application automation is ready to send personalized applications.

---
Automated Job Application System v2.1.3
Generated: {timestamp}
        """.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S MT")
        )

        return self.send_job_application_email(
            to_email=test_email, subject=test_subject, body=test_body, attachments=None
        )


def get_gmail_oauth_manager() -> GmailOAuthManager:
    """Get Gmail OAuth manager instance"""
    return GmailOAuthManager()


def get_gmail_sender(oauth_manager: Optional[GmailOAuthManager] = None) -> GmailSender:
    """Get Gmail sender instance"""
    if oauth_manager is None:
        oauth_manager = get_gmail_oauth_manager()
    return GmailSender(oauth_manager)
