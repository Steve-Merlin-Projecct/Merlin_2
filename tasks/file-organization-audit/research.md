# File Organization Audit - Research Phase
**Date:** October 8, 2025
**Research Level:** 2 (Medium complexity)

## Current State Analysis

### Root Directory Issues
**5 markdown files in `/workspace` root:**
1. `BRANCH_STATUS.md` - Branch-specific status documentation
2. `GOOGLE_DRIVE_IMPLEMENTATION_SUMMARY.md` - Implementation summary
3. `MIGRATION_COMPLETE.md` - Migration completion status
4. `VERIFICATION_SUMMARY.md` - Verification results
5. `claude.md` - Legacy filename (should be CLAUDE.md)

**Other root-level files:**
- `requirements.txt` ✅ (correct location)
- `cookies.txt` ❌ (should be gitignored/in data directory)
- `test_db_connection.py` ❌ (should be in tests/)
- `app_modular.py` ✅ (correct location)
- `main.py` ✅ (correct location)

### Documentation Structure
**Strong organization in `/docs`:**
- 20+ subdirectories with clear purposes
- Good categorization: api, architecture, automation, etc.
- Existing directories that could house misplaced files:
  - `docs/git_workflow/` - For BRANCH_STATUS.md content
  - `docs/integrations/` - For Google Drive docs
  - `docs/archived/` - For completed migration docs

### Specific Issues Identified

**BRANCH_STATUS.md:**
- Contains branch-specific information
- Also contains workflow guidance (review checklists, testing)
- **Suggested split:**
  - Branch info → `docs/git_workflow/branch-status/feature-task-guiding-documentation.md`
  - Workflow guidance → `docs/workflows/branch-review-workflow.md`

**Migration/Summary docs:**
- Multiple completion summaries in root
- Should be in `docs/archived/migrations/` or `docs/project_overview/`

**Git workflow docs:**
- 6 files currently in `docs/git_workflow/`
- Some are Replit-specific (may need archival review)

## Organization Patterns Observed

### Good Patterns ✅
- Clear directory hierarchy in `/docs`
- Purposeful subdirectories (automation, component_docs, etc.)
- Separation of active vs archived docs

### Anti-Patterns ❌
- Root directory accumulation of status/summary files
- Duplicate/legacy filenames (`claude.md` vs `CLAUDE.md`)
- Test files outside `/tests` directory
- No consistent naming (CAPS vs lowercase)

## Proposed Approaches

### Option A: Comprehensive Reorganization
**Scope:** Audit entire project, move all misplaced files
**Pros:**
- Complete cleanup
- Establishes clear standards
- Prevents future accumulation
**Cons:**
- Time-intensive
- Risk of breaking references
- May affect active workflows

### Option B: Targeted Cleanup (Recommended)
**Scope:** Focus on root directory and obvious issues
**Pros:**
- Quick wins
- Lower risk
- Immediate improvement
**Cons:**
- Doesn't address all issues
- May need follow-up rounds

### Option C: Metadata-Driven Organization
**Scope:** Create manifest file defining ideal locations
**Pros:**
- Documents intentions
- Allows gradual migration
- Clear standards for future
**Cons:**
- Doesn't immediately fix issues
- Requires discipline to maintain

## Recommendation

**Option B + Documentation** - Targeted cleanup with standards documentation:

1. **Immediate Actions:**
   - Move/split BRANCH_STATUS.md
   - Relocate root summary files to appropriate docs subdirectories
   - Move test files to `/tests`
   - Archive or remove cookies.txt

2. **Standards Documentation:**
   - Create `docs/FILE_ORGANIZATION_STANDARDS.md`
   - Define where different file types belong
   - Establish naming conventions

3. **Future Prevention:**
   - Add to PR review checklist
   - Document in contributing guidelines

## Key Questions for PRD

1. Should BRANCH_STATUS.md be split into branch-specific + workflow sections?
2. Where should migration completion summaries live?
3. Should we enforce naming conventions (CAPS vs lowercase)?
4. What to do with Replit-specific git workflow docs?
5. Should we create a file organization pre-commit hook?

## Estimated Scope

**Files to relocate:** 8-10
**Directories to create:** 2-3
**Documentation to create:** 1-2 files
**Risk level:** LOW (mostly documentation moves)
**Time estimate:** 2-3 hours

## Dependencies

- Need to verify no broken links after moves
- May need to update CLAUDE.md references
- Should check for hardcoded paths in scripts