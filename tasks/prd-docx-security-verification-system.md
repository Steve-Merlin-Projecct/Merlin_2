# Product Requirements Document: DOCX Security Verification System

**Version:** 1.0
**Date:** October 9, 2025
**Status:** Draft
**Author:** Automated Job Application System Team

---

## 1. Introduction/Overview

### Problem Statement
The Automated Job Application System generates personalized Word documents (.docx files) for resumes and cover letters. These generated documents must pass through multiple security verification systems including:
- Applicant Tracking Systems (ATS)
- Email platforms (Gmail, Outlook/Exchange Online)
- Cloud storage services (Google Drive, SharePoint, Microsoft Teams)
- Enterprise security tools (antivirus, malware scanners)

Currently, there is no verification mechanism to ensure generated documents will pass these security checks. A malware false-positive or structural corruption could result in rejected applications, blocked emails, or quarantined files.

### Goal
Implement a comprehensive DOCX security verification system that validates generated documents against industry-standard security checks, ensuring they are structurally sound, malware-free, and will successfully pass through common enterprise security platforms.

---

## 2. Goals

1. **Prevent False Positives**: Ensure generated DOCX files do not trigger malware detection false positives in major security platforms
2. **Structural Integrity**: Validate DOCX file structure conforms to Office Open XML (OOXML) standards
3. **Security Best Practices**: Implement document generation practices that align with security scanning expectations
4. **Verification Automation**: Provide automated pre-delivery verification for all generated documents
5. **Actionable Feedback**: Generate detailed verification reports identifying specific issues and remediation steps
6. **Platform Compatibility**: Ensure documents pass verification on Microsoft 365, Google Workspace, and major ATS platforms

---

## 3. Research Findings: How Platforms Scan DOCX Files

### 3.1 Email Platforms

#### Microsoft Outlook / Exchange Online (Microsoft Defender for Office 365)
- **Multi-layered scanning**: All attachments scanned by anti-malware protection with real-time threat response
- **Safe Attachments feature**: Detonates files in virtual sandbox environment (behavioral analysis)
- **Signature-based detection**: Uses Microsoft Defender for Endpoint with frequently updated signatures
- **Timeline**: Scanning typically completes within 15 minutes
- **Action on detection**: Files blocked so no one can open them
- **No exemptions**: No user or admin setting can bypass scanning

**Key Implications:**
- Documents must not contain executable content or suspicious embedded objects
- File structure must be valid to prevent sandbox errors
- Metadata should appear authentic to avoid heuristic flags

#### Gmail / Google Workspace
- **Automatic scanning**: All attachments scanned for viruses
- **File size limit**: Scans files under 100 MB
- **Scan timing**: Pre-download and pre-share scanning
- **AI-powered ransomware detection**: Specialized AI model trained on millions of ransomware samples
- **VirusTotal integration**: Leverages threat intelligence from VirusTotal
- **Action on detection**: Prevents download, sharing, or email sending

**Key Implications:**
- File modifications should not resemble ransomware encryption patterns
- Files must pass VirusTotal's multi-engine scanning
- Metadata timestamps should be realistic

### 3.2 Cloud Storage Platforms

#### Microsoft SharePoint / Teams
- **Built-in virus protection**: Common virus detection engine across SharePoint, OneDrive, Teams
- **Dual-engine scanning**:
  1. Microsoft Defender for Office 365 (sandbox detonation)
  2. Microsoft Defender for Endpoint (signature-based)
- **Scan timing**: Asynchronous after upload + on-demand before download
- **Safe Attachments**: Virtual environment testing (detonation) by default
- **Action on detection**: File property marked as infected, blocked from opening

**Key Implications:**
- Documents undergo behavioral analysis in virtual machines
- Any embedded automation must be benign
- File structure must survive detonation testing

#### Google Drive
- **Virus scanning**: Automatic for files under 100 MB
- **Pre-action scanning**: Scans before download and sharing
- **Ransomware detection**: AI model monitors file changes for malicious modification patterns
- **Sync protection**: Drive for desktop pauses syncing if ransomware detected
- **Integration**: Uses Drive, Gmail, and Chrome detection ecosystem

**Key Implications:**
- File modifications should follow predictable patterns
- Rapid bulk modifications may trigger ransomware alerts
- Metadata should show authentic creation/modification patterns

### 3.3 Applicant Tracking Systems (ATS)

