---
title: File Organization Audit & Cleanup
status: completed
created: '2025-10-08'
updated: '2025-10-08'
author: Steve-Merlin-Projecct
type: task
tags: []
---

# PRD: File Organization Audit & Cleanup
**Status:** ✅ COMPLETED
**Priority:** Medium
**Feature Branch:** `feature/file-organization-cleanup`
**Version:** 4.1.0
**Created:** October 8, 2025
**Completed:** October 8, 2025

## Executive Summary

Perform targeted cleanup of misplaced files in the project, focusing on root directory accumulation and establishing clear organization standards. This will improve project navigability and prevent future file sprawl.

## Problem Statement

The project has accumulated files in inappropriate locations:

1. **Root Directory Clutter:** 5 markdown files that should be in `/docs` subdirectories
2. **Mixed File Purposes:** BRANCH_STATUS.md contains both branch-specific and workflow guidance
3. **Test Files Misplaced:** `test_db_connection.py` in root instead of `/tests`
4. **Legacy/Obsolete Files:** Replit-specific git workflow documentation
5. **Inconsistent Naming:** Mix of CAPS and lowercase conventions

This makes the project harder to navigate and sets poor precedent for future file placement.

## Objectives

### Primary Goals
1. Relocate misplaced files from root to appropriate `/docs` subdirectories
2. Split BRANCH_STATUS.md into branch-specific and workflow components
3. Archive obsolete Replit-specific git workflow documentation
4. Establish file organization standards documentation
5. Ensure naming consistency (lowercase-with-hyphens)

### Success Criteria
- Root directory contains only essential project files (app_modular.py, main.py, requirements.txt, etc.)
- All documentation properly categorized in `/docs` subdirectories
- BRANCH_STATUS.md split and relocated appropriately
- File organization standards documented
- No broken links after reorganization
- All changes committed with clear documentation

## Scope

### In Scope ✅
1. **Root Directory Cleanup:**
   - Move BRANCH_STATUS.md (split into 2 files)
   - Move GOOGLE_DRIVE_IMPLEMENTATION_SUMMARY.md
   - Move MIGRATION_COMPLETE.md
   - Move VERIFICATION_SUMMARY.md
   - Resolve claude.md (legacy filename)

2. **Test Files:**
   - Move test_db_connection.py to /tests

3. **Git Workflow Documentation:**
   - Review 6 files in docs/git_workflow/
   - Archive obsolete Replit-specific docs
   - Keep relevant workflow documentation

4. **Standards Documentation:**
   - Create docs/FILE_ORGANIZATION_STANDARDS.md
   - Define directory purposes
   - Establish naming conventions

5. **Data Files:**
   - Handle cookies.txt (gitignore or relocate)

### Out of Scope ❌
- Reorganizing `/modules` or `/database_tools` code structure
- Renaming existing well-organized documentation
- Changing git history or commit messages
- Deep architectural refactoring
- Moving files in `.trees/` worktrees

## User Stories

**As a developer:**
- I want to find documentation quickly without searching the root directory
- I want to know where to place new files based on clear standards
- I want branch status information separate from workflow guidance

**As a project maintainer:**
- I want the root directory to be clean and professional
- I want obsolete documentation archived, not deleted
- I want naming conventions that are consistent and readable

**As a new contributor:**
- I want clear organization so I can understand the project structure
- I want standards documentation to guide my contributions
- I want to find examples of where different file types belong

## Functional Requirements

### FR1: Root Directory Cleanup
**Priority:** P0

**Requirements:**
1. Move BRANCH_STATUS.md content to two locations:
   - Branch-specific info → `docs/git_workflow/branch-status/feature-task-guiding-documentation.md`
   - Workflow guidance → `docs/workflows/branch-review-workflow.md`

