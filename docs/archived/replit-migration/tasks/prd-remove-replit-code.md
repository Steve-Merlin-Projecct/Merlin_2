# PRD: Remove Replit-Specific Code and Dependencies

## Introduction/Overview

The Merlin Job Application System was originally developed on the Replit platform and has been migrated to a standalone development environment with GitHub hosting. However, the codebase still contains Replit-specific code, imports, and dependencies that are no longer needed and may cause errors or confusion in the new environment.

This PRD outlines the systematic removal of all Replit-specific code while maintaining full application functionality. The goal is to create a clean, portable codebase that can run in any standard Python environment without Replit dependencies.

## Goals

1. Remove all Replit-specific import statements and dependencies from Python code
2. Replace Replit Object Storage with a local or cloud-agnostic file storage solution
3. Clean up any remaining Replit configuration files
4. Update all documentation to remove Replit references
5. Ensure the application runs successfully without any Replit dependencies
6. Maintain backward compatibility with existing database and file structures

## User Stories

1. **As a developer**, I want to run the application locally without Replit dependencies, so that I can develop and test features in my preferred environment.

2. **As a developer**, I want clear documentation on file storage configuration, so that I can easily switch between local and cloud storage providers.

3. **As a system administrator**, I want the codebase to be platform-agnostic, so that I can deploy to any hosting provider (Digital Ocean, AWS, etc.) without code changes.

4. **As a maintainer**, I want clean code without obsolete imports, so that the codebase is easier to understand and maintain.

## Functional Requirements

### 1. Code Analysis and Identification
1.1. Scan all Python files for `from replit` or `import replit` statements
1.2. Identify all modules using `replit.object_storage.Client`
1.3. Document all files that need modification
1.4. Create a comprehensive list of affected functionality

### 2. Storage Abstraction Layer
2.1. Create a new storage abstraction module that supports multiple backends:
   - Local filesystem storage
   - Future support for cloud providers (AWS S3, Google Cloud Storage, etc.)
2.2. Implement a configuration-based storage selection mechanism
2.3. Ensure the abstraction layer provides the same interface as current Replit storage usage

### 3. Code Replacement
3.1. Replace all `replit.object_storage.Client` usage with the new storage abstraction
3.2. Update the following modules (identified during cleanup):
   - `modules/content/document_generation/document_generator.py`
   - `modules/document_routes.py`
   - Any other modules using Replit storage
3.3. Remove all `from replit import` statements
3.4. Update import statements to use the new storage module

### 4. Configuration Updates
4.1. Add storage configuration to environment variables
4.2. Create `.env.example` file with storage configuration examples
4.3. Update secrets documentation to include storage configuration
4.4. Ensure default behavior uses local filesystem storage

### 5. Dependency Management
5.1. Remove `replit-object-storage` from `pyproject.toml` (already completed)
5.2. Verify no other Replit-specific dependencies remain
5.3. Update lock files if applicable

### 6. Testing and Validation
6.1. Test document generation with local file storage
6.2. Test document download endpoints
6.3. Verify all file upload/download functionality works
6.4. Ensure no runtime errors related to Replit imports

### 7. Documentation Updates
7.1. Update `claude.md` to remove Replit references in architecture section
7.2. Update component documentation for document generation
7.3. Add setup instructions for local file storage
7.4. Document how to configure alternative storage backends

### 8. Cleanup
8.1. Search for and remove any remaining Replit-specific comments
8.2. Update changelog with Replit removal notes
8.3. Archive Replit-specific documentation for historical reference

## Non-Goals (Out of Scope)

1. **Cloud storage implementation** - Initial implementation will focus on local filesystem. Cloud storage support (S3, GCS) will be added in a future iteration.
2. **Migration of existing stored files** - This PRD focuses on code changes only. Data migration is a separate concern.
3. **Performance optimization** - Storage performance improvements are out of scope for this cleanup.
4. **Alternative document storage formats** - The current document storage structure will be maintained.

## Design Considerations

### Storage Abstraction Interface
```python
# Proposed interface
class StorageBackend:
    def save(self, filename: str, content: bytes) -> str:
        """Save file and return path/URL"""
        pass

    def get(self, filename: str) -> bytes:
        """Retrieve file content"""
        pass

    def delete(self, filename: str) -> bool:
        """Delete file"""
        pass

    def exists(self, filename: str) -> bool:
        """Check if file exists"""
        pass
```

### Directory Structure for Local Storage
```
/storage/
  /generated_documents/
    /resumes/
    /cover_letters/
```

## Technical Considerations

### Dependencies to Add
- No additional dependencies required for local filesystem storage
- Future cloud storage will require provider-specific SDKs (boto3 for AWS, google-cloud-storage for GCP)

### Affected Modules
Based on earlier grep results:
- `modules/content/document_generation/document_generator.py`
- `modules/document_routes.py`
- `database_tools/generated/models.py` (if it has references)
- `database_tools/generated/schemas.py` (if it has references)

### Configuration Variables
Add to `.env`:
```bash
# Storage Configuration
STORAGE_BACKEND=local  # Options: local, s3, gcs
LOCAL_STORAGE_PATH=/path/to/storage
# Future: S3_BUCKET_NAME, GCS_BUCKET_NAME, etc.
```

### Backward Compatibility
- Existing file paths in the database should remain valid
- Migration script may be needed if file path format changes

## Success Metrics

1. **Zero Replit imports** - No `from replit` or `import replit` statements remain in codebase
2. **All tests pass** - Existing functionality works without errors
3. **Clean dependency list** - `pip install` succeeds without Replit packages
4. **Documentation complete** - Setup guide includes local storage configuration
5. **Code review approval** - Changes reviewed and validated

## Open Questions

1. Should we implement a migration utility to move existing Replit-stored files to local storage?
2. What is the preferred local storage location? (relative path vs. absolute path)
3. Should we add file size limits for local storage?
4. Do we need to maintain compatibility with any existing Replit deployments, or is this a complete migration?
5. Should we add file cleanup/rotation policies for local storage?

---

**Document Version:** 1.0
**Created:** 2025-10-06
**Status:** Draft
**Owner:** Steve Glen