**Current State:**
- **Limited malware scanning**: ATS platforms primarily focus on content parsing, not security
- **Third-party dependency**: Security scanning typically handled by enterprise infrastructure (email gateways, firewalls)
- **Format preferences**: Many ATS systems prefer DOCX over PDF for parsing accuracy
- **File validation**: Basic validation to ensure file can be parsed

**Key Implications:**
- Documents must be structurally valid for successful parsing
- While ATS may not scan directly, documents must pass through email/storage scanning first
- File corruption could result in parsing failures and rejected applications

### 3.4 Enterprise Security Tools

#### OOXML Malware Detection Techniques

**Common Attack Vectors:**
1. **VBA Macros**: Embedded malicious VBA code that executes on "Enable Content"
2. **Remote Template Injection**: DOCX loads malicious template from remote URL
3. **Embedded HTML/Framesets**: HTML elements exploited for malicious payloads
4. **OLE Objects**: Embedded objects containing malware
5. **External References**: Malicious URLs in embedded videos or links

**Detection Methods:**
- **Structure Analysis**: OOXML files are ZIP archives - can be decompressed and analyzed
- **Oletools**: Extracts and analyzes VBA macros, embedded objects, external links
- **YARA Rules**: Pattern matching for known malicious structures
- **ClamAV**: Signature-based detection with OOXML decompression support
- **VirusTotal API**: Multi-engine scanning (70+ antivirus products, 10+ sandboxes)

**File Structure Validation:**
- ZIP integrity checks (CRC validation)
- Required XML files presence: `[Content_Types].xml` in root
- Magic number verification: `50 4B 03 04` (ZIP header)
- Metadata consistency checks

**Macro Detection Best Practices:**
- **File extensions**: Macro-enabled files use `.docm`, `.dotm`, `.xlsm`, `.pptm`
- **Standard DOCX**: Cannot contain macros by default
- **VBA detection**: Check for `word/vbaProject.bin` in decompressed archive
- **Auto-execution triggers**: Scan for `AutoOpen`, `AutoExec`, `Document_Open` functions

---

## 4. User Stories

**US-1: As a job applicant**, I want my generated resume to pass through Gmail's virus scanner, so that my application email is successfully delivered to the hiring manager.

**US-2: As a system administrator**, I want to receive a verification report before documents are sent, so that I can identify and fix issues before they cause delivery failures.

**US-3: As a developer**, I want automated verification integrated into the document generation workflow, so that every generated document is validated without manual intervention.

**US-4: As a job applicant**, I want my resume to pass SharePoint's Safe Attachments scanning when uploaded to a company portal, so that my application is not blocked as malicious.

**US-5: As a security analyst**, I want to understand why a document was flagged, so that I can adjust the generation process to prevent future false positives.

---

## 5. Functional Requirements

### 5.1 Core Verification Engine

**FR-1**: The system MUST validate DOCX file structure integrity by:
- Verifying ZIP archive integrity (CRC checks, compression validity)
- Confirming presence of required OOXML files (`[Content_Types].xml`, `word/document.xml`)
- Validating XML well-formedness in all component files
- Checking ZIP magic number (`50 4B 03 04`)

**FR-2**: The system MUST scan for macro-enabled content by:
- Checking file extension (reject `.docm`, `.dotm` - only standard `.docx` allowed)
- Decompressing ZIP and verifying absence of `word/vbaProject.bin`
- Scanning for VBA-related XML elements in document structure

**FR-3**: The system MUST detect suspicious embedded content:
- Identify OLE objects within the document
- Extract and validate external references (URLs, template links)
- Scan for embedded HTML/framesets
- Flag executable content or scripts

**FR-4**: The system MUST validate document metadata for authenticity:
- Check for realistic creation/modification timestamps (not default values)
- Verify author and company information is set
- Validate document properties are complete
- Ensure editing time is within reasonable bounds (0.5 - 10 hours)

**FR-5**: The system MUST integrate with external malware detection services:
- **VirusTotal API**: Submit files for multi-engine scanning (optional, configurable)
- **ClamAV**: Local signature-based scanning (if available)
- **YARA Rules**: Apply custom detection rules for OOXML threats

**FR-6**: The system MUST perform content-based validation:
- Verify all template variables are replaced (no `<<variable>>` or `{placeholder}` remaining)
- Check for suspicious strings or patterns
- Validate character encoding consistency
- Ensure no corrupted or malformed XML tags

### 5.2 Verification Reporting

