"""
Storage Module

This module provides a unified storage abstraction layer for the Merlin Job
Application System. It allows the application to store and retrieve files
using a consistent interface, regardless of the underlying storage technology.

Supported Storage Backends:
- Local Filesystem: Simple, reliable local storage (default)
- AWS S3: Cloud object storage (future implementation)
- Google Cloud Storage: Cloud object storage (future implementation)

Quick Start:
    from modules.storage import get_storage_backend

    # Get storage backend (automatically configured from environment)
    storage = get_storage_backend()

    # Save a file
    with open('document.docx', 'rb') as f:
        result = storage.save('my_document.docx', f.read())
    print(f"Saved to: {result['file_path']}")

    # Retrieve a file
    content = storage.get('my_document.docx')

    # Check if file exists
    if storage.exists('my_document.docx'):
        print("File exists!")

    # Delete a file
    storage.delete('my_document.docx')

Configuration:
    Set environment variables to configure storage:

    # Use local filesystem storage (default)
    STORAGE_BACKEND=local
    LOCAL_STORAGE_PATH=/path/to/storage

    # Future: Use AWS S3
    STORAGE_BACKEND=s3
    S3_BUCKET_NAME=my-bucket
    AWS_ACCESS_KEY_ID=...
    AWS_SECRET_ACCESS_KEY=...

Module Structure:
- storage_backend.py: Abstract base class defining storage interface
- local_storage.py: Local filesystem storage implementation
- storage_factory.py: Factory function for creating storage instances
- __init__.py: Module exports and documentation
"""

from .storage_backend import StorageBackend
from .local_storage import LocalStorageBackend
from .storage_factory import (
    get_storage_backend,
    reset_storage_instance,
    validate_storage_configuration,
)

# Define public API
__all__ = [
    # Abstract base class
    "StorageBackend",
    # Implementations
    "LocalStorageBackend",
    # Factory functions
    "get_storage_backend",
    "reset_storage_instance",
    "validate_storage_configuration",
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Merlin Development Team"
__description__ = "Storage abstraction layer for document management"
