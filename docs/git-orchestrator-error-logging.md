# Git Orchestrator Error Logging

## Overview

The git-orchestrator agent automatically logs all errors, warnings, and failures to provide historical tracking, debugging context, and audit trails for git operations.

**Log Location:** `logs/git-orchestrator-errors.log`

---

## Log Entry Structure

Each log entry includes:
- **Timestamp:** UTC timestamp
- **Operation Type:** checkpoint, section_commit, or user_commit
- **Branch:** Current git branch
- **Error/Warning Type:** Specific category of issue
- **Status:** failed or success_with_warning
- **Details:** Full error description
- **Remediation:** Steps to resolve the issue
- **Git Context:** Current status and staged changes
- **Fallback Actions:** Any recovery actions taken

---

## Example Log Entries

### Error: Test Failures (Section Commit)

```
================================================================================
TIMESTAMP: 2025-10-12 14:32:15 UTC
OPERATION: section_commit
BRANCH: feature/email-validation
ERROR_TYPE: tests_failed
STATUS: failed

ERROR_DETAILS:
Tests failed: 2 failures detected
- test_email_validation.py::test_invalid_format FAILED
- test_email_validation.py::test_domain_check FAILED

REMEDIATION:
- Fix failing tests in test_email_validation.py
- Run: pytest test_email_validation.py -v for details
- Verify email validation logic handles edge cases

FALLBACK_ACTION: checkpoint_created
FALLBACK_COMMIT: a1b2c3d

GIT_STATUS:
M  modules/email_integration/validator.py
M  tests/test_email_validation.py

FILES_CHANGED:
 modules/email_integration/validator.py | 45 +++++++++++++++++---------
 tests/test_email_validation.py         | 23 ++++++++++---
 2 files changed, 48 insertions(+), 20 deletions(-)

================================================================================
```

### Warning: Tests Failed (Checkpoint)

```
================================================================================
TIMESTAMP: 2025-10-12 15:10:22 UTC
OPERATION: checkpoint
BRANCH: feature/dashboard-api
WARNING_TYPE: tests_failed
STATUS: success_with_warning

WARNING_DETAILS:
Tests failed: 1 failure detected
- test_dashboard.py::test_metrics_endpoint FAILED

ACTION_TAKEN:
Checkpoint created with test failures

COMMIT_HASH: d4e5f6g

GIT_STATUS:
M  modules/dashboard/api.py
A  modules/dashboard/metrics.py

================================================================================
```

### Warning: Schema Automation Failed

```
================================================================================
TIMESTAMP: 2025-10-12 16:45:30 UTC
OPERATION: checkpoint
BRANCH: feature/database-schema
WARNING_TYPE: schema_automation_failed
STATUS: success_with_warning

WARNING_DETAILS:
Schema automation error: Connection to database failed
Error: psycopg2.OperationalError: could not connect to server: Connection refused

ACTION_TAKEN:
Checkpoint created without schema files
Manual schema automation required

COMMIT_HASH: h7i8j9k

GIT_STATUS:
M  database_tools/migrations/006_add_validation_tables.sql

================================================================================
```

### Error: Documentation Missing (Section Commit)

```
================================================================================
TIMESTAMP: 2025-10-12 17:20:18 UTC
OPERATION: section_commit
BRANCH: feature/ai-integration
ERROR_TYPE: documentation_missing
STATUS: failed

ERROR_DETAILS:
Files requiring documentation:
- modules/ai_integration/gemini_client.py (new)
- modules/ai_integration/prompt_builder.py (new)

REMEDIATION:
- Create documentation in docs/component_docs/ai_integration/
- Add comprehensive docstrings to new files
- Document public API and usage examples
- Include configuration and environment variables

FALLBACK_ACTION: none
FALLBACK_COMMIT:

GIT_STATUS:
A  modules/ai_integration/gemini_client.py
A  modules/ai_integration/prompt_builder.py
M  modules/ai_integration/__init__.py

FILES_CHANGED:
 modules/ai_integration/__init__.py      |  5 +++
 modules/ai_integration/gemini_client.py | 87 ++++++++++++++++++++++++++++++++
 modules/ai_integration/prompt_builder.py| 54 +++++++++++++++++++
 3 files changed, 146 insertions(+)

================================================================================
```

### Warning: Push Failed

