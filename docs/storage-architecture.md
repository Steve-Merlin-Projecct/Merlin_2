# Storage Architecture Documentation

**Version:** 1.0
**Last Updated:** October 6, 2025
**Status:** Active

## Overview

The Merlin Job Application System uses a modular storage abstraction layer that provides a consistent interface for file storage operations across different backend technologies. This design allows the application to seamlessly switch between local filesystem storage and Google Drive without changing application code.

## Architecture Design

### Design Principles

1. **Abstraction:** Application code interacts with a consistent API regardless of storage backend
2. **Flexibility:** Easy runtime selection of storage provider via environment configuration
3. **Extensibility:** New storage backends can be added without modifying existing code
4. **Simplicity:** Minimal configuration required for basic local storage
5. **Cloud Storage:** Supports Google Drive for cloud-based document storage

### Module Structure

```
modules/storage/
├── __init__.py              # Public API exports
├── storage_backend.py       # Abstract base class defining interface
├── local_storage.py         # Local filesystem implementation
└── storage_factory.py       # Factory function for backend selection
```

### Class Hierarchy

```
StorageBackend (ABC)
├── LocalStorageBackend
└── GoogleDriveStorageBackend
```

## Storage Backend Interface

All storage backends implement the `StorageBackend` abstract base class:

### Core Methods

#### `save(filename: str, content: bytes, metadata: Optional[dict] = None) -> dict`
Saves file content to storage.

**Parameters:**
- `filename`: Name of the file to save
- `content`: Binary content of the file
- `metadata`: Optional metadata dictionary

**Returns:**
```python
{
    "file_path": "/storage/generated_documents/document.docx",
    "filename": "document.docx",
    "storage_type": "local",
    "file_size": 36808,
    "timestamp": "2025-10-06T12:00:00"
}
```

#### `get(filename: str) -> bytes`
Retrieves file content from storage.

**Returns:** Binary content of the file
**Raises:** `FileNotFoundError` if file doesn't exist

#### `delete(filename: str) -> bool`
Deletes a file from storage.

**Returns:** `True` if deleted, `False` if file didn't exist

#### `exists(filename: str) -> bool`
Checks if a file exists in storage.

**Returns:** `True` if file exists, `False` otherwise

#### `list(prefix: Optional[str] = None, pattern: Optional[str] = None) -> List[str]`
Lists files in storage with optional filtering.

**Parameters:**
- `prefix`: Filter files by prefix (e.g., 'resume_')
- `pattern`: Glob pattern to match (e.g., '*.docx')

**Returns:** List of filenames

### Security Features

#### Filename Validation
All backends include `validate_filename()` method that prevents:
- Path traversal attacks (e.g., `../etc/passwd`)
- Directory separators in filenames
- Null byte injection
- Empty filenames

## Local Storage Backend

### Implementation: `LocalStorageBackend`

The default storage backend that stores files in the local filesystem.

### Directory Structure

```
storage/
└── generated_documents/
    ├── resume_2025_10_06_abc123.docx
    ├── coverletter_2025_10_06_def456.docx
    └── test_document.txt
```

### Configuration

**Environment Variables:**
```bash
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./storage/generated_documents
```

**Defaults:**
- Backend type: `local`
- Storage path: `./storage/generated_documents` (relative to project root)

### Features

- Automatic directory creation with proper permissions
- Path sanitization for security
- File metadata tracking
- Pattern-based file listing
- Comprehensive error handling

### Error Handling

- `PermissionError`: Raised if directory is not writable
- `FileNotFoundError`: Raised when retrieving non-existent files
- `IOError`: Raised for filesystem read/write errors
- `ValueError`: Raised for invalid filenames

## Usage Examples

### Basic Usage

```python
from modules.storage import get_storage_backend

# Get configured storage backend
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

# List all .docx files
docx_files = storage.list(pattern='*.docx')

# Delete a file
storage.delete('my_document.docx')
```

### Integration with Document Generator

```python
from modules.content.document_generation.document_generator import DocumentGenerator

# Document generator automatically uses configured storage backend
generator = DocumentGenerator()

# Generate document (automatically saved to storage)
result = generator.generate_document(
    data={"full_name": "John Doe", ...},
    document_type="resume"
)

print(f"Document saved: {result['filename']}")
print(f"Storage type: {result['storage_type']}")
```

### Download Files via API

