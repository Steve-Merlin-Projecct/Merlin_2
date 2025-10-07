# PRD: Google Drive API Storage Backend Integration

**Version:** 1.0
**Created:** October 6, 2025
**Status:** Draft
**Owner:** Steve Glen

---

## Introduction/Overview

This PRD outlines the implementation of Google Drive API as a storage backend for the Merlin Job Application System. Currently, the system uses local filesystem storage for generated documents (resumes, cover letters). This feature will add Google Drive as a cloud storage option, allowing users to review and access generated documents directly from their Google Drive account.

**Problem Statement:** Generated documents are currently stored only on the local filesystem, making it difficult for users to review, share, or access files from different devices. Users need a cloud-based storage solution that integrates with familiar tools.

**Solution:** Implement a Google Drive storage backend that automatically uploads generated documents to a user's Google Drive account, organized by application version number, with private access and full traceability.

---

## Goals

1. **Cloud Storage Integration:** Implement Google Drive API v3 as a storage backend option alongside the existing local filesystem storage
2. **Version-Based Organization:** Automatically organize documents in Google Drive folders based on application version number (e.g., v4.1, v4.2)
3. **File Traceability:** Ensure all filenames include version and application identifiers for easy tracking
4. **Seamless Authentication:** Implement OAuth 2.0 authentication flow for secure, user-authorized access to Google Drive
5. **Database Tracking:** Store Google Drive file IDs and shareable links in the database for future reference
6. **Graceful Fallback:** Maintain local storage as automatic fallback if Google Drive is unavailable
7. **Zero Breaking Changes:** Maintain backward compatibility with existing storage abstraction layer

---

## User Stories

### US-1: Document Upload to Google Drive
**As a** job application system user,
**I want** my generated resumes and cover letters automatically uploaded to my Google Drive,
**So that** I can review and access them from any device without needing server access.

**Acceptance Criteria:**
- Documents are uploaded to Google Drive immediately after generation
- Files are organized in version-specific folders (e.g., `/Merlin Documents/v4.1/`)
- Filenames include application version (e.g., `merlin_v4.1_resume_2025_10_06_abc123.docx`)
- Upload completes within 5 seconds for typical document sizes (30-50KB)

### US-2: First-Time Google Drive Setup
**As a** new user setting up the system,
**I want** a simple OAuth flow to connect my Google Drive account,
**So that** I can authorize the application once and have all future documents automatically uploaded.

**Acceptance Criteria:**
- One-time browser-based OAuth 2.0 authentication flow
- Credentials stored securely and reused for subsequent uploads
- Clear error messages if authentication fails
- Ability to re-authenticate if credentials expire

### US-3: File Access and Review
**As a** user,
**I want** all my generated documents private and accessible only to me,
**So that** my job application materials remain confidential.

**Acceptance Criteria:**
- All files uploaded with private permissions (owner-only access)
- No public sharing links created automatically
- Files visible in user's Google Drive immediately after upload
- Folder structure matches application version

### US-4: Database File Tracking
**As a** system administrator,
**I want** Google Drive file IDs and links stored in the database,
**So that** I can track document locations and provide download links to users.

**Acceptance Criteria:**
- Database stores Google Drive file ID for each document
- Database stores shareable link (even if private)
- File metadata includes storage type ('google_drive')
- Existing local storage records remain unaffected

### US-5: Fallback to Local Storage
**As a** system,
**I want** to automatically fall back to local storage if Google Drive fails,
**So that** document generation is never interrupted by cloud service issues.

**Acceptance Criteria:**
- If Google Drive upload fails, save to local storage instead
- Log warning message indicating fallback occurred
- Storage type in response indicates 'local_fallback'
- User can retry upload to Google Drive manually later

---

## Functional Requirements

### FR-1: Google Drive Backend Implementation
1.1. Create `GoogleDriveStorageBackend` class implementing `StorageBackend` abstract interface
1.2. Support all required methods: `save()`, `get()`, `delete()`, `exists()`, `list()`
1.3. Use Google Drive API v3 Python client library (`google-api-python-client`)
1.4. Implement proper error handling for API failures (network, quota, authentication)

### FR-2: OAuth 2.0 Authentication
2.1. Implement OAuth 2.0 authorization flow using `google-auth-oauthlib`
2.2. Store credentials in `storage/google_drive_token.json` (gitignored)
2.3. Support credential refresh using refresh tokens
2.4. Require OAuth scopes: `https://www.googleapis.com/auth/drive.file` (app-created files only)
2.5. Handle token expiration and re-authentication gracefully

### FR-3: Folder Structure Management
3.1. Create root folder named "Merlin Documents" if it doesn't exist
3.2. Create version-specific subfolders based on `APP_VERSION` environment variable (e.g., "v4.1")
3.3. Check if folder exists before creating (avoid duplicates)
3.4. Store folder IDs in memory cache for performance
3.5. Folder structure: `/Merlin Documents/{version}/` (flat, no document-type subfolders)

