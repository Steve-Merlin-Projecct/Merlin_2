---
title: Replit Dependency Map
created: '2025-10-07'
updated: '2025-10-07'
author: Steve-Merlin-Projecct
type: task
status: active
tags:
- dependency
---

# Replit Dependency Map
**Generated:** October 7, 2025

## Direct Dependencies

### 1. `update_replit_md()` Method
**File:** `/workspace/database_tools/schema_automation.py`
**Called By:** Same file, line ~150 (self.update_replit_md())
**External Calls:** NONE found
**Dependency Chain:**
```
schema_automation.py:run()
  └── self.update_replit_md()
      └── Writes to "replit.md" file
```
**Risk:** Low - self-contained, no external dependencies
**Action:** Safe to remove method and call

### 2. `protected_replit_content.md` File
**Referenced By:** `/workspace/tools/secure_protected_content.py`
**File Exists:** NO - file not found
**Usage:**
- Attempts to protect/unprotect a file that doesn't exist
- 3 references to the path
**Risk:** Medium - tool may be called by scripts
**Action:** Check if tool is used anywhere

### 3. Replit CDN Bootstrap CSS
**File:** `/workspace/database_tools/schema_html_generator.py`
**Used By:** HTML generation for database schema
**Dependencies:** None - just a CDN link
**Risk:** Low - cosmetic only
**Action:** Replace with standard Bootstrap

### 4. Replit App URLs
**File:** `/workspace/docs/automation/scripts/generate_api_docs.py`
**Used As:** Example URLs in OpenAPI spec generation
**Dependencies:** None - example data only
**Risk:** Low - documentation examples
**Action:** Update to localhost examples

## Indirect Dependencies

### Tools That May Call secure_protected_content.py
**Search Results:** No Python files import or call this tool
```bash
grep -r "secure_protected_content" --include="*.py"
# Only finds the file itself
```
**Conclusion:** Tool appears unused

### Database Schema Automation Chain
```
update_schema.py (entry point)
  └── schema_automation.py:run()
      ├── extract_schema()
      ├── generate_models()
      ├── generate_html()
      └── update_replit_md() <-- Can be safely removed
```
**Impact:** Removing update_replit_md() won't break the chain

### Storage Backend References
**File:** `/workspace/modules/storage/storage_backend.py`
**Type:** Comment only
**Dependencies:** None - just explaining design rationale
**Impact:** No functional dependencies

## Module Import Analysis

### No Replit Package Imports
```python
# NONE of these found in active code:
from replit import ...
import replit
from replit.object_storage import ...
```
**All imports are in archived_files/**

### No Environment Variable Dependencies
```bash
# No REPL_ prefixed variables found:
grep "REPL_" *.env*
# Returns nothing
```

## Configuration File Dependencies

### .claude/worktree-config.json
**Contains:** Worktree management config
**Replit References:** Unknown (need to check)
**Dependencies:** Claude Code worktree system
**Risk:** Low - configuration only

### .config/.semgrep/semgrep_rules.json
**Contains:** Security scanning rules
**Replit References:** May have rules for Replit
**Dependencies:** Semgrep tool
**Risk:** Low - scanning rules only

## Execution Path Analysis

### Main Application (app_modular.py)
**Replit References:** NONE
**Import Chain:** No imports lead to Replit code

### Document Generation Pipeline
**Path:** webhook → document generation → storage
**Replit References:** NONE in active path
**Note:** All Replit storage code is in archived_files/

### Database Operations
**Path:** database tools → schema generation → HTML output
**Replit References:**
- CDN link in HTML template
- update_replit_md() method (unused externally)
**Impact:** Minimal - cosmetic and unused method

## Risk Assessment Summary

### Zero Risk (Can Remove Now)
1. Hidden state files in .local/state/replit/
2. .replit_md_hash file
3. update_replit_md() method

### Low Risk (Simple Updates)
1. CDN URL replacement
2. Example API URLs
3. Comments and documentation

### Medium Risk (Verify First)
1. secure_protected_content.py tool
   - Check: Is it called by any scripts?
   - Check: Is protected_replit_content.md needed?

### No Critical Dependencies Found
- No active code depends on Replit functionality
- No import chains lead to Replit modules
- No configuration requires Replit environment

## Recommended Execution Order

1. **Delete state files** - No dependencies
2. **Remove update_replit_md()** - Self-contained
3. **Update CDN and URLs** - Cosmetic changes
4. **Investigate secure_protected_content.py** - May be obsolete
5. **Update documentation** - No code impact