```python
from modules.document_routes import document_bp

# GET /download/<filename>
# Automatically retrieves from configured storage backend
# Falls back to local storage directory if storage backend fails
```

## Configuration Guide

### Local Filesystem Storage (Default)

**Setup:**
1. Set environment variables (or use defaults):
   ```bash
   STORAGE_BACKEND=local
   LOCAL_STORAGE_PATH=./storage/generated_documents
   ```

2. Ensure directory exists and is writable:
   ```bash
   mkdir -p storage/generated_documents
   chmod 755 storage/generated_documents
   ```

3. Verify configuration:
   ```python
   from modules.storage import validate_storage_configuration
   result = validate_storage_configuration()
   print(result)
   ```

### Google Drive Storage

**Implementation:**
```bash
STORAGE_BACKEND=google_drive
APP_VERSION=4.1
GOOGLE_DRIVE_CREDENTIALS_PATH=./storage/google_drive_credentials.json
GOOGLE_DRIVE_TOKEN_PATH=./storage/google_drive_token.json
```

**Setup Guide:** See `docs/GOOGLE_DRIVE_SETUP.md` for complete setup instructions.

## Migration from Replit Object Storage

### What Changed

**Before (Replit Object Storage):**
```python
from replit.object_storage import Client

storage_client = Client()
storage_client.upload("documents/file.docx", content)
file_data = storage_client.get("file.docx")
```

**After (Storage Abstraction Layer):**
```python
from modules.storage import get_storage_backend

storage = get_storage_backend()
storage.save("file.docx", content)
file_data = storage.get("file.docx")
```

### Migration Steps Completed

1. ✅ Created storage abstraction layer (`modules/storage/`)
2. ✅ Implemented local filesystem backend
3. ✅ Updated `document_generator.py` (line 21, 56-61, 245-290)
4. ✅ Updated `document_routes.py` (line 15, 27-32, 229-260)
5. ✅ Removed Replit imports from active codebase
6. ✅ Created `.env.example` with storage configuration
7. ✅ Updated documentation (CLAUDE.md, master-changelog.md)
8. ✅ Verified all tests passing

### Backward Compatibility

- Existing file paths in database remain valid
- Local storage directory structure maintained
- No breaking changes to API responses
- Fallback to local filesystem if storage backend unavailable

## Troubleshooting

### Common Issues

#### "Storage directory is not writable"
**Solution:** Check directory permissions
```bash
chmod 755 storage/generated_documents
```

#### "File not found" when downloading
**Solution:** Verify file was saved successfully
```python
storage = get_storage_backend()
files = storage.list()
print(files)
```

#### Import errors
**Solution:** Ensure storage module is in Python path
```python
import sys
sys.path.insert(0, '.')
from modules.storage import get_storage_backend
```

### Logging

Storage operations are logged at INFO level:
```
INFO: Local storage initialized at: /path/to/storage/generated_documents
INFO: File saved successfully: test.docx (12345 bytes) at /path/to/file
INFO: File retrieved successfully: test.docx (12345 bytes)
INFO: File deleted successfully: test.docx
```

## Future Enhancements

### Planned Features

1. **Advanced Features**
   - File versioning and history
   - Automatic backup and replication
   - CDN integration for downloads
   - Signed URLs for temporary access

2. **Performance Optimizations**
   - Caching layer for frequently accessed files
   - Lazy loading for large files
   - Streaming uploads/downloads
   - Connection pooling

3. **Migration Tools**
   - Data migration utilities between backends
   - Bulk transfer scripts
   - Storage usage analytics

## Testing

### Unit Tests

Located in `tests/test_storage_backend.py`:
- Filename validation
- Save/get/delete operations
- Path sanitization
- Error handling

### Integration Tests

Located in `tests/test_document_integration.py`:
- End-to-end document generation
- Storage backend integration
- API endpoint testing

### Manual Testing Checklist

- [ ] Generate document via API
- [ ] Download document via API
- [ ] Verify file saved to correct location
- [ ] Test with invalid filenames
- [ ] Test storage backend failover
- [ ] Verify logging output

## Support

For questions or issues with the storage system:
1. Check this documentation
2. Review logs for error messages
3. Verify environment configuration
4. Check file permissions
5. Consult troubleshooting section

## Version History

- **1.0** (October 6, 2025): Initial implementation
  - Local filesystem backend
  - Storage abstraction layer
  - Replit dependency removal
