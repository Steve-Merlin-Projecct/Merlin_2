---
title: 'Tasks: Remove Replit-Specific Code and Dependencies'
created: '2025-10-07'
updated: '2025-10-07'
author: Steve-Merlin-Projecct
type: prd
status: archived
tags:
- tasks
- remove
- replit
- code
---

# Tasks: Remove Replit-Specific Code and Dependencies

Based on Product Requirements Document: `prd-remove-replit-code.md`

## Relevant Files

### Active Production Files (CRITICAL - Must be updated)
- `modules/content/document_generation/document_generator.py` - Uses `replit.object_storage.Client` for uploads
- `modules/document_routes.py` - Uses `replit.object_storage.Client` for downloads
- `requirements.txt` - Missing `replit-object-storage` dependency (causes import errors)

### Supporting Files
- `modules/content/document_generation/template_engine.py` - Saves documents to local `storage/` directory
- `modules/content/document_generation/template_converter.py` - Saves converted templates
- `modules/content/document_generation/csv_content_mapper.py` - Saves CSV-mapped documents
- `modules/email_integration/gmail_oauth_official.py` - Uses `storage/` for OAuth credentials
- `modules/email_integration/gmail_enhancements.py` - Uses `storage/logs/` for error logs

### Documentation Files
- `CLAUDE.md` - References Replit Object Storage in architecture section
- `docs/architecture/PROJECT_ARCHITECTURE.md` - May contain Replit references
- `docs/component_docs/document_generation/document_generation_architecture.md` - Documents storage system
- `.env.example` - Needs storage configuration examples

### Archived Files (LOW PRIORITY - Historical reference only)
- `archived_files/scripts/services/makecom-document-generator.py`
- `archived_files/scripts/services/webhook_handler_original.py`
- `archived_files/scripts/services/base_generator.py`
- `archived_files/scripts/services/webhook_handler.py`
- `archived_files/scripts/services/resume_generator2.py`
- `archived_files/scripts/services/webhook_handler_2.py`
- `archived_files/scripts/services/resume_generator_original.py`

## Current Storage Architecture

### Storage Locations
- **Cloud**: Replit Object Storage with key pattern `documents/{filename}`
- **Local Fallback**: `storage/` directory (root level)
  - `storage/gmail_credentials.json` - OAuth credentials
  - `storage/gmail_token.json` - OAuth tokens
  - `storage/logs/gmail_errors.log` - Error logs
  - `storage/*.docx` - Generated documents (3 test files currently)

### Storage Operations
- **Upload**: `storage_client.upload(object_key, file_content)` → Save to cloud
- **Download**: `storage_client.get(filename)` → Retrieve from cloud
- **Fallback**: If cloud fails, use local filesystem

## Tasks

### Phase 1: Design and Planning
- [ ] 1.0 Storage Architecture Design
  - [ ] 1.1 Design storage abstraction layer interface:
    - [ ] 1.1.1 Define `StorageBackend` abstract base class with methods: `save()`, `get()`, `delete()`, `exists()`
    - [ ] 1.1.2 Plan interface signatures to match current Replit usage patterns
    - [ ] 1.1.3 Design error handling and fallback mechanisms
    - [ ] 1.1.4 Document interface in module docstring

  - [ ] 1.2 Design local filesystem storage implementation:
    - [ ] 1.2.1 Plan directory structure: `/storage/generated_documents/{document_type}/`
    - [ ] 1.2.2 Define file naming conventions (maintain current timestamp + UUID pattern)
    - [ ] 1.2.3 Design path resolution for relative vs absolute paths
    - [ ] 1.2.4 Plan file cleanup/rotation policy (currently 24 hours in `document_generator.py:292`)

  - [ ] 1.3 Design configuration system:
    - [ ] 1.3.1 Define environment variables: `STORAGE_BACKEND`, `LOCAL_STORAGE_PATH`
    - [ ] 1.3.2 Create configuration loader with defaults
    - [ ] 1.3.3 Plan validation for storage paths and permissions
    - [ ] 1.3.4 Design future cloud storage configuration structure (S3, GCS)

