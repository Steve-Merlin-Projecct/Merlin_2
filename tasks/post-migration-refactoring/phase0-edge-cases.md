# Phase 0: Edge Case Discovery Report
**Generated:** October 7, 2025
**Execution Time:** 15 minutes

## Executive Summary

Discovered **4 active Python files** and **35+ archived files** containing Replit references. Most active code references are in comments or string literals. Actual imports only exist in archived files under `.trees/` directories.

## Critical Findings

### 1. Active Code with Replit References (4 files)
- `/workspace/tools/secure_protected_content.py` - References `protected_replit_content.md`
- `/workspace/database_tools/schema_automation.py` - Has `update_replit_md()` method
- `/workspace/database_tools/schema_html_generator.py` - Uses Replit CDN for CSS
- `/workspace/docs/automation/scripts/generate_api_docs.py` - Contains replit.app URLs

### 2. No Active Replit Imports
- **ZERO** `import replit` or `from replit` statements in active code
- All imports found are in archived directories (`.trees/`, `archived_files/`)
- This is GOOD - means core cleanup will be easier

### 3. Pattern Variations Found
- Standard: `replit`, `Replit`, `REPLIT`
- No variations found: `repl.it`, `repl-it`, `repl_it`
- No typos found: `replt`, `repllit`
- Partial: `REPL_` prefix only in environment variable references (none found)

## Edge Cases Discovered

### Category 1: String Literals (Not Code)
**Files:** 4 active Python files
**Pattern:** References in strings, not actual code
**Decision:** UPDATE strings to Docker/localhost equivalents
```python
# Example from generate_api_docs.py
"url": "https://your-app.replit.app/api/v1"  # Change to localhost
```

### Category 2: Method Names
**File:** `database_tools/schema_automation.py`
**Pattern:** Method named `update_replit_md()`
**Decision:** REMOVE entire method - obsolete functionality
```python
def update_replit_md(self):  # DELETE this entire method
    """Update replit.md with schema automation information"""
```

### Category 3: CDN References
**File:** `database_tools/schema_html_generator.py`
**Pattern:** CSS from cdn.replit.com
**Decision:** REPLACE with standard Bootstrap CDN
```html
<link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
# Change to:
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
```

### Category 4: File Path References
**File:** `tools/secure_protected_content.py`
**Pattern:** Looking for `protected_replit_content.md` file
**Decision:** ARCHIVE entire tool if obsolete, or UPDATE path if needed

### Category 5: Comments Only
**Multiple Files:** Comment references to Replit
**Decision:** UPDATE comments to reference "legacy migration"
```python
# Update replit.md  ->  # Legacy migration reference (obsolete)
```

### Category 6: Documentation Files
**Files:** Multiple `.md` files in `/tasks/` and `/docs/`
**Decision:** ARCHIVE to `/docs/archived/replit-migration/`
- `tasks/prd-remove-replit-code.md`
- `docs/archived/replit-md_changelog.md`
- `docs/archived/replit_2.14__1754540640362.md`

### Category 7: Hidden/State Files
**Files:** `.local/state/replit/`, `.replit_md_hash`
**Decision:** DELETE - these are Replit runtime artifacts
```
.local/state/replit/agent/repl_state.bin
docs/changelogs/.replit_md_hash
```

### Category 8: Worktree References
**Files:** Multiple `.trees/` directories
**Decision:** IGNORE - these are git worktrees, not active code

## Risk Assessment

### Low Risk (Safe to Remove/Update)
1. String literal URLs - Simple find/replace
2. Comments mentioning Replit - Update text only
3. Hidden state files - Runtime artifacts, safe to delete
4. CDN references - Standard replacement available

### Medium Risk (Needs Verification)
1. `update_replit_md()` method - Check if called anywhere
2. `secure_protected_content.py` - Verify if tool is still used
3. Documentation files - Check for internal links

### High Risk (None Found)
- No critical functionality depends on Replit
- No active imports requiring code refactoring
- No database schemas referencing Replit

## Ambiguous Cases

### 1. Module Storage Reference
**File:** `modules/storage/storage_backend.py`
**Line:** `- Simple interface: Matches existing Replit Object Storage usage patterns`
**Context:** This is a COMMENT explaining the design rationale
**Decision:** Keep as-is - it's explaining why the interface was designed this way

### 2. Test Data References
**Files:** Some archived test files reference `.replit` in test data
**Decision:** Already in archived_files, leave as-is

### 3. Changelog Entries
**Files:** Various changelog mentions of Replit
**Decision:** KEEP - historical accuracy important

## File Type Distribution

| File Type | Count | Action |
|-----------|-------|---------|
| `.py` (active) | 4 | Update strings/comments |
| `.py` (archived) | 35+ | Leave in archives |
| `.md` | 6 | Archive to docs/archived/ |
| `.json` | 4 | Check each individually |
| Hidden files | 3 | Delete |
| Binary (.bin) | 2 | Delete |

## Recommended Approach

1. **Start with low-risk items** - String replacements, comment updates
2. **Delete obsolete state files** - `.local/state/replit/`, `.replit_md_hash`
3. **Archive documentation** - Move to `/docs/archived/replit-migration/`
4. **Update active Python files** - Only 4 files need changes
5. **Verify no functionality breaks** - Run tests after each change

## Special Considerations

### Git History
- Migration started: `43bae94` (Initial commit after Replit migration)
- Storage abstraction: `e3e6eee` (Removed Replit dependencies)
- Multiple feature branches merged related to migration
- **Decision:** Keep git history intact - valuable for understanding evolution

### Worktree Duplicates
- `.trees/` directories contain copies of main code
- These are git worktrees, not duplicates to clean
- **Decision:** Exclude from cleanup scope

### Already Archived Files
- Many Replit imports already in `/archived_files/`
- Previous cleanup already done partially
- **Decision:** Focus only on active code outside archives

## Next Steps for Phase 1

With these edge cases identified, Phase 1 can:
1. Focus on the 4 active Python files first
2. Use the risk assessment to prioritize changes
3. Apply the decision matrix for grey areas
4. Create detailed action plan with specific line changes