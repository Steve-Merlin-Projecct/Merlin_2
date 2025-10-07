# Task Execution Example: Email Validation System

This document shows a real example of how task execution would proceed following the Task Execution Guide.

---

## Starting Phase 3: Task Execution

**Agent:**

```
Phase 3: Task Execution

I'll now begin implementing the tasks in order, updating TodoWrite progress
in real-time.

Starting with Task 1.1: Create migration file for email_validations table
```

---

## Task 1.1: Create Migration File

**STEP 1A: Update TodoWrite**

```json
{
  "content": "Create migration file for email_validations table",
  "activeForm": "Creating migration file for email_validations table",
  "status": "in_progress"
}
```

**STEP 1B: Update Markdown** (same response)

```markdown
- [ ] 1.0 Database Schema Setup
  - [→] 1.1 Create migration file for email_validations table
  - [ ] 1.2 Create migration file to add validation fields to users table
  ...
```

**STEP 1C: Verify ONE Task In-Progress**
✅ Only task 1.1 is in_progress

---

**STEP 2: Execute the Work**

Agent creates file: `database_tools/migrations/004_add_email_validations.sql`

```sql
-- Migration: Add Email Validations Table
-- Date: 2025-10-06
-- Purpose: Track email validation attempts and results for audit and analytics
--
-- This table stores validation results for all email addresses entered in the system.
-- It supports multiple validation methods (format, DNS, disposable check) and tracks
-- which validation methods were used and whether they passed or failed.
--
-- Related Tables:
--   - users: Foreign key relationship for user-submitted emails
--
-- Indexes:
--   - email: For quick lookups of validation history for specific addresses
--   - validated_at: For time-based analytics and cleanup
--
-- Retention Policy:
--   - Records older than 90 days can be archived (future implementation)

CREATE TABLE email_validations (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  is_valid BOOLEAN NOT NULL,
  validation_method VARCHAR(50) NOT NULL,  -- 'format', 'dns', 'disposable_check', 'cache_hit'
  failure_reason TEXT,                     -- Null if valid, explanation if invalid
  validated_at TIMESTAMP DEFAULT NOW() NOT NULL,
  user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- Nullable: validation may occur before user creation

  -- Indexes for performance
  INDEX idx_email_validations_email (email),
  INDEX idx_email_validations_validated_at (validated_at),
  INDEX idx_email_validations_user_id (user_id)
);

-- Add comment for documentation
COMMENT ON TABLE email_validations IS 'Stores email validation attempts and results for audit trail and analytics';
COMMENT ON COLUMN email_validations.validation_method IS 'Method used: format (RFC 5322), dns (MX record check), disposable_check (blacklist), cache_hit (cached result)';
COMMENT ON COLUMN email_validations.failure_reason IS 'Human-readable explanation of validation failure, NULL if valid';
```

---

**STEP 3A: Update TodoWrite** (mark completed)

```json
{
  "content": "Create migration file for email_validations table",
  "activeForm": "Creating migration file for email_validations table",
  "status": "completed"
}
```

**STEP 3B: Update Markdown** (same response)

```markdown
- [ ] 1.0 Database Schema Setup
  - [x] 1.1 Create migration file for email_validations table
  - [ ] 1.2 Create migration file to add validation fields to users table
  ...
```

**STEP 3C: Verify Sync**
✅ TodoWrite: completed
✅ Markdown: [x]

---

## Task 1.2: Create Users Table Update Migration

**Agent continues with same pattern...**

**STEP 1A-C: Mark as in_progress** (TodoWrite + Markdown)

**STEP 2: Execute**

Creates file: `database_tools/migrations/005_update_users_validation.sql`

```sql
-- Migration: Add Email Validation Fields to Users Table
-- Date: 2025-10-06
-- Purpose: Track validation status and timestamp for user email addresses
--
-- These fields allow the system to quickly determine if a user's email has been
-- validated without querying the email_validations audit table. The status field
-- can be: 'pending', 'valid', 'invalid', or 'expired' (if validation >90 days old).

ALTER TABLE users
  ADD COLUMN email_validated_at TIMESTAMP,
  ADD COLUMN email_validation_status VARCHAR(20) DEFAULT 'pending';

-- Add index for filtering by validation status
CREATE INDEX idx_users_email_validation_status ON users(email_validation_status);

-- Add comments
COMMENT ON COLUMN users.email_validated_at IS 'Timestamp of most recent successful email validation';
COMMENT ON COLUMN users.email_validation_status IS 'Current validation status: pending, valid, invalid, expired';
```

