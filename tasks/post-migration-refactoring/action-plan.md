---
title: Post-Migration Refactoring Action Plan
created: '2025-10-07'
updated: '2025-10-07'
author: Steve-Merlin-Projecct
type: task
status: active
tags:
- action
- plan
---

# Post-Migration Refactoring Action Plan
**Generated:** October 7, 2025
**Total Files:** 11 active files + cleanup tasks
**Estimated Time:** 3-4 hours
**Risk Level:** LOW

## Execution Order (Prioritized by Risk & Dependencies)

### Batch 1: Zero-Risk Deletions (15 min)
**No dependencies, no functional impact**

#### 1.1 Delete Replit State Files
**Action:** DELETE
```bash
rm -rf /workspace/.local/state/replit/
rm -f /workspace/docs/changelogs/.replit_md_hash
```
**Validation:** `ls -la .local/state/ docs/changelogs/`

### Batch 2: Low-Risk Code Updates (30 min)
**Simple string replacements, cosmetic changes**

#### 2.1 Update CDN Reference
**File:** `/workspace/database_tools/schema_html_generator.py`
**Action:** UPDATE
**Line ~150:**
```python
# FROM:
<link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
# TO:
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
```
**Test:** Generate HTML and visually verify

#### 2.2 Update Example API URLs
**File:** `/workspace/docs/automation/scripts/generate_api_docs.py`
**Action:** UPDATE
**Lines:** Find and replace
```python
# FROM:
{"url": "https://your-app.replit.app/api/v1", "description": "Production"},
{"url": "https://staging-app.replit.app/api/v1", "description": "Staging"}
# TO:
{"url": "http://localhost:5000/api/v1", "description": "Development"},
{"url": "https://your-domain.com/api/v1", "description": "Production"}
```
**Test:** Run script, check output

### Batch 3: Medium-Risk Code Removal (45 min)
**Method removal, needs verification**

#### 3.1 Remove update_replit_md Method
**File:** `/workspace/database_tools/schema_automation.py`
**Action:** REMOVE
**Steps:**
1. Delete entire method `def update_replit_md(self):` (lines ~130-145)
2. Remove call `self.update_replit_md()` (line ~150)
3. Clean up any imports if unused

**Before:**
```python
def update_replit_md(self):
    """Update replit.md with schema automation information"""
    replit_md_path = "replit.md"
    if os.path.exists(replit_md_path):
        # ... method body ...
```
**After:** Method completely removed

**Test:**
```bash
python database_tools/update_schema.py
# Should complete without errors
```

#### 3.2 Investigate and Handle secure_protected_content.py
**File:** `/workspace/tools/secure_protected_content.py`
**Action:** ARCHIVE or UPDATE
**Investigation First:**
```bash
# Check if used in any scripts
grep -r "secure_protected_content" --include="*.sh" --include="*.py"
# Check if the protected file exists
ls -la tools/protected_replit_content.md
```

**If unused:** Move to archived_files
```bash
mkdir -p /workspace/archived_files/replit-tools/
mv /workspace/tools/secure_protected_content.py /workspace/archived_files/replit-tools/
```

**If used:** Update the path
```python
# FROM:
protected_file = project_root / "tools/protected_replit_content.md"
# TO:
protected_file = project_root / "tools/protected_content.md"  # Remove "replit"
```

### Batch 4: Documentation Updates (30 min)
**No code impact, text changes only**

#### 4.1 Update CLAUDE.md
**File:** `/workspace/CLAUDE.md`
**Action:** UPDATE
**Changes:**
1. Remove line: "Post migration from Replit - Replit dependencies removed..."
2. Update version context
3. Remove any Replit migration mentions

#### 4.2 Archive Task PRDs
**Action:** ARCHIVE
```bash
mkdir -p /workspace/docs/archived/replit-migration/tasks/
mv /workspace/tasks/*replit*.md /workspace/docs/archived/replit-migration/tasks/
# Keep only prd-post-replit-code-cleanup.md for reference
```

#### 4.3 Update Storage Backend Comment
**File:** `/workspace/modules/storage/storage_backend.py`
**Action:** UPDATE (Optional)
```python
# FROM:
# Simple interface: Matches existing Replit Object Storage usage patterns
# TO:
# Simple interface: Designed for compatibility with object storage patterns
# Legacy Note: Interface originally matched Replit patterns for migration ease
```

### Batch 5: Configuration Cleanup (15 min)
**Check and update if needed**

#### 5.1 Check Configuration Files
```bash
# Check for Replit references
grep -i "replit" /workspace/.claude/worktree-config.json
grep -i "replit" /workspace/.config/.semgrep/semgrep_rules.json
```
**Action:** UPDATE if references found, otherwise SKIP

### Batch 6: Final Validation (30 min)

#### 6.1 Run Test Suite
```bash
pytest -v tests/ > /tmp/post-cleanup-tests.txt 2>&1
diff /tmp/baseline-tests.txt /tmp/post-cleanup-tests.txt
```

#### 6.2 Verify No Replit References Remain
```bash
# Final scan excluding archives and trees
grep -r "replit\|Replit\|REPLIT" \
  --include="*.py" \
  --exclude-dir=.git \
  --exclude-dir=archived_files \
  --exclude-dir=.trees \
  --exclude-dir=project_venv \
  /workspace/
```
**Expected:** No results or only changelog entries

#### 6.3 Check Application Functionality
```bash
# Start server
python app_modular.py
# Check health endpoint
curl http://localhost:5000/health
```

## Commit Strategy

### Commit 1: State File Cleanup
```bash
git add -A
git commit -m "chore: Remove Replit state files and artifacts"
```

### Commit 2: Code Updates
```bash
git add database_tools/ docs/automation/
git commit -m "refactor: Remove Replit references from active code"
```

### Commit 3: Documentation
```bash
git add CLAUDE.md tasks/ docs/archived/
git commit -m "docs: Archive Replit migration documentation"
```

### Commit 4: Final Cleanup
```bash
git add .
git commit -m "chore: Complete post-Replit migration cleanup"
```

## Success Checklist

- [ ] All state files deleted
- [ ] CDN reference updated
- [ ] API URLs updated
- [ ] update_replit_md() removed
- [ ] secure_protected_content handled
- [ ] CLAUDE.md updated
- [ ] Task PRDs archived
- [ ] All tests passing
- [ ] No active Replit references
- [ ] Application runs correctly

## Rollback Procedures

### Quick Rollback
```bash
git reset --hard HEAD~1  # Undo last commit
```

### Selective Rollback
```bash
git checkout HEAD~1 -- path/to/specific/file.py
```

### Full Rollback
```bash
git checkout v4.0.2-post-migration-start
```

## Notes

- Start with Batch 1 & 2 for quick wins
- Take snapshot after Batch 3 (code changes)
- Document any unexpected findings
- Keep terminal logs for cleanup report
- Total active files to modify: 4-5 (depending on investigation)

## Next Phase

After completing this action plan:
1. Mark Phase 1 as completed
2. Proceed to Phase 2: Code Cleanup Stream
3. Use this action plan as the execution guide