**FR-7**: The system MUST generate a structured verification report including:
- Overall pass/fail status
- Individual check results (structure, macros, embedded content, metadata, external scans)
- Risk severity levels (critical, high, medium, low, info)
- Actionable remediation steps for failures
- Scan timestamp and document hash (SHA-256)

**FR-8**: The system MUST support multiple output formats for reports:
- JSON (machine-readable for API integration)
- Markdown (human-readable for logs)
- Database records (for historical tracking)

**FR-9**: The system MUST log all verification activities:
- Document ID, filename, file size
- Verification timestamp
- All checks performed and results
- External service responses (VirusTotal, ClamAV)
- Decision: approved, rejected, needs review

### 5.3 Integration Points

**FR-10**: The system MUST integrate with the document generation workflow:
- Automatically verify documents after generation
- Block storage/delivery if critical issues found
- Allow manual override with justification (admin only)

**FR-11**: The system MUST provide an API endpoint for on-demand verification:
- POST `/api/verify-document` with file upload
- Return verification report in requested format
- Support batch verification for multiple files

**FR-12**: The system MUST integrate with the storage backend:
- Store verification reports alongside generated documents
- Tag documents with verification status in metadata
- Enable filtering documents by verification status

### 5.4 Configuration & Management

**FR-13**: The system MUST support configurable verification rules:
- Enable/disable specific checks
- Set risk severity thresholds
- Configure external service integration (API keys, timeouts)
- Define custom YARA rules

**FR-14**: The system MUST maintain a verification rule database:
- Known malicious patterns (YARA rules)
- Known safe patterns (whitelist)
- Platform-specific requirements
- Version history of rule changes

**FR-15**: The system MUST provide administrative dashboard access to:
- View verification statistics (pass rate, common failures)
- Review flagged documents manually
- Update verification rules and configurations
- Export compliance reports

---

## 6. Non-Goals (Out of Scope)

**NG-1**: **Real-time monitoring of all document downloads** - Verification occurs at generation time, not at every access

**NG-2**: **Scanning documents uploaded by users** - System only verifies internally generated documents

**NG-3**: **Protection against zero-day exploits** - System validates against known patterns and best practices, not novel threats

**NG-4**: **Complete VirusTotal scanning for every document** - VirusTotal integration is optional due to API rate limits and costs

**NG-5**: **PDF verification** - System specifically targets DOCX format; PDF validation is separate scope

**NG-6**: **Remediation of flagged documents** - System identifies issues but does not automatically fix them

**NG-7**: **Real-time threat intelligence updates** - Rule updates are manual/scheduled, not real-time

---

## 7. Technical Considerations

### 7.1 Technology Stack

**Recommended Libraries:**
- **python-docx**: Already in use for document generation, can be extended for validation
- **zipfile**: Python standard library for ZIP archive validation
- **lxml**: XML parsing and validation
- **oletools**: OLE/VBA analysis (pip install oletools)
- **yara-python**: YARA rule engine integration (pip install yara-python)
- **clamd**: ClamAV daemon client (pip install clamd) - optional
- **requests**: VirusTotal API integration

### 7.2 Architecture

**Component Design:**
```
DocumentVerifier (main class)
├── StructureValidator: ZIP and OOXML structure checks
├── MacroDetector: VBA and executable content detection
├── EmbeddedContentScanner: OLE objects, external references
├── MetadataValidator: Document properties validation
├── ContentValidator: Template variables, string patterns
├── ExternalScanner: VirusTotal, ClamAV integration
└── ReportGenerator: Verification reports and logging
```

**Workflow Integration:**
```
Document Generation → Verification → Pass? → Storage Backend → Delivery
                           ↓
                         Fail → Block + Alert → Manual Review
```

### 7.3 Performance Considerations

- **Verification time target**: < 3 seconds for typical resume (50-200 KB)
- **ZIP decompression**: Use in-memory operations to avoid disk I/O
- **External API calls**: Implement timeout limits (VirusTotal: 30s, ClamAV: 10s)
- **Caching**: Cache VirusTotal results by file hash (24-hour TTL)
- **Async operations**: External scans can run asynchronously with callback

### 7.4 Security Considerations

**API Key Management:**
- Store VirusTotal API key in environment variables (`.env`)
- Never log API keys or sensitive credentials
- Implement rate limiting to avoid API quota exhaustion

