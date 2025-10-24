---
title: "Prd Content Based Validation"
type: technical_doc
component: security
status: draft
tags: []
---

# Product Requirements Document: Content-Based Validation

**Version:** 1.0.0
**Date:** 2025-01-11
**Author:** Security Team
**Status:** Approved

## Executive Summary

Implement content-based validation for generated DOCX documents to ensure that the actual content matches expected template variables and detect unexpected executable content, malicious scripts, or suspicious patterns that structural scanning cannot identify.

## Problem Statement

**Current Limitation:**
The existing security scanner validates document structure (ZIP integrity, OLE objects, XML structure) but does not analyze the actual text content. This creates vulnerabilities:

- Cannot detect JavaScript/VBScript code in hyperlinks
- Cannot validate that generated content matches input data
- Cannot identify unexpected executable content in text
- Cannot detect obfuscated malicious patterns
- Cannot verify template variable substitution completed correctly

**Impact:**
Attackers could inject malicious scripts through template variables or hyperlinks that execute when the document is opened, bypassing structural validation.

## Goals

### Primary Goals
1. **Validate content integrity** - Ensure generated content matches input data
2. **Detect executable content** - Find JavaScript, VBScript, PowerShell in text/hyperlinks
3. **Identify suspicious patterns** - Detect obfuscation, encoding tricks, malicious URLs
4. **Verify template completion** - Ensure all variables were replaced correctly

### Non-Goals
- Natural language content analysis (not checking grammar/spelling)
- Semantic analysis of resume/cover letter quality
- PII detection (separate feature)
- Content moderation (profanity, hate speech)

## Success Metrics

- **Detection Accuracy:** 98%+ detection of script injection attempts
- **Performance:** <10ms additional overhead per document
- **False Positives:** <1% false positive rate
- **Coverage:** 100% of text content and hyperlinks scanned

## User Stories

**US-1: Security Analyst**
As a security analyst, I want to detect malicious scripts in document content so that I can prevent XSS-style attacks through generated documents.

**US-2: Developer**
As a developer, I want to verify that template variables were replaced correctly so that I can ensure document quality.

**US-3: Compliance Officer**
As a compliance officer, I want to detect unexpected content in documents so that I can maintain data integrity standards.

## Requirements

### Functional Requirements

**FR-1: Script Detection in Text**
- MUST detect JavaScript in text content (`<script>`, `javascript:`)
- MUST detect VBScript patterns (`vbscript:`, VB functions)
- MUST detect PowerShell commands (`Invoke-Expression`, `IEX`)
- MUST detect command injection patterns (`;`, `&&`, `||`)

**FR-2: Hyperlink Validation**
- MUST extract all hyperlinks from document
- MUST validate URL schemes (allow: http, https, mailto)
- MUST detect `javascript:` protocol in links
- MUST detect `vbscript:` protocol in links
- MUST detect `file:` protocol (local file access)
- MUST check for obfuscated URLs (base64, hex encoding)

**FR-3: Template Variable Verification**
- MUST detect unreplaced template variables (`<<variable>>`, `{variable}`)
- MUST validate that critical variables were substituted
- MUST flag documents with placeholder text
- MUST detect malformed variable patterns

**FR-4: Suspicious Pattern Detection**
- MUST detect HTML/XML tags in plain text (potential injection)
- MUST detect base64-encoded payloads
- MUST detect hex-encoded strings (potential shellcode)
- MUST detect unusual Unicode characters (homograph attacks)
- MUST detect CLSID/ProgID references (COM object invocation)

**FR-5: Content Integrity Validation**
- SHOULD validate that content matches input data schema
- SHOULD detect unexpected content additions
- SHOULD verify expected sections present (resume: education, experience)

### Non-Functional Requirements

**NFR-1: Performance**
- MUST add <10ms overhead per document
- MUST scan text content in single pass
- MUST use compiled regex patterns

**NFR-2: Accuracy**
- MUST minimize false positives (<1%)
- MUST provide context for each detection
- MUST allow whitelisting of known safe patterns

**NFR-3: Extensibility**
- MUST support adding new detection patterns
- MUST allow custom validation rules
- MUST provide plugin architecture for validators

**NFR-4: Logging**
- MUST log all detected content issues
- MUST include matched patterns and locations
- MUST provide remediation guidance

## Technical Design

### Architecture

```
DOCXSecurityScanner
├── scan_file()
│   └── _validate_document_content() [NEW]
│       ├── _extract_text_content() [NEW]
│       ├── _extract_hyperlinks() [NEW]
│       ├── _detect_script_patterns() [NEW]
│       ├── _validate_hyperlinks() [NEW]
│       ├── _check_template_variables() [NEW]
│       └── _detect_suspicious_patterns() [NEW]
```

### Detection Patterns

```python
SCRIPT_PATTERNS = {
    'javascript': r'javascript:\s*',
    'vbscript': r'vbscript:\s*',
    'script_tag': r'<script[^>]*>',
    'event_handler': r'on(load|error|click|mouse)\s*=',
    'powershell': r'(Invoke-Expression|IEX|Invoke-Command)',
}

SUSPICIOUS_PATTERNS = {
    'base64_payload': r'(?:[A-Za-z0-9+/]{40,}={0,2})',
    'hex_string': r'(?:0x[0-9A-Fa-f]{8,})',
    'clsid': r'clsid:[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}',
    'html_injection': r'<\w+[^>]*>',
}

DANGEROUS_URL_SCHEMES = [
    'javascript:', 'vbscript:', 'file:', 'data:', 'about:'
]
```

### Data Flow

