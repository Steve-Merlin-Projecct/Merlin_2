"""
Local Filesystem Storage Backend

This module implements local filesystem storage for the Merlin Job Application System.
It provides a simple, reliable storage solution that works in any environment without
external dependencies or cloud service configuration.

Features:
- Automatic directory creation with proper permissions
- Path sanitization to prevent directory traversal attacks
- Organized directory structure by document type
- File metadata tracking
- Support for pattern-based file listing

Directory Structure:
    /storage/
        /generated_documents/
            resume_2025_10_06_abc123.docx
            coverletter_2025_10_06_def456.docx

Usage Example:
    from modules.storage.local_storage import LocalStorageBackend

    storage = LocalStorageBackend(base_path='/workspace/storage/generated_documents')

    # Save document
    with open('resume.docx', 'rb') as f:
        result = storage.save('resume_2025.docx', f.read())

    # Retrieve document
    content = storage.get('resume_2025.docx')
"""

import os
import logging
import fnmatch
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from .storage_backend import StorageBackend

logger = logging.getLogger(__name__)


class LocalStorageBackend(StorageBackend):
    """
    Local filesystem storage implementation

    This class stores files in a local directory structure. It handles
    directory creation, permissions, and file operations with comprehensive
    error handling.

    Attributes:
        base_path (Path): Root directory for file storage
        backend_name (str): Name of the storage backend ('LocalStorageBackend')
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize local storage backend

        Creates the base storage directory if it doesn't exist and validates
        that the path is writable.

        Args:
            base_path (str, optional): Root directory for storage.
                Defaults to './storage/generated_documents'

        Raises:
            PermissionError: If base_path is not writable
            OSError: If directory cannot be created
        """
        super().__init__()

        # Set default base path if not provided
        if base_path is None:
            base_path = os.path.join(os.getcwd(), "storage", "generated_documents")

        self.base_path = Path(base_path).resolve()

        # Create directory structure if it doesn't exist
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Local storage initialized at: {self.base_path}")
        except PermissionError as e:
            logger.error(f"Permission denied creating storage directory: {self.base_path}")
            raise PermissionError(f"Cannot create storage directory: {e}")
        except OSError as e:
            logger.error(f"Failed to create storage directory: {e}")
            raise OSError(f"Storage directory creation failed: {e}")

        # Verify directory is writable
        if not os.access(self.base_path, os.W_OK):
            raise PermissionError(f"Storage directory is not writable: {self.base_path}")

    def save(self, filename: str, content: bytes, metadata: Optional[dict] = None) -> dict:
        """
        Save file to local filesystem

        Writes binary content to a file in the storage directory. Automatically
        creates any necessary subdirectories and handles errors gracefully.

        Args:
            filename (str): Name of the file to save
            content (bytes): Binary content to write
            metadata (dict, optional): Additional metadata (not used in local storage)

        Returns:
            dict: Storage information with file details

        Raises:
            ValueError: If filename is invalid
            IOError: If file cannot be written
            PermissionError: If insufficient permissions
        """
        # Validate filename for security
        self.validate_filename(filename)

        # Construct full file path
        file_path = self.base_path / filename

        try:
            # Ensure parent directories exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            with open(file_path, "wb") as f:
                f.write(content)

            file_size = len(content)
            timestamp = datetime.now().isoformat()

            logger.info(
                f"File saved successfully: {filename} ({file_size} bytes) at {file_path}"
            )

            return {
                "file_path": str(file_path),
                "filename": filename,
                "storage_type": "local",
                "file_size": file_size,
                "timestamp": timestamp,
                "local_path": str(file_path),
            }

        except PermissionError as e:
            logger.error(f"Permission denied writing file {filename}: {e}")
            raise PermissionError(f"Cannot write file {filename}: {e}")
        except IOError as e:
            logger.error(f"IO error writing file {filename}: {e}")
            raise IOError(f"Failed to write file {filename}: {e}")

    def get(self, filename: str) -> bytes:
        """
        Retrieve file content from local filesystem

        Reads and returns the binary content of a file. Validates filename
        and checks file existence before reading.

        Args:
            filename (str): Name of the file to retrieve

        Returns:
            bytes: Binary content of the file

        Raises:
            ValueError: If filename is invalid
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
            PermissionError: If insufficient permissions
        """
        # Validate filename for security
        self.validate_filename(filename)

        # Construct full file path
        file_path = self.base_path / filename

        # Check if file exists
        if not file_path.exists():
            logger.warning(f"File not found: {filename}")
            raise FileNotFoundError(f"File not found: {filename}")

        # Check if path is a file (not directory)
        if not file_path.is_file():
            logger.error(f"Path is not a file: {filename}")
            raise IOError(f"Path is not a file: {filename}")

        try:
            # Read file content
            with open(file_path, "rb") as f:
                content = f.read()

            logger.info(f"File retrieved successfully: {filename} ({len(content)} bytes)")
            return content

        except PermissionError as e:
            logger.error(f"Permission denied reading file {filename}: {e}")
            raise PermissionError(f"Cannot read file {filename}: {e}")
        except IOError as e:
            logger.error(f"IO error reading file {filename}: {e}")
            raise IOError(f"Failed to read file {filename}: {e}")

    def delete(self, filename: str) -> bool:
        """
        Delete file from local filesystem

        Removes a file from storage. Returns False if file doesn't exist
        rather than raising an exception.

        Args:
            filename (str): Name of the file to delete

        Returns:
            bool: True if file was deleted, False if file did not exist

        Raises:
            ValueError: If filename is invalid
            IOError: If deletion fails
            PermissionError: If insufficient permissions
        """
        # Validate filename for security
        self.validate_filename(filename)

        # Construct full file path
        file_path = self.base_path / filename

        # Check if file exists
        if not file_path.exists():
            logger.info(f"File does not exist (nothing to delete): {filename}")
            return False

        try:
            # Delete the file
            file_path.unlink()
            logger.info(f"File deleted successfully: {filename}")
            return True

        except PermissionError as e:
            logger.error(f"Permission denied deleting file {filename}: {e}")
            raise PermissionError(f"Cannot delete file {filename}: {e}")
        except IOError as e:
            logger.error(f"IO error deleting file {filename}: {e}")
            raise IOError(f"Failed to delete file {filename}: {e}")

    def exists(self, filename: str) -> bool:
        """
        Check if file exists in local filesystem

        This is a lightweight check that doesn't read file content.

        Args:
            filename (str): Name of the file to check

        Returns:
            bool: True if file exists and is a file, False otherwise

        Raises:
            ValueError: If filename is invalid
        """
        # Validate filename for security
        self.validate_filename(filename)

        # Construct full file path
        file_path = self.base_path / filename

        # Check existence and that it's a file
        exists = file_path.exists() and file_path.is_file()

        logger.debug(f"File existence check for {filename}: {exists}")
        return exists

    def list(self, prefix: Optional[str] = None, pattern: Optional[str] = None) -> List[str]:
        """
        List files in local filesystem storage

        Returns a list of filenames, optionally filtered by prefix or glob pattern.
        Only returns files (not directories).

        Args:
            prefix (str, optional): Filter files by prefix (e.g., 'resume_')
            pattern (str, optional): Glob pattern to match (e.g., '*.docx')

        Returns:
            List[str]: List of filenames matching the criteria

        Raises:
            IOError: If listing operation fails
        """
        try:
            # Get all files in base path (non-recursive)
            all_files = [
                f.name for f in self.base_path.iterdir() if f.is_file()
            ]

            # Apply prefix filter if provided
            if prefix:
                all_files = [f for f in all_files if f.startswith(prefix)]

            # Apply pattern filter if provided
            if pattern:
                all_files = [f for f in all_files if fnmatch.fnmatch(f, pattern)]

            logger.info(
                f"Listed {len(all_files)} files (prefix={prefix}, pattern={pattern})"
            )
            return sorted(all_files)

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            raise IOError(f"Failed to list files: {e}")

    def get_storage_info(self) -> dict:
        """
        Get information about the storage backend

        Returns:
            dict: Storage backend information including path and statistics
        """
        try:
            all_files = self.list()
            total_size = sum(
                (self.base_path / f).stat().st_size for f in all_files
            )

            return {
                "backend_type": "local",
                "base_path": str(self.base_path),
                "total_files": len(all_files),
                "total_size_bytes": total_size,
                "writable": os.access(self.base_path, os.W_OK),
            }
        except Exception as e:
            logger.error(f"Error getting storage info: {e}")
            return {
                "backend_type": "local",
                "base_path": str(self.base_path),
                "error": str(e),
            }