**File Handling:**
- Perform all verification in isolated temporary directories
- Delete temporary files immediately after verification
- Never execute or open documents during verification
- Validate file size limits before processing (max 10 MB)

**Access Control:**
- Verification reports may contain sensitive information
- Restrict manual override capability to admin users
- Audit log all verification decisions and overrides

### 7.5 Database Schema

**New Table: `document_verifications`**
```sql
CREATE TABLE document_verifications (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES generated_documents(id),
    verification_timestamp TIMESTAMP DEFAULT NOW(),
    file_hash_sha256 VARCHAR(64) NOT NULL,
    overall_status VARCHAR(20) NOT NULL, -- 'passed', 'failed', 'warning'
    structure_check BOOLEAN,
    macro_check BOOLEAN,
    embedded_content_check BOOLEAN,
    metadata_check BOOLEAN,
    external_scan_status VARCHAR(20), -- 'passed', 'failed', 'skipped', 'error'
    virustotal_scan_id VARCHAR(255),
    clamav_result TEXT,
    issues_found JSONB, -- Array of issue objects
    risk_level VARCHAR(20), -- 'critical', 'high', 'medium', 'low', 'none'
    verification_report JSONB,
    manual_override BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    override_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_document_verifications_document_id ON document_verifications(document_id);
CREATE INDEX idx_document_verifications_status ON document_verifications(overall_status);
CREATE INDEX idx_document_verifications_timestamp ON document_verifications(verification_timestamp);
```

### 7.6 Dependencies

**New Python Packages:**
- `oletools>=0.60` - OLE/VBA analysis
- `yara-python>=4.3.0` - YARA rule engine (optional)
- `clamd>=1.0.2` - ClamAV integration (optional)
- `python-magic>=0.4.27` - File type detection

**External Services:**
- VirusTotal API v3 (optional, requires API key)
- ClamAV daemon (optional, requires local installation)

**System Requirements:**
- Python 3.11+ (current project version)
- Minimum 512 MB RAM for verification operations
- Temporary storage: 50 MB per concurrent verification

---

## 8. Design Considerations

### 8.1 Verification Report Format

**JSON Structure:**
```json
{
  "document_id": 12345,
  "filename": "John_Doe_Resume_20251009.docx",
  "file_hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "verification_timestamp": "2025-10-09T14:32:10Z",
  "overall_status": "passed",
  "risk_level": "none",
  "checks": {
    "structure_validation": {
      "status": "passed",
      "details": "ZIP integrity verified, all required OOXML files present"
    },
    "macro_detection": {
      "status": "passed",
      "details": "No VBA macros detected"
    },
    "embedded_content": {
      "status": "passed",
      "details": "No suspicious OLE objects or external references"
    },
    "metadata_validation": {
      "status": "passed",
      "details": "Realistic timestamps, complete properties"
    },
    "content_validation": {
      "status": "passed",
      "details": "All template variables replaced"
    },
    "external_scan": {
      "virustotal": {
        "status": "passed",
        "scan_id": "abc123...",
        "engines_detected": 0,
        "total_engines": 73
      },
      "clamav": {
        "status": "passed",
        "signature_version": "26998"
      }
    }
  },
  "issues": [],
  "recommendations": []
}
```

### 8.2 Error Handling

**Verification Failures:**
- **Critical**: Block document delivery, require remediation
  - Examples: Macros detected, VirusTotal detection, corrupted structure
- **High**: Allow delivery with warning, flag for review
  - Examples: Unusual external references, metadata anomalies
- **Medium**: Log warning, allow delivery
  - Examples: Missing optional metadata, unknown file properties
- **Low**: Informational only
  - Examples: File size unusually large, non-standard fonts

**External Service Failures:**
- VirusTotal timeout/error: Log error, allow delivery (scan is optional)
- ClamAV unavailable: Log warning, proceed with other checks
- Network errors: Implement retry logic (3 attempts with exponential backoff)

### 8.3 User Interface

**Admin Dashboard Section:**
- Widget: "Document Verification Status" showing pass rate (last 30 days)
- Table: Recent verifications with filterable status
- Detail view: Full verification report for selected document
- Actions: Manual review, override, re-verify

**API Response Format:**
- Success: 200 OK with verification report
- Failure: 400 Bad Request (invalid file), 500 Internal Server Error (scan failure)
- Rate limited: 429 Too Many Requests (VirusTotal quota exceeded)

---

## 9. Success Metrics

**SM-1**: **Zero False Positives** - No generated documents flagged as malicious by major platforms (Gmail, Outlook, SharePoint) in production use

