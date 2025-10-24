# DOCX Template Validation Guide

## Overview

The DOCX Template Validation System provides comprehensive validation of `.docx` template files to ensure they are:
- **Structurally valid** (proper ZIP/OOXML format)
- **Compatible** with Microsoft Word and python-docx
- **Secure** (no malicious content, macros, or remote templates)
- **Properly formatted** (valid template variables)

## Quick Start

### Basic Usage

```bash
# Validate all templates in default directory
python validate_docx_templates.py

# Validate specific directory
python validate_docx_templates.py --path /path/to/templates

# Validate single file
python validate_docx_templates.py --file template.docx

# Strict mode (warnings become failures)
python validate_docx_templates.py --strict

# Show detailed results
python validate_docx_templates.py --details
```

### Output Formats

```bash
# Console output (default)
python validate_docx_templates.py

# JSON output
python validate_docx_templates.py --json

# Save to file
python validate_docx_templates.py --output report.txt
python validate_docx_templates.py --json --output report.json
```

## What the Validator Checks

### 1. File Integrity Validation

**Purpose:** Verify the DOCX file is structurally valid and can be processed.

**Checks performed:**
- ✓ File exists and is accessible
- ✓ File is a valid ZIP archive (DOCX files are ZIP files)
- ✓ ZIP integrity (no corrupted files)
- ✓ Required OOXML files present:
  - `[Content_Types].xml` - Content type definitions
  - `_rels/.rels` - Root relationships
  - `word/document.xml` - Main document content
- ✓ All XML files are well-formed (can be parsed)

**Common failures:**
- File is not a ZIP archive (corrupted or wrong format)
- Missing required OOXML files (corrupted during editing)
- Malformed XML (syntax errors in XML structure)

**How to fix:**
- If ZIP is invalid: The file is corrupted. Restore from backup or recreate.
- If missing files: Open in Word, save a copy, and try again.
- If XML is malformed: Open in Word, fix any corruption warnings, and save.

### 2. Compatibility Validation

**Purpose:** Ensure the document can be opened and processed by python-docx and Microsoft Word.

**Checks performed:**
- ✓ Document opens successfully in python-docx
- ✓ Can access paragraphs (content structure is valid)
- ✓ Can access styles (formatting is valid)
- ✓ All internal relationships are valid (no broken references)

**Common failures:**
- Cannot open with python-docx: Compatibility issue with Word version
- Broken internal references: Missing referenced files or styles

**How to fix:**
- Re-save the document in Word (File → Save As → Word Document .docx)
- Ensure compatibility mode is disabled
- Remove any external content references
- Verify all styles and referenced content exists

### 3. Security Validation

**Purpose:** Detect and prevent security threats commonly found in DOCX files.

**Checks performed:**
- ✓ No remote template references (DOTM injection attacks)
- ✓ No embedded OLE objects (executables, scripts)
- ✓ No ActiveX controls (executable code)
- ✓ No XML bombs (denial-of-service attacks)
- ✓ No malicious file extensions in ZIP (.exe, .dll, .vbs, etc.)
- ✓ No path traversal attempts in ZIP structure
- ✓ No external content references (tracking pixels)

**Threat levels:**
- **Critical:** Remote templates, ActiveX controls, executables
- **High:** OLE objects, suspicious file types
- **Medium:** External content references, XML entity definitions
- **Low:** Informational warnings

**Common threats detected:**

#### Remote Template Injection (Critical)
A DOCX file can reference a remote `.dotm` template that contains macros. When opened in Word, it automatically downloads and executes the malicious macros.

**Detection:** Checks `word/settings.xml` for `attachedTemplate` elements and relationship files for remote template URLs.

**How to fix:**
1. Open file in Word
2. File → Options → Add-ins → Manage: Templates → Go
3. Remove any attached templates
4. Save the document

#### OLE Objects (High)
Embedded OLE objects can contain executable code, scripts, or malicious files packaged as Office documents.

**Detection:** Checks for `embeddings/` directory and `<o:OLEObject>` elements in document XML.

**How to fix:**
1. Open file in Word
2. Identify embedded objects (they appear as icons or embedded content)
3. Delete unnecessary embedded objects
4. Save the document

