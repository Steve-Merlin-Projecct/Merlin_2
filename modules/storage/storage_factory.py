"""
Storage Factory Module

This module provides a factory function for creating storage backend instances
based on configuration. It implements the Factory design pattern to allow
runtime selection of storage providers without changing application code.

Features:
- Environment-based backend selection
- Singleton pattern for storage instances
- Configuration validation
- Fallback to local storage
- Comprehensive logging

Configuration:
    Set environment variables to control storage backend:
    - STORAGE_BACKEND: Type of storage ('local', 's3', 'gcs', etc.)
    - LOCAL_STORAGE_PATH: Path for local filesystem storage

Usage Example:
    from modules.storage import get_storage_backend

    # Get configured storage backend
    storage = get_storage_backend()

    # Use storage (works regardless of backend type)
    storage.save('file.docx', b'content')
"""

import os
import logging
from typing import Optional
from .storage_backend import StorageBackend
from .local_storage import LocalStorageBackend

# Import Google Drive backend (may not be available if dependencies not installed)
try:
    from .google_drive_storage import GoogleDriveStorageBackend
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Singleton instance for storage backend
_storage_instance: Optional[StorageBackend] = None


def get_storage_backend(force_new: bool = False) -> StorageBackend:
    """
    Factory function to get storage backend instance

    This function returns a storage backend based on environment configuration.
    It uses a singleton pattern to ensure only one storage instance exists
    throughout the application lifecycle.

    Environment Variables:
        STORAGE_BACKEND: Type of storage backend to use
            - 'local' (default): Local filesystem storage
            - 'google_drive': Google Drive API storage

        LOCAL_STORAGE_PATH: Base path for local storage
            - Default: './storage/generated_documents'

        APP_VERSION: Application version for Google Drive folder organization
            - Required for google_drive backend
            - Format: X.Y (e.g., 4.1)

        GOOGLE_DRIVE_CREDENTIALS_PATH: Path to OAuth credentials
            - Required for google_drive backend
            - Default: './storage/google_drive_credentials.json'

        GOOGLE_DRIVE_TOKEN_PATH: Path to store OAuth token
            - Default: './storage/google_drive_token.json'

    Args:
        force_new (bool): If True, create a new instance even if one exists.
            Useful for testing. Default: False

    Returns:
        StorageBackend: Configured storage backend instance

    Raises:
        ValueError: If STORAGE_BACKEND specifies an unsupported backend type
        RuntimeError: If storage backend initialization fails

    Example:
        >>> storage = get_storage_backend()
        >>> storage.save('test.docx', b'content')
        {'file_path': '...', 'filename': 'test.docx', ...}
    """
    global _storage_instance

    # Return existing instance if available (singleton pattern)
    if _storage_instance is not None and not force_new:
        logger.debug("Returning existing storage backend instance")
        return _storage_instance

    # Get storage backend type from environment
    backend_type = os.getenv("STORAGE_BACKEND", "local").lower()

    logger.info(f"Initializing storage backend: {backend_type}")

    # Create storage backend based on type
    try:
        if backend_type == "local":
            # Get base path from environment or use default
            base_path = os.getenv("LOCAL_STORAGE_PATH")

            if base_path:
                logger.info(f"Using configured local storage path: {base_path}")
            else:
                # Use default path relative to project root
                base_path = os.path.join(os.getcwd(), "storage", "generated_documents")
                logger.info(f"Using default local storage path: {base_path}")

            _storage_instance = LocalStorageBackend(base_path=base_path)

        elif backend_type == "google_drive":
            # Google Drive API storage
            if not GOOGLE_DRIVE_AVAILABLE:
                logger.error("Google Drive storage requires additional dependencies")
                raise RuntimeError(
                    "Google Drive storage backend requires Google API libraries. "
                    "Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
                )

            credentials_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
            token_path = os.getenv("GOOGLE_DRIVE_TOKEN_PATH")

            _storage_instance = GoogleDriveStorageBackend(
                credentials_path=credentials_path,
                token_path=token_path
            )

        else:
            logger.error(f"Unknown storage backend type: {backend_type}")
            raise ValueError(
                f"Unsupported storage backend: {backend_type}. "
                f"Supported backends: local, google_drive"
            )

        logger.info(f"Storage backend initialized successfully: {backend_type}")
        return _storage_instance

    except Exception as e:
        logger.error(f"Failed to initialize storage backend: {e}")
        raise RuntimeError(f"Storage backend initialization failed: {e}")


def reset_storage_instance() -> None:
    """
    Reset the singleton storage instance

    This function clears the cached storage instance, forcing a new instance
    to be created on the next call to get_storage_backend(). This is primarily
    useful for testing.

    Warning:
        This should not be called in production code as it can lead to
        multiple storage instances existing simultaneously.

    Example:
        >>> from modules.storage.storage_factory import reset_storage_instance
        >>> reset_storage_instance()
        >>> storage = get_storage_backend()  # Creates new instance
    """
    global _storage_instance
    _storage_instance = None
    logger.debug("Storage backend instance reset")


def validate_storage_configuration() -> dict:
    """
    Validate current storage configuration

    This function checks the environment configuration and reports on the
    storage backend that would be created, without actually creating it.

    Returns:
        dict: Configuration validation results containing:
            - backend_type (str): Configured backend type
            - is_valid (bool): Whether configuration is valid
            - config (dict): Current configuration values
            - errors (list): Any configuration errors found

    Example:
        >>> from modules.storage.storage_factory import validate_storage_configuration
        >>> result = validate_storage_configuration()
        >>> print(result['is_valid'])
        True
    """
    backend_type = os.getenv("STORAGE_BACKEND", "local").lower()
    errors = []
    config = {}

    if backend_type == "local":
        base_path = os.getenv("LOCAL_STORAGE_PATH")
        config["base_path"] = base_path or "./storage/generated_documents (default)"

        # Check if custom path exists and is writable
        if base_path:
            if not os.path.exists(base_path):
                errors.append(f"Configured LOCAL_STORAGE_PATH does not exist: {base_path}")
            elif not os.access(base_path, os.W_OK):
                errors.append(f"LOCAL_STORAGE_PATH is not writable: {base_path}")

    elif backend_type == "google_drive":
        if not GOOGLE_DRIVE_AVAILABLE:
            errors.append("Google Drive backend requires: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

        app_version = os.getenv("APP_VERSION")
        credentials_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "./storage/google_drive_credentials.json")
        token_path = os.getenv("GOOGLE_DRIVE_TOKEN_PATH", "./storage/google_drive_token.json")

        config["app_version"] = app_version or "NOT SET"
        config["credentials_path"] = credentials_path
        config["token_path"] = token_path

        if not app_version:
            errors.append("APP_VERSION environment variable required for Google Drive backend")

        if not os.path.exists(credentials_path):
            errors.append(f"Google Drive credentials not found at: {credentials_path}")

    else:
        errors.append(f"Unknown storage backend type: {backend_type}")

    is_valid = len(errors) == 0

    return {
        "backend_type": backend_type,
        "is_valid": is_valid,
        "config": config,
        "errors": errors,
    }
