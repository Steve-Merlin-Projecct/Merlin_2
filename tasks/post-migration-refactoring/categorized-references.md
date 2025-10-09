---
title: Categorized Replit References
created: '2025-10-07'
updated: '2025-10-07'
author: Steve-Merlin-Projecct
type: task
status: active
tags:
- categorized
- references
---

# Categorized Replit References
**Generated:** October 7, 2025
**Total References:** 520 lines across files

## Category A: Obvious Replit Code (Safe to Remove)
**Files:** 0 active files
- No direct `import replit` in active code
- All imports are in archived_files or .trees directories
**Action:** NONE - already handled

## Category B: Documentation References (Update/Archive)
**Files:** 9 files

### Task Documentation (3 files)
- `/workspace/tasks/tasks-prd-remove-replit-code.md`
- `/workspace/tasks/prd-remove-replit-code.md`
- `/workspace/tasks/prd-post-replit-code-cleanup.md`
**Action:** ARCHIVE to `/docs/archived/replit-migration/tasks/`

### Archived Documentation (2 files)
- `/workspace/docs/archived/replit-md_changelog.md`
- `/workspace/docs/archived/replit_2.14__1754540640362.md`
**Action:** KEEP - already in archived location

### Active Documentation (Multiple)
- CLAUDE.md - Contains "Post migration from Replit" context
- Various workflow docs mentioning Replit
**Action:** UPDATE to remove Replit references

## Category C: Replit-Shaped Code (Requires Analysis)
**Files:** 4 active Python files

### 1. `/workspace/tools/secure_protected_content.py`
```python
protected_file = project_root / "tools/protected_replit_content.md"
```
**Analysis:** Looking for obsolete protection file
**Action:** ARCHIVE entire tool if unused, or UPDATE path

### 2. `/workspace/database_tools/schema_automation.py`
```python
def update_replit_md(self):
    """Update replit.md with schema automation information"""
    replit_md_path = "replit.md"
```
**Analysis:** Method for updating obsolete replit.md file
**Action:** REMOVE entire method and calls

### 3. `/workspace/database_tools/schema_html_generator.py`
```html
<link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
```
**Analysis:** Using Replit CDN for styling
**Action:** REPLACE with standard Bootstrap CDN

### 4. `/workspace/docs/automation/scripts/generate_api_docs.py`
```python
{"url": "https://your-app.replit.app/api/v1", "description": "Production"},
{"url": "https://staging-app.replit.app/api/v1", "description": "Staging"}
```
**Analysis:** Example URLs using Replit domains
**Action:** UPDATE to localhost/Docker URLs

## Category D: Optimization Opportunities (Enhance for Docker)
**Files:** 1 file

### `/workspace/modules/storage/storage_backend.py`
```python
# Comment: "Simple interface: Matches existing Replit Object Storage usage patterns"
```
**Analysis:** Design rationale comment explaining interface
**Action:** KEEP comment but add note about Docker optimization

## Category E: Archive Material (Preserve but Isolate)
**Files:** Multiple

### Hidden/State Files
- `/workspace/.local/state/replit/` (entire directory)
- `/workspace/docs/changelogs/.replit_md_hash`
**Action:** DELETE - runtime artifacts

### Configuration Files
- `.claude/worktree-config.json` - May contain Replit references
- `.config/.semgrep/semgrep_rules.json` - Security rules
**Action:** CHECK and UPDATE if needed

## Summary by Action Type

### DELETE (7 items)
1. `.local/state/replit/` directory
2. `docs/changelogs/.replit_md_hash`
3. `update_replit_md()` method in schema_automation.py
4. Related method calls

### UPDATE (4 files)
1. `database_tools/schema_html_generator.py` - CDN URL
2. `docs/automation/scripts/generate_api_docs.py` - Example URLs
3. `CLAUDE.md` - Remove migration context
4. `tools/secure_protected_content.py` - File path

### ARCHIVE (3 files)
1. `tasks/tasks-prd-remove-replit-code.md`
2. `tasks/prd-remove-replit-code.md`
3. `tools/secure_protected_content.py` (if unused)

### KEEP AS-IS
- Changelog entries (historical accuracy)
- Comments explaining design rationale
- Already archived files

## Risk Matrix

| File | Risk | Reason | Mitigation |
|------|------|--------|------------|
| schema_automation.py | Medium | Method removal | Check for calls first |
| secure_protected_content.py | Medium | May be in use | Verify usage |
| schema_html_generator.py | Low | Simple URL swap | Test HTML output |
| generate_api_docs.py | Low | Example data | No functional impact |
| CLAUDE.md | Low | Documentation | No code impact |
| Hidden files | Low | Runtime artifacts | Safe to delete |