#### External Content References (Medium)
External images, stylesheets, or hyperlinks that load content from remote servers can be used to track who opens the document.

**Detection:** Checks relationship files for HTTP/HTTPS URLs.

**How to fix:**
1. Open file in Word
2. File → Info → Check for Issues → Inspect Document
3. Remove external content references
4. Save the document

### 4. Template Variable Validation

**Purpose:** Ensure template variables are properly formatted and follow CSV standard.

**Expected format:** `<<variable_name>>`

**Checks performed:**
- ✓ Count valid variables using `<<variable_name>>` format
- ✓ Detect malformed variables:
  - `<variable>` - Single angle brackets (should be double)
  - `<<<variable>>>` - Triple angle brackets (typo)
  - `<<variable` - Missing closing brackets
  - `{{variable}}` - Wrong bracket type (Jinja2 style)
- ✓ Verify variable naming conventions (alphanumeric, underscore, spaces only)

**Common issues:**

#### Malformed Variables
Using wrong bracket types or counts.

**How to fix:**
Search and replace:
- `<variable>` → `<<variable>>`
- `{{variable}}` → `<<variable>>`
- `<<<variable>>>` → `<<variable>>`

#### Invalid Characters in Variable Names
Variable names should only contain letters, numbers, underscores, and spaces.

**Examples:**
- ✓ Valid: `<<first_name>>`, `<<email_address>>`, `<<Job Title>>`
- ✗ Invalid: `<<first-name>>` (dash), `<<email@address>>` (special char)

**How to fix:**
Replace special characters with underscores:
- `<<first-name>>` → `<<first_name>>`
- `<<email@address>>` → `<<email_address>>`

### 5. Content Validation

**Purpose:** Detect malicious or suspicious content in document text and hyperlinks.

**Checks performed:**
- ✓ No JavaScript/VBScript in text or hyperlinks
- ✓ No PowerShell commands or injection attempts
- ✓ No dangerous URL schemes (javascript:, vbscript:, file:, data:)
- ✓ No obfuscated URLs (excessive encoding, HTML entities)
- ✓ No suspicious patterns (base64 payloads, hex strings, HTML injection)

**Common issues:**

#### Script Patterns
Detection of scripting commands in document text.

**How to fix:**
Review and remove any scripting content:
1. Search for "javascript:", "vbscript:", "powershell"
2. Remove or replace with safe content
3. Save the document

#### Dangerous Hyperlinks
Hyperlinks using dangerous URL schemes that can execute code.

**Allowed schemes:** http, https, mailto, tel, ftp
**Dangerous schemes:** javascript, vbscript, file, data

**How to fix:**
1. Open file in Word
2. Press Ctrl+K to see hyperlinks
3. Remove or change dangerous hyperlinks
4. Save the document

## Understanding Validation Results

### Status Levels

- **✓ VALID** - All checks passed, template is safe to use
- **⚠ WARNING** - Non-critical issues detected (medium/low severity)
- **✗ INVALID** - Critical or high-severity issues detected
- **⚠ ERROR** - Validation could not complete (file access issues)

### Severity Levels

- **🔴 Critical** - Major security threat or corruption (must fix)
- **🟠 High** - Significant issue affecting security or functionality (should fix)
- **🟡 Medium** - Minor issue that may cause problems (recommended fix)
- **🔵 Low** - Informational warning (optional fix)

### Exit Codes

- `0` - All files valid
- `1` - One or more files invalid

### Example Reports

#### Valid Template

```
File: modern_professional_resume.docx
Path: content_template_library/resumes/modern_professional_resume.docx
Status: ✓ VALID
Checks: 15/15 passed
  Variables: 38 found
```

#### Template with Warnings

```
File: cover_letter_template.docx
Path: content_template_library/coverletters/cover_letter_template.docx
Status: ⚠ WARNING
Checks: 13/15 passed

  Issues found:
  🟡 [MEDIUM] malformed_variables: Found 2 malformed variable(s)
      malformed_variables: {"single_angle": ["company_name", "position"]}
  🔵 [LOW] variable_naming: Found 1 variable(s) with invalid characters
      invalid_variables: ["email@address"]

  Variables: 35 found
```

