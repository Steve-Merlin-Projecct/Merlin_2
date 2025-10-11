# DOCX Security Verification System

**Version:** 1.0.0
**Status:** Production Ready
**Security Level:** Defensive Only

## Overview

The DOCX Security Verification System provides comprehensive protection against malicious content in Word documents. This system scans generated documents for security threats before delivery, maintaining an audit trail of all security operations.

## Architecture

### Components

1. **DOCXSecurityScanner** (`docx_security_scanner.py`)
   - Multi-layer security validation
   - ZIP structure integrity checks
   - Remote template detection
   - OLE object inspection
   - XML bomb detection
   - External reference validation

2. **SecurityAuditLogger** (`security_audit_logger.py`)
   - JSON-formatted audit logs
   - Daily log rotation
   - Thread-safe logging
   - Query and reporting capabilities

3. **TemplateEngine Integration** (`template_engine.py`)
   - Automatic security scanning on document generation
   - Fail-safe: deletes unsafe documents
   - Comprehensive error reporting

## Threat Protection

### 1. Remote Template Injection (CRITICAL)

**Threat:** Documents can reference remote DOTM templates that execute macros when opened.

**Protection:**
- Scans `word/settings.xml` for `attachedTemplate` elements
- Checks relationship files for HTTP/HTTPS template URLs
- Blocks documents with remote template references

**Detection Pattern:**
```xml
<!-- BLOCKED: Remote template reference -->
<w:attachedTemplate r:id="rId1"/>
```

### 2. OLE Object Embedding (HIGH)

**Threat:** Embedded OLE objects can contain executable content or malicious documents.

**Protection:**
- Detects `embeddings/` directory in DOCX ZIP
- Scans document.xml for OLE object elements
- Identifies ActiveX controls and Package objects

**Blocked Content:**
- ActiveX controls
- Embedded executables (EXE, DLL, SCR)
- Macro-enabled Office documents (DOCM, XLSM)
- Scripting objects (VBS, JS, PS1)

### 3. ZIP Structure Attacks (CRITICAL)

**Threat:** Malformed ZIP files can exploit parser vulnerabilities or hide malicious content.

**Protection:**
- Validates ZIP integrity with `testzip()`
- Checks for required OOXML files
- Detects path traversal attempts (`..`, absolute paths)
- Blocks suspicious file extensions

**Validation Checks:**
- File is valid ZIP archive
- Contains `[Content_Types].xml` and `_rels/.rels`
- No corrupted files in archive
- No path traversal patterns
- Reasonable file size

### 4. External Content References (MEDIUM)

**Threat:** External URLs can leak information about who opens the document.

**Protection:**
- Scans relationship files for HTTP/HTTPS URLs
- Identifies external images (tracking pixels)
- Detects external stylesheet references

**Information Leakage Vectors:**
- External image URLs
- Remote stylesheets
- External hyperlinks

### 5. XML Bomb Attacks (HIGH)

**Threat:** Exponential entity expansion can exhaust memory and crash systems.

**Protection:**
- Detects DOCTYPE declarations with entity definitions
- Monitors XML nesting depth
- Blocks documents with suspicious entity patterns

**Example Blocked Pattern:**
```xml
<!DOCTYPE doc [
    <!ENTITY lol "lol">
    <!ENTITY lol2 "&lol;&lol;">
    <!ENTITY lol3 "&lol2;&lol2;">
]>
```

## Usage

### Basic Scanning

```python
from modules.content.document_generation.docx_security_scanner import scan_docx_file

# Scan a file
is_safe, report = scan_docx_file("document.docx", strict_mode=True)

if is_safe:
    print("Document is safe")
else:
    print(f"Threats found: {report['total_threats']}")
    for threat in report['threats']:
        print(f"  - {threat['threat_type']}: {threat['description']}")
```

### Scanning Bytes

```python
from modules.content.document_generation.docx_security_scanner import scan_docx_bytes

# Scan document content
with open("document.docx", "rb") as f:
    docx_bytes = f.read()

is_safe, report = scan_docx_bytes(docx_bytes, "document.docx", strict_mode=True)
```

### Integrated with Template Engine

```python
from modules.content.document_generation.template_engine import TemplateEngine

# Security scanning enabled by default
engine = TemplateEngine(enable_security_scan=True)

try:
    result = engine.generate_document(
        template_path="templates/resume.docx",
        data={"name": "John Doe", "title": "Software Engineer"}
    )

    # Check security scan results
    if result["security_scan"]["is_safe"]:
        print("Document passed security validation")

except SecurityError as e:
    print(f"Document blocked: {e}")
```

## Security Audit Trail

### Logging

All security scans are automatically logged to `logs/security_audit/`:

```python
from modules.content.document_generation.security_audit_logger import SecurityAuditLogger

logger = SecurityAuditLogger()

# Logs are written automatically during scanning
# Format: security_audit_YYYY-MM-DD.jsonl
```

### Querying Logs

```python
# Get recent scans
recent_scans = logger.get_recent_scans(limit=100, days=7)

# Get threat summary
summary = logger.get_threat_summary(days=30)
print(f"Total scans: {summary['total_scans']}")
print(f"Unsafe documents: {summary['unsafe_documents']}")
print(f"Critical threats: {summary['threats_by_severity']['critical']}")

# Query specific file
file_history = logger.query_by_file("/path/to/document.docx")
```

### Exporting Reports

```python
# Export comprehensive security report
logger.export_report("security_report_2025-01.json", days=30)
```

### Log Format

Each log entry is a JSON object:

```json
{
  "timestamp": "2025-01-11T10:30:45.123456",
  "event_type": "security_scan",
  "file_path": "/storage/document.docx",
  "is_safe": false,
  "threat_count": 2,
  "scan_report": {
    "total_threats": 2,
    "severity_counts": {
      "critical": 1,
      "high": 1,
      "medium": 0,
      "low": 0
    },
    "threats": [
      {
        "threat_type": "remote_template",
        "severity": "critical",
        "description": "Document contains remote template reference",
        "location": "word/settings.xml",
        "timestamp": "2025-01-11T10:30:45.123456"
      }
    ]
  },
  "metadata": {
    "author": "John Doe",
    "title": "Resume",
    "document_type": "resume"
  }
}
```

## Configuration

### Strict Mode

**Strict Mode (Recommended):**
- Blocks documents with HIGH or CRITICAL threats
- Suitable for production environments
- Maximum security

**Permissive Mode:**
- Only blocks CRITICAL threats
- Allows HIGH severity threats with warnings
- Use only for testing/development

```python
# Strict mode (default)
scanner = DOCXSecurityScanner(strict_mode=True)

# Permissive mode
scanner = DOCXSecurityScanner(strict_mode=False)
```

### Disabling Security Scanning

Security scanning can be disabled (NOT recommended):

```python
engine = TemplateEngine(enable_security_scan=False)
```

**⚠️ WARNING:** Disabling security scanning removes critical protection against malicious content.

## Threat Severity Levels

| Severity | Description | Action |
|----------|-------------|--------|
| **CRITICAL** | Immediate security risk (remote code execution, malware) | Always blocked |
| **HIGH** | Significant risk (embedded objects, suspicious content) | Blocked in strict mode |
| **MEDIUM** | Moderate risk (information leakage, tracking) | Logged but allowed |
| **LOW** | Minor concern (edge cases) | Logged but allowed |

## Testing

Run comprehensive security scanner tests:

```bash
pytest tests/test_docx_security_scanner.py -v
```

Test coverage includes:
- Safe document validation
- Remote template detection
- OLE object inspection
- XML bomb detection
- ZIP structure validation
- Audit logging functionality
- Integration workflows

## Performance

### Scanning Speed

- **Typical document (50KB):** ~50ms
- **Large document (200KB):** ~150ms
- **Overhead:** Minimal (~2-5% of generation time)

### Resource Usage

- **Memory:** ~5MB per concurrent scan
- **Disk I/O:** Sequential reads, no random access
- **CPU:** Low (XML parsing, regex matching)

## Maintenance

### Log Rotation

Logs rotate daily automatically. Clean up old logs:

```python
# Keep logs for 90 days
deleted_count = logger.cleanup_old_logs(keep_days=90)
```

### Monitoring

Monitor security metrics:

```python
summary = logger.get_threat_summary(days=30)

# Alert on high threat rate
threat_rate = summary['unsafe_documents'] / summary['total_scans']
if threat_rate > 0.05:  # More than 5% unsafe
    alert_security_team(summary)
```

## Security Best Practices

1. **Always enable strict mode in production**
   ```python
   scanner = DOCXSecurityScanner(strict_mode=True)
   ```

2. **Monitor security audit logs regularly**
   ```python
   # Daily monitoring script
   summary = logger.get_threat_summary(days=1)
   if summary['unsafe_documents'] > 0:
       send_alert(summary)
   ```

3. **Keep oletools dependency updated**
   ```bash
   pip install --upgrade oletools
   ```

4. **Review external references**
   - External URLs may leak information
   - Consider blocking or sanitizing external content

5. **Test with malicious samples**
   - Use test suite in `tests/test_docx_security_scanner.py`
   - Test with real-world malware samples (in isolated environment)

## Compliance

This security system helps meet compliance requirements:

- **SOC 2:** Audit trail, access logging, threat detection
- **ISO 27001:** Security controls, monitoring, incident response
- **GDPR:** Data protection, security measures
- **HIPAA:** Access controls, audit logs (if applicable)

## Incident Response

If a malicious document is detected:

1. **Document is automatically blocked**
   - File deleted from storage
   - SecurityError raised
   - Generation workflow halted

2. **Audit log created**
   - Timestamp and threat details
   - Source metadata
   - Full scan report

3. **Review threat details**
   ```python
   file_history = logger.query_by_file(blocked_file_path)
   threat_details = file_history[0]['scan_report']
   ```

4. **Investigate source**
   - Check template library
   - Review document metadata
   - Trace generation workflow

## Known Limitations

1. **No macro execution detection**
   - DOCX format cannot contain VBA macros
   - Only detects macro-enabled references (DOTM)

2. **No content-based malware scanning**
   - Focuses on structural threats
   - Does not perform antivirus scanning
   - Consider integrating with AV solution for comprehensive protection

3. **Limited OLE analysis**
   - Detects presence of OLE objects
   - Does not parse OLE stream contents
   - Consider `oletools` integration for deeper analysis

## Dependencies

- **python-docx** (>=1.2.0): DOCX creation and parsing
- **oletools** (>=0.60.2): Office document analysis (optional, recommended)
- **Standard library**: `zipfile`, `xml.etree.ElementTree`, `re`

## Support and Contact

For security concerns or vulnerability reports:
- **Email:** security@example.com (placeholder)
- **GitHub Issues:** For non-security bugs only
- **Security Policy:** See SECURITY.md

## Changelog

### Version 1.0.0 (2025-01-11)
- Initial release
- Remote template detection
- OLE object inspection
- ZIP structure validation
- External reference detection
- XML bomb detection
- Security audit logging
- Comprehensive test suite

## License

Same as parent project (Automated Job Application System).

---

**Last Updated:** 2025-01-11
**Maintained By:** Automated Job Application System Team