2. Move migration/summary files:
   - MIGRATION_COMPLETE.md → `docs/archived/migrations/`
   - VERIFICATION_SUMMARY.md → `docs/archived/migrations/`
   - GOOGLE_DRIVE_IMPLEMENTATION_SUMMARY.md → `docs/integrations/google-drive-implementation.md`

3. Handle legacy filename:
   - Verify claude.md is symlink or duplicate of CLAUDE.md
   - Remove if redundant

**Acceptance Criteria:**
- Root directory contains ≤3 documentation files (README, CLAUDE.md, CHANGELOG)
- All moved files maintain their content
- Links updated if any point to moved files

### FR2: Test File Organization
**Priority:** P1

**Requirements:**
1. Move test_db_connection.py to /tests/integration/test_db_connection.py
2. Verify it doesn't break any scripts or documentation references

**Acceptance Criteria:**
- Test file in correct location
- File executable permissions preserved
- No broken imports or references

### FR3: Git Workflow Documentation Review
**Priority:** P1

**Requirements:**
1. Review 6 files in docs/git_workflow/:
   - GITHUB_CONNECTIVITY_SOLUTION.md
   - GITHUB_SYNC_STATUS.md
   - MANUAL_MERGE_RESOLUTION.md
   - SMART_SCHEMA_ENFORCEMENT.md
   - github_connection_status.md
   - github_troubleshooting_guide.md

2. Categorize each as:
   - **Keep:** Still relevant for Docker/Claude Code environment
   - **Archive:** Replit-specific, move to docs/archived/replit-git-workflow/
   - **Update:** Needs Replit references removed

**Acceptance Criteria:**
- All obsolete Replit docs archived
- Remaining docs are Docker/Claude Code relevant
- Archive location clearly organized

### FR4: Standards Documentation
**Priority:** P0

**Requirements:**
1. Create `docs/FILE_ORGANIZATION_STANDARDS.md` with:
   - Directory structure guide
   - File type placement rules
   - Naming conventions (lowercase-with-hyphens)
   - Examples of correct placement
   - Decision tree for where to place new files

**Acceptance Criteria:**
- Standards document is comprehensive
- Examples cover common scenarios
- Easy to reference and follow

### FR5: Data File Handling
**Priority:** P2

**Requirements:**
1. Review cookies.txt:
   - If contains actual cookies: add to .gitignore, delete from repo
   - If test data: move to /tests/fixtures/
   - If template: move to /docs/templates/

**Acceptance Criteria:**
- No sensitive data in repository
- File properly categorized or removed

## Technical Approach

### Directory Structure
```
/workspace/
├── docs/
│   ├── git_workflow/
│   │   └── branch-status/
│   │       └── feature-task-guiding-documentation.md  # NEW
│   ├── workflows/
│   │   └── branch-review-workflow.md  # NEW
│   ├── archived/
│   │   ├── migrations/  # NEW
│   │   │   ├── migration-complete.md
│   │   │   └── verification-summary.md
│   │   └── replit-git-workflow/  # NEW
│   │       └── [obsolete git docs]
│   ├── integrations/
│   │   └── google-drive-implementation.md
│   └── FILE_ORGANIZATION_STANDARDS.md  # NEW
├── tests/
│   └── integration/
│       └── test_db_connection.py  # MOVED
└── [clean root - only essential files]
```

### File Naming Convention
**Standard:** lowercase-with-hyphens.md

**Examples:**
- ✅ `branch-review-workflow.md`
- ✅ `google-drive-implementation.md`
- ❌ `BRANCH_STATUS.md` (old style)
- ❌ `GoogleDriveImplementation.md` (camelCase)

### Link Update Strategy
1. Search for references to moved files:
   ```bash
   grep -r "BRANCH_STATUS" --include="*.md"
   grep -r "test_db_connection" --include="*.py"
   ```
2. Update all found references
3. Verify no broken links remain

