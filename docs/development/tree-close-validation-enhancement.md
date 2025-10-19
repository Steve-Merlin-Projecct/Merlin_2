---
title: "/tree close Validation Enhancement"
type: reference
component: workflow
status: draft
tags: ["tree-close", "validation", "worktree", "enhancement"]
created: 2025-10-17
updated: 2025-10-17
version: 1.0
---

# `/tree close` Validation Enhancement

**Status:** 📋 Proposed Enhancement (Not Implemented in This Worktree)
**Target Worktree:** Future worktree for `/tree close` improvements
**Related:** `docs/development/quality-validation-coordination.md`

---

## Overview

Enhance the `/tree close` slash command to run **context-aware quality validation** before worktree closure, ensuring all changes meet quality standards appropriate to the worktree's purpose.

---

## Current State

**`/tree close` currently:**
- Closes the worktree
- (Does not run validation)

**Gap:** No quality gate before worktree closure

---

## Proposed Enhancement

### Context-Aware Validation

**The `/tree close` command should:**

1. **Detect worktree purpose** from:
   - Branch name patterns (`feature/*`, `docs/*`, `librarian-*`)
   - `PURPOSE.md` file content
   - Manual worktree configuration file

2. **Identify changed files:**
   ```bash
   git diff --name-only main...HEAD
   ```

3. **Route to appropriate validation suite:**
   - `.py` files changed → Code quality validation
   - `.md` files changed → Documentation quality validation
   - Mixed → Run both suites

4. **Report results** with clear pass/fail indicators

5. **Handle failures:**
   - Block close (strict mode)
   - Warn but allow (permissive mode)
   - User configurable per worktree

---

## Validation Routing Logic

```yaml
# Conceptual validation routing algorithm

CHANGED_FILES = git diff --name-only main...HEAD

IF any(*.py in CHANGED_FILES):
  RUN code_quality_validation:
    - black --check CHANGED_FILES
    - flake8 CHANGED_FILES
    - vulture CHANGED_FILES --min-confidence 80

IF any(*.md in CHANGED_FILES):
  RUN documentation_quality_validation:
    - python tools/librarian_validate.py CHANGED_FILES
    - python tools/validate_links.py CHANGED_FILES

AGGREGATE_RESULTS:
  - Count errors by category
  - Generate summary report
  - Determine pass/fail status

IF validation_failed AND strict_mode:
  BLOCK /tree close
  SHOW remediation_steps
ELSE:
  WARN and allow close
```

---

## Example: This Worktree (librarian-improvements)

**Worktree Purpose:** Librarian system improvements (documentation tools)

**Changed Files (Expected):**
- `docs/librarian-usage-guide.md`
- `docs/development/quality-validation-coordination.md`
- `tools/librarian_validate.py`
- `.claude/agents/librarian.md`

**Validation Suite:** Documentation quality only
- ✅ Run: `librarian_validate.py`, `validate_links.py`
- ❌ Skip: Black, Flake8, Vulture (tool scripts have different standards)

**Rationale:** This worktree focuses on documentation and librarian tools, not application code.

---

## Example Output

### Success Case

```
🌳 Closing worktree: librarian-improvements
📊 Detecting validation requirements...

Changed files (4):
  ✓ docs/librarian-usage-guide.md
  ✓ docs/development/quality-validation-coordination.md
  ✓ tools/librarian_validate.py
  ✓ .claude/agents/librarian.md

📚 Running documentation quality validation...

✅ Metadata validation: PASS (4/4 files)
   - All files have required YAML frontmatter
   - Valid type/status enum values
   - Proper date formats

✅ Link validation: PASS
   - 0 broken internal links
   - All cross-references valid

✅ File placement: PASS
   - All files correctly located per standards
   - Naming conventions followed

🎉 Validation passed! Safe to close worktree.

Would you like to close this worktree? [Y/n]
```

### Failure Case

```
🌳 Closing worktree: feature-email-validation
📊 Detecting validation requirements...

Changed files (8):
  ✓ modules/email_integration/validator.py
  ✓ tests/test_email_validator.py
  ✓ docs/api/email-validation-api.md
  ✓ ... (5 more)

🔧 Running code quality validation...

❌ Black formatting: FAILED (2 files need formatting)
   - modules/email_integration/validator.py (12 lines)
   - tests/test_email_validator.py (5 lines)

⚠️  Flake8 linting: WARNINGS (3 issues)
   - modules/email_integration/validator.py:45: F401 unused import
   - tests/test_email_validator.py:23: E501 line too long

✅ Vulture dead code: PASS

📚 Running documentation quality validation...

❌ Metadata validation: FAILED (1 file)
   - docs/api/email-validation-api.md: missing 'status' field

✅ Link validation: PASS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ VALIDATION FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Required actions before closing:

1. Format Python files:
   black modules/email_integration/validator.py tests/test_email_validator.py

2. Fix Flake8 issues:
   - Remove unused import in validator.py:45
   - Break long line in test_email_validator.py:23

3. Add metadata to documentation:
   - Add 'status: active' to docs/api/email-validation-api.md

Run validation again: /lint && python tools/librarian_validate.py

❌ Worktree close blocked. Fix issues above and retry.
```