**STEP 3A-C: Mark as completed** (TodoWrite + Markdown)

---

## Continuing Through Sub-Tasks...

Agent continues with tasks 1.3, 1.4, 1.5...

---

## Parent Task 1.0 Complete: Test & Commit

After completing all sub-tasks (1.1 through 1.6):

```markdown
All sub-tasks for Parent Task 1.0 (Database Schema Setup) are complete.

Now running tests before committing...
```

**STEP 5.1: Run Tests**

```bash
pytest tests/test_database_schema.py
```

Output:
```
======================== test session starts ========================
collected 12 items

tests/test_database_schema.py::test_email_validations_table PASSED
tests/test_database_schema.py::test_users_validation_fields PASSED
tests/test_database_schema.py::test_email_validations_indexes PASSED
...

======================== 12 passed in 2.45s =========================
```

✅ All tests pass!

**STEP 5.2: Stage Changes**

```bash
git add database_tools/migrations/004_add_email_validations.sql
git add database_tools/migrations/005_update_users_validation.sql
git add frontend_templates/database_schema.html
git add docs/component_docs/database/database_schema.md
git add database_tools/generated/models.py
```

**STEP 5.3: Clean Up**

✅ No temporary files
✅ No debug statements
✅ No secrets in code

**STEP 5.6: Create Component Documentation**

Creates: `/docs/component_docs/validation/email_validation_system.md`

```markdown
# Email Validation System Documentation

**Status:** Development
**Last Updated:** 2025-10-06
**Version:** 1.0
**Author:** AI Assistant (Claude Code)

## Overview

The email validation system provides multi-layered email address validation
across the job application platform, reducing email bounce rates and improving
data quality.

**Purpose:** Validate email addresses using format checking, DNS verification,
and disposable email detection.

**Key Functionality:**
- RFC 5322 email format validation
- DNS MX record verification
- Disposable email domain blocking
- Real-time UI validation feedback
- Validation result caching

## Architecture

### Database Schema

#### email_validations Table
Stores complete validation history for audit and analytics.

Columns:
- `id`: Primary key
- `email`: Email address validated
- `is_valid`: Boolean validation result
- `validation_method`: Method used (format/dns/disposable_check/cache_hit)
- `failure_reason`: Explanation if validation failed
- `validated_at`: Timestamp of validation
- `user_id`: Foreign key to users table (nullable)

Indexes:
- `idx_email_validations_email`: Fast lookup by email address
- `idx_email_validations_validated_at`: Time-based queries
- `idx_email_validations_user_id`: User validation history

#### users Table Updates
Added fields for quick validation status lookup:
- `email_validated_at`: Most recent validation timestamp
- `email_validation_status`: Current status (pending/valid/invalid/expired)

...
[Full documentation continues with all required sections]
```

**STEP 5.6.2: Update Master Changelog**

Edits: `docs/changelogs/master-changelog.md`

```markdown
## 2025-10-06

### Email Validation System - Database Schema

- **Version:** 4.01 (minor increment)
- **Task:** 1.0 - Database Schema Setup
- **Changes:**
  - Created email_validations table for validation audit trail
  - Added email validation fields to users table
  - Implemented indexes for performance optimization
  - Added comprehensive inline documentation to migration files
  - Generated updated database schema documentation
- **Files Modified:**
  - `database_tools/migrations/004_add_email_validations.sql` (new)
  - `database_tools/migrations/005_update_users_validation.sql` (new)
  - `frontend_templates/database_schema.html` (auto-generated)
  - `docs/component_docs/database/database_schema.md` (auto-generated)
  - `database_tools/generated/models.py` (auto-generated)
- **Documentation:**
  - Created `/docs/component_docs/validation/email_validation_system.md`
  - Added inline SQL comments explaining schema design
  - Generated database schema documentation via automation tools
- **Tests:** All passing (12 database schema tests)
- **Related:** `/tasks/email-validation/prd.md`
```

**STEP 5.7: Update Version**

