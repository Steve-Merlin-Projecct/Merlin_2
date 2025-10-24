---
title: "Git Orchestrator Guide"
type: guide
component: general
status: draft
tags: []
---

# Git Orchestrator User Guide
**Version:** 1.0
**Date:** October 9, 2025
**Audience:** Developers using Claude Code with automated workflows

---

## Overview

The **git-orchestrator** agent automates git operations during development, eliminating manual context switching between coding and version control. It handles checkpoints, section commits, validation, and error recovery autonomously.

**Key Benefit:** Focus on coding while git operations happen automatically at logical task boundaries.

---

## How It Works

### Automatic Invocation

You don't call git-orchestrator directly. The **primary development agent** invokes it automatically when:

1. **3+ tasks completed** in a section → Creates checkpoint
2. **All section tasks done** → Creates section commit
3. **End of work session** → Saves progress
4. **Switching sections** → Preserves current work

### What git-orchestrator Does

**For Checkpoints:**
- Stages all changes
- Runs quick test check
- Detects schema changes, runs automation if needed
- Warns about missing documentation
- Creates checkpoint commit
- Returns control to primary agent

**For Section Commits:**
- Validates ALL section tasks complete
- Runs full test suite (blocks if fail)
- Checks documentation exists (blocks if missing)
- Generates conventional commit message
- Shows preview, requests confirmation
- Creates commit after approval
- Updates version in CLAUDE.md
- **Automatically pushes to remote**
- Generates changelog template

---

## What You'll See

### Checkpoint Example

```
✅ Task 1.3: Ran migrations on development database

Section progress: 3/5 tasks complete
Creating checkpoint...

✅ Checkpoint created: Database Schema (tasks 1.1-1.3) [abc1234]
   Tests: 12 passed
   Schema automation: run

→ Continuing to task 1.4...
```

**What happened:**
- git-orchestrator detected 3+ tasks done
- Ran tests automatically
- Detected database changes, ran schema automation
- Created checkpoint commit
- Returned control immediately

---

### Section Commit Example

```
✅ Task 1.5: Verified schema documentation

All tasks in "Database Schema Setup" complete!
Creating section commit...

Running validation...
✅ Tests: 12 passed
✅ Schema automation: run
✅ Documentation: present

Commit message preview:
---
feat: database schema setup

- Created email_validations table for audit trail
- Added validation fields to users table
- Implemented performance indexes
- Generated schema documentation

Related to Task: Database Schema Setup in PRD: /tasks/email-validation/prd.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
---

Confirm commit? (y/n): y

✅ Section committed: feat: database schema setup [def5678]
📊 Version updated: 4.00 → 4.01
📤 Pushed to remote: success
📝 Changelog template generated

→ Moving to section: Core Validation Service
```

**What happened:**
- Validated all 5 tasks complete
- Ran full test suite
- Checked documentation exists
- Generated commit message
- Requested confirmation
- Created commit and updated version
- Pushed to remote automatically
- Generated changelog template for you to complete

---

## User Interactions

### When Confirmation Needed

**You'll be asked to confirm:**
- Section commits (see preview first)
- Large checkpoints (>20 files)

**You can:**
- Type `y` to proceed
- Type `n` to cancel and revise
- Review the commit message and files

---

### When Blockers Occur

**Test Failures (Section Commit):**
```
❌ Cannot commit section: 2 tests failing

Failures:
  - modules/database/operations.py::test_insert_job FAILED
  - modules/database/models.py::test_relationship FAILED

Remediation:
  1. Run: pytest modules/database/ -v for details
  2. Fix failing tests
  3. Section commit will retry automatically

✅ Progress saved as checkpoint [ghi9012]

Options:
1. Debug and fix tests now
2. Continue with other sections (tests can be fixed later)

What would you like to do?
```

**What to do:**
- Option 1: Fix tests immediately, section commit retries
- Option 2: Continue other work, come back to fix tests later
- Your progress is saved in checkpoint - nothing lost!

---

**Documentation Missing (Section Commit):**
```
❌ Cannot commit section: documentation required

Missing documentation for:
  - modules/validation/email_validator.py (new file)

Required:
  - Create: docs/component_docs/validation/email_validator.md
  - Add comprehensive docstrings to email_validator.py
  - Document public API and usage examples

Shall I create the documentation now? (y/n)
```

**What to do:**
- Say `y` to have agent create documentation template
- Or create documentation yourself
- Section commit will retry once docs exist

---

### When Warnings Appear

**Test Warnings (Checkpoint):**
```
✅ Checkpoint created [abc1234]
⚠️  Warning: 2 tests failing
   - modules/database/operations.py::test_insert_job
   - Consider fixing before section commit

→ Continuing to task 1.4...
```

**What to do:**
- Nothing required immediately
- Tests will be checked again at section commit
- Consider fixing when convenient

---

