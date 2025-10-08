"""
Storage Backend Abstract Base Class

This module defines the abstract interface for all storage backends in the Merlin
Job Application System. It provides a consistent API for storing, retrieving, and
managing document files regardless of the underlying storage technology (local
filesystem, AWS S3, Google Cloud Storage, etc.).

Design Principles:
- Platform-agnostic: Works with any storage provider
- Simple interface: Designed for compatibility with object storage patterns
- Error handling: Consistent exception patterns across implementations
- Type safety: Full type hints for better IDE support

Legacy Note: Interface originally designed to ease migration from Replit Object Storage.

Usage Example:
    from modules.storage import get_storage_backend

    storage = get_storage_backend()

    # Save a document
    with open('document.docx', 'rb') as f:
        content = f.read()
    storage.save('resume_2025.docx', content)

    # Retrieve a document
    file_data = storage.get('resume_2025.docx')

    # Check existence
    if storage.exists('resume_2025.docx'):
        storage.delete('resume_2025.docx')
"""

from abc import ABC, abstractmethod
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """
    Abstract base class for storage backends

    All storage implementations (local, S3, GCS, etc.) must inherit from this
    class and implement all abstract methods. This ensures consistent behavior
    across different storage providers.

    Attributes:
        backend_name (str): Human-readable name of the storage backend
    """

    def __init__(self):
        """Initialize storage backend with logging"""
        self.backend_name = self.__class__.__name__
        logger.info(f"Initializing storage backend: {self.backend_name}")

    @abstractmethod
    def save(self, filename: str, content: bytes, metadata: Optional[dict] = None) -> dict:
        """
        Save file content to storage

        This method stores the provided binary content with the given filename.
        It should handle directory creation, path sanitization, and error handling.

        Args:
            filename (str): Name of the file to save (e.g., 'resume_2025.docx')
            content (bytes): Binary content of the file
            metadata (dict, optional): Additional metadata to store with the file
                - content_type: MIME type of the file
                - document_type: Type of document (resume, cover_letter, etc.)

        Returns:
            dict: Storage information containing:
                - file_path (str): Full path or key where file is stored
                - filename (str): Name of the stored file
                - storage_type (str): Type of storage used (local, s3, gcs, etc.)
                - file_size (int): Size of stored file in bytes
                - timestamp (str): ISO format timestamp of storage

        Raises:
            ValueError: If filename is invalid or contains path traversal attempts
            IOError: If storage operation fails
            PermissionError: If insufficient permissions to write

        Example:
            >>> storage.save('test.docx', b'file content')
            {
                'file_path': '/storage/generated_documents/test.docx',
                'filename': 'test.docx',
                'storage_type': 'local',
                'file_size': 12,
                'timestamp': '2025-10-06T12:00:00'
            }
        """
        pass

    @abstractmethod
    def get(self, filename: str) -> bytes:
        """
        Retrieve file content from storage

        This method retrieves the binary content of a file by its filename.
        It should validate the filename and handle missing files gracefully.

        Args:
            filename (str): Name of the file to retrieve

        Returns:
            bytes: Binary content of the file

        Raises:
            ValueError: If filename is invalid or contains path traversal attempts
            FileNotFoundError: If file does not exist in storage
            IOError: If file cannot be read
            PermissionError: If insufficient permissions to read

        Example:
            >>> content = storage.get('test.docx')
            >>> print(len(content))
            12
        """
        pass

    @abstractmethod
    def delete(self, filename: str) -> bool:
        """
        Delete file from storage

        This method removes a file from storage. It should handle missing
        files gracefully and return False rather than raising an exception.

        Args:
            filename (str): Name of the file to delete

        Returns:
            bool: True if file was deleted, False if file did not exist

        Raises:
            ValueError: If filename is invalid
            IOError: If deletion fails due to storage error
            PermissionError: If insufficient permissions to delete

        Example:
            >>> storage.delete('old_resume.docx')
            True
            >>> storage.delete('nonexistent.docx')
            False
        """
        pass

    @abstractmethod
    def exists(self, filename: str) -> bool:
        """
        Check if file exists in storage

        This method checks for file existence without retrieving content.
        It should be efficient and not read the entire file.

        Args:
            filename (str): Name of the file to check

        Returns:
            bool: True if file exists, False otherwise

        Raises:
            ValueError: If filename is invalid

        Example:
            >>> storage.exists('test.docx')
            True
            >>> storage.exists('missing.docx')
            False
        """
        pass

    @abstractmethod
    def list(self, prefix: Optional[str] = None, pattern: Optional[str] = None) -> List[str]:
        """
        List files in storage

        This method returns a list of filenames stored in the backend,
        optionally filtered by prefix or glob pattern.

        Args:
            prefix (str, optional): Filter files by prefix (e.g., 'resume_')
            pattern (str, optional): Glob pattern to match (e.g., '*.docx')

        Returns:
            List[str]: List of filenames matching the criteria

        Raises:
            IOError: If listing operation fails

        Example:
            >>> storage.list(prefix='resume_')
            ['resume_2025.docx', 'resume_2024.docx']
            >>> storage.list(pattern='*.pdf')
            ['document.pdf', 'report.pdf']
        """
        pass

    def validate_filename(self, filename: str) -> None:
        """
        Validate filename for security

        This method checks that the filename does not contain path traversal
        attempts or invalid characters. It raises ValueError if validation fails.

        Args:
            filename (str): Filename to validate

        Raises:
            ValueError: If filename is invalid, empty, or contains security risks

        Example:
            >>> storage.validate_filename('test.docx')  # OK
            >>> storage.validate_filename('../etc/passwd')  # Raises ValueError
        """
        if not filename:
            raise ValueError("Filename cannot be empty")

        # Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            raise ValueError(
                f"Invalid filename '{filename}': contains path traversal or directory separators"
            )

        # Check for null bytes (security)
        if "\x00" in filename:
            raise ValueError(f"Invalid filename '{filename}': contains null byte")

        logger.debug(f"Filename validation passed: {filename}")