**SM-2**: **100% Structure Validation Pass Rate** - All generated documents pass OOXML structure validation

**SM-3**: **Verification Time < 3 seconds** - 95th percentile verification time under 3 seconds

**SM-4**: **Early Detection Rate** - Catch 100% of template variable replacement failures before delivery

**SM-5**: **Audit Compliance** - 100% of generated documents have verification records in database

**SM-6**: **External Scan Coverage** - 90%+ of documents scanned by VirusTotal (when API quota available)

---

## 10. Implementation Phases

### Phase 1: Core Verification Engine (Week 1-2)
- Implement structure validation (ZIP, OOXML)
- Implement macro detection
- Create verification report generator
- Database schema setup
- Unit tests for core validators

### Phase 2: Content & Metadata Validation (Week 2-3)
- Implement template variable check
- Metadata validation
- Embedded content scanner
- Integration with document generation workflow

### Phase 3: External Service Integration (Week 3-4)
- VirusTotal API integration
- ClamAV integration (optional)
- YARA rule engine setup
- Caching and rate limiting

### Phase 4: Reporting & Administration (Week 4-5)
- Admin dashboard widgets
- API endpoints for on-demand verification
- Batch verification support
- Export compliance reports

### Phase 5: Testing & Production Deployment (Week 5-6)
- End-to-end testing with real-world documents
- Performance optimization
- Documentation
- Production rollout with monitoring

---

## 11. Open Questions

**OQ-1**: Should we implement automatic remediation for common issues (e.g., auto-fix metadata), or always require manual intervention?

**OQ-2**: What is the acceptable VirusTotal API rate limit and cost budget? Free tier: 4 requests/minute, 500 requests/day.

**OQ-3**: Should verification be mandatory for all documents, or only for certain document types (e.g., only resumes sent to external recipients)?

**OQ-4**: How long should we retain verification reports? Same retention policy as documents, or separate?

**OQ-5**: Should we implement a "known good" whitelist where documents with verified clean hashes can skip re-verification?

**OQ-6**: Do we need to support custom YARA rule uploads by administrators, or maintain a curated rule set?

**OQ-7**: Should failed verifications trigger automatic notifications to administrators, or only log for periodic review?

**OQ-8**: What level of detail should be exposed in API responses to prevent information disclosure about security mechanisms?

---

## 12. References & Research Sources

- Microsoft Learn: Built-in virus protection in SharePoint, OneDrive, and Teams
- Microsoft Learn: Safe Attachments - Microsoft Defender for Office 365
- Google Workspace: AI-powered ransomware detection in Google Drive
- Gmail Help: Anti-virus scanning attachments
- Intezer: How to Analyze Malicious Microsoft Office Files
- YARA Documentation: Pattern matching for malware detection
- ClamAV Documentation: Virus scanning and YARA integration
- VirusTotal API v3 Documentation
- OWASP: Office Document Security Best Practices

---

## 13. Appendix: YARA Rule Examples

**Detect Unreplaced Template Variables:**
```yara
rule UnreplacedTemplateVariables
{
    meta:
        description = "Detects unreplaced template variables in DOCX"
        author = "Automated Job Application System"
        severity = "high"

    strings:
        $angle_var = /<<[a-zA-Z0-9_]+>>/ ascii wide
        $curly_var = /{[a-zA-Z0-9_]+}/ ascii wide

    condition:
        uint16(0) == 0x4B50 and  // ZIP signature
        any of them
}
```

**Detect Remote Template Injection:**
```yara
rule RemoteTemplateInjection
{
    meta:
        description = "Detects remote template loading in DOCX"
        author = "Automated Job Application System"
        severity = "critical"

    strings:
        $template_http = "http://" ascii wide
        $template_https = "https://" ascii wide
        $template_tag = "<w:attachedTemplate" ascii wide

    condition:
        uint16(0) == 0x4B50 and
        $template_tag and ($template_http or $template_https)
}
```

**Detect VBA Macros:**
```yara
rule VBAMacroDetection
{
    meta:
        description = "Detects presence of VBA macros in DOCX"
        author = "Automated Job Application System"
        severity = "critical"

    strings:
        $vba_project = "word/vbaProject.bin" ascii
        $vba_dir = "word/vbaData.xml" ascii

    condition:
        uint16(0) == 0x4B50 and
        any of them
}
```

---

**End of Document**
