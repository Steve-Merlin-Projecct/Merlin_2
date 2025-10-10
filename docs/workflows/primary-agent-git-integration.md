# Primary Agent Git Integration Guide
**Version:** 1.0
**Date:** October 9, 2025
**For:** Development agents working with git-orchestrator

---

## Overview

This guide explains how primary development agents should integrate with the `git-orchestrator` agent for seamless version control operations during task execution.

**Key Principle:** Primary agent decides WHEN to invoke git operations (based on task progress), git-orchestrator handles HOW to execute them (validation, commits, error recovery).

---

## When to Invoke git-orchestrator

### Trigger 1: After Completing 3+ Sub-Tasks (Checkpoint)

**Decision Logic:**
```
After marking any sub-task complete in TodoWrite:
1. Count completed sub-tasks in current section
2. If count >= 3 AND not recently checkpointed:
   → Invoke git-orchestrator for checkpoint
3. Continue to next task
```

**Example:**
```markdown
Primary Agent completes task 1.3:

✅ Task 1.3: Created migrations on development database

Checking section progress...
- Section "Database Schema" has 5 tasks
- Completed: 3/5 (tasks 1.1, 1.2, 1.3)
- Decision: Create checkpoint (3+ tasks done)

Invoking git-orchestrator...
```

---

### Trigger 2: After Completing All Section Tasks (Section Commit)

**Decision Logic:**
```
After marking final sub-task in section complete:
1. Verify ALL sub-tasks in section marked [x]
2. If all complete:
   → Invoke git-orchestrator for section commit
3. Wait for response (may need user confirmation)
4. If success: Move to next section
5. If failed: Surface errors, wait for resolution
```

**Example:**
```markdown
Primary Agent completes task 1.5 (final task):

✅ Task 1.5: Verified schema documentation

Section status check:
- Section "Database Schema" has 5 tasks
- Completed: 5/5 ✓
- Decision: Create section commit

Invoking git-orchestrator for section commit...
```

---

### Trigger 3: End of Work Session

**Decision Logic:**
```
When user indicates session ending ("let's pause", "save progress"):
1. Check for uncommitted changes
2. If changes exist AND tasks completed since last checkpoint:
   → Invoke git-orchestrator for checkpoint
3. Report session summary to user
```

---

### Trigger 4: Before Switching Sections

**Decision Logic:**
```
When moving to new section:
1. Check if current section has uncommitted work
2. If yes AND tasks completed:
   → Invoke git-orchestrator for checkpoint
3. Proceed to new section
```

---

## How to Invoke git-orchestrator

### Checkpoint Invocation

**Required Context:**
1. **Operation type:** `checkpoint_check`
2. **Section name:** Current section (e.g., "Database Schema")
3. **Summary:** Brief description of what was done
4. **Files changed:** List of key files modified

**Invocation Pattern:**
```
Invoking git-orchestrator for checkpoint...

Operation: checkpoint_check:Database Schema
Summary: Completed tasks 1.1-1.3: created email_validations table migration, added validation fields to users table, ran migrations
Files changed:
- database_tools/migrations/004_add_email_validations.sql (new)
- database_tools/migrations/005_update_users_validation.sql (new)
- database_tools/migrations/test_migrations.sh (modified)
```

**Template:**
```
Invoking git-orchestrator for checkpoint...

Operation: checkpoint_check:{SECTION_NAME}
Summary: Completed tasks {TASK_RANGE}: {BRIEF_DESCRIPTION_OF_WORK}
Files changed:
- {FILE_PATH_1} ({new|modified|deleted})
- {FILE_PATH_2} ({new|modified|deleted})
```

---

### Section Commit Invocation

**Required Context:**
1. **Operation type:** `commit_section`
2. **Section name:** Full section name
3. **Summary:** Comprehensive description of all section work
4. **Files changed:** ALL files modified in section

**Invocation Pattern:**
```
Invoking git-orchestrator for section commit...

Operation: commit_section:Database Schema Setup
Summary: All tasks complete (1.1-1.5): created migrations for email_validations and users tables, added validation indexes, ran schema automation, updated documentation, verified all tests passing (12/12 tests passed)
Files changed:
- database_tools/migrations/004_add_email_validations.sql (new)
- database_tools/migrations/005_update_users_validation.sql (new)
- docs/component_docs/validation/email_validation_system.md (new)
- frontend_templates/database_schema.html (generated)
- database_tools/generated/models.py (generated)
- database_tools/generated/schemas.py (generated)
```

**Template:**
```
Invoking git-orchestrator for section commit...

Operation: commit_section:{FULL_SECTION_NAME}
Summary: All tasks complete ({TASK_RANGE}): {COMPREHENSIVE_DESCRIPTION_OF_ALL_WORK_INCLUDING_TESTS_STATUS}
Files changed:
- {FILE_PATH_1} ({new|modified|deleted})
- {FILE_PATH_2} ({new|modified|deleted})
- ... (all section files)
```