### Phase 2: Implementation - Storage Abstraction Layer
- [ ] 2.0 Create Storage Module
  - [ ] 2.1 Create base storage module:
    - [ ] 2.1.1 Create new file: `modules/storage/storage_backend.py`
    - [ ] 2.1.2 Implement `StorageBackend` abstract base class using Python ABC
    - [ ] 2.1.3 Define abstract methods: `save()`, `get()`, `delete()`, `exists()`, `list()`
    - [ ] 2.1.4 Add comprehensive docstrings with usage examples

  - [ ] 2.2 Implement local filesystem backend:
    - [ ] 2.2.1 Create `modules/storage/local_storage.py`
    - [ ] 2.2.2 Implement `LocalStorageBackend` class extending `StorageBackend`
    - [ ] 2.2.3 Implement `save()`: Write bytes to local file with error handling
    - [ ] 2.2.4 Implement `get()`: Read bytes from local file with validation
    - [ ] 2.2.5 Implement `delete()`: Remove file with existence check
    - [ ] 2.2.6 Implement `exists()`: Check file presence
    - [ ] 2.2.7 Implement `list()`: List files in directory with pattern matching
    - [ ] 2.2.8 Add automatic directory creation with proper permissions
    - [ ] 2.2.9 Add file path sanitization to prevent path traversal attacks

  - [ ] 2.3 Create storage factory and configuration:
    - [ ] 2.3.1 Create `modules/storage/storage_factory.py`
    - [ ] 2.3.2 Implement `get_storage_backend()` factory function
    - [ ] 2.3.3 Add environment-based backend selection
    - [ ] 2.3.4 Implement singleton pattern for storage instances
    - [ ] 2.3.5 Add logging for storage initialization and operations

  - [ ] 2.4 Add storage module initialization:
    - [ ] 2.4.1 Create `modules/storage/__init__.py`
    - [ ] 2.4.2 Export `StorageBackend`, `LocalStorageBackend`, `get_storage_backend()`
    - [ ] 2.4.3 Add module-level documentation

### Phase 3: Code Migration - Document Generation System
- [ ] 3.0 Update Document Generator Module
  - [ ] 3.1 Update `modules/content/document_generation/document_generator.py`:
    - [ ] 3.1.1 Remove import: `from replit.object_storage import Client` (line 21)
    - [ ] 3.1.2 Add import: `from modules.storage import get_storage_backend`
    - [ ] 3.1.3 Replace `self.storage_client = Client()` with `self.storage_client = get_storage_backend()` (lines 56-61)
    - [ ] 3.1.4 Update `upload_to_storage()` method (lines 245-290):
      - [ ] 3.1.4.1 Replace `self.storage_client.upload(object_key, file_content)` with `self.storage_client.save(filename, file_content)`
      - [ ] 3.1.4.2 Update object_key pattern from `documents/{filename}` to just `{filename}` (backend handles paths)
      - [ ] 3.1.4.3 Update return dictionary to include new storage metadata
      - [ ] 3.1.4.4 Maintain backward compatibility with existing file path references
    - [ ] 3.1.5 Test document upload with new storage backend
    - [ ] 3.1.6 Verify error handling and fallback logic still works

  - [ ] 3.2 Update `modules/document_routes.py`:
    - [ ] 3.2.1 Remove import: `from replit.object_storage import Client` (line 15)
    - [ ] 3.2.2 Add import: `from modules.storage import get_storage_backend`
    - [ ] 3.2.3 Replace `storage_client = Client()` with `storage_client = get_storage_backend()` (lines 27-32)
    - [ ] 3.2.4 Update `download_file()` function (lines 211-270):
      - [ ] 3.2.4.1 Replace `storage_client.get(filename)` with new backend call
      - [ ] 3.2.4.2 Update error handling for new storage exceptions
      - [ ] 3.2.4.3 Maintain content-type detection logic
      - [ ] 3.2.4.4 Keep security validation for filename (path traversal protection)
    - [ ] 3.2.5 Test document download from storage
    - [ ] 3.2.6 Verify Response headers are correct (Content-Disposition, Content-Length)

### Phase 4: Environment Configuration
- [ ] 4.0 Configuration and Environment Setup
  - [ ] 4.1 Update environment configuration:
    - [ ] 4.1.1 Add to `.env` file:
      ```
      # Storage Configuration
      STORAGE_BACKEND=local
      LOCAL_STORAGE_PATH=./storage/generated_documents
      ```
    - [ ] 4.1.2 Create `.env.example` with storage configuration template
    - [ ] 4.1.3 Document all storage-related environment variables
    - [ ] 4.1.4 Add validation for storage path existence and permissions

  - [ ] 4.2 Update dependency files:
    - [ ] 4.2.1 Verify `requirements.txt` does NOT include `replit-object-storage`
    - [ ] 4.2.2 Check `pyproject.toml` for any Replit dependencies (if exists)
    - [ ] 4.2.3 Update `uv.lock` if using uv package manager
    - [ ] 4.2.4 Run `pip install -r requirements.txt` to verify no missing dependencies

