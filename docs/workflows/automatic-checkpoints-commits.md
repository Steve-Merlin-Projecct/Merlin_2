# Automatic Checkpoints and Commits Guide
**Version:** 1.0
**Date:** October 6, 2025
**Environment:** Claude Code

## Overview

Checkpoints and commits happen **automatically** when task sections are complete. The agent uses scripts to minimize manual work and ensure consistency.

## Two Types of Saves

### 1. Checkpoint (Work in Progress)
**When:** Sub-tasks complete but section not ready for final commit
**Purpose:** Save progress, create restore point
**Script:** `./scripts/checkpoint.sh`

### 2. Section Commit (Complete Section)
**When:** All tasks in a section are complete and tested
**Purpose:** Permanent commit with full documentation
**Script:** `./scripts/commit-section.sh`

## Automatic Trigger Rules

### Checkpoint Triggers

Create checkpoint when:
- ✅ 3+ sub-tasks completed in a section
- ✅ End of work session (user says "let's pause" or "save progress")
- ✅ Before switching to different section
- ✅ After implementing risky/complex code (create restore point)

**Agent action:**
```bash
# Stage changes
git add .

# Run checkpoint script
./scripts/checkpoint.sh "Section Name" "Completed tasks 1.1-1.3"
```

**Checkpoint script automatically:**
1. Runs tests (quick check)
2. Checks for database schema changes (runs automation if needed)
3. Stages generated files
4. Creates checkpoint commit
5. Does NOT update changelog (checkpoint is WIP)

### Section Commit Triggers

Create section commit when:
- ✅ All tasks under `## Section Heading` marked complete
- ✅ All tests passing
- ✅ Documentation created/updated
- ✅ User confirms "section is complete"

**Agent action:**
```bash
# Stage all changes
git add .

# Run section commit script
./scripts/commit-section.sh "Database Schema Setup" "feat" "/tasks/email-validation/prd.md"
```

**Section commit script automatically:**
1. Runs full test suite
2. Checks database schema changes (runs automation if needed)
3. **Verifies documentation exists** (fails if missing!)
4. Cleans up temporary files
5. Generates conventional commit message
6. Creates commit
7. Updates version in CLAUDE.md
8. Prompts for changelog update

## Task List Structure for Auto-Detection

Use section headings to mark commit boundaries:

```markdown
# Tasks: Email Validation System

## 1. Database Schema  ← Section boundary (commit point)
- [ ] Create migration for email_validations table
- [ ] Create migration for users table updates
- [ ] Run migrations on development database
- [ ] Run database schema automation
- [ ] Verify schema documentation

## 2. Core Validation Service  ← Section boundary (commit point)
- [ ] Implement RFC 5322 format validation
- [ ] Implement DNS MX record verification
- [ ] Create disposable email checker
- [ ] Implement Redis caching
- [ ] Add comprehensive error handling

## 3. Documentation (REQUIRED)  ← Section boundary (commit point)
- [ ] Add inline documentation to all files
- [ ] Create component documentation
- [ ] Update related documentation
- [ ] Update master changelog
```

## Agent Workflow

### When Sub-Task Completes

```markdown
✅ Task 1.1 completed

Checking section status...
- Section "Database Schema" has 5 tasks
- Completed: 1/5
- Not ready for commit yet

Continuing to next task...
```

### When Section Has 3+ Complete (Checkpoint)

```markdown
✅ Task 1.3 completed

Section progress: 3/5 tasks complete

Creating checkpoint to save progress...
```

```bash
git add .
./scripts/checkpoint.sh "Database Schema" "Completed tasks 1.1-1.3 (migrations created)"
```

```markdown
✅ Checkpoint created successfully

Continuing with task 1.4...
```

### When All Section Tasks Complete (Section Commit)

```markdown
✅ Task 1.5 completed

All tasks in section "Database Schema" are complete!

Running section commit workflow...
```

```bash
git add .
./scripts/commit-section.sh "Database Schema Setup" "feat" "/tasks/email-validation/prd.md"
```

**Script output:**
```
=== Section Commit: Database Schema Setup ===

Step 1: Running full test suite...
✅ All tests passed (12 passed)

Step 2: Checking for database schema changes...
Database changes detected. Running schema automation...
✅ Schema documentation generated and staged

Step 3: Verifying documentation...
✅ Component documentation found

Step 4: Cleaning up temporary files...
✅ Cleanup complete

Step 5: Generating commit message...
Commit message preview:
---
feat: database schema setup

Section: Database Schema Setup
Status: Complete and tested

Changes:
- 5 new file(s), 3 modified, 0 deleted

Key files:
- database_tools/migrations/004_add_email_validations.sql
- database_tools/migrations/005_update_users_validation.sql
- docs/component_docs/validation/email_validation_system.md
- frontend_templates/database_schema.html
- database_tools/generated/models.py

Related: /tasks/email-validation/prd.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
---

Step 6: Changes to be committed:
[git diff --stat output]

Create commit? (y/n)
```

**Agent responds:**
```markdown
Script is asking for confirmation. Responding 'y' to create commit...
```

**Script continues:**
```
✅ Section committed successfully!

Step 7: Updating version in CLAUDE.md...
Version: 4.00 → 4.01
✅ Version updated

Step 8: Update master changelog
[Shows template entry for changelog]

Open docs/changelogs/master-changelog.md for editing? (y/n)
```