---

## Response Handling

### Response Structure

git-orchestrator returns structured JSON. Primary agent should check the `status` field:

```json
{
  "status": "success|failed|skipped|no_changes|cancelled",
  "action": "checkpoint|section_commit|none",
  "commit_hash": "abc1234",
  "message": "Human-readable summary",
  // ... additional fields
}
```

---

### Handling Success Response

**Status: "success"**

```python
if response.status == "success":
    # Operation completed successfully
    print(f"✅ {response.message}")

    if response.action == "checkpoint":
        print(f"   Checkpoint: [{response.commit_hash}]")
        # Continue to next task immediately

    elif response.action == "section_commit":
        print(f"   Commit: {response.commit_type}: {response.message} [{response.commit_hash}]")
        print(f"   Version: {response.version_updated}")
        print(f"   Push: {response.push_status}")
        # Move to next section

    # Continue work immediately
    continue_to_next_task()
```

**User Output Example:**
```
✅ Checkpoint created: Database Schema (tasks 1.1-1.3) [abc1234]
→ Continuing to task 1.4...
```

---

### Handling Failed Response

**Status: "failed"**

```python
if response.status == "failed":
    # Operation failed with blocking issues
    print(f"❌ {response.message}")
    print(f"\nBlocking Issues:")
    for issue in response.blocking_issues:
        print(f"  - {issue}")

    print(f"\nRemediation Steps:")
    for step in response.remediation:
        print(f"  {step}")

    # Check if fallback action taken
    if response.fallback_action == "checkpoint_created":
        print(f"\n✅ Progress saved as checkpoint [{response.fallback_hash}]")
        print("Fix the issues above, then retry section commit.")

    # Surface to user, wait for resolution
    await_user_action()
```

**User Output Example:**
```
❌ Cannot commit section: 2 tests failing

Blocking Issues:
  - modules/database/operations.py::test_insert_job FAILED
  - modules/database/models.py::test_relationship FAILED

Remediation Steps:
  1. Fix failing tests in database module
  2. Run: pytest modules/database/ -v for details
  3. Re-invoke commit_section after fixing

✅ Progress saved as checkpoint [ghi9012]
Fix the issues above, then retry section commit.

Options:
1. Debug and fix tests
2. Continue with other sections
3. Show detailed test output
```

---

### Handling Skipped/No Changes Response

**Status: "skipped" or "no_changes" or "cancelled"**

```python
if response.status in ["skipped", "no_changes", "cancelled"]:
    # No action taken, just informational
    print(f"ℹ️  {response.message}")

    # Continue immediately
    continue_work()
```

**User Output Example:**
```
ℹ️  No uncommitted changes detected. Skipping checkpoint.
→ Continuing to task 1.4...
```

---

## TodoWrite Integration

**After every TodoWrite call that marks task complete:**

```python
# Mark task complete
TodoWrite(todos=[...task marked complete...])

# Check if checkpoint needed
completed_in_section = count_completed_tasks(current_section)

if completed_in_section >= 3 and not recently_checkpointed():
    # Invoke checkpoint
    response = invoke_git_orchestrator(
        operation="checkpoint_check",
        section=current_section,
        summary=summarize_recent_work(),
        files=get_changed_files()
    )

    handle_response(response)

# Check if section complete
if all_tasks_complete(current_section):
    # Invoke section commit
    response = invoke_git_orchestrator(
        operation="commit_section",
        section=current_section,
        summary=summarize_section_work(),
        files=get_all_section_files()
    )

    handle_response(response)

    if response.status == "success":
        move_to_next_section()
```

---

## Error Scenarios & Handling

### Scenario 1: Test Failures During Checkpoint

**Response:**
```json
{
  "status": "success",
  "warnings": ["2 tests failed but checkpoint created"],
  "tests": {"passed": 10, "failed": 2}
}
```

**Handling:**
```
✅ Checkpoint created [abc1234]
⚠️  Warning: 2 tests failing
   - Consider fixing before section commit

→ Continuing to task 1.4...
```

---

### Scenario 2: Test Failures During Section Commit

**Response:**
```json
{
  "status": "failed",
  "reason": "tests_failed",
  "fallback_action": "checkpoint_created",
  "fallback_hash": "def5678"
}
```

**Handling:**
```
❌ Cannot commit section: tests failing
✅ Checkpoint created instead [def5678]

Options:
1. Fix tests and retry
2. Continue with other work

Waiting for user decision...
```

---

### Scenario 3: Documentation Missing During Section Commit

**Response:**
```json
{
  "status": "failed",
  "reason": "documentation_missing",
  "blocking_issues": ["modules/validation/email_validator.py needs docs"]
}
```

