"""
Google Drive Storage Backend

This module implements Google Drive API v3 as a storage backend for the Merlin
Job Application System. It provides cloud-based document storage with automatic
organization by application version number.

Features:
- OAuth 2.0 user authentication
- Automatic folder creation by version (e.g., /Merlin Documents/v4.1/)
- Version-tagged filenames (merlin_v4.1_document.docx)
- Private file permissions (owner-only access)
- Google Drive file ID and link tracking
- Automatic fallback to local storage on errors

Prerequisites:
- Google Cloud Project with Drive API enabled
- OAuth 2.0 credentials (credentials.json)
- APP_VERSION environment variable set

Usage Example:
    from modules.storage.google_drive_storage import GoogleDriveStorageBackend

    storage = GoogleDriveStorageBackend()
    result = storage.save('document.docx', file_content)
    # Returns: {
    #   'google_drive_file_id': '1a2b3c...',
    #   'google_drive_link': 'https://drive.google.com/file/d/...',
    #   ...
    # }
"""

import os
import io
import logging
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False

from .storage_backend import StorageBackend

logger = logging.getLogger(__name__)

# OAuth 2.0 scopes - only access files created by this app
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveStorageBackend(StorageBackend):
    """
    Google Drive API storage implementation

    This class provides cloud storage using Google Drive API v3. Files are
    automatically organized into version-specific folders and tagged with
    application version numbers for traceability.

    Attributes:
        app_version (str): Application version from environment (e.g., "4.1")
        credentials_path (Path): Path to OAuth credentials JSON
        token_path (Path): Path to stored OAuth token
        service: Google Drive API service instance
        folder_cache (dict): Cache of folder IDs to avoid repeated searches
    """

    def __init__(self,
                 credentials_path: Optional[str] = None,
                 token_path: Optional[str] = None):
        """
        Initialize Google Drive storage backend

        Args:
            credentials_path (str, optional): Path to credentials.json
            token_path (str, optional): Path to token.json

        Raises:
            ImportError: If Google API libraries not installed
            ValueError: If APP_VERSION environment variable not set
            RuntimeError: If authentication fails
        """
        super().__init__()

        # Check if Google APIs are available
        if not GOOGLE_APIS_AVAILABLE:
            raise ImportError(
                "Google API libraries not installed. Install with: "
                "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )

        # Get application version from environment
        self.app_version = os.getenv('APP_VERSION')
        if not self.app_version:
            raise ValueError(
                "APP_VERSION environment variable not set. "
                "Set it to current version (e.g., APP_VERSION=4.1)"
            )

        # Validate version format (X.Y)
        if not self._validate_version_format(self.app_version):
            raise ValueError(
                f"Invalid APP_VERSION format: {self.app_version}. "
                "Must be in format X.Y (e.g., 4.1)"
            )

        # Set credential paths
        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
            self.credentials_path = Path(
                os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH',
                         './storage/google_drive_credentials.json')
            )

        if token_path:
            self.token_path = Path(token_path)
        else:
            self.token_path = Path(
                os.getenv('GOOGLE_DRIVE_TOKEN_PATH',
                         './storage/google_drive_token.json')
            )

        # Initialize service and folder cache
        self.service = None
        self.folder_cache: Dict[str, str] = {}

        # Authenticate and build service
        self._authenticate()

        logger.info(
            f"Google Drive storage initialized for version {self.app_version}"
        )

    def _validate_version_format(self, version: str) -> bool:
        """
        Validate version number format

        Args:
            version (str): Version string to validate

        Returns:
            bool: True if format is valid (X.Y pattern)
        """
        import re
        return bool(re.match(r'^\d+\.\d+$', version))

    def _authenticate(self) -> None:
        """
        Authenticate with Google Drive using OAuth 2.0

        This method handles the complete OAuth flow:
        1. Check for existing token
        2. Refresh if expired
        3. Run OAuth flow if no valid token
        4. Build Drive API service

        Raises:
            RuntimeError: If authentication fails
            FileNotFoundError: If credentials.json not found
        """
        creds = None

        # Load existing token if available
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(self.token_path), SCOPES
                )
                logger.info("Loaded existing Google Drive credentials")
            except Exception as e:
                logger.warning(f"Failed to load existing credentials: {e}")

        # Refresh or re-authenticate if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed Google Drive credentials")
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {e}")
                    creds = None

            if not creds:
                # Need to run OAuth flow
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Google Drive credentials not found at: {self.credentials_path}\n"
                        "Please follow the setup instructions to obtain credentials.json"
                    )

                # This will require user interaction - browser-based OAuth
                logger.info("Starting OAuth 2.0 authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("OAuth authentication successful")

            # Save credentials for future use
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'w') as token_file:
                token_file.write(creds.to_json())
            logger.info(f"Saved credentials to: {self.token_path}")

        # Build the Drive API service
        try:
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive API service initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to build Google Drive service: {e}")

    def _get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """
        Get existing folder ID or create new folder

        Args:
            folder_name (str): Name of folder to find or create
            parent_id (str, optional): Parent folder ID

        Returns:
            str: Folder ID

        Raises:
            HttpError: If folder operation fails
        """
        # Check cache first
        cache_key = f"{parent_id or 'root'}:{folder_name}"
        if cache_key in self.folder_cache:
            return self.folder_cache[cache_key]

        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        else:
            query += " and 'root' in parents"
        query += " and trashed=false"

        try:
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            items = results.get('files', [])

            if items:
                # Folder exists
                folder_id = items[0]['id']
                logger.debug(f"Found existing folder: {folder_name} (ID: {folder_id})")
            else:
                # Create new folder
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                if parent_id:
                    file_metadata['parents'] = [parent_id]

                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()

                folder_id = folder['id']
                logger.info(f"Created folder: {folder_name} (ID: {folder_id})")

            # Cache the folder ID
            self.folder_cache[cache_key] = folder_id
            return folder_id

        except HttpError as e:
            logger.error(f"Error getting/creating folder {folder_name}: {e}")
            raise

    def _ensure_version_folder(self) -> str:
        """
        Ensure version-specific folder structure exists

        Creates: /Merlin Documents/v{version}/

        Returns:
            str: Version folder ID
        """
        # Create root folder
        root_folder_id = self._get_or_create_folder("Merlin Documents")

        # Create version folder
        version_folder_name = f"v{self.app_version}"
        version_folder_id = self._get_or_create_folder(
            version_folder_name,
            root_folder_id
        )

        return version_folder_id

    def _format_filename(self, filename: str) -> str:
        """
        Format filename with application version prefix

        Args:
            filename (str): Original filename

        Returns:
            str: Formatted filename (e.g., merlin_v4.1_resume_2025_10_06.docx)
        """
        return f"merlin_v{self.app_version}_{filename}"

    def save(self, filename: str, content: bytes, metadata: Optional[dict] = None) -> dict:
        """
        Save file to Google Drive

        Uploads file to version-specific folder with formatted filename.
        Returns Google Drive file ID and shareable link.

        Args:
            filename (str): Name of file to save
            content (bytes): File content
            metadata (dict, optional): Additional metadata

        Returns:
            dict: Storage information including Google Drive file ID and link

        Raises:
            ValueError: If filename is invalid
            HttpError: If upload fails
        """
        # Validate filename
        self.validate_filename(filename)

        try:
            # Ensure folder structure exists
            folder_id = self._ensure_version_folder()

            # Format filename with version
            formatted_filename = self._format_filename(filename)

            # Prepare file metadata
            file_metadata = {
                'name': formatted_filename,
                'parents': [folder_id]
            }

            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(content),
                mimetype='application/octet-stream',
                resumable=True
            )

            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, createdTime, size'
            ).execute()

            file_id = file['id']
            web_link = file['webViewLink']
            file_size = int(file.get('size', len(content)))

            logger.info(
                f"Uploaded to Google Drive: {formatted_filename} "
                f"(ID: {file_id}, Size: {file_size} bytes)"
            )

            return {
                'file_path': file_id,  # Use file ID as path
                'filename': formatted_filename,
                'storage_type': 'google_drive',
                'file_size': file_size,
                'timestamp': datetime.now().isoformat(),
                'google_drive_file_id': file_id,
                'google_drive_link': web_link,
                'folder_path': f"/Merlin Documents/v{self.app_version}/"
            }

        except HttpError as e:
            logger.error(f"Google Drive upload failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise

    def get(self, filename: str) -> bytes:
        """
        Retrieve file from Google Drive

        Args:
            filename (str): Name of file to retrieve (can be file ID or filename)

        Returns:
            bytes: File content

        Raises:
            FileNotFoundError: If file not found
            HttpError: If download fails
        """
        # Validate filename
        self.validate_filename(filename)

        try:
            # Check if filename is actually a file ID (Google Drive IDs don't have extensions)
            if '.' not in filename:
                file_id = filename
            else:
                # Search for file by name
                formatted_filename = self._format_filename(filename)
                folder_id = self._ensure_version_folder()

                query = (
                    f"name='{formatted_filename}' and '{folder_id}' in parents "
                    f"and trashed=false"
                )

                results = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name)'
                ).execute()

                items = results.get('files', [])
                if not items:
                    raise FileNotFoundError(f"File not found: {filename}")

                file_id = items[0]['id']

            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            content = file_content.getvalue()
            logger.info(f"Downloaded from Google Drive: {filename} ({len(content)} bytes)")
            return content

        except HttpError as e:
            if e.resp.status == 404:
                raise FileNotFoundError(f"File not found: {filename}")
            logger.error(f"Google Drive download failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            raise

    def delete(self, filename: str) -> bool:
        """
        Delete file from Google Drive

        Args:
            filename (str): Name of file to delete

        Returns:
            bool: True if deleted, False if not found

        Raises:
            HttpError: If delete operation fails
        """
        # Validate filename
        self.validate_filename(filename)

        try:
            # Search for file
            formatted_filename = self._format_filename(filename)
            folder_id = self._ensure_version_folder()

            query = (
                f"name='{formatted_filename}' and '{folder_id}' in parents "
                f"and trashed=false"
            )

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            items = results.get('files', [])
            if not items:
                logger.info(f"File not found for deletion: {filename}")
                return False

            file_id = items[0]['id']

            # Delete file
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted from Google Drive: {formatted_filename}")
            return True

        except HttpError as e:
            logger.error(f"Google Drive delete failed: {e}")
            raise

    def exists(self, filename: str) -> bool:
        """
        Check if file exists in Google Drive

        Args:
            filename (str): Name of file to check

        Returns:
            bool: True if file exists
        """
        # Validate filename
        self.validate_filename(filename)

        try:
            formatted_filename = self._format_filename(filename)
            folder_id = self._ensure_version_folder()

            query = (
                f"name='{formatted_filename}' and '{folder_id}' in parents "
                f"and trashed=false"
            )

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()

            exists = len(results.get('files', [])) > 0
            logger.debug(f"File existence check for {filename}: {exists}")
            return exists

        except HttpError as e:
            logger.error(f"Google Drive exists check failed: {e}")
            return False

    def list(self, prefix: Optional[str] = None, pattern: Optional[str] = None) -> List[str]:
        """
        List files in Google Drive version folder

        Args:
            prefix (str, optional): Filter by filename prefix
            pattern (str, optional): Glob pattern (converted to contains search)

        Returns:
            List[str]: List of original filenames (version prefix removed)
        """
        try:
            folder_id = self._ensure_version_folder()

            # Build query
            query = f"'{folder_id}' in parents and trashed=false"

            # Add prefix filter
            if prefix:
                formatted_prefix = self._format_filename(prefix)
                query += f" and name contains '{formatted_prefix}'"

            # Add pattern filter (convert glob * to contains)
            if pattern:
                # Simple conversion: *.docx -> contains '.docx'
                if pattern.startswith('*'):
                    search_term = pattern[1:]  # Remove leading *
                    query += f" and name contains '{search_term}'"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(name)',
                pageSize=100
            ).execute()

            items = results.get('files', [])

            # Remove version prefix from filenames
            version_prefix = f"merlin_v{self.app_version}_"
            filenames = [
                item['name'].replace(version_prefix, '', 1)
                for item in items
            ]

            logger.info(f"Listed {len(filenames)} files from Google Drive")
            return sorted(filenames)

        except HttpError as e:
            logger.error(f"Google Drive list failed: {e}")
            raise IOError(f"Failed to list files: {e}")