```
================================================================================
TIMESTAMP: 2025-10-12 18:05:42 UTC
OPERATION: section_commit
BRANCH: feature/storage-backend
WARNING_TYPE: push_failed
STATUS: success_with_warning

WARNING_DETAILS:
Push error: error: failed to push some refs to 'origin'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally. This is usually caused by another repository pushing
hint: to the same ref. You may want to first integrate the remote changes

ACTION_TAKEN:
Commit k1l2m3n created locally, manual push required
User should run: git pull --rebase origin feature/storage-backend
Then: git push origin feature/storage-backend

COMMIT_HASH: k1l2m3n

GIT_STATUS:
(clean - all changes committed)

================================================================================
```

---

## Log Analysis

### Finding Recent Errors

```bash
# View last 5 error entries
grep -B1 "STATUS: failed" logs/git-orchestrator-errors.log | tail -50

# View errors from specific date
grep "TIMESTAMP: 2025-10-12" logs/git-orchestrator-errors.log

# View errors by type
grep "ERROR_TYPE:" logs/git-orchestrator-errors.log | sort | uniq -c
```

### Finding Warnings

```bash
# View all warnings
grep -B1 "STATUS: success_with_warning" logs/git-orchestrator-errors.log

# Count warnings by type
grep "WARNING_TYPE:" logs/git-orchestrator-errors.log | sort | uniq -c
```

### Finding Errors by Branch

```bash
# Errors on specific branch
grep -A20 "BRANCH: feature/email-validation" logs/git-orchestrator-errors.log | grep "ERROR_TYPE:"
```

---

## Log Rotation

The error log is append-only. To prevent unbounded growth:

### Manual Rotation

```bash
# Archive old logs (keep last 1000 entries)
tail -1000 logs/git-orchestrator-errors.log > logs/git-orchestrator-errors.log.tmp
mv logs/git-orchestrator-errors.log logs/git-orchestrator-errors.$(date +%Y%m%d).log
mv logs/git-orchestrator-errors.log.tmp logs/git-orchestrator-errors.log
```

### Automated Rotation (Optional)

Add to cron or workflow scripts:

```bash
#!/bin/bash
# Rotate log if > 5MB
LOG_FILE="logs/git-orchestrator-errors.log"
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE") -gt 5242880 ]; then
    mv "$LOG_FILE" "logs/git-orchestrator-errors.$(date +%Y%m%d-%H%M%S).log"
    touch "$LOG_FILE"
fi
```

---

## Privacy & Security

**What's Safe to Log:**
- Error types and categories
- File paths (relative to project)
- Git status and branch names
- Test failure counts
- Public operation details

**What's NEVER Logged:**
- Environment variables (credentials, API keys)
- User data or personal information
- Database connection strings with passwords
- Secret tokens or authentication details

**Gitignore:** The `logs/` directory is gitignored to prevent accidental commits.

---

## Integration with Response Format

Error log entries complement the structured JSON responses:

**JSON Response (returned to primary agent):**
```json
{
  "status": "failed",
  "reason": "tests_failed",
  "message": "Tests failed, checkpoint created as fallback",
  "blocking_issues": ["test_email.py::test_validation FAILED"],
  "remediation": ["Fix test_email.py", "Run: pytest -v"],
  "fallback_action": "checkpoint_created",
  "fallback_hash": "a1b2c3d"
}
```

**Log File (persistent historical record):**
- Full git context (status, diff stats)
- UTC timestamp for correlation
- Complete error details
- Branch information
- Multiple error entries over time

---

## Troubleshooting

### Log File Not Created

```bash
# Ensure logs directory exists
mkdir -p logs

# Check permissions
ls -la logs/

# Verify log file can be written
touch logs/git-orchestrator-errors.log
```

### Log Entries Missing

Check that the git-orchestrator agent is:
1. Using the `log_error()` or `log_warning()` helper functions
2. Calling logging functions before returning responses
3. Not silently catching exceptions that prevent logging

### Log File Growing Too Large

Implement log rotation (see above) or archive old entries:

```bash
# Keep only last 30 days
find logs/ -name "git-orchestrator-errors.*.log" -mtime +30 -delete
```

---

## Related Documentation

- Git Orchestrator Agent: `.claude/agents/git-orchestrator.md`
- CLAUDE.md Git Operations Policy: `CLAUDE.md` (Git Operations section)
- Error Recovery Workflows: `docs/workflows/`