### Phase 5: Testing and Validation
- [ ] 5.0 Comprehensive Testing
  - [ ] 5.1 Unit tests for storage abstraction:
    - [ ] 5.1.1 Create `tests/test_storage_backend.py`
    - [ ] 5.1.2 Test `LocalStorageBackend.save()` - successful save and error cases
    - [ ] 5.1.3 Test `LocalStorageBackend.get()` - retrieve existing and missing files
    - [ ] 5.1.4 Test `LocalStorageBackend.delete()` - delete existing files
    - [ ] 5.1.5 Test `LocalStorageBackend.exists()` - check file presence
    - [ ] 5.1.6 Test path sanitization prevents directory traversal
    - [ ] 5.1.7 Test automatic directory creation

  - [ ] 5.2 Integration tests for document generation:
    - [ ] 5.2.1 Test resume generation end-to-end (POST /resume)
    - [ ] 5.2.2 Test cover letter generation end-to-end (POST /cover-letter)
    - [ ] 5.2.3 Test document download (GET /download/<filename>)
    - [ ] 5.2.4 Test file storage in correct directory structure
    - [ ] 5.2.5 Verify file naming follows expected pattern
    - [ ] 5.2.6 Test error handling when storage is unavailable

  - [ ] 5.3 Manual testing checklist:
    - [ ] 5.3.1 Generate resume via API and verify file saved locally
    - [ ] 5.3.2 Download generated resume and verify content
    - [ ] 5.3.3 Generate cover letter and verify storage
    - [ ] 5.3.4 Check storage directory structure matches design
    - [ ] 5.3.5 Verify no Replit-related errors in logs
    - [ ] 5.3.6 Test with missing STORAGE_BACKEND env var (should default to local)

  - [ ] 5.4 Import verification:
    - [ ] 5.4.1 Run: `grep -r "from replit" --include="*.py" .` → Should return 0 results in active code
    - [ ] 5.4.2 Run: `grep -r "import replit" --include="*.py" .` → Should return 0 results in active code
    - [ ] 5.4.3 Run: `python -m py_compile modules/content/document_generation/document_generator.py` → No syntax errors
    - [ ] 5.4.4 Run: `python -m py_compile modules/document_routes.py` → No syntax errors
    - [ ] 5.4.5 Start Flask application and check for ImportError exceptions

### Phase 6: Documentation Updates
- [ ] 6.0 Update Project Documentation
  - [ ] 6.1 Update `CLAUDE.md`:
    - [ ] 6.1.1 Remove "Replit Object Storage" from System Architecture section
    - [ ] 6.1.2 Update "Cloud Storage" bullet to "File Storage with local filesystem and cloud support"
    - [ ] 6.1.3 Remove "Google Cloud: Underlying infrastructure for Replit Object Storage" from dependencies
    - [ ] 6.1.4 Add new storage abstraction layer to architecture description
    - [ ] 6.1.5 Update version number in header (increment minor version)

  - [ ] 6.2 Update technical documentation:
    - [ ] 6.2.1 Create `docs/storage/storage-architecture.md` documenting new storage system
    - [ ] 6.2.2 Update `docs/component_docs/document_generation/document_generation_architecture.md`
    - [ ] 6.2.3 Document storage configuration options and environment variables
    - [ ] 6.2.4 Add migration guide for future cloud storage backends (S3, GCS)
    - [ ] 6.2.5 Document local storage directory structure and file organization

  - [ ] 6.3 Update setup and deployment guides:
    - [ ] 6.3.1 Create "Local Storage Setup" section in setup documentation
    - [ ] 6.3.2 Document required directory permissions
    - [ ] 6.3.3 Add troubleshooting section for storage-related issues
    - [ ] 6.3.4 Update deployment checklist to include storage configuration

  - [ ] 6.4 Update changelog:
    - [ ] 6.4.1 Add entry to `docs/changelogs/master-changelog.md`:
      ```
      - October 06, 2025. Removed Replit dependencies and implemented storage abstraction layer
        * Removed replit-object-storage dependency
        * Created modular StorageBackend system with local filesystem implementation
        * Migrated document generation and download to new storage abstraction
        * Updated all documentation to remove Replit references
        * Maintained backward compatibility with existing file paths
      ```
    - [ ] 6.4.2 Document breaking changes (if any)
    - [ ] 6.4.3 Add migration notes for developers