#### Invalid Template (Security Threat)

```
File: suspicious_template.docx
Path: templates/suspicious_template.docx
Status: ✗ INVALID
Checks: 12/15 passed

  Issues found:
  🔴 [CRITICAL] security_scan: Security threats detected: 2 total
      threat_count: 2
      by_severity: {"critical": 1, "high": 1, "medium": 0, "low": 0}
      threats: [
        {
          "threat_type": "remote_template",
          "severity": "critical",
          "description": "Document contains remote template reference (DOTM injection risk)",
          "location": "word/settings.xml"
        }
      ]
```

## Integration with CI/CD

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validate all DOCX templates before commit

python validate_docx_templates.py --strict
if [ $? -ne 0 ]; then
    echo "ERROR: DOCX template validation failed"
    echo "Fix issues and try again"
    exit 1
fi
```

### GitHub Actions Workflow

```yaml
name: Validate Templates

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install python-docx
      - name: Validate templates
        run: |
          python validate_docx_templates.py --strict --json --output report.json
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: validation-report
          path: report.json
```

### Automated Testing

```python
import pytest
from validate_docx_templates import DOCXTemplateValidator

def test_all_templates_valid():
    """Ensure all templates pass validation"""
    validator = DOCXTemplateValidator(strict_mode=True)

    template_dir = "content_template_library"
    for file_path in Path(template_dir).rglob("*.docx"):
        report = validator.validate_file(str(file_path))
        assert report.overall_status in ["valid", "warning"], \
            f"Template {file_path} failed validation: {report.overall_status}"
```

## Troubleshooting

### "python-docx not available"

**Problem:** python-docx library not installed.

**Solution:**
```bash
pip install python-docx
```

### "File is not a valid ZIP archive"

**Problem:** DOCX file is corrupted or not a Word document.

**Solution:**
1. Try opening in Microsoft Word
2. If it opens, save a new copy: File → Save As
3. If it doesn't open, restore from backup

### "Missing required OOXML file"

**Problem:** DOCX file structure is corrupted.

**Solution:**
1. Open in Microsoft Word
2. File → Info → Check for Issues → Inspect Document
3. Fix any issues found
4. Save as new file

### "Remote template detected"

**Problem:** Critical security threat - document references external template with potential macros.

**Solution:**
1. Open in Word
2. File → Options → Add-ins → Manage: Templates
3. Click "Go"
4. Remove attached template
5. Save document

### "Security threats detected"

**Problem:** Document contains potentially malicious content.

**Solution:**
1. Review the specific threats in the report
2. For each threat:
   - Remove embedded objects
   - Remove external references
   - Remove suspicious content
3. Re-validate after fixes

### "Malformed variables"

**Problem:** Template variables using wrong format.

**Solution:**
Use Find & Replace in Word:
- Find: `<([a-zA-Z0-9_]+)>` (enable wildcards)
- Replace: `<<\1>>`

Or manually fix each variable to use `<<variable_name>>` format.

## Best Practices

### Creating New Templates

1. **Start from scratch in Word** - Don't copy templates from unknown sources
2. **Use standard variable format** - Always use `<<variable_name>>`
3. **Avoid external content** - Don't embed or link to external files
4. **No macros** - Save as `.docx`, never `.docm` or `.dotm`
5. **Validate immediately** - Run validator on new templates before committing

### Maintaining Existing Templates

1. **Regular validation** - Run validator monthly on all templates
2. **Version control** - Track changes to templates in git
3. **Document variables** - Maintain list of expected variables per template
4. **Security updates** - Re-validate after any security updates to Word

### Template Variable Standards

1. **Naming convention:**
   - Use lowercase with underscores: `<<first_name>>`
   - Or title case with spaces: `<<First Name>>`
   - Be consistent across all templates

2. **Required variables:**
   - Document expected variables in template metadata
   - Create CSV/JSON with sample data for testing

3. **Testing:**
   - Test variable replacement with real data
   - Verify formatting is preserved after replacement

## API Usage (Python)

### Validate Single File

```python
from validate_docx_templates import DOCXTemplateValidator