---

## Configuration Options

### Per-Worktree Configuration

**`.tree-config.yml` (proposed):**
```yaml
# Validation configuration for this worktree

validation:
  mode: strict  # or 'permissive', 'warn-only'

  suites:
    code_quality:
      enabled: true
      tools: [black, flake8, vulture]

    documentation_quality:
      enabled: true
      tools: [librarian_validate, link_validator]

  scope: changed-files-only  # or 'full-project'

  on_failure:
    action: block  # or 'warn', 'ignore'
    show_remediation: true
```

### Global Defaults

**`.claude/settings.local.json` (proposed extension):**
```json
{
  "tree_close_validation": {
    "default_mode": "strict",
    "auto_detect_suite": true,
    "parallel_execution": true,
    "timeout_seconds": 300
  }
}
```

---

## Implementation Considerations

### Performance Optimization

**Only validate changed files:**
```bash
# Fast path: only files in this worktree
git diff --name-only main...HEAD | xargs black --check
git diff --name-only main...HEAD | xargs flake8

# vs. slow path: full project scan
black --check .
flake8 .
```

**Parallel execution:**
```bash
# Run both suites simultaneously
black --check . & flake8 & python tools/librarian_validate.py &
wait
```

### User Experience

**Fast feedback loop:**
- Start validation immediately on `/tree close` invocation
- Stream output as tools run (don't wait for all to finish)
- Show progress indicators for long-running validations

**Clear error messages:**
- File:line references for all issues
- Suggested fix commands (copy-paste ready)
- Links to relevant documentation

**Escape hatch:**
```bash
# Force close without validation (emergency use only)
/tree close --force --no-validation
```

---

## Integration with Existing Tools

### Leverage Existing Slash Commands

**`/tree close` should internally invoke:**
- `/lint` (if code files changed)
- Librarian validation tools (if doc files changed)

**Benefits:**
- Reuse existing tool configurations
- Consistent behavior with manual validation
- No code duplication

### Extend Librarian Tools

**Add `--worktree-files` flag:**
```bash
# Current: validate all docs
python tools/librarian_validate.py --all

# Proposed: validate only worktree changes
python tools/librarian_validate.py --worktree-files
```

**Implementation:**
```python
# In librarian_validate.py
if args.worktree_files:
    changed_files = subprocess.check_output(
        ["git", "diff", "--name-only", "main...HEAD"],
        text=True
    ).strip().split("\n")

    md_files = [f for f in changed_files if f.endswith(".md")]
    validate_files(md_files)
```

---

## Rollout Strategy

### Phase 1: Opt-In Beta
- Add validation to `/tree close` as **warn-only** mode
- Collect feedback on performance and UX
- Identify false positives and edge cases

### Phase 2: Default with Escape Hatch
- Enable validation by default
- Provide `--no-validation` flag for emergency use
- Log usage metrics

### Phase 3: Strict Enforcement
- Block close on validation failure (configurable)
- Remove escape hatch (or require explicit override)
- Full integration with CI/CD

---

## Testing Strategy

**Test scenarios:**

1. **Code-only worktree:**
   - Verify code quality validation runs
   - Verify documentation validation skips

2. **Docs-only worktree:**
   - Verify documentation validation runs
   - Verify code quality validation skips

3. **Mixed worktree:**
   - Verify both suites run
   - Verify independent pass/fail reporting

4. **No changes worktree:**
   - Verify validation skips (nothing to validate)
   - Fast close path

5. **Validation failure:**
   - Verify close blocked in strict mode
   - Verify warning shown in permissive mode

6. **Performance test:**
   - Large worktrees (100+ changed files)
   - Validate completes in < 5 minutes

---

## Success Metrics

**Goals:**
- ✅ 100% of worktree closes run appropriate validation
- ✅ < 5 minute validation time for typical worktrees
- ✅ < 5% false positive rate (valid code flagged as error)
- ✅ 90% developer satisfaction with validation UX
- ✅ 50% reduction in post-merge issues caught by validation

---

## Related Documentation

- **Quality Validation Coordination:** `docs/development/quality-validation-coordination.md`
- **Automated Tooling Guide:** `docs/development/standards/AUTOMATED_TOOLING_GUIDE.md`
- **Librarian Usage Guide:** `docs/librarian-usage-guide.md`

---

## Implementation Tracking

**Status:** 📋 Proposed (Not Yet Implemented)

**Next Steps:**
1. Create dedicated worktree for `/tree close` enhancements
2. Design `/tree close` validation API
3. Implement context detection logic
4. Add `--worktree-files` flag to librarian tools
5. Integrate validation into `/tree close` workflow
6. Write tests for validation routing
7. Beta test with opt-in warn-only mode
8. Collect feedback and iterate
9. Enable by default with escape hatch
10. Document user workflows

**Estimated Effort:** Medium (2-3 days implementation)

**Not Implemented in This Worktree Because:**
This worktree focuses on librarian system improvements (documentation, metadata, validation tools). The `/tree close` enhancement requires changes to the worktree management system itself, which is a separate concern. Implementing it here would violate the single-purpose worktree principle.

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Version:** 1.0 (Proposal)