### Phase 7: Cleanup and Archival
- [ ] 7.0 Code Cleanup
  - [ ] 7.1 Clean up archived files:
    - [ ] 7.1.1 Add comment header to archived files noting they contain obsolete Replit code
    - [ ] 7.1.2 Move to `archived_files/replit_migration/` subdirectory for clear separation
    - [ ] 7.1.3 Create `archived_files/replit_migration/README.md` explaining archival reason

  - [ ] 7.2 Search and remove Replit comments:
    - [ ] 7.2.1 Search for "replit" in comments (case-insensitive): `grep -ri "replit" --include="*.py" . | grep "#"`
    - [ ] 7.2.2 Update or remove obsolete comments referencing Replit
    - [ ] 7.2.3 Replace with generic "cloud storage" or "file storage" terminology

  - [ ] 7.3 Update code quality tools:
    - [ ] 7.3.1 Run Black formatter on modified files
    - [ ] 7.3.2 Run Flake8 linter and fix any issues
    - [ ] 7.3.3 Run Vulture to check for dead code
    - [ ] 7.3.4 Update `.flake8` or `.pylintrc` if needed

### Phase 8: Production Deployment Preparation
- [ ] 8.0 Deployment Readiness
  - [ ] 8.1 Pre-deployment checklist:
    - [ ] 8.1.1 All tests passing (unit + integration)
    - [ ] 8.1.2 No Replit imports in active codebase
    - [ ] 8.1.3 Documentation updated and reviewed
    - [ ] 8.1.4 Environment variables documented
    - [ ] 8.1.5 Storage directories created with correct permissions

  - [ ] 8.2 Create deployment script:
    - [ ] 8.2.1 Create `scripts/setup_storage.sh` to initialize storage directories
    - [ ] 8.2.2 Add permission checks and directory creation
    - [ ] 8.2.3 Add validation for environment variables
    - [ ] 8.2.4 Include in deployment documentation

  - [ ] 8.3 Backup and rollback plan:
    - [ ] 8.3.1 Document current storage state (files and locations)
    - [ ] 8.3.2 Create rollback procedure if deployment fails
    - [ ] 8.3.3 Test rollback in development environment
    - [ ] 8.3.4 Prepare communication plan for stakeholders

### Phase 9: Future Enhancement Planning (Out of Scope for Initial Release)
- [ ] 9.0 Future Cloud Storage Support

  - [ ] 9.2 Google Cloud Storage backend implementation

  - [ ] 9.4 Storage migration utilities between backends
  - [ ] 9.5 Performance optimization and caching layer

---

## Success Criteria

✅ **Zero Replit imports** - No `from replit` or `import replit` in active codebase
✅ **All tests pass** - Unit and integration tests complete successfully
✅ **Clean dependency installation** - `pip install -r requirements.txt` succeeds without errors
✅ **Documentation complete** - All docs updated, setup guide includes storage config
✅ **Storage abstraction working** - Documents save and retrieve successfully
✅ **No breaking changes** - Existing functionality maintained
✅ **Code quality checks pass** - Black, Flake8, Vulture all pass

## Priority Levels

**P0 (Critical)**: Phase 2, 3, 5.1-5.4 - Core functionality replacement
**P1 (High)**: Phase 1, 4, 6 - Design, configuration, documentation
**P2 (Medium)**: Phase 7, 8 - Cleanup and deployment prep
**P3 (Low)**: Phase 9 - Future enhancements

## Estimated Timeline

- **Phase 1**: 2-3 hours (design and planning)
- **Phase 2**: 4-6 hours (storage abstraction implementation)
- **Phase 3**: 3-4 hours (code migration)
- **Phase 4**: 1-2 hours (configuration)
- **Phase 5**: 4-6 hours (testing)
- **Phase 6**: 3-4 hours (documentation)
- **Phase 7**: 2-3 hours (cleanup)
- **Phase 8**: 2-3 hours (deployment prep)

**Total Estimated Time**: 21-31 hours

---

**Document Version:** 1.0
**Created:** 2025-10-06
**Based on PRD:** prd-remove-replit-code.md
**Status:** Ready for Implementation
**Owner:** Steve Glen