validator = DOCXTemplateValidator(strict_mode=False)
report = validator.validate_file("template.docx")

if report.overall_status == "valid":
    print("Template is valid!")
else:
    print(f"Template has issues: {report.overall_status}")
    for result in report.results:
        if not result.passed:
            print(f"  - {result.check_name}: {result.message}")
```

### Batch Validation

```python
from pathlib import Path
from validate_docx_templates import DOCXTemplateValidator

validator = DOCXTemplateValidator(strict_mode=True)
reports = []

for template_file in Path("templates").rglob("*.docx"):
    report = validator.validate_file(str(template_file))
    reports.append(report)

# Check results
invalid_templates = [r for r in reports if r.overall_status == "invalid"]
if invalid_templates:
    print(f"Found {len(invalid_templates)} invalid templates")
```

### Generate JSON Report

```python
from validate_docx_templates import (
    DOCXTemplateValidator,
    ValidationReportGenerator
)

validator = DOCXTemplateValidator()
reports = []

# Validate files
for file_path in ["template1.docx", "template2.docx"]:
    report = validator.validate_file(file_path)
    reports.append(report)

# Generate JSON report
generator = ValidationReportGenerator()
json_report = generator.generate_json_report(reports)

# Save to file
import json
with open("validation_report.json", "w") as f:
    json.dump(json_report, f, indent=2)
```

## Security Considerations

### Why Security Validation Matters

DOCX files can contain dangerous content:

1. **Remote Template Injection (DOTM)**
   - Automatically downloads and executes macros
   - Can bypass antivirus and security software
   - Used in targeted phishing attacks

2. **Embedded Executables**
   - OLE objects can contain .exe, .dll, or scripts
   - Executed when user double-clicks embedded icon
   - Can install malware or steal data

3. **Tracking Pixels**
   - External image references reveal who opened the document
   - Privacy leak and potential reconnaissance
   - Used to validate email addresses for spam

4. **XML Bombs**
   - Exponentially expanding XML entities
   - Can crash Word or consume all system memory
   - Denial of service attack

### Defense in Depth

This validator is one layer of security:

1. **Pre-generation validation** - Validate templates before use
2. **Post-generation validation** - Validate generated documents
3. **User training** - Educate users about DOCX threats
4. **Email filtering** - Block suspicious DOCX files at email gateway
5. **Endpoint protection** - Use antivirus with DOCX scanning

### Compliance

This validator helps meet security requirements for:

- **SOC 2** - Security controls for document handling
- **ISO 27001** - Information security management
- **GDPR** - Privacy protection (no tracking pixels)
- **HIPAA** - Healthcare data security (no data leaks)

## Support and Contributing

### Reporting Issues

If you find a security vulnerability:
1. Do NOT create a public issue
2. Email security team directly
3. Include sample file (if safe) and detailed description

For bugs or feature requests:
1. Create GitHub issue with detailed description
2. Include validation output and sample file
3. Specify your environment (OS, Python version, Word version)

### Contributing

Contributions welcome! Areas for improvement:

1. Additional security checks
2. Better error messages
3. Performance optimization
4. Support for more Office formats (.dotx, .docm)
5. Integration with other validation tools

### Version History

- **1.0.0** (2025-10-24)
  - Initial release
  - Comprehensive validation system
  - Security scanning integration
  - Template variable validation
  - JSON and console output

## License

This validation system is part of the Automated Job Application System.
See main project LICENSE file for details.

## References

### OOXML Specification
- [Office Open XML File Formats](https://docs.microsoft.com/en-us/openspecs/office_standards/ms-docx/)
- [ECMA-376 Standard](https://www.ecma-international.org/publications-and-standards/standards/ecma-376/)

### Security Resources
- [DOTM Injection Attacks](https://www.bleepingcomputer.com/news/security/microsoft-word-documents-hijack-pcs-via-remote-templates/)
- [OLE Object Exploitation](https://www.fortinet.com/blog/threat-research/malicious-ole-objects-in-office-documents)
- [XML Security](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)

### Python Libraries
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [zipfile Module](https://docs.python.org/3/library/zipfile.html)
- [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html)