**Schema Automation Warning:**
```
✅ Checkpoint created [abc1234]
⚠️  Warning: Schema automation failed

Manual action needed:
  1. Check database connection (.env file)
  2. Run: python database_tools/update_schema.py
  3. Commit generated files

Shall I help troubleshoot? (y/n)
```

**What to do:**
- Say `y` for help debugging
- Or fix manually and continue

---

## Benefits

### Automatic Validation
- ✅ Tests run before every commit
- ✅ Schema automation triggered on database changes
- ✅ Documentation verified for new code
- ✅ Conventional commit format enforced
- ✅ Version numbers updated automatically

### Error Recovery
- ✅ Checkpoint fallback when section commit fails
- ✅ Clear error messages with remediation steps
- ✅ Progress never lost
- ✅ Can continue other work while issues fixed

### Consistent History
- ✅ Conventional commit messages
- ✅ Proper co-authorship attribution
- ✅ Linked to PRD and task sections
- ✅ Changelog templates generated
- ✅ Automatic remote push

---

## Troubleshooting

### "Checkpoint keeps getting skipped"

**Cause:** No uncommitted changes exist

**Solution:** Make code changes first, then checkpoint triggers

---

### "Section commit says 'section incomplete'"

**Cause:** Not all tasks in section marked [x]

**Solution:** Complete remaining tasks in tasklist_*.md

---

### "Tests pass locally but fail in git-orchestrator"

**Cause:** Test framework not in PATH or dependencies missing

**Solution:**
```bash
# Verify test framework installed
pytest --version  # or npm test

# If missing, install
pip install pytest  # or npm install
```

---

### "Schema automation not running"

**Cause:** Database connection not configured or script missing

**Solution:**
```bash
# Check .env file has PGPASSWORD set
cat .env | grep PGPASSWORD

# Test schema automation manually
python database_tools/update_schema.py
```

---

### "Push failed after section commit"

**Cause:** Remote branch doesn't exist or auth issue

**Solution:**
```bash
# Set upstream manually
git push --set-upstream origin <branch-name>

# Or check authentication
git push origin <branch-name>
```

Commit was created locally - push can be retried.

---

## Best Practices

### DO:
- ✅ Let checkpoints happen automatically (don't worry about them)
- ✅ Review section commit previews before confirming
- ✅ Complete documentation before section commits
- ✅ Fix test failures promptly
- ✅ Complete changelog templates after section commits

### DON'T:
- ❌ Run manual git commands (let git-orchestrator handle it)
- ❌ Skip documentation (section commits will be blocked)
- ❌ Ignore test warnings (they become blockers at section commit)
- ❌ Force push (git-orchestrator pushes automatically)

---

## FAQ

**Q: Can I skip a checkpoint?**
A: Checkpoints happen automatically. If you have no changes, it skips automatically.

**Q: Can I edit the commit message?**
A: Yes, during preview you can cancel and the primary agent can regenerate with your feedback.

**Q: What if I disagree with the commit type (feat/fix/etc)?**
A: Cancel and provide feedback. Agent will regenerate with correct type.

**Q: Can I create manual commits between checkpoints?**
A: Not recommended - let git-orchestrator manage all commits for consistency.

**Q: Does it work with worktrees?**
A: Yes! git-orchestrator detects git root and works correctly in worktree branches.

**Q: What if I need to amend a commit?**
A: Ask primary agent to make changes and create new checkpoint, or use `git commit --amend` manually if needed.

**Q: Where do I see the changelog template?**
A: After section commit, agent shows the template. Copy it to `docs/changelogs/master-changelog.md`.

**Q: Can I disable auto-push?**
A: Not currently - it's automatic for section commits. Checkpoints never push (local only).

---

## Advanced Usage

### Forcing a Checkpoint

If you want to checkpoint before 3 tasks done:

```
User: "Create a checkpoint now"
Agent: "Creating immediate checkpoint..."
[invokes git-orchestrator]
```

---

### Checking Git Status

```
User: "Show me git status"
Agent: [runs git status, shows uncommitted changes]
```

---

### Manual Section Commit Retry

If section commit failed and you fixed the issue:

```
User: "Try section commit again"
Agent: [re-invokes git-orchestrator with same section]
```

---

## Related Documentation

- [Git Orchestrator Agent Specification](/.claude/agents/git-orchestrator.md) - Technical details
- [Primary Agent Git Integration](./primary-agent-git-integration.md) - How agents integrate
- [Automated Task Workflow](./automated-task-workflow.md) - Complete development workflow
- [Automatic Checkpoints & Commits](./automatic-checkpoints-commits.md) - Original workflow guide

---

## Support

**Issues with git operations:**
1. Check agent exists: `.claude/agents/git-orchestrator.md`
2. Verify test framework installed
3. Check database connection (.env file)
4. Review error messages and remediation steps

**Feature requests or bugs:**
Report in project issue tracker with:
- Description of issue
- Expected vs actual behavior
- Agent response/error message
- Steps to reproduce

---

**Document Version:** 1.0
**Last Updated:** October 9, 2025
**Status:** Production Ready