Edits: `CLAUDE.md` line 3

```markdown
Version 4.01 (Update the version number during development...)
```

**STEP 5.4: Commit**

```bash
git commit -m "$(cat <<'EOF'
feat: add email validation database schema

- Created email_validations table for validation audit trail
- Added validation status fields to users table (email_validated_at, email_validation_status)
- Implemented performance indexes on email, timestamp, and user_id columns
- Added comprehensive SQL comments documenting schema design and relationships
- Generated updated database schema documentation via automation tools

Database changes:
- email_validations table: stores validation attempts and results
- users table: added email_validated_at and email_validation_status columns
- Indexes: optimized for email lookup, time-based queries, and user history

Documentation:
- Created /docs/component_docs/validation/email_validation_system.md
- Auto-generated schema docs in frontend_templates/ and docs/component_docs/database/
- Updated master changelog with complete change summary

Tests: All 12 database schema tests passing

Completed: Task 1.0 - Database Schema Setup
Related: /tasks/email-validation/prd.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**STEP 5.5: Mark Parent Task Completed**

**Update TodoWrite:**
```json
{
  "content": "Database Schema Setup",
  "activeForm": "Setting up database schema",
  "status": "completed"
}
```

**Update Markdown:** (same response)
```markdown
- [x] 1.0 Database Schema Setup
  - [x] 1.1 Create migration file for email_validations table
  - [x] 1.2 Create migration file to add validation fields to users table
  - [x] 1.3 Run migrations on development database
  - [x] 1.4 Run python database_tools/update_schema.py
  - [x] 1.5 Verify schema documentation
  - [x] 1.6 Commit all database changes
```

**Verify Sync:**
✅ TodoWrite: `status: "completed"`
✅ Markdown: `[x]` on parent and all sub-tasks
✅ Both updated in same response

---

## Moving to Next Parent Task

**Agent:**

```
Parent Task 1.0 complete! Moving to Task 2.0: Core Validation Service

Starting Task 2.1: Implement RFC 5322 email format validation
```

**Update TodoWrite:**
```json
{
  "content": "Implement RFC 5322 email format validation",
  "activeForm": "Implementing RFC 5322 email format validation",
  "status": "in_progress"
}
```

**Update Markdown:** (same response)
```markdown
- [x] 1.0 Database Schema Setup
  - [x] 1.1 through 1.6...

- [ ] 2.0 Core Validation Service
  - [→] 2.1 Implement RFC 5322 email format validation  ← Currently working
  - [ ] 2.2 Implement DNS MX record verification
  ...
```

---

## Key Takeaways from This Example

### ✅ What Was Done Correctly:

1. **Sync Pattern:** TodoWrite and markdown updated together in every status change
2. **One In-Progress:** Only one task marked `in_progress` at any time
3. **Immediate Updates:** Status changed immediately upon completion, no batching
4. **Documentation Created:** Component documentation written during parent task completion
5. **Changelog Updated:** Master changelog updated with comprehensive details
6. **Tests Run First:** Full test suite executed before committing
7. **Conventional Commits:** Proper commit message format with detailed description
8. **Inline Documentation:** SQL migration files have comprehensive comments
9. **Database Automation:** Used `update_schema.py` to generate schema docs
10. **Version Updated:** CLAUDE.md version incremented appropriately

### 🔄 Sync Verification Points:

**Starting Task 1.1:**
- ✅ TodoWrite: `in_progress`
- ✅ Markdown: `[→]`
- ✅ Same response

**Completing Task 1.1:**
- ✅ TodoWrite: `completed`
- ✅ Markdown: `[x]`
- ✅ Same response

**Completing Parent Task 1.0:**
- ✅ TodoWrite: `completed`
- ✅ Markdown: `[x]`
- ✅ Tests run first
- ✅ Documentation created
- ✅ Changelog updated
- ✅ Commit created
- ✅ All in proper sequence

### 📊 Progress Visibility:

At any point, both TodoWrite and markdown show identical progress:
- User sees real-time updates in Claude Code UI (TodoWrite)
- User can review complete task hierarchy in markdown file
- Both systems stay synchronized throughout execution

---

**This example demonstrates the complete workflow from task start through parent task completion, following all guidelines in the Task Execution Guide.**