### FR-4: File Naming Convention
4.1. Prepend application identifier and version to all filenames
4.2. Format: `merlin_v{version}_{original_filename}`
4.3. Example: `merlin_v4.1_resume_2025_10_06_abc123.docx`
4.4. Preserve original file extension
4.5. Ensure filename uniqueness (timestamp + UUID already in original names)

### FR-5: Upload Operations
5.1. Upload files using `files.create()` API method with media upload
5.2. Set file permissions to private (owner-only access)
5.3. Upload to version-specific folder automatically
5.4. Return metadata including: file_id, name, web_view_link, created_time
5.5. Handle files up to 50MB (cover typical document sizes with buffer)

### FR-6: Download Operations
6.1. Download files using `files.get_media()` API method with file ID
6.2. Support download by filename (search for file first, then download)
6.3. Return file content as bytes (matching StorageBackend interface)
6.4. Handle "file not found" errors gracefully

### FR-7: Database Integration
7.1. Add `google_drive_file_id` column to relevant document tables (VARCHAR 255)
7.2. Add `google_drive_link` column to store web view link (TEXT)
7.3. Update document generator to save Google Drive metadata after upload
7.4. Ensure backward compatibility (columns nullable, default NULL)

### FR-8: Configuration and Environment Variables
8.1. Add `STORAGE_BACKEND=google_drive` option to `.env.example`
8.2. Add `APP_VERSION` environment variable (e.g., `APP_VERSION=4.1`)
8.3. Add `GOOGLE_DRIVE_CREDENTIALS_PATH` for OAuth client secrets file
8.4. Add `GOOGLE_DRIVE_TOKEN_PATH` for storing authenticated tokens
8.5. Update storage factory to support Google Drive backend selection

### FR-9: Fallback Mechanism
9.1. Implement try-except wrapper around Google Drive operations
9.2. On failure, automatically call `LocalStorageBackend.save()`
9.3. Log warning with error details when fallback occurs
9.4. Return storage_type as 'local_fallback' in response metadata
9.5. Maintain same response structure for consistent API behavior

### FR-10: List and Search Operations
10.1. Implement `list()` method to query files in current version folder
10.2. Support filtering by prefix and pattern (matching StorageBackend interface)
10.3. Use Google Drive query syntax: `'folder_id' in parents and name contains 'pattern'`
10.4. Return list of filenames (not full metadata, for consistency)

---

## Non-Goals (Out of Scope)

1. **AWS S3 Support:** Remove all AWS S3 references from codebase and documentation. Google Drive is the only cloud storage option.
2. **File Migration:** No automatic migration of existing local files to Google Drive. Only new files are uploaded.
3. **Public File Sharing:** No automatic creation of public shareable links. All files remain private.
4. **Lifecycle Management:** No automatic deletion or archival of old files. All files are kept permanently.
5. **File Versioning:** No version history within Google Drive. Documents are created once and stored.
6. **Multi-User Support:** Single Google account authentication only (the account that runs OAuth flow).
7. **Google Workspace Integration:** No domain-wide delegation or service account support in initial version.
8. **Folder Permissions:** No custom folder sharing or team access controls.
9. **Advanced Search:** No full-text search or metadata-based filtering beyond basic filename patterns.

---

## Design Considerations

### Folder Structure
```
Google Drive Root
└── Merlin Documents/
    ├── v4.1/
    │   ├── merlin_v4.1_resume_2025_10_06_abc123.docx
    │   ├── merlin_v4.1_coverletter_2025_10_06_def456.docx
    │   └── ...
    ├── v4.2/
    │   ├── merlin_v4.2_resume_2025_11_15_xyz789.docx
    │   └── ...
    └── v5.0/
        └── ...
```

### File Naming Pattern
```
merlin_v{APP_VERSION}_{document_type}_{date}_{uuid}.{extension}

Examples:
- merlin_v4.1_resume_2025_10_06_abc123.docx
- merlin_v4.1_coverletter_2025_10_06_def456.docx
- merlin_v4.2_resume_2025_11_15_xyz789.docx
```

### OAuth Flow Diagram
```
1. User starts application
2. System checks for google_drive_token.json
3. If missing:
   a. Launch browser for OAuth consent
   b. User authorizes application
   c. Save credentials to google_drive_token.json
4. If present:
   a. Load credentials
   b. Check if expired
   c. Refresh if needed
5. Initialize Google Drive client
6. Ready for uploads
```

### API Response Format
```python
{
    "file_path": "1a2b3c4d5e6f7g8h9i",  # Google Drive file ID
    "filename": "merlin_v4.1_resume_2025_10_06_abc123.docx",
    "storage_type": "google_drive",
    "file_size": 36808,
    "timestamp": "2025-10-06T12:00:00",
    "google_drive_file_id": "1a2b3c4d5e6f7g8h9i",
    "google_drive_link": "https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i/view"
}
```

---

## Technical Considerations

### Dependencies
- **google-api-python-client** (v2.0+): Official Google API client library
- **google-auth-httplib2** (v0.1.0+): HTTP library for authentication
- **google-auth-oauthlib** (v1.0.0+): OAuth 2.0 flow implementation
- **google-auth** (v2.0+): Google authentication library