```
1. Extract all text from document.xml
2. Extract all hyperlinks from relationships
3. Run regex patterns against text
4. Validate each hyperlink
5. Check for unreplaced variables
6. Create SecurityThreat for each finding
7. Log to audit trail
```

## Implementation Plan

### Phase 1: Text Extraction (Day 1)
- Create `content_validator.py` module
- Implement text extraction from document.xml
- Implement hyperlink extraction from rels files

### Phase 2: Script Detection (Day 2)
- Implement JavaScript/VBScript detection
- Add PowerShell command detection
- Create threat objects for findings

### Phase 3: Hyperlink Validation (Day 2)
- Implement URL scheme validation
- Add obfuscation detection
- Test with malicious link samples

### Phase 4: Template Variable Check (Day 3)
- Implement variable pattern detection
- Add critical variable verification
- Test with incomplete documents

### Phase 5: Suspicious Pattern Detection (Day 3)
- Implement base64/hex detection
- Add HTML injection detection
- Test with obfuscated payloads

### Phase 6: Integration & Testing (Day 4)
- Integrate with main scanner
- Write comprehensive unit tests
- Performance benchmarking

### Phase 7: Documentation (Day 5)
- Update security docs
- Add usage examples
- Document detection patterns

## Testing Strategy

### Test Cases

**TC-1: Clean Content**
- Given: Document with normal text content
- When: Content validation runs
- Then: No threats detected

**TC-2: JavaScript in Hyperlink**
- Given: Hyperlink with `javascript:alert(1)`
- When: Hyperlink validation runs
- Then: SecurityThreat with type="malicious_hyperlink"

**TC-3: Unreplaced Variables**
- Given: Document with `<<first_name>>` placeholder
- When: Template validation runs
- Then: SecurityThreat with type="unreplaced_variable"

**TC-4: Base64 Payload**
- Given: Text with long base64 string
- When: Pattern detection runs
- Then: SecurityThreat with type="suspicious_content"

**TC-5: HTML Injection**
- Given: Text with `<script>alert(1)</script>`
- When: Script detection runs
- Then: SecurityThreat with type="script_injection"

**TC-6: Performance Test**
- Given: Large document (200KB text)
- When: Content validation runs
- Then: Completes in <10ms

### Test Data

- Clean resume with normal content
- Document with JavaScript in links
- Document with VBScript in text
- Document with unreplaced variables
- Document with base64-encoded data
- Document with HTML tags in text
- Large document for performance testing

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| False positives | Medium | Low | Whitelist, context awareness |
| Performance impact | Low | Medium | Optimized regex, caching |
| Bypass via encoding | Medium | High | Multiple encoding detection |
| Legitimate code flagged | Low | Low | Allow legitimate patterns |

## Dependencies

**New Dependencies:**
- None (uses Python standard library)

**Existing Dependencies:**
- DOCXSecurityScanner
- SecurityThreat class
- Template engine patterns (from template_engine.py)

## Acceptance Criteria

- [ ] Detects JavaScript/VBScript in text and hyperlinks
- [ ] Validates all hyperlink URL schemes
- [ ] Detects unreplaced template variables
- [ ] Identifies suspicious patterns (base64, hex, HTML)
- [ ] Performance overhead <10ms per document
- [ ] False positive rate <1%
- [ ] 95%+ test coverage for new code
- [ ] Documentation includes detection pattern examples

## Configuration

```python
# Security scanner config
CONTENT_VALIDATION_CONFIG = {
    'enable_script_detection': True,
    'enable_hyperlink_validation': True,
    'enable_template_verification': True,
    'enable_pattern_detection': True,
    'strict_mode': True,  # Block on any detection
    'whitelist_patterns': [],  # Allowed patterns
    'max_text_length': 10_000_000,  # 10MB text limit
}
```

## Future Enhancements

**Phase 2 (Optional):**
- Machine learning-based anomaly detection
- Natural language processing for context
- Content similarity analysis (detect template deviations)
- Custom validation rule DSL

## Appendix

### Script Detection Patterns (Detailed)

```python
# JavaScript detection
r'javascript:\s*'  # Protocol
r'<script[^>]*>'   # Tag
r'on(load|error|click|mouse|key)\s*='  # Event handlers

# VBScript detection
r'vbscript:\s*'  # Protocol
r'(msgbox|createobject|wscript\.shell)'  # VB functions (case-insensitive)

# PowerShell detection
r'(Invoke-Expression|IEX|Invoke-Command|Invoke-WebRequest)'
r'(Get-Process|Start-Process|Stop-Process)'
r'(New-Object\s+System\.)'

# Command injection
r'[;|&]{2,}'  # ; && || command separators
r'\$\([^)]+\)'  # $(...) substitution
```

### URL Validation Rules

```python
ALLOWED_SCHEMES = ['http', 'https', 'mailto', 'tel']
BLOCKED_SCHEMES = ['javascript', 'vbscript', 'file', 'data', 'about']

# Obfuscation patterns
OBFUSCATED_URL_PATTERNS = [
    r'&#\d+;',  # HTML entities
    r'%[0-9A-Fa-f]{2}',  # URL encoding
    r'\\u[0-9A-Fa-f]{4}',  # Unicode escapes
]
```

### Performance Benchmarks (Target)

| Operation | Target Time | Notes |
|-----------|-------------|-------|
| Text extraction | <2ms | From document.xml |
| Hyperlink extraction | <1ms | From rels files |
| Script detection | <3ms | Regex matching |
| Pattern detection | <4ms | Multiple regex |
| **Total** | **<10ms** | Per document |

---

**Approved By:** Security Team
**Next Review:** 2025-02-11