### Git Strategy
1. Create feature branch: `feature/file-organization-cleanup`
2. Commit moves in logical groups:
   - Commit 1: Root directory cleanup
   - Commit 2: Test file moves
   - Commit 3: Git workflow doc archival
   - Commit 4: Standards documentation
3. Verify no broken references before pushing

## Non-Functional Requirements

### NFR1: Backward Compatibility
- All moved files maintain original content
- Update references to prevent broken links
- Archive rather than delete (preserve history)

### NFR2: Discoverability
- New locations more intuitive than old
- Standards document easy to find
- Clear directory purposes

### NFR3: Maintainability
- Naming conventions make alphabetical sorting useful
- Similar files grouped together
- Archive structure preserves context

## Dependencies

### Internal Dependencies
- CLAUDE.md may reference moved files
- Scripts may have hardcoded paths
- Documentation may link to root files

### External Dependencies
- None (internal reorganization only)

## Risks & Mitigation

### Risk 1: Broken Links
**Impact:** Medium
**Mitigation:**
- Search for all references before moving
- Update links in same commit as move
- Test documentation builds after changes

### Risk 2: Script Path Dependencies
**Impact:** Medium
**Mitigation:**
- Search for hardcoded paths in .py and .sh files
- Update before moving files
- Test scripts after reorganization

### Risk 3: Lost Context
**Impact:** Low
**Mitigation:**
- Archive rather than delete
- Preserve original filenames in archives
- Add README in archive directories

## Testing Strategy

### Validation Steps
1. **Link Check:**
   ```bash
   # Check for broken internal links
   grep -r "\[.*\](.*)" docs/ --include="*.md"
   ```

2. **Path References:**
   ```bash
   # Check for hardcoded paths
   grep -r "BRANCH_STATUS\|test_db_connection" --include="*.py" --include="*.sh"
   ```

3. **File Integrity:**
   - Compare file checksums before/after move
   - Verify content unchanged

4. **Git Status:**
   - Ensure git tracks moves (not delete+add)
   - Preserve file history

## Success Metrics

### Quantitative
- Root directory: 5 .md files → ≤2 .md files
- docs/git_workflow: 6 files → ~3 files (3 archived)
- Misplaced files: 8-10 → 0
- File organization standards: 0 docs → 1 doc

### Qualitative
- Easier to find documentation
- Clear placement rules for new files
- Professional root directory appearance
- Consistent naming across project

## Timeline

### Phase 1: Preparation (30 min)
- Create feature branch
- Search for references to files being moved
- Document all links that need updating

### Phase 2: Root Cleanup (45 min)
- Split BRANCH_STATUS.md
- Move migration summaries
- Move Google Drive summary
- Handle claude.md

### Phase 3: Specialized Moves (30 min)
- Move test files
- Review and archive git workflow docs
- Handle cookies.txt

### Phase 4: Documentation (30 min)
- Create FILE_ORGANIZATION_STANDARDS.md
- Update any broken references
- Create archive README files

### Phase 5: Validation (30 min)
- Run link checks
- Verify no broken paths
- Test moved test files
- Review all changes

**Total Estimated Time:** 2.5-3 hours

## Deliverables

1. Clean root directory (≤2 .md files)
2. Reorganized docs/ subdirectories
3. FILE_ORGANIZATION_STANDARDS.md
4. Updated references (no broken links)
5. Archive directories with context
6. Git commits with clear messages
7. Updated master changelog

## Future Enhancements

### Not in Current Scope
1. Pre-commit hook to enforce organization
2. Automated link checker in CI/CD
3. Documentation site generator
4. File organization linter

### Potential Follow-ups
1. Review all docs/ subdirectories for optimization
2. Create documentation templates
3. Establish PR review checklist for file placement
4. Document exceptions to standards

## Approval & Sign-off

**Prepared by:** Claude (Sonnet 4.5)
**Review Status:** Pending user approval
**Approval Required:** Yes - proceed to Task Generation

---

**Ready to proceed with Phase 2: Task Generation?**