### OAuth 2.0 Setup Requirements
1. Create Google Cloud Project in Google Cloud Console
2. Enable Google Drive API for the project
3. Create OAuth 2.0 credentials (Desktop application type)
4. Download `credentials.json` file
5. Store in `storage/google_drive_credentials.json` (gitignored)

### Scopes Required
- `https://www.googleapis.com/auth/drive.file` - Access to files created by this app only

### Rate Limits
- Google Drive API: 1,000 requests per 100 seconds per user
- File upload size limit: 5TB (but we expect <1MB files)
- Consider implementing exponential backoff for rate limit errors

### Error Handling
Common errors to handle:
- `HttpError 401`: Authentication failed (re-authenticate)
- `HttpError 403`: Insufficient permissions (check scopes)
- `HttpError 404`: File/folder not found (create folder)
- `HttpError 429`: Rate limit exceeded (exponential backoff)
- `HttpError 500/503`: Google server error (retry with backoff)

### Performance Considerations
- Cache folder IDs to avoid repeated searches (in-memory dict)
- Reuse Drive API client instances (don't create new client per request)
- Use resumable uploads for files >5MB (if needed in future)
- Implement connection pooling via httplib2

### Security Considerations
- Store `credentials.json` and `token.json` in gitignored `storage/` directory
- Never commit OAuth tokens to version control
- Use minimal OAuth scopes (drive.file, not drive.full)
- Encrypt tokens at rest if storing in database (future enhancement)
- Validate all filenames to prevent injection attacks

---

## Success Metrics

1. **Upload Success Rate:** ≥99% of document uploads succeed on first attempt
2. **Upload Performance:** Average upload time <3 seconds for typical documents (30-50KB)
3. **Authentication Success:** OAuth flow completes successfully for ≥95% of users on first attempt
4. **Fallback Usage:** <5% of uploads fall back to local storage (indicates high Google Drive reliability)
5. **Database Tracking:** 100% of Google Drive uploads have file_id and link stored in database
6. **Zero Breaking Changes:** Existing local storage functionality remains 100% operational

---

## Open Questions

1. **Q:** Should we provide a UI or admin panel to view Google Drive upload status?
   - **Decision Needed By:** Before implementation starts

2. **Q:** Should we implement a manual "retry upload to Google Drive" function for failed uploads?
   - **Decision Needed By:** During implementation

3. **Q:** What happens if user revokes OAuth access after initial authorization?
   - **Proposed Answer:** System falls back to local storage and logs error requiring re-authentication

4. **Q:** Should version number format be validated (e.g., must match X.Y pattern)?
   - **Proposed Answer:** Yes, validate against regex `^\d+\.\d+$` and fail startup if invalid

5. **Q:** How to handle the transition when APP_VERSION changes (e.g., from 4.1 to 4.2)?
   - **Proposed Answer:** System automatically creates new version folder on first upload with new version

6. **Q:** Should we support multiple Google accounts or always use the first authenticated account?
   - **Proposed Answer:** Single account only for v1, multi-account support deferred to future version

7. **Q:** What if Google Drive quota is exceeded?
   - **Proposed Answer:** Upload fails, falls back to local storage, user notification logged

---

## Implementation Phases

### Phase 1: Research and Setup (Complete)
- ✅ Research Google Drive API v3
- ✅ Compare GCS vs Google Drive
- ✅ Create PRD

### Phase 2: Foundation (Week 1)
- Create `GoogleDriveStorageBackend` class skeleton
- Implement OAuth 2.0 authentication flow
- Create folder management functions
- Add environment variables and configuration

### Phase 3: Core Functionality (Week 2)
- Implement `save()` method with upload logic
- Implement `get()` method with download logic
- Implement `delete()`, `exists()`, `list()` methods
- Add filename formatting and version handling

### Phase 4: Integration (Week 3)
- Update storage factory to support Google Drive
- Integrate with document generator
- Add database schema changes for file tracking
- Implement fallback mechanism

### Phase 5: Testing and Documentation (Week 4)
- Unit tests for all Google Drive operations
- Integration tests with document generation
- Update documentation (README, architecture docs)
- Create setup guide for OAuth configuration

### Phase 6: Deployment Preparation (Week 5)
- Remove AWS references from codebase
- Update .env.example with Google Drive settings
- Create deployment scripts and guides
- Final verification and QA

---

## Appendix: AWS Removal Checklist

As part of this PRD, all AWS S3 references will be removed:

### Files to Update:
- [ ] `docs/storage-architecture.md` - Remove AWS S3 sections
- [ ] `.env.example` - Remove S3 configuration examples
- [ ] `modules/storage/storage_factory.py` - Remove S3 backend option
- [ ] `CLAUDE.md` - Remove AWS from External Dependencies
- [ ] All documentation mentioning "future AWS support"

### Verification:
- [ ] Grep for "s3" or "aws" in codebase (should return no results)
- [ ] Update future roadmap to show only Google Drive as cloud option
- [ ] Update migration documentation to reflect Google Drive as primary cloud storage

---

**Document Version:** 1.0
**Created:** October 6, 2025
**Last Updated:** October 6, 2025
**Status:** Ready for Review
**Next Steps:** Review and approval, then proceed to task generation