**Handling:**
```
❌ Cannot commit section: documentation required

Missing documentation for:
  - modules/validation/email_validator.py

Required:
  - Create docs/component_docs/validation/email_validator.md
  - Add comprehensive docstrings to email_validator.py

Shall I create the documentation now? (y/n)
```

---

### Scenario 4: Schema Automation Failure

**Response:**
```json
{
  "status": "success",
  "warnings": ["Schema automation failed, checkpoint created without generated files"],
  "schema_automation": "failed"
}
```

**Handling:**
```
✅ Checkpoint created [abc1234]
⚠️  Warning: Schema automation failed

Manual action required:
  1. Check database connection (.env file)
  2. Run: python database_tools/update_schema.py
  3. Create new checkpoint with generated files

→ Do you want me to help debug the schema automation? (y/n)
```

---

## Decision Flowchart

```
Task Complete (TodoWrite)
    ↓
Count completed tasks in section
    ↓
    ├─→ 3+ tasks completed?
    │   ├─→ YES → Invoke checkpoint
    │   │   ├─→ Success: Continue
    │   │   ├─→ Failed: Report, continue
    │   │   └─→ Skipped: Continue
    │   └─→ NO → Continue to next task
    ↓
All section tasks complete?
    ├─→ YES → Invoke section commit
    │   ├─→ Success: Move to next section
    │   ├─→ Failed: Surface errors, await resolution
    │   └─→ Cancelled: Wait for user
    └─→ NO → Continue to next task
```

---

## Best Practices

### DO:
- ✅ Always provide section name in invocations
- ✅ Include comprehensive summary for section commits
- ✅ List all key files changed
- ✅ Check response status before proceeding
- ✅ Surface blocking issues to user immediately
- ✅ Continue with other work when section commit fails (don't block)

### DON'T:
- ❌ Run git commands directly (always use git-orchestrator)
- ❌ Skip checkpoint after 3+ tasks
- ❌ Continue to next section when commit fails
- ❌ Ignore "failed" status responses
- ❌ Provide minimal context (git-orchestrator needs full picture)
- ❌ Bypass git-orchestrator for "quick" commits

---

## Example: Complete Section Workflow

```markdown
### Section: Database Schema (5 tasks)

**Task 1.1: Create migrations**
→ Implement changes
→ Mark complete in TodoWrite
→ Check: 1/5 tasks done → Continue (no checkpoint yet)

**Task 1.2: Update users table**
→ Implement changes
→ Mark complete in TodoWrite
→ Check: 2/5 tasks done → Continue (no checkpoint yet)

**Task 1.3: Run migrations**
→ Implement changes
→ Mark complete in TodoWrite
→ Check: 3/5 tasks done → INVOKE CHECKPOINT ✓
→ Checkpoint response: success
→ Continue to task 1.4

**Task 1.4: Run schema automation**
→ Implement changes
→ Mark complete in TodoWrite
→ Check: 4/5 tasks done → Continue (checkpoint recent)

**Task 1.5: Verify documentation**
→ Implement changes
→ Mark complete in TodoWrite
→ Check: 5/5 tasks done → INVOKE SECTION COMMIT ✓
→ Section commit response: success
→ Version updated: 4.00 → 4.01
→ Pushed to remote: success
→ Move to next section: "Core Validation Service"
```

---

## Troubleshooting

### Issue: "git-orchestrator not responding"
**Solution:** Verify agent exists in `.claude/agents/git-orchestrator.md`

### Issue: "Checkpoint always skipped"
**Solution:** Check if uncommitted changes exist (`git status`)

### Issue: "Section commit fails with 'section incomplete'"
**Solution:** Verify all tasks in section marked [x] in task list

### Issue: "Tests pass locally but fail in git-orchestrator"
**Solution:** Ensure test framework installed and accessible in PATH

### Issue: "Schema automation not running"
**Solution:** Verify `database_tools/update_schema.py` exists and database connection configured

---

## Quick Reference

| Situation | Action | Invocation |
|-----------|--------|------------|
| 3+ tasks done in section | Checkpoint | `checkpoint_check:Section Name` |
| All section tasks done | Section Commit | `commit_section:Full Section Name` |
| End of session | Checkpoint | `checkpoint_check:Current Section` |
| Switching sections | Checkpoint | `checkpoint_check:Old Section` |
| Tests fail (checkpoint) | Continue anyway | Agent proceeds with warning |
| Tests fail (section commit) | Fix tests | Agent creates checkpoint fallback |
| Docs missing (section commit) | Create docs | Agent blocks commit |
| No changes | Skip | Agent returns "no_changes" |

---

**Document Version:** 1.0
**Last Updated:** October 9, 2025
**Related Documentation:**
- [Git Orchestrator Agent Specification](/.claude/agents/git-orchestrator.md)
- [Automated Task Workflow](./automated-task-workflow.md)
- [Agent Usage Guide](../agent-usage-guide.md)