**Agent responds:**
```markdown
Responding 'y' to update changelog...
```

**Agent then edits changelog:**
```markdown
Updating master changelog with section completion details...
```

```
## 2025-10-06

### Database Schema Setup

- **Version:** 4.01
- **Commit:** feat
- **Changes:**
  - Created email_validations table for validation audit trail
  - Added validation fields to users table
  - Implemented performance indexes
  - Generated schema documentation via automation
- **Files Modified:**
  - database_tools/migrations/004_add_email_validations.sql (new)
  - database_tools/migrations/005_update_users_validation.sql (new)
  - docs/component_docs/validation/email_validation_system.md (new)
  - frontend_templates/database_schema.html (auto-generated)
  - database_tools/generated/models.py (auto-generated)
- **Documentation:**
  - Created component documentation for email validation system
  - Generated database schema documentation
- **Tests:** All passing (12 tests)
- **Related:** /tasks/email-validation/prd.md
```

```markdown
✅ Section "Database Schema Setup" complete!
✅ Committed with conventional format
✅ Version updated to 4.01
✅ Changelog updated

Moving to next section: "Core Validation Service"
```

## TodoWrite Integration

**Update TodoWrite when section completes:**

```json
{
  "todos": [
    {
      "content": "Database Schema Setup - SECTION COMPLETE",
      "activeForm": "Database Schema Setup completed",
      "status": "completed"
    },
    {
      "content": "Core Validation Service",
      "activeForm": "Starting Core Validation Service",
      "status": "in_progress"
    }
  ]
}
```

**And update markdown:**

```markdown
- [x] ## 1. Database Schema ✅ COMMITTED
  - [x] Create migration for email_validations table
  - [x] Create migration for users table updates
  - [x] Run migrations on development database
  - [x] Run database schema automation
  - [x] Verify schema documentation

- [ ] ## 2. Core Validation Service ← Now working on this
  - [ ] Implement RFC 5322 format validation
  ...
```

## Script Capabilities

### checkpoint.sh
**What it does automatically:**
- Runs test suite (quick check)
- Detects database changes
- Runs `database_tools/update_schema.py` if needed
- Stages generated schema files
- Warns if documentation missing (doesn't fail)
- Creates checkpoint commit

**Agent just needs to:**
1. Stage files: `git add .`
2. Run script: `./scripts/checkpoint.sh "Section Name" "Brief description"`
3. Script handles the rest

### commit-section.sh
**What it does automatically:**
- Runs full test suite (fails if tests fail)
- Detects database changes
- Runs schema automation automatically
- **Verifies documentation exists** (fails if missing!)
- Cleans up temp files (*.pyc, __pycache__, etc.)
- Generates conventional commit message
- Shows preview and asks confirmation
- Creates commit
- Updates version in CLAUDE.md
- Generates changelog template
- Opens changelog for editing

**Agent just needs to:**
1. Stage files: `git add .`
2. Run script: `./scripts/commit-section.sh "Section Name" "feat|fix|docs" "/tasks/feature/prd.md"`
3. Answer 'y' to confirmations
4. Update changelog when prompted
5. Script handles everything else

## Error Handling

### Tests Fail
**Script output:**
```
❌ Tests failed! Cannot commit.

Options:
1. Fix the failing tests
2. Create a new task for fixing tests
3. Use checkpoint instead: ./scripts/checkpoint.sh "Section Name" "WIP"
```

**Agent action:**
- If quick fix: Fix and re-run script
- If complex: Create new task "Fix failing tests in [component]"
- If saving progress: Use checkpoint instead

### Documentation Missing
**Script output:**
```
❌ Error: New code files added but no component documentation found!

New files:
- modules/validation/email_validator.py

Required: Create documentation in docs/component_docs/[module]/
```

**Agent action:**
- Cannot proceed without documentation
- Must create component documentation first
- Then re-run script

### Database Automation Fails
**Script output:**
```
❌ Schema automation failed!
```

**Agent action:**
- Check database connection
- Verify migration syntax
- Run manually: `python database_tools/update_schema.py`
- Fix errors, then re-run script

## Best Practices

**DO:**
- ✅ Use checkpoints frequently (every 3+ tasks)
- ✅ Let scripts handle automation (don't bypass)
- ✅ Create documentation before committing
- ✅ Stage all files before running scripts (`git add .`)
- ✅ Use conventional commit types (feat/fix/docs/refactor)

**DON'T:**
- ❌ Skip running scripts and commit manually
- ❌ Bypass documentation checks
- ❌ Commit without running tests
- ❌ Forget to update changelog
- ❌ Skip database automation

## Quick Reference

**Create checkpoint:**
```bash
git add .
./scripts/checkpoint.sh "Section Name" "Description"
```

**Commit section:**
```bash
git add .
./scripts/commit-section.sh "Section Name" "feat|fix|docs|refactor" "[PRD path]"
```

**What gets automated:**
- ✅ Test execution
- ✅ Database schema automation
- ✅ Generated file staging
- ✅ Temp file cleanup
- ✅ Commit message generation
- ✅ Version increment
- ✅ Documentation verification

**What agent still does:**
- Stage files
- Run script
- Answer confirmations
- Update changelog (with template provided)

---

**The scripts do the heavy lifting. The agent just triggers them at the right time.**
