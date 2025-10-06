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
            - 's3': AWS S3 (future implementation)
            - 'gcs': Google Cloud Storage (future implementation)

        LOCAL_STORAGE_PATH: Base path for local storage
            - Default: './storage/generated_documents'

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

        elif backend_type == "s3":
            # Future implementation: AWS S3 storage
            logger.error("S3 storage backend not yet implemented")
            raise ValueError(
                "S3 storage backend is not yet implemented. Use 'local' for now."
            )

        elif backend_type == "gcs":
            # Future implementation: Google Cloud Storage
            logger.error("GCS storage backend not yet implemented")
            raise ValueError(
                "GCS storage backend is not yet implemented. Use 'local' for now."
            )

        else:
            logger.error(f"Unknown storage backend type: {backend_type}")
            raise ValueError(
                f"Unsupported storage backend: {backend_type}. "
                f"Supported backends: local, s3 (future), gcs (future)"
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

    elif backend_type in ["s3", "gcs"]:
        errors.append(f"{backend_type.upper()} storage backend not yet implemented")

    else:
        errors.append(f"Unknown storage backend type: {backend_type}")

    is_valid = len(errors) == 0

    return {
        "backend_type": backend_type,
        "is_valid": is_valid,
        "config": config,
        "errors": errors,
    }
